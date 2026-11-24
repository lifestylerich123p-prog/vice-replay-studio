"""Long-video thumbnails A/B/C for YouTube Studio's "Test & Compare" (long videos only, not Shorts).

    python -m studio.thumbs episodes/<slug>.json     # rebuild only the thumbnails (no video render)

Episode `thumbnail`: {line1, line2, tag, image} = version A. Without `variants`, B and C reuse A's words on another
picture (the old way). With `"variants": [{line1, line2, tag, image|"vice"}, ...]` (Nov 23), B and C test different
IDEAS (a number, a contrast...), which teaches more than three backgrounds with the same words. `"image": "vice"`
puts the words on our animated Vice City set (studio/vicecards.py). Official screenshots are allowed in thumbnails
(CLAUDE.md), never in the videos themselves.
"""
import json
import shutil
import sys
from pathlib import Path

from . import brand

ROOT = Path(__file__).resolve().parent.parent
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp"}
W, H = 1280, 720


def _vice_bg(out_dir, seed=0):
    from . import vicecards
    still, hz = vicecards.sky(W, H, seed)
    p = out_dir / "work" / f"thumb-vice-{seed}.jpg"
    p.parent.mkdir(parents=True, exist_ok=True)
    vicecards.frame_bg(still, hz, 0.4, W, H).convert("RGB").save(p, quality=95)
    return str(p)


def render(ep, base, out_dir):
    """Write thumbnail-a/b/c.jpg (+ thumbnail.jpg = A) into out_dir. `base` = the folder the episode's paths are
    relative to (the episodes/ folder)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    th = ep.get("thumbnail", {})

    def pic(p):
        if not p:
            return None
        if p == "vice" or str(p).startswith("vice:"):
            return _vice_bg(out_dir, int(str(p).split(":")[1]) if ":" in str(p) else 0)
        q = Path(p) if Path(p).is_absolute() else (Path(base) / p)
        return str(q.resolve()) if q.exists() else None

    a = {"line1": th.get("line1", ep["title"]), "line2": th.get("line2", ""), "tag": th.get("tag", ""),
         "image": pic(th.get("image"))}
    if th.get("variants"):
        versions = [a] + [{"line1": v.get("line1", a["line1"]), "line2": v.get("line2", a["line2"]),
                           "tag": v.get("tag", a["tag"]), "image": pic(v.get("image"))} for v in th["variants"][:2]]
    else:
        pics = [a["image"]] if a["image"] else []
        pics += [pic(s["media"]) for s in ep.get("segments", [])
                 if s.get("media") and Path(s["media"]).suffix.lower() in IMAGE_EXT]
        pics += [pic(p) for p in th.get("images", [])]
        pics = list(dict.fromkeys(x for x in pics if x))
        backgrounds = (pics[:2] + [None]) if pics else [None]
        versions = [dict(a, image=bg) for bg in backgrounds]
    files = []
    for label, v in zip("abc", versions):
        f = out_dir / f"thumbnail-{label}.jpg"
        brand.thumbnail(v["line1"], v["line2"], v["tag"], f, bg_image=v["image"])
        files.append(f)
    shutil.copy(out_dir / "thumbnail-a.jpg", out_dir / "thumbnail.jpg")
    return files


if __name__ == "__main__":
    ep_path = Path(sys.argv[1]).resolve()
    ep = json.loads(ep_path.read_text())
    out = ROOT / "output" / ep["slug"]
    for f in render(ep, ep_path.parent, out):
        print(f)
