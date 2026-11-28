"""Website check (owner Nov 28 #7, "automated website maintenance"): free, local, read-only audit of the built site
(../vicereplay-site) and the map pins. Deterministic: no AI, no paid calls.

    python -m studio.sitecheck          # PROBLEMS (fix before publishing) + WARNINGS; exit 1 when there are problems
    python -m studio.sitecheck --live   # also: home, Spanish home, sitemap and 5 sitemap pages answer 200 (uptime)

Checks: internal links and images resolve; one canonical per page and its target exists; hreflang targets exist and
point back; sitemap URLs exist and every indexable page is listed; title, meta description and viewport present, no
duplicate titles; JSON-LD parses; Amazon links are direct amazon.com links with tag vicereplay-20 on a page carrying
the disclosure; target=_blank links have rel=noopener; scripts only from our site or Cloudflare's beacon; no
secret-looking strings in published files; no claim a video fact-check cut (content/learn/cut-claims.json); site checkout clean (rollback = its git history); map pins use a known
category and 2+ sources unless the place is printed on Rockstar's official map. Freshness (pre-launch wording, deal
prices, expired deal pages) stays in studio.site_stale. Result: content/learn/sitecheck.json (the daily report reads it).
"""
import html
import json
import os
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = Path(os.environ.get("VICEREPLAY_SITE") or ROOT.parent / "vicereplay-site")
PINS = ROOT / "site" / "map-pins.json"
OUT = ROOT / "content" / "learn" / "sitecheck.json"
DOMAIN = "https://vicereplay.com"
TAG = "vicereplay-20"
SCRIPT_HOSTS = {"static.cloudflareinsights.com"}
SECRET = re.compile(r"AIza[0-9A-Za-z_\-]{35}|sk-[A-Za-z0-9_\-]{20,}|ghp_[A-Za-z0-9]{36}|gh[ousr]_[A-Za-z0-9]{36}"
                    r"|-----BEGIN [A-Z ]*PRIVATE KEY|\"refresh_token\"\s*:|\bEAA[A-Za-z0-9]{40,}")
DISCLOSURE = ("Amazon Associate", "afiliado de Amazon")


def url_of(rel):
    """Site path of a file: index.html -> /, guides/x/index.html -> /guides/x/, 404.html -> /404.html."""
    rel = rel.replace(os.sep, "/")
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def exists(site, path):
    path = urllib.parse.unquote(path.split("#")[0].split("?")[0])
    if not path or path == "/":
        return (site / "index.html").exists()
    p = site / path.lstrip("/")
    return (p / "index.html").exists() if path.endswith("/") else (p.is_file() or (p / "index.html").exists())


def _internal(href, page_url):
    """Site path for an internal link, None for external/mailto/anchors."""
    href = html.unescape(href.strip())
    if not href or href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    if href.startswith(DOMAIN):
        return href[len(DOMAIN):] or "/"
    if href.startswith(("http://", "https://", "//")):
        return None
    if href.startswith("/"):
        return href
    return urllib.parse.urljoin(page_url, href)  # relative link


