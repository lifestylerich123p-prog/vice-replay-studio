"""YouTube's daily API quota: use all of it for what grows the channel, never run dry mid-day (Nov 21, 2026).

    python -m studio.quota            # today's units used/left, uploads that still fit, free posting slots (3 days)
    python -m studio.quota spare      # units left after today's free slots are filled (for extras like subtitle backfill)

The YouTube Data API documents 10,000 units a day per project, reset at midnight Pacific (3 AM ET), and ~2,500 units
for an upload with our extras (2 subtitle tracks, playlist, pinned comment). Real days disagree (Nov 21: 7 uploads, no
error), so limit() learns the usable number: a clean day raises it, a "quota used up" error pins it.
Every call the uploader makes is logged here (content/learn/quota.json, by Pacific day). Other runs (comment replies,
breaking news) spend from the same pool in their own containers, so the numbers are a floor: keep a margin.
Priority when units are short: new uploads in free slots > pinned comments > subtitle backfill > anything else.
"""
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "content" / "learn" / "quota.json"
PT, ET = ZoneInfo("America/Los_Angeles"), ZoneInfo("America/New_York")
DAILY = int(os.environ.get("YT_DAILY_QUOTA", "10000"))
UPLOAD = 1600 + 400 + 400 + 50 + 50  # insert + English and Spanish subtitles + playlist + pinned comment
MARGIN = 500  # other runs (auto-replies, breaking news) spend from the same pool


def cost(method, url):
    """Quota units of one YouTube Data API call (developers.google.com/youtube/v3/determine_quota_cost)."""
    if "upload_id=" in url:  # the resumable upload's second request (the bytes) is free
        return 0
    path = url.split("?")[0]
    m = re.search(r"/youtube/v3/([a-zA-Z]+)(?:/([a-zA-Z]+))?$", path)
    if not m:
        return 0
    res, sub = m.group(1), m.group(2)
    if method == "GET":
        return {"search": 100, "captions": 50}.get(res, 1)
    if res == "videos" and method == "POST":
        return 1600
    if res == "captions":
        return 400 if method == "POST" else 450
    if res == "thumbnails" or sub == "set":
        return 50
    return 50  # insert/update/delete of comments, playlists, playlistItems, channels, banners


def day():
    return dt.datetime.now(PT).date().isoformat()


def _load():
    try:
        return json.loads(LEDGER.read_text())
    except (OSError, ValueError):
        return {}


def _save(d):
    keep = sorted(d)[-14:]  # two weeks is plenty
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps({k: d[k] for k in keep}, indent=1))


def spend(method, url):
    units = cost(method, url)
    if not units:
        return
    d = _load()
    t = d.setdefault(day(), {"used": 0, "calls": {}})
    t["used"] += units
    m = re.search(r"/youtube/v3/([a-zA-Z/]+)", url.split("?")[0])
    key = f"{method} {m.group(1) if m else '?'}"
    t["calls"][key] = t["calls"].get(key, 0) + 1
    _save(d)


def mark_exhausted():
    """A real "quota used up" answer: remember how much we had spent, which is the project's actual daily limit."""
    spent = used_today()
    d = _load()
    t = d.setdefault(day(), {"used": 0, "calls": {}})
    t["exhausted_at_et"] = dt.datetime.now(ET).strftime("%H:%M")
    t["limit_seen"] = spent
    _save(d)


def limit():
    """The daily limit we can count on. YouTube documents 10,000 units, but on Nov 21, 2026 seven uploads with
    subtitles (~17,500 units by the documented costs) went through without an error, so the real number is learned:
    the most recent "quota used up" ceiling if we ever hit one, else the biggest day that finished without hitting it."""
    d = _load()
    seen = [v["limit_seen"] for k, v in sorted(d.items()) if v.get("limit_seen")]
    if seen:
        return seen[-1]
    fine = [max(v.get("used", 0), v.get("registry_est", 0)) for k, v in d.items() if k < day()]
    return max([DAILY] + fine)


def uploads_today():
    """Uploads the committed registry (content/learn/uploads.json) records for today's Pacific day, from any run."""
    try:
        reg = json.loads((ROOT / "content" / "learn" / "uploads.json").read_text())
    except (OSError, ValueError):
        return 0
    n = 0
    for rec in reg.values():
        try:
            t = dt.datetime.fromisoformat(str(rec.get("uploaded", ""))[:19]).replace(tzinfo=dt.timezone.utc)
        except ValueError:
            continue
        n += t.astimezone(PT).date().isoformat() == day()
    return n


