"""Follow-up opportunities from what's working (owner Nov 26, Phase 3 #4: "When a video performs significantly above
the channel baseline, automatically identify related topics... Check the episode database before creating any
follow-up. Never generate a duplicate simply because an earlier video succeeded").

    python -m studio.opportunities            # winners (3x+ their matched baseline) and their follow-up topics
    python -m studio.opportunities --json

How a winner is found (per platform, never mixed):
* YouTube (our English channel): views at the same age (min(age, 24 h), from content/learn/history.jsonl) vs the
  median of our other Shorts from the last 14 days at that age; same card format (map vs other) when 3+ exist.
* TikTok (Windsor pulls, content/learn/tiktok-*.json): views vs the median of TikToks posted 1-14 days earlier
  (no hourly history there, so only videos 24 h+ old count).
* Sufficient data: YouTube age >= 3 h and 3+ comparable Shorts; TikTok age >= 24 h and 3+ comparable posts.
Follow-ups come from content/learn/map-candidates.json (kept by the map intelligence agent,
.claude/agents/vice-replay-map-intelligence.md): same family, not already produced (episode database: slugs,
titles and keywords), facts verified (status "verified" + 2+ source sites), relevant to the language, within budget
(0 paid credits unless the owner said otherwise). Unverified ones are listed as "research next".
"""
import argparse
import datetime as dt
import json
import re
import statistics
from pathlib import Path

from . import scorecard

ROOT = Path(__file__).resolve().parent.parent
LEARN = ROOT / "content" / "learn"
CANDIDATES = LEARN / "map-candidates.json"
OUT = LEARN / "opportunities.json"
RATIO = 3.0


def _now():
    return dt.datetime.now(dt.timezone.utc)


def load_candidates(path=None):
    try:
        return json.loads(Path(path or CANDIDATES).read_text())
    except (OSError, ValueError):
        return {"families": {}, "candidates": []}


def family_of(text, families):
    """The family whose keywords appear most in the text (None if none)."""
    text = (text or "").lower()
    best, hits = None, 0
    for name, f in families.items():
        n = sum(1 for k in f.get("keywords", []) if re.search(r"\b" + re.escape(k.lower()), text))
        if n > hits:
            best, hits = name, n
    return best


def episode_index(root=None):
    """Every episode's slug + titles + script words, to spot topics we already made."""
    out = []
    for p in sorted(Path(root or ROOT / "episodes").glob("*.json")):
        try:
            ep = json.loads(p.read_text())
        except ValueError:
            continue
        head = " ".join([ep.get("slug", p.stem).replace("-", " "), ep.get("title", ""), ep.get("short_title", ""),
                         (ep.get("short_es") or {}).get("title", "")]).lower()
        script = " ".join(s.get("text", "") for s in ep.get("short") or []).lower()
        out.append((ep.get("slug", p.stem), head, script))
    return out


def _keys(cand):
    return [k for k in [cand["key"].replace("-", " ")] + [k.lower() for k in cand.get("keywords", [])] if k]


def already_produced(cand, index):
    """Done when an episode's slug or title names the topic (a passing mention in a script is only 'related')."""
    for slug, head, _ in index:
        if any(re.search(r"\b" + re.escape(k), head) for k in _keys(cand)):
            return slug
    return None


def related(cand, index):
    return [slug for slug, head, script in index if any(re.search(r"\b" + re.escape(k), script) for k in _keys(cand))]


def _domains(srcs):
    return {m.group(1).lower() for s in srcs or [] for m in [re.search(r"https?://(?:www\.)?([^/\s]+)", s)] if m}


def evaluate_follow_up(winner, candidates, index, budget_credits=0, lang="en"):
    """The directive's rule, on our data: only for a real winner; never a duplicate; verified facts; right audience;
    within budget. Returns (ready, research_next)."""
    if not winner.get("sufficient") or not winner.get("baseline") or winner.get("ratio", 0) < RATIO:
        return [], []
    ready, research = [], []
    for c in candidates:
        if c.get("family") != winner.get("family") or c.get("status") in ("rejected",):
            continue
        dup = already_produced(c, index)
        if dup or c.get("status") == "produced":
            continue
        if lang not in c.get("langs", ["en", "es"]) or c.get("credits", 0) > budget_credits:
            continue
        verified = c.get("status") == "verified" and len(_domains(c.get("sources"))) >= 2
        (ready if verified else research).append(c)
    return ready, research


