"""Cross-platform performance layer (owner Nov 26, Phase 3 #14: "a shared analytics layer that records YouTube,
TikTok, Instagram and website performance. Keep individual platform measurements separate... Compare content against
platform-specific baselines. Do not assume TikTok performance will automatically translate to YouTube").

    python -m studio.xplat        # content/learn/xplat.json + xplat.md

One row per post per platform, never merged across platforms: views, engaged/completion where the platform gives it,
watch time, likes, comments, shares, saves, followers gained, publish hour (ET), format, language, production cost
(Everygen credits from the claim ledger). Each row's `rel` = its views / the median of the same platform + language
(YouTube: views at 24 h from history.jsonl, so old and new videos compare at the same age; TikTok: posts 1-14 days
old; Instagram: likes, because views need a connection the owner hasn't made). Website rows (Search Console pages)
stay separate. A format "works across platforms" only when its median rel is >= 1.2 on 2+ platforms.
Fields a platform doesn't report are None, never guessed.
"""
import datetime as dt
import json
import re
import statistics
from pathlib import Path

from . import scorecard

ROOT = Path(__file__).resolve().parent.parent
LEARN = ROOT / "content" / "learn"
ET = dt.timezone(dt.timedelta(hours=-5))

FORMATS = [  # first match wins; from the title/caption when the episode can't tell
    ("map/location", r"\b(where|location|located|d[oó]nde|map spot|lugar #|shop|store|tienda|zapater|barber|dealership)\b"),
    ("tutorial/how-to", r"\b(how to|do this|settings|ajustes|c[oó]mo|check these|first \d|tips?|truco)\b"),
    ("secret/easter egg", r"\b(secret|secreto|easter egg|hidden|escond|bigfoot|ufo|ovni|ghost|portal|backrooms)\b"),
    ("tier list", r"\b(tier|ranked)\b"),
    ("versus", r"\bvs\.?\b|\bversus\b"),
    ("streamer", r"\b(ishowspeed|speed|lacy|kai|ibai|illojuan|rubius|streamer)\b"),
]


HOOKS = [  # Phase 4 #8: hook structures, tracked per episode ("hook_type") or read from the first line
    ("location-reveal", r"\b(is (right )?(in|at|here|next to)|right in|here's exactly where|está (en|aquí|junto)|aquí está)\b"),
    ("warning", r"\b(before you|don't|do not|stop|antes de|no (compres|gastes|hagas))\b"),
    ("curiosity", r"\b(most players|nobody|walk (straight )?past|hidden|secret|casi nadie|escond)\b"),
    ("myth-check", r"\b(does .* exist|is it real|there's no|there is no|isn't real|no hay|existe)\b"),
    ("benefit", r"\b(free|gratis|track|save|in seconds|one tap|un toque)\b"),
    ("result-first", r"\d|\b(already|just|ya)\b"),
]


def hook_of(slug, title=""):
    p = ROOT / "episodes" / f"{slug}.json" if slug else None
    first = ""
    if p and p.exists():
        ep = json.loads(p.read_text())
        if ep.get("hook_type"):
            return ep["hook_type"]
        first = ((ep.get("short") or [{}])[0].get("text") or "")
    t = (first or title or "").lower()
    for name, pat in HOOKS:
        if re.search(pat, t):
            return name
    return "statement"


def fmt_of(text, card=None):
    if card == "map":
        return "map/location"
    t = (text or "").lower()
    for name, pat in FORMATS:
        if re.search(pat, t):
            return name
    return "news/facts"


def _credits_by_slug():
    try:
        from . import credits, everygen_claim
        _, rows = everygen_claim.fetch_ledger()
        return credits.ledger_summary(rows)["per_episode"]
    except Exception:  # no GitHub: costs unknown, not zero
        return None


