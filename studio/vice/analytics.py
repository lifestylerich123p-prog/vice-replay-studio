"""/vice audit: channel performance from real YouTube data, by series, with videos that need investigation.

Free: YouTube Data API (public numbers, ~5 quota units) + YouTube Analytics API (owner OAuth, Vice Replay only).
Every run appends snapshots (metric_snapshots, channel_snapshots, content/learn/history.jsonl); nothing earlier is
overwritten. Comparisons use the same age (views in the first 24 h) or age-independent ratios (engaged views / views,
% viewed), and a group needs 3+ videos before the report draws a conclusion from it.
"""
import datetime as dt
import json
import statistics
import urllib.parse
import urllib.request

from . import db
from .. import learn, scorecard

CHANNEL_ID = "UCzk9Wts3WFynOHZQJRWOQIw"
CREATED = "2026-11-13"


def series_of(v):
    t = v["title"].lower()
    tg = scorecard.tags(v)
    if tg["kind"] == "campaign clip":
        return "A: Moments (campaign streamer clips)"
    if any(k in t for k in ("ranking", "ranked", "top 3", "top 5", "funniest", "best 3")):
        return "B: Rankings"
    if tg["format"] == "comparison":
        return "C: Versus / Tested"
    if tg["format"] == "tips/discovery":
        return "C: Tips / Details"
    if tg["format"] == "streamer":
        return "Explained: streamer news (our narration)"
    return "Explained: news / facts"


def analytics_rows(start, end):
    from ..youtube_upload import token
    tok = token()

    def report(**p):
        q = {"ids": "channel==MINE", "startDate": start, "endDate": end, **p}
        req = urllib.request.Request("https://youtubeanalytics.googleapis.com/v2/reports?" + urllib.parse.urlencode(q),
                                     headers={"Authorization": f"Bearer {tok}"})
        with urllib.request.urlopen(req, timeout=40) as r:
            d = json.load(r)
        cols = [c["name"] for c in d.get("columnHeaders", [])]
        return [dict(zip(cols, row)) for row in d.get("rows", [])]

    per_video = report(metrics="views,engagedViews,averageViewDuration,averageViewPercentage,subscribersGained,"
                               "shares,likes,comments", dimensions="video", sort="-views", maxResults=200)
    return {"videos": {r["video"]: r for r in per_video},
            "traffic": report(metrics="views", dimensions="insightTrafficSourceType", sort="-views"),
            "content_type": report(metrics="views,engagedViews,subscribersGained", dimensions="creatorContentType"),
            "daily": report(metrics="views,subscribersGained,subscribersLost", dimensions="day", sort="day")}


def med(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.median(xs), 1) if xs else None