# ---------- weighted score (owner Nov 26, Phase 4 #13) ----------
# Every input is normalized to 0..1 (documented below); the weights are the owner's starting point, NOT validated:
# calibrate them against real results (content/learn/xplat.json) before trusting small differences.
from dataclasses import dataclass, field

# Owner Phase 7 #21 starting weights (sum 1.0; uncalibrated: re-fit once 20+ follow-ups have 72 h results).
WEIGHTS = {"search_demand": 0.17, "relative_performance": 0.17, "audience_relevance": 0.14, "visual_potential": 0.12,
           "asset_availability": 0.10, "originality": 0.10, "timeliness": 0.08, "website_value": 0.07,
           "monetization_relevance": 0.05}
COST_WEIGHT = 0.5  # cost (0..1 = Everygen credits / 20, capped) costs up to half a point: zero-credit work wins ties


@dataclass
class Opportunity:
    search_demand: float          # 0..1: YouTube search-terms views for its phrases / 200 (capped); 0.3 = hypothesis only
    relative_performance: float   # 0..1: the winner it follows, ratio vs matched baseline / 10 (capped); 0 if none
    audience_relevance: float     # 0..1: both languages 1.0, one 0.7
    originality: float            # 0..1: 1.0 new, 0.6 when existing Shorts already mention it
    visual_potential: float       # 0..1: a map place/grid known 0.8 (+0.2 with a site demo), else 0.5
    asset_availability: float     # 0..1: our own assets cover it (map, cards, site) 1.0, needs footage 0.3
    timeliness: float             # 0..1: winner < 48 h old 1.0, < 7 days 0.6, else 0.3
    estimated_credit_cost: float  # 0..1: production_cost(): credits, minutes, licensing, upkeep, rendering
    facts_verified: bool
    duplicate: bool
    rights_verified: bool
    evidence: dict = field(default_factory=dict)  # where each input came from: analytics / research / hypothesis
    website_value: float = 0.3          # 0..1: becomes a map pin / guide on vicereplay.com 1.0, a pin-able place 0.8
    monetization_relevance: float = 0.0  # 0..1: a relevant, compliant affiliate topic (studio.affiliate.RELEVANCE) 1.0

    def __post_init__(self):
        for k in list(WEIGHTS) + ["estimated_credit_cost"]:
            v = getattr(self, k)
            if not isinstance(v, (int, float)) or not 0.0 <= v <= 1.0:
                raise ValueError(f"opportunity input {k}={v!r} must be within 0..1")


def score_opportunity(o):
    if not o.facts_verified or o.duplicate or not o.rights_verified:
        return float("-inf")
    return round(sum(getattr(o, k) * w for k, w in WEIGHTS.items()) - o.estimated_credit_cost * COST_WEIGHT, 3)


LICENSING = {"own": 0.0, "official": 0.3, "permission": 0.7, "third-party": 1.0}
MAINTENANCE = {"low": 0.0, "medium": 0.5, "high": 1.0}  # high = prices/deals/patch facts that go stale within days


def production_cost(cand):
    """0..1 cost (owner Phase 8 #12: more than Everygen credits). Weighted: paid credits / 20 (0.40), production
    minutes / 180 (0.25), licensing complexity (0.15), upkeep (0.10), rendering (0.10: long video 1.0, Short 0.2).
    Inputs come from the candidate (credits, minutes, licensing, maintenance, format); defaults = a free map Short."""
    credits = min(1.0, (cand.get("credits") or 0) / 20)
    minutes = min(1.0, (cand.get("minutes") or 45) / 180)
    lic = LICENSING.get(cand.get("licensing", "official"), 0.3)
    upkeep = MAINTENANCE.get(cand.get("maintenance", "low"), 0.0)
    render = 1.0 if cand.get("format") == "long" else 0.2
    return round(0.40 * credits + 0.25 * minutes + 0.15 * lic + 0.10 * upkeep + 0.10 * render, 3)


