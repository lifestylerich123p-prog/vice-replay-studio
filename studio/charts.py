"""Our own animated graphics as a segment background (Nov 22, 2026).

Why: YouTube's Oct 1, 2026 Shorts update ranks original videos higher, and voice-over on reused footage doesn't count
as original. Trailer clips under our voice was most of every Short; a leaderboard or a big counter drawn here is 100%
ours. Use trailer footage as short cutaways around it, not as the whole video.

Segment key (episodes/<slug>.json, Shorts or main video):
    "chart": {"type": "bars", "items": [["IShowSpeed, launch", 68.7], ["CarryMinati", 18.1]], "prefix": "",
              "unit": "M", "highlight": 0, "note": "YouTube view counts, Nov 22"}   (+ "floor": 90 to start bars at 90)
    "chart": {"type": "counter", "value": 3.79, "prefix": "$", "unit": "B", "label": "preorders + day one",
              "vs": {"value": 0.8, "prefix": "$", "unit": "B", "label": "GTA 5, day one"}}
    "chart": {"type": "line", "items": [["2008", 59.99], ["2013", 59.99], ["2026", 79.99]], "prefix": "$",
              "highlight": 2, "note": "Launch price, standard edition"}   (a trend over time, max 8 points)
Bars grow one after another (ease-out) while the numbers count up; the highlighted bar is pink, the rest cyan. Everything
is drawn between the headline (top 30%) and the captions (bottom 38%) on Shorts.
"""
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from . import brand

FPS = 30


def _ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def _decimals(values):
    return max((len(str(v).split(".")[1]) if "." in str(v) else 0) for v in values) if values else 0


def _fmt(v, dec, prefix="", unit="", locale="en"):
    s = f"{v:,.{dec}f}" if dec else f"{round(v):,}"
    if locale == "es":  # 3.790,5 (Spanish: dot for thousands, comma for decimals)
        s = s.replace(",", "\0").replace(".", ",").replace("\0", ".")
    return f"{prefix}{s}{unit}"


def _region(w, h):
    vertical = h > w
    if vertical:
        return int(w * 0.07), int(h * 0.315), int(w * 0.93), int(h * 0.595)
    return int(w * 0.08), int(h * 0.24), int(w * 0.92), int(h * 0.80)


PALETTES = [((255, 31, 142), (40, 10, 90)), ((0, 229, 210), (30, 12, 80)), ((120, 40, 200), (255, 31, 142)),
            ((255, 140, 60), (60, 10, 90)), ((0, 150, 255), (90, 20, 120)), ((255, 31, 142), (0, 120, 160))]


