"""Growth audit (owner Nov 28, "Audience growth recovery"): free, deterministic, read-only, per channel.

    python -m studio.growth            # both channels -> content/learn/growth-audit.json + growth-audit.md
    python -m studio.growth --lang es  # one channel

What it collects (YouTube Data + Analytics APIs, the channel's own token): subscribers, total views, views in the last
24 h / 48 h / 7 d (our own view snapshots in history.jsonl; Analytics lags 2-3 days), engaged views, median views per
Short, Shorts-feed share of views, stayed-to-watch proxy (engaged views / views), average view duration and % viewed,
retention curves for the 10 strongest and 10 weakest Shorts, search terms, traffic sources, subscriber conversion,
visibility (public / scheduled / private, made-for-kids, region blocks, rejected uploads). Matched age: views at 24 h,
72 h and 7 d after publishing from the snapshots (None when no snapshot brackets that age; never guessed).

Each public Short older than 48 h gets ONE likely problem (owner's A-G list; heuristic, compared with the channel's own
medians, small samples marked): A barely shown, B shown but swiped, C starts but leaves before the payoff, D watches but
doesn't engage/subscribe, G visibility or policy restriction. E (low demand) and F (competitors better) need topic and
competitor research, so they are left for the weekly scout, never inferred here. Missing data stays None
(a 0-view video is "no data", not 0% retention). Not available through the API: impressions in the Shorts feed
("shown in feed"), Studio's exact viewed-vs-swiped number, returning viewers, copyright claims: reported as unavailable.
"""
import datetime as dt
import json
import statistics
import sys
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEARN = ROOT / "content" / "learn"
API = "https://youtube.googleapis.com/youtube/v3"
UNAVAILABLE = ["Shorts feed impressions (shown in feed)", "Studio's exact viewed-vs-swiped-away %", "returning viewers",
               "copyright claims (Studio only)"]


def _med(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.median(xs), 1) if xs else None


def snapshots():
    out = []
    f = LEARN / "history.jsonl"
    if f.exists():
        for line in f.read_text().splitlines():
            try:
                r = json.loads(line)
                out.append((dt.datetime.fromisoformat(r["t"]), r.get("views") or {}))
            except (ValueError, KeyError):
                continue
    return sorted(out, key=lambda x: x[0])


def views_at(snaps, vid, published, hours):
    """Views `hours` after publishing, interpolated between the two snapshots around that moment; None if not bracketed."""
    target = published + dt.timedelta(hours=hours)
    before = after = None
    for t, views in snaps:
        if vid not in views:
            continue
        if t <= target:
            before = (t, views[vid])
        elif after is None:
            after = (t, views[vid])
            break
    if not before or not after:
        return None
    (t0, v0), (t1, v1) = before, after
    if (t1 - t0) > dt.timedelta(hours=36):  # too far apart to say what happened at that age
        return None
    frac = (target - t0) / (t1 - t0) if t1 > t0 else 0
    return round(v0 + (v1 - v0) * frac)


def classify(v, med):
    """One likely problem for a public Short >= 48 h old (see module doc). Returns (code, why)."""
    if v["visibility"] != "public" or v.get("restricted"):
        return "G", v.get("restricted") or v["visibility"]
    if v["views"] is None or v["views"] < max(50, 0.25 * (med["views"] or 0)):
        return "A", f"{v['views']} views vs channel median {med['views']}: YouTube barely tested it"
    if v["stayed_pct"] is not None and med["stayed_pct"] is not None and v["stayed_pct"] < med["stayed_pct"] - 10:
        return "B", f"stayed {v['stayed_pct']}% vs median {med['stayed_pct']}%: opening frame/hook loses people"
    if v["avg_pct"] is not None and v["avg_pct"] < 50:
        return "C", f"{v['avg_pct']}% viewed: they leave before the payoff"
    if v["subs_per_1k"] is not None and med["subs_per_1k"] and v["subs_per_1k"] < 0.5 * med["subs_per_1k"]:
        return "D", f"{v['subs_per_1k']} subs per 1,000 engaged views vs median {med['subs_per_1k']}"
    return "OK", "at or above the channel's own medians"


