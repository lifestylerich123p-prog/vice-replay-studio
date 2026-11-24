# Builds the guide pages, /links/, sitemap.xml and robots.txt for vicereplay.com (repo vicereplay-site).
# Add a guide() call per new video, run: python tools/site_guides.py, then commit+push vicereplay-site.
import os, html, json
SITE = os.environ.get("VICEREPLAY_SITE") or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "vicereplay-site")
DOMAIN = "https://vicereplay.com"
TAG = "vicereplay-20"
YT = "https://www.youtube.com/@vicereplaytv-q8s"
YT_ES = "https://www.youtube.com/@vicereplayes"  # Vice Replay en Español (UCWPnqYqYu9_CLsJ8Bk1MPgQ)
import re as _re
# Deals shown as direct Amazon buttons on the links page (bio link) and the homepage. Update prices here when they
# change (checked Nov 24, 2026: Kotaku/Gamerant DualSense $54; 9to5Toys Pulse Elite ~$110; Sony sale Nov 16-30).
DEALS_CHECKED = "Nov 24"
DEALS = [("🛍️ Amazon's full Black Friday sale", "TVs, consoles, everything on sale through Nov 30", "https://www.amazon.com/deals"),
         ("🎮 PS5 DualSense controller: $54.99", "usually $74 · the best GTA 6 deal this week", "PS5 DualSense wireless controller"),
         ("🎧 PlayStation Pulse Elite headset: ~$110", "usually $150", "PlayStation Pulse Elite wireless headset"),
         ("💾 2 TB PS5 SSD with heatsink", "GTA 6 is 212 GB: the upgrade that fits", "PS5 compatible 2TB NVMe SSD with heatsink"),
         ("🌴 GTA 6 for PS5", "full price at US stores right now", "https://www.amazon.com/dp/B0H6K928WL"),
         ("📦 Free 30-day Amazon Prime trial", "fast delivery on all of the above", "https://www.amazon.com/tryprimefree")]


def deals_html(heading="🔥 Black Friday deals on Amazon"):
    items = "".join(f'<a class="item" href="{amz(q)}" target="_blank" rel="sponsored noopener">{html.escape(t)}<small>{html.escape(sub)}</small><span aria-hidden="true">→</span></a>' for t, sub, q in DEALS)
    return (f'<div class="box"><h3>{heading}</h3><div class="btns">{items}</div><p class="sources" style="margin:10px 0 0">'
            f'Prices checked {DEALS_CHECKED} and they change fast. Affiliate links: as an Amazon Associate we earn from qualifying '
            f'purchases, at no extra cost to you. <a href="/guides/gta-6-black-friday/">All GTA 6 Black Friday deals</a></p></div>')


def tag_amazon(doc):
    """Safety net: every amazon.com link on every page carries our Associates tag (Prime trial links too: they pay a bounty)."""
    def fix(m):
        u = m.group(1)
        return m.group(0) if "tag=" in u else f'href="{u}{"&" if "?" in u else "?"}tag={TAG}"'
    return _re.sub(r'href="(https://www\.amazon\.com/[^"]*)"', fix, doc)


def amz(q): return f"{q}?tag={TAG}" if q.startswith("http") else f"https://www.amazon.com/s?k={q.replace(' ','+')}&tag={TAG}"

CSS = """:root{--bg:#0d0717;--panel:#170d26;--panel-2:#21123a;--line:#3a2357;--fg:#f4eefc;--muted:#b7a9cf;--pink:#ff1f8e;--cyan:#00e5d2;
--display:"Anton","Impact","Arial Narrow",sans-serif;--body:"Montserrat",system-ui,-apple-system,"Segoe UI",sans-serif;color-scheme:dark}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--body);font-size:17px;line-height:1.65}
.wrap{max-width:720px;margin:0 auto;padding:22px max(16px,env(safe-area-inset-right,0px)) 64px max(16px,env(safe-area-inset-left,0px))}
nav{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:28px;flex-wrap:wrap}
.brand{font-family:var(--display);font-size:24px;letter-spacing:.02em;color:var(--fg);text-decoration:none}.brand b{color:var(--cyan);font-weight:400}
nav .menu{display:flex;gap:16px;font-weight:700;font-size:14px}nav .menu a{color:var(--muted);text-decoration:none}nav .menu a:hover{color:var(--pink)}
h1{font-family:var(--display);font-weight:400;font-size:clamp(32px,8vw,50px);line-height:1.15;margin:0 0 12px;text-wrap:balance}
h1 span{background:var(--pink);padding:0 .15em;-webkit-box-decoration-break:clone;box-decoration-break:clone}
h2{font-family:var(--display);font-weight:400;font-size:28px;line-height:1.15;margin:36px 0 8px;color:var(--fg)}
h2::before{content:"";display:inline-block;width:10px;height:22px;background:var(--cyan);margin-right:10px;vertical-align:-2px}
.meta{color:var(--muted);font-size:14px;margin:0 0 20px}.lede{font-size:19px;color:var(--fg)}
a{color:var(--cyan)}p{margin:0 0 14px}ul.list{padding-left:22px}ul.list li{margin-bottom:8px}
.video{position:relative;aspect-ratio:16/9;border-radius:14px;overflow:hidden;border:1px solid var(--line);margin:20px 0;background:#000}
.video iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.box{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px;margin:24px 0}
.box h3{margin:0 0 10px;font-size:14px;text-transform:uppercase;letter-spacing:.1em;color:var(--cyan)}
.note{border-left:4px solid var(--pink);background:var(--panel);padding:12px 16px;border-radius:0 10px 10px 0;margin:20px 0}
.btns{display:grid;gap:8px}.item{display:grid;grid-template-columns:1fr auto;align-items:center;column-gap:12px;gap:12px;padding:14px 16px;border-radius:10px;background:var(--panel-2);color:var(--fg);text-decoration:none;font-weight:700;line-height:1.3}
.item span{color:var(--pink);font-size:20px;grid-column:2;grid-row:1/3}.item small{grid-column:1;grid-row:2;color:var(--muted);font-weight:500;font-size:13px}
.item:hover,.item:focus-visible{outline:2px solid var(--pink);outline-offset:2px}
.cards{display:grid;gap:12px}.card{display:block;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px 18px;color:var(--fg);text-decoration:none}
.card:hover{border-color:var(--pink)}.card b{font-size:18px;display:block;line-height:1.3}.card small{color:var(--muted)}
.sources{font-size:14px;color:var(--muted)}.sources a{word-break:break-word}
footer{margin-top:44px;color:var(--muted);font-size:13px;border-top:1px solid var(--line);padding-top:16px}
.banner{position:relative;display:flex;align-items:flex-end;aspect-ratio:16/9;border-radius:16px;overflow:hidden;border:1px solid var(--line);margin:0 0 16px;background:var(--panel)}
.banner img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:right center}
.banner::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(13,7,23,.88) 0%,rgba(13,7,23,.5) 42%,rgba(13,7,23,0) 72%)}
.banner h1{position:relative;z-index:1;margin:0;padding:18px 20px;max-width:68%}
.related{margin-top:34px}
.watch{display:flex;flex-direction:column;background:var(--pink);color:#fff;text-decoration:none;font-weight:800;font-size:17px;border-radius:12px;padding:12px 16px;margin:0 0 22px}
.watch small{font-weight:500;font-size:13px;opacity:.9}
table{width:100%;border-collapse:collapse;margin:10px 0 16px;font-size:16px}
th,td{text-align:left;padding:10px 8px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--cyan);font-size:12px;letter-spacing:.08em;text-transform:uppercase}
tr:nth-child(even) td{background:rgba(255,255,255,.035)}
.toc{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:14px 16px;margin:0 0 22px;display:grid;gap:2px}
.toc b{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--cyan);margin-bottom:4px}
.toc a{color:var(--fg);text-decoration:none;padding:7px 0;border-bottom:1px solid var(--line);font-weight:700;font-size:15px}
.toc a:last-child{border-bottom:0}
h2[id]{scroll-margin-top:16px}
.search{display:flex;align-items:center;gap:10px;margin:0 0 16px}
.search input{flex:1;font:inherit;font-size:16px;padding:13px 16px;border-radius:12px;border:1px solid var(--line);background:var(--panel);color:var(--fg)}
.search input:focus{outline:2px solid var(--pink);border-color:transparent}
.search span{color:var(--muted);font-size:13px;white-space:nowrap}
footer a{display:inline-block;padding:6px 0}
.lead{display:block;width:100%;height:auto;aspect-ratio:40/21;border-radius:14px;margin:4px 0 18px;border:1px solid var(--line);background:var(--panel-2)}
.card.pic{display:grid;grid-template-columns:128px 1fr;gap:14px;align-items:start;padding:12px}@media(max-width:639px){.card.pic{grid-template-columns:1fr;gap:10px}.card.pic b{font-size:18px}}
.card.pic img{display:block;width:100%;height:auto;aspect-ratio:40/21;border-radius:8px;background:var(--panel-2)}
.card.pic b{font-size:16px}.card.pic small{display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;margin-top:4px}
@media(min-width:600px){.banner{aspect-ratio:21/9}.card.pic{grid-template-columns:200px 1fr;gap:16px}.card.pic b{font-size:18px}}"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
STUDIO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_H = os.path.join(STUDIO, "assets/fonts/Anton.ttf"); FONT_B = os.path.join(STUDIO, "assets/fonts/Montserrat.ttf")
OFFICIAL = os.path.join(STUDIO, "media/official")
# English page path -> Spanish page path (hreflang pairs)
ALT = {"guides/gta-6-cheats/": "es/guias/trucos-gta-6/", "guides/gta-6-storage/": "es/guias/espacio-gta-6/",
       "guides/gta-6-unlock-time/": "es/guias/hora-de-lanzamiento-gta-6/", "guides/gta-6-pc-release-date/": "es/guias/gta-6-pc/",
       "guides/gta-6-launch-live/": "es/guias/gta-6-lanzamiento-en-vivo/", "guides/": "es/"}
ALT.update({v: k for k, v in list(ALT.items())})

def card(name, line1, line2, shot=None):
    """1200x630 share image (og:image) in the channel style. Returns its URL."""
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), "#0d0717")
    if shot and os.path.exists(os.path.join(OFFICIAL, shot)):
        _hd = os.path.join(STUDIO, "media", "official-hd", shot)  # Nov 24: 4K original when present (studio.officialhd)
        ph = Image.open(_hd if os.path.exists(_hd) else os.path.join(OFFICIAL, shot)).convert("RGB")
        r = max(W / ph.width, H / ph.height); ph = ph.resize((int(ph.width * r) + 1, int(ph.height * r) + 1), Image.LANCZOS)
        ph = ph.crop(((ph.width - W) // 2, (ph.height - H) // 2, (ph.width - W) // 2 + W, (ph.height - H) // 2 + H))
        im.paste(ph)
        shade = Image.new("L", (W, H)); sd = ImageDraw.Draw(shade)
        for x in range(W): sd.line([(x, 0), (x, H)], fill=int(235 - 150 * x / W))
        im = Image.composite(Image.new("RGB", (W, H), "#0d0717"), im, shade)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 10], fill="#ff1f8e"); d.rectangle([0, H - 10, W, H], fill="#00e5d2")
    fb = ImageFont.truetype(FONT_H, 40)
    d.text((60, 48), "VICE", font=fb, fill="#f4eefc"); d.text((60 + d.textlength("VICE ", font=fb), 48), "REPLAY", font=fb, fill="#00e5d2")
    def fit(text, maxw, size):
        while size > 40:
            f = ImageFont.truetype(FONT_H, size)
            if d.textlength(text, font=f) <= maxw: return f
            size -= 4
        return ImageFont.truetype(FONT_H, size)
    f1 = fit(line1, 1080, 120); d.text((60, 200), line1, font=f1, fill="#ffffff")
    y2 = 200 + f1.size + 48
    f2 = fit(line2, 1040, 104); w2 = d.textlength(line2, font=f2)
    d.rectangle([48, y2 - 6, 60 + w2 + 18, y2 + f2.size + 22], fill="#ff1f8e"); d.text((60, y2), line2, font=f2, fill="#ffffff")
    d.text((60, H - 70), "vicereplay.com", font=ImageFont.truetype(FONT_B, 28), fill="#b7a9cf")
    os.makedirs(os.path.join(SITE, "og"), exist_ok=True)
    im.save(os.path.join(SITE, "og", name + ".jpg"), quality=85)
    os.makedirs(os.path.join(SITE, "og", "t"), exist_ok=True)  # small copy for the picture cards on the guide lists
    im.resize((960, 504), Image.LANCZOS).save(os.path.join(SITE, "og", "t", name + ".webp"), quality=74, method=6)  # 2x for phone screens (Nov 24)
    return f"{DOMAIN}/og/{name}.jpg"

AI_BG = os.path.join(STUDIO, "assets/ai-backgrounds")  # AI illustrations, cleared for vicereplay.com (rights: ai-backgrounds)
def banner_img(name):
    """assets/ai-backgrounds/<name>.jpg -> /img/<name>-720.webp + -1440.webp. Returns the <img> tag."""
    os.makedirs(os.path.join(SITE, "img"), exist_ok=True)
    src = Image.open(os.path.join(AI_BG, name + ".jpg")).convert("RGB")
    for w in (720, 1440):
        out = os.path.join(SITE, "img", f"{name}-{w}.webp")
        if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(os.path.join(AI_BG, name + ".jpg")):
            src.resize((w, round(w * src.height / src.width)), Image.LANCZOS).save(out, quality=80, method=6)
    return (f'<img src="/img/{name}-720.webp" srcset="/img/{name}-720.webp 720w, /img/{name}-1440.webp 1440w" '
            f'sizes="(min-width: 760px) 720px, 100vw" width="1440" height="810" alt="" fetchpriority="high">')

def banner(h1_html, name):
    """Page header: the h1 over a neon illustration (dark left side, art on the right)."""
    return f'<div class="banner">{banner_img(name)}<h1>{h1_html}</h1></div>'

def hero_media():
    """Homepage hero: assets/intro/sting.mp4 -> /img/hero.mp4 (silent, 960x540) + /img/hero-poster.webp (first frame)."""
    import shutil, subprocess
    sting = os.path.join(STUDIO, "assets/intro/sting.mp4"); os.makedirs(os.path.join(SITE, "img"), exist_ok=True)
    mp4, poster = os.path.join(SITE, "img", "hero.mp4"), os.path.join(SITE, "img", "hero-poster.webp")
    if not os.path.exists(sting) or not shutil.which("ffmpeg"): return
    if os.path.exists(mp4) and os.path.getmtime(mp4) >= os.path.getmtime(sting): return
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", sting, "-an", "-vf", "scale=960:540", "-c:v", "libx264", "-crf", "27",
                    "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", mp4], check=True)
    tmp = os.path.join(SITE, "img", "_poster.png")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", sting, "-frames:v", "1", "-vf", "scale=1280:720", tmp], check=True)
    Image.open(tmp).convert("RGB").save(poster, quality=80, method=6); os.remove(tmp)
hero_media()
banner_img("deals-gear")  # used by the hand-written gear/ page

def page(path, title, desc, body, image=None, jsonld=None, lang="en"):
    body = __import__("re").sub(r"<h1>(.*?)</h1>", lambda m: "<h1>" + m.group(1).replace("GTA 6", "GTA&nbsp;6") + "</h1>", body, flags=16)  # never split "GTA 6" (16 = re.S)
    url = f"{DOMAIN}/{path}" if path else DOMAIN + "/"
    image = image or f"{DOMAIN}/og/default.jpg"
    alt = ""
    if path in ALT:
        en, es = (path, ALT[path]) if lang == "en" else (ALT[path], path)
        alt = f'<link rel="alternate" hreflang="en" href="{DOMAIN}/{en}"><link rel="alternate" hreflang="es" href="{DOMAIN}/{es}"><link rel="alternate" hreflang="x-default" href="{DOMAIN}/{en}">'
    jsonld = list(jsonld or [])
    if path.startswith(("guides/", "es/guias/")) and path not in ("guides/", "es/guias/"):  # breadcrumbs for guide pages
        hub = ("Guías", f"{DOMAIN}/es/") if lang == "es" else ("Guides", f"{DOMAIN}/guides/")
        jsonld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Vice Replay", "item": DOMAIN + "/"},
            {"@type": "ListItem", "position": 2, "name": hub[0], "item": hub[1]},
            {"@type": "ListItem", "position": 3, "name": title, "item": url}]})
    ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in jsonld)
    if lang == "es":
        menu = f'<a href="/es/guias/gta-6-lanzamiento-en-vivo/">Noticias</a><a href="/es/guias/mapa-gta-6/">Mapa</a><a href="/es/">Guías</a><a href="/es/equipo/">Equipo</a><a href="{YT_ES}" target="_blank" rel="noopener">YouTube</a><a href="/{ALT.get(path, "")}">EN</a>'
        foot = 'Negocios y patrocinios: <a href="mailto:contact@vicereplay.com">contact@vicereplay.com</a> · <a href="/es/acerca/">Quiénes somos</a><br>Vice Replay es un canal de fans y no está afiliado con Rockstar Games ni con Take-Two Interactive. Grand Theft Auto y GTA son marcas de Take-Two Interactive. Como Afiliado de Amazon, gano con las compras que califican: algunos enlaces de este sitio son de afiliado, sin costo extra para ti.'
    else:
        menu = f'<a href="/guides/gta-6-launch-live/">News</a><a href="/guides/gta-6-map-leonida-places/">Map</a><a href="/guides/">Guides</a><a href="/gear/">Gear</a><a href="{YT}" target="_blank" rel="noopener">YouTube</a>' + (f'<a href="/{ALT[path]}" hreflang="es">ES</a>' if path in ALT else "")
        foot = 'Business &amp; sponsors: <a href="mailto:contact@vicereplay.com">contact@vicereplay.com</a> · <a href="/contact/">Work with us</a> · <a href="/about/">About us</a><br>Vice Replay is a fan channel and is not affiliated with Rockstar Games or Take-Two Interactive. Grand Theft Auto and GTA are trademarks of Take-Two Interactive. As an Amazon Associate I earn from qualifying purchases: some links on this site are affiliate links, at no extra cost to you.'
    doc = f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">{alt}
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="{'article' if 'guid' in path else 'website'}"><meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}"><meta property="og:site_name" content="Vice Replay"><meta property="og:image" content="{image}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{html.escape(title)}"><meta name="twitter:description" content="{html.escape(desc)}"><meta name="twitter:image" content="{image}">
<meta name="theme-color" content="#0d0717">
<link rel="icon" href="/favicon.png"><link rel="apple-touch-icon" href="/favicon.png"><link rel="manifest" href="/site.webmanifest"><link rel="alternate" type="application/rss+xml" title="Vice Replay: GTA 6 news and guides" href="/feed.xml">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Montserrat:wght@500;700;800&display=swap">
<style>{CSS}</style>{ld}
</head>
<body>
<div class="wrap">
<nav><a class="brand" href="/">VICE <b>REPLAY</b></a><div class="menu">{menu}</div></nav>
<main>
{body}
</main>
<footer>{foot}</footer>
</div>
<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "4c4c637dcde8478da5fd7073dcde1b11"}}'></script><!-- End Cloudflare Web Analytics -->
</body>
</html>
"""
    d = os.path.join(SITE, path)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w").write(tag_amazon(doc))

