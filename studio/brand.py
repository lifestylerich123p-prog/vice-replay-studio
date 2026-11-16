"""Vice Replay brand kit: colors, fonts and generated graphics (Pillow)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
HEADLINE_FONT = str(FONTS / "Anton.ttf")
BODY_FONT = str(FONTS / "Montserrat.ttf")

PINK = (255, 31, 142)
CYAN = (0, 229, 210)
WHITE = (255, 255, 255)
NIGHT = (10, 6, 24)
PURPLE = (60, 14, 90)


def font(path, size):
    return ImageFont.truetype(path, size)


def neon_background(w, h, seed=0):
    """Synthwave night sky: gradient, sun, skyline silhouettes, neon horizon."""
    import random
    rnd = random.Random(seed)
    img = Image.new("RGB", (w, h), NIGHT)
    d = ImageDraw.Draw(img)
    horizon = int(h * 0.68)
    for y in range(horizon):
        t = y / horizon
        c = tuple(int(NIGHT[i] + (PURPLE[i] - NIGHT[i]) * t + (PINK[i] - PURPLE[i]) * max(0, t - 0.7) * 1.6) for i in range(3))
        d.line([(0, y), (w, y)], fill=c)
    # sun
    sun = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun)
    r = int(min(w, h) * 0.22)
    cx = int(w * (0.62 + rnd.uniform(-0.1, 0.1)))
    for i in range(r, 0, -2):
        t = i / r
        sd.ellipse([cx - i, horizon - r - i + r // 3, cx + i, horizon - r + i + r // 3],
                   fill=(255, int(60 + 140 * (1 - t)), int(120 + 40 * t), 255))
    for k in range(6):  # retro sun stripes
        y = horizon - r // 2 + k * (r // 9)
        sd.rectangle([0, y, w, y + 3 + k], fill=(0, 0, 0, 0))
    img.paste(sun, (0, 0), sun)
    # skyline
    x = 0
    while x < w:
        bw = rnd.randint(w // 60, w // 22)
        bh = rnd.randint(h // 20, h // 4)
        d.rectangle([x, horizon - bh, x + bw, horizon], fill=(14, 8, 30))
        for wy in range(horizon - bh + 8, horizon - 6, 14):
            for wx in range(x + 4, x + bw - 4, 10):
                if rnd.random() < 0.18:
                    d.rectangle([wx, wy, wx + 3, wy + 5], fill=rnd.choice([PINK, CYAN, (255, 210, 120)]))
        x += bw + rnd.randint(0, 6)
    # water / grid
    d.rectangle([0, horizon, w, h], fill=(8, 4, 20))
    for i in range(1, 14):
        y = horizon + int((h - horizon) * (i / 14) ** 1.8)
        d.line([(0, y), (w, y)], fill=(90, 20, 110), width=2)
    for i in range(-20, 21):
        d.line([(w // 2 + i * w // 40, horizon), (w // 2 + i * w // 6, h)], fill=(70, 16, 95), width=2)
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.line([(0, horizon), (w, horizon)], fill=CYAN + (255,), width=6)
    glow = glow.filter(ImageFilter.GaussianBlur(8))
    img.paste(glow, (0, 0), glow)
    d.line([(0, horizon), (w, horizon)], fill=CYAN, width=2)
    return img


def logo(size):
    """Replay-arrow ring with a play triangle, like the channel icon."""
    s = size * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pad, wdt = s * 0.08, int(s * 0.13)
    d.arc([pad, pad, s - pad, s - pad], 40, 330, fill=PINK, width=wdt)
    ax, ay = s * 0.80, s * 0.20
    d.polygon([(ax - s * 0.16, ay - s * 0.05), (ax + s * 0.12, ay + s * 0.02), (ax - s * 0.02, ay + s * 0.24)], fill=PINK)
    d.polygon([(s * 0.40, s * 0.32), (s * 0.40, s * 0.68), (s * 0.70, s * 0.50)], fill=PINK)
    return im.resize((size, size), Image.LANCZOS)


def wordmark(height):
    """'VICE REPLAY' wordmark (white + cyan) with the logo, transparent PNG."""
    f = font(HEADLINE_FONT, height)
    w1 = f.getlength("VICE ")
    w2 = f.getlength("REPLAY")
    lg = logo(int(height * 1.15))
    W = int(lg.width + height * 0.25 + w1 + w2 + 10)
    im = Image.new("RGBA", (W, int(height * 1.35)), (0, 0, 0, 0))
    im.paste(lg, (0, int(height * 0.08)), lg)
    d = ImageDraw.Draw(im)
    x = lg.width + height * 0.25
    d.text((x, 0), "VICE ", font=f, fill=WHITE, stroke_width=max(2, height // 18), stroke_fill=NIGHT)
    d.text((x + w1, 0), "REPLAY", font=f, fill=CYAN, stroke_width=max(2, height // 18), stroke_fill=NIGHT)
    return im


def fit_lines(text, fnt_path, max_w, start_size, min_size=40):
    """Largest font size where the text wraps into <=3 lines within max_w."""
    words = text.split()
    size = start_size
    while size >= min_size:
        f = font(fnt_path, size)
        lines, cur = [], ""
        for wd in words:
            t = (cur + " " + wd).strip()
            if f.getlength(t) <= max_w:
                cur = t
            else:
                lines.append(cur)
                cur = wd
        lines.append(cur)
        if len(lines) <= 3 and all(f.getlength(l) <= max_w for l in lines):
            return f, lines
        size -= 6
    return font(fnt_path, min_size), [text]


def headline_card(text, w, h, vertical=False):
    """Transparent overlay: slanted pink slab with the segment headline + channel bug."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if text:
        max_w = int(w * (0.82 if vertical else 0.55))
        f, lines = fit_lines(text.upper(), HEADLINE_FONT, max_w, int(h * (0.06 if vertical else 0.085)))
        lh = int(f.size * 1.12)
        x0 = int(w * 0.05)
        y0 = int(h * (0.17 if vertical else 0.14))
        for i, ln in enumerate(lines):
            tw = f.getlength(ln)
            y = y0 + i * (lh + 10)
            skew = 18
            d.polygon([(x0 - 16 + skew, y - 4), (x0 + tw + 22 + skew, y - 4), (x0 + tw + 22, y + lh + 2), (x0 - 16, y + lh + 2)],
                      fill=PINK + (235,))
            d.text((x0, y - f.size * 0.06), ln, font=f, fill=WHITE)
    wm = wordmark(int(h * (0.026 if vertical else 0.04)))
    im.paste(wm, (int(w * 0.03), int(h * 0.03)), wm)
    return im


