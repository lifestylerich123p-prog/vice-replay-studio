"""Fact and content-risk checks for scripts, titles and descriptions (free, no AI; flags for a human/Claude review).

- claims(): sentences with numbers, money, dates, records, "confirmed"/"official" wording: each needs a source.
- check_episode(): every claim must sit in an episode that lists sources; rumor wording must be labelled;
  "confirmed" must not appear next to leak/rumor wording; sources must be dated within the freshness window.
- content_risks(): sexual content, story spoilers, leaks, graphic violence focus, other creators' footage.
"""
import json
import re

CLAIM = re.compile(r"(\$\s?\d|\d[\d,.]*\s?(%|percent|million|billion|hours?|minutes?|gb|gigabytes?|tb|fps|dollars?|"
                   r"copies|players|views|subscribers|days?)|\b(record|first (to|player|person|ever|time)|fastest|biggest|confirmed|"
                   r"announced|patch|update \d|version \d)\b)", re.I)
RUMOR = re.compile(r"\b(leak\w*|rumou?r\w*|insiders?|reportedly|allegedly|according to|supposedly|unconfirmed|claims?)\b", re.I)
HEDGE = re.compile(r"\b(reportedly|allegedly|according to|rumou?r\w*|leak\w*|claims?|says?|said|disputed|unconfirmed|"
                   r"guides?|reviewers?|tracker|estimate\w*|about|around|up to|may|might|could)\b", re.I)
RISKS = {
    "sexual content": r"\b(shower|strip ?club|stripper|nude|naked|sex\w*|lap ?dance|twerk|thirst|onlyfans|boob)\w*",
    "story spoiler": r"\b(ending|final mission|dies|death of|killed off|cheating on|betray\w*|twist|spoiler)\b",
    "leak / pre-release": r"\b(early copy|pirat\w*|datamin\w*)\b",  # "leak" words: classify_leak() (context)
    "violence focus": r"\b(kill\w* (the |a )?(dog|cat|cop|police|civilian)s?|massacre|rampage|gore|blood\w*|shoot\w* everyone)\b",
    "negative portrayal": r"\b(exposed|cringe|fraud|cancel\w*|hate)\b",
}


# Phase 3 #11 (Nov 26: "green ooze leaks through a crack" was blocked as a game leak): "leak" words are classified by
# their context instead of matched blindly. Physical leaks (liquid, gas, a pipe...) and words inside in-game dialogue or
# parody are not information leaks; anything else stays treated as one (fail closed: precision, not a weaker check).
LEAK = re.compile(r"\b(leak\w*|leaker\w*)\b", re.I)
PHYSICAL = re.compile(r"\b(water|ooze|slime|goo|mutagen|liquid|fluid|oil|gas|fuel|petrol|gasoline|acid|sewage|sewer|"
                      r"drain|pipe\w*|roof|ceiling|tank|hull|boat|tire|tyre|valve|hose|faucet|radiator|blood|juice|"
                      r"crack\w*|drip\w*|puddle|flood\w*|toxic|chemical\w*|barrel\w*|bucket)\b", re.I)
PHYS_IDIOM = re.compile(r"\b(springs? a leak|leak-?proof|leak(s|ing|ed)? (out of|through|from|into|onto) the "
                        r"(pipe|tank|hull|roof|wall|ceiling|crack|floor|barrel|boat))\b", re.I)
INFO = re.compile(r"\b(footage|video\w*|build|source code|code|map|trailer|screenshot\w*|document\w*|info\w*|"
                  r"details?|data|release date|dlc|online|insider\w*|leaker\w*|rumou?r\w*|reveal\w*|"
                  r"pre-?release|announce\w*|gta ?(6|vi|7)|rockstar|take-?two|ps5|pc (port|version)|update|patch)\b",
                  re.I)
FICTION = re.compile(r"\b(in-game|radio (host|show|station|ad)|npc|parody|satir\w*|spoof|fake ad|weazel|"
                     r"(jason|lucia|a character|the character|the host|the dj) (says|said|yells|jokes))\b", re.I)