def _affiliate_relevance(cand):
    """1.0 when the topic itself is about something a compliant product link helps with (storage, controller...)."""
    from . import affiliate
    text = " ".join([cand.get("title_en", ""), " ".join(cand.get("keywords") or []), " ".join(cand.get("search") or [])])
    return 1.0 if any(affiliate.relevant(n, text) for n in ("storage", "controller", "headset", "gear")) else 0.0


def search_views(phrases):
    try:
        terms = json.loads((LEARN / "search-terms.json").read_text())
    except (OSError, ValueError):
        return None
    rows = terms.get("terms", terms) if isinstance(terms, dict) else terms
    total = 0
    for r in rows if isinstance(rows, list) else []:
        t = str(r.get("term") or r.get("query") or "").lower()
        if any(p.lower() in t or t in p.lower() for p in phrases):
            total += int(r.get("views") or 0)
    return total


def opportunity_for(cand, winner, index):
    sv = search_views(cand.get("search") or [])
    age = winner.get("age_h") or 999
    rel = related(cand, index)
    o = Opportunity(
        search_demand=min(1.0, sv / 200) if sv else 0.3,
        relative_performance=min(1.0, (winner.get("ratio") or 0) / 10),
        audience_relevance=1.0 if set(cand.get("langs", ["en", "es"])) >= {"en", "es"} else 0.7,
        originality=0.6 if rel else 1.0,
        visual_potential=0.8 if (cand.get("place") or cand.get("grid")) else 0.5,
        asset_availability=1.0 if cand.get("family") in ("map", "shopping", "money", "creatures", "easter-eggs", "vehicles") else 0.3,
        timeliness=1.0 if age < 48 else 0.6 if age < 168 else 0.3,
        estimated_credit_cost=production_cost(cand),
        website_value=1.0 if cand.get("site_target") else 0.8 if (cand.get("place") or cand.get("grid")) else 0.3,
        monetization_relevance=_affiliate_relevance(cand),
        facts_verified=cand.get("status") == "verified" and len(_domains(cand.get("sources"))) >= 2,
        duplicate=bool(already_produced(cand, index)) or cand.get("status") == "produced",
        rights_verified=True,  # our own map/cards/site; footage-based topics must set "rights_verified": false until cleared
        evidence={"search_demand": "verified analytics (YouTube search terms)" if sv else "hypothesis",
                  "relative_performance": f"{winner.get('platform')} matched baseline"})
    if cand.get("rights_verified") is False:
        o.rights_verified = False
    return o


# ---------- winners per platform ----------

def youtube_winners(snap=None, hist=None, ups=None, now=None, days=14, recent_h=96):
    now = now or _now()
    snap = snap if snap is not None else json.loads((LEARN / "channel.json").read_text())
    hist = hist if hist is not None else scorecard.load_history()
    ups = ups if ups is not None else json.loads((LEARN / "uploads.json").read_text())
    # launch week lifted everything (scorecard.LAUNCH_END) and campaign clips are a retired format: both left out
    shorts = [v for v in snap.get("videos", []) if v.get("type") == "Short"
              and now - scorecard.ts(v["published"]) <= dt.timedelta(days=days)
              and scorecard.ts(v["published"]) >= scorecard.LAUNCH_END
              and scorecard.tags(v)["kind"] != "campaign clip"]
    fmt = {v["id"]: ("map" if (scorecard.script_tags(v["id"], ups) or {}).get("card") == "map" else "other")
           for v in shorts}
    out = []
    for v in shorts:
        pub = scorecard.ts(v["published"])
        age = (now - pub).total_seconds() / 3600
        if age > recent_h:
            continue  # a baseline peer only: follow-ups are for Shorts that are hot now
        rec = {"platform": "youtube-en", "id": v["id"], "title": v["title"], "age_h": round(age, 1),
               "views": v["views"], "format": fmt[v["id"]], "slug": (ups.get(v["id"]) or {}).get("slug"),
               "sufficient": False}
        if age < 3:
            out.append(rec)
            continue
        at = min(age, 24.0)
        mine = v["views"] if at >= age - 0.01 else scorecard.views_at(hist, v["id"], pub, at)
        peers = [o for o in shorts if o["id"] != v["id"] and (now - scorecard.ts(o["published"])).total_seconds() / 3600 >= at]
        same = [o for o in peers if fmt[o["id"]] == fmt[v["id"]]]
        group = same if len(same) >= 3 else peers
        vals = [scorecard.views_at(hist, o["id"], scorecard.ts(o["published"]), at) for o in group]
        vals = [x for x in vals if x is not None]
        if mine is None or len(vals) < 3:
            out.append(rec)
            continue
        base = statistics.median(vals)
        rec.update(sufficient=True, at_h=round(at, 1), views_at=mine, baseline=base,
                   baseline_n=len(vals), baseline_group="same format" if group is same else "all Shorts",
                   ratio=round(mine / base, 1) if base > 0 else None)
        out.append(rec)
    return out


