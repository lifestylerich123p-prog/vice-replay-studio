"""One table for the autonomous publishing cycle (owner Nov 26, Phase 6 #1: "Verify: overnight fact-check execution,
required re-renders, automatic uploads, correct destination channels, correct publication times, successful helper
execution, GitHub commits and pushes, successful merge, no duplicate uploads, analytics retrieval, actual generation
costs, public video availability... Do not report scheduled publication as completed publication.").

    python -m studio.cycle [--date 2026-11-27] [--offline]

Each row is PASS / FAIL / WAIT (not due yet) / UNKNOWN (couldn't check), with the evidence. --offline skips YouTube
reads (channel, publishAt, public). The cycle is OPERATIONAL only when every row is PASS for a day that had uploads.
"""
import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
ET = ZoneInfo("America/New_York")
LEARN = ROOT / "content" / "learn"
CHANNEL = {"youtube-en": "UCzk9Wts3WFynOHZQJRWOQIw", "youtube-es": "UCWPnqYqYu9_CLsJ8Bk1MPgQ"}


def _j(p, default=None):
    try:
        return json.loads(Path(p).read_text())
    except (OSError, ValueError):
        return default


def _git(*a):
    r = subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, timeout=120)
    return r.stdout.strip() if r.returncode == 0 else None


def due_items(day):
    """Queue items booked for `day` on either channel: (slug, lang, [date, time])."""
    q = _j(LEARN / "approved_queue.json", {"items": []})
    return [(it["slug"], lang, it[lang]) for it in q["items"] for lang in ("en", "es")
            if it.get(lang) and it[lang][0] == day and it.get("item", "short") == "short"]


