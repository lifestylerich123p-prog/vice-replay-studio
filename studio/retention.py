"""Retention learning (free, no AI): which hooks, lengths and topics keep viewers watching.

    python -m studio.retention        # -> content/learn/retention.json + content/learn/retention.md

For every upload with analytics (YouTube shows them after ~1-2 days): average % viewed, seconds watched, how many
viewers are still there at ~10% of the video (the hook) and at the end, subscribers gained, plus our own data from the
episode file (hook headline, first line, length, Short or long). Then simple, honest comparisons: hooks with a number
vs without, under/over 30 s, streamer/news vs guide topics. The daily run reads retention.md before writing scripts.
"""
import datetime as dt
import json
import re
import statistics
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from .youtube_upload import token

ROOT = Path(__file__).resolve().parent.parent
LEARN = ROOT / "content" / "learn"


def report(tok, **p):
    end = dt.date.today()
    q = {"ids": "channel==MINE", "startDate": (end - dt.timedelta(days=60)).isoformat(), "endDate": end.isoformat(), **p}
    r = urllib.request.Request("https://youtubeanalytics.googleapis.com/v2/reports?" + urllib.parse.urlencode(q),
                               headers={"Authorization": f"Bearer {tok}"})
    with urllib.request.urlopen(r, timeout=30) as resp:
        d = json.load(resp)
    cols = [c["name"] for c in d.get("columnHeaders", [])]
    return [dict(zip(cols, row)) for row in d.get("rows", [])]


def episode_index():
    """YouTube id -> what we know from our own episode files (hook, first line, kind)."""
    out = {}
    for f in sorted((ROOT / "episodes").glob("*.json")):
        try:
            ep = json.loads(f.read_text())
        except ValueError:
            continue
        reg = json.loads((ROOT / "content/learn/uploads.json").read_text()) if (ROOT / "content/learn/uploads.json").exists() else {}
        done = {r["item"]: {"id": vid} for vid, r in reg.items() if r.get("slug") == ep.get("slug")}
        shorts = ([{"id": "", "segments": ep.get("short", []), "title": ep.get("short_title")}] if ep.get("short") else [])
        shorts += ep.get("shorts", [])
        for key, v in done.items():
            if not isinstance(v, dict) or not v.get("id"):
                continue
            if key == "main":
                segs, kind = ep.get("segments", []), "long"
            else:
                sh = next((s for s in shorts if (s.get("id") or "short") == key or (key == "short" and not s.get("id"))), {})
                segs, kind = sh.get("segments", []), "short"
            first = segs[0] if segs else {}
            out[v["id"]] = {"slug": ep.get("slug"), "kind": kind, "hook": first.get("headline", ""),
                            "first_line": first.get("text", ""),
                            "topic": "news" if key in ("news",) or "#ViceReplayBreaking" in json.dumps(ep) else "guide"}
    return out


def curve(tok, vid):
    """Watch ratio along one video: sorted [(elapsed ratio 0..1, watch ratio)], or None if unavailable."""
    try:
        rows = report(tok, metrics="audienceWatchRatio", dimensions="elapsedVideoTimeRatio", filters=f"video=={vid}")
    except urllib.error.HTTPError:
        return None
    if not rows:
        return None
    return sorted((r["elapsedVideoTimeRatio"], r["audienceWatchRatio"]) for r in rows)


def curve_points(pts):
    hook = min(pts, key=lambda p: abs(p[0] - 0.1))[1]
    end = pts[-1][1]
    return round(hook * 100), round(end * 100)


def per_second(pts, length):
    """% still watching at each whole second 0..length, read from the nearest sampled point of the curve."""
    out = []
    for s in range(int(length) + 1):
        ratio = s / length
        near = min(pts, key=lambda p: abs(p[0] - ratio))
        out.append(round(near[1] * 100))
    return out


def avg_med(xs):
    return round(statistics.median(xs)) if xs else "-"


def drop_summary(secs):
    """Second with the biggest one-second drop (never second 0), and how many points were lost there."""
    drops = [(secs[s - 1] - secs[s], s) for s in range(1, len(secs))]
    loss, s = max(drops)
    return s, loss


