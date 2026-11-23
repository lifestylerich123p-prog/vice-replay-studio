"""GTA 6-style lettering cards (owner, Nov 23, 2026: "stop posting the video with trailer imaging, we're moving to the
ones with lettering and more modern style ... do it GTA 6 style").

Everything here is drawn by us, no game images:
- `vice` backdrop: a Vice City synthwave set (the look GTA: Vice City gave synthwave): sunset sky, a striped sun, palm
  silhouettes, stars, and a neon grid floor that scrolls toward the viewer. Each seed changes the sky colors and palms.
- five card types, made for the kinetic-typography Shorts that work in 2026 (animate the key words only, change the
  picture every 2-4 s; tier lists, countdown listicles, VS / "this or that", breaking-news cards):

    "chart": {"type": "kinetic", "lines": ["13 YEARS", "AFTER GTA 5", "IT'S HERE"], "pink": ["IT'S HERE"]}
    "chart": {"type": "countdown", "n": 3, "of": 5, "label": "A real Easter egg", "sub": "throw it off the tower"}
    "chart": {"type": "versus", "a": ["GTA 5", "32 HOURS"], "b": ["GTA 6", "80 HOURS"], "winner": "b"}
    "chart": {"type": "tier", "title": "EASTER EGGS", "rows": [["S", "Tower egg"], ["A", ["Chiliad", "Bigfoot"]]]}
    "chart": {"type": "headline", "kicker": "PLAYERS REPORT", "text": "A real Easter egg", "ticker": "..."}

Lines and labels appear one after another across the segment (studio.charts.render passes the length as `_dur`).
Every card can also set "bg": "gradient" to use the older chart backdrop; the older chart types can set "bg": "vice".
"""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import brand

NIGHT = (10, 4, 24)
YELLOW = (255, 214, 92)
SKIES = [  # (top, middle, horizon)
    ((14, 6, 40), (110, 24, 130), (255, 92, 120)),
    ((8, 10, 44), (60, 30, 140), (255, 120, 90)),
    ((20, 4, 36), (150, 20, 110), (255, 150, 80)),
    ((6, 14, 40), (30, 70, 150), (255, 60, 150)),
]
TIER_COLORS = {"S": (255, 52, 110), "A": (255, 140, 56), "B": (255, 214, 92), "C": (0, 229, 210), "D": (120, 110, 255)}


def _ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def _back(t):  # ease-out with a little overshoot: the "slam" of a word landing
    t = max(0.0, min(1.0, t))
    c = 1.9
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


def region(w, h):
    """The card area between the headline (top) and the captions (bottom), same as studio.charts._region."""
    if h > w:
        return int(w * 0.06), int(h * 0.30), int(w * 0.94), int(h * 0.60)
    return int(w * 0.08), int(h * 0.24), int(w * 0.92), int(h * 0.80)


# ---------- the Vice City set ----------

def _palm(d, x, base, height, lean, color, rnd):
    pts = [(x + lean * (k / 24) ** 1.7, base - height * k / 24) for k in range(25)]
    for k in range(24):
        d.line([pts[k], pts[k + 1]], fill=color, width=max(3, int(height * 0.04 * (1 - 0.55 * k / 24))))
    tx, ty = pts[-1]
    for a in (8, 38, 70, 112, 142, 172, 200, -20):
        a += rnd.uniform(-8, 8)
        length = height * rnd.uniform(0.36, 0.48)
        up, low = [], []
        for k in range(15):
            s = k / 14
            ang = math.radians(a)
            px = tx + math.cos(ang) * length * s
            py = ty - math.sin(ang) * length * s + length * 0.62 * s * s
            nx, ny = -math.sin(ang), -math.cos(ang)
            wdt = length * 0.075 * math.sin(math.pi * min(1.0, s * 1.15))
            up.append((px + nx * wdt, py + ny * wdt))
            low.append((px - nx * wdt, py - ny * wdt))
        d.polygon(up + low[::-1], fill=color)
    d.ellipse([tx - height * 0.03, ty - height * 0.02, tx + height * 0.03, ty + height * 0.04], fill=color)


