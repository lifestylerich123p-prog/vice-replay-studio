"""Our own animated graphics as a segment background (Nov 22, 2026).

Why: YouTube's Oct 1, 2026 Shorts update ranks original videos higher, and voice-over on reused footage doesn't count
as original. Trailer clips under our voice was most of every Short; a leaderboard or a big counter drawn here is 100%
ours. Use trailer footage as short cutaways around it, not as the whole video.

Segment key (episodes/<slug>.json, Shorts or main video):
    "chart": {"type": "bars", "items": [["IShowSpeed, launch", 68.7], ["CarryMinati", 18.1]], "prefix": "",
              "unit": "M", "highlight": 0, "note": "YouTube view counts, Nov 22"}
    "chart": {"type": "counter", "value": 3.79, "prefix": "$", "unit": "B", "label": "preorders + day one",
              "vs": {"value": 0.8, "prefix": "$", "unit": "B", "label": "GTA 5, day one"}}
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


def _fmt(v, dec, prefix="", unit=""):
    s = f"{v:,.{dec}f}" if dec else f"{round(v):,}"
    return f"{prefix}{s}{unit}"


def _region(w, h):
    vertical = h > w
    if vertical:
        return int(w * 0.07), int(h * 0.315), int(w * 0.93), int(h * 0.595)
    return int(w * 0.08), int(h * 0.24), int(w * 0.92), int(h * 0.80)


def _backdrop(w, h, seed):
    bg = brand.neon_background(w, h, seed=seed).convert("RGB").filter(ImageFilter.GaussianBlur(6))
    shade = Image.new("RGB", (w, h), brand.NIGHT)
    return Image.blend(bg, shade, 0.45)


def _panel(img, box):
    x0, y0, x1, y1 = box
    over = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    pad = int((x1 - x0) * 0.04)
    d.rounded_rectangle([x0 - pad, y0 - pad, x1 + pad, y1 + pad], radius=pad * 2, fill=(13, 7, 23, 200),
                        outline=brand.PINK + (160,), width=4)
    img.alpha_composite(over)


def bars_frame(base, spec, t, w, h):
    img = base.copy().convert("RGBA")
    x0, y0, x1, y1 = _region(w, h)
    _panel(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    items = spec["items"][:6]
    n = len(items)
    vmax = max(v for _, v in items) or 1
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
        full = (x1 - x0) * 0.74 * (v / vmax)
        col = brand.PINK if k == hl else brand.CYAN
        if p > 0:
            d.rounded_rectangle([x0, by, x0 + max(bar_h, full * p), by + bar_h], radius=bar_h // 2, fill=col)
            txt = _fmt(v * p, dec, spec.get("prefix", ""), spec.get("unit", ""))
            d.text((x0 + max(bar_h, full * p) + int(w * 0.015), by - int(bar_h * 0.35)), txt, font=fv, fill=brand.WHITE)
    if spec.get("note"):
        fn = brand.font(brand.BODY_FONT, int(h * 0.018))
        d.text((x0, y1 - note_h + 4), spec["note"], font=fn, fill=(183, 169, 207))
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
        txt = _fmt(s["value"] * p, dec, s.get("prefix", ""), s.get("unit", ""))
        final = _fmt(s["value"], dec, s.get("prefix", ""), s.get("unit", ""))
        size = int(rh * (0.55 if rows == 2 else 0.5))
        fv = brand.font(brand.HEADLINE_FONT, size)
        while fv.getlength(final) > (x1 - x0) * 0.9 and size > 30:
            size -= 4
            fv = brand.font(brand.HEADLINE_FONT, size)
        top = y0 + k * rh * (1.35 if rows == 2 else 1) + rh * 0.04
        cx = (x0 + x1) / 2
        d.text((cx - fv.getlength(txt) / 2, top), txt, font=fv, fill=brand.PINK if k == 0 else brand.CYAN)
        if s.get("label"):
            ls = max(26, int(rh * 0.15))
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


def render(spec, dur, w, h, out, seed=0):
    """Write an mp4 (no audio) of the animated chart, dur seconds long; returns its path."""
    out = Path(out)
    base = _backdrop(w, h, seed=spec.get("seed", seed))
    draw = counter_frame if spec.get("type") == "counter" else bars_frame
    proc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                             "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)
    for f in range(max(1, int(round(dur * FPS)))):
        proc.stdin.write(draw(base, spec, f / FPS, w, h).tobytes())
    proc.stdin.close()
    proc.wait()
    return out
