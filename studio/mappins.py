"""Pins on Rockstar's official Leonida map (owner, Nov 24, 2026: "use any app we have to [show] specific spots in the
map"). Draws numbered neon pins + labels on media/official/leonida-map-poster.jpg, by place name (read off the map's
own labels) or by the map's printed grid (columns 1-9, rows A-M), and can render a zoom-to-pin clip.

    from studio import mappins
    mappins.pinned_map([{"n": 1, "at": "Washington Island", "label": "Dexter's apartment"},
                        {"n": 2, "at": "G7", "label": "..."}], "out.jpg", crop="all")
    mappins.zoom_clip({"at": "Port Gellhorn", "label": "UFO, after 2 AM"}, "ufo.mp4", dur=4)   # video: see below

Where it can be used: the official map is official media, so website pages, thumbnails and Instagram carousels yes;
inside Shorts/long videos only once the owner allows official images in videos again (CLAUDE.md "No trailer images in
ANY video"; the photo-cards question of Nov 24). Locations must come from 2+ reputable guides; when guides disagree,
pin the area and say so in the text.
"""
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from . import brand

ROOT = Path(__file__).resolve().parent.parent
MAP = ROOT / "media" / "official" / "leonida-map-poster.jpg"
# Nov 24 (owner: "I want high definition"): Rockstar's printable poster, 5775 x 7900 (2x the poster above, same
# layout), fetched on demand from Rockstar's own download page and kept out of git (46 MB): media/official-hd/.
HD_ZIP = "https://media-rockstargames-com.akamaized.net/VI/downloads/artwork_wallpapers/Leonida_Map_Poster_Printable.zip"
HD_MAP = ROOT / "media" / "official-hd" / "leonida-map-print.jpg"


def map_image():
    """The sharpest official map available: the printable HD poster (downloaded once), else the 2900 px poster."""
    if not HD_MAP.exists():
        try:
            import io
            import urllib.request
            import zipfile
            data = urllib.request.urlopen(HD_ZIP, timeout=300).read()
            z = zipfile.ZipFile(io.BytesIO(data))
            name = next(n for n in z.namelist() if n.lower().endswith(".jpg"))
            Image.MAX_IMAGE_PIXELS = None
            im = Image.open(io.BytesIO(z.read(name))).convert("RGB")
            HD_MAP.parent.mkdir(parents=True, exist_ok=True)
            im.save(HD_MAP, quality=92)
        except Exception as e:  # noqa: BLE001 - fall back to the committed poster
            print(f"HD map unavailable ({type(e).__name__}); using the 2900 px poster")
            return Image.open(MAP).convert("RGB")
    Image.MAX_IMAGE_PIXELS = None
    return Image.open(HD_MAP).convert("RGB")
VIEW_W, VIEW_H = 1023.4, 1400.0  # the 1400 px-high view the positions below were read from (Nov 24)

# Label centers read off the official map (x, y in that view); every name is printed on Rockstar's map (the first 37 checked
# against the HD poster on Nov 24; "Starlet Motel" was removed: it isn't printed, so a pin there was a guess).
PLACES = {
    "Port Gellhorn": (312, 498), "Kelly County": (433, 553),
    "Vice City": (686, 728), "Vice Beach": (870, 685), "Vice-Dale County": (738, 803), "Downtown": (718, 748),
    "Little Cuba": (676, 747), "VCIA": (580, 798), "Washington Island": (850, 603), "Vespucci Island": (781, 677), "Rialto Islands": (783, 658), "Washington Beach": (875, 622),
    "Ambrosia": (567, 500), "Leonard County": (715, 503), "Belville": (672, 554), "Lake Leonida": (618, 437),
    "Lummox County": (510, 283), "Mount Kalaga": (515, 318), "Millport": (673, 323), "Bonanza": (493, 199),
    "Grayson": (389, 305), "Waning Sands": (756, 452), "Draper Island": (252, 419), "Capri": (294, 738),
    "Breakwater Quarry": (443, 817), "Grassrivers": (461, 928), "Hamlet": (573, 958), "Bluegrass": (573, 885),
    "South Vice-Dale": (632, 945), "Watson Bay": (442, 985), "Mariana County": (421, 1021),
    "Pelican Valley": (533, 1025), "Cottonmouth Lake": (536, 1078), "Gambit Bay": (566, 1106), "Key Lento": (581, 1165),
    "Southwind": (336, 1195), "Mile Zero Air Station": (281, 1218),
    # Nov 24, second pass (map research): smaller labels, read the same way off the HD poster
    "La Perle": (696, 650), "Crosstown": (713, 695), "Rockridge": (668, 697), "Bayside": (735, 661), "Salton": (636, 757),
    "Waxman Island": (790, 745), "Southside": (634, 909), "Peacock Bay": (679, 894), "T.H. Power Station": (642, 1000),
    "Frogswater": (443, 480), "Howe Dairy": (432, 527), "Tequesta Retreat": (742, 832), "Port Vice City": (808, 778),
    "Paradise RV Park": (481, 953), "Gullet Marsh": (511, 1000), "Gellhorn": (365, 625),
}
COLS = {str(i + 1): x for i, x in enumerate([88, 193, 299, 405, 511, 617, 723, 829, 935])}
ROWS = {r: y for r, y in zip("ABCDEFGHIJKLM", [76, 168, 274, 380, 487, 593, 698, 805, 912, 1018, 1124, 1231, 1327])}


