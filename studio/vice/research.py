"""/vice discover: competitor research from public YouTube data (free, ~150-450 quota units per full run).

What it reads: the seed competitor videos, their channels (subscribers, total views, creation date) and each
channel's latest 50 uploads (views, durations, titles, likes, comments). Optional discovery searches find more
GTA 6 channels (100 units each). Everything is cached for 24 h in database/vice.db, so re-running is cheap.

What it does NOT do: watch videos. YouTube video pages are blocked from the cloud session, so editing techniques
are never claimed; only titles, numbers and durations are compared. A format is called a trend only when 3+
independent channels show it.
"""
import collections
import datetime as dt
import json
import re
import statistics

from . import db
from .. import learn

SEEDS = {  # given by the owner, verified Nov 20, 2026
    "SUiwFz6SQtU": "GTA by Sam - Top GTA 6 Moments",
    "VZ5TZfzGNMQ": "GamingLife - Ranking Funniest GTA 6 Moments",
    "_WNJQFnWiGk": "xQc Daily Fan Page - First 10 Seconds Playing GTA 6",
    "KRpMIW0uaEg": "StreamingJoe - Ranking Lacy's Funniest GTA 6 Moments",
    "WbVEIA8sUXw": "ViralOnly - Ranking Insane GTA 6 Clips",
}
DISCOVERY_QUERIES = ["GTA 6 funny moments", "GTA 6 ranking", "GTA 6 tested"]
OWN = {"UCzk9Wts3WFynOHZQJRWOQIw", "UCgmVgDyZV-XuHmFl99zDnkw"}

PATTERNS = {  # title structures, checked per channel
    "ranking": r"\branking|\branked|\btier list",
    "top-N / best": r"\btop\s*\d*\b|\bbest\b|\bmost\b",
    "first-time / POV": r"\bfirst\b|\bpov\b|\bwhen you\b",
    "streamer name": r"\b(lacy|xqc|kai|speed|ishowspeed|jynxzi|kreek\w*|n3on|adin|clix|caseoh|sketch|tfue|summit)\b",
    "funny / insane": r"\bfunn|\binsane|\bwild|\bcrazy|\bchaos",
    "question": r"\?",
    "number": r"\d",
    "versus / tested": r"\bvs\b|\bversus\b|\btested\b|\btest\b|\bdoes it\b|\bmyth",
    "emoji": r"[\U0001F300-\U0001FAFF]",
}


def med(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.median(xs)) if xs else None


def channel_profile(con, cid, max_age_h=24):
    key = f"channel:{cid}"
    hit = db.cache_get(con, key)
    if hit:
        return hit
    c = learn.call("channels", part="snippet,statistics,contentDetails", id=cid)["items"][0]
    ids = [i["contentDetails"]["videoId"] for i in learn.call(
        "playlistItems", part="contentDetails", playlistId=c["contentDetails"]["relatedPlaylists"]["uploads"],
        maxResults=50).get("items", [])]
    vids = learn.video_details(ids)
    db.log_cost(con, "youtube_data_api", 3, "quota units", f"discover: channel {cid}")
    taken = db.now()
    st = c["statistics"]
    now = dt.datetime.now(dt.timezone.utc)
    ages = [(now - dt.datetime.fromisoformat(v["published"].replace("Z", "+00:00"))).total_seconds() / 86400 for v in vids]
    views = [v["views"] for v in vids]
    m = med(views) or 0
    gta = [v for v in vids if re.search(r"gta\s?(6|vi)\b|gta6", v["title"], re.I)]
    prof = {
        "channel_id": cid, "title": c["snippet"]["title"], "handle": c["snippet"].get("customUrl"),
        "created": c["snippet"]["publishedAt"][:10], "subs": int(st.get("subscriberCount", 0)),
        "views": int(st.get("viewCount", 0)), "videos": int(st.get("videoCount", 0)), "fetched_at": taken,
        "sample": len(vids), "sample_days": round(max(ages), 1) if ages else None,
        "uploads_last_7d": sum(1 for a in ages if a <= 7), "uploads_per_day_7d": round(sum(1 for a in ages if a <= 7) / 7, 1),
        "median_views": m, "max_views": max(views) if views else 0,
        "breakouts": [{"id": v["id"], "title": v["title"], "views": v["views"], "x_median": round(v["views"] / max(m, 1), 1)}
                      for v in sorted(vids, key=lambda v: -v["views"]) if m and v["views"] >= 5 * m][:5],
        "median_seconds": med([v["seconds"] for v in vids]),
        "length_mix": dict(collections.Counter("<=15s" if v["seconds"] <= 15 else "16-30s" if v["seconds"] <= 30 else
                                               "31-60s" if v["seconds"] <= 60 else "60s+" for v in vids)),
        "gta6_share": round(len(gta) / len(vids), 2) if vids else 0,
        "like_rate_pct": round(100 * sum(v["likes"] for v in vids) / max(1, sum(views)), 2),
        "comment_rate_pct": round(100 * sum(v["comments"] for v in vids) / max(1, sum(views)), 3),
        "title_patterns": {k: round(sum(1 for v in vids if re.search(p, v["title"], re.I)) / max(1, len(vids)), 2)
                           for k, p in PATTERNS.items()},
        "top_titles": [v["title"] for v in sorted(vids, key=lambda v: -v["views"])[:5]],
    }
    con.execute("INSERT OR REPLACE INTO competitor_channels VALUES (?,?,?,?,?,?,?,?,?)",
                (cid, taken, prof["title"], prof["handle"], prof["subs"], prof["views"], prof["videos"],
                 prof["created"], json.dumps(prof)))
    for v in vids:
        con.execute("INSERT OR REPLACE INTO competitor_videos VALUES (?,?,?,?,?,?,?,?,?)",
                    (v["id"], taken, cid, v["title"], v["published"], v["seconds"], v["views"], v["likes"], v["comments"]))
    con.commit()
    db.cache_put(con, key, prof, max_age_h)
    return prof


