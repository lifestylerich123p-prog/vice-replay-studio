"""Flop review (owner Nov 22: "start deleting videos that don't have the needed views and learn from it" -> "OK do it
as you say, don't delete"). Rule (.claude/commands/daily-video.md "NOV 22 FLOP REVIEW"): a public Short with fewer
than 50 views 48 hours after going public is set PRIVATE (never deleted, reversible in Studio) and its pattern goes to
content/learn/lessons.md, so the machine stops making that kind of Short.

    python -m studio.flops            # list today's flops with their pattern (~3 YouTube units, changes nothing)
    python -m studio.flops --apply    # MAIN CHAT ONLY: set them private, mark uploads.json `hidden`, log lessons

Never touched: campaign clips (submitted to their campaign; owner kept them), videos the website embeds, long videos
(the rule is about Shorts), anything in KEEP, and the Spanish channel (a new channel's first Shorts sit near 0 views
for days; hiding them would end it before it starts).
"""
import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlencode

from . import scorecard
from .youtube_upload import channel_ids, req, token

ROOT = Path(__file__).resolve().parent.parent
LEARN = ROOT / "content" / "learn"
# youtube.googleapis.com, not www.googleapis.com: this environment adds its read-only API key to www.googleapis.com
# requests, which then see public videos only (Nov 22: private videos looked "deleted" through it)
API = "https://youtube.googleapis.com/youtube/v3/"
MIN_VIEWS, MIN_HOURS = 50, 48
# owner.md 2026-11-22 11 AM: kept public on purpose (the website embeds them)
KEEP = {"vJDnv7_7Hcs": "website embed (launch checklist)", "YqnShunG7WY": "website embed (best settings)",
        "GjhaJdjHR4Q": "website embed (map size)"}
WRITABLE = ("privacyStatus", "embeddable", "license", "publicStatsViewable", "selfDeclaredMadeForKids",
            "containsSyntheticMedia")


def get(tok, path, **q):
    return req("GET", API + path + "?" + urlencode(q), tok)[0]


def public_shorts(tok, channel_id, limit=50):
    ch = get(tok, "channels", part="contentDetails", id=channel_id)["items"][0]
    up = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids = [i["contentDetails"]["videoId"] for i in
           get(tok, "playlistItems", part="contentDetails", playlistId=up, maxResults=limit).get("items", [])]
    out = []
    for v in get(tok, "videos", part="snippet,statistics,status,contentDetails", id=",".join(ids)).get("items", []):
        if v["status"].get("privacyStatus") != "public":
            continue
        secs = _seconds(v["contentDetails"].get("duration", ""))
        out.append({"id": v["id"], "title": v["snippet"]["title"], "published": v["snippet"]["publishedAt"],
                    "views": int(v["statistics"].get("viewCount", 0)), "seconds": secs,
                    "short": secs <= 180 and "#shorts" in v["snippet"]["title"].lower() or secs <= 60,
                    "status": v["status"]})
    return out


def _seconds(iso):
    m = re.fullmatch(r"P(?:\d+D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    return (int(m.group(1) or 0) * 3600 + int(m.group(2) or 0) * 60 + int(m.group(3) or 0)) if m else 0


def review(videos, ups, now=None):
    """(flops, skipped): flops = public Shorts MIN_HOURS+ old under MIN_VIEWS views, each with its pattern tags."""
    now = now or dt.datetime.now(dt.timezone.utc)
    flops, skipped = [], []
    for v in videos:
        age = (now - dt.datetime.fromisoformat(v["published"].replace("Z", "+00:00"))).total_seconds() / 3600
        if not v["short"] or age < MIN_HOURS or v["views"] >= MIN_VIEWS:
            continue
        base = scorecard.tags({**v, "published": v["published"]})
        if v["id"] in KEEP:
            skipped.append((v, KEEP[v["id"]]))
        elif base["kind"] == "campaign clip":
            skipped.append((v, "campaign clip (submitted to its campaign; owner kept them)"))
        else:
            flops.append({**v, "age_h": round(age), **base, **scorecard.script_tags(v["id"], ups)})
    return flops, skipped


def pattern(f):
    return (f"{f.get('format')}, {f.get('picture', '?')}, opener {f.get('opener', '?')}, title hook {f.get('hook')}, "
            f"{f.get('length')}, posted {f.get('slot (ET)')}")


def hide(tok, v, ups, today):
    status = {k: v["status"][k] for k in WRITABLE if k in v["status"]}
    status["privacyStatus"] = "private"
    req("PUT", API + "videos?part=status", tok, {"id": v["id"], "status": status})
    check = get(tok, "videos", part="status", id=v["id"])["items"][0]["status"]["privacyStatus"]
    if v["id"] in ups:
        ups[v["id"]]["hidden"] = (f"{today}: set private by studio.flops ({v['views']} views after {v['age_h']} h; "
                                  f"rule: under {MIN_VIEWS} after {MIN_HOURS} h). Not deleted.")
    return check


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--apply", action="store_true", help="main chat only: set the flops private and log the lessons")
    a = ap.parse_args()
    tok = token()
    ups_file = LEARN / "uploads.json"
    ups = json.loads(ups_file.read_text())
    flops, skipped = review(public_shorts(tok, channel_ids()["en"]), ups)
    today = dt.date.today().isoformat()
    print(f"# Flop review ({today}): public Shorts {MIN_HOURS} h+ old with under {MIN_VIEWS} views\n")
    if not flops:
        print("- none: every public Short that's 48 h+ old has 50+ views")
    for f in flops:
        print(f"- {f['views']} views at {f['age_h']} h · {f['id']} · {f['title'][:60]}\n    pattern: {pattern(f)}")
    for v, why in skipped:
        print(f"- kept: {v['id']} {v['title'][:50]} ({v['views']} views): {why}")
    if not flops or not a.apply:
        if flops:
            print("\nMain chat: `python -m studio.flops --apply` sets these private (never deletes) and logs the lessons.")
        return
    lessons = []
    for f in flops:
        state = hide(tok, f, ups, today)
        print(f"  set {f['id']} -> {state}")
        lessons.append(f"- {today} flop review: \"{f['title'][:70]}\" had {f['views']} views at {f['age_h']} h "
                       f"({pattern(f)}); set private (not deleted).")
    ups_file.write_text(json.dumps(ups, indent=1, ensure_ascii=False))
    with open(LEARN / "lessons.md", "a") as fh:
        fh.write("\n" + "\n".join(lessons) + "\n")
    print(f"\nLogged {len(lessons)} lesson line(s) in content/learn/lessons.md; commit uploads.json + lessons.md.")


if __name__ == "__main__":
    sys.exit(main())