def video(vid, title):
    return f'<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/{vid}" title="{html.escape(title)}" loading="lazy" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture; fullscreen" allowfullscreen></iframe></div>'

def gearbox(items, intro="If you're short on space for the 212 GB install, these searches show current options and prices:"):
    items = list(items) + [("Free 30-day Amazon Prime trial: fast delivery", "https://www.amazon.com/tryprimefree")]
    lis = "".join(f'<a class="item" href="{amz(q)}" target="_blank" rel="sponsored noopener">{html.escape(label)}<span aria-hidden="true">→</span></a>' for label, q in items)
    return f'<div class="box"><h3>Gear for GTA 6 (affiliate links)</h3><p>{intro}</p><div class="btns">{lis}</div><p class="sources" style="margin:10px 0 0">Affiliate links: as an Amazon Associate I earn from qualifying purchases, at no extra cost to you. We haven\'t tested these products; check reviews and compatibility before you buy. <a href="/gear/">All gear picks</a></p></div>'

STORAGE = [("PS5 storage upgrade (2TB NVMe SSD with heatsink)", "PS5 compatible 2TB NVMe SSD with heatsink"),
           ("Xbox Series X|S storage expansion card", "Xbox Series X S storage expansion card 2TB")]
GAME = [("GTA 6 for PS5", "https://www.amazon.com/dp/B0H6K928WL"), ("GTA 6 for Xbox Series X|S", "https://www.amazon.com/dp/B0H6K49W6Y")]

GEAR = [("PS5 DualSense controller", "PS5 DualSense controller"), ("Gaming headset (PS5 / Xbox)", "gaming headset PS5 Xbox")]

def sources(lst):
    return '<div class="sources"><h2>Sources</h2><ul class="list">' + "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{html.escape(n)}</a></li>' for n, u in lst) + "</ul></div>"

def watchmore(vid, lang="en"):
    if lang == "es":
        return f'<div class="box"><h3>Mira más</h3><div class="btns"><a class="item" href="https://www.youtube.com/watch?v={vid}" target="_blank" rel="noopener">Míralo en YouTube<span aria-hidden="true">→</span></a><a class="item" href="{YT_ES}?sub_confirmation=1" target="_blank" rel="noopener">Suscríbete a Vice Replay en Español<small>Noticias y Shorts de GTA 6 en español</small><span aria-hidden="true">→</span></a></div></div>'
    return f'<div class="box"><h3>Watch more</h3><div class="btns"><a class="item" href="https://www.youtube.com/watch?v={vid}" target="_blank" rel="noopener">Watch this on YouTube<span aria-hidden="true">→</span></a><a class="item" href="{YT}?sub_confirmation=1" target="_blank" rel="noopener">Subscribe to Vice Replay<small>New GTA 6 news and Shorts every day</small><span aria-hidden="true">→</span></a></div></div>'

CHEATS = [  # verified: GameSpot, PC Gamer, GamesRadar, Screen Rant, Vice (Nov 19)
 ("$250,000 cash", "250.000 $ en efectivo", "↑ → ↓ ← ↑ ← ↓ →", "Finish the main story", "Termina la historia principal"),
 ("Body armor", "Chaleco antibalas", "↓ ↑ ← ↑ ↑ ↑ ↑ ↑ ↓ ↓", "Complete 100 workouts", "Completa 100 entrenamientos"),
 ("Max ammo", "Munición al máximo", "↓ ↑ → ↓ ← ← ↑ ↑ ↓ ←", "Bronze medals at the shooting range (25; PC Gamer says 20)", "Medallas de bronce en el campo de tiro (25; PC Gamer dice 20)"),
 ("Infinite ammo", "Munición infinita", "↓ ↑ → ↓ ← ← ↑ ↓ ↓ ↓", "25 silver medals at the shooting range", "25 medallas de plata en el campo de tiro"),
 ("No reload", "Sin recargar", "↓ ↑ → ↓ ← ← ↑ ↓ ↓ ↑", "25 gold medals at the shooting range", "25 medallas de oro en el campo de tiro"),
 ("Maibatsu Boomazoom", "Maibatsu Boomazoom", "← ↑ → ↓ ← ← ↑ ←", "Complete 5 shopping challenges", "Completa 5 retos de compras"),
 ("Raise wanted level", "Subir nivel de búsqueda", "← ↓ → ↓ ↑ ↓ ↑", "Lose or escape a 3-star wanted level 25 times", "Pierde o escapa de 3 estrellas 25 veces"),
]
def cheat_table(lang="en"):
    en = lang == "en"
    unlock = "Unlock" if en else "Se desbloquea"
    code = 'style="font-family:system-ui,-apple-system,\'Segoe UI Symbol\',\'Noto Sans Symbols 2\',sans-serif;color:var(--cyan);font-size:24px;letter-spacing:6px;line-height:1.3;margin:4px 0 6px;word-break:break-word"'
    return '<div class="cheats">' + "".join(
        f'<div class="box" style="margin:12px 0"><h3>{html.escape(r[0] if en else r[1])}</h3><p {code}>{r[2].replace(" ", "")}</p>'
        f'<p style="margin:0;color:var(--muted)"><b>{unlock}:</b> {html.escape(r[3] if en else r[4])}</p></div>' for r in CHEATS) + "</div>"

GUIDES = []
CARDS = {}  # slug -> (line1, line2, screenshot in media/official)
def faq_html(faq, lang="en"):
    if not faq: return ""
    return f'<h2>{"Quick answers" if lang == "en" else "Respuestas rápidas"}</h2>' + "".join(f'<div class="box"><h3>{html.escape(q)}</h3><p style="margin:0">{html.escape(a)}</p></div>' for q, a in faq)

# Dated update notes on guides written before launch (Nov 24, 2026). The old text stays as a record; the note says what
# changed. studio/site_stale.py skips pages that carry one.
NOTICES = {
 "gta-6-unlock-time": 'GTA 6 is out: it unlocked on November 19, 2026. This page explains how the staggered launch worked. What\'s new now: <a href="/guides/gta-6-launch-live/">live updates</a>.',
 "gta-6-new-zealand-trick": 'GTA 6 has been out everywhere since November 19, so there\'s no reason to change your region now. What\'s new: <a href="/guides/gta-6-launch-live/">live updates</a>.',
 "gta-6-launch-checklist": 'Launch week is over. Still useful: storage, settings and the day-one update. The latest patch is 1.002.002: <a href="/guides/gta-6-patch-notes/">patch notes</a>.',
 "gta-6-launch-day-survival-guide": 'Launch day is over. Having problems now? The latest patch, 1.002.002, fixed crashes, autosaves and missing phone calls: <a href="/guides/gta-6-patch-notes/">patch notes</a>.',
 "gta-6-launch-streams": 'Launch night is over. Who won it: <a href="/guides/gta-6-streaming-records/">GTA 6 streaming records</a>.',
 "gta-6-game-awards-nominations": 'The show is Thursday, December 10, at 7:30 PM Eastern. Our full preview: <a href="/guides/gta-6-game-awards/">GTA 6 at The Game Awards 2026</a>.',
 "gta-6-reviews": 'Metacritic still shows 99 for the PS5 version, now from 158 critic reviews.',
 "hora-de-lanzamiento-gta-6": 'GTA 6 ya salió: se desbloqueó el 19 de noviembre de 2026. Esta página explica cómo funcionó el lanzamiento. Lo nuevo: <a href="/es/guias/gta-6-lanzamiento-en-vivo/">noticias en vivo</a>.',
 "guia-lanzamiento-gta-6": 'La semana de lanzamiento terminó. ¿Problemas ahora? El parche 1.002.002 arregló cierres, autoguardado y llamadas que no llegaban: <a href="/es/guias/gta-6-notas-del-parche/">notas del parche</a>.',
}
NOTICE_DATE = {"en": "Update, Nov 24", "es": "Actualización, 24 nov"}


def with_lead(body, img, title):
    """Nov 24 upgrade: the guide's 1200x630 card as a big header image (looks like a magazine page; Google Discover
    favours pages with a large image). Goes right before the lede, so after the h1, meta line and any update note."""
    tag = (f'<img class="lead" src="{img}" width="1200" height="630" alt="{html.escape(title)}" '
           'fetchpriority="high" decoding="async">')
    k = body.find('<p class="lede">')
    if k >= 0:  # owner Nov 24 ("think like a visitor"): the answer first, the picture right after it
        k = body.find("</p>", k) + 4
    else:
        k = body.find("</h1>")
        k = body.find("</p>", body.find('<p class="meta">', k)) + 4 if '<p class="meta">' in body[k:] else k + 5
    return body[:k] + "\n" + tag + body[k:]


# Visitor-first (owner Nov 24, "do what you think best"): news pages don't push gear. On these the big Amazon box
# becomes one quiet line; buyer pages (storage, SSD, deals, gifts, PS5 Pro, physical edition...) keep the full box.
NEWS_SLUGS = {"gta-6-launch-live", "gta-6-hacker-sentence", "gta-6-online", "gta-6-streaming-records", "gta-6-game-awards",
              "gta-6-game-awards-nominations", "gta-6-patch-notes", "gta-6-launch-week-numbers", "gta-6-reviews", "gta-6-darts",
              "gta-6-characters", "gta-6-radio-stations", "gta-6-easter-eggs", "gta-6-trophies", "gta-6-launch-streams",
              "gta-6-lanzamiento-en-vivo", "gta-6-online-cuando-sale", "gta-6-records-streaming", "gta-6-premios-game-awards",
              "gta-6-notas-del-parche", "gta-6-cifras-semana-lanzamiento", "dardos-gta-6"}


def soften_gear(slug, body, lang):
    if slug not in NEWS_SLUGS:
        return body
    line = ('<p class="sources">Short on space or need a controller? <a href="/es/equipo/">Nuestro equipo para GTA 6</a> (enlaces de afiliado).</p>'
            if lang == "es" else '<p class="sources">Short on space or need a controller? <a href="/gear/">Our GTA 6 gear picks</a> (affiliate links).</p>')
    return _re.sub(r'<div class="box"><h3>Gear for GTA 6 \(affiliate links\)</h3>.*?All gear picks</a></p></div>', line, body, count=1, flags=_re.S)


def load_watch(lang="en"):
    """{guide slug: (YouTube id, kind)} for guides with a matching upload that is PUBLIC now (its slot has passed, not
    hidden). Episodes name their guide with `guide`, or match it by name (gta6-x -> gta-6-x), like the uploader does.
    Shorts win over long videos; newest first. No API call: registry + approved_queue slots.
    lang="es": Vice Replay en Español uploads (uploads-es.json, queue "es" slots); with_watch maps a Spanish guide to
    them through its English pair (ALT) or its own slug (a Spanish-only episode can name its es guide directly)."""
    import datetime as _dt, glob as _glob
    from zoneinfo import ZoneInfo
    et = ZoneInfo("America/New_York"); now = _dt.datetime.now(et)
    try:
        reg = json.load(open(os.path.join(STUDIO, "content/learn/uploads-es.json" if lang == "es" else "content/learn/uploads.json")))
        queue = json.load(open(os.path.join(STUDIO, "content/learn/approved_queue.json")))["items"]
    except (OSError, ValueError, KeyError):
        return {}
    slot = {(i["slug"], i.get("item", "short")): i.get(lang) for i in queue}
    have = {os.path.basename(d.rstrip("/")) for d in _glob.glob(os.path.join(SITE, "guides", "*/"))}
    have |= {g[0] for g in GUIDES}
    guide_of = {}
    for f in _glob.glob(os.path.join(STUDIO, "episodes", "*.json")):
        try:
            e = json.load(open(f))
        except ValueError:
            continue
        slug = e.get("slug") or os.path.basename(f)[:-5]
        g = e.get("guide") or slug.replace("gta6-", "gta-6-", 1)
        if g in have or e.get("guide"):
            guide_of[slug] = g
    best = {}
    for vid, r in reg.items():
        g = guide_of.get(r.get("slug"))
        if not g or r.get("hidden"):
            continue
        s_ = slot.get((r["slug"], r.get("item", "short")))
        if s_ and _dt.datetime.strptime(f"{s_[0]} {s_[1]}", "%Y-%m-%d %I:%M %p").replace(tzinfo=et) > now:
            continue  # still private until its slot
        kind = "main" if r.get("item") == "main" else "short"
        rank = (kind == "short", r.get("uploaded") or "")
        if g not in best or rank > best[g][2]:
            best[g] = (vid, kind, rank)
    return {g: (v, k) for g, (v, k, _r) in best.items()}  # es: keyed by the episode's (usually English) guide slug