def _near(text, start, end, pattern, span=45):
    return pattern.search(text[max(0, start - span):end + span]) is not None


def classify_leak(sentence):
    """'physical' | 'fiction' | 'info' | None (no leak word). Unknown context counts as 'info' (fail closed)."""
    m = LEAK.search(sentence or "")
    if not m:
        return None
    quoted = [q.span() for q in re.finditer(r'"[^"]+"|“[^”]+”', sentence)]
    in_quote = any(a <= m.start() < b for a, b in quoted)
    if in_quote and FICTION.search(sentence):
        return "fiction"
    if PHYS_IDIOM.search(sentence) or (_near(sentence, m.start(), m.end(), PHYSICAL)
                                        and not _near(sentence, m.start(), m.end(), INFO, 25)):
        return "physical"
    return "info"


def leak_risk(text):
    """True when the text talks about leaked game information (not a dripping pipe, not a line of in-game dialogue)."""
    return any(classify_leak(s) == "info" for s in sentences(text) if LEAK.search(s))


# Phase 3 #12: claims about these topics must say what kind of claim they are (episode "claim_status")
SENSITIVE = re.compile(r"\b(bigfoot|sasquatch|skunk ape|ufo|alien\w*|ghost\w*|secret (mission|room|area|ending|"
                       r"level|island|boss)|hidden (room|area|mission|island|level)|crossover|easter eggs?|"
                       r"unreleased|cut content|coming soon|update \d|patch|hotfix|coordinates|performance mode|"
                       r"\d+ ?fps|frame ?rate|pc (version|port|release)|on pc)\b", re.I)
CLAIM_KINDS = {
    "confirmed": "Rockstar / the platform said it (needs an official source: rockstargames.com, support.rockstargames.com,"
                 " take2games.com, blog.playstation.com, news.xbox.com)",
    "community-found": "players found it in the game (2+ independent guides from different sites)",
    "theory": "unproven: the script says theory / players think / unconfirmed",
    "hypothetical": "a what-if: the script says what if / imagine, never 'confirmed'",
    "fiction": "in-game fiction (radio, ads, dialogue), presented as such",
}
OFFICIAL = re.compile(r"rockstargames\.com|support\.rockstargames|take2games\.com|blog\.playstation\.com|"
                      r"news\.xbox\.com|store\.playstation\.com", re.I)
THEORY_WORDS = re.compile(r"\b(theor\w*|players think|fans think|unconfirmed|might|may be|could be|rumou?r\w*|"
                          r"teor[ií]a|podr[ií]a|sin confirmar)\b", re.I)
WHATIF_WORDS = re.compile(r"\b(what if|imagine|qu[eé] pasar[ií]a|imagina)\b", re.I)


def _domains(srcs):
    out = set()
    for s in srcs:
        m = re.search(r"https?://(?:www\.)?([^/\s]+)", s)
        if m:
            out.add(m.group(1).lower())
    return out


