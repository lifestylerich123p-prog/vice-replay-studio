"""Use the rest of the day's YouTube quota (owner, Nov 22 night: "every posting credit must be used posting or answering
comments").

    python -m studio.spend           # plan: units left today, which approved Shorts fit, how many comments wait
    python -m studio.spend upload    # MAIN CHAT: upload the approved Shorts that fit, earliest slot first (scheduled)

Order: (1) approved Shorts from content/learn/approved_queue.json that aren't up yet, uploaded early and scheduled
for their own slots (each upload is checked with `studio.vice publish` first; studio.ship's duplicate guard skips
anything already posted); (2) every unanswered comment on both channels (`studio.replies list` / `list --es`, the
standing auto-reply approval). Subtitle files on Shorts are off (config/channel.json `shorts_subtitles`), so a Short
costs ~1,750 units per channel. Facts are re-checked by the chat right before running `upload`.
"""
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

from . import quota

ROOT = Path(__file__).resolve().parent.parent
LEARN = ROOT / "content" / "learn"
QUEUE = LEARN / "approved_queue.json"
PER_CHANNEL = 160  # videos.insert is billed to its own uploads bucket (100/day) since 2026; playlist 50 + thumbnail 50 + reads
KEEP = 300          # left for comments posted after Shorts go live


def _registry(name):
    try:
        return {(r.get("slug"), r.get("item")) for r in json.loads((LEARN / name).read_text()).values()}
    except (OSError, ValueError):
        return set()


def winners_rule():
    """config/channel.json `spanish_winners_only` (owner Nov 23): Spanish versions only for English Shorts that did well."""
    try:
        r = json.loads((ROOT / "config" / "channel.json").read_text()).get("spanish_winners_only") or {}
    except (OSError, ValueError):
        return None
    return r if r.get("on") else None


def es_paused_until():
    """config/channel.json `spanish_youtube_paused_until` (owner Nov 26 "DO IT": the Spanish YouTube channel had 37 views
    in 12 videos, so no Spanish YouTube uploads for a week; Spanish goes to TikTok). A date "YYYY-MM-DD" or None."""
    try:
        d = json.loads((ROOT / "config" / "channel.json").read_text()).get("spanish_youtube_paused_until")
    except (OSError, ValueError):
        return None
    return d if d and d > dt.date.today().isoformat() else None


def es_paused(it):
    """True when this item's Spanish slot falls inside the pause (it is not uploaded; studio.doctor lists it)."""
    until = es_paused_until()
    return bool(until and it.get("es") and it["es"][0] < until)


def es_waits(it):
    """True while a Spanish version still has to prove itself on the English channel (winners-only rule)."""
    if it.get("es_only") or not winners_rule():
        return False
    return not str(it.get("es_status", "")).startswith("winner")


def es_threshold(rule, days=7):
    """max(rule min, median views at 24 h of our English Shorts from the last `days` days)."""
    import statistics
    from . import scorecard
    try:
        snap = json.loads((LEARN / "channel.json").read_text())
    except (OSError, ValueError):
        return rule.get("min_views_24h", 150)
    hist, now, v24 = scorecard.load_history(), dt.datetime.now(dt.timezone.utc), []
    for v in snap.get("videos", []):
        pub = scorecard.ts(v["published"])
        if v.get("type") == "Short" and dt.timedelta(hours=24) <= now - pub <= dt.timedelta(days=days):
            x = scorecard.views_at(hist, v["id"], pub)
            if x is not None:
                v24.append(x)
    med = statistics.median(v24) if len(v24) >= 3 else 0
    return max(rule.get("min_views_24h", 150), int(med))


def es_times():
    """The Spanish channel's slots = the gate's `auto_publish_es.slots` (Nov 26: 12:30 PM / 7:00 PM ET test slots), so a
    winner is never booked at a time the gate would hold."""
    from . import approvals
    return tuple(approvals.auto_cfg("youtube-es")["slots"])


def next_es_slot(after, taken):
    """First free Spanish daytime slot at or after `after` (ET datetime), not in `taken` {(date, time)}; never inside a
    Spanish YouTube pause (`spanish_youtube_paused_until`)."""
    until = es_paused_until()
    if until:
        after = max(after, dt.datetime.strptime(until, "%Y-%m-%d").replace(tzinfo=quota.ET))
    day = after.date()
    for _ in range(14):
        for t in es_times():
            when = dt.datetime.strptime(f"{day} {t}", "%Y-%m-%d %I:%M %p").replace(tzinfo=quota.ET)
            if when >= after and (str(day), t) not in taken:
                return [str(day), t]
        day += dt.timedelta(days=1)
    return None


