import sys
sys.path.insert(0, "/home/user/vice-replay-studio")
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from studio import brand
from studio.ig_cards import boxed_title, ARROW_FONT
W, H = 1080, 1350
OUT = "/home/user/vice-replay-studio/output/ig-images/gta6-cheat-sheet/"
ROWS = [("$250,000 CASH", "Finish the main story", "↑ → ↓ ← ↑ ← ↓ →"),
        ("BODY ARMOR", "Complete 100 workouts", "↓ ↑ ← ↑ ↑ ↑ ↑ ↑ ↓ ↓"),
        ("INFINITE AMMO", "25 silver shooting range medals", "↓ ↑ → ↓ ← ← ↑ ↓ ↓ ↓"),
        ("NO RELOAD", "25 gold shooting range medals", "↓ ↑ → ↓ ← ← ↑ ↓ ↓ ↑"),
        ("MAX AMMO", "Bronze shooting range medals", "↓ ↑ → ↓ ← ← ↑ ↑ ↓ ←"),
        ("BOOMAZOOM CAR", "5 shopping challenges", "← ↑ → ↓ ← ← ↑ ←"),
        ("WANTED LEVEL UP", "Lose or escape 3 stars, 25 times", "← ↓ → ↓ ↑ ↓ ↑")]
im = ImageOps.fit(Image.open(OUT + "bg-ai.jpg").convert("RGB"), (W, H), Image.LANCZOS).convert("RGBA")
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
top, row_h = 372, 92
bottom = top + 70 + row_h * len(ROWS) + 10
od.rounded_rectangle([36, top, W - 36, bottom], 34, fill=(13, 7, 23, 215), outline=(0, 229, 210, 255), width=3)
im = Image.alpha_composite(im, ov)
wm = brand.wordmark(46); im.paste(wm, (48, 44), wm)
d = ImageDraw.Draw(im)
y = boxed_title(d, "GTA 6 CHEAT CODES", 130, 112)
f = brand.font(brand.BODY_FONT, 32)
sub = "PS5 + Xbox  ·  verified  ·  save this"
d.text(((W - f.getlength(sub)) / 2 if False else 60, y + 16), sub, font=f, fill=brand.CYAN)
f = brand.font(brand.BODY_FONT, 25)
how = "Finish the story, open the phone, hold L1 + R1 (LB + RB), enter:"
d.text(((W - f.getlength(how)) / 2, top + 24), how, font=f, fill=brand.WHITE)
fn, fu = brand.font(brand.HEADLINE_FONT, 44), brand.font(brand.BODY_FONT, 22)
fa = ImageFont.truetype(ARROW_FONT, 40)
cell = max(fa.getlength(c) for c in "←↑→↓") + 9
for i, (name, unlock, code) in enumerate(ROWS):
    ry = top + 70 + i * row_h
    if i:
        d.line([66, ry, W - 66, ry], fill=(58, 35, 87), width=2)
    d.text((66, ry + 8), name, font=fn, fill=brand.WHITE)
    d.text((66, ry + 60), unlock, font=fu, fill=(183, 169, 207))
    keys = code.split(); x0 = W - 66 - cell * 10
    for k, c in enumerate(keys):
        d.text((x0 + cell * k + (cell - fa.getlength(c)) / 2, ry + 22), c, font=fa, fill=brand.CYAN)
f = brand.font(brand.HEADLINE_FONT, 40)
warn = "CHEATS TURN OFF SAVING + TROPHIES. SAVE FIRST!"
wx = (W - f.getlength(warn)) / 2
d.rounded_rectangle([wx - 24, bottom + 22, wx + f.getlength(warn) + 24, bottom + 86], 30, fill=brand.PINK)
d.text((wx, bottom + 26), warn, font=f, fill=brand.WHITE)
f = brand.font(brand.BODY_FONT, 30)
foot = "Full list: vicereplay.com"
tw = f.getlength(foot)
d.rounded_rectangle([(W - tw) / 2 - 20, H - 78, (W + tw) / 2 + 20, H - 30], 24, fill=(13, 7, 23, 230))
d.text(((W - tw) / 2, H - 74), foot, font=f, fill=brand.CYAN)
im.convert("RGB").save(OUT + "gta6-cheat-sheet.jpg", quality=93)
print("bottom of panel", bottom)
