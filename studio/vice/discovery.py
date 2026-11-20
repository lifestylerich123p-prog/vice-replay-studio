"""/vice scan: find candidate moments from AUTHORIZED sources only, dedupe them, and record them in the database.

Sources (config/sources.json):
1. Approved campaign streamers' own stream replays on YouTube (the footage the campaign lets us clip).
2. "Moments in circulation": other clippers' Shorts about those streamers, used ONLY as a signal of what happened
   and how crowded it is. Their videos are never footage; a usable clip must be cut from the streamer's own stream.
3. The owner's own gameplay in media/gameplay/ (loudness + scene-change moments, timestamps included).

Each candidate gets: creator, source URL, publication date, timestamps (when known), description, views, duration,
category, rights record + status, restrictions, used/fresh, and an event key for deduplication.
Quota: ~400 units per streamer for the circulation signal (cached 6 h), ~5 for replays.
"""
import hashlib
import json
from pathlib import Path

from . import db, dedupe, rights
from .. import learn

CAMPAIGNS = db.ROOT / "content" / "campaigns"


def approved_campaigns():
    out = []
    for f in sorted(CAMPAIGNS.glob("*.json")):
        if f.name.startswith("_"):
            continue
        c = json.loads(f.read_text())
        st = str(c.get("status", "")).lower()
        if c.get("owner_approved") and not st.startswith(("paused", "ended")):
            out.append((f.stem, c))
    return out


def cid(*parts):
    return hashlib.sha1("|".join(map(str, parts)).encode()).hexdigest()[:12]


def used_events():
    """What we already posted (campaign tracker + upload registry titles), for 'already used' checks."""
    used = []
    tracker = CAMPAIGNS / "tracker.md"
    if tracker.exists():
        for line in tracker.read_text().splitlines():
            cells = [c.strip() for c in line.split("|")]
            if len(cells) > 4 and cells[1][:4].isdigit():
                creator = "lacy" if "lacy" in cells[2] else "kreekcraft" if "kreek" in cells[2] else cells[2]
                used.append({"creator": creator, "published": cells[1] + "T12:00:00", "description": cells[3]})
    return used


def stream_replays(con, name, c):
    ch = c.get("youtube_channel_id")
    if not ch:
        return []
    up = learn.call("channels", part="contentDetails", id=ch)["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    ids = [i["contentDetails"]["videoId"] for i in learn.call("playlistItems", part="contentDetails", playlistId=up,
                                                               maxResults=15).get("items", [])]
    db.log_cost(con, "youtube_data_api", 3, "quota units", f"scan: {name} replays")
    out = []
    for v in learn.video_details(ids):
        if "gta" not in v["title"].lower():
            continue
        out.append({"id": cid(v["url"]), "creator": c.get("twitch_login") or name.split("-")[0], "source_url": v["url"],
                    "published": v["published"], "ts_start": None, "ts_end": None,
                    "description": f"Stream replay: {v['title']} ({round(v['seconds'] / 3600, 1)} h)",
                    "views": v["views"], "duration": v["seconds"], "category": "source replay",
                    "rights_source": f"campaign:{name}", "origin": "authorized replay",
                    "restrictions": "; ".join(c.get("rules", [])[:3])})
    return out


def circulating(con, name, c, hours=24):
    from .. import moments
    creator = c.get("twitch_login") or name.split("-")[0]
    key = f"circulating:{creator}:{hours}"
    vids = db.cache_get(con, key)
    if vids is None:
        vids = moments.scan(creator, hours)
        db.log_cost(con, "youtube_data_api", 400, "quota units", f"scan: clips in circulation about {creator}")
        db.cache_put(con, key, vids, 6)
    events = []
    for v in sorted(vids, key=lambda v: -v["views"]):
        cand = {"creator": creator, "published": v["published"], "description": v["title"]}
        for e in events:
            if dedupe.same_event(e, cand, threshold=0.34):
                e["clippers"].add(v["channel"])
                e["views"] += v["views"]
                e["examples"].append(v["url"])
                break
        else:
            events.append({**cand, "clippers": {v["channel"]}, "views": v["views"], "examples": [v["url"]],
                           "duration": v["seconds"]})
    out = []
    for e in events:
        n = len(e["clippers"])
        out.append({"id": cid(creator, dedupe.event_key(creator, e["description"])), "creator": creator,
                    "source_url": None, "published": e["published"], "ts_start": None, "ts_end": None,
                    "description": e["description"], "views": e["views"], "duration": e["duration"],
                    "category": "moment signal", "rights_source": f"campaign:{name}",
                    "origin": f"signal: {n} channel(s) posted it; cut only from {creator}'s own stream",
                    "restrictions": "footage must come from the streamer's own stream replay, never from these Shorts",
                    "crowded": n >= 3, "examples": e["examples"][:3]})
    return out