_WATCH = None
_WATCH_ES = None


def with_watch(slug, body, lang):
    """A 'watch it' button right under the answer/picture/jump list when a public video matches the guide."""
    global _WATCH, _WATCH_ES
    if 'class="video"' in body:
        return body
    if lang == "es":
        if _WATCH_ES is None:
            _WATCH_ES = load_watch("es")
        en = ALT.get(f"es/guias/{slug}/", "")  # its English pair, looked up now (ALT fills in as pages are built)
        en = en.split("/")[1] if en.startswith("guides/") else None
        watch = {slug: _WATCH_ES[k] for k in (slug, en) if k in _WATCH_ES}
    else:
        if _WATCH is None:
            _WATCH = load_watch()
        watch = _WATCH
    if slug not in watch:
        return body
    vid, kind = watch[slug]
    url = f"https://www.youtube.com/shorts/{vid}" if kind == "short" else f"https://www.youtube.com/watch?v={vid}"
    if lang == "es":
        label = "▶ Míralo en 30 segundos" if kind == "short" else "▶ Mira el video"
        btn = f'<a class="watch" href="{url}" target="_blank" rel="noopener">{label}<small>en Vice Replay en Español</small></a>'
    else:
        label = "▶ Watch it in 30 seconds" if kind == "short" else "▶ Watch the video"
        btn = f'<a class="watch" href="{url}" target="_blank" rel="noopener">{label}<small>on our YouTube channel</small></a>'
    for anchor in ('</nav>', '<img class="lead"'):
        k = body.find(anchor)
        if k >= 0:
            k = body.find(">", k) + 1
            return body[:k] + "\n" + btn + body[k:]
    k = body.find("</p>", body.find('<p class="lede">')) + 4
    return body[:k] + "\n" + btn + body[k:]


def with_toc(body, lang):
    """Guides with 4+ sections get an 'On this page' jump list under the picture, and each h2 gets an id (Nov 24:
    a phone reader with a specific question shouldn't scroll 7-9 screens)."""
    heads = _re.findall(r"<h2>(.*?)</h2>", body)
    if len(heads) < 4:
        return body
    def anchor(h):
        return _re.sub(r"[^a-z0-9áéíóúñ]+", "-", _re.sub(r"<[^>]+>", "", h).lower()).strip("-")[:60]
    for h in heads:
        body = body.replace(f"<h2>{h}</h2>", f'<h2 id="{anchor(h)}">{h}</h2>', 1)
    label = "En esta página" if lang == "es" else "On this page"
    links = "".join(f'<a href="#{anchor(h)}">{_re.sub(r"<[^>]+>", "", h)}</a>' for h in heads)
    toc = f'<nav class="toc" aria-label="{label}"><b>{label}</b>{links}</nav>'
    k = body.find('<img class="lead"')
    k = body.find(">", k) + 1 if k >= 0 else body.find("</p>", body.find('<p class="lede">')) + 4
    return body[:k] + "\n" + toc + body[k:]


def with_notice(slug, body, lang):
    """Put the dated update note right under the page's meta line (or its h1)."""
    if slug not in NOTICES:
        return body
    box = f'<div class="note update"><b>{NOTICE_DATE[lang]}:</b> {NOTICES[slug]}</div>'
    for anchor in ('<p class="meta">', '</h1>'):
        k = body.find(anchor)
        if k >= 0:
            end = body.find("</p>", k) + 4 if anchor.startswith("<p") else k + len(anchor)
            return body[:end] + "\n" + box + body[end:]
    return box + body

def guide(slug, title, desc, date, body, faq=None, lang="en", modified=None):
    faq = faq or FAQS.get(slug)
    body = with_notice(slug, body, lang)
    path = f"guides/{slug}/" if lang == "en" else f"es/guias/{slug}/"
    l1, l2, shot = CARDS.get(slug, (title.split(":")[0][:28], "", None))
    img = card(slug, l1, l2 or "On replay", shot)
    body = with_lead(body, img, title)
    body = with_toc(body, lang)
    body = with_watch(slug, body, lang)
    body = soften_gear(slug, body, lang)
    if lang == "es" and YT_ES not in body:  # every Spanish guide points Spanish readers to the Spanish channel
        body += f'<div class="box"><h3>GTA 6 en español, cada día</h3><div class="btns"><a class="item" href="{YT_ES}?sub_confirmation=1" target="_blank" rel="noopener">Suscríbete a Vice Replay en Español<small>Shorts y noticias de GTA 6 en español</small><span aria-hidden="true">→</span></a></div></div>'
    if lang == "en": GUIDES.append((slug, title, desc, date))
    else: GUIDES_ES.append((slug, title, desc, date))
    ld = [{"@context": "https://schema.org", "@type": "Article", "headline": title[:110], "description": desc, "image": [img],
           "datePublished": date, "dateModified": modified or date, "inLanguage": lang,
           "author": {"@type": "Organization", "name": "Vice Replay", "url": YT},
           "publisher": {"@type": "Organization", "name": "Vice Replay", "url": DOMAIN + "/", "logo": {"@type": "ImageObject", "url": DOMAIN + "/favicon.png"}},
           "mainEntityOfPage": f"{DOMAIN}/{path}"}]
    if faq:
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})
    marker = '<div class="sources">'
    body = body.replace(marker, faq_html(faq, lang) + marker, 1) if marker in body else body + faq_html(faq, lang)
    page(path, f"{title} · Vice Replay", desc, body, image=img, jsonld=ld, lang=lang)
GUIDES_ES = []

CARDS.update({
 "gta-6-unlock-time": ("GTA 6 UNLOCK TIME", "WHOSE MIDNIGHT?", "vice-city-05.jpg"),
 "gta-6-new-zealand-trick": ("THE NEW ZEALAND TRICK", "WORTH THE RISK?", "leonida-keys-03.jpg"),
 "gta-6-launch-checklist": ("GTA 6 LAUNCH", "CHECKLIST", "jason-and-lucia-05.jpg"),
 "gta-6-map-leonida-places": ("BIGGER THAN", "VICE CITY", "leonida-map-poster.jpg"),
 "gta-6-storage": ("GTA 6 STORAGE FULL?", "FREE FIXES FIRST", "car-vapid-stanier-01.jpg"),
 "gta-6-cheats": ("GTA 6 CHEAT CODES", "$250K + 6 MORE", "car-grotti-cheetah-01.jpg"),
 "gta-6-pc-release-date": ("GTA 6 ON PC", "WHEN?", "port-gellhorn-02.jpg"),
 "gta-6-launch-streams": ("LAUNCH NIGHT", "WHERE TO WATCH", "vice-city-13.jpg"),
 "gta-6-reviews": ("GTA 6 REVIEWS", "99 ON METACRITIC", "jason-and-lucia-03.jpg"),
 "gta-6-game-awards-nominations": ("GAME OF THE YEAR", "8 NOMINATIONS", "lucia-caminos-10.jpg"),
 "gta-6-launch-live": ("GTA 6 NEWS", "LIVE UPDATES", "vice-city-21.jpg"),
 "trucos-gta-6": ("TRUCOS DE GTA 6", "250.000 $ + 6 MÁS", "car-grotti-cheetah-01.jpg"),
 "espacio-gta-6": ("¿SIN ESPACIO?", "GTA 6 PESA 212 GB", "car-vapid-stanier-01.jpg"),
 "hora-de-lanzamiento-gta-6": ("GTA 6: ¿A QUÉ HORA", "SE DESBLOQUEA?", "vice-city-05.jpg"),
 "gta-6-pc": ("GTA 6 EN PC", "¿CUÁNDO?", "port-gellhorn-02.jpg"),
 "gta-6-lanzamiento-en-vivo": ("LANZAMIENTO GTA 6", "EN VIVO", "vice-city-21.jpg"),
})
FAQS = {
 "gta-6-cheats": [("Are there GTA 6 cheat codes?", "Yes. Launch guides from GameSpot, GamesRadar and PC Gamer list them, but they only unlock after you finish the main story. Open the phone, hold L1 + R1 (LB + RB) and enter the code on the D-pad."),
                  ("Do GTA 6 cheats disable trophies?", "Yes. While a cheat is on, saving is blocked and Trophies/Achievements are off for the rest of that session. Load a clean save to get them back."),
                  ("Is there a GTA 6 money cheat?", "Yes: up, right, down, left, up, left, down, right gives $250,000 once you finish the story, according to GameSpot, PC Gamer and GamesRadar. Cheats block saving, so the cash doesn't stay in your save. 'Money generator' sites are scams.")],
 "gta-6-storage": [("How much space does GTA 6 need?", "Rockstar says up to 212 GB, depending on your console, plus some temporary space while it installs."),
                   ("Can I play GTA 6 from a USB drive?", "No. On PS5 and Xbox Series X|S, current-gen games have to run from internal storage, a PS5 M.2 SSD or an Xbox storage expansion card. USB drives can only store them.")],
 "gta-6-unlock-time": [("What time does GTA 6 unlock?", "At midnight local time on November 19, 2026, region by region. New Zealand is first, around 6 AM Eastern on November 18, according to PlayStation Store listings."),
                       ("When does GTA 6 start on Xbox Cloud Gaming?", "At 1 AM Eastern on November 19, according to Forbes.")],
 "gta-6-pc-release-date": [("Is GTA 6 on PC?", "Not at launch. GTA 6 launches November 19, 2026 on PS5 and Xbox Series X|S only."),
                           ("When is the GTA 6 PC release date?", "There's no official date. A GamesBeat report says early 2027 (January to March), but Rockstar hasn't confirmed it.")],
  "gta-6-launch-checklist": [("How much is GTA 6?", "$79.99 for the standard edition and $99.99 for the Ultimate edition in the US."),
                            ("Is GTA Online in GTA 6 at launch?", "No. The new GTA Online isn't there on day one; it's expected sometime in 2027.")],
 "gta-6-new-zealand-trick": [("Does the New Zealand trick work for GTA 6?", "It's unconfirmed. Guides describe changing your Xbox region; on PS5 the store region is tied to your account. It can break platform rules, so it's a risk.")],
}

# 1. Unlock time
guide("gta-6-unlock-time", "GTA 6 Unlock Time: When You Can Play in Every Time Zone",
 "GTA 6 unlocks at midnight local time on November 19, 2026. Here's whose midnight comes first, the US question, Xbox Cloud Gaming and the New Zealand trick.",
 "2026-11-17", f"""<h1>GTA 6 unlock time: <span>whose midnight?</span></h1>
<p class="meta">Updated November 17, 2026 · Vice Replay</p>
<p class="lede">GTA 6 comes out on Thursday, November 19, 2026, on PS5 and Xbox Series X and S. It unlocks at <b>midnight local time</b> in each region, so not everyone starts at the same moment.</p>
{video("pcoMWOraJA4","GTA 6 Unlock Time in Every Time Zone")}
<h2>The rule: midnight where you are</h2>
<p>Rockstar's rule is a regional midnight unlock. Players in the furthest-east time zones get in first, and the unlock rolls west around the world over the following hours.</p>
<h2>Who plays first</h2>
<p>New Zealand reaches midnight first. According to PlayStation Store listings, that is around <b>6 AM Eastern on November 18</b>. Australia, Japan and India follow, then Europe and the UK.</p>
<h2>The US: one unlock or four?</h2>
<p>This is still debated. Some reports say US players get one shared unlock the evening of November 18, while others expect each US time zone to unlock at its own midnight. The safest way to know your exact time is your console's store page: open the GTA 6 listing and look for the release time shown there.</p>
<h2>Xbox Cloud Gaming</h2>
<p>According to Forbes, GTA 6 starts streaming on Xbox Cloud Gaming at <b>1 AM Eastern</b>, not midnight.</p>
<h2>The New Zealand trick</h2>
<p>Some players plan to switch their Xbox region to New Zealand to play early. It's unconfirmed for GTA 6 and it carries account risks. <a href="/guides/gta-6-new-zealand-trick/">Read our full breakdown of the New Zealand trick.</a></p>
<div class="note">Times change fast before a launch. Everything here is as reported two days before release; your console's store page has the final word.</div>
{gearbox(STORAGE)}
{watchmore("pcoMWOraJA4")}
{sources([("Rockstar regional release times (as cited by GTA Wiki)","https://grandtheftautowiki.com/articles/gta-6-release-time-unlock"),("Yahoo Tech: US unlock the night before","https://tech.yahoo.com/gaming/articles/gta-6-unlocks-midnight-november-124500352.html"),("Push Square: release times","https://www.pushsquare.com/guides/gta-6-release-times-when-can-you-start-playing"),("Forbes: Xbox Cloud Gaming start time","https://www.forbes.com/sites/brianmazique/2026/11/16/xbox-just-revealed-the-exact-hour-gta-6-starts-streaming-and-it-isnt-midnight/"),("Screen Rant: PS5 region purchases","https://screenrant.com/gta-6-global-launch-times-play-early/")])}""")

# 2. NZ trick
guide("gta-6-new-zealand-trick", "GTA 6 New Zealand Trick: Can You Play Early, and Is It Safe?",
 "How the GTA 6 New Zealand trick reportedly works on Xbox, why PS5 is different, and the account risks before you try it.",
 "2026-11-17", f"""<h1>The GTA 6 New Zealand trick: <span>worth the risk?</span></h1>
<p class="meta">Updated November 17, 2026 · Vice Replay</p>
<p class="lede">Some players say they can play GTA 6 up to eighteen hours early by pretending to be in New Zealand. It's unconfirmed, and it could put your account at risk. Here's what's actually reported.</p>
{video("-C9KX5Afwgw","GTA 6 New Zealand Trick")}
<h2>Why New Zealand?</h2>
<p>GTA 6 unlocks at midnight local time. According to PlayStation Store listings, New Zealand reaches that midnight first, around 6 AM Eastern on November 18. Rockstar hasn't confirmed those times.</p>
<h2>On Xbox</h2>
<p>Guides from outlets like Insider Gaming and Windows Central describe changing your Xbox's location setting to New Zealand, then switching it back later. Nobody has confirmed it works for GTA 6 yet.</p>
<h2>On PS5</h2>
<p>PlayStation is different. Reports say your store region is tied to your account, and Sony's terms reportedly rule out the shortcut. Changing the clock or the console settings won't move your unlock time.</p>
<h2>The risks</h2>
<ul class="list"><li>Fake region details can break platform rules.</li><li>Your account could get flagged.</li><li>You may need to buy the game in the New Zealand store.</li><li>Rockstar and Microsoft haven't commented.</li></ul>
<h2>Our take</h2>
<p>Not worth risking a console account for a few hours. Launch-day servers will be busy anyway. <a href="/guides/gta-6-unlock-time/">Here's when GTA 6 unlocks where you live.</a></p>
{gearbox(STORAGE)}
{watchmore("-C9KX5Afwgw")}
{sources([("Insider Gaming: Xbox NZ trick","https://insider-gaming.com/how-to-play-gta-6-early-xbox-new-zealand-trick/"),("Windows Central","https://www.windowscentral.com/gaming/xbox/grand-theft-auto-6-launch-new-zealand-changing-region"),("BGR","https://www.bgr.com/2259294/xbox-series-x-get-early-access-gta-6/"),("Digital Citizen: Sony terms and PS5","https://www.digitalcitizen.life/gta-6-ps5-new-zealand-unlock-time-psn-region-rules/"),("MP1st: unlock times","https://mp1st.com/news/gta-6-unlock-times-revealed")])}""")

