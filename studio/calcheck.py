"""Calendar check for the publishing queue (owner Nov 26, Phase 5 #1: "November 30, 2026, is Monday, not Sunday. Check
the publishing queue for mismatches between calendar dates, weekday labels, time zones and scheduled timestamps").

    python -m studio.calcheck            # queue vs calendar vs gate records (free, no network)
    python -m studio.calcheck --live     # also YouTube's real publishAt for videos the gate marked SCHEDULED

Checks: every slot is a real date with a valid time; future gate-bound slots are plan slots (EN 8:00 AM / 6:00 PM,
ES 12:30 PM / 7:00 PM); the gate's approved slot matches the queue (else the upload would be refused); weekday words
written next to a date in notes ("Sat Nov 28") match the real weekday; ET -> UTC uses America/New_York (DST-safe).
Reports must name weekdays with `label(date)`, never by hand.
"""
import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
ET = ZoneInfo("America/New_York")
QUEUE = ROOT / "content" / "learn" / "approved_queue.json"
WEEKDAY_NOTE = re.compile(r"\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*\.? (Nov|Dec|Jan|Feb) (\d{1,2})\b")
MONTHS = {"Nov": 11, "Dec": 12, "Jan": 1, "Feb": 2}


def label(date_s):
    """'Mon Nov 30' from '2026-11-30' (use this in every report)."""
    d = dt.date.fromisoformat(date_s)
    return d.strftime("%a %b ") + str(d.day)


def to_utc(date_s, time_s):
    local = dt.datetime.strptime(f"{date_s} {time_s}", "%Y-%m-%d %I:%M %p").replace(tzinfo=ET)
    return local.astimezone(dt.timezone.utc)


def check(queue=None, store=None, now=None, year=2026):
    from . import approvals
    q = queue if queue is not None else json.loads(QUEUE.read_text())
    store = store if store is not None else approvals._load()
    now = now or dt.datetime.now(ET)
    problems, rows = [], []
    slots = {"en": approvals.auto_cfg("youtube-en")["slots"], "es": approvals.auto_cfg("youtube-es")["slots"]}
    uploaded = {}
    for lang, f in (("en", "uploads.json"), ("es", "uploads-es.json")):
        try:
            reg = json.loads((ROOT / "content" / "learn" / f).read_text())
        except (OSError, ValueError):
            reg = {}
        uploaded[lang] = {(r.get("slug"), r.get("item", "short")) for r in reg.values()}
    for it in q["items"]:
        key = it.get("item", "short")
        for lang in ("en", "es"):
            s = it.get(lang)
            if not s:
                continue
            where = f"{it['slug']} ({lang})"
            try:
                when = dt.datetime.strptime(f"{s[0]} {s[1]}", "%Y-%m-%d %I:%M %p").replace(tzinfo=ET)
            except (ValueError, TypeError, IndexError):
                problems.append(f"{where}: not a valid date/time {s}")
                continue
            future = when > now
            rec = store.get(approvals.key_of(it["slug"], key, "youtube-es" if lang == "es" else "youtube-en"))
            already = (it["slug"], key) in uploaded[lang]  # uploaded before the gate: YouTube holds its time
            if future and key == "short" and not already and s[1] not in slots[lang] and not (
                    rec and rec.get("state") in ("SCHEDULED", "PUBLISHED")):
                problems.append(f"{where}: {label(s[0])} {s[1]} is not a plan slot ({' / '.join(slots[lang])}); "
                                "the gate will hold it")
            if rec and rec.get("publish") and rec["publish"] != "now" and list(rec["publish"]) != list(s) and \
                    rec.get("state") in ("AUTO_APPROVED", "UPLOADING", "SCHEDULED"):
                problems.append(f"{where}: queue says {label(s[0])} {s[1]} but the gate approved {rec['publish']} "
                                f"({rec['state']}): evaluate again before the upload")
            if future:
                rows.append((when, lang, it["slug"], label(s[0]), s[1], to_utc(*s).strftime("%Y-%m-%d %H:%M UTC")))
        for k, v in it.items():
            if isinstance(v, str):
                for m in WEEKDAY_NOTE.finditer(v):
                    wd, mon, day = m.group(1), MONTHS[m.group(2)], int(m.group(3))
                    y = year + (1 if mon < 6 and year == 2026 else 0)
                    real = dt.date(y, mon, day).strftime("%a")
                    if real != wd[:3]:
                        problems.append(f"{it['slug']}: note '{m.group(0)}' in \"{k}\": {m.group(2)} {day} is a {real}")
    return problems, sorted(rows)


def live(store=None):
    """YouTube's real publishAt for SCHEDULED videos vs the approved slot."""
    from . import approvals
    store = store if store is not None else approvals._load()
    out = []
    for k, r in store.items():
        if r.get("state") not in ("SCHEDULED",) or not r.get("video_id") or r.get("publish") in (None, "now"):
            continue
        plat = r.get("platform")
        try:
            if plat == "youtube-es":
                from . import youtube_es as y
                tok = y.token_for(y.config().get("vice-replay-es", {}).get("channel_id"), y.ENV)
            else:
                from .youtube_upload import token
                tok = token()
            from .youtube_upload import req
            v, _ = req("GET", "https://youtube.googleapis.com/youtube/v3/videos?part=status,snippet&id=" + r["video_id"], tok)
        except (SystemExit, Exception) as e:  # noqa: BLE001
            out.append(f"{k}: couldn't read YouTube ({str(e)[:80]})")
            continue
        items = v.get("items") or []
        if not items:
            out.append(f"{k}: video {r['video_id']} not found on YouTube")
            continue
        pa = items[0]["status"].get("publishAt")
        want = to_utc(*r["publish"]).strftime("%Y-%m-%dT%H:%M")
        if not pa or not pa.startswith(want):
            out.append(f"{k}: YouTube publishAt {pa} != approved {want} UTC ({label(r['publish'][0])} {r['publish'][1]} ET)")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m studio.calcheck")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--days", type=int, default=7)
    a = ap.parse_args(argv)
    problems, rows = check()
    end = dt.datetime.now(ET) + dt.timedelta(days=a.days)
    print(f"Next {a.days} days (ET, with UTC):")
    for when, lang, slug, lab, t, utc in rows:
        if when <= end:
            print(f"  {lab} {t:>8} ET  {lang.upper()}  {slug}  ({utc})")
    if a.live:
        problems += live()
    print("\n".join(["PROBLEMS:"] + [f"  - {p}" for p in problems]) if problems else "calendar OK")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