def discover_channels(con, queries=DISCOVERY_QUERIES, days=7):
    key = "discover:" + "|".join(queries) + f":{days}"
    hit = db.cache_get(con, key)
    if hit:
        return hit
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    found = collections.Counter()
    for q in queries:
        r = learn.call("search", part="snippet", q=q, type="video", videoDuration="short", order="viewCount",
                       publishedAfter=since, maxResults=25)
        db.log_cost(con, "youtube_data_api", 100, "quota units", f"discover search: {q}")
        for it in r.get("items", []):
            found[it["snippet"]["channelId"]] += 1
    out = [cid for cid, _ in found.most_common() if cid not in OWN]
    db.cache_put(con, key, out, 24)
    return out


def run(extra=True, max_extra=6):
    con = db.connect()
    seeds = {v["id"]: v for v in learn.video_details(list(SEEDS))}
    db.log_cost(con, "youtube_data_api", 1, "quota units", "discover: seed videos")
    seed_channels = []
    for vid, label in SEEDS.items():
        v = seeds.get(vid)
        if v:
            cid = learn.call("videos", part="snippet", id=vid)["items"][0]["snippet"]["channelId"]
            seed_channels.append((cid, v))
    profiles = {}
    for cid, _ in seed_channels:
        profiles[cid] = channel_profile(con, cid)
    discovered = []
    if extra:
        for cid in discover_channels(con):
            if cid not in profiles and len(discovered) < max_extra:
                profiles[cid] = channel_profile(con, cid)
                discovered.append(cid)
    trends = {}
    for k in PATTERNS:
        users = [p["title"] for p in profiles.values() if p["title_patterns"].get(k, 0) >= 0.2]
        trends[k] = {"channels": users, "trend": len(users) >= 3}
    rep = {"taken": db.now(), "seeds": [{"video": v, "label": SEEDS[v["id"]], "channel_id": cid} for cid, v in seed_channels],
           "profiles": list(profiles.values()), "discovered": discovered, "title_trends": trends}
    return rep, write(rep)


def esc(t):
    return str(t).replace("|", "/")


def write(rep):
    day = rep["taken"][:10]
    out = db.ROOT / "research" / "competitors" / f"competitors-{day}.md"
    L = [f"# Competitor research ({rep['taken']})", "",
         "Source: YouTube Data API (public numbers). Videos were NOT watched (YouTube pages are blocked from this "
         "environment), so nothing here describes editing; only titles, durations and view counts.", "",
         "## Seed videos (given by the owner, re-checked now)", "",
         "| Video | Channel | Views now | Length | Published | Views/hour |", "|---|---|---|---|---|---|"]
    for s in rep["seeds"]:
        v = s["video"]
        L.append(f"| [{esc(v['title'])}]({v['url']}) | {esc(v['channel'])} | {v['views']:,} | {v['seconds']} s | {v['published'][:10]} | {v['views_per_hour']:,} |")
    L += ["", "## Channels (latest 50 uploads each)", "",
          "| Channel | Subs | Created | Uploads/day (7 d) | Median views | Max views | Median length | GTA 6 share | Likes/views | Seed or found |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    seed_ids = {s["channel_id"] for s in rep["seeds"]}
    for p in sorted(rep["profiles"], key=lambda p: -(p["median_views"] or 0)):
        L.append(f"| {esc(p['title'])} | {p['subs']:,} | {p['created']} | {p['uploads_per_day_7d']} | {p['median_views']:,} | "
                 f"{p['max_views']:,} | {p['median_seconds']} s | {int(100 * p['gta6_share'])}% | {p['like_rate_pct']}% | "
                 f"{'seed' if p['channel_id'] in seed_ids else 'found'} |")
    L += ["", "## Breakouts (5x+ the channel's own median)", ""]
    for p in rep["profiles"]:
        for b in p["breakouts"][:3]:
            L.append(f"- {esc(p['title'])}: [{esc(b['title'])}](https://youtu.be/{b['id']}) {b['views']:,} views ({b['x_median']}x median)")
    L += ["", "## Title structures across channels", "",
          "A structure counts for a channel when 20%+ of its latest uploads use it; it's a trend only with 3+ channels.", "",
          "| Structure | Channels using it | Trend? |", "|---|---|---|"]
    for k, t in rep["title_trends"].items():
        L.append(f"| {k} | {len(t['channels'])}: {', '.join(esc(c) for c in t['channels'][:7])} | {'yes' if t['trend'] else 'no'} |")
    out.write_text("\n".join(L) + "\n")
    jpath = out.with_suffix(".json")
    jpath.write_text(json.dumps(rep, indent=1, default=str))
    return out, jpath