def used_today():
    """Units spent today: what this machine logged, or the registry's uploads x UPLOAD if that is higher (calls made
    before logging existed, or from another container that committed its registry)."""
    d = _load()
    t = d.get(day(), {})
    if t.get("exhausted_at_et"):
        return t.get("limit_seen") or DAILY
    est = uploads_today() * UPLOAD
    if est and est != t.get("registry_est"):  # remembered, so a day that ends without an error teaches limit()
        d.setdefault(day(), {"used": 0, "calls": {}})["registry_est"] = est
        _save(d)
    return max(t.get("used", 0), est)


def left_today():
    return max(0, limit() - used_today() - MARGIN)


def reset_in():
    now = dt.datetime.now(PT)
    nxt = dt.datetime.combine(now.date() + dt.timedelta(days=1), dt.time(0), PT)
    h, rem = divmod(int((nxt - now).total_seconds()), 3600)
    return f"{h} h {rem // 60} min (midnight Pacific = 3 AM ET)"


DAYTIME = ("9:30 AM", "11:00 AM", "12:30 PM")  # Nov 22 data (21 Shorts since launch): 6-11 AM median 16 views/h,
# 11 AM-2 PM 10, 2-6 PM 2.7, 6 PM-6 AM 1.9. Fill these first; afternoon/evening slots are for big news or long videos.


def slots_for(d):
    """The posting slots of a day (ET): the CLAUDE.md / review_page schedule plus the 11 AM Short slot."""
    from .review_page import extra_time, times_for
    main, short, news = times_for(d)
    day = {short, extra_time(d), main, news} | ({"11:00 AM"} if d.weekday() < 5 else set())
    return sorted(day, key=lambda s: dt.datetime.strptime(s, "%I:%M %p"))


def is_daytime(slot):
    t = dt.datetime.strptime(slot, "%I:%M %p").time()
    return dt.time(6) <= t < dt.time(14)


def scheduled(tok=None):
    """{date: [ET datetime, ...]} of videos scheduled to go public (private + publishAt) on the channel."""
    from .youtube_upload import req, token
    tok = tok or token()
    ch, _ = req("GET", "https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&mine=true", tok)
    up = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    r, _ = req("GET", f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=50&playlistId={up}", tok)
    ids = [i["contentDetails"]["videoId"] for i in r.get("items", [])]
    v, _ = req("GET", "https://youtube.googleapis.com/youtube/v3/videos?part=status&id=" + ",".join(ids), tok)
    out = {}
    for it in v.get("items", []):
        pa = it["status"].get("publishAt")
        if pa and it["status"].get("privacyStatus") == "private":
            when = dt.datetime.fromisoformat(pa.replace("Z", "+00:00")).astimezone(ET)
            out.setdefault(when.date(), []).append(when)
    return out


def free_slots(sched, days=3):
    """[(date, [free slot labels])] for today and the next days; a slot counts as taken by a video within 45 min."""
    today = dt.datetime.now(ET).date()
    out = []
    for k in range(days):
        d = today + dt.timedelta(days=k)
        taken = sched.get(d, [])
        free = []
        for s in slots_for(d):
            at = dt.datetime.combine(d, dt.datetime.strptime(s, "%I:%M %p").time(), ET)
            if at <= dt.datetime.now(ET) + dt.timedelta(minutes=30):
                continue
            if not any(abs((t - at).total_seconds()) <= 2700 for t in taken):  # slots are 90 min apart
                free.append(s)
        out.append((d, free))
    return out


def spare_units(today_free):
    """Units left after filling today's free slots: what extras (subtitle backfill) may use."""
    return max(0, left_today() - today_free * UPLOAD)


def main():
    left = left_today()
    print(f"YouTube quota today (Pacific day {day()}): ~{used_today():,} of ~{limit():,} used (estimate: documented "
          f"costs; the limit is learned from real days); ~{left:,} usable, keeping {MARGIN} for other runs. "
          f"Resets in {reset_in()}.")
    print(f"Room for {left // UPLOAD} more upload(s) today (~{UPLOAD:,} units each with subtitles, playlist, comment).")
    sched = scheduled()
    plan = free_slots(sched)
    print("\nFree posting slots (CLAUDE.md schedule + 11 AM; a video within 45 min of a slot fills it):")
    for d, free in plan:
        n = len(sched.get(d, []))
        daylist = [x for x in free if is_daytime(x)]
        late = [x for x in free if not is_daytime(x)]
        print(f"- {d:%a %b %d}: {n} scheduled; free daytime: {', '.join(daylist) or 'none'}"
              + (f"; later (big news / long video only): {', '.join(late)}" if late else ""))
    if len(sys.argv) > 1 and sys.argv[1] == "spare":
        print(f"\nSpare units after today's free slots: {spare_units(len(plan[0][1])):,}")


if __name__ == "__main__":
    main()