def thumbnail(line1, line2, tag, out, bg_image=None, w=1280, h=720):
    """YouTube thumbnail in the channel style: wordmark, huge white + pink text, cyan tag."""
    if bg_image:
        bg = Image.open(bg_image).convert("RGB")
        r = max(w / bg.width, h / bg.height)
        bg = bg.resize((int(bg.width * r) + 1, int(bg.height * r) + 1), Image.LANCZOS)
        bg = bg.crop(((bg.width - w) // 2, (bg.height - h) // 2, (bg.width - w) // 2 + w, (bg.height - h) // 2 + h))
    else:
        bg = neon_background(w, h, seed=hash(line1 + line2) % 1000)
    # darken the left half so the text pops
    shade = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for x in range(w):
        a = int(max(0, 200 * (1 - x / (w * 0.75))))
        sd.line([(x, 0), (x, h)], fill=(0, 0, 0, a))
    img = bg.convert("RGBA")
    img.alpha_composite(shade)
    d = ImageDraw.Draw(img)
    wm = wordmark(56)
    img.alpha_composite(wm, (30, 24))
    max_w = int(w * 0.62)
    f1, l1 = fit_lines(line1.upper(), HEADLINE_FONT, max_w, 170, 60)
    f2, l2 = fit_lines(line2.upper(), HEADLINE_FONT, max_w, 210, 60)
    def put(y, ln, f, stroke, slab=False):
        # place by real glyph box so lines never overlap
        l, t, r, b = f.getbbox(ln, stroke_width=stroke)
        if slab:
            pad = 18
            d.polygon([(22, y - pad), (40 + r + 34, y - pad), (40 + r + 20, y + (b - t) + pad),
                       (8, y + (b - t) + pad)], fill=PINK)
        d.text((40, y - t), ln, font=f, fill=WHITE, stroke_width=stroke, stroke_fill=NIGHT)
        return y + (b - t)

    y = 120
    for ln in l1:
        y = put(y, ln, f1, 8) + 22
    y += 18
    for ln in l2:
        y = put(y, ln, f2, 6, slab=True) + 40
    if tag:
        ft = font(HEADLINE_FONT, 54)
        tw = ft.getlength(tag.upper())
        ty = min(y + 4, h - 90)
        d.polygon([(40, ty), (80 + tw, ty), (70 + tw, ty + 70), (30, ty + 70)], fill=NIGHT, outline=CYAN, width=5)
        d.text((56, ty + 2), tag.upper(), font=ft, fill=WHITE)
    img.convert("RGB").save(out, quality=92)
    return out
