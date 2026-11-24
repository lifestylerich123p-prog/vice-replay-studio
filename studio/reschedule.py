"""Move an uploaded video that is still SCHEDULED (private + publishAt) to a new time (main control chat only).

    python -m studio.reschedule <video_id> "2026-11-28 12:30"   # new time, US Eastern
    python -m studio.reschedule <video_id> --show               # print its current status
    python -m studio.reschedule <video_id> --unschedule         # keep it PRIVATE with no publish time (never deletes)

Nov 24 (owner: "start posting what will work"): lets the morning swap move a weak scheduled Short out of a prime slot
so a stronger one (search demand, map spot, comparison, tier list) can take it. Reads the video's current status first
and sends it back with only publishAt changed, so made-for-kids, license and embedding stay exactly as they were.
Refuses a video that is already public or has no publish time. Cost: ~51 units (list 1 + update 50).
"""
import argparse
import datetime as dt
import json
import sys
from zoneinfo import ZoneInfo

from .youtube_upload import req, token

YT = "https://youtube.googleapis.com/youtube/v3/"
ET = ZoneInfo("America/New_York")
READ_ONLY = {"uploadStatus", "failureReason", "rejectionReason", "madeForKids"}


def when_utc(text):
    """"2026-11-28 12:30" (ET) -> "2026-11-28T17:30:00Z"."""
    t = dt.datetime.strptime(text.strip(), "%Y-%m-%d %H:%M").replace(tzinfo=ET)
    if t <= dt.datetime.now(ET) + dt.timedelta(minutes=15):
        sys.exit(f"{text} ET is in the past or less than 15 minutes away: pick a later time")
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def status_of(tok, vid):
    items = req("GET", YT + f"videos?part=status,snippet&id={vid}", tok)[0].get("items") or []
    if not items:
        sys.exit(f"{vid}: not found on the channel")
    return items[0]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("when", nargs="?", help='new time in US Eastern, "YYYY-MM-DD HH:MM"')
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--unschedule", action="store_true", help="take it off the schedule: stays private, nothing deleted")
    a = ap.parse_args()
    tok = token()
    item = status_of(tok, a.video)
    st, title = item["status"], item["snippet"]["title"]
    if a.show or (not a.when and not a.unschedule):
        print(json.dumps({"title": title, **{k: st.get(k) for k in ("privacyStatus", "publishAt")}}, indent=1))
        return
    if st.get("privacyStatus") != "private" or not st.get("publishAt"):
        sys.exit(f"{a.video} ({title}) is {st.get('privacyStatus')} with no publish time: not a scheduled video, left as is")
    if a.unschedule:  # Nov 24 (owner: "cut the remaining fact Shorts"): private, no publishAt; the file stays on YouTube
        body = {"id": a.video, "status": {k: v for k, v in st.items() if k not in READ_ONLY | {"publishAt"}}}
        body["status"]["privacyStatus"] = "private"
        out = req("PUT", YT + "videos?part=status", tok, body)[0]
        left = (out.get("status") or {}).get("publishAt")
        print(f"{a.video} ({title}): unscheduled, stays private" + (f" (YouTube still shows {left}!)" if left else ""))
        if left:
            sys.exit("YouTube kept a publish time: check it in Studio")
        return
    new = when_utc(a.when)
    body = {"id": a.video, "status": {**{k: v for k, v in st.items() if k not in READ_ONLY}, "publishAt": new}}
    out = req("PUT", YT + "videos?part=status", tok, body)[0]
    got = (out.get("status") or {}).get("publishAt")
    print(f"{a.video} ({title}): {st['publishAt']} -> {got}")
    if got != new:
        sys.exit("YouTube returned a different time than asked: check it in Studio")


if __name__ == "__main__":
    main()
