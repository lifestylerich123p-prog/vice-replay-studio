"""Claim-level source ledger (owner Nov 26, Phase 6 #5: "For each material claim, record: source URL, source type,
publication date, directly inspected or search-summary-only, supporting evidence, independence from other sources,
confidence, required wording restrictions. Two websites repeating the same unverified rumor do not constitute
independent confirmation... Hold significant unsupported claims.").

An episode's "claims" list (part of the facts fingerprint, so editing it means the gate evaluates again):

  {"claim": "BALSERO is a district label on Rockstar's official map", "material": true,
   "keywords": ["Balsero"],                 # words that show the claim in the script (EN or ES)
   "evidence": [{"url": "...", "type": "official|gameplay|guide|news|real-world|wiki|community",
                 "published": "2026-11-19" | null, "checked": "direct|visual|search-summary",
                 "supports": "what the source says", "copies": "<url it repeats>" | null}],
   "confidence": "high|medium|low", "wording": "fact|hedged",
   "kind": "game|real-world"}             # real-world facts (history, sports) may rest on 2+ independent outlets

Rules (evaluate()):
  - a claim is CONFIRMED by an official source (Rockstar / platform) that we inspected directly or visually, or by 2+
    INDEPENDENT sources (different sites, not one copying the other, not both wikis/community posts) of which at
    least one was inspected directly or visually;
  - search-summary-only evidence caps confidence at "medium": such a claim must be worded "hedged" ("reportedly",
    "según", "fans say", "Rockstar hasn't confirmed") in every script line that states it;
  - a material claim with fewer than 2 independent sources and no official one is UNSUPPORTED: the gate holds the
    video (BLOCKED) until it is cut or sourced;
  - wiki/community-only claims are "theory" at best: hedged wording, never stated as fact.

    python -m studio.sources episodes/<slug>.json      # the ledger, verdict per claim, wording problems
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

OFFICIAL_HOSTS = re.compile(r"(^|\.)(rockstargames\.com|take2games\.com|playstation\.com|xbox\.com|youtube\.com/@rockstar"
                            r"|support\.google\.com|affiliate-program\.amazon\.com|ftc\.gov)$")
WEAK_TYPES = {"wiki", "community"}
INSPECTED = {"direct", "visual"}
HEDGE = re.compile(r"\b(reportedly|according to|fans?:|fans? (say|think|believe|call|compare)|rumou?r|unconfirmed|not confirmed|"
                   r"hasn'?t confirmed|may|might|seems?|appears?|theory|según|dicen|los fans|se rumorea|no (lo )?ha "
                   r"confirmado|no (lo )?confirma|parece|podría|teoría|supuestamente)(?!\w)", re.I)  # "FANS:" ends in a colon


def host(u):
    h = urlparse(u if "://" in u else "https://" + u).netloc.lower()
    return h[4:] if h.startswith("www.") else h


def independent(evidence):
    """Evidence items that count as separate confirmations: one per site, copies of another listed URL removed,
    wiki/community sources count once together."""
    urls = {e["url"] for e in evidence}
    out, sites, weak = [], set(), False
    for e in evidence:
        if e.get("copies") in urls:
            continue
        h = host(e["url"])
        if h in sites:
            continue
        if e.get("type") in WEAK_TYPES:
            if weak:
                continue
            weak = True
        sites.add(h)
        out.append(e)
    return out


def verdict(c):
    """(status, confidence, problems) for one claim."""
    ev = c.get("evidence") or []
    probs = []
    for e in ev:
        for k in ("url", "type", "checked", "supports"):
            if not e.get(k):
                probs.append(f"evidence without '{k}': {e.get('url', '?')}")
    official = [e for e in ev if OFFICIAL_HOSTS.search(host(e.get("url", ""))) or e.get("type") == "official"]
    ind = independent(ev)
    inspected = [e for e in ev if e.get("checked") in INSPECTED]
    strong = [e for e in ind if e.get("type") not in WEAK_TYPES]
    if official and any(e.get("checked") in INSPECTED for e in official):
        status, conf = "confirmed", "high"
    elif len(ind) >= 2 and all(e.get("type") in ("real-world", "news") for e in strong) and len(strong) >= 2 and \
            c.get("kind") == "real-world":
        status, conf = "confirmed", "medium"  # established real-world fact (history, sports) in 2+ independent outlets
    elif len(ind) >= 2 and len(strong) >= 1 and inspected:
        status, conf = "confirmed", "high" if len(strong) >= 2 else "medium"
    elif len(ind) >= 2 and len(strong) >= 1:
        status, conf = "reported", "medium"  # search summaries only: true per sources, but say it as reported
    elif ev and all(e.get("type") in WEAK_TYPES for e in ev):
        status, conf = "theory", "low"
    else:
        status, conf = "unsupported", "low"
    order = ["low", "medium", "high"]
    if c.get("confidence") and order.index(c["confidence"]) > order.index(conf):
        probs.append(f"confidence '{c['confidence']}' is higher than the evidence allows ('{conf}')")
    if status != "confirmed" and c.get("wording", "fact") == "fact":
        probs.append(f"{status}: must be worded as hedged (reportedly / fans say / según / no confirmado), not as fact")
    return status, conf, probs


def script_lines(ep):
    """Every line a viewer hears or reads: narration and the lettering on cards (EN and ES)."""
    for key in ("segments", "short"):
        for i, s in enumerate(ep.get(key) or []):
            for f in ("text", "text_es", "say", "say_es", "headline", "headline_es"):
                if s.get(f):
                    yield f"{key}[{i}].{f}", s[f]
            for f in ("chart", "chart_es"):
                c = s.get(f) or {}
                t = " ".join(str(x) for x in [c.get("text"), c.get("title"), c.get("sub"), *(c.get("lines") or [])] if x)
                if t:
                    yield f"{key}[{i}].{f}", t


def wording_problems(ep, c):
    """Lines that state a non-confirmed claim without a hedge (checked per line, EN and ES)."""
    if c.get("wording") != "hedged":
        return []
    kws = [k.lower() for k in c.get("keywords") or []]
    out = []
    for where, t in script_lines(ep):
        if any(k in t.lower() for k in kws) and not HEDGE.search(t):
            out.append(f"{where} states it without a hedge: {t[:70]!r}")
    return out


def evaluate(ep):
    """{"claims": [...], "blockers": [...], "advice": [...]} for the publishing gate."""
    rows, block, advice = [], [], []
    for c in ep.get("claims") or []:
        status, conf, probs = verdict(c)
        wp = wording_problems(ep, c)
        rows.append({"claim": c.get("claim"), "status": status, "confidence": conf,
                     "inspected": sum(1 for e in c.get("evidence", []) if e.get("checked") in INSPECTED),
                     "independent": len(independent(c.get("evidence") or [])), "problems": probs + wp})
        if c.get("material", True) and status == "unsupported":
            block.append(f"unsupported material claim: {c.get('claim')!r} (cut it or add 2 independent sources)")
        elif probs or wp:
            (block if c.get("material", True) else advice).extend(f"{c.get('claim')!r}: {p}" for p in probs + wp)
    return {"claims": rows, "blockers": block, "advice": advice}


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    ep = json.loads(Path(argv[0]).read_text())
    r = evaluate(ep)
    if not r["claims"]:
        print("no claim ledger in this episode (\"claims\": [...]); see python -m studio.sources --help")
    for c in r["claims"]:
        print(f"- {c['status'].upper():11} conf {c['confidence']:6} {c['independent']} independent, "
              f"{c['inspected']} inspected: {c['claim']}")
        for p in c["problems"]:
            print(f"    ! {p}")
    print("BLOCKERS:\n  " + "\n  ".join(r["blockers"]) if r["blockers"] else "no blockers")
    sys.exit(1 if r["blockers"] else 0)


if __name__ == "__main__":
    main()
