"""The numbered map series (owner APPROVE, Nov 26: "number the map Shorts as a series, each ending with the next
one, and pin the map playlist at the top of the channel").

Members: English Shorts whose episode says `"series": "Map Spots"` (the main `short`), or an extra `shorts[]` item
that says it itself. They are numbered in posting order (content/learn/approved_queue.json): spot #1 is the first
one posted. Each one not uploaded yet gets, in its episode file:
  - `"spot": N`: the map card shows a "MAP SPOT #N" badge ("LUGAR #N" in Spanish; studio/charts.py map_frame)
  - `"cta"` / `"cta_es"`: the follow pill on the last card promises the next one ("SPOT #N+1 NEXT: FOLLOW")
  - a "📍 Map Spot #N" line in the English and Spanish descriptions

    python -m studio.mapseries            # the series in order, and what is out of date
    python -m studio.mapseries number     # write the numbers into the episodes not uploaded yet (then re-render)
    python -m studio.mapseries sync       # YouTube: retitle scheduled ones to the episode title, add the spot line,
                                          # keep the map playlist in spot order (~50 units per change)
    python -m studio.mapseries sync --home   # ...and put the map playlist first on the channel's home tab

`studio.doctor` warns when a booked spot's number no longer matches its place in the schedule (a Short was moved):
run `number` and re-render it with `python -m studio.ship`.
"""
import argparse
import datetime as dt
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE = ROOT / "content" / "learn" / "approved_queue.json"
UPLOADS = ROOT / "content" / "learn" / "uploads.json"
EPISODES = ROOT / "episodes"
SERIES = "Map Spots"
PLAYLIST = "GTA 6 Map: Where to Find It"
LINE = re.compile(r"^📍 (Map Spot|Lugar) #\d+.*$", re.M)


def cta(n, lang="en"):
    """The follow pill on a spot's last card: promises the next spot (under ~26 characters)."""
    return f"LUGAR #{n + 1} PRONTO: SÍGUENOS" if lang == "es" else f"SPOT #{n + 1} NEXT: FOLLOW"


def desc_line(n, lang="en"):
    if lang == "es":
        return f"📍 Lugar #{n} de nuestra serie del mapa de GTA 6: todos están en la lista \"{PLAYLIST}\"."
    return f"📍 Map Spot #{n} of our GTA 6 map series: every spot is in the playlist \"{PLAYLIST}\"."


def with_line(text, line):
    """The description with our spot line (replaced if it is already there, else added after the first paragraph)."""
    text = text or ""
    if LINE.search(text):
        return LINE.sub(line, text, count=1)
    head, sep, rest = text.partition("\n\n")
    return f"{head}\n\n{line}" + (f"\n\n{rest}" if sep else "")


def _when(item):
    d, t = item["en"]
    return dt.datetime.strptime(f"{d} {t}", "%Y-%m-%d %I:%M %p")


def _item_spec(ep, item):
    if item == "short":
        return ep
    return next((s for s in ep.get("shorts", []) if s.get("id") == item), {})


def members(queue_items, uploads, load):
    """The series in posting order: [{slug, item, when, vid, n, stored}] (`stored` = the number in the episode)."""
    up = {(u.get("slug"), u.get("item")): vid for vid, u in uploads.items()}
    out = []
    for it in queue_items:
        if it.get("es_only") or not it.get("en") or it.get("item", "short") == "main":
            continue
        try:
            ep = load(it["slug"])
        except (OSError, KeyError, ValueError):
            continue
        item = it.get("item", "short")
        spec = _item_spec(ep, item)
        if (spec.get("series") if item != "short" else ep.get("series")) != SERIES:
            continue
        out.append({"slug": it["slug"], "item": item, "when": _when(it), "vid": up.get((it["slug"], item)),
                    "stored": spec.get("spot")})
    out.sort(key=lambda m: m["when"])
    for i, m in enumerate(out, 1):
        m["n"] = i
    return out


def stale(ms):
    """Booked spots (not uploaded yet) whose number no longer matches their place in the schedule."""
    return [m for m in ms if not m["vid"] and m["stored"] != m["n"]]


def apply_number(ep, n):
    """Writes the spot number, the next-spot pill and the description lines into an episode dict (main Short)."""
    ep["spot"] = n
    for key, lang in (("cta", "en"), ("cta_es", "es")):
        if not ep.get(key) or ep[key].startswith(("SPOT #", "LUGAR #")):
            ep[key] = cta(n, lang)
    ep["short_description"] = with_line(ep.get("short_description", ""), desc_line(n))
    if isinstance(ep.get("short_es"), dict) and ep["short_es"].get("description") is not None:
        ep["short_es"]["description"] = with_line(ep["short_es"]["description"], desc_line(n, "es"))
    return ep


def _load(slug):
    return json.loads((EPISODES / f"{slug}.json").read_text())


def _save(slug, ep):
    p = EPISODES / f"{slug}.json"
    raw = p.read_text()
    indent = 2 if raw.startswith('{\n  "') else (1 if raw.startswith('{\n "') else None)
    p.write_text(json.dumps(ep, ensure_ascii=False, indent=indent) + "\n")


def current():
    return members(json.loads(QUEUE.read_text())["items"], json.loads(UPLOADS.read_text()), _load)