def where(at):
    """(x, y) as 0-1 fractions of the map for a place name, a grid cell like "G7" / "g7", or an (x, y) pair."""
    if isinstance(at, (tuple, list)):
        return float(at[0]), float(at[1])
    key = next((k for k in PLACES if k.lower() == str(at).lower()), None)
    if key:
        x, y = PLACES[key]
    else:
        cell = str(at).strip().upper()
        if len(cell) < 2 or cell[0] not in ROWS or cell[1:] not in COLS:
            raise KeyError(f"unknown place or grid cell: {at!r} (places: {', '.join(PLACES)})")
        x, y = COLS[cell[1:]], ROWS[cell[0]]
    return x / VIEW_W, y / VIEW_H


def _pin(d, x, y, n, scale):
    r = int(26 * scale)
    d.ellipse((x - r * 1.9, y - r * 1.9, x + r * 1.9, y + r * 1.9), outline=brand.PINK, width=max(2, int(4 * scale)))
    d.ellipse((x - r, y - r, x + r, y + r), fill=brand.PINK, outline=(255, 255, 255), width=max(2, int(4 * scale)))
    f = brand.font(brand.HEADLINE_FONT, int(30 * scale))
    t = str(n)
    d.text((x - f.getlength(t) / 2, y - r * 0.78), t, font=f, fill=(255, 255, 255))


def _label(d, x, y, text, scale, w, side=None):
    f = brand.font(brand.BODY_FONT, int(26 * scale))
    tw = f.getlength(text)
    pad = 12 * scale
    right = side != "left" and x + 40 * scale + tw + 2 * pad < w
    lx = x + 40 * scale if right else x - 40 * scale - tw - 2 * pad
    box = (lx, y - 22 * scale, lx + tw + 2 * pad, y + 22 * scale)
    d.rounded_rectangle(box, radius=int(10 * scale), fill=(13, 7, 23), outline=brand.CYAN, width=max(1, int(2 * scale)))
    d.text((lx + pad, y - 16 * scale), text, font=f, fill=(255, 255, 255))


def pinned_map(pins, out, crop="all", width=1600, title=None):
    """Draw numbered pins (+ labels) on the official map and save a JPEG/WebP. crop="all" = whole map; or a place /
    grid cell to center on, or "pins" = the box around all pins. Returns the output path."""
    base = map_image()
    W, H = base.size
    pts = [(p, where(p["at"])) for p in pins]
    if crop == "pins" and pts:
        xs, ys = [q[0] * W for _, q in pts], [q[1] * H for _, q in pts]
        m = 0.12 * W
        box = (max(0, min(xs) - m), max(0, min(ys) - m), min(W, max(xs) + m), min(H, max(ys) + m))
    elif crop not in (None, "all"):
        cx, cy = where(crop)
        half = 0.22 * W
        box = (max(0, cx * W - half), max(0, cy * H - half * 1.25), min(W, cx * W + half), min(H, cy * H + half * 1.25))
    else:
        box = (0, 0, W, H)
    img = base.crop(tuple(int(v) for v in box))
    s = width / img.width
    img = img.resize((width, int(img.height * s)), Image.LANCZOS)
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    scale = width / 1600 * 1.4
    for p, (fx, fy) in pts:
        x, y = (fx * W - box[0]) * s, (fy * H - box[1]) * s
        _pin(d, x, y, p.get("n", ""), scale)
        if p.get("label"):
            _label(d, x, y, p["label"], scale, img.width, p.get("side"))
    f = brand.font(brand.BODY_FONT, int(20 * scale))
    credit = "Map: Rockstar Games (official) · pins: vicereplay.com"
    d.text((img.width - f.getlength(credit) - 16, img.height - 34 * scale), credit, font=f, fill=(13, 7, 23))
    if title:
        ft = brand.font(brand.HEADLINE_FONT, int(56 * scale))
        d.rectangle((0, 0, img.width, 90 * scale), fill=(13, 7, 23))
        d.text((24, 14 * scale), title, font=ft, fill=brand.PINK)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, quality=88)
    return out


def zoom_clip(pin, out, dur=4.0, w=1080, h=1920, fps=30):
    """A vertical clip that starts on the whole map and zooms to one pin, which then pulses. For Shorts only after the
    owner allows official images in videos again (see module docstring)."""
    base = map_image()
    W, H = base.size
    fx, fy = where(pin["at"])
    tx, ty = fx * W, fy * H
    proc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                             "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                             "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)
    n = int(dur * fps)
    for i in range(n):
        p = min(1.0, i / (n * 0.6))
        e = 1 - (1 - p) ** 3
        vw = W * (1 - e) + W * 0.28 * e          # visible width: whole map -> 28% of it
        vh = vw * h / w
        cx = W / 2 * (1 - e) + tx * e
        cy = H / 2 * (1 - e) + ty * e
        x0, y0 = max(0, min(W - vw, cx - vw / 2)), max(0, min(H - vh, cy - vh / 2))
        frame = base.crop((int(x0), int(y0), int(x0 + vw), int(y0 + vh))).resize((w, h), Image.BILINEAR)
        d = ImageDraw.Draw(frame)
        px, py = (tx - x0) / vw * w, (ty - y0) / vh * h
        if p >= 1.0:
            pulse = 1 + 0.25 * abs(((i - n * 0.6) / fps * 2) % 2 - 1)
            _pin(d, px, py, pin.get("n", ""), 2.0 * pulse)
            if pin.get("label"):
                _label(d, px, py, pin["label"], 2.0, w)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    proc.wait()
    return Path(out)
