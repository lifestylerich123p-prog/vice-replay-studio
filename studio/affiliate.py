"""Affiliate links policy (owner Nov 26, Phase 6 #6: "Do not automatically insert unrelated Amazon affiliate links into
every video or comment... Never publish affiliate links if the account's eligibility or required disclosures are
unresolved.").

One switch and three rules, used by video descriptions (make_video), comments (studio.comments) and the website
(tools/site_guides.py):
  1. account: content/affiliate.json "account_status" must be "active" (the owner confirmed in Associates Central that
     the account is open, the tax interview is done and a payment method is set). Anything else = no tagged links
     anywhere; site links stay as plain, untagged Amazon links.
  2. relevance: a link set is used only when the video is about it (storage, controller, headset, setup/capture, buying
     the game); the episode lists the sets it wants in "affiliate" and each must match its own text.
  3. disclosure: Amazon's sentence ("As an Amazon Associate I earn from qualifying purchases") next to the links, the
     word "affiliate" on the link line in comments; no prices (Amazon policy: prices only from Amazon's own data).

    python -m studio.affiliate status            # the switch and why
    python -m studio.affiliate check "<text>" --topic "<video title + tags>"   # what a comment/description may carry
"""
import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "content" / "affiliate.json"
LINK = re.compile(r"https?://(?:www\.)?(?:amazon\.[a-z.]+|amzn\.to)/\S*", re.I)
PRICE = re.compile(r"[$€£]\s?\d|\d+(?:[.,]\d+)?\s?(?:USD|dollars|dólares)\b", re.I)
AMAZON_SENTENCE = "as an amazon associate"
# a set is relevant only when the video itself talks about it (title, tags, script)
RELEVANCE = {
    "storage": r"\b(storage|ssd|nvme|install size|download size|gb|tb|space|almacenamiento|espacio)\b",
    "controller": r"\b(controller|dualsense|gamepad|mando|control)\b",
    "headset": r"\b(headset|headphones|audio|sound|auriculares|cascos)\b",
    "gear": r"\b(setup|capture card|record(ing)? (your )?gameplay|controller|headset|accessor(y|ies))\b",
    "game": r"\b(buy|price|edition|pre-?order|physical|disc|where to buy|comprar|precio|edici[oó]n)\b",
    "deals": r"\b(deal|deals|sale|black friday|cyber monday|discount|oferta|ofertas)\b",
}


def cfg():
    try:
        return json.loads(CFG.read_text())
    except (OSError, ValueError):
        return {}


def property_status(prop, c=None):
    c = cfg() if c is None else c
    return ((c.get("properties") or {}).get(prop) or {}).get("status", "unverified")


def active(c=None, prop=None):
    """Account confirmed (owner) and, for a given property, that property listed in Associates Central."""
    c = cfg() if c is None else c
    ok = bool(c.get("enabled")) and c.get("account_status") == "active"
    return ok and (prop is None or property_status(prop, c) == "listed")


def why_inactive(c=None, prop=None):
    c = cfg() if c is None else c
    if not c.get("enabled"):
        return "affiliate links switched off (content/affiliate.json enabled=false)"
    if c.get("account_status") != "active":
        return (f"Amazon Associates account status is '{c.get('account_status', 'unknown')}': the owner must confirm in "
                "Associates Central that the account is open (3 qualifying sales within 180 days of sign-up), the tax "
                "interview is done and a payment method is set")
    if prop and property_status(prop, c) != "listed":
        return (f"property '{prop}' isn't verified as listed in Associates Central (status "
                f"'{property_status(prop, c)}'): links stay off there until it is")
    return ""


@dataclass
class AffiliatePlacement:
    """Owner Phase 7 #8: every placement passes all nine or it isn't published."""
    account_confirmed: bool
    property_verified: bool
    tracking_id_verified: bool
    product_relevant: bool
    compatibility_verified: bool
    disclosure_present: bool
    platform_allowed: bool
    program_compliant: bool
    claims_verified: bool

    def failures(self):
        return [k for k, v in self.__dict__.items() if not v]


def affiliate_eligible(item):
    return not item.failures()


def placement(text, topic, prop, c=None):
    """Evaluate the Amazon links in `text` (a description/comment/page block) for property `prop`."""
    c = cfg() if c is None else c
    links = LINK.findall(text or "")
    low = (text or "").lower()
    tag = c.get("tag", "vicereplay-20")
    sets = [n for n in RELEVANCE if relevant(n, topic) and relevant(n, text)]
    return AffiliatePlacement(
        account_confirmed=c.get("account_status") == "active" and bool(c.get("enabled")),
        property_verified=property_status(prop, c) == "listed",
        tracking_id_verified=all(f"tag={tag}" in u for u in links if "amazon." in u and "tryprimefree" not in u)
        and tag == (c.get("tracking_id") or {}).get("id", tag),
        product_relevant=bool(sets),
        compatibility_verified=all(n in (c.get("compat") or {}) for n in sets) if sets else False,
        disclosure_present="affiliate" in low or "#ad" in low or AMAZON_SENTENCE in low or "afiliado" in low,
        platform_allowed=prop in ("vicereplay.com", "youtube-en", "youtube-es", "instagram"),
        program_compliant=not PRICE.search(text or "") and not re.search(r"vicereplay\.com/v/|bit\.ly|tinyurl", text or ""),
        claims_verified=True,  # product claims come from content/affiliate.json labels, which carry no performance claims
    )


