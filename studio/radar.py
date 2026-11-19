"""Free news radar (no AI): is there a big GTA 6 story right now? Used to stop breaking-news runs early.

    python -m studio.radar            # prints the top stories and BIG / QUIET; exit code 0 = BIG, 1 = QUIET

Reads Google News RSS for GTA 6 stories from the last 6 hours, groups headlines about the same story, and counts
how many reputable outlets cover each. A story is BIG when 3+ reputable outlets covered it in the window.
"""
import collections
import datetime as dt
import email.utils
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

REPUTABLE = ["ign", "gamespot", "kotaku", "polygon", "forbes", "the verge", "eurogamer", "bloomberg", "pc gamer",
             "gamesradar", "rock paper shotgun", "videogameschronicle", "vgc", "insider gaming", "push square",
             "pure xbox", "windows central", "tom's guide", "techradar", "dexerto", "game rant", "the gamer",
             "screen rant", "reuters", "cnbc", "bbc", "the guardian", "variety", "rockstar games", "gtaboom",
             "sportskeeda", "notebookcheck", "engadget", "ars technica", "gamesindustry", "destructoid", "rolling stone"]
STOP = set("gta grand theft auto vi 6 the a an and of to in for on with is are at as how what when why your you it its "
           "this that from new now here all about can will be after before by out up more just".split())
FEEDS = ["GTA 6", "GTA VI", "Rockstar GTA 6"]
# Topics that matter even when outlets word their headlines differently (launch week = hundreds of headlines).
TOPICS = {
    "review scores": ["metacritic", "opencritic", "review score", "reviews are in", "review roundup", "10/10", "perfect score"],
    "sales / records": ["sales", "sold", "million copies", "record-breaking", "biggest launch", "concurrent", "peak viewers", "million players"],
    "servers / outage": ["servers down", "server issues", "outage", "can't connect", "error code", "crashing"],
    "patch / update": ["patch", "update", "hotfix", "day one", "day-one"],
    "delay / refund": ["delay", "delayed", "refund", "recall"],
    "bans": ["ban", "banned", "suspended", "suspension"],
    "cheats": ["cheat", "cheats", "cheat code"],
    "pc / online": ["pc version", "pc release", "gta online", "online mode"],
    "rockstar statement": ["houser", "rockstar says", "rockstar confirms", "statement", "take-two", "zelnick"],
}


def fetch(q):
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(
        {"q": f"{q} when:6h", "hl": "en-US", "gl": "US", "ceid": "US:en"})
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30) as r:
        root = ET.fromstring(r.read())
    for it in root.iter("item"):
        title = it.findtext("title") or ""
        source = it.findtext("source") or (title.rsplit(" - ", 1)[-1] if " - " in title else "")
        when = email.utils.parsedate_to_datetime(it.findtext("pubDate")) if it.findtext("pubDate") else None
        yield {"title": title.rsplit(" - ", 1)[0], "source": source, "when": when, "link": it.findtext("link")}


def words(t):
    return {w for w in re.findall(r"[a-z0-9']+", t.lower()) if w not in STOP and len(w) > 2}


def main():
    now = dt.datetime.now(dt.timezone.utc)
    items, seen, failed = [], set(), 0
    for q in FEEDS:
        try:
            for it in fetch(q):
                if it["title"] not in seen and (not it["when"] or now - it["when"] <= dt.timedelta(hours=6)):
                    seen.add(it["title"])
                    items.append(it)
        except Exception as e:
            failed += 1
            print(f"radar: feed '{q}' failed ({type(e).__name__}); continuing")
    if not items:
        if failed == len(FEEDS):
            print("UNKNOWN: news feed unreachable. Do the full breaking-news check instead of skipping.")
            sys.exit(2)
        print("QUIET: no GTA 6 headlines in the last 6 hours.")
        sys.exit(1)
    # cluster: headlines sharing most of their meaningful words (compared with the story's first headline)
    clusters = []
    for it in items:
        w = words(it["title"])
        for c in clusters:
            shared = w & c["words"]
            if len(shared) >= 3 or (len(shared) >= 2 and len(shared) >= 0.6 * min(len(w), len(c["words"]))):
                c["items"].append(it)
                break
        else:
            clusters.append({"words": set(w), "items": [it]})
    for c in clusters:
        c["reputable"] = sorted({i["source"] for i in c["items"] if any(r in i["source"].lower() for r in REPUTABLE)})
    clusters.sort(key=lambda c: (len(c["reputable"]), len(c["items"])), reverse=True)
    print(f"{len(items)} GTA 6 headlines in the last 6 hours, {len(clusters)} stories. Top stories:")
    for c in clusters[:5]:
        lead = c["items"][0]
        print(f"- {len(c['reputable'])} reputable / {len(c['items'])} total: {lead['title']}  "
              f"[{', '.join(c['reputable'][:5]) or lead['source']}]  {lead['link']}")
    # topic sweep: 3+ reputable outlets on the same topic counts as BIG even if headlines differ
    topic_hits = []
    for name, keys in TOPICS.items():
        hit = [i for i in items if any(k in i["title"].lower() for k in keys)]
        rep = sorted({i["source"] for i in hit if any(r in i["source"].lower() for r in REPUTABLE)})
        if len(rep) >= 3:
            topic_hits.append((len(rep), name, rep, hit))
    topic_hits.sort(reverse=True)
    for n, name, rep, hit in topic_hits[:3]:
        print(f"- TOPIC '{name}': {n} reputable outlets, e.g. \"{hit[0]['title']}\" [{', '.join(rep[:5])}]")
    big = clusters[0] if len(clusters[0]["reputable"]) >= 3 else None
    if not big and topic_hits:
        n, name, rep, hit = topic_hits[0]
        print(f"\nBIG: topic '{name}' is covered by {n} reputable outlets. Check it.")
        sys.exit(0)
    if not big and len(items) >= 120:
        print(f"\nUNKNOWN: very busy news ({len(items)} headlines in 6 hours); do the full check.")
        sys.exit(2)
    if big:
        print(f"\nBIG: \"{big['items'][0]['title']}\" is covered by {len(big['reputable'])} reputable outlets.")
        sys.exit(0)
    print("\nQUIET: no story is covered by 3+ reputable outlets right now.")
    sys.exit(1)


if __name__ == "__main__":
    main()
