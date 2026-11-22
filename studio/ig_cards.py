"""Instagram carousel cards (free, no AI images): our brand look on official screenshots, 1080x1350 JPEGs.

    python -m studio.ig_cards content/carousels/<slug>.json      # -> output/carousels/<slug>/01.jpg ...

Spec (JSON): {"slug", "caption", "first_comment", "cover": {"title", "subtitle", "bg"},
              "tips": [{"title", "text", "bg", "code"?}...], "cta": {"title", "text", "bg"}}
code (optional) = a button sequence like "↑ → ↓ ←", drawn big in even cells under the title.
bg = a file name in media/official/ (only official screenshots; keep the excluded shots in owner.md out).
Only facts we already checked (episodes / site guides); label reports as reports.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import brand

ROOT = Path(__file__).resolve().parent.parent
W, H = 1080, 1350
ARROW_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # even ←↑→↓ for "code" rows


def background(name):
    p = ROOT / "media" / "official" / name
    im = Image.open(p).convert("RGB") if p.exists() else brand.neon_background(W, H).convert("RGB")
    s = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    im = im.crop((x, y, x + W, y + H))
    # darken toward the bottom so text reads on any picture
    shade = Image.new("L", (W, H))
    sd = ImageDraw.Draw(shade)
    for yy in range(H):
        sd.line([(0, yy), (W, yy)], fill=int(90 + 140 * (yy / H) ** 1.2))
    night = Image.new("RGB", (W, H), brand.NIGHT)
    return Image.composite(night, im, shade)


def wrap(text, fnt, max_w):
    """Word-wrap to max_w; a "\n" in the text starts a new line (Nov 22: quiz options one per line)."""
    out = []
    for para in str(text).split("\n"):
        lines, cur = [], ""
        for wd in para.split():
            t = (cur + " " + wd).strip()
            if fnt.getlength(t) <= max_w:
                cur = t
            else:
                lines.append(cur)
                cur = wd
        out += lines + [cur]
    return out


def header(im, page, total):
    wm = brand.wordmark(46)
    im.paste(wm, (48, 44), wm)
    d = ImageDraw.Draw(im)
    f = brand.font(brand.BODY_FONT, 30)
    t = f"{page}/{total}"
    d.text((W - 48 - f.getlength(t), 56), t, font=f, fill=brand.WHITE)


def footer(d, text="vicereplay.com"):
    f = brand.font(brand.BODY_FONT, 32)
    d.text(((W - f.getlength(text)) / 2, H - 80), text, font=f, fill=brand.CYAN)


def boxed_title(d, text, y, size=120, color=brand.PINK, max_w=W - 120):
    f, lines = brand.fit_lines(text.upper(), brand.HEADLINE_FONT, max_w, size, 60)
    for ln in lines:
        tw = f.getlength(ln)
        x = 60
        d.rectangle([x - 18, y - 4, x + tw + 18, y + f.size * 1.12], fill=color)
        d.text((x, y - f.size * 0.06), ln, font=f, fill=brand.WHITE)
        y += int(f.size * 1.22)
    return y


def body(d, text, y, size=46, color=brand.WHITE):
    f = brand.font(brand.BODY_FONT, size)
    for ln in wrap(text, f, W - 140):
        d.text((62, y), ln, font=f, fill=color, stroke_width=2, stroke_fill=brand.NIGHT)
        y += int(size * 1.35)
    return y


def code_row(d, code, y, max_w=W - 120):
    """Button sequence (e.g. "↑ → ↓ ←") drawn arrow by arrow in even cells: the brand fonts draw arrows in uneven sizes."""
    keys = code.split()
    size = 96
    while True:
        f = ImageFont.truetype(ARROW_FONT, size)
        cell = max(f.getlength(c) for c in keys) + size * 0.18
        if cell * len(keys) + 60 <= max_w or size <= 40:
            break
        size -= 4
    h = size + 50
    d.rounded_rectangle([60, y, 60 + cell * len(keys) + 60, y + h], 28, fill=(13, 7, 23, 235), outline=brand.CYAN, width=4)
    for i, c in enumerate(keys):
        x = 90 + cell * i + (cell - f.getlength(c)) / 2
        d.text((x, y + 25 - size * 0.12), c, font=f, fill=brand.CYAN)
    return y + h


def build(spec_path):
    spec = json.loads(Path(spec_path).read_text())
    out = ROOT / "output" / "carousels" / spec["slug"]
    out.mkdir(parents=True, exist_ok=True)
    pages = [("cover", spec["cover"])] + [("tip", t) for t in spec["tips"]] + [("cta", spec["cta"])]
    files = []
    for k, (kind, p) in enumerate(pages, 1):
        im = background(p.get("bg", "vice-city-05.jpg"))
        header(im, k, len(pages))
        d = ImageDraw.Draw(im)
        if kind == "cover":
            y = boxed_title(d, p["title"], 640, 132)
            y = body(d, p.get("subtitle", ""), y + 30, 50, brand.CYAN)
            f = brand.font(brand.HEADLINE_FONT, 54)
            t = "SWIPE  →"
            d.rounded_rectangle([60, H - 210, 60 + f.getlength(t) + 60, H - 130], 40, fill=brand.CYAN)
            d.text((90, H - 206), t, font=f, fill=brand.NIGHT)
        elif kind == "tip":
            n = str(k - 1)
            top = 400 if p.get("code") else 520  # cards with a code start higher to fit it
            f = brand.font(brand.HEADLINE_FONT, 150)
            d.ellipse([60, top, 260, top + 200], fill=brand.PINK)
            d.text((160 - f.getlength(n) / 2, top + 7), n, font=f, fill=brand.WHITE)
            y = boxed_title(d, p["title"], top + 250, 96, brand.NIGHT)
            if p.get("code"):
                y = code_row(d, p["code"], y + 30)
            body(d, p["text"], y + 26)
            footer(d)
        else:
            lg = brand.logo(170)
            im.paste(lg, (60, 400), lg)
            d = ImageDraw.Draw(im)
            y = boxed_title(d, p["title"], 620, 110)
            y = body(d, p.get("text", ""), y + 30, 48, brand.CYAN)
            footer(d)
        f_path = out / f"{k:02d}.jpg"
        im.convert("RGB").save(f_path, quality=92)
        files.append(f_path)
    # contact sheet to check the look once
    thumbs = [Image.open(f).resize((270, 338)) for f in files]
    sheet = Image.new("RGB", (270 * len(thumbs), 338), brand.NIGHT)
    for i, t in enumerate(thumbs):
        sheet.paste(t, (270 * i, 0))
    sheet.save(out / "sheet.jpg", quality=85)
    print(f"{len(files)} cards -> {out} (check {out / 'sheet.jpg'})")
    return files


if __name__ == "__main__":
    build(sys.argv[1])
