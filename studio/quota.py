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
UPLOAD = 50 + 50 + 50  # playlist + pinned comment + thumbnail (no subtitle files on Shorts since Nov 22)
# Nov 26 (owner directive v2.0): videos.insert is now billed to a separate "uploads" bucket (1 unit, 100 uploads a
# day per project, per Google's 2026 quota docs as summarised by several API guides; the old 1,600-unit figure is
# outdated). It no longer counts against the 10,000-unit pool, so uploads are tracked by count (UPLOADS_PER_DAY).
UPLOADS_PER_DAY = 100
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
        return 0  # separate uploads bucket (see UPLOADS_PER_DAY)
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


GATE_DEFAULT = {"en": ("8:00 AM", "6:00 PM"), "es": ("12:30 PM", "7:00 PM")}


def gate_slots(lang="en"):
    """The publishing slots (ET) from config/channel.json `auto_publish` / `auto_publish_es` (owner Phase 10, Nov 26:
    English 8:00 AM + 6:00 PM, Spanish 12:30 PM + 7:00 PM, max 2 a day). The config is the one source of truth."""
    try:
        cfg = json.loads((ROOT / "config" / "channel.json").read_text())
        slots = (cfg.get("auto_publish" if lang == "en" else "auto_publish_es") or {}).get("slots")
    except (OSError, ValueError):
        slots = None
    return tuple(slots or GATE_DEFAULT[lang])


def slots_for(d, lang="en"):
    """The publishing slots of a day (ET): the gate's slots (same every day; old 9:30/11:00/12:30/3:30/8:30 retired)."""
    return sorted(gate_slots(lang), key=lambda s: dt.datetime.strptime(s, "%I:%M %p"))


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


def reserved(lang="en"):
    """{date: [ET datetime]} of approved Shorts still waiting in content/learn/approved_queue.json (Nov 23: the free-slot
    list showed Tue/Wed as empty while 10 approved Shorts were booked for them)."""
    try:
        from .spend import pending
        items = pending()
    except Exception:
        return {}
    out = {}
    for it, ne, ns in items:
        slot = it.get("en") if lang == "en" and ne else it.get("es") if lang == "es" and ns else None
        if slot:
            when = dt.datetime.combine(dt.date.fromisoformat(slot[0]), dt.datetime.strptime(slot[1], "%I:%M %p").time(), ET)
            out.setdefault(when.date(), []).append(when)
    return out


def free_slots(sched, days=3, lang="en"):
    """[(date, [free slot labels])] for today and the next days; a slot counts as taken by a video within 45 min,
    scheduled on YouTube or booked in the approved queue."""
    today = dt.datetime.now(ET).date()
    booked = reserved(lang)
    out = []
    for k in range(days):
        d = today + dt.timedelta(days=k)
        taken = sched.get(d, []) + booked.get(d, [])
        free = []
        for s in slots_for(d, lang):
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
    print("\nFree publishing slots (the gate's slots from config/channel.json; a video within 45 min of a slot fills it):")
    for d, free in plan:
        n = len(sched.get(d, []))
        print(f"- {d:%a %b %d}: {n} scheduled; free: {', '.join(free) or 'none'}")
    if len(sys.argv) > 1 and sys.argv[1] == "spare":
        print(f"\nSpare units after today's free slots: {spare_units(len(plan[0][1])):,}")


if __name__ == "__main__":
    main()