def youtube_rows(snap=None, hist=None, ups=None, ret=None, cost=None):
    snap = snap if snap is not None else json.loads((LEARN / "channel.json").read_text())
    hist = hist if hist is not None else scorecard.load_history()
    ups = ups if ups is not None else json.loads((LEARN / "uploads.json").read_text())
    try:
        ret = ret if ret is not None else {r["id"]: r for r in json.loads((LEARN / "retention.json").read_text())}
    except (OSError, ValueError):
        ret = {}
    out = []
    for v in snap.get("videos", []):
        if v.get("type") != "Short" or scorecard.tags(v)["kind"] == "campaign clip":
            continue
        pub = scorecard.ts(v["published"])
        slug = (ups.get(v["id"]) or {}).get("slug")
        card = (scorecard.script_tags(v["id"], ups) or {}).get("card")
        r = ret.get(v["id"]) or {}
        ages = {f"views_{lab}": scorecard.views_at(hist, v["id"], pub, h, slack=max(0.5, h * 0.25))
                for lab, h in (("1h", 1), ("72h", 72), ("7d", 168), ("28d", 672))}
        out.append({"platform": "youtube", "lang": "en", "id": v["id"], "title": v["title"], "slug": slug, **ages,
                    "hook_type": hook_of(slug, v["title"]),
                    "format": fmt_of(v["title"], card), "published": v["published"],
                    "hour_et": pub.astimezone(ET).hour, "launch_week": pub < scorecard.LAUNCH_END,
                    "views": v["views"], "views_24h": scorecard.views_at(hist, v["id"], pub, 24),
                    "completion_pct": r.get("avg_pct"), "avg_watch_s": r.get("avg_sec"), "engaged": None,
                    "likes": v.get("likes"), "comments": v.get("comments"), "shares": r.get("shares"), "saves": None,
                    "followers": r.get("subs"), "cost_credits": (cost or {}).get(slug) if cost is not None else None})
    return out


def youtube_es_rows():
    """Vice Replay en Español: Analytics (28 days) joined with uploads-es.json (slug, voice). Separate platform."""
    try:
        an = json.loads((LEARN / "analytics-es.json").read_text())
        reg = json.loads((LEARN / "uploads-es.json").read_text())
    except (OSError, ValueError):
        return []
    out = []
    for v in an.get("videos", []):
        u = reg.get(v.get("video")) or {}
        out.append({"platform": "youtube-es", "lang": "es", "id": v.get("video"), "title": u.get("title", v.get("video")),
                    "slug": u.get("slug"), "format": fmt_of(u.get("title")), "views": v.get("views"),
                    "completion_pct": v.get("averageViewPercentage"), "avg_watch_s": v.get("averageViewDuration"),
                    "followers": v.get("subscribersGained"), "likes": v.get("likes"), "shares": v.get("shares"),
                    "comments": None, "saves": None, "engaged": None, "voice": u.get("voice"), "cost_credits": None,
                    "hook_type": hook_of(u.get("slug"), u.get("title", ""))})
    return out


def tiktok_rows(path=None):
    files = sorted(LEARN.glob("tiktok-*.json")) if path is None else [Path(path)]
    if not files:
        return []
    out = []
    for v in json.loads(files[-1].read_text()).get("videos", []):
        out.append({"platform": "tiktok", "lang": v.get("lang"), "id": v.get("posted_at_utc"), "title": v.get("caption", "")[:90],
                    "slug": None, "format": fmt_of(v.get("caption")), "published": v.get("posted_at_utc"),
                    "hour_et": (dt.datetime.fromisoformat(v["posted_at_utc"]).replace(tzinfo=dt.timezone.utc)
                                .astimezone(ET).hour),
                    "views": v.get("views"), "completion_pct": round(100 * v["full_watch_rate"], 1)
                    if v.get("full_watch_rate") is not None else None, "avg_watch_s": v.get("avg_watch_s"),
                    "engaged": None, "likes": None, "comments": None, "shares": None, "saves": None,
                    "followers": v.get("new_followers"), "cost_credits": None})
    return out