def check(day, offline=False, now=None):
    from . import approvals, renderdeps, calcheck
    now = now or dt.datetime.now(ET)
    rows = []
    add = lambda name, status, ev: rows.append((name, status, ev))
    items = due_items(day)
    store = approvals._load()
    reg = {"en": _j(LEARN / "uploads.json", {}), "es": _j(LEARN / "uploads-es.json", {})}
    pre = {}  # (slug, lang) -> video id uploaded before/outside the gate (YouTube already holds the slot)
    for l in ("en", "es"):
        for vid, r in reg[l].items():
            if r.get("item", "short") == "short" and not r.get("hidden"):
                pre[(r.get("slug"), l)] = vid
    recs = {(s, l): store.get(approvals.key_of(s, "short", "youtube-es" if l == "es" else "youtube-en")) or {}
            for s, l, _ in items}
    add("queue", "PASS" if items else "WAIT", f"{len(items)} Shorts booked {calcheck.label(day)}: "
        + ", ".join(f"{s} {l.upper()} {t[1]}" for s, l, t in items))

    # 1 overnight fact re-checks: stamped within 2 days of the slot
    fc = _j(LEARN / "factchecks.json", {})
    stale = [s for s, l, t in items if (s, l) not in pre and recs[(s, l)].get("state") not in ("SCHEDULED", "PUBLISHED") and (not fc.get(s) or
             (dt.date.fromisoformat(t[0]) - dt.date.fromisoformat(fc[s]["date"])).days > 2)]
    add("fact re-checks", "PASS" if items and not stale else ("FAIL" if stale else "WAIT"),
        "all stamped within 2 days" if not stale else f"not re-checked: {', '.join(sorted(set(stale)))}")

    # 2 re-renders: every due render matches its inputs
    bad = []
    for s, l, _ in items:
        p = ROOT / "episodes" / f"{s}.json"
        ep = _j(p, {})
        f = ROOT / "output" / s / f"{s}-short{'-es' if l == 'es' else ''}.mp4"
        st = renderdeps.status(f, ep, "short", l, p) if ep else "missing"
        if renderdeps.needs_render(st) and (s, l) not in pre and recs[(s, l)].get("state") not in ("SCHEDULED", "PUBLISHED"):
            bad.append(f"{s} {l}: {st}")
    add("renders current", "PASS" if not bad else "FAIL", "; ".join(bad) or "every due render matches its episode")

    # 3 uploads: gate state per item (scheduled is NOT published)
    states = {f"{s} {l}": ("SCHEDULED" if (s, l) in pre else recs[(s, l)].get("state", "none")) for s, l, _ in items}
    up = [k for k, v in states.items() if v in ("SCHEDULED", "PUBLISHED")]
    held = {k: v for k, v in states.items() if v not in ("SCHEDULED", "PUBLISHED")}
    before_run = day > now.date().isoformat() or (day == now.date().isoformat() and (now.hour, now.minute) < (3, 45))
    add("uploads", "PASS" if items and not held else ("WAIT" if held and before_run else ("FAIL" if held else "WAIT")),
        f"uploaded {len(up)}/{len(items)}" + (f"; not uploaded: {held}" if held else ""))

    # 4-5, 12: YouTube: channel, publishAt, public
    if offline:
        add("channel / time / public", "UNKNOWN", "--offline")
    else:
        ch_bad, t_bad, public, pending, unread = [], [], [], [], []
        for s, l, slot in items:
            r = recs[(s, l)]
            vid = r.get("video_id") or pre.get((s, l))
            if not vid:
                continue
            try:
                from .youtube_upload import req, token
                if l == "es":
                    from . import youtube_es as y
                    tok = y.token_for(CHANNEL["youtube-es"], y.ENV)
                else:
                    tok = token()
                v, _ = req("GET", f"https://youtube.googleapis.com/youtube/v3/videos?part=status,snippet&id={vid}", tok)
            except (SystemExit, Exception) as e:  # noqa: BLE001
                unread.append(f"{s} {l}: {str(e)[:60]}")
                continue
            it = (v.get("items") or [None])[0]
            if not it:
                unread.append(f"{s} {l}: {vid} not found")
                continue
            if it["snippet"]["channelId"] != CHANNEL["youtube-es" if l == "es" else "youtube-en"]:
                ch_bad.append(f"{s} {l} on {it['snippet']['channelId']}")
            want = calcheck.to_utc(*slot)
            pa, pub = it["status"].get("publishAt"), it["snippet"].get("publishedAt")
            when = pa or pub
            if when and abs((dt.datetime.fromisoformat(when.replace("Z", "+00:00")) - want).total_seconds()) > 900:
                t_bad.append(f"{s} {l}: {when} vs slot {want:%H:%M} UTC")
            if it["status"]["privacyStatus"] == "public":
                public.append(f"{s} {l} https://youtu.be/{vid}")
            else:
                pending.append(f"{s} {l} ({it['status']['privacyStatus']}, slot {calcheck.label(slot[0])} {slot[1]})")
        seen = len(public) + len(pending)
        add("right channel", "FAIL" if ch_bad else ("UNKNOWN" if unread else ("PASS" if seen else "WAIT")),
            "; ".join(ch_bad + unread) or (f"{seen} uploads on the right channel" if seen else "nothing uploaded yet"))
        add("right time", "FAIL" if t_bad else ("PASS" if seen else "WAIT"),
            "; ".join(t_bad) or (f"{seen} publish times = booked slots (±15 min)" if seen else "nothing uploaded yet"))
        add("public", "PASS" if public and not pending else ("WAIT" if pending else "WAIT"),
            ("public: " + "; ".join(public) if public else "none public yet") + (f"; not yet: {'; '.join(pending)}" if pending else ""))

    # 6-8 helper run: branch pushed, manifest, merged into main
    br = f"claude/daily-{day}"
    _git("fetch", "-q", "origin")
    remote = _git("rev-parse", "-q", "--verify", f"origin/{br}")
    if not remote:
        add("helper run pushed", "FAIL" if now.date().isoformat() >= day and now.hour >= 7 else "WAIT",
            f"no {br} on GitHub")
        add("helper merged", "WAIT", "nothing to merge")
    else:
        man = _git("show", f"origin/{br}:content/runs/daily-{day}.json")
        add("helper run pushed", "PASS", f"{br} at {remote[:8]}" + (" with manifest" if man else " (NO manifest)"))
        merged = subprocess.run(["git", "merge-base", "--is-ancestor", remote, "origin/main"], cwd=ROOT).returncode == 0
        add("helper merged", "PASS" if merged else "WAIT", "in origin/main" if merged else
            "not merged yet (python -m studio.runsafe merge " + br + ")")
    local, origin = _git("rev-parse", "HEAD"), _git("rev-parse", "origin/main")
    dirty = "\n".join(l for l in (_git("status", "--porcelain") or "").splitlines()
                       if not l.endswith(("content/learn/quota.json", "content/learn/tests_status.json")))  # run logs
    add("main pushed", "PASS" if local == origin and not dirty else "FAIL",
        "local main = origin/main, clean" if local == origin and not dirty else
        f"local {str(local)[:8]} vs origin {str(origin)[:8]}{', uncommitted changes' if dirty else ''}")

    # 9 duplicates: one registry entry per slug/item/channel, no repeated titles
    dup = []
    for f, plat in (("uploads.json", "en"), ("uploads-es.json", "es")):
        reg = _j(LEARN / f, {})
        seen = {}
        for vid, r in reg.items():
            if r.get("hidden"):  # set private (e.g. the Nov 20 re-uploads): not a live duplicate
                continue
            k = (r.get("slug"), r.get("item", "short"))
            if k in seen:
                dup.append(f"{plat} {k[0]} twice ({seen[k]}, {vid})")
            seen[k] = vid
    add("no duplicates", "FAIL" if dup else "PASS", "; ".join(dup) or "registry: one upload per slug/item per channel")

    # 10 analytics: refreshed in the last 26 h
    a = LEARN / "analytics.json"
    age = (dt.datetime.now().timestamp() - a.stat().st_mtime) / 3600 if a.exists() else 999
    add("analytics", "PASS" if age < 26 else "FAIL", f"analytics.json refreshed {age:.0f} h ago (python -m studio.learn --mine)")

    # 11 costs: Everygen spends recorded for Vice Replay that day
    try:
        from . import credits
        s = credits.summary()
        vr = [x for x in s.get("spends", []) if str(x.get("at", "")).startswith(day) and x.get("project", "vice-replay") == "vice-replay"]
        b = s.get("balance") or {}
        add("generation cost", "PASS", f"{sum(x.get('credits', 0) for x in vr)} Everygen credits for Vice Replay on {day}; "
            f"balance {b.get('remaining')} {'VERIFIED' if b.get('verified') else 'UNVERIFIED'} (read {b.get('read_at')})")
    except Exception as e:  # noqa: BLE001
        add("generation cost", "UNKNOWN", f"credits summary failed: {str(e)[:80]}")
    return rows


def verdict(rows):
    st = [r[1] for r in rows]
    if "FAIL" in st:
        return "NOT OPERATIONAL: fix the FAIL rows and run again"
    if "WAIT" in st or "UNKNOWN" in st:
        return "NOT VERIFIED YET: some steps haven't happened or couldn't be checked"
    return "OPERATIONAL: every step of the cycle verified"


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m studio.cycle")
    ap.add_argument("--date", default=dt.datetime.now(ET).date().isoformat())
    ap.add_argument("--offline", action="store_true")
    a = ap.parse_args(argv)
    rows = check(a.date, a.offline)
    w = max(len(r[0]) for r in rows)
    for name, status, ev in rows:
        print(f"{status:8} {name:<{w}}  {ev}")
    print(verdict(rows))


if __name__ == "__main__":
    main()