# 3. Launch checklist
guide("gta-6-launch-checklist", "GTA 6 Launch Checklist: Download Size, Price and What's Missing on Day One",
 "GTA 6's install is up to 212 GB. Here's the launch-night checklist: preload, day-one patch, price, what's not there at launch, and how to dodge spoilers.",
 "2026-11-16", f"""<h1>GTA 6 launch checklist: <span>be ready at midnight</span></h1>
<p class="meta">Updated November 16, 2026 · Vice Replay</p>
<p class="lede">GTA 6 launches November 19 on PS5 and Xbox Series X and S. Here's how much space you need, what it costs, what isn't there on day one, and a simple launch-night plan.</p>
{video("vJDnv7_7Hcs","GTA 6 Launches in 3 Days")}
<h2>Download size: up to 212 GB</h2>
<p>The preload went live on November 10. Rockstar says the install is <b>up to 212 GB</b>, depending on your console, and your console may need extra temporary space while it installs. <a href="/guides/gta-6-storage/">How to make room for GTA 6.</a></p>
<h2>Price</h2>
<p>The standard edition is <b>$79.99</b> in the US and the Ultimate edition is <b>$99.99</b>. Physical copies are reportedly a code in a box, so you still need the download.</p>
<h2>Not there on day one</h2>
<ul class="list"><li><b>No PC version</b> at launch, and no PC date announced yet.</li><li><b>No GTA Online</b> for the new game on day one; it's expected sometime in 2027.</li></ul>
<h2>Your launch-night plan</h2>
<ul class="list"><li>Finish the preload early, before launch-night traffic.</li><li>On launch day, update your console and the game before midnight so the day-one patch doesn't eat your first hour.</li><li>Test your controller, headset and TV picture mode (turn on Game Mode).</li><li>Mute GTA 6 keywords on social apps: clips and spoilers will flood every feed within minutes.</li><li>Want to share your best moments? Turn on your console's capture features before you play.</li></ul>
{video("YqnShunG7WY","GTA 6 Survival Guide: 7 Things to Do Before You Play")}
{gearbox(STORAGE + GAME)}
{watchmore("vJDnv7_7Hcs")}
{sources([("Forbes: release time, download size, day-one update","https://www.forbes.com/sites/erikkain/2026/11/16/gta-6-release-date-time-ps5-xbox-series-x-download-size-day-one-update/"),("Gameluster: 212 GB preload","https://gameluster.com/gta-6-212gb-download-size-preload/"),("Rockstar Games: official GTA VI site","https://www.rockstargames.com/VI")])}""")

# 4. Map: since Nov 24 the map hub is site/guides/gta-6-map-leonida-places.json (interactive official HD map, EN) +
# mapa-gta-6.json (ES); its old 6-places text is the 'Places to know' pins in site/map-pins.json.

# 5. Storage evergreen
guide("gta-6-storage", "How Many GB Is GTA 6? 212 GB, and How to Make Room on PS5 and Xbox",
 "GTA 6 needs up to 212 GB. Free ways to clear space on PS5 and Xbox Series X|S first, then what to look for if you need a storage upgrade.",
 "2026-11-18", f"""<h1>GTA 6 storage full? <span>Free fixes first</span></h1>
<p class="meta">Updated November 18, 2026 · Vice Replay</p>
<p class="lede">Rockstar says GTA 6 needs <b>up to 212 GB</b>, plus some temporary space while it installs. On a base console that's a big part of the drive. Try the free fixes first; buy storage only if you still need it.</p>
<h2>Free fix 1: check what's using space</h2>
<p><b>PS5:</b> Settings → Storage → Console Storage → Games and Apps, sorted by size. <b>Xbox:</b> My games &amp; apps → Manage → Storage. Big games you finished are the first to go.</p>
<h2>Free fix 2: delete, don't lose</h2>
<p>Deleting a game doesn't delete your saves on most games with cloud saves, and you can download games you own again later. Check that cloud saves are on (PS Plus cloud storage on PS5; Xbox saves to the cloud automatically) before you delete.</p>
<h2>Free fix 3: clear captures and extras</h2>
<p>Old video clips and screenshots add up fast. So do language packs and optional modes some games let you uninstall separately.</p>
<h2>Free fix 4: park games on a USB drive</h2>
<p>Both consoles can store games on an external USB drive. PS5 and Xbox Series games need to be moved back to fast storage to play, but parking them outside is quicker than downloading again.</p>
<h2>If you still need space: the upgrade</h2>
<p><b>PS5:</b> the console has an expansion slot for an M.2 NVMe SSD (PCIe Gen4). Sony recommends a drive with a heatsink. A 2 TB drive gives you room for GTA 6 and a lot more.</p>
<p><b>Xbox Series X|S:</b> current-gen games have to run from internal storage or an official storage expansion card, which plugs into the back. A regular USB drive can store them, but can't play them.</p>
{gearbox(STORAGE + [("External USB drive (to park games)", "external hard drive for PS5 Xbox 2TB")], "These searches show current options and prices. Check compatibility with your exact console before you buy:")}
<div class="note">More GTA 6 prep: <a href="/guides/gta-6-launch-checklist/">launch checklist</a> · <a href="/guides/gta-6-unlock-time/">unlock times</a></div>
{sources([("Forbes: GTA 6 download size","https://www.forbes.com/sites/erikkain/2026/11/16/gta-6-release-date-time-ps5-xbox-series-x-download-size-day-one-update/"),("PlayStation: how to add M.2 SSD storage to PS5","https://www.playstation.com/en-us/support/hardware/ps5-install-m2-ssd/"),("Xbox: storage options for Xbox Series X|S","https://support.xbox.com/en-US/help/hardware-network/console/xbox-series-x-s-storage-options")])}""")

# 6. Cheats tracker
guide("gta-6-cheats", "GTA 6 Cheat Codes: Money, Armor, Ammo + How to Unlock",
 "Verified GTA 6 cheat codes for PS5 and Xbox: the $250,000 money cheat, body armor, infinite ammo, no reload and more, how to unlock each one, and the catch (no saves, no trophies).",
 "2026-11-19", f"""<h1>GTA 6 cheat codes: <span>the verified list</span></h1>
<p class="meta">Updated November 19, 2026, 4:30 PM ET · Vice Replay · We add codes once two sources agree on them</p>
<p class="lede">Short answer: <b>yes, GTA 6 has cheats</b>, including a <b>$250,000 money cheat</b>. The catch: <b>they only unlock after you finish the main story</b>, most need their own challenge, and using one turns off saving and trophies for that session.</p>
<div class="box"><h3>How GTA 6 cheats work</h3><ul class="list" style="margin:0"><li><b>Finish the story first:</b> cheats unlock after the main story is done (Eurogamer found the cheat menu appears after the credits). PC Gamer says the unlock only counts for that save file.</li><li><b>Earn each one:</b> many cheats also have their own unlock challenge, so knowing a code isn't enough.</li><li><b>No saves, no trophies:</b> while a cheat is on, saving is blocked and Trophies/Achievements are off for the rest of that session. Load a clean save to get them back.</li><li><b>Entering a code:</b> according to Screen Rant, open the phone (D-pad up), then hold L1 + R1 on PS5 (LB + RB on Xbox) and enter the code.</li></ul></div>
<h2>Verified GTA 6 cheat codes (PS5 and Xbox)</h2>
<p>Open the phone (D-pad up), hold <b>L1 + R1</b> (<b>LB + RB</b> on Xbox) and press the arrows on the D-pad. Every code below is listed the same way by at least two of GameSpot, PC Gamer, GamesRadar, Screen Rant and Vice.</p>
{cheat_table("en")}
<h2>Which cheat lists to trust</h2>
<p>Launch-day guides list around 60 cheats, but they don't all agree on every code or unlock. We left out codes where guides disagree (like the weather cheat's unlock) or that only one guide lists. Before launch, most "GTA 6 cheat" lists were GTA 5 codes with a new name, so check the date on any list you use.</p>
<h2>Is there a money cheat?</h2>
<p>Yes: <b>↑ → ↓ ← ↑ ← ↓ →</b> gives <b>$250,000</b> once you finish the story. But cheats block saving, so the cash doesn't stay in your save. GTA 5 never had a money cheat. Any site offering a GTA 6 "money generator" is a scam.</p>
<h2>Trophy hunting? Do this</h2>
<ul class="list"><li>Make a manual save before trying cheats.</li><li>Play with cheats, then quit and reload your clean save to keep earning trophies.</li><li>Cheats are a story-mode feature: GTA 5's never worked online, and GTA Online for GTA 6 isn't expected until 2027.</li></ul>
<h2>Scam alert</h2>
<p>Any site or video asking for your PlayStation or Xbox login, or offering a "money generator" download, is a scam. Never type your password anywhere except the official store or console.</p>
{gearbox(GAME + STORAGE, "Getting GTA 6 or making room for the 212 GB install? These searches show current options and prices:")}
{watchmore("vlPV5Yre8T8")}
{sources([("GameSpot: all GTA 6 cheats and how to unlock them","https://www.gamespot.com/articles/all-gta-6-cheats-and-how-to-unlock-them/"),("Vice: all GTA 6 cheat codes","https://www.vice.com/en/article/gta-6-cheat-codes-list/"),("GamesRadar: all GTA 6 cheats and how to unlock them","https://www.gamesradar.com/games/grand-theft-auto/gta-6-cheats/"),("PC Gamer: all GTA 6 cheats and how to unlock them","https://www.pcgamer.com/games/grand-theft-auto/gta-6-cheats-list/"),("Insider Gaming: all GTA 6 cheats","https://insider-gaming.com/all-gta-6-cheats-best-grand-theft-auto-6-cheat-codes/"),("VGTimes on Eurogamer's testing: cheats locked behind the story","https://vgtimes.com/gaming-news/175043-gta-6-locks-cheats-behind-the-main-story-and-disables-saving.html"),("Screen Rant: GTA 6 cheats for PS5 and Xbox","https://screenrant.com/gta-6-cheats-ps5-xbox/")])}""")

# 7-10. News articles (Nov 17)
guide("gta-6-pc-release-date", "Is GTA 6 on PC? PC Release Date and What's Actually Reported",
 "GTA 6 is out on PS5 and Xbox Series X|S only. Here's what Take-Two has said about PC, the reported early 2027 window, and what's still unconfirmed.",
 "2026-11-17", f"""<h1>GTA 6 on PC: <span>when?</span></h1>
<p class="meta">Updated November 17, 2026 · Vice Replay</p>
<p class="lede">GTA 6 came out on November 19, 2026, on <b>PS5 and Xbox Series X|S only</b>. There is still no official PC release date (checked November 24: Take-Two says PC news will come from Rockstar). Here's what's known and what's only reported.</p>
<h2>What's official</h2>
<p>Take-Two and Rockstar have only announced console versions. Take-Two CEO Strauss Zelnick has defended the console-first plan, saying Rockstar "always starts on console" and serves its core audience first.</p>
<h2>What's reported: early 2027</h2>
<p>According to a GamesBeat report citing four anonymous industry sources, Rockstar is reportedly aiming for a PC release between <b>January and March 2027</b>. Rockstar and Take-Two have not confirmed it. Some outlets also read Take-Two's financial outlook as a hint at early 2027, but that's an interpretation, not an announcement.</p>
<h2>History says: wait</h2>
<p>Rockstar's last big games followed the same pattern. GTA 5 reached PC about a year and a half after its console launch, and Red Dead Redemption 2 about a year after. A wait of a few months would actually be faster than usual.</p>
<h2>What PC players can do now</h2>
<ul class="list"><li>Don't buy "GTA 6 PC" keys or downloads: there's no PC version, so they're scams.</li><li>Watch Rockstar's official channels for the real announcement.</li><li>Playing on console? <a href="/guides/gta-6-storage/">Make room for the 212 GB install.</a></li></ul>
{gearbox(GAME + STORAGE, "Playing on console at launch? These searches show current options and prices:")}
{sources([("GodisaGeek: PC reportedly targets Q1 2027","https://godisageek.com/2026/10/gta-6-pc-release-date-q1-2027"),("Outlook Respawn: PC reportedly early 2027","https://respawn.outlookindia.com/gaming/gaming-news/gta-6-pc-release-reportedly-targets-early-2027"),("tbreak: Take-Two CEO on console-first","https://tbreak.com/gta-6-pc-release-delayed-console-first/"),("Gfinity: GTA 6 platforms explained","https://www.gfinityesports.com/article/will-gta-6-come-to-pc-at-launch-platforms-explained")])}""")

guide("gta-6-launch-streams", "GTA 6 Launch Streams: YouTube's 24-Hour Livestream and Kai Cenat's 100% Marathon",
 "Where to watch GTA 6 on launch night: YouTube's 24-hour livestream with 30+ creators starting November 19, plus Kai Cenat's plan to 100% the game on stream.",
 "2026-11-17", f"""<h1>GTA 6 launch night: <span>where to watch</span></h1>
<p class="meta">Updated November 17, 2026 · Vice Replay</p>
<p class="lede">GTA 6 might be the biggest launch night in streaming history. Here's what's been announced, so you know where to watch if you're not playing yet.</p>
<h2>YouTube's 24-hour GTA 6 livestream</h2>
<p>YouTube is hosting <b>"Launch Day: YouTube's 24 Hour GTAVI Livestream"</b> with more than 30 creators. According to reports, a pre-show hosted by RDCWorld starts at <b>11 PM Eastern on November 18</b>, and the 24-hour main stream begins at <b>midnight Eastern on November 19</b>, with streams in several languages.</p>
<h2>Kai Cenat's 100% marathon</h2>
<p>Kai Cenat has said he wants to complete GTA 6 to 100% on stream: not just the story, but every optional extra. How long that takes depends on how big the game really is, and nobody knows that yet.</p>
<h2>Watching without spoilers</h2>
<p>Streams will show the story live. If you want to go in blind, skip the marathons for the first few days and mute "GTA 6" on social apps. <a href="/guides/gta-6-launch-checklist/">Our launch checklist</a> has more.</p>
<div class="note">Plans can change on launch night. Check each creator's own channel for the final times.</div>
{watchmore("DIFRHVF6T0E")}
{sources([("Notebookcheck: YouTube 24-hour GTA 6 livestream","https://www.notebookcheck.net/YouTube-to-host-24-hour-GTA-6-release-date-livestream-with-launch-day-gameplay.1449040.0.html"),("GTA BOOM: 24-hour livestream with 30+ creators","https://www.gtaboom.com/gta-6-is-getting-a-24-hour-youtube-livestream-with-more-than-30-creators-5ad2"),("Streams Charts: YouTube launch marathon","https://streamscharts.com/news/youtube-announces-24-hour-gta-6-launch-marathon-global-creators"),("Sportskeeda: Kai Cenat 100% marathon","https://sportskeeda.com/us/streamers/news-kai-cenat-hold-gta-6-100-playthrough-marathon-upon-game-s-release"),("GTA BOOM: Kai Cenat wants to 100% GTA 6","https://www.gtaboom.com/kai-cenat-wants-to-100-gta-6-in-one-nonstop-marathon-d0ed")])}""")