def instagram_rows():
    try:
        posts = json.loads((LEARN / "ig-stats.json").read_text())
    except (OSError, ValueError):
        return []
    return [{"platform": "instagram", "lang": "en", "id": p.get("id"), "title": (p.get("caption") or "")[:90],
             "slug": None, "format": fmt_of(p.get("caption")), "published": p.get("time"), "hour_et": None,
             "views": p.get("views"), "likes": p.get("likes"), "comments": p.get("comments"), "shares": p.get("shares"),
             "saves": p.get("saved"), "completion_pct": None, "avg_watch_s": None, "engaged": None, "followers": None,
             "cost_credits": None} for p in posts if p.get("kind") == "Reel"]


def website_rows():
    files = sorted(LEARN.glob("searchconsole-*.json"))
    if not files:
        return []
    d = json.loads(files[-1].read_text())
    return [{"platform": "website", "page": p["page"], "clicks": p.get("clicks"), "impressions": p.get("impressions"),
             "position": p.get("position"), "lang": "es" if p["page"].startswith("/es/") else "en"}
            for p in d.get("pages", [])]


def add_baselines(rows):
    """rel = metric / median of the same platform + language (YouTube: views at 24 h, after launch week)."""
    groups = {}
    for r in rows:
        if r["platform"] == "youtube":
            m = r["views_24h"] if not r.get("launch_week") else None
        elif r["platform"] == "instagram":
            m = r["views"] if r.get("views") is not None else r.get("likes")
        else:
            m = r.get("views")
        r["metric"] = m
        if m is not None:
            groups.setdefault((r["platform"], r["lang"]), []).append(m)
    base = {k: statistics.median(v) for k, v in groups.items() if len(v) >= 3}
    for r in rows:
        b = base.get((r["platform"], r["lang"]))
        r["baseline"] = b
        r["rel"] = round(r["metric"] / b, 2) if b and r.get("metric") is not None else None
    return base


def across(rows, min_rel=1.2):
    table = {}
    for r in rows:
        if r.get("rel") is not None:
            table.setdefault(r["format"], {}).setdefault(r["platform"], []).append(r["rel"])
    out = {}
    for f, per in table.items():
        med = {p: round(statistics.median(v), 2) for p, v in per.items()}
        n = {p: len(v) for p, v in per.items()}
        good = [p for p, m in med.items() if m >= min_rel and n[p] >= 2]
        out[f] = {"median_rel": med, "n": n, "works_on": good, "consistent": len(good) >= 2}
    return out


def hook_table(rows):
    """Median rel per hook type (YouTube only: the platform where we know the first line)."""
    g = {}
    for r in rows:
        if r["platform"] == "youtube" and r.get("rel") is not None and not r.get("launch_week"):
            g.setdefault(r.get("hook_type") or "statement", []).append(r["rel"])
    return {k: {"median_rel": round(statistics.median(v), 2), "n": len(v), "preliminary": len(v) < 5} for k, v in g.items()}


def age_table(rows):
    """Median YouTube views at 1 h / 24 h / 72 h / 7 d / 28 d (after launch week), with n; n < 5 = preliminary."""
    out = {}
    for lab in ("1h", "24h", "72h", "7d", "28d"):
        vals = [r[f"views_{lab}"] for r in rows if r["platform"] == "youtube" and not r.get("launch_week")
                and r.get(f"views_{lab}") is not None]
        out[lab] = {"median": statistics.median(vals) if vals else None, "n": len(vals), "preliminary": len(vals) < 5}
    return out