def check_site(site=SITE):
    problems, warnings = [], []
    pages = {}
    for f in sorted(site.rglob("*.html")):
        rel = str(f.relative_to(site))
        if rel.startswith(".git"):
            continue
        pages[url_of(rel)] = f.read_text(errors="ignore")
    titles = {}
    canon = {}
    alts = {}
    indexable = set()
    for url, doc in pages.items():
        redirect = url.startswith("/v/") or 'http-equiv="refresh"' in doc
        noindex = re.search(r'<meta name="robots" content="[^"]*noindex', doc) is not None
        for attr, href in re.findall(r'\s(href|src)="([^"]*)"', doc):
            path = _internal(href, url)
            if path and not exists(site, path):
                problems.append(f"broken link {url} -> {href}")
        for href in re.findall(r'<a\s[^>]*href="(https?://[^"]*(?:amazon\.|amzn\.)[^"]*)"', doc):
            h = html.unescape(href)
            if "/gp/help/" in h:  # Amazon's own help/policy pages (privacy page): information, not an affiliate link
                continue
            if not re.match(r"https://(www\.)?amazon\.com/", h):
                problems.append(f"affiliate link not a direct amazon.com link on {url}: {h[:80]}")
            elif f"tag={TAG}" not in h:
                problems.append(f"Amazon link without tag={TAG} on {url}: {h[:80]}")
            if not any(d in doc for d in DISCLOSURE):
                problems.append(f"Amazon link without the affiliate disclosure on {url}")
        for tag in re.findall(r"<a\s[^>]*target=\"_blank\"[^>]*>", doc):
            if "noopener" not in tag:
                warnings.append(f"target=_blank without rel=noopener on {url}")
                break
        for src in re.findall(r'<script[^>]*\ssrc="([^"]+)"', doc):
            host = urllib.parse.urlparse(src).hostname
            if host and host not in SCRIPT_HOSTS and not src.startswith(DOMAIN):
                problems.append(f"script from an unexpected host on {url}: {src[:80]}")
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', doc, re.S):
            try:
                json.loads(block)
            except ValueError:
                problems.append(f"structured data (JSON-LD) does not parse on {url}")
        if redirect or url == "/404.html":
            continue
        if 'name="viewport"' not in doc:
            problems.append(f"no viewport meta (mobile) on {url}")
        t = re.search(r"<title>(.*?)</title>", doc, re.S)
        if not t:
            problems.append(f"no <title> on {url}")
        else:
            title = html.unescape(t.group(1).strip())
            titles.setdefault(title, []).append(url)
            if len(title) > 70:
                warnings.append(f"title over 70 characters on {url} ({len(title)})")
        if not re.search(r'<meta name="description" content="[^"]+', doc):
            warnings.append(f"no meta description on {url}")
        cs = re.findall(r'<link rel="canonical" href="([^"]+)"', doc)
        if len(cs) != 1:
            problems.append(f"{len(cs)} canonical tags on {url}")
        elif not cs[0].startswith(DOMAIN) or not exists(site, cs[0][len(DOMAIN):]):
            problems.append(f"canonical of {url} points to a missing page: {cs[0]}")
        else:
            canon[url] = cs[0][len(DOMAIN):] or "/"
        alts[url] = re.findall(r'<link rel="alternate" hreflang="([\w-]+)" href="([^"]+)"', doc)
        if not noindex and canon.get(url) == url:
            indexable.add(url)
    for title, urls in titles.items():
        if len(urls) > 1:
            warnings.append(f"duplicate title on {len(urls)} pages: {title[:60]} ({', '.join(urls[:3])})")
    for url, pairs in alts.items():
        for lang, href in pairs:
            if not href.startswith(DOMAIN):
                problems.append(f"hreflang {lang} on {url} is not an absolute vicereplay.com URL: {href}")
                continue
            target = href[len(DOMAIN):] or "/"
            if not exists(site, target):
                problems.append(f"hreflang {lang} on {url} points to a missing page: {href}")
            elif lang != "x-default" and target != url and target in alts and canon.get(url) == url:
                if not any(h == DOMAIN + url for _, h in alts[target]):
                    problems.append(f"hreflang not reciprocal: {url} -> {target} (no link back)")
    sm = site / "sitemap.xml"
    listed = set()
    if not sm.exists():
        problems.append("sitemap.xml missing")
    else:
        for loc in re.findall(r"<loc>(.*?)</loc>", sm.read_text()):
            path = loc.strip()[len(DOMAIN):] or "/"
            listed.add(path)
            if not exists(site, path):
                problems.append(f"sitemap lists a missing page: {loc}")
        for url in sorted(indexable - listed):
            warnings.append(f"indexable page not in sitemap.xml: {url}")
    cut = ROOT / "content" / "learn" / "cut-claims.json"  # claims a video fact-check had to drop
    phrases = [c["phrase"] for c in json.loads(cut.read_text()).get("claims", [])] if cut.exists() else []
    for url, doc in pages.items():
        text = html.unescape(re.sub(r"<[^>]+>", " ", doc)).lower()
        for ph in phrases:
            if ph.lower() in text:
                problems.append(f"cut claim still on the site: {ph!r} on {url} (content/learn/cut-claims.json)")
    for f in site.rglob("*"):
        if f.is_file() and ".git" not in f.parts and f.suffix in (".html", ".js", ".json", ".xml", ".txt", ".css"):
            if SECRET.search(f.read_text(errors="ignore")):
                problems.append(f"secret-looking string in a published file: {f.relative_to(site)}")
    return {"pages": len(pages), "indexable": len(indexable), "sitemap": len(listed),
            "problems": problems, "warnings": warnings}