guide("gta-6-reviews", "GTA 6 Reviews: 99 on Metacritic, Tied for the Best Score Ever",
 "GTA 6 reviews are in: 99 on Metacritic and OpenCritic, tied with Zelda: Ocarina of Time for the highest score ever, with no mixed or negative reviews. What critics loved and the one common complaint.",
 "2026-11-18", f"""<h1>GTA 6 reviews: <span>99 on Metacritic</span></h1>
<p class="meta">Updated November 18, 2026 · Vice Replay · Scores can still move as more reviews come in</p>
<p class="lede">The reviews are in, and they're historic. GTA 6 debuted with a <b>99 on Metacritic</b>, tying <b>The Legend of Zelda: Ocarina of Time</b> (1998) for the highest score in the site's history.</p>
<div class="box"><h3>The scores (as of November 18)</h3><ul class="list" style="margin:0"><li><b>Metacritic:</b> 99, with no mixed or negative reviews</li><li><b>OpenCritic:</b> 99, with 100% of critics recommending it</li><li><b>Reviews counted:</b> well over 100, about five times as many as Ocarina of Time had</li></ul></div>
<h2>What critics loved</h2>
<p>Reviewers praised the open world of Leonida, the story of Jason and Lucia, and how much there is to do. Several called it Rockstar's best game.</p>
<h2>The one common complaint</h2>
<p>It runs at <b>30 frames per second</b> on consoles, with no 60 fps mode, and some reviewers mention a learning curve on the controls. <a href="/guides/gta-6-best-settings/">Best settings for GTA 6</a>.</p>
<h2>Where it ranks</h2>
<p>Before GTA 6, no game had reached a 99 on Metacritic since 1998. For comparison, GTA 4 has a 98 and GTA 5 a 97.</p>
{video("S5L5Mah6LIU","GTA 6 just got a 99 on Metacritic")}
{gearbox(GAME + STORAGE, "Getting GTA 6 after the reviews? Links go to the exact listings:")}
{sources([("Forbes: Metacritic score ties the all-time record","https://www.forbes.com/sites/paultassi/2026/11/18/the-gta-6-metacritic-review-score-is-in-and-ties-an-all-time-record/"),("GameSpot: a score so high it's only happened once","https://www.gamespot.com/articles/gta-6-has-a-metacritic-score-so-high-its-only-happened-once-before/"),("Kotaku: 99 Metacritic","https://kotaku.com/gta-6-review-scores-99-metacritic-rockstar-grand-theft-auto-vi-2000757999"),("GamesRadar: highest-rated game of all time","https://www.gamesradar.com/games/grand-theft-auto/gta-6-metacritic-score-makes-it-the-highest-rated-game-of-all-time-matching-the-og-zelda-ocarina-of-time/"),("Dot Esports: review roundup","https://dotesports.com/gta/news/gta-6-review-roundup")])}""",
 faq=[("What is GTA 6's Metacritic score?", "99, tied with The Legend of Zelda: Ocarina of Time for the highest score in Metacritic's history (as of November 18, 2026)."),
      ("Does GTA 6 have any bad reviews?", "As of November 18, 2026, there were no mixed or negative reviews on Metacritic.")],
 modified="2026-11-18")
guide("gta-6-game-awards-nominations", "GTA 6 at The Game Awards 2026: 8 Nominations Including Game of the Year",
 "GTA 6 earned 8 nominations at The Game Awards 2026, including Game of the Year and Best Performance for Lucia's actress Manni L. Perez, two days before launch.",
 "2026-11-17", f"""<h1>GTA 6 is up for <span>Game of the Year</span></h1>
<p class="meta">Updated November 17, 2026 · Vice Replay</p>
<p class="lede">The Game Awards 2026 nominations came out on November 17, two days before GTA 6 even launched, and GTA 6 got <b>8 nominations</b>, including <b>Game of the Year</b>.</p>
<h2>Lucia's actress, confirmed</h2>
<p>One nomination finally confirmed something fans had guessed since the first trailer: <b>Manni L. Perez</b> plays Lucia. She's nominated for Best Performance. Jason's actor still hasn't been officially revealed.</p>
<h2>Why this is unusual</h2>
<p>Games have to be out by the eligibility cutoff, and GTA 6 launches November 19, just inside it. Jurors got very little time with the game before voting on nominations.</p>
<h2>When are the winners revealed?</h2>
<p>The Game Awards 2026 show is on <b>December 10, 2026</b>, at the Peacock Theater in Los Angeles.</p>
<div class="box"><h3>Watch</h3><div class="btns"><a class="item" href="https://www.youtube.com/watch?v=xvudsg_o6ow" target="_blank" rel="noopener">GTA 6 just got nominated for Game of the Year<small>Vice Replay Short</small><span aria-hidden="true">→</span></a><a class="item" href="https://www.youtube.com/watch?v=_5ZWAUY75y4" target="_blank" rel="noopener">Lucia's actress is CONFIRMED<small>Vice Replay Short</small><span aria-hidden="true">→</span></a></div></div>
{sources([("Insider Gaming: Lucia's actress revealed","https://insider-gaming.com/gta-6-lucia-actress-officially-revealed-during-2026-game-awards-nominations/"),("GamesRadar: Lucia actor revealed","https://www.gamesradar.com/games/grand-theft-auto/gta-6-lucia-actor-revealed-thanks-to-the-game-awards-best-performance-nomination-and-yes-its-exactly-who-everyone-expected/"),("Destructoid: TGA 2026 nominations","https://www.destructoid.com/gta-6-the-game-awards-tga-nominations-2026/"),("Forbes: Game of the Year nominees","https://www.forbes.com/sites/paultassi/2026/11/17/the-6-game-of-the-year-nominees-at-the-game-awards--did-gta-6-make-it/")])}""")

# 11. Launch live hub (update the UPDATES list every day of launch week; newest first)
UPDATES = [(u["time"], u["html"]) for u in json.load(open(os.path.join(STUDIO, "site/live.json")))]  # newest first
guide("gta-6-launch-live", "GTA 6 Live Updates: Patches, Records and News After Launch",
 "GTA 6 news, newest first: patch notes, sales and streaming records, The Game Awards and PC news, all checked in 2+ sources. Updated every day.",
 "2026-11-17", f"""<h1>GTA 6 news: <span>live updates</span></h1>
<p class="meta">Last updated {UPDATES[0][0]} · Vice Replay · Updated every day</p>
<p class="lede">GTA 6 came out on <b>November 19, 2026</b> on PS5 and Xbox Series X|S. Every confirmed update since then is on this page, newest first.</p>
<div class="box"><h3>Coming up (Eastern)</h3><ul class="list" style="margin:0">
<li><b>Now until Nov 30:</b> Black Friday sales. GTA 6 itself is still full price. <a href="/guides/gta-6-black-friday/">What's worth buying</a></li>
<li><b>Thu Dec 10, 7:30 PM:</b> The Game Awards. GTA 6 has 8 nominations, the most this year. <a href="/guides/gta-6-game-awards/">Our preview</a></li>
<li><b>Next patch:</b> no date yet. The latest is 1.002.002 (Nov 23). <a href="/guides/gta-6-patch-notes/">Patch notes</a></li>
<li><b>PC:</b> no official date. A report says early 2027; Rockstar hasn't confirmed it. <a href="/guides/gta-6-pc-release-date/">What's known</a></li></ul></div>
<h2>Latest updates</h2>
{"".join(f'<div class="note"><b>{t}</b><br>{x}</div>' for t, x in UPDATES)}
<h2>Popular guides</h2>
<ul class="list"><li><a href="/guides/gta-6-storage/">Storage full? Free fixes first</a></li>
<li><a href="/guides/gta-6-patch-notes/">Patch notes: every fix so far</a></li>
<li><a href="/guides/gta-6-how-long-to-beat/">How long to beat GTA 6</a></li>
<li><a href="/guides/gta-6-cheats/">Cheat codes: what's real</a></li>
<li><a href="/guides/gta-6-streaming-records/">Streaming records: who won launch week</a></li>
<li><a href="/guides/gta-6-launch-week-numbers/">Launch week in numbers</a></li></ul>
{gearbox(GAME + STORAGE, "Getting the game or making room for the 212 GB install? Links go to the exact listings:")}
{watchmore("pcoMWOraJA4")}""",
 faq=[("When did GTA 6 come out?", "November 19, 2026, on PS5 and Xbox Series X|S."),
      ("Is GTA 6 on PC?", "Not yet. There's no official PC date; a report says early 2027, but Rockstar hasn't confirmed it.")],
 modified="2026-11-24")

# Spanish guides (es/guias/)
guide("trucos-gta-6", "Trucos de GTA 6: dinero, chaleco, munición y cómo desbloquearlos",
 "Trucos verificados de GTA 6 para PS5 y Xbox: el truco de 250.000 $, chaleco, munición infinita, sin recargar y más, cómo se desbloquea cada uno y la trampa (sin guardar ni trofeos).",
 "2026-11-19", f"""<h1>Trucos de GTA 6: <span>la lista verificada</span></h1>
<p class="meta">Actualizado el 19 de noviembre de 2026, 4:30 PM (hora del Este) · Vice Replay</p>
<p class="lede">Respuesta corta: <b>sí, GTA 6 tiene trucos</b>, incluido uno de <b>250.000 $</b>. La trampa: <b>solo se desbloquean al terminar la historia principal</b>, y usar uno desactiva el guardado y los trofeos durante esa sesión.</p>
<div class="box"><h3>Cómo funcionan</h3><ul class="list" style="margin:0"><li><b>Primero termina la historia:</b> los trucos se desbloquean al completar la historia principal (Eurogamer vio que el menú aparece después de los créditos), y solo en esa partida, según PC Gamer.</li><li><b>Gánate cada uno:</b> muchos trucos piden además su propio desafío.</li><li><b>Sin guardar ni trofeos:</b> con un truco activo no puedes guardar y los trofeos/logros se apagan el resto de esa sesión. Carga una partida limpia para recuperarlos.</li><li><b>Cómo se introducen:</b> según Screen Rant, abre el teléfono (cruceta arriba), mantén L1 + R1 en PS5 (LB + RB en Xbox) e introduce el código.</li></ul></div>
<h2>Trucos verificados de GTA 6 (PS5 y Xbox)</h2>
<p>Abre el teléfono (cruceta arriba), mantén <b>L1 + R1</b> (<b>LB + RB</b> en Xbox) y marca las flechas con la cruceta. Cada código aparece igual en al menos dos de estas guías: GameSpot, PC Gamer, GamesRadar, Screen Rant y Vice.</p>
{cheat_table("es")}
<h2>¿Qué listas creer?</h2>
<p>Las guías de lanzamiento hablan de unos 60 trucos, pero no coinciden en todos los códigos ni en cómo se desbloquean. Dejamos fuera los que no coinciden o que solo aparecen en una guía.</p>
<h2>¿Truco de dinero?</h2>
<p>Sí: <b>↑ → ↓ ← ↑ ← ↓ →</b> da <b>250.000 $</b> al terminar la historia. Pero los trucos bloquean el guardado, así que el dinero no se queda en tu partida. Cualquier sitio que te pida tu cuenta de PlayStation o Xbox, o que ofrezca un "generador de dinero", es una estafa.</p>
{gearbox(GAME + STORAGE, "¿Vas a comprar GTA 6 o necesitas espacio? Enlaces (en inglés, Amazon EE. UU.):")}
{sources([("GameSpot","https://www.gamespot.com/articles/all-gta-6-cheats-and-how-to-unlock-them/"),("Vice","https://www.vice.com/en/article/gta-6-cheat-codes-list/"),("GamesRadar","https://www.gamesradar.com/games/grand-theft-auto/gta-6-cheats/"),("PC Gamer","https://www.pcgamer.com/games/grand-theft-auto/gta-6-cheats-list/"),("Insider Gaming","https://insider-gaming.com/all-gta-6-cheats-best-grand-theft-auto-6-cheat-codes/"),("VGTimes (pruebas de Eurogamer)","https://vgtimes.com/gaming-news/175043-gta-6-locks-cheats-behind-the-main-story-and-disables-saving.html")])}""",
 faq=[("¿Hay trucos en GTA 6?", "Sí. Según Polygon, GamesRadar y PC Gamer, GTA 6 tiene trucos, pero solo se desbloquean al terminar la historia principal."),
      ("¿Los trucos de GTA 6 desactivan los trofeos?", "Sí. Con un truco activo no puedes guardar y los trofeos/logros se apagan el resto de esa sesión. Carga una partida limpia para recuperarlos."),
      ("¿Hay truco de dinero en GTA 6?", "Sí: arriba, derecha, abajo, izquierda, arriba, izquierda, abajo, derecha da 250.000 $ al terminar la historia, según GameSpot, PC Gamer y GamesRadar. Los trucos bloquean el guardado, así que el dinero no se queda. Los 'generadores de dinero' son estafas.")], lang="es")

guide("espacio-gta-6", "¿Sin espacio para GTA 6? Cómo liberar espacio en PS5 y Xbox (212 GB)",
 "GTA 6 necesita hasta 212 GB. Primero las soluciones gratis para liberar espacio en PS5 y Xbox Series X|S, y luego qué buscar si necesitas más almacenamiento.",
 "2026-11-18", f"""<h1>¿Sin espacio? <span>Primero lo gratis</span></h1>
<p class="meta">Actualizado el 18 de noviembre de 2026 · Vice Replay</p>
<p class="lede">Según Rockstar, GTA 6 ocupa <b>hasta 212 GB</b>, más un poco de espacio temporal durante la instalación. Prueba primero lo gratis.</p>
<h2>1. Mira qué ocupa espacio</h2>
<p><b>PS5:</b> Ajustes → Almacenamiento → Almacenamiento de la consola → Juegos y aplicaciones. <b>Xbox:</b> Mis juegos y aplicaciones → Administrar → Almacenamiento.</p>
<h2>2. Borra sin perder nada</h2>
<p>Con las partidas en la nube activadas, borrar un juego no borra tu progreso, y puedes volver a descargar los juegos que tienes.</p>
<h2>3. Borra clips y capturas viejas</h2>
<p>Los videos y capturas antiguas ocupan mucho más de lo que parece.</p>
<h2>4. Guarda juegos en un disco USB</h2>
<p>Ambas consolas pueden guardar juegos en un disco USB externo. Los juegos de PS5 y Xbox Series hay que pasarlos de vuelta para jugarlos, pero es más rápido que descargarlos otra vez.</p>
<h2>Si aún necesitas espacio</h2>
<p><b>PS5:</b> tiene una ranura para un SSD M.2 NVMe (PCIe Gen4); Sony recomienda uno con disipador. <b>Xbox Series X|S:</b> los juegos actuales solo funcionan desde el almacenamiento interno o una tarjeta de expansión oficial.</p>
{gearbox(STORAGE, "Opciones y precios actuales (Amazon EE. UU.). Revisa la compatibilidad con tu consola antes de comprar:")}
{sources([("PlayStation: SSD M.2 en PS5","https://www.playstation.com/es-mx/support/hardware/ps5-install-m2-ssd/"),("Xbox: almacenamiento Series X|S","https://support.xbox.com/es-MX/help/hardware-network/console/xbox-series-x-s-storage-options")])}""",
 faq=[("¿Cuánto pesa GTA 6?", "Según Rockstar, hasta 212 GB según la consola, más espacio temporal durante la instalación.")], lang="es")