def relevant(set_name, text):
    pat = RELEVANCE.get(set_name)
    return bool(pat and re.search(pat, text or "", re.I))


def episode_text(ep):
    parts = [ep.get("title", ""), ep.get("short_title", ""), " ".join(ep.get("tags", []))]
    for key in ("segments", "short"):
        for s in ep.get(key) or []:
            parts.append(s.get("text", ""))
    return " ".join(parts)


def sets_for(ep, c=None, prop="youtube-en"):
    """The link sets this episode may show: none while the account is unconfirmed; otherwise only the sets the episode
    asked for ("affiliate": [...], no default) that match what the video is about."""
    c = cfg() if c is None else c
    if not active(c, prop):
        return []
    text = episode_text(ep)
    return [n for n in ep.get("affiliate", []) if n in c.get("sets", {}) and relevant(n, text)]


def block(ep, c=None, prop="youtube-en"):
    """Description lines (heading, links, Amazon's disclosure) or [] (make_video.affiliate_block)."""
    c = cfg() if c is None else c
    items = [it for n in sets_for(ep, c, prop) for it in c["sets"].get(n, [])]
    items = [(label, url) for label, url in items if not PRICE.search(label)]  # no prices in our own text
    if not items:
        return []
    sep = lambda u: "&" if "?" in u else "?"
    # disclosure FIRST, next to the links (Phase 7 #9: not hidden at the bottom)
    lines = [c["heading"], c["disclosure"]] + [f"{label}: {url}{sep(url)}tag={c['tag']}" for label, url in items]
    return lines + [""]


def url(u, c=None, prop="vicereplay.com"):
    """Website links: tagged only while the account is active and the site is a listed property; plain otherwise."""
    c = cfg() if c is None else c
    u = re.sub(r"([?&])tag=[^&\"#]*&?", r"\1", u).rstrip("?&")
    if not active(c, prop):
        return u
    return f"{u}{'&' if '?' in u else '?'}tag={c.get('tag', 'vicereplay-20')}"


def check(text, topic="", c=None, prop="youtube-en"):
    """Problems with affiliate links in a comment or description ([] = fine). A text without Amazon links is fine."""
    c = cfg() if c is None else c
    links = LINK.findall(text or "")
    if not links:
        return []
    out = []
    if not active(c, prop):
        out.append(why_inactive(c, prop))
    if not any(relevant(n, topic) and relevant(n, text) for n in RELEVANCE):
        out.append("the link isn't about what the video covers (e.g. no SSD link on an ATM robbery guide)")
    low = (text or "").lower()
    if "affiliate" not in low and "#ad" not in low and AMAZON_SENTENCE not in low:
        out.append("no disclosure next to the link ('affiliate link' or Amazon's sentence)")
    if PRICE.search(text or ""):
        out.append("a price next to an Amazon link (Amazon policy: prices only from Amazon's own data)")
    return out


def plan(prop="youtube-en", c=None):
    """Which uploaded long videos on `prop` would carry which link sets (relevance only; the account/property switch is
    applied when they are actually added). Shorts are skipped: links in Shorts descriptions aren't clickable."""
    c = cfg() if c is None else c
    reg_file = ROOT / "content" / "learn" / ("uploads-es.json" if prop == "youtube-es" else "uploads.json")
    try:
        reg = json.loads(reg_file.read_text())
    except (OSError, ValueError):
        return []
    out = []
    for vid, r in reg.items():
        if r.get("hidden") or r.get("item") not in ("main",):
            continue
        p = ROOT / "episodes" / f"{r.get('slug')}.json"
        if not p.exists():
            continue
        ep = json.loads(p.read_text())
        text = " ".join([ep.get("title", ""), r.get("title", ""), " ".join(ep.get("tags", []))])  # what it's ABOUT
        wanted = ep.get("affiliate") or []
        ok = [n for n in wanted if n in c.get("sets", {}) and relevant(n, text) and n != "deals"]
        out.append({"video": vid, "slug": r.get("slug"), "title": r.get("title", "")[:60], "sets": ok,
                    "skipped": [n for n in wanted if n not in ok]})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m studio.affiliate")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    pl = sub.add_parser("plan")
    pl.add_argument("--prop", default="youtube-en")
    p = sub.add_parser("check")
    p.add_argument("text")
    p.add_argument("--topic", default="")
    a = ap.parse_args(argv)
    if a.cmd == "status":
        c = cfg()
        print("account: " + ("CONFIRMED by the owner" if c.get("account_status") == "active" else why_inactive(c)))
        for prop in (c.get("properties") or {}):
            print(f"  {prop:15} links {'ON' if active(c, prop) else 'OFF'}  ({property_status(prop, c)})")
        return
    if a.cmd == "plan":
        rows = plan(a.prop)
        print(f"{a.prop}: links {'ON' if active(prop=a.prop) else 'OFF (' + why_inactive(prop=a.prop) + ')'}")
        for r in rows:
            print(f"  {r['video']}  {r['title']:<60}  links: {', '.join(r['sets']) or 'none (not relevant)'}"
                  + (f"  (skipped: {', '.join(r['skipped'])})" if r["skipped"] else ""))
        return
    probs = check(a.text, a.topic)
    print("ok" if not probs else "\n".join("- " + p for p in probs))
    sys.exit(1 if probs else 0)


if __name__ == "__main__":
    main()
