"""Video -> website links that can be measured (owner Nov 26, Phase 5 #10: "Track referral sources using appropriate
campaign parameters and privacy-compliant analytics... Use real data rather than estimating conversions").

The site's Cloudflare Web Analytics is cookieless and reports pages by PATH (query strings are dropped), so each Short
gets its own short path: https://vicereplay.com/v/<slug>/ (Spanish: /v/<slug>-es/). That page counts the visit,
then forwards to the guide or map spot with utm_source/medium/campaign kept on the target (for any future analytics).
It is noindex and canonical to the target, so it never competes in search.

    python -m studio.sitelinks build      # writes ../vicereplay-site/v/<slug>/index.html for every linked episode

Which episodes get one: location / map_tutorial / secrets Shorts (studio.mix categories) or any with "site_target".
"""
import html
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = "https://vicereplay.com"
SITE = Path(os.environ.get("VICEREPLAY_SITE") or ROOT.parent / "vicereplay-site")
DEFAULT = {"en": "/guides/gta-6-map-leonida-places/", "es": "/es/guias/mapa-gta-6/"}
BEACON = ("<script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' "
          "data-cf-beacon='{\"token\": \"4c4c637dcde8478da5fd7073dcde1b11\"}'></script>")


def wants_link(ep):
    from . import mix
    return bool(ep.get("site_target")) or mix.category(ep) in ("location", "map_tutorial", "secrets")


def target(ep, lang):
    t = ep.get("site_target_es" if lang == "es" else "site_target")
    if isinstance(t, str) and t:
        return t
    return DEFAULT[lang]


def short_path(slug, lang):
    return f"/v/{slug}{'-es' if lang == 'es' else ''}/"


def link(ep, lang):
    """The URL to print in a Short's description, or None."""
    return DOMAIN + short_path(ep["slug"], lang) if wants_link(ep) else None


def line(ep, lang):
    url = link(ep, lang)
    if not url:
        return None
    return (f"📍 Guía completa y mapa interactivo: {url}" if lang == "es" else
            f"📍 Full guide + interactive map: {url}")


def page(ep, lang):
    tgt = target(ep, lang)
    sep = "&" if "?" in tgt else "?"
    base, frag = (tgt.split("#", 1) + [""])[:2]
    dest = f"{base}{sep}utm_source=youtube&utm_medium=short&utm_campaign={ep['slug']}{'-es' if lang == 'es' else ''}"
    dest += f"#{frag}" if frag else ""
    title = html.escape((ep.get("short_es") or {}).get("title") if lang == "es" else ep.get("short_title") or "")
    msg = "Abriendo la guía…" if lang == "es" else "Opening the guide…"
    d = html.escape(dest, quote=True)
    return (f"<!doctype html><html lang=\"{lang}\"><head><meta charset=\"utf-8\">"
            f"<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><meta name=\"robots\" content=\"noindex\">"
            f"<link rel=\"canonical\" href=\"{DOMAIN}{html.escape(base)}\"><title>{title}</title>"
            f"<meta http-equiv=\"refresh\" content=\"2;url={d}\">{BEACON}</head>"
            f"<body style=\"background:#0d0717;color:#f4eefc;font-family:sans-serif;padding:40px\">"
            f"<p>{msg} <a style=\"color:#00e5d2\" href=\"{d}\">{html.escape(DOMAIN + base)}</a></p>"
            f"<script>setTimeout(function(){{location.replace({json.dumps(dest)})}},600)</script></body></html>")


def build(site=SITE):
    n = 0
    for p in sorted((ROOT / "episodes").glob("*.json")):
        try:
            ep = json.loads(p.read_text())
        except ValueError:
            continue
        if not ep.get("short") or not wants_link(ep):
            continue
        for lang in ("en", "es"):
            if lang == "es" and not (ep.get("short_es") or {}).get("title"):
                continue
            out = Path(site) / short_path(ep["slug"], lang).strip("/") / "index.html"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(page(ep, lang))
            n += 1
    return n


if __name__ == "__main__":
    if sys.argv[1:2] == ["build"]:
        print(f"{build()} short-link pages -> {SITE}/v/")