guide("hora-de-lanzamiento-gta-6", "GTA 6: a qué hora se desbloquea en cada país",
 "GTA 6 se desbloquea a la medianoche hora local el 19 de noviembre de 2026. Quién juega primero, la duda de EE. UU., Xbox Cloud Gaming y el truco de Nueva Zelanda.",
 "2026-11-18", f"""<h1>GTA 6: <span>¿qué medianoche?</span></h1>
<p class="meta">Actualizado el 18 de noviembre de 2026 · Vice Replay</p>
<p class="lede">GTA 6 sale el jueves 19 de noviembre de 2026 en PS5 y Xbox Series X|S, y se desbloquea a la <b>medianoche hora local</b> en cada región.</p>
<h2>Quién juega primero</h2>
<p>Nueva Zelanda llega primero a la medianoche: según las fichas de PlayStation Store, alrededor de las 6 AM hora del Este de EE. UU. del 18 de noviembre. Luego Australia, Japón, India, Europa y Reino Unido.</p>
<h2>Latinoamérica y EE. UU.</h2>
<p>Algunos reportes dicen que en América se desbloquea la noche del 18 de noviembre; otros esperan la medianoche de cada zona horaria. Lo más seguro: revisa la hora en la página de GTA 6 en la tienda de tu consola.</p>
<h2>Xbox Cloud Gaming</h2>
<p>Según Forbes, empieza a la <b>1 AM hora del Este</b>, no a la medianoche.</p>
<h2>El truco de Nueva Zelanda</h2>
<p>Cambiar la región de tu Xbox a Nueva Zelanda no está confirmado para GTA 6 y puede poner en riesgo tu cuenta. No vale la pena por unas horas.</p>
{gearbox(STORAGE)}
{sources([("Push Square","https://www.pushsquare.com/guides/gta-6-release-times-when-can-you-start-playing"),("Forbes: Xbox Cloud Gaming","https://www.forbes.com/sites/brianmazique/2026/11/16/xbox-just-revealed-the-exact-hour-gta-6-starts-streaming-and-it-isnt-midnight/")])}""",
 faq=[("¿A qué hora sale GTA 6?", "A la medianoche hora local del 19 de noviembre de 2026, región por región. Revisa la hora exacta en la tienda de tu consola.")], lang="es")

guide("gta-6-pc", "GTA 6 en PC: fecha de salida y lo que se sabe",
 "GTA 6 sale solo en PS5 y Xbox Series X|S. Lo que dijo Take-Two sobre PC, la fecha reportada de principios de 2027 y lo que aún no está confirmado.",
 "2026-11-18", f"""<h1>GTA 6 en PC: <span>¿cuándo?</span></h1>
<p class="meta">Actualizado el 18 de noviembre de 2026 · Vice Replay</p>
<p class="lede">GTA 6 salió el 19 de noviembre de 2026 <b>solo en PS5 y Xbox Series X|S</b>. Todavía no hay fecha oficial para PC (revisado el 24 de noviembre).</p>
<h2>Lo oficial</h2><p>Take-Two solo anunció consolas. Su CEO, Strauss Zelnick, dijo que Rockstar "siempre empieza en consola".</p>
<h2>Lo reportado: principios de 2027</h2><p>Según un reporte de GamesBeat con fuentes anónimas, la versión de PC apuntaría a <b>enero-marzo de 2027</b>. Rockstar no lo ha confirmado.</p>
<h2>Cuidado</h2><p>No compres "claves de GTA 6 para PC": no existe esa versión, son estafas.</p>
{gearbox(GAME + STORAGE, "¿Vas a jugar en consola? Enlaces (Amazon EE. UU.):")}
{sources([("GodisaGeek","https://godisageek.com/2026/10/gta-6-pc-release-date-q1-2027"),("tbreak","https://tbreak.com/gta-6-pc-release-delayed-console-first/")])}""",
 faq=[("¿GTA 6 sale en PC?", "No en el lanzamiento. No hay fecha oficial; un reporte habla de principios de 2027, sin confirmar.")], lang="es")

guide("gta-6-lanzamiento-en-vivo", "GTA 6 en vivo: parches, récords y noticias tras el lanzamiento",
 "Noticias de GTA 6, de la más nueva a la más vieja: notas del parche, récords de ventas y de streaming, The Game Awards y PC. Todo revisado en 2+ fuentes.",
 "2026-11-18", f"""<h1>Noticias de GTA 6: <span>en vivo</span></h1>
<p class="meta">Actualizado el 24 de noviembre de 2026 · Vice Replay</p>
<p class="lede">GTA 6 salió el <b>19 de noviembre de 2026</b> en PS5 y Xbox Series X|S. Aquí está cada novedad confirmada desde entonces.</p>
<div class="box"><h3>Lo que viene (hora del Este de EE. UU.)</h3><ul class="list" style="margin:0">
<li><b>Hasta el 30 nov:</b> rebajas de Black Friday; GTA 6 sigue a precio completo</li>
<li><b>Jue 10 dic, 7:30 PM:</b> The Game Awards. GTA 6 tiene 8 nominaciones. <a href="/es/guias/gta-6-premios-game-awards/">Nuestra previa</a></li>
<li><b>Próximo parche:</b> sin fecha. El último es el 1.002.002 (23 nov). <a href="/es/guias/gta-6-notas-del-parche/">Notas del parche</a></li>
<li><b>PC:</b> sin fecha oficial; un reporte habla de principios de 2027, sin confirmar. <a href="/es/guias/gta-6-pc/">Lo que se sabe</a></li></ul></div>
<h2>Últimas noticias</h2>
<div class="note"><b>24 nov</b><br>Los creadores más vistos del primer día (Streams Charts): IShowSpeed, 4,47 millones de horas; el VTuber TheBurntPeanut, 3,89 millones. <a href="/es/guias/gta-6-records-streaming/">Récords de streaming</a>.</div>
<div class="note"><b>23 nov</b><br>Rockstar publicó por fin notas del parche: la actualización 1.002.002 trae 7 arreglos. <a href="/es/guias/gta-6-notas-del-parche/">Los 7 arreglos</a>.</div>
<div class="note"><b>20 nov</b><br>Take-Two: GTA 6 hizo 3.790 millones de dólares entre preventas y ventas del primer día. <a href="/es/guias/gta-6-cifras-semana-lanzamiento/">Todas las cifras</a>.</div>
<div class="note"><b>19 nov, 3 AM</b><br>Los trucos existen, pero solo se desbloquean al terminar la historia, y desactivan el guardado y los trofeos durante la sesión. <a href="/es/guias/trucos-gta-6/">Cómo funcionan</a>.</div>
<div class="note"><b>17 nov</b><br>The Game Awards 2026: GTA 6 recibe 8 nominaciones, incluido Juego del Año. Manni L. Perez, la actriz de Lucía, está nominada a Mejor Actuación.</div>
<h2>Guías populares</h2>
<ul class="list"><li><a href="/es/guias/espacio-gta-6/">¿Sin espacio? Primero lo gratis</a></li><li><a href="/es/guias/cuanto-dura-gta-6/">Cuánto dura GTA 6</a></li><li><a href="/es/guias/trucos-gta-6/">Trucos de GTA 6</a></li><li><a href="/es/guias/gta-6-pc/">GTA 6 en PC</a></li></ul>
{gearbox(GAME + STORAGE, "Enlaces directos (Amazon EE. UU.):")}""",
 faq=[("¿Cuándo salió GTA 6?", "El 19 de noviembre de 2026 en PS5 y Xbox Series X|S."),
      ("¿GTA 6 está en PC?", "Todavía no. No hay fecha oficial; un reporte habla de principios de 2027, sin confirmar.")], lang="es")

# Guides written as data by the daily run: site/guides/<slug>.json
# {"slug","lang":"en|es","title","desc","date","video":"YouTube id or null","card":[line1,line2,"screenshot.jpg"],
#  "lede","sections":[[heading, html]],"note","faq":[[q,a]],"gear":["game","storage"],"sources":[[name,url]]}
import glob as _glob


def interactive_map(lang="en", only=None):
    """Nov 24 (owner: "research those maps pictures more"): Rockstar's official Leonida map, zoomable to full HD
    (tiles from tools/map_tiles.py), with our pins from site/map-pins.json and category filters. A guide JSON section
    that contains <!--MAP--> gets it, followed by a numbered list of the pins (tap one to fly to it)."""
    import shutil
    import sys
    sys.path.insert(0, STUDIO)
    from studio import mappins
    src = json.load(open(os.path.join(STUDIO, "site", "map-pins.json")))
    os.makedirs(os.path.join(SITE, "js"), exist_ok=True)
    shutil.copy(os.path.join(STUDIO, "site", "assets", "vr-map.js"), os.path.join(SITE, "js", "vr-map.js"))
    cats = [{"id": c["id"], "color": c["color"], "name": c[lang]} for c in src["cats"]]
    pins = []
    for n, p in enumerate(src["pins"], 1):
        x, y = mappins.where(p["at"])
        if "dx" not in p and "dy" not in p and str(p["at"]).lower() in {k.lower() for k in mappins.PLACES}:
            y -= 0.009  # just above the printed place name, so the pin doesn't cover it
        t = p[lang]
        slug = _re.sub(r"[^a-z0-9]+", "-", p["en"]["t"].lower().replace("'", "")).strip("-")  # same id in EN and ES
        pins.append({"n": n, "id": slug, "cat": p["cat"], "x": round(x + p.get("dx", 0), 4), "y": round(y + p.get("dy", 0), 4),
                     "t": t["t"], "d": t["d"], "when": t.get("when", "")})
    data = {"lang": lang, "w": 5775, "h": 7900, "cats": cats, "pins": pins}
    if only:  # a category page (<!--MAP:mods-->): opens on that layer, lists only its pins; the rest stay one tap away
        data["only"] = list(only)
    data = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    es = lang == "es"
    hint = ("Pellizca o usa la rueda para acercarte hasta las calles; toca un pin para ver qué hay y dónde. Los pines marcan la zona."
            if es else "Pinch or scroll to zoom down to street names; tap a pin for what's there. Pins mark the area.")
    items = "".join(f'<li id="{p["id"]}-item"><a href="#{p["id"]}" data-pin="{p["n"]}"><b>{p["n"]}. {html.escape(p["t"])}</b></a>: {html.escape(p["d"])}'
                    + (f' <i>({html.escape(p["when"])})</i>' if p["when"] else "") + "</li>" for p in pins
                    if not only or p["cat"] in only)
    style = ('<style>#vrmap{height:min(78vh,720px);border-radius:14px;border:1px solid var(--line);margin:12px 0 6px;background:#0d0717}'
             '.vrpin b{display:flex;align-items:center;justify-content:center;width:30px;height:30px;border-radius:50%;color:#fff;'
             'font:700 14px/1 var(--body);border:2px solid #fff;box-shadow:0 0 0 3px rgba(13,7,23,.55),0 0 14px rgba(255,31,142,.6)}'
             '.vrsmall .vrpin b{width:18px;height:18px;margin:6px;font-size:10px;border-width:1.5px;box-shadow:0 0 0 2px rgba(13,7,23,.5)}'
             '.vrlegend{background:rgba(13,7,23,.88);color:#f4eefc;padding:8px 10px;border-radius:10px;font:600 13px/1.5 var(--body)}'
             '.vrlegend label{display:flex;align-items:center;gap:6px;cursor:pointer}.vrlegend i{width:12px;height:12px;border-radius:50%;display:inline-block}'
             '.leaflet-container img.leaflet-tile{mix-blend-mode:normal;width:256.6px!important;height:256.6px!important}.leaflet-popup-content{font:14px/1.45 var(--body)}.vrdone b{opacity:.45;filter:grayscale(.6)}.vrok{color:#1a9c5b;font-weight:700}.vrbtn{margin-top:8px;padding:6px 10px;border-radius:8px;border:0;background:#ff1f8e;color:#fff;font:600 13px var(--body);cursor:pointer}.vrprog{margin-top:6px;padding-top:6px;border-top:1px solid rgba(255,255,255,.2)}.vrcount{display:block;color:#00e5d2}.vrlink{background:none;border:0;color:#b7a9cf;text-decoration:underline;font:12px var(--body);padding:0;cursor:pointer}.vrdone-item{opacity:.55;text-decoration:line-through}.vrsearch{width:100%;margin:0 0 6px;padding:5px 8px;border-radius:7px;border:1px solid rgba(255,255,255,.25);background:rgba(255,255,255,.08);color:#f4eefc;font:13px var(--body)}.vrlegend small{color:#b7a9cf;margin-left:2px}.vrnext{display:block;margin:6px 0 4px;padding:5px 9px}.vrlist li{margin-bottom:8px}</style>')
    return (f'<link rel="stylesheet" href="/js/leaflet.css">{style}<div id="vrmap" role="application" '
            f'aria-label="{"Mapa interactivo de Leonida" if es else "Interactive map of Leonida"}"></div>'
            f'<p class="meta">{hint}</p><ol class="list vrlist">{items}</ol>'
            f'<script type="application/json" id="vrpins">{data}</script>'
            '<script src="/js/leaflet.js"></script><script src="/js/vr-map.js"></script>')


_MAPTAG = _re.compile(r"<!--MAP(?::([a-z,]+))?-->")  # <!--MAP--> = every pin; <!--MAP:mods--> = a category page
_JSON = [json.load(open(_f)) for _f in sorted(_glob.glob(os.path.join(STUDIO, "site/guides/*.json")))]
for _g in _JSON:  # "pair": slug of the same guide in the other language (EN guides/<slug>/ <-> ES es/guias/<slug>/)
    if _g.get("pair") and _g.get("lang", "en") == "en":
        ALT[f"guides/{_g['slug']}/"] = f"es/guias/{_g['pair']}/"
        ALT[f"es/guias/{_g['pair']}/"] = f"guides/{_g['slug']}/"
for g in _JSON:
    if g.get("card"): CARDS[g["slug"]] = tuple(g["card"])
    items = (GAME if "game" in g.get("gear", []) else []) + (STORAGE if "storage" in g.get("gear", []) else []) + (GEAR if "gear" in g.get("gear", []) else [])
    es = g.get("lang") == "es"
    h1 = g.get("h1") or g["title"]
    body = f'<h1>{h1}</h1><p class="meta">{"Actualizado el" if es else "Updated"} {__import__("datetime").date.fromisoformat(g["date"]).strftime("%B %-d, %Y")} · Vice Replay</p><p class="lede">{g.get("lede", "")}</p>'
    body += video(g["video"], g["title"]) if g.get("video") else ""
    body += "".join(_MAPTAG.sub(lambda m: interactive_map(g.get("lang", "en"), (m.group(1) or "").split(",") if m.group(1) else None),
                                f"<h2>{html.escape(h)}</h2>{b}") for h, b in g.get("sections", []))
    body += f'<div class="note">{g["note"]}</div>' if g.get("note") else ""
    body += gearbox(items, "Enlaces (Amazon EE. UU.):" if es else "Getting GTA 6 or making room for it? Links go to current listings:") if items else ""
    body += watchmore(g["video"], "es" if es else "en") if g.get("video") else ""
    body += sources([tuple(x) for x in g.get("sources", [])]) if g.get("sources") else ""
    guide(g["slug"], g["title"], g["desc"], g["date"], body, faq=[tuple(x) for x in g.get("faq", [])] or None, lang=g.get("lang", "en"))