def check_claims(ep, texts):
    """Sensitive topics need a labelled claim status that matches the sources and the wording."""
    allt = " ".join(t for _, t in texts)
    hit = SENSITIVE.search(allt)
    if not hit:
        return []
    kind = ep.get("claim_status")
    srcs = ep.get("sources") or []
    if kind not in CLAIM_KINDS:
        return [{"level": "fail", "where": "claim_status", "text": f"sensitive topic ({hit.group(0)!r}) without a claim status",
                 "fix": "set \"claim_status\" to one of: " + "; ".join(f"{k} = {v}" for k, v in CLAIM_KINDS.items())}]
    out = []
    if kind == "confirmed" and not any(OFFICIAL.search(x) for x in srcs):
        out.append({"level": "fail", "where": "claim_status", "text": "confirmed, but no official source",
                    "fix": CLAIM_KINDS["confirmed"]})
    if kind == "community-found" and len(_domains(srcs)) < 2:
        out.append({"level": "fail", "where": "claim_status", "text": "community-found needs 2+ guides from different sites",
                    "fix": CLAIM_KINDS["community-found"]})
    if kind == "theory" and not THEORY_WORDS.search(allt):
        out.append({"level": "fail", "where": "claim_status", "text": "a theory presented without theory wording",
                    "fix": CLAIM_KINDS["theory"]})
    if kind == "hypothetical" and (not WHATIF_WORDS.search(allt) or re.search(r"\bconfirm", allt, re.I)):
        out.append({"level": "fail", "where": "claim_status", "text": "a hypothetical must say what-if and never 'confirmed'",
                    "fix": CLAIM_KINDS["hypothetical"]})
    for key in ("segments", "short"):
        for i, s in enumerate(ep.get(key) or []):
            if (s.get("ai_image") or "media/ai/" in json.dumps(s)) and not ep.get("ai_visuals_labelled"):
                out.append({"level": "fail", "where": f"{key}[{i}]", "text": "AI-generated picture without a label",
                            "fix": "AI visuals are never shown as gameplay: label them on screen and set "
                                   "\"ai_visuals_labelled\": true"})
    return out


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text or "") if s.strip()]


def claims(text):
    return [s for s in sentences(text) if CLAIM.search(s)]


def content_risks(text):
    out = [k for k, p in RISKS.items() if re.search(p, text or "", re.I)]
    if "leak / pre-release" not in out and leak_risk(text):
        out.append("leak / pre-release")
    return out


SPOILER_REVEAL = re.compile(r"\b(ending|final mission|dies|death of|killed off|cheating on|betray\w*|twist)\b", re.I)


def check_episode(ep):
    """Returns a list of findings: {"level": "fail"|"warn", "where", "text", "fix"}.

    Owner Nov 24 ("put spoiler and leaks to get viewers in"; content/owner.md): an episode may set "spoilers_ok"
    (a warned, chaptered spoiler round) and/or "leaks_ok" (leaks covered as labeled, reported news; never leaked
    footage). Then those words in the script are warnings, not blockers. A title or thumbnail may say "spoilers"
    but never reveal one: ending/dies/twist/betrayal wording in a title still fails."""
    ok_spoil, ok_leak = bool(ep.get("spoilers_ok")), bool(ep.get("leaks_ok"))
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
            if classify_leak(s) == "info" and not HEDGE.search(s.replace("leak", "")):
                out.append({"level": "warn", "where": w, "text": s, "fix": "label leaks: 'according to leaks', 'reportedly'"})
        for r in content_risks(t):
            allowed = (r == "story spoiler" and ok_spoil) or (r == "leak / pre-release" and ok_leak)
            out.append({"level": "fail" if r in ("sexual content", "story spoiler", "leak / pre-release") and not allowed
                        else "warn", "where": w, "text": t[:120],
                        "fix": f"{r}: {'allowed for this episode (owner); keep it warned/labeled' if allowed else 'remove or rewrite (channel rules)'}"})
    title = ep.get("short_title") or ep.get("title") or ""
    risks = content_risks(title)
    if ok_spoil and "story spoiler" in risks and not SPOILER_REVEAL.search(title):
        risks.remove("story spoiler")  # the word "spoilers" may sell the video; a revealed spoiler may not
    if ok_leak and "leak / pre-release" in risks:
        risks.remove("leak / pre-release")
    if risks:
        out.append({"level": "fail", "where": "title", "text": title, "fix": "no spoilers or sexual wording in titles"})
    out.extend(check_claims(ep, texts))
    for s in srcs:
        if not re.search(r"https?://", s):
            out.append({"level": "warn", "where": "sources", "text": s, "fix": "each source needs its URL"})
    out.extend({"level": "info", "where": w, "text": c, "fix": "verify against the sources (number, date, who said it)"}
               for w, c in all_claims if not HEDGE.search(c))
    return out