def collect(con):
    taken = db.now()
    ch = learn.call("channels", part="snippet,statistics,contentDetails", id=CHANNEL_ID)["items"][0]
    st = ch["statistics"]
    con.execute("INSERT OR REPLACE INTO channel_snapshots VALUES (?,?,?,?,?)",
                (CHANNEL_ID, taken, int(st["subscriberCount"]), int(st["viewCount"]), int(st["videoCount"])))
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, tok = [], None
    while True:
        r = learn.call("playlistItems", part="contentDetails", playlistId=uploads, maxResults=50,
                       **({"pageToken": tok} if tok else {}))
        ids += [i["contentDetails"]["videoId"] for i in r.get("items", [])]
        tok = r.get("nextPageToken")
        if not tok:
            break
    vids = learn.video_details(ids)
    for v in vids:  # YouTube treats <=3 min vertical uploads as Shorts; our main videos never say #Shorts
        v["type"] = "Short" if v["seconds"] <= 60 or (v["seconds"] <= 180 and "#short" in v["title"].lower()) else "Main"
    db.log_cost(con, "youtube_data_api", 2 + len(ids) // 50 * 2, "quota units", "audit: channel + uploads")
    try:
        ana = analytics_rows(CREATED, dt.date.today().isoformat())
        ana_note = None
    except Exception as e:  # token expired, scope missing...
        ana, ana_note = {"videos": {}, "traffic": [], "content_type": [], "daily": []}, f"analytics unavailable: {e}"
    for v in vids:
        a = ana["videos"].get(v["id"], {})
        v["series"] = series_of(v)
        v["age_h"] = round(learn.hours_since(v["published"]), 1)
        v.update({"engaged_views": a.get("engagedViews"), "avg_pct": a.get("averageViewPercentage"),
                  "avg_sec": a.get("averageViewDuration"), "subs_gained": a.get("subscribersGained"),
                  "shares": a.get("shares"), "a_views": a.get("views")})
        con.execute("INSERT OR REPLACE INTO metric_snapshots VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (v["id"], taken, v["published"], v["age_h"], v["title"], v["type"], v["series"], v["views"],
                     v["likes"], v["comments"], v["engaged_views"], v["avg_pct"], v["avg_sec"], v["subs_gained"],
                     v["shares"], "data+analytics api"))
    con.commit()
    scorecard.append_history({"checked": dt.datetime.now(dt.timezone.utc).isoformat(timespec="minutes"),
                              "videos": vids})
    return {"taken": taken, "channel": {"subs": int(st["subscriberCount"]), "views": int(st["viewCount"]),
                                        "videos": int(st["videoCount"])},
            "videos": vids, "analytics": ana, "analytics_note": ana_note}


def build(data):
    hist = scorecard.load_history()
    vids = data["videos"]
    for v in vids:
        v["views_24h"] = scorecard.views_at(hist, v["id"], scorecard.ts(v["published"])) if v["age_h"] >= 24 else None
        ev = v.get("engaged_views")
        v["engaged_rate"] = round(100 * ev / v["a_views"], 1) if ev is not None and v.get("a_views") else None
        v["subs_per_1k"] = round(1000 * (v.get("subs_gained") or 0) / v["a_views"], 2) if v.get("a_views") else None
    groups = {}
    for v in vids:
        groups.setdefault((v["type"], v["series"]), []).append(v)
    table = []
    for (typ, ser), vs in sorted(groups.items(), key=lambda kv: -sum(x["views"] for x in kv[1])):
        table.append({"type": typ, "series": ser, "n": len(vs), "total_views": sum(x["views"] for x in vs),
                      "median_views": med([x["views"] for x in vs]),
                      "median_views_24h": med([x["views_24h"] for x in vs]),
                      "n_24h": sum(1 for x in vs if x["views_24h"] is not None),
                      "median_engaged_rate": med([x["engaged_rate"] for x in vs]),
                      "median_pct_viewed": med([x["avg_pct"] for x in vs]),
                      "subs_gained": sum(x.get("subs_gained") or 0 for x in vs),
                      "conclusive": len(vs) >= 3})
    shorts = [v for v in vids if v["type"] == "Short"]
    m24 = med([v["views_24h"] for v in shorts])
    m_er = med([v["engaged_rate"] for v in shorts])
    flags = []
    for v in vids:
        why = []
        if v["type"] == "Short" and v["age_h"] >= 24 and v["views_24h"] is not None and m24 and v["views_24h"] < 0.25 * m24:
            why.append(f"{v['views_24h']} views in 24 h vs Short median {m24}")
        if v["type"] == "Short" and v["engaged_rate"] is not None and v["a_views"] >= 100 and m_er and v["engaged_rate"] < m_er - 15:
            why.append(f"only {v['engaged_rate']}% of viewers stayed to watch (median {m_er}%)")
        if v["age_h"] >= 48 and v["views"] < 20:
            why.append(f"{v['views']} views after {int(v['age_h'])} h: shown to almost nobody")
        if v.get("a_views") and v["a_views"] >= 1000 and not v.get("subs_gained"):
            why.append(f"{v['a_views']} views, 0 subscribers")
        if why:
            flags.append({"id": v["id"], "title": v["title"], "series": v["series"], "why": why})
    return {"taken": data["taken"], "channel": data["channel"], "groups": table, "flags": flags,
            "short_median_24h": m24, "short_median_engaged_rate": m_er,
            "traffic": data["analytics"]["traffic"], "content_type": data["analytics"]["content_type"],
            "daily": data["analytics"]["daily"], "analytics_note": data["analytics_note"],
            "videos": sorted(vids, key=lambda v: -v["views"])}