# Search box on the guide lists (Nov 24): filters the cards as you type, no server needed
SEARCH_JS = '<script>(function(){var q=document.getElementById("q");if(!q)return;var cs=[].slice.call(document.querySelectorAll(".cards .card"));var n=document.getElementById("qn");q.addEventListener("input",function(){var t=q.value.toLowerCase().trim(),k=0;cs.forEach(function(c){var m=!t||c.textContent.toLowerCase().indexOf(t)>-1;c.style.display=m?"":"none";if(m)k++;});n.textContent=t?(k+" / "+cs.length):"";});})();</script>'
GUIDES_ES.sort(key=lambda g: g[3], reverse=True)
page("es/", "Guías de GTA 6 en español · Vice Replay", "Guías de GTA 6 en español: trucos, hora de lanzamiento, espacio y PC. Sin spoilers.",
     banner('Guías de GTA&nbsp;6 <span>en español</span>', 'swamp-nature') + '<p class="lede">Guías rápidas y con fuentes. Sin spoilers. <a href="' + YT_ES + '?sub_confirmation=1">Suscríbete a Vice Replay en Español</a>: Shorts de GTA 6 en español cada día.</p><div class="search"><input type="search" id="q" placeholder="Busca entre ' + str(len(GUIDES_ES)) + ' guías: trucos, precio, online..." aria-label="Buscar guías" autocomplete="off"><span id="qn"></span></div><div class="cards">'
     + "".join(f'<a class="card pic" href="/es/guias/{s}/"><img src="/og/t/{s}.webp" width="480" height="252" alt="{html.escape(t)}" loading="lazy"><span><b>{html.escape(t)}</b><small>{html.escape(d)}</small></span></a>' for s, t, d, _ in GUIDES_ES) + '</div>' + SEARCH_JS, lang="es")

# Spanish gear page (Nov 22, 2026): the Amazon link for Vice Replay en Español (channel links, descriptions, comments)
ALT.update({"es/equipo/": "gear/"})
ES_GEAR = [("Más espacio para PS5: SSD NVMe de 2 TB con disipador", "PS5 compatible 2TB NVMe SSD with heatsink"),
           ("Tarjeta de expansión para Xbox Series X|S", "Xbox Series X S storage expansion card 2TB"),
           ("Control DualSense de PS5", "PS5 DualSense controller"),
           ("Audífonos gamer (PS5 / Xbox)", "gaming headset PS5 Xbox"),
           ("GTA 6 para PS5", GAME[0][1]), ("GTA 6 para Xbox Series X|S", GAME[1][1]),
           ("Capturadora para grabar tu gameplay", "capture card 4K60 PS5"),
           ("Prueba gratis de Amazon Prime (30 días)", "https://www.amazon.com/tryprimefree")]
_es_items = "".join(f'<a class="item" href="{amz(q)}" target="_blank" rel="sponsored noopener">{html.escape(label)}<span aria-hidden="true">→</span></a>' for label, q in ES_GEAR)
page("es/equipo/", "Equipo para GTA 6 (Amazon) · Vice Replay", "Equipo para GTA 6: espacio para PS5 y Xbox, control, audífonos y el juego. Enlaces de Amazon.",
     banner('Equipo para <span>GTA&nbsp;6</span>', 'deals-gear')
     + '<p class="lede">Lo que más nos preguntan: espacio para instalar GTA 6, control, audífonos y el juego. Los botones buscan en Amazon.com con precios actuales.</p>'
     + f'<div class="box"><h3>Equipo para GTA 6 (enlaces de afiliado)</h3><div class="btns">{_es_items}</div>'
     + '<p class="sources" style="margin:10px 0 0">Enlaces de afiliado: como Afiliado de Amazon gano con las compras que califican, sin costo extra para ti. '
       'No hemos probado estos productos: revisa reseñas y compatibilidad antes de comprar. Los enlaces llevan a Amazon.com (Estados Unidos); '
       'desde México u otros países revisa el envío y el precio final.</p></div>'
     + '<p>¿Sin espacio para GTA 6? Antes de comprar, prueba lo gratis: <a href="/es/guias/espacio-gta-6/">nuestra guía de espacio</a>.</p>', lang="es")

# guides index
GUIDES.sort(key=lambda g: (g[0] != "gta-6-launch-live", g[3]), reverse=False)
GUIDES[1:] = sorted(GUIDES[1:], key=lambda g: g[3], reverse=True)
card("default", "GTA'S WILDEST MOMENTS.", "ON REPLAY.", "vice-city-11.jpg")
cards = "".join(f'<a class="card pic" href="/guides/{s}/"><img src="/og/t/{s}.webp" width="480" height="252" alt="{html.escape(t)}" loading="lazy"><span><b>{html.escape(t)}</b><small>{html.escape(d)}</small></span></a>' for s, t, d, _ in GUIDES)
page("guides/", "GTA 6 Guides · Vice Replay", "GTA 6 guides from Vice Replay: unlock times, download size, storage, the map and launch tips.",
     banner('GTA&nbsp;6 <span>guides</span>', 'news-skyline') + f'<p class="lede">Quick, sourced GTA 6 guides that go with our videos. No story spoilers. <a href="/es/">En español</a></p><div class="search"><input type="search" id="q" placeholder="Search {len(GUIDES)} guides: money, radio, cheats..." aria-label="Search guides" autocomplete="off"><span id="qn"></span></div><div class="cards">{cards}</div>' + SEARCH_JS)

# links page
latest = GUIDES[0]
page("links/", "Vice Replay Links", "Every Vice Replay link: GTA 6 Black Friday deals, storage fixes, gear, YouTube, TikTok and Instagram.", f"""<h1>Vice Replay <span>links</span></h1>
<p class="lede">GTA's wildest moments. On replay. Fresh GTA 6 news first, then deals and our channels.</p>
<h2>Latest</h2>
<div class="cards">{"".join(f'<a class="card pic" href="/guides/{s_}/"><img src="/og/t/{s_}.webp" width="480" height="252" alt="{html.escape(t_)}" loading="lazy"><span><b>{html.escape(t_)}</b><small>{html.escape(d_)}</small></span></a>' for s_, t_, d_, _x in GUIDES[:4])}</div>
<div class="btns" style="margin-top:12px"><a class="item" href="{YT}?sub_confirmation=1" target="_blank" rel="noopener">▶️ Watch on YouTube<small>Daily GTA 6 Shorts and news</small><span aria-hidden="true">→</span></a></div>
{deals_html()}
<div class="btns">
<a class="item" href="/guides/gta-6-deals/">🏷️ GTA 6 deals and discount codes<small>What's real this week, and the "free code" scams</small><span aria-hidden="true">→</span></a>
<a class="item" href="/guides/gta-6-black-friday/">🔥 GTA 6 Black Friday deals<small>What's worth buying for GTA 6 this week</small><span aria-hidden="true">→</span></a>
<a class="item" href="/guides/gta-6-storage/">💾 GTA 6 says "not enough space"?<small>Free fixes + the PS5 SSD that fits (212 GB)</small><span aria-hidden="true">→</span></a>
<a class="item" href="/guides/gta-6-best-ssd/">🛒 Best SSD for GTA 6 (PS5)<small>What to buy, what to skip, how to install</small><span aria-hidden="true">→</span></a>
<a class="item" href="/guides/gta-6-ps5-pro-worth-it/">🎯 Is PS5 Pro worth it for GTA 6?<small>30 FPS everywhere: what the Pro actually changes</small><span aria-hidden="true">→</span></a>
<a class="item" href="/gear/">🎮 GTA 6 gear picks<small>Controllers, headsets, storage (affiliate)</small><span aria-hidden="true">→</span></a>
<a class="item" href="{YT}?sub_confirmation=1" target="_blank" rel="noopener">YouTube<small>Daily GTA 6 news and Shorts</small><span aria-hidden="true">→</span></a>
<a class="item" href="https://www.tiktok.com/@vicereplay00" target="_blank" rel="noopener">TikTok<small>@vicereplay00</small><span aria-hidden="true">→</span></a>
<a class="item" href="https://www.instagram.com/vice.replaytv/" target="_blank" rel="noopener">Instagram<small>@vice.replaytv</small><span aria-hidden="true">→</span></a>
<a class="item" href="/guides/gta-6-cheats/">GTA 6 cheat codes<small>$250K money, armor, ammo: the verified list</small><span aria-hidden="true">→</span></a>
<a class="item" href="/guides/">GTA 6 guides<small>Unlock times, storage, the map</small><span aria-hidden="true">→</span></a>
<a class="item" href="/contact/">Work with us<small>contact@vicereplay.com</small><span aria-hidden="true">→</span></a>
</div>""")

page("contact/", "Work With Vice Replay", "Sponsorships, clipping campaigns and business enquiries for Vice Replay, a GTA 6 news and Shorts channel.", f"""<h1>Work with <span>Vice Replay</span></h1>
<p class="lede">Vice Replay is a GTA 6 channel: daily news, streamer news, guides and Shorts in English, with Spanish subtitles. We post on YouTube and TikTok.</p>
<div class="box"><h3>Get in touch</h3><div class="btns"><a class="item" href="mailto:contact@vicereplay.com?subject=Vice%20Replay%20enquiry">contact@vicereplay.com<small>Sponsorships, campaigns, press</small><span aria-hidden="true">→</span></a></div></div>
<h2>What we can do</h2>
<ul class="list"><li><b>Sponsored segments</b> in a GTA 6 video or Short, clearly labeled as sponsored.</li><li><b>Clipping campaigns</b> for GTA 6 streamers and creators.</li><li><b>Gear and game features</b> on this site and in our videos.</li></ul>
<h2>What we don't do</h2>
<ul class="list"><li>Fake reviews or claims that we used a product we haven't.</li><li>Gambling, account selling, "money generators" or anything that breaks Rockstar's or YouTube's rules.</li><li>Hidden ads: every paid placement is disclosed.</li></ul>
<p>Include your brand or channel, what you have in mind, and your timing. We usually reply within 2 days.</p>""")

# Privacy policy + terms (Nov 22, 2026): Google needs both links on its Branding page before the YouTube upload app
# ("Creator HQ", shared by Vice Replay, What If Arena and ClipCircuit) can be published, and YouTube API Services require the privacy wording below.
page("privacy/", "Privacy Policy · Vice Replay", "How vicereplay.com and the Creator HQ YouTube tool (Vice Replay, What If Arena, ClipCircuit) handle data.", f"""<h1>Privacy <span>policy</span></h1>
<p class="lede">Last updated November 23, 2026. Vice Replay is a fan channel and website about GTA 6. We collect as little as possible.</p>
<h2>This website</h2>
<ul class="list"><li><b>No accounts, no sign-ups.</b> We don't ask for your name, email or anything else to read the site.</li>
<li><b>Analytics:</b> we use Cloudflare Web Analytics, which counts visits without cookies and without tracking you across sites.</li>
<li><b>Amazon links:</b> some links are Amazon affiliate links (tag vicereplay-20). If you click one, Amazon may use cookies under
<a href="https://www.amazon.com/gp/help/customer/display.html?nodeId=GX7NJQ4ZB8MHFRNJ">Amazon's privacy notice</a>, and we may earn a commission.</li>
<li><b>Embedded YouTube videos</b> are served by YouTube under Google's privacy policy.</li></ul>
<h2>Creator HQ (our YouTube tool)</h2>
<p>Creator HQ is a private tool that uploads and manages videos on <b>the owner's own</b> YouTube channels (Vice Replay, Vice Replay en Español, What If Arena and ClipCircuit) through the <b>YouTube API Services</b>.
It is used only by the channel owner. When the owner signs in with Google, the tool receives access to those channels to upload and schedule videos, add them to playlists, post and reply to comments on the owner's own videos, and read those channels' statistics.</p>
<ul class="list"><li>To plan videos, the tool also reads <b>public</b> YouTube information about popular gaming videos (titles, channel names, view counts) through the YouTube API Services. It is used only inside the tool, never published or shared, and deleted or refreshed within 30 days.</li>
<li>We do not sell or share any YouTube data, and we do not collect personal data from other YouTube users.</li>
<li>The access key is stored privately in our own production environment and used only for our channels.</li>
<li>By using features built on YouTube, you are also subject to the <a href="https://www.youtube.com/t/terms">YouTube Terms of Service</a> and the <a href="https://policies.google.com/privacy">Google Privacy Policy</a>.</li>
<li>Access can be revoked at any time on the <a href="https://security.google.com/settings/security/permissions">Google security settings page</a>. To have data deleted, write to the contact address below; we answer within 30 days.</li></ul>
<h2>Children</h2><p>This site and our channels are not directed to children under 13.</p>
<h2>Contact</h2><p>Questions about privacy: <a href="mailto:contact@vicereplay.com">contact@vicereplay.com</a>.</p>""")

page("terms/", "Terms of Use · Vice Replay", "Terms of use for vicereplay.com and Vice Replay.", f"""<h1>Terms <span>of use</span></h1>
<p class="lede">Last updated November 22, 2026.</p>
<h2>Fan site</h2><p>Vice Replay is a fan channel and website. It is <b>not affiliated with Rockstar Games or Take-Two Interactive</b>. Grand Theft Auto, GTA and related names and images belong to their owners and are used here for news, commentary and guides.</p>
<h2>Content</h2><p>Guides and news are for information and entertainment. We check facts against sources and date our pages, but games and prices change: always check the official source before you buy or rely on something.</p>
<h2>Affiliate links</h2><p>Some links are affiliate links (Amazon Associates, tag vicereplay-20). We may earn a commission at no extra cost to you, and we disclose it where it applies.</p>
<h2>YouTube</h2><p>Our videos are on YouTube and follow the <a href="https://www.youtube.com/t/terms">YouTube Terms of Service</a>.</p>
<h2>No warranty</h2><p>The site is provided as is. We aren't responsible for third-party sites we link to.</p>
<h2>Contact</h2><p><a href="mailto:contact@vicereplay.com">contact@vicereplay.com</a></p>""")