def main():
    tok = token()
    try:
        rows = report(tok, metrics="views,engagedViews,averageViewDuration,averageViewPercentage,subscribersGained,likes,shares",
                      dimensions="video", sort="-views", maxResults=200)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Analytics unavailable ({e.code}). Reconnect YouTube with tools/youtube_auth.py if this persists.")
    ch = json.loads((LEARN / "channel.json").read_text()) if (LEARN / "channel.json").exists() else {}
    vids = {v.get("id"): v for v in (ch.get("videos") or ch.get("uploads") or [])}
    ours = episode_index()
    data = []
    for r in rows:
        vid = r["video"]
        meta = vids.get(vid, {})
        e = ours.get(vid, {})
        title = meta.get("title", "")
        kind = e.get("kind") or ("short" if "#shorts" in title.lower() else "long")
        pts = curve(tok, vid) if r.get("views", 0) >= 30 else None
        hook_pct, end_pct = curve_points(pts) if pts else (None, None)
        length = meta.get("duration_sec") or meta.get("seconds")
        secs = per_second(pts, float(length)) if pts and length and kind == "short" else None
        hook_text = e.get("hook") or title
        data.append({"id": vid, "title": title, "kind": kind, "views": r.get("views", 0),
                     "avg_pct": r.get("averageViewPercentage"), "avg_sec": r.get("averageViewDuration"),
                     "subs": r.get("subscribersGained", 0), "hook_kept_pct": hook_pct, "end_kept_pct": end_pct,
                     "hook": hook_text, "first_line": e.get("first_line", ""), "topic": e.get("topic", ""),
                     "hook_has_number": bool(re.search(r"\d", hook_text)),
                     "length_sec": length, "per_second": secs,
                     # engaged views / views: YouTube counts a Shorts view as "engaged" once it plays past the first
                     # moments, so this is the closest API number to Studio's "stayed to watch" (Nov 22)
                     "stayed_pct": round(100 * r["engagedViews"] / r["views"]) if r.get("engagedViews") is not None and r.get("views") else None,
                     "likes": r.get("likes", 0), "shares": r.get("shares", 0)})
    LEARN.mkdir(parents=True, exist_ok=True)
    (LEARN / "retention.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def avg(xs):
        xs = [x for x in xs if x is not None]
        return round(statistics.mean(xs), 1) if xs else None

    shorts = [d for d in data if d["kind"] == "short" and d["avg_pct"] is not None]
    lines = ["# Retention (auto-generated by `python -m studio.retention`; YouTube analytics lag 1-2 days)", "",
             "Use these when writing hooks and choosing length. Only trust a comparison with 3+ videos on each side.", ""]
    if shorts:
        def cmp(name, a, b, la, lb):
            if a and b:
                lines.append(f"- {name}: {la} {avg([d['avg_pct'] for d in a])}% viewed ({len(a)} Shorts) vs "
                             f"{lb} {avg([d['avg_pct'] for d in b])}% ({len(b)})")
        lines.append("## What keeps viewers (Shorts)")
        cmp("Hook with a number", [d for d in shorts if d["hook_has_number"]], [d for d in shorts if not d["hook_has_number"]],
            "number", "no number")
        cmp("Topic", [d for d in shorts if d["topic"] == "news"], [d for d in shorts if d["topic"] != "news"], "news/breaking",
            "other")
        lines.append(f"- Average Short: {avg([d['avg_pct'] for d in shorts])}% viewed, "
                     f"{avg([d['hook_kept_pct'] for d in shorts])}% still watching at the hook (~10% in; over 100 = people rewatch).")
        lines += ["", "## Best and worst Shorts by % viewed", "| % viewed | at hook (100 = all) | views | subs | hook |", "|---|---|---|---|---|"]
        ranked = sorted(shorts, key=lambda d: d["avg_pct"], reverse=True)
        for d in ranked[:5] + (ranked[-3:] if len(ranked) > 8 else []):
            lines.append(f"| {d['avg_pct']:.0f}% | {d['hook_kept_pct'] if d['hook_kept_pct'] is not None else '-'}% | "
                         f"{d['views']} | {d['subs']} | {d['hook'][:60]} |")
    timed = [d for d in shorts if d["per_second"]]
    if timed:
        at3 = [d["per_second"][3] for d in timed if len(d["per_second"]) > 3]
        at5 = [d["per_second"][5] for d in timed if len(d["per_second"]) > 5]
        lines += ["", "## Where Shorts lose viewers (per second; the biggest drop is where to fix the hook or cut)",
                  f"Median still watching: {avg_med(at3)}% at 3 s, {avg_med(at5)}% at 5 s ({len(timed)} Shorts with curves).",
                  "", "| % viewed | at 3 s | at 5 s | biggest drop | hook |", "|---|---|---|---|---|"]
        for d in sorted(timed, key=lambda d: d["avg_pct"], reverse=True)[:8]:
            s, loss = drop_summary(d["per_second"])
            at = lambda i: d["per_second"][i] if len(d["per_second"]) > i else "-"
            lines.append(f"| {d['avg_pct']:.0f}% | {at(3)}% | {at(5)}% | 0:{s:02d} (-{loss} pts) | {d['hook'][:60]} |")
    stayed = [d for d in shorts if d.get("stayed_pct") is not None and d["views"] >= 30]
    if stayed:  # YouTube has no official pass mark: compare each Short to our own median (research, Nov 22)
        med = statistics.median(d["stayed_pct"] for d in stayed)
        likes = sum(d["likes"] for d in stayed) * 100 / max(1, sum(d["views"] for d in stayed))
        lines += ["", "## Stayed to watch (engaged views / views; beat our own median, not a magic number)",
                  f"Median {med:.0f}% over {len(stayed)} Shorts with 30+ views; {likes:.1f} likes per 100 views.",
                  "", "| stayed | vs median | % viewed | views | hook |", "|---|---|---|---|---|"]
        for d in sorted(stayed, key=lambda d: d["stayed_pct"], reverse=True)[:6] + sorted(stayed, key=lambda d: d["stayed_pct"])[:3]:
            lines.append(f"| {d['stayed_pct']}% | {d['stayed_pct'] - med:+.0f} | {d['avg_pct']:.0f}% | {d['views']} | {d['hook'][:60]} |")
    longs = [d for d in data if d["kind"] == "long" and d["avg_pct"] is not None]
    if longs:
        lines += ["", "## Long videos", "| % viewed | avg seconds | views | title |", "|---|---|---|---|"]
        for d in sorted(longs, key=lambda d: d["avg_pct"], reverse=True)[:5]:
            lines.append(f"| {d['avg_pct']:.0f}% | {d['avg_sec']} | {d['views']} | {d['title'][:60]} |")
    (LEARN / "retention.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:14]))


if __name__ == "__main__":
    main()