def sky(w, h, seed=0):
    """The still part of the set: sky, stars, sun, palms, horizon glow. Returns (RGB image, horizon y)."""
    rnd = random.Random(seed * 7919 + 3)
    top, mid, hor = (np.array(c, np.float32) for c in SKIES[seed % len(SKIES)])
    horizon = int(h * (0.635 if h > w else 0.66))
    t = np.linspace(0, 1, horizon, dtype=np.float32)[:, None]
    col = np.where(t < 0.62, top + (mid - top) * (t / 0.62), mid + (hor - mid) * ((t - 0.62) / 0.38))
    img = np.empty((h, w, 3), np.float32)
    img[:horizon] = col[:, None, :]
    fy = np.linspace(0, 1, h - horizon, dtype=np.float32)[:, None, None]
    img[horizon:] = np.array(NIGHT, np.float32) * (1 - 0.3 * fy) + np.array((40, 8, 60), np.float32) * 0.25 * (1 - fy)
    im = Image.fromarray(img.clip(0, 255).astype(np.uint8), "RGB").convert("RGBA")
    d = ImageDraw.Draw(im)
    for _ in range(int(w * h / 26000)):  # stars in the dark top of the sky
        sx, sy = rnd.uniform(0, w), rnd.uniform(0, horizon * 0.42)
        r = rnd.choice((1, 1, 1, 2))
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 255, 255, rnd.randint(90, 220)))
    # sun: yellow at the top, pink at the bottom, cut by stripes that thicken toward the horizon
    r = int(w * (0.30 if h > w else 0.16))
    cx = int(w * (0.5 + rnd.uniform(-0.12, 0.12)))
    cy = horizon - int(r * 0.42)
    sun = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun)
    for y in range(cy - r, min(cy + r, horizon)):
        half = math.sqrt(max(0, r * r - (y - cy) ** 2))
        k = (y - (cy - r)) / (2 * r)
        c = tuple(int(YELLOW[i] + (brand.PINK[i] - YELLOW[i]) * min(1, k * 1.25)) for i in range(3))
        sd.line([(cx - half, y), (cx + half, y)], fill=c + (255,))
    for k in range(7):
        y = cy + int(r * (0.02 + 0.13 * k))
        sd.rectangle([0, y, w, y + 2 + int(k * r * 0.012)], fill=(0, 0, 0, 0))
    glow = sun.filter(ImageFilter.GaussianBlur(r * 0.22))
    im.alpha_composite(glow)
    im.alpha_composite(sun)
    # palm silhouettes framing the card (left and right), a different pair per seed
    pd = ImageDraw.Draw(im)
    dark = (16, 6, 30, 255)
    sides = [(-0.04, 1), (1.04, -1)] if seed % 2 == 0 else [(-0.02, 1), (0.92, -1), (1.06, -1)]
    for k, (fx, sign) in enumerate(sides):
        height = h * rnd.uniform(0.36, 0.46) * (0.8 if k == 1 and len(sides) == 3 else 1)
        _palm(pd, w * fx, horizon + h * 0.02, height, sign * w * rnd.uniform(0.10, 0.18), dark, rnd)
    # horizon glow line
    hl = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hl)
    hd.rectangle([0, horizon - 3, w, horizon + 3], fill=brand.CYAN + (255,))
    im.alpha_composite(hl.filter(ImageFilter.GaussianBlur(10)))
    pd.line([(0, horizon), (w, horizon)], fill=brand.CYAN + (255,), width=2)
    # faint scanlines (VHS)
    arr = np.asarray(im.convert("RGB"), np.float32)
    arr[::4] *= 0.9
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGB"), horizon


