"""Is every booked video ready to upload? (owner, Nov 24, 2026: "organize and see what's missing").

For each item in content/learn/approved_queue.json from today on that isn't uploaded yet: the rendered file exists,
plays at 30 fps, and its last quality check (the .qc.json studio.vice publish writes) passed.

    python -m studio.readiness          # table of every booked item, problems first
    from studio import readiness; readiness.problems(hours=48)   # what studio.doctor warns about
"""
import datetime as dt
import json
import subprocess
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
LEARN = ROOT / "content" / "learn"
ET = ZoneInfo("America/New_York")
SUFFIX = {"short": "-short", "news": "-short-news", "tips": "-short-tips", "main": ""}


def _when(day, slot):
    t = dt.datetime.strptime(f"{day} {slot}", "%Y-%m-%d %I:%M %p")
    return t.replace(tzinfo=ET)


def booked():
    """[(when, slug, item, lang, path)] for queue items not uploaded yet, soonest first."""
    q = json.loads((LEARN / "approved_queue.json").read_text())["items"]
    ups = json.loads((LEARN / "uploads.json").read_text())
    upes = json.loads((LEARN / "uploads-es.json").read_text())
    done_en = {(u.get("slug"), u.get("item")) for u in ups.values()}
    done_es = {(u.get("slug"), u.get("item")) for u in (upes.values() if isinstance(upes, dict) else [])}
    now = dt.datetime.now(ET) - dt.timedelta(hours=1)
    out = []
    for i in q:
        slug, item = i.get("slug"), i.get("item", "short")
        if i.get("es_only"):
            if not i.get("es") or (slug, item) in done_es:
                continue
            when, lang = _when(*i["es"]), "es"
            path = ROOT / "output" / slug / f"{slug}{SUFFIX.get(item, '-short')}-es.mp4"
        else:
            if not i.get("en") or (slug, item) in done_en:
                continue
            when, lang = _when(*i["en"]), "en"
            path = ROOT / "output" / slug / f"{slug}{SUFFIX.get(item, '-short')}.mp4"
        if when >= now:
            out.append((when, slug, item, lang, path))
    return sorted(out)


def check(path):
    """'' when ready, else the problem."""
    if not path.exists():
        return "not rendered"
    rate = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
                           "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout.strip()
    if rate not in ("30/1", "30000/1001"):
        return f"frame rate {rate}"
    qc = path.with_suffix(".qc.json")
    if qc.exists():
        try:
            d = json.loads(qc.read_text())
            if qc.stat().st_mtime >= path.stat().st_mtime - 5 and not d.get("passed", True):
                fails = [c["check"] for c in d.get("checks", []) if c.get("status") == "fail"]
                return "quality check failed: " + ", ".join(fails)
        except (OSError, ValueError):
            pass
    return ""


def problems(hours=None):
    rows = booked()
    if hours is not None:
        limit = dt.datetime.now(ET) + dt.timedelta(hours=hours)
        rows = [r for r in rows if r[0] <= limit]
    return [(w, s, it, lang, msg) for w, s, it, lang, p in rows for msg in [check(p)] if msg]


def main():
    rows = booked()
    print(f"# Booked videos not uploaded yet: {len(rows)}\n")
    bad = 0
    for w, s, it, lang, p in rows:
        msg = check(p)
        bad += bool(msg)
        print(f"{'❌' if msg else '✅'} {w:%a %b %d %I:%M %p} {lang.upper()} {it:5} {s}{'  ← ' + msg if msg else ''}")
    print(f"\n{len(rows) - bad} ready, {bad} need work")


if __name__ == "__main__":
    main()
