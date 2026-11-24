"""The website's still map pictures, made from the same pins as the interactive map (site/map-pins.json), so the
pictures, the interactive map and the easter eggs guide never disagree (Nov 24, 2026: the old pictures had the UFO
on a spot read from a label that isn't on Rockstar's map).

    python tools/map_pictures.py      # -> <site>/img/maps/*.jpg + the easter eggs guide's map section

Uses Rockstar's official HD Leonida poster (studio.mappins); every picture credits Rockstar.
"""
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from studio import mappins  # noqa: E402

SITE = ROOT.parent / "vicereplay-site"
OUT = SITE / "img" / "maps"
# The easter eggs guide's set, in its numbering: (pin title in map-pins.json, short label, label side)
EGGS = [("Egg tower", "Egg tower", None), ("UFO abduction", "UFO · after 2 AM", None), ("Skunk Ape", "Skunk Ape", None),
        ("Dexter's apartment", "Dexter's apartment", None), ("Giant crab", "Giant crab", "left"),
        ("Cool Dog on a jet ski", "Cool Dog", "left"), ("Paul Walker's car", "Paul Walker's car", "left"),
        ("The NPC who knows it's a game", "Self-aware NPC", None), ("Arthur Morgan's hat", "Arthur Morgan's hat", None),
        ("A Red Dead book", "Red Dead book", None), ("Tommy Vercetti's portal", "Tommy Vercetti portal", None)]
PICTURES = [  # file, pins (EGGS numbers), crop, width, alt, heading
    ("gta-6-easter-eggs-map.jpg", list(range(1, 12)), "pins", 1800,
     "GTA 6 easter egg locations pinned on Rockstar's official Leonida map", None),
    ("gta-6-secrets-north-hd.jpg", [2, 8, 9, 10], "pins", 2000,
     "UFO, Arthur Morgan's hat, the Red Dead book and the self-aware NPC's house on the official map of north Leonida",
     "Close-up: north Leonida (high resolution)"),
    ("gta-6-secrets-vice-city-hd.jpg", [4, 7], "Vice City", 2000,
     "Dexter's apartment and Paul Walker's car on the official map of Vice City", "Close-up: Vice City (high resolution)"),
    ("gta-6-secrets-south-hd.jpg", [1, 3, 5, 6, 11], "pins", 2000,
     "Egg tower, Skunk Ape, giant crab, Cool Dog and the Tommy Vercetti portal on the official map of south Leonida",
     "Close-up: south Leonida (high resolution)"),
]


def pins_by_title():
    src = json.loads((ROOT / "site" / "map-pins.json").read_text())
    return {p["en"]["t"]: p for p in src["pins"]}


def pin_at(p):
    x, y = mappins.where(p["at"])
    if "dx" in p or "dy" in p:
        return (x + p.get("dx", 0), y + p.get("dy", 0))
    return (x, y - 0.009)  # same rule as the interactive map: just above the printed name


def build():
    by = pins_by_title()
    eggs = [(n, by[t], label, side) for n, (t, label, side) in enumerate(EGGS, 1)]
    OUT.mkdir(parents=True, exist_ok=True)
    blocks = []
    from PIL import Image
    for name, nums, crop, width, alt, heading in PICTURES:
        pins = [{"n": n, "at": pin_at(p), "label": label, "side": side} for n, p, label, side in eggs if n in nums]
        overview = name == "gta-6-easter-eggs-map.jpg"  # numbers only (the list below names them), big enough for a phone
        out = mappins.pinned_map(pins, OUT / name, crop=crop, width=width, scale=2.6 if overview else 1.9,
                                 labels=False, legend=not overview)
        w, h = Image.open(out).size
        img = (f'<a href="/img/maps/{name}" target="_blank" rel="noopener"><img src="/img/maps/{name}" width="{w}" '
               f'height="{h}" alt="{html.escape(alt)}" loading="lazy" style="width:100%;height:auto;border-radius:14px;'
               f'border:1px solid var(--line);margin:8px 0"></a>')
        blocks.append((heading, img))
    items = "".join(f'<li><b>{n}. {html.escape(p["en"]["t"])}:</b> {html.escape(p["en"]["d"])}</li>' for n, p, _, _ in eggs)
    section = blocks[0][1] + f'<ol class="list">{items}</ol>' + "".join(f"<h3>{h}</h3>{b}" for h, b in blocks[1:])
    section += ('<p>Want to zoom in yourself? <a href="/guides/gta-6-map-leonida-places/">Open the interactive map</a> '
                '(every spot, plus places, cars and mod shops).</p><p class="sources">Pins are placed on Rockstar\'s official '
                'printable Leonida map from launch-week guides (GTABase, Red Bull, The Click, Game8, GameSpot, GamesRadar, '
                'Dexerto, VICE, PCGamesN, TheGamer); each spot is in at least two of them, and where they disagree we say so. '
                'Tap an image to open it full size.</p>')
    gpath = ROOT / "site" / "guides" / "gta-6-easter-eggs.json"
    g = json.loads(gpath.read_text())
    for s in g["sections"]:
        if s[0] == "Where they are on the map":
            s[1] = section
    gpath.write_text(json.dumps(g, indent=1, ensure_ascii=False))
    return [b[0] for b in PICTURES]


if __name__ == "__main__":
    print(build())
