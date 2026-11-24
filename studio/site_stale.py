"""Stale-wording check for vicereplay.com (Nov 24, 2026).

The site was written before GTA 6 came out (Nov 19, 2026); pages that still say "comes out on November 19" make the
whole site look abandoned. `scan(site_dir)` lists built pages that still use pre-launch wording. Pages that carry a
dated update note (class "note update", added by tools/site_guides.py NOTICES) are skipped: their old text is kept on
purpose as a record and the note on top says what changed.

    python -m studio.site_stale            # scan ../vicereplay-site
"""
import html
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


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    site = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("VICEREPLAY_SITE") or root.parent / "vicereplay-site"
    hits = scan(site)
    for page, ctx in hits:
        print(f"STALE {page}: ...{ctx}...")
    print(f"{len(hits)} stale phrase(s)")