def check_pins(pins_file=PINS):
    out = []
    data = json.loads(pins_file.read_text())
    cats = {c["id"] for c in data.get("cats", [])}
    for p in data.get("pins", []):
        name = p.get("en", {}).get("t") or p.get("at")
        if p.get("cat") not in cats:
            out.append(f"map pin {name}: unknown category {p.get('cat')}")
        src = p.get("src") or []
        official = any("Rockstar" in s for s in src)
        if len(src) < 2 and not official:
            out.append(f"map pin {name}: {len(src)} source(s), needs 2+ guides (or move it to unconfirmed)")
        if not p.get("es", {}).get("t"):
            out.append(f"map pin {name}: no Spanish text")
    return out


def checkout_state(site=SITE):
    try:
        dirty = subprocess.run(["git", "-C", str(site), "status", "--porcelain"], capture_output=True, text=True,
                               timeout=30).stdout.strip()
        head = subprocess.run(["git", "-C", str(site), "rev-parse", "--short=12", "HEAD"], capture_output=True,
                              text=True, timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None, "site checkout: git not readable"
    return head, (f"site checkout has uncommitted changes ({len(dirty.splitlines())} file(s)): publish or discard them"
                  if dirty else None)


def live(n=5):
    import urllib.request
    paths = ["/", "/es/", "/sitemap.xml"]
    try:
        with urllib.request.urlopen(DOMAIN + "/sitemap.xml", timeout=30) as r:
            locs = re.findall(r"<loc>(.*?)</loc>", r.read().decode(errors="ignore"))
        step = max(1, len(locs) // n)
        paths += [loc[len(DOMAIN):] for loc in locs[::step][:n]]
    except OSError:
        pass
    bad = []
    for p in paths:
        try:
            with urllib.request.urlopen(urllib.request.Request(DOMAIN + p, headers={"User-Agent": "sitecheck"}),
                                        timeout=30) as r:
                if r.status != 200:
                    bad.append(f"{p} answered {r.status}")
        except OSError as e:
            bad.append(f"{p} failed: {str(e)[:80]}")
    return len(paths), bad


def main(argv=None):
    import datetime as dt
    argv = sys.argv[1:] if argv is None else argv
    r = check_site()
    r["warnings"] += check_pins()
    head, dirty = checkout_state()
    r["site_commit"] = head
    if dirty:
        r["warnings"].append(dirty)
    if "--live" in argv:
        n, bad = live()
        r["live_checked"], r["live_failed"] = n, bad
        r["problems"] += [f"live: {b}" for b in bad]
    r["checked_at"] = dt.datetime.now().isoformat(timespec="minutes")
    OUT.write_text(json.dumps(r, indent=1, ensure_ascii=False))
    print(f"Website: {r['pages']} pages, {r['indexable']} indexable, {r['sitemap']} in sitemap, commit {head}"
          + (f", live {r['live_checked'] - len(r['live_failed'])}/{r['live_checked']} OK" if "live_checked" in r else ""))
    for p in r["problems"]:
        print("PROBLEM", p)
    for w in r["warnings"][:40]:
        print("warn", w)
    if len(r["warnings"]) > 40:
        print(f"... {len(r['warnings']) - 40} more warnings in {OUT.relative_to(ROOT)}")
    print(f"{len(r['problems'])} problem(s), {len(r['warnings'])} warning(s)")
    return 1 if r["problems"] else 0


if __name__ == "__main__":
    sys.exit(main())
