"""Stale-wording check for vicereplay.com (Nov 24, 2026).

The site was written before GTA 6 came out (Nov 19, 2026); pages that still say "comes out on November 19" make the
whole site look abandoned. `scan(site_dir)` lists built pages that still use pre-launch wording. Pages that carry a
dated update note (class "note update", added by tools/site_guides.py NOTICES) are skipped: their old text is kept on
purpose as a record and the note on top says what changed.

    python -m studio.site_stale            # scan ../vicereplay-site
"""
import datetime as dt
import html
import json
import os
import re
import sys
from pathlib import Path

STALE = re.compile(
    r"comes out on|launches on November 19|will (?:be )?(?:released|launch|come out) on November|"
    r"updated every day of launch week|everything you need for launch week|what you need for launch week|"
    r"before launch makes|sale el (?:jueves )?19 de noviembre|saldr[áa] el|"
    r"actualizado cada d[ií]a de la semana de lanzamiento|todo lo de la semana de lanzamiento", re.I)


def _text(path):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", path.read_text(errors="ignore"), flags=re.S)
    return t, re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))


def scan(site_dir):
    """[(page, phrase in context), ...] for pages with pre-launch wording and no dated update note."""
    site = Path(site_dir)
    out = []
    for f in sorted(site.rglob("index.html")):
        raw, txt = _text(f)
        if 'class="note update"' in raw:
            continue
        for m in STALE.finditer(txt):
            out.append((str(f.relative_to(site).parent) + "/", txt[max(0, m.start() - 40):m.end() + 40].strip()))
    return out


def _month_day(text, today):
    """'Nov 24' / 'Nov 24, 6 AM ET' -> date in today's year (last year if that would be in the future)."""
    m = re.match(r"([A-Z][a-z]{2})[a-z]*\.? (\d{1,2})", text.strip())
    if not m:
        return None
    d = dt.datetime.strptime(f"{m.group(1)} {m.group(2)} {today.year}", "%b %d %Y").date()
    return d.replace(year=d.year - 1) if d > today else d


def freshness(studio_root, today=None, max_days=3):
    """Warnings for time-sensitive site content (Nov 24 owner: "monitor so this doesn't happen"):
    expired guides (`expires` in site/guides/*.json), deal prices checked more than `max_days` ago (DEALS_CHECKED in
    tools/site_guides.py) and a live-updates page with no new line for more than `max_days`."""
    root = Path(studio_root)
    today = today or dt.date.today()
    out = []
    for f in sorted((root / "site" / "guides").glob("*.json")):
        try:
            g = json.loads(f.read_text())
        except ValueError:
            continue
        if g.get("expires") and dt.date.fromisoformat(g["expires"]) < today:
            out.append(f"guide {g.get('slug', f.stem)} expired on {g['expires']}: update its deals or retire it")
    src = root / "tools" / "site_guides.py"
    m = re.search(r'^DEALS_CHECKED = "([^"]+)"', src.read_text(), re.M) if src.exists() else None
    checked = _month_day(m.group(1), today) if m else None
    if checked and (today - checked).days > max_days:
        out.append(f"deal prices last checked {m.group(1)} ({(today - checked).days} days ago): re-check DEALS in tools/site_guides.py")
    live = root / "site" / "live.json"
    if live.exists():
        items = json.loads(live.read_text())
        newest = _month_day(items[0]["time"], today) if items else None
        if newest and (today - newest).days > max_days:
            out.append(f"live updates page: newest line is from {items[0]['time']} ({(today - newest).days} days ago): add today's news to site/live.json")
    return out


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    site = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("VICEREPLAY_SITE") or root.parent / "vicereplay-site"
    hits = scan(site)
    for page, ctx in hits:
        print(f"STALE {page}: ...{ctx}...")
    old = freshness(root)
    for w in old:
        print("OLD", w)
    print(f"{len(hits)} stale phrase(s), {len(old)} freshness warning(s)")