def _backdrop(w, h, seed):
    """A gradient at its own angle and colors per chart video (seed), with faint synthwave lines. Nov 22: one shared
    dark neon backdrop made every chart video fingerprint like our old title cards (and like each other)."""
    import math

    import numpy as np
    c1, c2 = PALETTES[seed % len(PALETTES)]
    ang = math.radians((seed * 67) % 360)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = ((xx / w - 0.5) * math.cos(ang) + (yy / h - 0.5) * math.sin(ang)) + 0.5
    t = np.clip(t, 0, 1)[..., None]
    img = (np.array(c1, np.float32) * (1 - t) + np.array(c2, np.float32) * t) * 0.55
    lines = (((xx * math.cos(ang + 1.2) + yy * math.sin(ang + 1.2)) // (h * 0.045)) % 2 == 0)[..., None]
    img = img * np.where(lines, 1.0, 0.86)
    return Image.fromarray(img.clip(0, 255).astype(np.uint8), "RGB")


def _panel(img, box):
    x0, y0, x1, y1 = box
    over = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    pad = int((x1 - x0) * 0.04)
    d.rounded_rectangle([x0 - pad, y0 - pad, x1 + pad, y1 + pad], radius=pad * 2, fill=(13, 7, 23, 200),
                        outline=brand.PINK + (160,), width=4)
    img.alpha_composite(over)


def _note(d, spec, x0, x1, y, h):
    """The source line under a chart, shrunk to fit the panel (Nov 22: a long note ran off the right edge)."""
    if not spec.get("note"):
        return
    size = int(h * 0.018)
    fn = brand.font(brand.BODY_FONT, size)
    while fn.getlength(spec["note"]) > (x1 - x0) and size > int(h * 0.011):
        size -= 1
        fn = brand.font(brand.BODY_FONT, size)
    d.text((x0, y), spec["note"], font=fn, fill=(183, 169, 207))


def bars_frame(base, spec, t, w, h):
    img = base.copy().convert("RGBA")
    x0, y0, x1, y1 = _region(w, h)
    _panel(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    items = spec["items"][:6]
    n = len(items)
    vmax = max(v for _, v in items) or 1
    floor = spec.get("floor", 0)  # e.g. 90 for review scores (99 vs 97 would look identical from 0); stated in "note"
    dec = _decimals([v for _, v in items])
    hl = spec.get("highlight", 0)
    note_h = int(h * 0.028) if spec.get("note") else 0
    row = (y1 - y0 - note_h) / n
    fl = brand.font(brand.BODY_FONT, max(int(w * 0.031), min(int(row * 0.34), int(w * 0.045))))  # >= 34 px on a Short
    fv = brand.font(brand.HEADLINE_FONT, max(int(w * 0.044), min(int(row * 0.52), int(w * 0.075))))
    bar_h = int(row * 0.40)
    for k, (label, v) in enumerate(items):
        p = _ease((t - 0.15 - 0.18 * k) / 0.8)
        top = int(y0 + k * row)
        d.text((x0, top), str(label), font=fl, fill=brand.WHITE)
        by = top + int(row * 0.42)
        # leave room for the longest value label at the end of the longest bar (Nov 22: "$3.790 M" ran off the panel)
        widest = max(fv.getlength(_fmt(x, dec, spec.get("prefix", ""), spec.get("unit", ""), spec.get("locale", "en")))
                     for _, x in items)
        span = min((x1 - x0) * 0.74, (x1 - x0) - widest - w * 0.03)
        full = span * (max(0.0, v - floor) / max(1e-9, vmax - floor))
        col = brand.PINK if k == hl else brand.CYAN
        if p > 0:
            d.rounded_rectangle([x0, by, x0 + max(bar_h, full * p), by + bar_h], radius=bar_h // 2, fill=col)
            txt = _fmt(v * p, dec, spec.get("prefix", ""), spec.get("unit", ""), spec.get("locale", "en"))
            d.text((x0 + max(bar_h, full * p) + int(w * 0.015), by - int(bar_h * 0.35)), txt, font=fv, fill=brand.WHITE)
    _note(d, spec, x0, x1, y1 - note_h + 4, h)
    return img.convert("RGB")


def counter_frame(base, spec, t, w, h):
    """One big number, or two stacked with VS between them (a tall screen reads top to bottom)."""
    img = base.copy().convert("RGBA")
    x0, y0, x1, y1 = _region(w, h)
    _panel(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    sides = [spec] + ([spec["vs"]] if spec.get("vs") else [])
    rows = len(sides)
    rh = (y1 - y0) / (rows + (0.35 if rows == 2 else 0))
    for k, s in enumerate(sides):
        p = _ease((t - 0.1 - 0.45 * k) / 1.0)
        dec = _decimals([s["value"]])
        loc = spec.get("locale", "en")
        txt = _fmt(s["value"] * p, dec, s.get("prefix", ""), s.get("unit", ""), loc)
        final = _fmt(s["value"], dec, s.get("prefix", ""), s.get("unit", ""), loc)
        size = int(rh * (0.55 if rows == 2 else 0.5))
        fv = brand.font(brand.HEADLINE_FONT, size)
        while fv.getlength(final) > (x1 - x0) * 0.9 and size > 30:
            size -= 4
            fv = brand.font(brand.HEADLINE_FONT, size)
        top = y0 + k * rh * (1.35 if rows == 2 else 1) + rh * 0.04
        cx = (x0 + x1) / 2
        d.text((cx - fv.getlength(txt) / 2, top), txt, font=fv, fill=brand.PINK if k == 0 else brand.CYAN)
        if s.get("label"):
            ls = max(int(w * 0.034), int(rh * 0.15))  # >= 36 px on a Short
            fl = brand.font(brand.BODY_FONT, ls)
            while fl.getlength(s["label"]) > (x1 - x0) * 0.9 and ls > 22:
                ls -= 2
                fl = brand.font(brand.BODY_FONT, ls)
            bottom = top + fv.getbbox(final)[3]  # the digits' real bottom edge, so the label never overlaps them
            d.text((cx - fl.getlength(s["label"]) / 2, bottom + int(rh * 0.06)), s["label"], font=fl, fill=brand.WHITE)
    if rows == 2:
        fvs = brand.font(brand.HEADLINE_FONT, int(rh * 0.28))
        vy = y0 + rh * 1.04
        d.text(((x0 + x1) / 2 - fvs.getlength("VS") / 2, vy), "VS", font=fvs, fill=brand.WHITE)
    return img.convert("RGB")


def line_frame(base, spec, t, w, h):
    """A trend that draws itself left to right (prices over the years, views per day...). Each point's value appears
    when the line reaches it; the highlighted point (default: the last) is pink. Added Nov 22 so graph Shorts don't
    all look like the same leaderboard (YouTube's repetitive-content checks look at the whole channel)."""
    img = base.copy().convert("RGBA")
    x0, y0, x1, y1 = _region(w, h)
    _panel(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    items = spec["items"][:8]
    n = len(items)
    loc, pre, unit = spec.get("locale", "en"), spec.get("prefix", ""), spec.get("unit", "")
    dec = _decimals([v for _, v in items])
    hl = spec.get("highlight", n - 1)
    note_h = int(h * 0.028) if spec.get("note") else 0
    fv = brand.font(brand.HEADLINE_FONT, max(int(w * 0.036), int(w * 0.05 * min(1.0, 5 / max(n, 1)))))
    vh = fv.getbbox("0")[3]
    px0, px1 = x0 + int((x1 - x0) * 0.08), x1 - int((x1 - x0) * 0.08)
    # labels may have two lines ("GTA 3\n2001"); shrink them until the widest fits the space between points
    labels = [str(lab).split("\n") for lab, _ in items]
    gap = (px1 - px0) / max(1, n - 1) if n > 1 else (px1 - px0)
    ls = max(int(w * 0.030), int(w * 0.036 * min(1.0, 6 / max(n, 1))))
    fl = brand.font(brand.BODY_FONT, ls)
    while ls > int(w * 0.024) and max(fl.getlength(x) for lab in labels for x in lab) > gap * 0.94:
        ls -= 2
        fl = brand.font(brand.BODY_FONT, ls)
    lh = fl.getbbox("Ay")[3]
    nl = max(len(lab) for lab in labels)
    py0, py1 = y0 + int(vh * 1.6), y1 - note_h - int(lh * (0.9 + 1.15 * nl))
    floor = spec.get("floor", 0)  # start the axis above 0 only when the note says so (honest charts)
    vmax = max(v for _, v in items)
    span = max(1e-9, vmax - floor)
    pts = [(px0 + (px1 - px0) * (k / max(1, n - 1)), py1 - (py1 - py0) * max(0.0, v - floor) / span)
           for k, (_, v) in enumerate(items)]
    d.line([(px0, py1), (px1, py1)], fill=(183, 169, 207), width=max(2, w // 360))  # baseline
    reach = _ease((t - 0.15) / 1.8) * (n - 1)  # how far along the line has drawn, in points
    lw = max(4, int(w * 0.009))
    for k in range(n - 1):
        part = max(0.0, min(1.0, reach - k))
        if part <= 0:
            break
        (ax, ay), (bx, by) = pts[k], pts[k + 1]
        d.line([(ax, ay), (ax + (bx - ax) * part, ay + (by - ay) * part)], fill=brand.CYAN, width=lw)
    for k, ((_, v), (px, py)) in enumerate(zip(items, pts)):
        for j, part_txt in enumerate(labels[k]):
            d.text((px - fl.getlength(part_txt) / 2, py1 + int(lh * (0.45 + 1.15 * j))), part_txt, font=fl,
                   fill=brand.WHITE if j == 0 else (183, 169, 207))
        p = max(0.0, min(1.0, (reach - k + 0.6) / 0.6)) if n > 1 else _ease(t / 0.6)
        if p <= 0:
            continue
        col = brand.PINK if k == hl else brand.CYAN
        r = int(lw * (1.9 if k == hl else 1.3))
        d.ellipse([px - r, py - r, px + r, py + r], fill=col, outline=brand.WHITE, width=max(2, lw // 3))
        txt = _fmt(v * _ease(p), dec, pre, unit, loc)
        tx = min(max(px - fv.getlength(txt) / 2, x0), x1 - fv.getlength(txt))
        d.text((tx, py - r - vh * 1.35), txt, font=fv, fill=brand.PINK if k == hl else brand.WHITE)
    _note(d, spec, x0, x1, y1 - note_h + 4, h)
    return img.convert("RGB")


def _wrap(text_words, font, width):
    lines, cur = [], []
    for wd in text_words:
        if cur and font.getlength(" ".join(cur + [wd])) > width:
            lines.append(cur)
            cur = []
        cur.append(wd)
    return lines + ([cur] if cur else [])


def quote_frame(base, spec, t, w, h):
    """A quote card: the exact words someone said appear word by word (~8 words/s), words listed in `pink` light up,
    then who said it and where. Nov 22: Rockstar interviews and streamer stories have no numbers to chart, and a
    trailer clip under our voice isn't original; their own words in our typography is (keep quotes short and exact)."""
    img = base.copy().convert("RGBA")
    x0, y0, x1, y1 = _region(w, h)
    _panel(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    words = str(spec["text"]).split()
    pink = {p.lower().strip(".,!?\"'") for p in spec.get("pink", []) for p in str(p).split()}
    who_font = brand.font(brand.BODY_FONT, max(int(w * 0.032), int((y1 - y0) * 0.065)))
    mark_font = brand.font(brand.HEADLINE_FONT, int((y1 - y0) * 0.30))
    top = y0 + int((y1 - y0) * 0.17)
    room = (y1 - y0) * 0.80 - (top - y0) - who_font.getbbox("Ay")[3] * 1.6
    size = int(w * 0.075)
    while True:
        f = brand.font(brand.BODY_FONT, size)
        lines = _wrap(words, f, (x1 - x0) * 0.92)
        lh = f.getbbox("Ay")[3] * 1.22
        if len(lines) * lh <= room or size <= int(w * 0.034):
            break
        size -= 2
    block = len(lines) * lh + (who_font.getbbox("Ay")[3] * 1.6 if spec.get("who") else 0)
    top = max(top, y0 + ((y1 - y0) - block) / 2)  # centre the quote in the panel when it's short
    if spec.get("mark", True):
        d.text((x0, y0 - int((y1 - y0) * 0.06)), "“", font=mark_font, fill=brand.PINK)
    shown = len(words) * _ease((t - 0.15) / max(0.6, len(words) / 8))
    k = 0
    for row, line in enumerate(lines):
        x = x0 + ((x1 - x0) - f.getlength(" ".join(line))) / 2
        y = top + row * lh
        for wd in line:
            on = k < shown
            key = wd.lower().strip(".,!?\"'")
            col = (brand.PINK if key in pink else brand.WHITE) if on else (70, 52, 92)
            d.text((x, y), wd, font=f, fill=col)
            x += f.getlength(wd + " ")
            k += 1
    if spec.get("who") and shown >= len(words):
        who = str(spec["who"])
        d.text(((x0 + x1) / 2 - who_font.getlength(who) / 2, top + len(lines) * lh + lh * 0.35), who, font=who_font,
               fill=brand.CYAN)
    _note(d, spec, x0, x1, y1 - int(h * 0.028) + 4, h)
    return img.convert("RGB")


GOOD = {"in", "yes", "sí", "si", "real", "true", "✓"}


def list_frame(base, spec, t, w, h):
    """A checklist: rows pop in one after another, each with a tag on the right (IN / CUT, YES / NO, REAL / FAKE).
    Tags in GOOD (or spec["good"]) are cyan, the rest pink. Nov 22 evening (owner: facts only, no footage)."""
    img = base.copy().convert("RGBA")
    x0, y0, x1, y1 = _region(w, h)
    _panel(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    items = spec["items"][:6]
    good = {str(g).lower() for g in spec.get("good", [])} or GOOD
    note_h = int(h * 0.028) if spec.get("note") else 0
    title_h = 0
    if spec.get("title"):
        ft = brand.font(brand.HEADLINE_FONT, int(w * 0.05))
        d.text(((x0 + x1) / 2 - ft.getlength(spec["title"]) / 2, y0), spec["title"], font=ft, fill=brand.WHITE)
        title_h = int(ft.getbbox("A")[3] * 1.5)
    row = (y1 - y0 - note_h - title_h) / max(1, len(items))
    fl = brand.font(brand.BODY_FONT, max(int(w * 0.04), min(int(row * 0.42), int(w * 0.065))))
    fg = brand.font(brand.HEADLINE_FONT, max(int(w * 0.04), min(int(row * 0.46), int(w * 0.07))))
    for k, (label, tag) in enumerate(items):
        p = _ease((t - 0.15 - 0.4 * k) / 0.35)
        if p <= 0:
            continue
        cy = y0 + title_h + k * row + row / 2
        shift = (1 - p) * w * 0.08
        lab = str(label)
        d.text((x0 + shift, cy - fl.getbbox("Ay")[3] / 2), lab, font=fl, fill=brand.WHITE)
        tg = str(tag)
        col = brand.CYAN if tg.lower() in good else brand.PINK
        tw = fg.getlength(tg)
        pad = int(w * 0.018)
        bh = fg.getbbox("A")[3] + pad * 2
        bx1 = x1 - shift * 0.5
        bw = max(tw + pad * 3, bh * 1.6)
        d.rounded_rectangle([bx1 - bw, cy - bh / 2, bx1, cy + bh / 2], radius=int(bh / 2), fill=col)
        d.text((bx1 - bw / 2 - tw / 2, cy - bh / 2 + pad * 0.7), tg, font=fg, fill=(13, 7, 23))
    _note(d, spec, x0, x1, y1 - note_h + 4, h)
    return img.convert("RGB")


def text_frame(base, spec, t, w, h):
    """A big statement card (a hook or the closing question): the words appear one by one, `pink` words light up,
    optional `sub` line under it. Same engine as the quote card, without quote marks."""
    return quote_frame(base, {**spec, "mark": False, "who": spec.get("sub")}, t, w, h)


def quiz_frame(base, spec, t, w, h):
    """A quiz question (Nov 22 evening, owner: "how much do you know" Shorts): `q` on top, `options` as A/B/C rows
    popping in, a countdown bar while the viewer guesses. With `"reveal": true` (the answer segment) the right option
    (`answer`, 0-based) turns cyan with a check and the others fade. Optional `tag` ("1/3") top-left."""
    img = base.copy().convert("RGBA")
    x0, y0, x1, y1 = _region(w, h)
    _panel(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    opts = [str(o) for o in spec["options"][:4]]
    ans, reveal = spec.get("answer", 0), bool(spec.get("reveal"))
    if spec.get("tag"):
        ftag = brand.font(brand.HEADLINE_FONT, int(w * 0.04))
        d.text((x0, y0 - int(h * 0.004)), str(spec["tag"]), font=ftag, fill=brand.CYAN)
    qsize = int(w * 0.058)
    while True:
        fq = brand.font(brand.BODY_FONT, qsize)
        lines = _wrap(str(spec["q"]).split(), fq, (x1 - x0) * 0.94)
        if len(lines) <= 2 or qsize <= int(w * 0.04):
            break
        qsize -= 2
    lh = fq.getbbox("Ay")[3] * 1.18
    qy = y0 + int(h * 0.03)
    for k, line in enumerate(lines):
        txt = " ".join(line)
        d.text(((x0 + x1) / 2 - fq.getlength(txt) / 2, qy + k * lh), txt, font=fq, fill=brand.WHITE)
    top = qy + len(lines) * lh + int(h * 0.018)
    bottom = y1 - int(h * 0.03)
    row = (bottom - top) / max(1, len(opts))
    fo = brand.font(brand.BODY_FONT, max(int(w * 0.04), min(int(row * 0.40), int(w * 0.055))))
    fl = brand.font(brand.HEADLINE_FONT, max(int(w * 0.04), min(int(row * 0.42), int(w * 0.06))))
    for k, o in enumerate(opts):
        p = 1.0 if reveal else _ease((t - 0.1 - 0.18 * k) / 0.3)
        if p <= 0:
            continue
        cy = top + k * row + row / 2
        right = reveal and k == ans
        faded = reveal and k != ans
        fill = brand.CYAN if right else ((60, 44, 82) if faded else (40, 24, 66))
        d.rounded_rectangle([x0, cy - row * 0.38, x1, cy + row * 0.38], radius=int(row * 0.2), fill=fill,
                            outline=None if right else brand.PINK + (90,), width=2)
        letter = "ABCD"[k]
        d.text((x0 + int(w * 0.025), cy - fl.getbbox("A")[3] / 2 - 2), letter, font=fl,
               fill=(13, 7, 23) if right else (brand.PINK if not faded else (110, 80, 120)))
        tx = x0 + int(w * 0.10)
        d.text((tx, cy - fo.getbbox("Ay")[3] / 2), o, font=fo,
               fill=(13, 7, 23) if right else ((130, 110, 150) if faded else brand.WHITE))
        if right:  # a drawn check mark (the brand fonts have no check glyph)
            cx, sz = tx + fo.getlength(o) + int(w * 0.035), int(row * 0.16)
            d.line([(cx, cy), (cx + sz * 0.8, cy + sz * 0.8), (cx + sz * 2.2, cy - sz * 0.9)], fill=(13, 7, 23),
                   width=max(4, int(w * 0.008)), joint="curve")
    if not reveal:  # countdown bar while the viewer guesses
        frac = max(0.0, 1 - max(0.0, t - 0.6) / max(0.5, spec.get("think", 2.5)))
        bw = (x1 - x0) * frac
        d.rounded_rectangle([x0, y1 - int(h * 0.016), x0 + max(int(h * 0.01), bw), y1 - int(h * 0.006)],
                            radius=int(h * 0.005), fill=brand.PINK)
    return img.convert("RGB")


_MAP = {}


def map_frame(base, spec, t, w, h):
    """A "where is it" card (owner approved Nov 24: the official map with pins/zoom in videos): Rockstar's official
    Leonida map, starting on the whole state and zooming to `at` (a place printed on the map, a grid cell like "G7", or
    [x, y] fractions; `dx`/`dy` nudge it), then a pulsing numbered pin and our `label`. Spec: {"type": "map",
    "at": "Kelly County", "label": "UFO · after 2 AM", "n": 1, "to": 0.28 (final visible width share)}."""
    from . import mappins
    if "img" not in _MAP:
        _MAP["img"] = mappins.map_image()
    im = _MAP["img"]
    W, H = im.size
    fx, fy = mappins.where(spec.get("at", "Vice City"))
    tx, ty = (fx + spec.get("dx", 0)) * W, (fy + spec.get("dy", 0)) * H
    dur = max(spec.get("_dur", 4.0), 0.5)
    p = min(1.0, t / (dur * 0.55))
    e = 1 - (1 - p) ** 3
    vh0 = H                                   # start: the whole height of the map
    vh1 = W * float(spec.get("to", 0.28)) * h / w
    vh = vh0 * (1 - e) + vh1 * e
    vw = vh * w / h
    cx = (W / 2) * (1 - e) + tx * e
    cy = (H / 2) * (1 - e) + ty * e
    x0, y0 = max(0, min(W - vw, cx - vw / 2)), max(0, min(H - vh, cy - vh / 2))
    if vw > W:                                # wider than the map: centre it on a dark band
        x0 = (W - vw) / 2
    frame = im.crop((int(x0), int(y0), int(x0 + vw), int(y0 + vh))).resize((w, h), Image.BILINEAR)
    if vw > W:
        frame = frame.copy()
    d = ImageDraw.Draw(frame)
    px, py = (tx - x0) / vw * w, (ty - y0) / vh * h
    if p >= 1.0:
        k = (t - dur * 0.55) * FPS
        pulse = 1 + 0.18 * abs((k / FPS * 2) % 2 - 1)
        mappins._pin(d, px, py, spec.get("n", ""), 1.9 * pulse)
        if spec.get("label"):
            mappins._label(d, px, py, spec["label"], 1.9, w, spec.get("side"))
    f = brand.font(brand.BODY_FONT, 26)
    credit = "Map: Rockstar Games (official)"
    d.text((w - f.getlength(credit) - 24, h - 130), credit, font=f, fill=(255, 255, 255))
    return frame


DRAW = {"bars": bars_frame, "counter": counter_frame, "line": line_frame, "quote": quote_frame, "list": list_frame,
        "text": text_frame, "quiz": quiz_frame, "map": map_frame}


def _source_line(img, spec, w, h):
    """A small on-screen source under the card ("src": "Metacritic · VGC"): YouTube's July 2026 originality guidance
    rewards visible research; viewers see where a number comes from (owner rule: facts checked in 2+ sources)."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = _region(w, h)
    label = ("Fuente: " if spec.get("locale") == "es" else "Source: ") + str(spec["src"])
    size = int(min(w, h) * 0.026)
    fn = brand.font(brand.BODY_FONT, size)
    while fn.getlength(label) > (x1 - x0) and size > 12:
        size -= 1
        fn = brand.font(brand.BODY_FONT, size)
    # vertical: above the card (two-line captions reach up to ~60% of the height); 16:9: under it
    y = y0 - int(size * 1.55) if h > w else y1 + int(h * 0.02)
    d.text(((x0 + x1) / 2 - fn.getlength(label) / 2, y), label, font=fn, fill=(200, 190, 220))
    return img


ZOOM = 1.12  # photo cards: the picture starts at 112% of the frame and slowly zooms in to 102%


def _photo_base(path, w, h):
    """Photo cards (owner approved Nov 24): the screenshot cover-cropped to ZOOM x the frame, darkened with a top/bottom
    gradient and a purple shade so neon lettering reads on any picture. None if the file is missing."""
    from PIL import ImageEnhance
    root = Path(__file__).resolve().parent.parent
    f = Path(path) if Path(path).is_absolute() else root / path
    if not f.exists():
        return None
    from . import officialhd
    f = officialhd.best(f)  # Nov 24: the 4K original (a 9:16 slice of a 1920 px shot was blown up ~2.2x)
    W, H = int(w * ZOOM), int(h * ZOOM)
    im = Image.open(f).convert("RGB")
    r = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    left, top = (im.width - W) // 2, (im.height - H) // 2
    im = im.crop((left, top, left + W, top + H))
    # Nov 24 "hook v2" (owner: full creative access): the picture was darkened so much it read as a plain dark set.
    # Brighter and punchier now; the dark band sits only where text goes (logo/slab on top, captions at the bottom).
    im = ImageEnhance.Brightness(im).enhance(0.72)
    im = ImageEnhance.Contrast(im).enhance(1.08)
    im = ImageEnhance.Color(im).enhance(1.25)
    grad = Image.new("L", (1, H))
    for y in range(H):  # 0 = full picture, 255 = night purple
        v = y / H
        top = max(0.0, (0.16 - v) / 0.16)            # logo + headline slab
        bottom = max(0.0, (v - 0.58) / 0.42)         # captions and YouTube's own buttons
        grad.putpixel((0, y), int(255 * min(0.92, 0.22 + 0.55 * top + 0.70 * bottom ** 1.2)))
    shade = Image.new("RGB", (W, H), (14, 4, 30))
    return Image.composite(shade, im, grad.resize((W, H)))


def _photo_frame(base, p, w, h, t=None, hook=False):
    """Slow push-in over the card. On a Short's hook card (hook=True) the camera first punches in fast during the first
    0.45 s, so the opening frame moves (Nov 22 data: Shorts that open on motion got ~5x the views)."""
    s = ZOOM - 0.10 * max(0.0, min(1.0, p))
    if hook and t is not None:
        k = min(1.0, t / 0.45)
        s = ZOOM - 0.13 * (1 - (1 - k) ** 3) - 0.06 * max(0.0, min(1.0, p))
    cw, ch = int(w * s), int(h * s)
    x0, y0 = (base.width - cw) // 2, (base.height - ch) // 2
    return base.crop((x0, y0, x0 + cw, y0 + ch)).resize((w, h), Image.BILINEAR)


def render(spec, dur, w, h, out, seed=0):
    """Write an mp4 (no audio) of the animated chart, dur seconds long; returns its path. The GTA 6-style cards
    (studio/vicecards.py: kinetic, countdown, versus, tier, headline) and any chart with "bg": "vice" play on the
    animated Vice City set (sunset, palms, scrolling neon grid); the rest keep the gradient backdrop."""
    from . import vicecards
    out = Path(out)
    kind = spec.get("type")
    draw = vicecards.DRAW.get(kind) or DRAW.get(kind, bars_frame)
    bgname = str(spec.get("bg", "vice" if kind in vicecards.DRAW else "gradient"))
    photo = _photo_base(bgname[6:], w, h) if bgname.startswith("photo:") else None
    vice = bgname == "vice" or (bgname.startswith("photo:") and photo is None)
    sd = spec.get("seed", seed)
    if vice:
        still, horizon = vicecards.sky(w, h, sd)
    elif photo is None:
        base = _backdrop(w, h, seed=sd)
    spec = dict(spec, _dur=dur)
    shift = 5.0 if spec.get("cover") and kind != "kinetic" else 0.0  # cover: show the finished card from frame one
    proc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                             "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)
    for f in range(max(1, int(round(dur * FPS)))):
        t = f / FPS
        if photo is not None:  # Nov 24 photo cards: a real GTA 6 screenshot behind the lettering, slow zoom in
            bg = _photo_frame(photo, t / max(dur, 0.1), w, h, t=t, hook=bool(spec.get("cover")))
        else:
            bg = vicecards.frame_bg(still, horizon, t, w, h) if vice else base
        frame = draw(bg, spec, t + shift, w, h)
        if spec.get("src"):
            frame = _source_line(frame, spec, w, h)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    proc.wait()
    if kind in vicecards.DRAW and not shift:  # where the lettering lands, for the renderer's sound effects
        import json
        out.with_suffix(".hits.json").write_text(json.dumps([round(x, 3) for x in vicecards.hits(spec, dur)]))
    return out
