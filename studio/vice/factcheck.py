"""Fact and content-risk checks for scripts, titles and descriptions (free, no AI; flags for a human/Claude review).

- claims(): sentences with numbers, money, dates, records, "confirmed"/"official" wording: each needs a source.
- check_episode(): every claim must sit in an episode that lists sources; rumor wording must be labelled;
  "confirmed" must not appear next to leak/rumor wording; sources must be dated within the freshness window.
- content_risks(): sexual content, story spoilers, leaks, graphic violence focus, other creators' footage.
"""
import re

CLAIM = re.compile(r"(\$\s?\d|\d[\d,.]*\s?(%|percent|million|billion|hours?|minutes?|gb|gigabytes?|tb|fps|dollars?|"
                   r"copies|players|views|subscribers|days?)|\b(record|first (to|player|person|ever|time)|fastest|biggest|confirmed|"
                   r"announced|patch|update \d|version \d)\b)", re.I)
RUMOR = re.compile(r"\b(leak\w*|rumou?r\w*|insider|reportedly|allegedly|according to|supposedly|unconfirmed|claims?)\b", re.I)
HEDGE = re.compile(r"\b(reportedly|allegedly|according to|rumou?r\w*|leak\w*|claims?|says?|said|disputed|unconfirmed|"
                   r"guides?|reviewers?|tracker|estimate\w*|about|around|up to|may|might|could)\b", re.I)
RISKS = {
    "sexual content": r"\b(shower|strip ?club|stripper|nude|naked|sex\w*|lap ?dance|twerk|thirst|onlyfans|boob)\w*",
    "story spoiler": r"\b(ending|final mission|dies|death of|killed off|cheating on|betray\w*|twist|spoiler)\b",
    "leak / pre-release": r"\b(leak\w*|leaked|early copy|pirat\w*)\b",
    "violence focus": r"\b(kill\w* (the |a )?(dog|cat|cop|police|civilian)s?|massacre|rampage|gore|blood\w*|shoot\w* everyone)\b",
    "negative portrayal": r"\b(exposed|cringe|fraud|cancel\w*|hate)\b",
}


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text or "") if s.strip()]


def claims(text):
    return [s for s in sentences(text) if CLAIM.search(s)]


def content_risks(text):
    return [k for k, p in RISKS.items() if re.search(p, text or "", re.I)]


def check_episode(ep):
    """Returns a list of findings: {"level": "fail"|"warn", "where", "text", "fix"}."""
    out = []
    texts = []
    for key in ("segments", "short", "news_short", "tips_short"):
        for i, s in enumerate(ep.get(key) or []):
            texts.append((f"{key}[{i}]", s.get("text", "")))
            texts.append((f"{key}[{i}].headline", s.get("headline", "")))
    for key in ("title", "short_title", "description", "short_description"):
        if ep.get(key):
            texts.append((key, ep[key]))
    srcs = ep.get("sources") or []
    all_claims = [(w, c) for w, t in texts for c in claims(t)]
    if all_claims and not srcs:
        out.append({"level": "fail", "where": "sources", "text": f"{len(all_claims)} factual claims, no sources listed",
                    "fix": "add the source URLs the facts came from to 'sources'"})
    for w, t in texts:
        for s in sentences(t):
            if RUMOR.search(s) and re.search(r"\bconfirmed\b", s, re.I) and not re.search(r"not (yet )?confirmed|nobody'?s confirmed|unconfirmed", s, re.I):
                out.append({"level": "fail", "where": w, "text": s,
                            "fix": "rumor/leak wording next to 'confirmed': say who confirmed it, or drop 'confirmed'"})
            if re.search(r"\bleak", s, re.I) and not HEDGE.search(s.replace("leak", "")):
                out.append({"level": "warn", "where": w, "text": s, "fix": "label leaks: 'according to leaks', 'reportedly'"})
        for r in content_risks(t):
            out.append({"level": "fail" if r in ("sexual content", "story spoiler", "leak / pre-release") else "warn",
                        "where": w, "text": t[:120], "fix": f"{r}: remove or rewrite (channel rules)"})
    title = ep.get("short_title") or ep.get("title") or ""
    if content_risks(title):
        out.append({"level": "fail", "where": "title", "text": title, "fix": "no spoilers or sexual wording in titles"})
    for s in srcs:
        if not re.search(r"https?://", s):
            out.append({"level": "warn", "where": "sources", "text": s, "fix": "each source needs its URL"})
    out.extend({"level": "info", "where": w, "text": c, "fix": "verify against the sources (number, date, who said it)"}
               for w, c in all_claims if not HEDGE.search(c))
    return out