INDEXNOW_KEY = "42ea7b879d668a2c990cad4a77c32361"  # public by design: proves to Bing/IndexNow that we own the site
open(os.path.join(SITE, f"{INDEXNOW_KEY}.txt"), "w").write(INDEXNOW_KEY)
open(os.path.join(SITE, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
_newest = max([d for *_, d in GUIDES] + ["2026-11-18"]); _newest_es = max([d for *_, d in GUIDES_ES] + ["2026-11-18"])  # hubs change whenever a guide is added
# About pages (Nov 24 upgrade): who we are and how we check facts. Google's quality guidance weighs trust; a fan site
# earns it by showing its rules. No owner name or location here (owner info stays private).
ALT["about/"] = "es/acerca/"; ALT["es/acerca/"] = "about/"
_ORG = {"@context": "https://schema.org", "@type": "Organization", "name": "Vice Replay", "url": DOMAIN + "/",
        "logo": DOMAIN + "/favicon.png", "email": "contact@vicereplay.com",
        "sameAs": [YT, YT_ES, "https://www.tiktok.com/@vicereplay00", "https://www.instagram.com/vice.replaytv/"]}
page("about/", "About Vice Replay: How We Check GTA 6 News", "Who makes Vice Replay, how we check every GTA 6 fact in 2+ sources, how we fix mistakes, and how the site makes money.", f"""<h1>About <span>Vice Replay</span></h1>
<p class="lede">Vice Replay is an independent GTA 6 fan channel and website: daily news, streamer stories, guides and Shorts, in English and Spanish. GTA's wildest moments. On replay.</p>
<h2>How we check facts</h2>
<ul class="list"><li>Every number, date and quote is checked in <b>at least two reputable sources</b> before we publish, and again right before a video goes out.</li>
<li>Sources are listed at the bottom of every guide, with links.</li>
<li>Reports and rumors are labeled ("reportedly", "not confirmed by Rockstar").</li>
<li>No story spoilers in titles or thumbnails, and we never use leaked material.</li></ul>
<h2>When something changes</h2>
<p>GTA 6 news moves fast. When a fact changes we update the page and its date; when an older page is out of date we add a dated note at the top instead of quietly rewriting history. Spotted a mistake? <a href="mailto:contact@vicereplay.com">contact@vicereplay.com</a>.</p>
<h2>How the site makes money</h2>
<p>Some links are Amazon affiliate links: as an Amazon Associate we earn from qualifying purchases, at no extra cost to you. Sponsored segments are always labeled. We never sell codes, accounts or "money generators".</p>
<h2>Not official</h2>
<p>Vice Replay is a fan project, not affiliated with Rockstar Games or Take-Two Interactive. Grand Theft Auto and GTA are trademarks of Take-Two Interactive.</p>
<h2>Find us</h2>
<div class="btns"><a class="item" href="{YT}" target="_blank" rel="noopener">YouTube<small>English</small><span aria-hidden="true">→</span></a><a class="item" href="{YT_ES}" target="_blank" rel="noopener">YouTube en español<span aria-hidden="true">→</span></a><a class="item" href="https://www.instagram.com/vice.replaytv/" target="_blank" rel="noopener">Instagram<small>@vice.replaytv</small><span aria-hidden="true">→</span></a><a class="item" href="https://www.tiktok.com/@vicereplay00" target="_blank" rel="noopener">TikTok<small>@vicereplay00</small><span aria-hidden="true">→</span></a></div>""",
     jsonld=[_ORG, {"@context": "https://schema.org", "@type": "AboutPage", "name": "About Vice Replay", "url": DOMAIN + "/about/"}])
page("es/acerca/", "Quiénes somos: así revisa Vice Replay las noticias de GTA 6", "Quién hace Vice Replay, cómo revisamos cada dato de GTA 6 en 2+ fuentes, cómo corregimos errores y cómo se financia el sitio.", f"""<h1>Quiénes <span>somos</span></h1>
<p class="lede">Vice Replay es un canal y sitio de fans de GTA 6, independiente: noticias diarias, streamers, guías y Shorts, en inglés y en español.</p>
<h2>Cómo revisamos los datos</h2>
<ul class="list"><li>Cada cifra, fecha y cita se revisa en <b>al menos dos fuentes confiables</b> antes de publicar.</li><li>Las fuentes están al final de cada guía, con enlaces.</li><li>Los rumores se marcan como tales ("según reportes", "sin confirmar").</li><li>Sin spoilers de la historia en títulos ni miniaturas, y nunca usamos material filtrado.</li></ul>
<h2>Cuando algo cambia</h2>
<p>Actualizamos la página y su fecha; si una página vieja quedó desactualizada, ponemos una nota fechada arriba. ¿Viste un error? <a href="mailto:contact@vicereplay.com">contact@vicereplay.com</a>.</p>
<h2>Cómo se financia</h2>
<p>Algunos enlaces son de afiliado de Amazon: como Asociado de Amazon ganamos con las compras que califican, sin costo extra para ti. Los patrocinios siempre se indican.</p>
<h2>No oficial</h2>
<p>Vice Replay es un proyecto de fans, no afiliado con Rockstar Games ni con Take-Two Interactive.</p>""",
     jsonld=[_ORG, {"@context": "https://schema.org", "@type": "AboutPage", "name": "Quiénes somos", "url": DOMAIN + "/es/acerca/"}], lang="es")

urls = [("", _newest), ("guides/", _newest), ("gear/", "2026-11-18"), ("links/", _newest), ("contact/", "2026-11-18"), ("privacy/", "2026-11-23"), ("terms/", "2026-11-22"), ("es/equipo/", "2026-11-22"), ("about/", "2026-11-24"), ("es/acerca/", "2026-11-24")] + [(f"guides/{s}/", d) for s, _, _, d in GUIDES] + [("es/", _newest_es)] + [(f"es/guias/{s}/", d) for s, _, _, d in GUIDES_ES]
open(os.path.join(SITE, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join(f"  <url><loc>{DOMAIN}/{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n")
def refresh_home():
    """Homepage (hand-written index.html): rebuild its deals list and 'Latest GTA 6 news' on every build (Nov 24), so it
    can't keep showing launch-night links or old prices. Latest news = picture cards right under the intro, so a phone
    sees fresh news on the first screen. Also makes sure the head has the org/website data, icon, manifest and RSS."""
    path = os.path.join(SITE, "index.html")
    doc = open(path).read()
    deals = "".join(f'\n    <li><a class="item big" href="{amz(q)}" target="_blank" rel="sponsored noopener">{html.escape(t)}<span aria-hidden="true">→</span></a></li>'
                    for t, sub, q in DEALS)
    deals_sec = (f'<section class="group" id="deals"><h2>🔥 Black Friday deals on Amazon</h2><p>Checked {DEALS_CHECKED} · prices change fast · '
                 f'<a href="/guides/gta-6-deals/" style="color:#00e5d2">every real GTA 6 deal</a></p><ul class="links">{deals}\n  </ul>'
                 '<p style="font-size:13px;opacity:.75">Affiliate links: as an Amazon Associate we earn from qualifying purchases, at no extra cost to you.</p></section>')
    newest = [g for g in GUIDES if g[0] not in ("gta-6-launch-live", "gta-6-map-leonida-places")][:5]
    def short(title):  # "GTA 6 Streaming Records: Most-Watched..." -> "GTA 6 Streaming Records"
        head = title.split(":")[0].strip()
        if len(title) <= 58: return title
        if 14 <= len(head) <= 58: return head
        return title[:58].rsplit(" ", 1)[0] + "…"
    def pic(slug, title, sub, hot=False):
        return (f'\n    <a class="card pic{" hot" if hot else ""}" href="/guides/{slug}/"><img src="/og/t/{slug}.webp" width="480" height="252" '
                f'alt="{html.escape(title)}" loading="lazy"><span><b>{html.escape(title)}</b><small>{html.escape(sub)}</small></span></a>')
    cards = pic("gta-6-launch-live", "🔴 GTA 6 news: live updates", "Every confirmed update since launch, newest first", True)
    cards += pic("gta-6-map-leonida-places", "🗺️ Interactive GTA 6 map (official HD)",
                 "Zoom to street names: easter eggs, the UFO, Bigfoot, bonus cars and mod shops pinned", True)
    cards += "".join(pic(s_, short(ti), de) for s_, ti, de, dt_ in newest)
    latest_sec = f'<section class="group" id="latest"><h2>Latest GTA 6 news</h2><div class="cards">{cards}\n  </div></section>'
    doc2 = _re.sub(r'<section class="group" id="deals">.*?</section>', lambda m: deals_sec, doc, count=1, flags=_re.S)
    doc2 = _re.sub(r'\s*<section class="group"(?: id="latest")?><h2>Latest GTA 6 news</h2>.*?</section>', "", doc2, count=1, flags=_re.S)
    k = doc2.find('<p class="lede">')
    k = doc2.find("</p>", k) + 4
    doc2 = doc2[:k] + "\n  " + latest_sec + doc2[k:]
    style = ('<style id="vr-cards">.cards{display:grid;gap:10px}.card{display:block;background:var(--panel-2);border:1px solid var(--line);'
             'border-radius:14px;color:var(--fg);text-decoration:none}.card:hover{border-color:#ff1f8e}.card.pic{display:grid;'
             'grid-template-columns:120px 1fr;gap:12px;align-items:center;padding:10px}.card.pic img{display:block;width:100%;height:auto;'
             'aspect-ratio:40/21;border-radius:8px}.card.pic b{font-size:16px;line-height:1.3;display:block}.card.pic small{color:var(--muted);'
             'font-size:13px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}.card.hot{outline:2px solid #ff1f8e}'
             '@media(min-width:640px){.card.pic{grid-template-columns:200px 1fr}}@media(max-width:639px){.card.pic{grid-template-columns:1fr}.card.pic b{font-size:18px}.hero{aspect-ratio:2.2/1}.hero .brand{font-size:clamp(36px,11vw,56px)}main>h1,.wrap>h1{font-size:clamp(30px,9vw,42px);margin-top:16px}}</style>')
    doc2 = _re.sub(r'<style id="vr-cards">.*?</style>', "", doc2, flags=_re.S)
    org = json.dumps([{"@context": "https://schema.org", "@type": "WebSite", "name": "Vice Replay", "url": DOMAIN + "/", "inLanguage": ["en", "es"]},
                      {"@context": "https://schema.org", "@type": "Organization", "name": "Vice Replay", "url": DOMAIN + "/", "logo": DOMAIN + "/favicon.png",
                       "sameAs": [YT, YT_ES, "https://www.tiktok.com/@vicereplay00", "https://www.instagram.com/vice.replaytv/"]}], ensure_ascii=False)
    doc2 = _re.sub(r'<script type="application/ld\+json" id="vr-org">.*?</script>', "", doc2, flags=_re.S)
    head_extra = style + f'<script type="application/ld+json" id="vr-org">{org}</script>'
    if 'rel="manifest"' not in doc2:
        head_extra += ('<link rel="apple-touch-icon" href="/favicon.png"><link rel="manifest" href="/site.webmanifest">'
                       '<link rel="alternate" type="application/rss+xml" title="Vice Replay: GTA 6 news and guides" href="/feed.xml">')
    doc2 = doc2.replace("</head>", head_extra + "\n</head>", 1)
    if 'href="/about/"' not in doc2:
        doc2 = doc2.replace('>Work with us</a></p>', '>Work with us</a> · <a href="/about/" style="color:#00e5d2">About us</a></p>', 1)
    if doc2 != doc:
        open(path, "w").write(doc2)



def add_related():
    """Nov 24 upgrade: a 'Related guides' box with 4 picture cards at the end of every guide (EN + ES), picked by shared
    words in title + description (newest first on ties). Internal links help readers stay and help search engines find
    and rank every page. Rebuilt on each run (old box removed first)."""
    stop = set("gta 6 vi the a an and or of to in on for is it its what how why when where with you your our are be".split()
               + "de el la los las y o en un una que para por con del al es su sus lo".split())
    def words(t):
        return {w for w in _re.findall(r"[a-záéíóúñ0-9]+", t.lower()) if w not in stop and len(w) > 2}
    for items, base, heading in ((GUIDES, "guides", "Related guides"), (GUIDES_ES, "es/guias", "Guías relacionadas")):
        info = {s_: (t_, d_, dt_, words(t_ + " " + d_)) for s_, t_, d_, dt_ in items}
        for slug, (title, desc, date, w) in info.items():
            f = os.path.join(SITE, base, slug, "index.html")
            if not os.path.exists(f):
                continue
            ranked = sorted((o for o in info if o != slug), key=lambda o: (len(w & info[o][3]), info[o][2]), reverse=True)[:4]
            cards = "".join(f'<a class="card pic" href="/{base}/{o}/"><img src="/og/t/{o}.webp" width="480" height="252" alt="{html.escape(info[o][0])}" loading="lazy"><span><b>{html.escape(info[o][0])}</b><small>{html.escape(info[o][1])}</small></span></a>' for o in ranked)
            box = f'<div class="related"><h2>{heading}</h2><div class="cards">{cards}</div></div>'
            doc = open(f).read()
            doc = _re.sub(r'<div class="related">.*?</div></div>', "", doc, flags=_re.S)
            doc = doc.replace("</main>", box + "\n</main>", 1)
            open(f, "w").write(doc)


def write_feeds_404_manifest():
    """Nov 24 upgrades: RSS feeds (EN /feed.xml, ES /es/feed.xml) so readers and aggregators can follow new guides,
    a branded 404 page (GitHub Pages serves /404.html) and a web app manifest (save-to-home-screen icon)."""
    import datetime as _dt
    from email.utils import format_datetime
    def feed(items, path, title, link, lang):
        rows = []
        for slug, ti, desc, date in items[:30]:
            url = f"{DOMAIN}/{'es/guias' if lang == 'es' else 'guides'}/{slug}/"
            when = format_datetime(_dt.datetime.fromisoformat(date + "T12:00:00+00:00"))
            rows.append(f"<item><title>{html.escape(ti)}</title><link>{url}</link><guid>{url}</guid>"
                        f"<pubDate>{when}</pubDate><description>{html.escape(desc)}</description></item>")
        xml = (f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>{html.escape(title)}</title>'
               f'<link>{link}</link><description>{html.escape(title)}</description><language>{lang}</language>'
               + "".join(rows) + "</channel></rss>\n")
        os.makedirs(os.path.dirname(os.path.join(SITE, path)) or SITE, exist_ok=True)
        open(os.path.join(SITE, path), "w").write(xml)
    feed(sorted(GUIDES, key=lambda g: g[3], reverse=True), "feed.xml", "Vice Replay: GTA 6 news and guides", DOMAIN + "/", "en")
    feed(sorted(GUIDES_ES, key=lambda g: g[3], reverse=True), "es/feed.xml", "Vice Replay en español: guías de GTA 6", DOMAIN + "/es/", "es")
    latest = "".join(f'<a class="item" href="/guides/{s}/">{html.escape(t)}<span aria-hidden="true">→</span></a>'
                     for s, t, _, _ in sorted(GUIDES, key=lambda g: g[3], reverse=True)[:6])
    page("404/", "Page not found · Vice Replay", "This page went off the map.", f"""<h1>This page went <span>off the map</span></h1>
<p class="lede">The link is old or mistyped. Here's what's new on Vice Replay instead.</p>
<div class="btns"><a class="item" href="/guides/gta-6-launch-live/">🔴 GTA 6 news: live updates<span aria-hidden="true">→</span></a>{latest}<a class="item" href="/guides/">All guides<span aria-hidden="true">→</span></a></div>""")
    d404 = os.path.join(SITE, "404")
    doc = open(os.path.join(d404, "index.html")).read()
    doc = doc.replace('content="index,follow,max-image-preview:large"', 'content="noindex"')
    doc = _re.sub(r'<link rel="canonical"[^>]*>', "", doc)
    open(os.path.join(SITE, "404.html"), "w").write(doc)
    import shutil
    shutil.rmtree(d404, ignore_errors=True)
    json.dump({"name": "Vice Replay", "short_name": "Vice Replay", "start_url": "/", "display": "standalone",
               "background_color": "#0d0717", "theme_color": "#0d0717", "description": "GTA 6 news, guides and Shorts",
               "icons": [{"src": "/favicon.png", "sizes": "192x192", "type": "image/png"}]},
              open(os.path.join(SITE, "site.webmanifest"), "w"))


add_related()
write_feeds_404_manifest()

refresh_home()
try:
    import sys as _sys
    _sys.path.insert(0, STUDIO)
    from studio.site_stale import scan as _stale_scan, freshness as _fresh
    for _pg, _ctx in _stale_scan(SITE):
        print(f"STALE {_pg}: ...{_ctx}...")
    for _w in _fresh(STUDIO):
        print("OLD", _w)
except Exception as _e:  # the check must never break a build
    print("stale check skipped:", _e)

print("ok", len(GUIDES))


def ping_indexnow(urls):
    """Tell Bing (and other IndexNow search engines) about new/changed pages. Free, no login. Run after the push is live."""
    import urllib.request
    body = json.dumps({"host": "vicereplay.com", "key": INDEXNOW_KEY, "keyLocation": f"{DOMAIN}/{INDEXNOW_KEY}.txt",
                       "urlList": urls}).encode()
    r = urllib.request.Request("https://api.indexnow.org/indexnow", body, {"Content-Type": "application/json; charset=utf-8"})
    return urllib.request.urlopen(r, timeout=30).status

if __name__ == "__main__" and "--ping" in __import__("sys").argv:
    print("IndexNow:", ping_indexnow([f"{DOMAIN}/{u}" for u, _ in urls]))