def es_review(fetch=None, now=None):
    """Winners-only rule: for each queued Short whose Spanish version waits, look at the English Short once it's 24 h
    old. Winner -> book the Spanish version in the next free Spanish slot; below the bar -> skip it (logged in the queue)."""
    rule = winners_rule()
    if not rule:
        return []
    q = json.loads(QUEUE.read_text())
    es_done = _registry("uploads-es.json")
    try:
        reg = json.loads((LEARN / "uploads.json").read_text())
    except (OSError, ValueError):
        reg = {}
    now = now or dt.datetime.now(quota.ET)
    taken = {tuple(i["es"]) for i in q["items"] if i.get("es") and str(i.get("es_status", "")).startswith("winner")}
    taken |= {tuple(i["es"]) for i in q["items"] if i.get("es") and i.get("es_only")}
    notes, bar = [], None
    for it in q["items"]:
        key = (it["slug"], it.get("item", "short"))
        if not it.get("es") or it.get("es_only") or key in es_done or it.get("es_status"):
            continue
        vid = next((v for v, r in reg.items() if (r.get("slug"), r.get("item")) == key), None)
        if not vid:
            continue  # English not up yet
        pub, views = (fetch or _en_stats)(vid)
        if pub is None or now - pub < dt.timedelta(hours=24):
            continue
        bar = bar if bar is not None else es_threshold(rule)
        if views >= bar:
            slot = next_es_slot(max(now, pub + dt.timedelta(hours=24)) + dt.timedelta(hours=1), taken)
            it["es"], it["es_status"] = slot, f"winner: {views} views at {int((now - pub).total_seconds() // 3600)} h (bar {bar})"
            taken.add(tuple(slot))
            notes.append(f"ES winner: {it['slug']} -> {slot[0]} {slot[1]} ({views} views, bar {bar})")
            try:
                segs = json.loads((ROOT / "episodes" / f"{it['slug']}.json").read_text()).get("short") or []
                if segs and not all(x.get("audio_es") for x in segs):
                    notes.append(f"  needs the Viral Adam Spanish voice first: one line per segment (CLAUDE.md), then "
                                 f"python -m studio.make_video episodes/{it['slug']}.json --short --es")
            except (OSError, ValueError):
                pass
        else:
            it["es_status"] = f"skipped: {views} views at {int((now - pub).total_seconds() // 3600)} h (bar {bar})"
            notes.append(f"ES skipped: {it['slug']} ({views} views < {bar})")
    if notes:
        QUEUE.write_text(json.dumps(q, indent=1, ensure_ascii=False))
    return notes


def _en_stats(vid):
    """(publish time ET, views) of an English video (owner token, 1 unit)."""
    from .youtube_upload import req, token
    r = req("GET", f"https://youtube.googleapis.com/youtube/v3/videos?part=status,snippet,statistics&id={vid}", token())
    d = r[1] if isinstance(r, tuple) and isinstance(r[1], dict) else (r[0] if isinstance(r, tuple) else r)
    items = (d or {}).get("items") or []
    if not items or items[0]["status"].get("privacyStatus") != "public":
        return None, 0
    pub = dt.datetime.fromisoformat(items[0]["snippet"]["publishedAt"].replace("Z", "+00:00")).astimezone(quota.ET)
    return pub, int(items[0]["statistics"].get("viewCount", 0))


def pending():
    """Approved queue items with the channels still to upload: [(item, needs_en, needs_es)], earliest slot first."""
    q = json.loads(QUEUE.read_text())["items"]
    en, es = _registry("uploads.json"), _registry("uploads-es.json")
    out = []
    for it in q:
        key = (it["slug"], it.get("item", "short"))
        need_en = bool(it.get("en")) and not it.get("es_only") and key not in en
        need_es = bool(it.get("es")) and key not in es and not es_waits(it) and not es_paused(it)
        if need_en or need_es:
            out.append((it, need_en, need_es))
    first = lambda it: min(dt.datetime.strptime(f"{d} {t}", "%Y-%m-%d %I:%M %p") for d, t in
                           [x for x in (it.get("en"), it.get("es")) if x])
    return sorted(out, key=lambda x: first(x[0]))


def plan():
    for n in es_review():
        print(n)
    left = quota.left_today()
    print(f"YouTube units left today: ~{left:,} (resets in {quota.reset_in()})")
    budget = left - KEEP
    fits = []
    for it, ne, ns in pending():
        cost = PER_CHANNEL * (ne + ns)
        if cost <= budget:
            fits.append((it, ne, ns))
            budget -= cost
    rest = [x for x in pending() if x not in fits]
    for it, ne, ns in fits:
        print(f"- FITS: {it['slug']} ({'EN ' + ' '.join(it['en']) if ne else ''}{' + ' if ne and ns else ''}"
              f"{'ES ' + ' '.join(it['es']) if ns else ''})")
    for it, ne, ns in rest:
        print(f"- waits: {it['slug']}")
    print(f"After uploads: ~{max(0, budget):,} units for comment replies (50 each): run python -m studio.replies list "
          f"and list --es, answer every real comment, then post.")
    return fits


def commands(it, ne, ns):
    ep = f"episodes/{it['slug']}.json"
    key = it.get("item", "short")
    if ne and ns and it["en"] == it["es"]:
        return [["python", "-m", "studio.ship", ep, "--upload", key, "--date", it["en"][0], "--at", it["en"][1]]]
    cmds = []
    if ne:
        cmds.append(["python", "-m", "studio.ship", ep, "--upload", key, "--date", it["en"][0], "--at", it["en"][1],
                     "--no-es-upload"])
    if ns:
        cmds.append(["python", "-m", "studio.youtube_es", ep, "--approve", key, "--date", it["es"][0], "--at", it["es"][1]])
    return cmds