def number():
    changed = []
    for m in current():
        if m["vid"] or m["item"] != "short":
            continue
        ep = _load(m["slug"])
        before = json.dumps(ep, ensure_ascii=False)
        apply_number(ep, m["n"])
        if json.dumps(ep, ensure_ascii=False) != before:
            _save(m["slug"], ep)
            changed.append(m)
    return changed


def sync(home=False):
    """YouTube side: scheduled members take the episode's (search-phrase) title, every uploaded member gets the spot
    line, the map playlist follows spot order (any other video in it, e.g. the long guide, goes after), and with
    `home` the playlist is the first section on the channel's home tab."""
    from .youtube_upload import add_to_playlist, req, token
    yt = "https://youtube.googleapis.com/youtube/v3/"
    tok = token()
    ms = [m for m in current() if m["vid"]]
    if not ms:
        return []
    r, _ = req("GET", yt + "videos?part=snippet,status&id=" + ",".join(m["vid"] for m in ms), tok)
    cur = {v["id"]: v for v in r.get("items", [])}
    done = []
    now = dt.datetime.now(dt.timezone.utc)
    for m in ms:
        v = cur.get(m["vid"])
        if not v:
            continue
        sn, st = v["snippet"], v.get("status", {})
        spec = _item_spec(_load(m["slug"]), m["item"])
        title = sn["title"]
        scheduled = st.get("privacyStatus") == "private" and st.get("publishAt") and \
            dt.datetime.fromisoformat(st["publishAt"].replace("Z", "+00:00")) > now
        want = spec.get("short_title") if m["item"] == "short" else spec.get("title")
        if scheduled and want and want != title:
            title = want  # live videos keep their title: only booked ones are retitled
        desc = with_line(sn.get("description", ""), desc_line(m["n"]))
        if title != sn["title"] or desc != sn.get("description", ""):
            body = {"id": m["vid"], "snippet": {"title": title, "description": desc[:4900],
                                                  "categoryId": sn.get("categoryId", "20"), "tags": sn.get("tags", []),
                                                  "defaultLanguage": sn.get("defaultLanguage") or "en"}}
            if sn.get("defaultAudioLanguage"):
                body["snippet"]["defaultAudioLanguage"] = sn["defaultAudioLanguage"]
            req("PUT", yt + "videos?part=snippet", tok, body)
            done.append(f"#{m['n']} {m['vid']}: " + ("title + " if title != sn["title"] else "") + "spot line")
        add_to_playlist(tok, m["vid"], PLAYLIST)
    # playlist order = spot order
    from .youtube_upload import _playlist_cache
    pid = _playlist_cache[PLAYLIST]
    r, _ = req("GET", yt + f"playlistItems?part=snippet&playlistId={pid}&maxResults=50", tok)
    items = sorted(r.get("items", []), key=lambda p: p["snippet"]["position"])
    rank = {m["vid"]: m["n"] for m in ms}
    want = sorted(items, key=lambda p: (rank.get(p["snippet"]["resourceId"]["videoId"], 10 ** 6),
                                        p["snippet"]["position"]))
    for pos, p in enumerate(want):
        if p["snippet"]["position"] != pos:
            req("PUT", yt + "playlistItems?part=snippet", tok,
                {"id": p["id"], "snippet": {"playlistId": pid, "position": pos,
                                            "resourceId": p["snippet"]["resourceId"]}})
            done.append(f"playlist: {p['snippet']['resourceId']['videoId']} -> position {pos}")
            r, _ = req("GET", yt + f"playlistItems?part=snippet&playlistId={pid}&maxResults=50", tok)
            items = {q["id"]: q for q in r.get("items", [])}
            want = [items.get(q["id"], q) for q in want]
    if home:
        r, _ = req("GET", yt + "channelSections?part=snippet,contentDetails&mine=true", tok)
        secs = r.get("items", [])
        if not any(pid in (s.get("contentDetails") or {}).get("playlists", []) for s in secs):
            req("POST", yt + "channelSections?part=snippet,contentDetails", tok,
                {"snippet": {"type": "singlePlaylist", "position": 0},
                 "contentDetails": {"playlists": [pid]}})
            done.append(f"channel home: \"{PLAYLIST}\" added as the first section")
    return done


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", nargs="?", default="show", choices=["show", "number", "sync"])
    ap.add_argument("--home", action="store_true", help="sync: also put the map playlist first on the channel home")
    a = ap.parse_args()
    if a.cmd == "number":
        for m in number():
            print(f"#{m['n']} {m['slug']} ({m['when']:%a %b %d %I:%M %p}): numbered: re-render with studio.ship")
    elif a.cmd == "sync":
        for line in sync(a.home) or ["nothing to change"]:
            print(line)
    ms = current()
    for m in ms:
        flag = "" if m["vid"] or m["stored"] == m["n"] else f"  <- episode says {m['stored']}: run number + re-render"
        print(f"#{m['n']:>2} {m['when']:%a %b %d %I:%M %p}  {m['slug']} ({m['item']})  "
              f"{'uploaded ' + m['vid'] if m['vid'] else 'booked'}{flag}")


if __name__ == "__main__":
    main()
