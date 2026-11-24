"""Zoomable tiles of Rockstar's official Leonida map for the website's interactive map (owner, Nov 24, 2026: "research
those maps pictures more"; "gta 6 map" / "gta 6 mapa interactivo" are top searches we didn't answer).

    python tools/map_tiles.py [--site ../vicereplay-site]

Cuts the HD printable poster (studio.mappins.map_image(): 5775 x 7900, fetched from Rockstar on first use) into
256 px WebP tiles, zoom 0-5 (5 = full resolution), at <site>/img/map/{z}/{x}/{y}.webp, plus Leaflet (self-hosted, BSD-2)
at <site>/js/. The page side is tools/site_guides.py `interactive_map()`, pins in site/map-pins.json.
"""
import argparse
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from PIL import Image  # noqa: E402

from studio import mappins  # noqa: E402

TILE, MAXZ = 256, 5


def tiles(site):
    im = mappins.map_image()
    W, H = im.size
    pad = (13, 7, 23)  # the page's background, so the map ends at the poster's own edge
    out = Path(site) / "img" / "map"
    if out.exists():
        shutil.rmtree(out)
    n = 0
    for z in range(MAXZ + 1):
        s = 2 ** (z - MAXZ)
        w, h = max(1, math.ceil(W * s)), max(1, math.ceil(H * s))
        lvl = im if z == MAXZ else im.resize((w, h), Image.LANCZOS)
        for x in range(math.ceil(w / TILE)):
            for y in range(math.ceil(h / TILE)):
                t = lvl.crop((x * TILE, y * TILE, min(w, (x + 1) * TILE), min(h, (y + 1) * TILE)))
                if t.size != (TILE, TILE):
                    full = Image.new("RGB", (TILE, TILE), pad)
                    full.paste(t, (0, 0))
                    t = full
                d = out / str(z) / str(x)
                d.mkdir(parents=True, exist_ok=True)
                t.save(d / f"{y}.webp", quality=76, method=5)
                n += 1
    return n, (W, H)


def leaflet(site):
    """Copy Leaflet 1.9.4 (npm) into <site>/js/ once."""
    js = Path(site) / "js"
    if (js / "leaflet.js").exists():
        return
    js.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["npm", "pack", "leaflet@1.9.4", "--silent"], cwd=tmp, check=True, capture_output=True)
        subprocess.run(["tar", "xzf", "leaflet-1.9.4.tgz"], cwd=tmp, check=True)
        for f in ("leaflet.js", "leaflet.css"):
            shutil.copy(Path(tmp) / "package" / "dist" / f, js / f)
        shutil.copy(Path(tmp) / "package" / "LICENSE", js / "leaflet-LICENSE.txt")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default=str(ROOT.parent / "vicereplay-site"))
    a = ap.parse_args()
    leaflet(a.site)
    n, size = tiles(a.site)
    print(f"{n} tiles for a {size[0]}x{size[1]} map in {a.site}/img/map/")