def write(rep):
    day = rep["taken"][:10]
    out = db.ROOT / "reports" / f"audit-{day}.md"
    c = rep["channel"]
    L = [f"# Vice Replay audit ({rep['taken']})", "",
         f"Public channel numbers (YouTube Data API): **{c['subs']} subscribers, {c['views']:,} views, {c['videos']} videos**. "
         "(Public counters lag; per-video totals below can be higher.)", ""]
    if rep["analytics_note"]:
        L += [f"> {rep['analytics_note']}", ""]
    L += ["## By series (observations)", "",
          "Engaged = share of views where the viewer stayed to watch (YouTube Analytics `engagedViews`; analytics lag 1-2 days, "
          "so the newest uploads show '-'). "
          "24 h = views in the first 24 hours (fair across ages). Groups under 3 videos are not conclusive.", "",
          "| Type | Series | Videos | Total views | Median views | Median 24 h | Median engaged % | Median % viewed | Subs gained |",
          "|---|---|---|---|---|---|---|---|---|"]
    for g in rep["groups"]:
        L.append(f"| {g['type']} | {g['series']}{'' if g['conclusive'] else ' *(n<3)*'} | {g['n']} | {g['total_views']:,} | "
                 f"{g['median_views']} | {g['median_views_24h'] or '-'} (n={g['n_24h']}) | {g['median_engaged_rate'] or '-'} | "
                 f"{g['median_pct_viewed'] or '-'} | {g['subs_gained']} |")
    L += ["", "## Top 10 uploads", "", "| Views | Engaged % | % viewed | Subs | Series | Title |", "|---|---|---|---|---|---|"]
    for v in rep["videos"][:10]:
        L.append(f"| {v['views']:,} | {v['engaged_rate'] or '-'} | {v['avg_pct'] or '-'} | {v.get('subs_gained') or 0} | "
                 f"{v['series']} | [{v['title']}]({v['url']}) |")
    L += ["", "## Videos needing investigation (signals, not verdicts)", ""]
    L += [f"- [{f['title']}](https://youtu.be/{f['id']}) ({f['series']}): " + "; ".join(f["why"]) for f in rep["flags"]] or ["- none"]
    if rep["traffic"]:
        tot = sum(t["views"] for t in rep["traffic"]) or 1
        L += ["", "## Where views come from", "",
              ", ".join(f"{t['insightTrafficSourceType']} {round(100 * t['views'] / tot)}%" for t in rep["traffic"][:6])]
    if rep["content_type"]:
        L += ["", "Shorts vs long: " + ", ".join(
            f"{t['creatorContentType']}: {t['views']:,} views, {t.get('engagedViews', '-')} engaged, +{t.get('subscribersGained', 0)} subs"
            for t in rep["content_type"])]
    L += ["", "## Unknowns (not measured here)", "",
          "- Copyright claims and Content ID status: check YouTube Studio > Content > Restrictions (no API for this).",
          "- Revenue: the channel is not in the Partner Program; there is no revenue data.",
          "- Thumbnail impressions/CTR: not available from the Analytics API for this channel.", ""]
    out.write_text("\n".join(L))
    jpath = out.with_suffix(".json")
    jpath.write_text(json.dumps(rep, indent=1, default=str))
    return out, jpath


def run():
    con = db.connect()
    rep = build(collect(con))
    return rep, write(rep)
