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
        rows.append({**w, "ready": [c["key"] for c in ready], "research_next": [c["key"] for c in research],
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
        print("  ready (verified, not made yet): " + (", ".join(w["ready"]) or "none"))
        print("  research next (map intelligence agent): " + (", ".join(w["research_next"]) or "none"))


if __name__ == "__main__":
    main()
