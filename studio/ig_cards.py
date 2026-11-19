"""Instagram carousel cards (free, no AI images): our brand look on official screenshots, 1080x1350 JPEGs.

    python -m studio.ig_cards content/carousels/<slug>.json      # -> output/carousels/<slug>/01.jpg ...

Spec (JSON): {"slug", "caption", "first_comment", "cover": {"title", "subtitle", "bg"},
              "tips": [{"title", "text", "bg"}...], "cta": {"title", "text", "bg"}}
bg = a file name in media/official/ (only official screenshots; keep the excluded shots in owner.md out).
Only facts we already checked (episodes / site guides); label reports as reports.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from . import brand

ROOT = Path(__file__).resolve().parent.parent
W, H = 1080, 1350


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
    lines, cur = [], ""
    for wd in text.split():
        t = (cur + " " + wd).strip()
        if fnt.getlength(t) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    return lines + [cur]


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
            f = brand.font(brand.HEADLINE_FONT, 150)
            d.ellipse([60, 520, 260, 720], fill=brand.PINK)
            d.text((160 - f.getlength(n) / 2, 527), n, font=f, fill=brand.WHITE)
            y = boxed_title(d, p["title"], 770, 96, brand.NIGHT)
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
