"""What people search about GTA 6 right now, and which searches the website doesn't answer yet (owner, Nov 24, 2026:
"look on Google what people search for and we try to match to get traffic").

Uses the free autocomplete endpoints of Google (suggestqueries.google.com) and Bing (api.bing.com): the phrases people
are typing right now, ordered by the engine (most popular first). No volumes: rank and repetition across seeds and
engines are the signal. Each query is matched against our guides (site/guides/*.json + tools/site_guides.py titles);
unmatched ones with demand are listed as GAPS = page ideas.

    python -m studio.search_demand              # English + Spanish, writes content/learn/search-demand-<date>.md
    python -m studio.search_demand --lang en    # one language

Network: both hosts are on the environment's allowlist (Nov 24). Polite: one request at a time, small pause.
"""
import argparse
import collections
import datetime as dt
import json
import re
import string
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEEDS = {
    "en": ["gta 6", "gta 6 how", "gta 6 how to", "is gta 6", "does gta 6", "can you", "gta 6 best", "gta 6 where",
           "gta 6 when", "gta 6 why", "gta 6 what", "gta 6 cheats", "gta 6 money", "gta 6 map", "gta 6 ps5",
           "gta 6 online", "gta 6 price", "gta 6 update", "gta 6 how to get", "gta 6 how to make", "gta 6 where to find",
           "gta 6 where is", "gta 6 can you", "gta 6 is there", "gta 6 how many", "gta 6 radio", "gta 6 secret", "gta 6 easter egg"] + [f"gta 6 {c}" for c in string.ascii_lowercase],
    "es": ["gta 6", "gta 6 como", "gta 6 cuando", "gta 6 donde", "gta 6 trucos", "gta 6 dinero", "gta 6 mapa",
           "gta 6 precio", "gta 6 online", "gta 6 mejor"] + [f"gta 6 {c}" for c in "abcdefghilmnopqrstv"],
}
STOP = {"gta", "6", "vi", "the", "a", "in", "to", "is", "of", "for", "and", "on", "how", "what", "when", "where", "does",
        "can", "you", "de", "el", "la", "en", "y", "como", "cuando", "donde", "que", "para", "con", "los", "las", "un",
        "una", "es", "6?", "do", "i", "my", "it", "are", "with", "game"}


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (search-demand research)"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))


def google(q, lang):
    gl = "us" if lang == "en" else "mx"
    data = _get("https://suggestqueries.google.com/complete/search?client=firefox&hl=" + lang + "&gl=" + gl
                + "&q=" + urllib.parse.quote(q))
    return data[1] if isinstance(data, list) and len(data) > 1 else []


def bing(q, lang):
    mkt = "en-US" if lang == "en" else "es-MX"  # osjson.aspx answers 204 (empty); qsonhs.aspx returns the suggestions
    data = _get("https://api.bing.com/qsonhs.aspx?type=cb&mkt=" + mkt + "&q=" + urllib.parse.quote(q))
    out = []
    for block in (data.get("AS") or {}).get("Results") or []:
        out += [s.get("Txt", "") for s in block.get("Suggests") or []]
    return [q2 for q2 in out if q2.strip().lower() != q.strip().lower()]


def collect(lang, pause=0.25):
    """{query: score}: higher when it ranks near the top and shows up for several seeds/engines."""
    score = collections.Counter()
    for seed in SEEDS[lang]:
        for engine in (google, bing):
            try:
                rows = engine(seed + " ", lang)
            except Exception:  # noqa: BLE001 - one failed seed must not stop the run
                rows = []
            for rank, q in enumerate(rows[:10]):
                q = re.sub(r"\s+", " ", q.lower()).strip()
                if re.search(r"\bgta ?(6|vi)\b", q):
                    score[q] += 10 - rank
            time.sleep(pause)
    return score


def our_pages():
    """[(path, words)] for every guide we have, from the JSON guides and the titles in tools/site_guides.py."""
    pages = []
    for f in (ROOT / "site" / "guides").glob("*.json"):
        g = json.loads(f.read_text())
        base = "es/guias" if g.get("lang") == "es" else "guides"
        pages.append((f"/{base}/{g['slug']}/", f"{g['slug']} {g.get('title', '')} {g.get('desc', '')}".lower()))
    src = (ROOT / "tools" / "site_guides.py").read_text()
    for m in re.finditer(r'guide\("([a-z0-9-]+)", "([^"]+)",\s*\n?\s*"([^"]+)"', src):
        pages.append((f"/guides/{m.group(1)}/", f"{m.group(1)} {m.group(2)} {m.group(3)}".lower()))
    return pages


def keywords(q):
    return [w for w in re.findall(r"[a-záéíóúñ0-9$]+", q.lower()) if w not in STOP and len(w) > 1]


def best_match(q, pages):
    """The page whose slug/title/desc contains the most of the query's key words (all of them = covered)."""
    kw = keywords(q)
    if not kw:
        return None, 1.0
    best, frac = None, 0.0
    for path, words in pages:
        hit = sum(1 for w in kw if w in words) / len(kw)
        if hit > frac:
            best, frac = path, hit
    return best, frac


def report(langs=("en", "es"), top=60):
    pages = our_pages()
    today = dt.date.today().isoformat()
    lines = [f"# GTA 6 search demand ({today}, `python -m studio.search_demand`)", "",
             "Google + Bing autocomplete (US English, Mexico Spanish). Score = rank weight summed across seeds and engines:",
             "a rough popularity order, not search volume. COVERED = a page of ours has every key word; GAP = page idea.", ""]
    gaps_all = []
    for lang in langs:
        score = collect(lang)
        rows = score.most_common(top)
        lines += [f"## {'English' if lang == 'en' else 'Spanish'}: top {len(rows)} searches", "",
                  "| # | Search | Score | Our page |", "|---|---|---|---|"]
        for i, (q, s) in enumerate(rows, 1):
            page, frac = best_match(q, pages)
            mark = f"COVERED {page}" if frac >= 0.99 else (f"partly {page}" if frac >= 0.5 else "**GAP**")
            if frac < 0.5:
                gaps_all.append((lang, q, s))
            lines.append(f"| {i} | {q} | {s} | {mark} |")
        lines.append("")
    lines += ["## Gaps (no page answers these yet), most searched first", ""]
    lines += [f"- [{lang}] {q} ({s})" for lang, q, s in sorted(gaps_all, key=lambda x: -x[2])]
    out = ROOT / "content" / "learn" / f"search-demand-{today}.md"
    out.write_text("\n".join(lines) + "\n")
    return out, gaps_all


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=["en", "es"])
    a = ap.parse_args()
    path, gaps = report((a.lang,) if a.lang else ("en", "es"))
    print(path)
    for lang, q, s in sorted(gaps, key=lambda x: -x[2])[:25]:
        print(f"GAP [{lang}] {q} ({s})")