def tiktok_winners(path=None, now=None):
    now = now or _now()
    files = sorted(LEARN.glob("tiktok-*.json")) if path is None else [Path(path)]
    if not files:
        return []
    vids = json.loads(files[-1].read_text()).get("videos", [])
    out = []
    for v in vids:
        t = dt.datetime.fromisoformat(v["posted_at_utc"]).replace(tzinfo=dt.timezone.utc)
        age = (now - t).total_seconds() / 3600
        rec = {"platform": "tiktok", "title": v.get("caption", "")[:80], "posted": v["posted_at_utc"],
               "age_h": round(age, 1), "views": v["views"], "lang": v.get("lang"), "sufficient": False}
        peers = [o["views"] for o in vids if o is not v and o.get("lang") == v.get("lang") and
                 dt.timedelta(days=1) <= t - dt.datetime.fromisoformat(o["posted_at_utc"]).replace(
                     tzinfo=dt.timezone.utc) <= dt.timedelta(days=14)]
        peers = peers or [o["views"] for o in vids if o is not v and o.get("lang") == v.get("lang")]
        if age >= 24 and len(peers) >= 3 and age <= 14 * 24:
            base = statistics.median(peers)
            rec.update(sufficient=True, baseline=base, baseline_n=len(peers),
                       ratio=round(v["views"] / base, 1) if base > 0 else None)
        out.append(rec)
    return out


def run(now=None):
    cands = load_candidates()
    fams, index = cands.get("families", {}), episode_index()
    rows = []
    for w in youtube_winners(now=now) + tiktok_winners(now=now):
        if not (w.get("sufficient") and w.get("ratio") and w["ratio"] >= RATIO):
            continue
        text = w["title"]
        if w.get("slug"):
            text += " " + w["slug"].replace("-", " ")
        w["family"] = family_of(text, fams)
        ready, research = evaluate_follow_up(w, cands.get("candidates", []), index, lang=w.get("lang") or "en")
        scored = sorted(((score_opportunity(opportunity_for(c, w, index)), c["key"]) for c in ready), reverse=True)
        ready = [next(c for c in ready if c["key"] == k) for _, k in scored]
        rows.append({**w, "ready": [c["key"] for c in ready], "scores": {k: v for v, k in scored},
                     "research_next": [c["key"] for c in research],
                     "related_existing": sorted({x for c in ready + research for x in related(c, index)})[:6]})
    res = {"at": (now or _now()).isoformat(), "ratio_rule": RATIO, "winners": rows}
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m studio.opportunities")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    res = run()
    if a.json:
        print(json.dumps(res, indent=1, ensure_ascii=False))
        return
    if not res["winners"]:
        print("No Short is 3x+ its matched baseline right now: keep the plan.")
    for w in res["winners"]:
        print(f"WINNER {w['platform']}: {w['title'][:60]} = {w['ratio']}x baseline ({w.get('views_at', w['views'])} vs "
              f"median {w['baseline']} of {w['baseline_n']}{', ' + w['baseline_group'] if w.get('baseline_group') else ''}"
              f"{', at ' + str(w['at_h']) + ' h' if w.get('at_h') else ''}); family: {w['family']}")
        print("  ready (verified, not made yet): " + (", ".join(f"{k} (score {w['scores'].get(k)})" for k in w["ready"])
                                                         or "none"))
        print("  research next (map intelligence agent): " + (", ".join(w["research_next"]) or "none"))


if __name__ == "__main__":
    main()
