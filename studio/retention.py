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


def curve_points(tok, vid):
    try:
        rows = report(tok, metrics="audienceWatchRatio", dimensions="elapsedVideoTimeRatio", filters=f"video=={vid}")
    except urllib.error.HTTPError:
        return None, None
    if not rows:
        return None, None
    pts = sorted((r["elapsedVideoTimeRatio"], r["audienceWatchRatio"]) for r in rows)
    hook = min(pts, key=lambda p: abs(p[0] - 0.1))[1]
    end = pts[-1][1]
    return round(hook * 100), round(end * 100)


def main():
    tok = token()
    try:
        rows = report(tok, metrics="views,averageViewDuration,averageViewPercentage,subscribersGained",
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
        hook_pct, end_pct = curve_points(tok, vid) if r.get("views", 0) >= 30 else (None, None)
        hook_text = e.get("hook") or title
        data.append({"id": vid, "title": title, "kind": kind, "views": r.get("views", 0),
                     "avg_pct": r.get("averageViewPercentage"), "avg_sec": r.get("averageViewDuration"),
                     "subs": r.get("subscribersGained", 0), "hook_kept_pct": hook_pct, "end_kept_pct": end_pct,
                     "hook": hook_text, "first_line": e.get("first_line", ""), "topic": e.get("topic", ""),
                     "hook_has_number": bool(re.search(r"\d", hook_text)),
                     "length_sec": meta.get("duration_sec") or meta.get("seconds")})
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
    longs = [d for d in data if d["kind"] == "long" and d["avg_pct"] is not None]
    if longs:
        lines += ["", "## Long videos", "| % viewed | avg seconds | views | title |", "|---|---|---|---|"]
        for d in sorted(longs, key=lambda d: d["avg_pct"], reverse=True)[:5]:
            lines.append(f"| {d['avg_pct']:.0f}% | {d['avg_sec']} | {d['views']} | {d['title'][:60]} |")
    (LEARN / "retention.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:14]))


if __name__ == "__main__":
    main()