def frame_bg(still, horizon, t, w, h):
    """The set at time t: the neon grid floor scrolls toward the viewer."""
    img = still.copy()
    d = ImageDraw.Draw(img)
    depth = h - horizon
    phase = (t * 0.55) % 1.0
    n = 12
    for k in range(n + 1):
        s = (k + phase) / n
        y = horizon + int(depth * s ** 2.1)
        if y <= horizon + 1 or y >= h:
            continue
        a = 0.35 + 0.65 * s
        d.line([(0, y), (w, y)], fill=tuple(int(c * a) for c in brand.PINK), width=max(1, int(1 + 3 * s)))
    vx = w / 2
    for k in range(-14, 15):
        d.line([(vx + k * w * 0.035, horizon), (vx + k * w * 0.32, h)], fill=(150, 30, 140), width=2)
    return img


# ---------- lettering ----------

_SPRITES = {}


def lettering(text, size, max_w, top=brand.WHITE, bottom=brand.CYAN, glow=brand.PINK, font=None):
    """A neon chrome word as an RGBA sprite: gradient fill, dark outline, soft glow. Cached (same text, same look)."""
    key = (text, size, max_w, top, bottom, glow, font)
    if key in _SPRITES:
        return _SPRITES[key]
    path = font or brand.HEADLINE_FONT
    while True:
        f = brand.font(path, size)
        if f.getlength(text) <= max_w or size <= 24:
            break
        size = int(size * 0.94)
    x0, y0, x1, y1 = f.getbbox(text)
    pad = int(size * 0.32)
    W, H = int(x1 - x0) + 2 * pad, int(y1 - y0) + 2 * pad
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).text((pad - x0, pad - y0), text, font=f, fill=255)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # a dark drop shadow first, so sunset-colored words still read over the sun
    sh = Image.new("RGBA", (W, H), (8, 2, 18, 0))
    sh.putalpha(mask.filter(ImageFilter.GaussianBlur(max(2, size * 0.05))).point(lambda v: int(v * 0.9)))
    out.alpha_composite(sh, (int(size * 0.035), int(size * 0.05)))
    g = Image.new("RGBA", (W, H), glow + (0,))
    g.putalpha(mask.filter(ImageFilter.GaussianBlur(max(2, size * 0.10))).point(lambda v: min(255, int(v * 1.6))))
    out.alpha_composite(g)
    edge = mask.filter(ImageFilter.MaxFilter(max(3, (size // 18) | 1)))
    ol = Image.new("RGBA", (W, H), (22, 6, 40, 0))
    ol.putalpha(edge)
    out.alpha_composite(ol)
    ys = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    grad = np.array(top, np.float32) * (1 - ys) + np.array(bottom, np.float32) * ys
    fill = Image.fromarray(np.repeat(grad, W, axis=1).clip(0, 255).astype(np.uint8), "RGB").convert("RGBA")
    fill.putalpha(mask)
    out.alpha_composite(fill)
    if len(_SPRITES) > 300:
        _SPRITES.clear()
    _SPRITES[key] = out
    return out


def place(img, sprite, cx, cy, scale=1.0, alpha=1.0):
    if alpha <= 0 or scale <= 0:
        return
    s = sprite
    if abs(scale - 1) > 0.01:
        s = sprite.resize((max(1, int(sprite.width * scale)), max(1, int(sprite.height * scale))), Image.BILINEAR)
    if alpha < 1:
        s = s.copy()
        s.putalpha(s.getchannel("A").point(lambda v: int(v * alpha)))
    img.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2)))


def _small(d, text, cx, y, size, fill=brand.WHITE, max_w=None, font=None):
    path = font or brand.BODY_FONT
    while True:
        f = brand.font(path, size)
        if not max_w or f.getlength(text) <= max_w or size <= 16:
            break
        size -= 2
    d.text((cx - f.getlength(text) / 2, y), text, font=f, fill=fill)
    return f.getbbox("Ay")[3]


def _times(n, dur, first=0.08, last_gap=0.55):
    """When each of n items appears, spread over the segment."""
    span = max(0.3, dur - first - last_gap)
    return [first + span * k / max(1, n) for k in range(n)]


def _shake(t, t0, w):
    """A small screen shake right after a word lands."""
    dt = t - t0 - 0.16
    if 0 <= dt < 0.12:
        a = w * 0.006 * (1 - dt / 0.12)
        return int(a * math.sin(dt * 90)), int(a * math.cos(dt * 70))
    return 0, 0


def _is_pink(line, spec):
    return any(p.lower() == line.lower() or p.lower() in line.lower() for p in spec.get("pink") or [])


# ---------- cards ----------

def kinetic_frame(base, spec, t, w, h):
    """Big neon lettering, one line at a time (punch in + small shake), stacked in the card area. `pink` lines get the
    sunset (yellow-pink) fill instead of white-cyan."""
    img = base.copy().convert("RGBA")
    x0, y0, x1, y1 = region(w, h)
    lines = [str(x) for x in spec.get("lines") or str(spec.get("text", "")).split("|")][:4]
    n = len(lines)
    times = _times(n, spec.get("_dur", 3.0))
    slot = (y1 - y0) / max(n, 1)
    size = int(min(slot * 0.78, w * (0.20 if n <= 2 else 0.15)))
    ox, oy = (0, 0)
    for k, t0 in enumerate(times):
        if t >= t0:
            ox, oy = _shake(t, t0, w)
    cover = spec.get("cover")  # a Short's first segment: its first frame is the cover, so every line shows at once
    for k, (line, t0) in enumerate(zip(lines, times)):
        p = (t - t0) / 0.22
        if p <= 0 and not cover:
            continue
        pink = _is_pink(line, spec)
        spr = lettering(line.upper(), size, int((x1 - x0) * 0.98), *((YELLOW, brand.PINK, brand.CYAN) if pink else
                                                                    (brand.WHITE, brand.CYAN, brand.PINK)))
        cy = y0 + slot * (k + 0.5) + (y1 - y0 - slot * n) / 2
        if cover:  # visible from frame one; each line still pulses on its beat
            pulse = 0.14 * (1 - _ease((t - t0) / 0.25)) if t >= t0 else 0.0
            place(img, spr, (x0 + x1) / 2 + ox, cy + oy, scale=1.0 + pulse)
        else:
            place(img, spr, (x0 + x1) / 2 + ox, cy + oy, scale=1.0 + 0.45 * (1 - _back(p)), alpha=min(1.0, p * 1.6))
    if spec.get("sub") and t > times[-1] + 0.2:
        d = ImageDraw.Draw(img)
        _small(d, str(spec["sub"]), (x0 + x1) / 2, y1 + int(h * 0.004), int(w * 0.04), fill=(230, 220, 245),
               max_w=x1 - x0)
    return img.convert("RGB")


def countdown_frame(base, spec, t, w, h):
    """A countdown listicle item: the number slams in, the label lands under it, the sub line fades in. `of` draws
    progress dots (5 dots, this one lit)."""
    img = base.copy().convert("RGBA")
    x0, y0, x1, y1 = region(w, h)
    d = ImageDraw.Draw(img)
    total = int(spec.get("of") or 0)
    n = int(spec.get("n", 1))
    if total:
        r = int(w * 0.014)
        gap = r * 4
        sx = (x0 + x1) / 2 - gap * (total - 1) / 2
        for k in range(total):
            lit = (total - k) == n
            c = brand.PINK if lit else (90, 60, 120)
            cx = sx + gap * k
            d.ellipse([cx - r, y0 - r, cx + r, y0 + r], fill=c)
    p = (t - 0.05) / 0.25
    num = lettering(f"No. {n}" if spec.get("prefix") else str(n), int((y1 - y0) * 0.46), int((x1 - x0) * 0.6),
                    YELLOW, brand.PINK, brand.CYAN)
    ox, oy = _shake(t, 0.05, w)
    place(img, num, (x0 + x1) / 2 + ox, y0 + (y1 - y0) * 0.30 + oy, scale=1 + 0.8 * (1 - _back(p)),
          alpha=min(1.0, max(0.0, p) * 2))
    pl = (t - 0.35) / 0.25
    if pl > 0:
        lab = lettering(str(spec.get("label", "")).upper(), int((y1 - y0) * 0.17), int((x1 - x0) * 0.98))
        place(img, lab, (x0 + x1) / 2, y0 + (y1 - y0) * 0.68, scale=1 + 0.3 * (1 - _back(pl)), alpha=min(1.0, pl * 1.6))
    if spec.get("sub") and t > 0.8:
        a = min(1.0, (t - 0.8) / 0.3)
        d = ImageDraw.Draw(img)
        _small(d, str(spec["sub"]), (x0 + x1) / 2, y0 + (y1 - y0) * 0.84, int(w * 0.042),
               fill=tuple(int(c * a + 20 * (1 - a)) for c in (235, 225, 250)), max_w=x1 - x0)
    return img.convert("RGB")


def versus_frame(base, spec, t, w, h):
    """VS / "this or that": card A slides in from the left, card B from the right, VS slams between them; with
    `winner` ("a"/"b") the winner lights up pink after 60% of the segment and the other dims. Each side: [label, value]."""
    img = base.copy().convert("RGBA")
    x0, y0, x1, y1 = region(w, h)
    dur = spec.get("_dur", 3.0)
    win = spec.get("winner")
    decided = win and t > dur * 0.6
    half = (y1 - y0) * 0.40
    for k, key in enumerate(("a", "b")):
        label, value = (list(spec.get(key) or ["", ""]) + [""])[:2]
        p = _ease((t - 0.05 - 0.3 * k) / 0.35)
        if p <= 0:
            continue
        dx = (1 - p) * w * (-1 if k == 0 else 1)
        top = y0 + (0 if k == 0 else (y1 - y0) - half)
        box = [x0 + dx, top, x1 + dx, top + half]
        lit = decided and win == key
        dim = decided and win != key
        over = Image.new("RGBA", img.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(over)
        if lit:  # pink neon glow around the winner
            od.rounded_rectangle(box, radius=int(w * 0.04), outline=brand.PINK + (255,), width=18)
            over = over.filter(ImageFilter.GaussianBlur(14))
            od = ImageDraw.Draw(over)
        od.rounded_rectangle(box, radius=int(w * 0.04), fill=(13, 7, 23, 215 if not dim else 165),
                             outline=(brand.PINK if lit else brand.CYAN) + (255 if not dim else 110,), width=6 if lit else 3)
        img.alpha_composite(over)
        d = ImageDraw.Draw(img)
        lh = _small(d, str(label).upper(), (box[0] + box[2]) / 2, top + half * 0.10, int(w * 0.045),
                    fill=(brand.WHITE if lit else brand.CYAN) if not dim else (120, 110, 140), max_w=x1 - x0 - w * 0.06,
                    font=brand.HEADLINE_FONT)
        spr = lettering(str(value).upper(), int(half * 0.46), int((x1 - x0) * 0.9),
                        *((YELLOW, brand.PINK, brand.CYAN) if lit else (brand.WHITE, brand.CYAN, brand.PINK)))
        place(img, spr, (box[0] + box[2]) / 2, top + half * 0.10 + lh + (half * 0.9 - lh) / 2,
              alpha=0.6 if dim else 1.0)
    pv = (t - 0.7) / 0.22
    if pv > 0:
        vs = lettering("VS", int((y1 - y0) * 0.16), w, YELLOW, brand.PINK, brand.CYAN)
        place(img, vs, (x0 + x1) / 2, (y0 + y1) / 2, scale=1 + 0.9 * (1 - _back(pv)), alpha=min(1.0, pv * 2))
    return img.convert("RGB")


def tier_frame(base, spec, t, w, h):
    """A tier list: S/A/B/C/D rows (colored letters), items drop into their row one by one. rows: [["S", "item"] or
    ["S", ["item", "item"]]]; optional `title` above."""
    img = base.copy().convert("RGBA")
    x0, y0, x1, y1 = region(w, h)
    d = ImageDraw.Draw(img)
    rows = [(str(r[0]), (r[1] if isinstance(r[1], list) else [r[1]]) if len(r) > 1 else []) for r in
            spec.get("rows") or []][:5]
    static = {str(x) for x in spec.get("static") or []}  # rows already filled in an earlier segment: no animation
    top = y0
    if spec.get("title"):
        top += _small(d, str(spec["title"]).upper(), (x0 + x1) / 2, y0, int(w * 0.05), fill=brand.WHITE,
                      max_w=x1 - x0, font=brand.HEADLINE_FONT) + int(h * 0.012)
    rh = (y1 - top) / max(1, len(rows))
    items = [(ri, it) for ri, (lab, its) in enumerate(rows) for it in its if lab not in static]
    times = dict(zip(items, _times(len(items), spec.get("_dur", 3.0), first=0.25)))
    times.update({(ri, it): -1.0 for ri, (lab, its) in enumerate(rows) for it in its if lab in static})
    over = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(over)
    for ri, (lab, its) in enumerate(rows):
        ry = top + ri * rh
        od.rounded_rectangle([x0, ry + rh * 0.06, x1, ry + rh * 0.94], radius=int(rh * 0.14), fill=(13, 7, 23, 185))
    img.alpha_composite(over)
    d = ImageDraw.Draw(img)
    fl = brand.font(brand.HEADLINE_FONT, int(rh * 0.56))
    for ri, (lab, its) in enumerate(rows):
        ry = top + ri * rh
        c = TIER_COLORS.get(lab.upper()[:1], brand.CYAN)
        sq = rh * 0.88
        d.rounded_rectangle([x0, ry + rh * 0.06, x0 + sq, ry + rh * 0.94], radius=int(rh * 0.14), fill=c)
        d.text((x0 + sq / 2 - fl.getlength(lab) / 2, ry + rh / 2 - fl.getbbox(lab)[3] / 2 - rh * 0.02), lab, font=fl,
               fill=(13, 7, 23))
        cx = x0 + sq + w * 0.02
        avail = (x1 - w * 0.015) - cx
        per = avail / max(1, len(its)) - w * 0.015
        for it in its:
            p = _ease((t - times[(ri, it)]) / 0.28)
            if p <= 0:
                cx += per + w * 0.015
                continue
            size = int(rh * 0.30)
            while True:
                fi = brand.font(brand.BODY_FONT, size)
                if fi.getlength(it) <= per - w * 0.03 or size <= 14:
                    break
                size -= 1
            yoff = -(1 - p) * rh * 0.6
            chip = [cx, ry + rh * 0.18 + yoff, cx + per, ry + rh * 0.82 + yoff]
            d.rounded_rectangle(chip, radius=int(rh * 0.12), fill=(40, 22, 70), outline=c, width=3)
            d.text(((chip[0] + chip[2]) / 2 - fi.getlength(it) / 2, (chip[1] + chip[3]) / 2 - fi.getbbox("Ay")[3] / 2),
                   it, font=fi, fill=brand.WHITE)
            cx += per + w * 0.015
    return img.convert("RGB")


def headline_frame(base, spec, t, w, h):
    """A breaking-news card in our own look: a flashing kicker tag (e.g. PLAYERS REPORT, CONFIRMED), the headline in
    lettering, and a ticker that scrolls along the bottom of the card. Label rumors in the kicker ("REPORTEDLY")."""
    img = base.copy().convert("RGBA")
    x0, y0, x1, y1 = region(w, h)
    over = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(over)
    od.rounded_rectangle([x0, y0, x1, y1], radius=int(w * 0.03), fill=(13, 7, 23, 175), outline=brand.CYAN + (200,),
                         width=3)
    img.alpha_composite(over)
    d = ImageDraw.Draw(img)
    kick = str(spec.get("kicker", "BREAKING")).upper()
    fk = brand.font(brand.HEADLINE_FONT, int(w * 0.05))
    kw = fk.getlength(kick) + w * 0.05
    flash = 1.0 if (t * 2.2) % 1 < 0.7 else 0.55
    d.rectangle([x0 + w * 0.03, y0 + h * 0.018, x0 + w * 0.03 + kw, y0 + h * 0.018 + fk.getbbox("A")[3] * 1.5],
                fill=tuple(int(c * flash) for c in brand.PINK))
    d.text((x0 + w * 0.055, y0 + h * 0.018 + fk.getbbox("A")[3] * 0.18), kick, font=fk, fill=brand.WHITE)
    words = str(spec.get("text", "")).upper().split()
    lines, cur = [], []
    fsize = int(w * 0.11)
    test = brand.font(brand.HEADLINE_FONT, fsize)
    for wd in words:
        if cur and test.getlength(" ".join(cur + [wd])) > (x1 - x0) * 0.9:
            lines.append(" ".join(cur))
            cur = []
        cur.append(wd)
    if cur:
        lines.append(" ".join(cur))
    lines = lines[:3]
    times = _times(len(lines), spec.get("_dur", 3.0) * 0.6, first=0.15, last_gap=0.0)
    area_top, area_bot = y0 + h * 0.075, y1 - h * 0.055
    lh = (area_bot - area_top) / max(1, len(lines))
    for k, (line, t0) in enumerate(zip(lines, times)):
        p = (t - t0) / 0.22
        if p <= 0:
            continue
        pink = _is_pink(line, spec)
        spr = lettering(line, min(fsize, int(lh * 0.9)), int((x1 - x0) * 0.92),
                        *((YELLOW, brand.PINK, brand.CYAN) if pink else (brand.WHITE, brand.CYAN, brand.PINK)))
        place(img, spr, (x0 + x1) / 2, area_top + lh * (k + 0.5), scale=1 + 0.3 * (1 - _back(p)), alpha=min(1.0, p * 1.6))
    tick = str(spec.get("ticker") or "")
    if tick:
        band = [x0 + 3, y1 - h * 0.045, x1 - 3, y1 - 3]
        d = ImageDraw.Draw(img)
        d.rectangle(band, fill=brand.CYAN)
        ft = brand.font(brand.HEADLINE_FONT, int(h * 0.022))
        text = ("   •   ".join([tick] * 4))
        tw = ft.getlength(tick + "   •   ")
        sx = band[0] + w * 0.02 - (t * w * 0.22) % tw
        strip = Image.new("RGBA", (int(band[2] - band[0]), int(band[3] - band[1])), (0, 0, 0, 0))
        ImageDraw.Draw(strip).text((sx - band[0], (band[3] - band[1]) / 2 - ft.getbbox("A")[3] / 2 - 2), text,
                                   font=ft, fill=(13, 7, 23))
        img.alpha_composite(strip, (int(band[0]), int(band[1])))
    return img.convert("RGB")


def hits(spec, dur):
    """When each word, number or item lands on the card (seconds into the segment): the renderer puts a soft pop
    there. A cover segment (first frame shows everything) skips the first beat, which the hook impact covers."""
    kind = spec.get("type")
    if kind == "kinetic":
        lines = spec.get("lines") or str(spec.get("text", "")).split("|")
        out = [t0 + 0.12 for t0 in _times(len(lines[:4]), dur)]
        return out[1:] if spec.get("cover") else out
    if kind == "countdown":
        return [0.2, 0.52]
    if kind == "versus":
        return [0.3, 0.6, 0.85] + ([dur * 0.6] if spec.get("winner") else [])
    if kind == "tier":
        static = {str(x) for x in spec.get("static") or []}
        n = sum(len(r[1]) if isinstance(r[1], list) else 1 for r in spec.get("rows") or []
                if len(r) > 1 and str(r[0]) not in static)
        return [t0 + 0.2 for t0 in _times(n, dur, first=0.25)]
    if kind == "headline":
        return [0.1] + [t0 + 0.15 for t0 in _times(min(3, max(1, len(str(spec.get("text", "")).split()) // 3)),
                                                    dur * 0.6, first=0.15, last_gap=0.0)]
    return []


DRAW = {"kinetic": kinetic_frame, "countdown": countdown_frame, "versus": versus_frame, "tier": tier_frame,
        "headline": headline_frame}