def own_gameplay():
    from .. import clip
    out = []
    for f in sorted((db.ROOT / "media" / "gameplay").rglob("*")):
        if f.suffix.lower() not in {".mp4", ".mov", ".mkv"}:
            continue
        for start, score in clip.find_moments(f, top=5, clip_len=20, total=clip.probe(f)[0]):
            out.append({"id": cid(f.name, start), "creator": "owner", "source_url": str(f.relative_to(db.ROOT)),
                        "published": None, "ts_start": round(start, 1), "ts_end": round(start + 20, 1),
                        "description": f"Loud/fast moment in {f.name} at {int(start // 60)}:{int(start % 60):02d}",
                        "views": None, "duration": 20, "category": "owner gameplay moment",
                        "rights_source": str(f.relative_to(db.ROOT)), "origin": "owner gameplay", "restrictions": "radio off"})
    return out


def save(con, cands, used):
    for c in cands:
        chk = rights.check(c["rights_source"], "clipcircuit" if c["rights_source"].startswith("campaign:") else "vice-replay")
        is_used = any(dedupe.same_event(u, c) for u in used)
        c["rights_status"] = "OK (" + chk["record"] + ")" if chk["ok"] else "BLOCKED: " + "; ".join(chk["reasons"])
        c["used"] = int(is_used)
        con.execute("INSERT OR REPLACE INTO candidates (id, creator, source_url, published, ts_start, ts_end, description,"
                    " views, duration, category, rights_id, rights_status, restrictions, used, event_key, origin, created_at)"
                    " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (c["id"], c["creator"], c["source_url"], c["published"], c["ts_start"], c["ts_end"], c["description"],
                     c["views"], c["duration"], c["category"], chk["record"], c["rights_status"], c["restrictions"],
                     c["used"], dedupe.event_key(c["creator"], c["description"]), c["origin"], db.now()))
    con.commit()


def run(signals=True):
    con = db.connect()
    used = used_events()
    cands = []
    for name, c in approved_campaigns():
        cands += stream_replays(con, name, c)
        if signals:
            cands += circulating(con, name, c)
    cands += own_gameplay()
    save(con, cands, used)
    return cands, write(cands)


def write(cands):
    day = db.now()[:10]
    out = db.ROOT / "reports" / f"scan-{day}.md"
    L = [f"# Moment scan ({db.now()})", "",
         "Authorized replays are footage we may cut (for the campaign's destination, ClipCircuit). Moment signals show "
         "what other clippers already posted: crowded = 3+ channels (skip), fresh = 1-2 channels. Signals are never footage.", "",
         "| Fresh? | Creator | Category | Description | Views | Rights | Used by us |", "|---|---|---|---|---|---|---|"]
    for c in sorted(cands, key=lambda c: (c["category"] != "source replay", c.get("crowded", False), -(c["views"] or 0))):
        fresh = "-" if c["category"] == "source replay" else ("crowded" if c.get("crowded") else "fresh")
        L.append(f"| {fresh} | {c['creator']} | {c['category']} | {c['description'][:80].replace('|', '/')} | "
                 f"{c['views'] or '-'} | {c['rights_status'][:40]} | {'yes' if c['used'] else 'no'} |")
    out.write_text("\n".join(L) + "\n")
    return out