def audit(lang):
    from .retention import curve, curve_points, report
    from .youtube_upload import channel_ids, req, token_for
    cid = channel_ids().get(lang)
    if not cid:
        return {"lang": lang, "error": "channel not configured"}
    tok = token_for(cid, "YT_REFRESH_TOKEN" if lang == "en" else "YT_ES_REFRESH_TOKEN")
    now = dt.datetime.now(dt.timezone.utc)
    today = dt.date.today()
    ch, _ = req("GET", f"{API}/channels?part=statistics,contentDetails&id={cid}", tok)
    item = ch["items"][0]
    st = item["statistics"]
    pl = item["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, page = [], ""
    while len(ids) < 250:
        d, _ = req("GET", f"{API}/playlistItems?part=contentDetails&maxResults=50&playlistId={pl}"
                   + (f"&pageToken={page}" if page else ""), tok)
        ids += [i["contentDetails"]["videoId"] for i in d.get("items", [])]
        page = d.get("nextPageToken")
        if not page:
            break
    meta = {}
    for i in range(0, len(ids), 50):
        d, _ = req("GET", f"{API}/videos?part=snippet,statistics,status,contentDetails&id={','.join(ids[i:i + 50])}", tok)
        meta.update({v["id"]: v for v in d.get("items", [])})

    def safe(**p):
        try:
            return report(tok, **p)
        except urllib.error.HTTPError as e:
            return {"error": f"Analytics {e.code}"}
    per = safe(metrics="views,engagedViews,averageViewDuration,averageViewPercentage,subscribersGained,likes,shares,"
                       "comments", dimensions="video", sort="-views", maxResults=200)
    per = {r["video"]: r for r in per} if isinstance(per, list) else {}
    start28 = (today - dt.timedelta(days=28)).isoformat()
    sources = safe(metrics="views,engagedViews", dimensions="insightTrafficSourceType", sort="-views", startDate=start28)
    terms = safe(metrics="views", dimensions="insightTrafficSourceDetail", filters="insightTrafficSourceType==YT_SEARCH",
                 sort="-views", maxResults=25, startDate=start28)
    daily = safe(metrics="views,engagedViews,subscribersGained,subscribersLost", dimensions="day", sort="day",
                 startDate=(today - dt.timedelta(days=14)).isoformat())
    snaps = snapshots()
    vids = []
    for vid, m in meta.items():
        s, status, cd = m["snippet"], m["status"], m.get("contentDetails", {})
        pub = dt.datetime.fromisoformat((status.get("publishAt") if status.get("privacyStatus") == "private"
                                         and status.get("publishAt") else s["publishedAt"]).replace("Z", "+00:00"))
        a = dict(per.get(vid, {}))
        if a.get("views", 0) < 10:  # owner Nov 28: retention of a 0-9 view video is noise, not 0%: keep it unavailable
            for k in ("engagedViews", "averageViewPercentage", "averageViewDuration"):
                a.pop(k, None)
        views = int(m.get("statistics", {}).get("viewCount", 0))
        engaged = a.get("engagedViews")
        restricted = ("made for kids" if status.get("madeForKids") else None) or \
                     ("region-blocked" if cd.get("regionRestriction") else None) or \
                     (f"upload {status.get('uploadStatus')}" if status.get("uploadStatus") not in ("processed", "uploaded")
                      else None)
        dur = cd.get("duration", "")
        vids.append({
            "id": vid, "title": s["title"], "published": pub.isoformat(), "age_h": round((now - pub).total_seconds() / 3600),
            "short": "#shorts" in s["title"].lower() or dur.startswith("PT") and "M" not in dur.replace("PT", "")[:3],
            "visibility": ("scheduled" if status.get("privacyStatus") == "private" and status.get("publishAt")
                           else status.get("privacyStatus")),
            "restricted": restricted, "views": views if a or views else (views or None),
            "engaged": engaged, "stayed_pct": round(100 * engaged / a["views"]) if engaged is not None and a.get("views") else None,
            "avg_pct": round(a["averageViewPercentage"], 1) if a.get("averageViewPercentage") is not None else None,
            "avg_sec": a.get("averageViewDuration"),
            "subs": a.get("subscribersGained"), "likes": a.get("likes"), "comments": a.get("comments"),
            "shares": a.get("shares"),
            "subs_per_1k": round(1000 * a["subscribersGained"] / engaged, 2) if engaged and a.get("subscribersGained") is not None else None,
            "at_24h": views_at(snaps, vid, pub, 24), "at_72h": views_at(snaps, vid, pub, 72),
            "at_7d": views_at(snaps, vid, pub, 168)})
    public_shorts = [v for v in vids if v["short"] and v["visibility"] == "public" and v["age_h"] >= 48]
    med = {"views": _med([v["views"] for v in public_shorts]), "stayed_pct": _med([v["stayed_pct"] for v in public_shorts]),
           "avg_pct": _med([v["avg_pct"] for v in public_shorts]), "subs_per_1k": _med([v["subs_per_1k"] for v in public_shorts]),
           "at_24h": _med([v["at_24h"] for v in public_shorts]), "at_72h": _med([v["at_72h"] for v in public_shorts]),
           "at_7d": _med([v["at_7d"] for v in public_shorts])}
    for v in public_shorts:
        v["problem"], v["why"] = classify(v, med)
    # strongest / weakest by matched age (72 h when known, else views per day), only Shorts at least 72 h old
    ranked = [v for v in public_shorts if v["age_h"] >= 72]
    key = lambda v: v["at_72h"] if v["at_72h"] is not None else 72 * v["views"] / max(v["age_h"], 1)
    ranked.sort(key=key, reverse=True)
    top, bottom = ranked[:10], ranked[-10:][::-1] if len(ranked) > 10 else []
    for v in top + bottom:
        if (v["views"] or 0) >= 30:
            pts = curve(tok, v["id"])
            v["hook_kept_pct"], v["end_kept_pct"] = curve_points(pts) if pts else (None, None)

    def total_delta(hours):
        cut = now - dt.timedelta(hours=hours)
        past = next((views for t, views in reversed(snaps) if t <= cut), None)
        if not past:
            return None
        mine = [v["id"] for v in vids]
        if not any(i in past for i in mine):
            return None
        born = {v["id"] for v in vids if dt.datetime.fromisoformat(v["published"]) > cut}  # new since then: all views
        return sum(int(meta[i]["statistics"].get("viewCount", 0)) - past.get(i, 0) for i in mine
                   if (i in past or i in born) and "statistics" in meta[i])

    shorts_src = next((r for r in sources if r.get("insightTrafficSourceType") == "SHORTS"), {}) if isinstance(sources, list) else {}
    src_total = sum(r["views"] for r in sources) if isinstance(sources, list) else 0
    counts = {}
    for v in public_shorts:
        counts[v["problem"]] = counts.get(v["problem"], 0) + 1
    return {
        "lang": lang, "channel": cid, "at": now.isoformat(timespec="minutes"),
        "subscribers": int(st.get("subscriberCount", 0)), "total_views": int(st.get("viewCount", 0)),
        "videos": len(vids), "public": sum(v["visibility"] == "public" for v in vids),
        "scheduled": sum(v["visibility"] == "scheduled" for v in vids),
        "private": sum(v["visibility"] == "private" for v in vids),
        "unlisted": sum(v["visibility"] == "unlisted" for v in vids),
        "restricted": [(v["id"], v["restricted"]) for v in vids if v["restricted"]],
        "views_24h": total_delta(24), "views_48h": total_delta(48), "views_7d": total_delta(168),
        "daily": daily if isinstance(daily, list) else daily,
        "shorts_feed_share_pct": round(100 * shorts_src.get("views", 0) / src_total) if src_total else None,
        "sources": sources, "search_terms": terms, "medians": med, "n_shorts": len(public_shorts),
        "problems": counts, "top": top, "bottom": bottom, "shorts": public_shorts,
        "unavailable": UNAVAILABLE}


def md(r):
    if r.get("error"):
        return f"## {r['lang'].upper()}: {r['error']}\n"
    m = r["medians"]
    prelim = " (preliminary: n < 10)" if r["n_shorts"] < 10 else ""
    lines = [f"## {'English' if r['lang'] == 'en' else 'Spanish'} channel ({r['at']})",
             f"- Subscribers {r['subscribers']}, total views {r['total_views']}, videos {r['videos']} "
             f"(public {r['public']}, scheduled {r['scheduled']}, private {r['private']}, unlisted {r['unlisted']})",
             f"- Views last 24 h / 48 h / 7 d (our snapshots): {r['views_24h']} / {r['views_48h']} / {r['views_7d']}",
             f"- Public Shorts 48 h+: {r['n_shorts']}{prelim}. Medians: views {m['views']}, at 24 h {m['at_24h']}, "
             f"72 h {m['at_72h']}, 7 d {m['at_7d']}; stayed-to-watch proxy {m['stayed_pct']}%; % viewed {m['avg_pct']}; "
             f"subs per 1,000 engaged views {m['subs_per_1k']}",
             f"- Shorts feed share of views (28 d): {r['shorts_feed_share_pct']}%",
             "- Likely problem per Short: " + ", ".join(f"{k} {n}" for k, n in sorted(r["problems"].items())),
             "- Traffic sources (28 d): " + (", ".join(f"{s['insightTrafficSourceType']} {s['views']}" for s in r["sources"][:6])
                                             if isinstance(r["sources"], list) else str(r["sources"])),
             "- Search terms (28 d): " + (", ".join(f"{t['insightTrafficSourceDetail']} {t['views']}" for t in r["search_terms"][:10])
                                          if isinstance(r["search_terms"], list) and r["search_terms"] else "none / unavailable"),
             f"- Restrictions: {r['restricted'] or 'none found'}",
             "", "| Strongest (72 h views or rate) | views | 72 h | stayed | % viewed | hook kept | subs |", "|---|---|---|---|---|---|---|"]
    row = lambda v: (f"| {v['title'][:55]} | {v['views']} | {v['at_72h']} | {v['stayed_pct']} | {v['avg_pct']} | "
                     f"{v.get('hook_kept_pct')} | {v['subs']} |")
    lines += [row(v) for v in r["top"]]
    lines += ["", "| Weakest | views | 72 h | stayed | % viewed | hook kept | problem |", "|---|---|---|---|---|---|---|"]
    lines += [f"| {v['title'][:55]} | {v['views']} | {v['at_72h']} | {v['stayed_pct']} | {v['avg_pct']} | "
              f"{v.get('hook_kept_pct')} | {v.get('problem')} |" for v in r["bottom"]]
    lines += ["", "Unavailable through the API: " + "; ".join(r["unavailable"]) + "."]
    return "\n".join(lines) + "\n"


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    langs = [argv[argv.index("--lang") + 1]] if "--lang" in argv else ["en", "es"]
    out = {lang: audit(lang) for lang in langs}
    old = json.loads((LEARN / "growth-audit.json").read_text()) if (LEARN / "growth-audit.json").exists() else {}
    old.update(out)
    (LEARN / "growth-audit.json").write_text(json.dumps(old, indent=1, ensure_ascii=False, default=str))
    text = "# Growth audit (studio.growth; heuristic problem codes, the channel's own medians)\n\n" + \
           "\n".join(md(old[k]) for k in ("en", "es") if k in old)
    (LEARN / "growth-audit.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