def build():
    cost = _credits_by_slug()
    rows = youtube_rows(cost=cost) + youtube_es_rows() + tiktok_rows() + instagram_rows()
    base = add_baselines(rows)
    # YouTube: same-age comparison (studio.opportunities: views at min(age, 24 h) vs the median of other Shorts at that
    # age, same card format when 3+), so a 6-hour-old Short counts without waiting for its 24 h mark
    from . import opportunities
    try:
        same_age = {w["id"]: w for w in opportunities.youtube_winners(days=30, recent_h=10 ** 6) if w.get("sufficient")}
    except Exception:  # noqa: BLE001 - missing snapshot files: keep the 24 h numbers
        same_age = {}
    for r in rows:
        w = same_age.get(r.get("id")) if r["platform"] == "youtube" else None
        if w and w.get("ratio") is not None:
            r.update(metric=w["views_at"], baseline=w["baseline"], rel=w["ratio"], at_h=w["at_h"])
    res = {"at": dt.datetime.now(dt.timezone.utc).isoformat(), "baselines": {f"{p}/{l}": b for (p, l), b in base.items()},
           "formats": across(rows), "hooks": hook_table(rows), "ages": age_table(rows), "posts": rows,
           "website": website_rows(),
           "missing": ["YouTube engaged views (not in our pull)", "TikTok likes/comments/shares (not requested from Windsor yet)",
                       "Instagram views/reach/saves (needs the owner's one-click Windsor Instagram connect)"]}
    (LEARN / "xplat.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str) + "\n")
    L = [f"# Cross-platform performance ({res['at'][:16]} UTC, `python -m studio.xplat`)", "",
         "Each platform is compared only with itself (rel = views / that platform's median; YouTube at 24 h, after "
         "launch week; Instagram by likes until views are connected).", "", "## Baselines",
         *[f"- {k}: median {v}" for k, v in res["baselines"].items()], "", "## Formats (median rel per platform, n)",
         "| Format | YouTube | TikTok | Instagram | Works on |", "|---|---|---|---|---|"]
    for f, d in sorted(res["formats"].items(), key=lambda x: -max(x[1]["median_rel"].values())):
        cell = lambda p: f"{d['median_rel'][p]} ({d['n'][p]})" if p in d["median_rel"] else "-"
        L.append(f"| {f} | {cell('youtube')} | {cell('tiktok')} | {cell('instagram')} | "
                 f"{', '.join(d['works_on']) or '-'}{' ✅ consistent' if d['consistent'] else ''} |")
    L += ["", "## Hooks (YouTube, median rel, n; n < 5 = preliminary)"]
    L += [f"- {k}: {d['median_rel']} (n={d['n']}{', preliminary' if d['preliminary'] else ''})"
          for k, d in sorted(res["hooks"].items(), key=lambda x: -x[1]["median_rel"])]
    L += ["", "## YouTube views by age (median, n)"]
    L += [f"- {k}: {d['median']} (n={d['n']}{', preliminary' if d['preliminary'] else ''})" for k, d in res["ages"].items()]
    es = [r for r in rows if r["platform"] == "youtube-es" and r.get("completion_pct") is not None and r.get("views")]
    if es:
        by = {}
        for r in es:
            by.setdefault(r.get("voice") or "unknown (before Nov 26)", []).append(r["completion_pct"])
        L += ["", "## Spanish YouTube: average % viewed by voice (28 days)"]
        L += [f"- {k}: {round(statistics.median(v), 1)}% (n={len(v)}{', preliminary' if len(v) < 5 else ''})"
              for k, v in by.items()]
    L += ["", "## Top posts per platform"]
    for p in ("youtube", "youtube-es", "tiktok", "instagram"):
        top = sorted([r for r in rows if r["platform"] == p and r.get("rel")], key=lambda r: -r["rel"])[:3]
        L += [f"- {p}: " + "; ".join(f"{r['title'][:50]} ({r['rel']}x)" for r in top)] if top else []
    if res["website"]:
        top = sorted(res["website"], key=lambda r: -(r["impressions"] or 0))[:3]
        L += ["- website (Search Console): " + "; ".join(f"{r['page']} {r['impressions']} impr / {r['clicks']} clicks"
                                                           for r in top)]
    L += ["", "Not available yet: " + "; ".join(res["missing"]), ""]
    (LEARN / "xplat.md").write_text("\n".join(L))
    return res


if __name__ == "__main__":
    build()
    print((LEARN / "xplat.md").read_text())