def renders_needed(it, ne, ns):
    """Short videos the upload needs that aren't on disk (output/ isn't committed; a fresh container has none).
    Everything to rebuild them is committed: the episode, its cards and any voice files in media/voice/."""
    slug, key = it["slug"], it.get("item", "short")
    out = ROOT / "output" / slug
    if key == "main":  # the weekly hub video (Nov 23)
        return [] if (out / f"{slug}.mp4").exists() else [["python", "-m", "studio.make_video", f"episodes/{slug}.json"]]
    if key != "short":
        return []
    need = []
    src = ROOT / "episodes" / f"{slug}.json"

    def stale(video):  # missing, or older than its episode (e.g. a map-series number changed: studio/mapseries.py)
        return not video.exists() or (src.exists() and video.stat().st_mtime < src.stat().st_mtime)
    if ne and stale(out / f"{slug}-short.mp4"):
        need.append(["python", "-m", "studio.make_video", f"episodes/{slug}.json", "--short"])
    if ns and stale(out / f"{slug}-short-es.mp4"):
        need.append(["python", "-m", "studio.make_video", f"episodes/{slug}.json", "--short", "--es"])
    return need


def upload():
    # Nov 26 (owner APPROVE ALL: numbered map series): number the spots right before uploading, so a Short booked in
    # between renumbers only the ones not uploaded yet; renders_needed() then re-renders those (episode is newer)
    try:
        from . import mapseries
        for m in mapseries.number():
            print(f"map series: {m['slug']} is now spot #{m['n']} (re-rendered before upload)")
    except (OSError, ValueError, KeyError) as e:
        print(f"! map series numbering skipped: {type(e).__name__}")
    # Owner, Nov 26 ("Autonomous publishing authorization update"): a video posts automatically only when every
    # mandatory check passes (studio/approvals.py); anything uncertain is held for review, never posted.
    from . import approvals
    ok, why = approvals.tests_ok()
    if not ok:
        print(f"$ python -m studio.approvals tests ({why})")
        passed, tail = approvals.run_tests()
        print(("tests passed: " if passed else "! tests FAILED (nothing posts until they pass): ") + tail)
    held = []
    for it, ne, ns in plan():
        for cmd in renders_needed(it, ne, ns):
            print("$", " ".join(cmd), "(video missing or older than its episode: rendering it first)")
            subprocess.run(cmd, cwd=ROOT)
        # each channel is checked on its own (English: 8 AM / 6 PM map plan; Spanish: its own identity, owner Nov 26)
        for lang, need, platform in (("en", ne, "youtube-en"), ("es", ns, "youtube-es")):
            if not need:
                continue
            try:
                rec = approvals.evaluate(ROOT / "episodes" / f"{it['slug']}.json", it.get("item", "short"), platform,
                                         tuple(it[lang]))
            except approvals.Blocked as e:
                rec = {"state": "BLOCKED", "blockers": [str(e)]}
            if rec["state"] != "AUTO_APPROVED":
                reasons = "; ".join(rec.get("blockers") or rec.get("reviews") or [])
                print(f"! hold {it['slug']} {platform} ({rec['state']}): {reasons[:300]}")
                held.append((dict(it, en=it[lang]), reasons))
                if lang == "en":
                    ne = False
                else:
                    ns = False
                continue
            print(f"AUTO_APPROVED {it['slug']} {platform} for {' '.join(it[lang])} ET: all publishing conditions passed")
        if not (ne or ns):
            continue
        for cmd in commands(it, ne, ns):
            print("$", " ".join(cmd))
            r = subprocess.run(cmd, cwd=ROOT)
            if r.returncode:
                print(f"! {it['slug']}: upload step failed (exit {r.returncode}); stopping")
                return
    if held:
        print(f"\nHELD FOR REVIEW ({len(held)}): " + "; ".join(f"{h['slug']} {' '.join(h['en'])}" for h, _ in held))
    # Nov 24: the backup titles (option 2, a "catch" angle on the map Shorts) were never used because nothing ran the
    # swap. Underperformers 24-96 h old get their option-2 title once (owner's standing approval; ~60 units each).
    try:
        from . import quota
        if quota.left_today() > 800:
            print("$ python -m studio.title_swap")
            subprocess.run(["python", "-m", "studio.title_swap"], cwd=ROOT)
        else:
            print("title swap skipped tonight: under 800 units left")
    except Exception as e:  # noqa: BLE001 - never block the upload run on the swap
        print(f"title swap skipped ({type(e).__name__})")
    print("Done. Schedule each printed COMMENTS TO POST for 10 min after its slot, commit uploads*.json, quota.json.")


if __name__ == "__main__":
    upload() if sys.argv[1:2] == ["upload"] else plan()
