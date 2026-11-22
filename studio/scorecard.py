"""Scorecard: turn raw YouTube numbers into "what works for US" (run automatically at the end of studio.learn).

    python -m studio.scorecard        # rebuild from content/learn/channel.json (+ analytics.json, history.jsonl)

Why: "views per hour since posting" flatters brand-new videos. Every learn run appends a snapshot to
content/learn/history.jsonl, so each upload gets a fair "views in its first 24 h" number. Each Short is tagged by
what we control (our own vs campaign clip, hook style, length, posting slot), and groups are compared by median.
Writes content/learn/scorecard.md (the daily run reads it before picking a topic): group table, best/worst
uploads, and auto "do more / do less" lines (only for groups with 3+ uploads, so one fluke doesn't steer us).
"""
import datetime as dt
import json
import re
import statistics
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
LEARN = ROOT / "content" / "learn"
HIST = LEARN / "history.jsonl"
ET = ZoneInfo("America/New_York")


def ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def append_history(snap):
    line = {"t": snap["checked"], "views": {v["id"]: v["views"] for v in snap["videos"]}}
    with HIST.open("a") as f:
        f.write(json.dumps(line, separators=(",", ":")) + "\n")


def load_history():
    if not HIST.exists():
        return []
    out = []
    for line in HIST.read_text().splitlines():
        try:
            h = json.loads(line)
            out.append((ts(h["t"]), h["views"]))
        except (ValueError, KeyError):
            continue
    return sorted(out, key=lambda x: x[0])


def views_at(hist, vid, published, hours=24, slack=13):
    """Views at `hours` after publishing, interpolated between the two snapshots around it (None if no data)."""
    target = published + dt.timedelta(hours=hours)
    pts = [(t, v[vid]) for t, v in hist if vid in v]
    before = [p for p in pts if p[0] <= target]
    after = [p for p in pts if p[0] >= target]
    if before and after:
        (t0, v0), (t1, v1) = before[-1], after[0]
        if t1 == t0:
            return v0
        if (t1 - t0) > dt.timedelta(hours=2 * slack):
            return None
        return round(v0 + (v1 - v0) * (target - t0) / (t1 - t0))
    if after and after[0][0] - target <= dt.timedelta(hours=slack):  # first check came a little late: close enough
        return after[0][1]
    return None


def tags(v):
    t = v["title"]
    base = re.sub(r"#\w+|\bGTA\s?(6|VI)\b|\bGTA6\b", "", t, flags=re.I)  # "GTA 6" is in every title
    out = {"kind": "campaign clip" if re.search(r"\blacy\b|kreek", t, re.I) else "own Short"}
    low = base.lower()
    out["format"] = ("campaign clip" if out["kind"] == "campaign clip" else
                     "quiz" if re.search(r"guess|quiz|only real|\b\d/\d\b|can you name", t, re.I) else
                     "comparison" if re.search(r"gta ?5|gta v\b| vs |took away|never did|difference|\bmap\b.*\b(florida|real)", t, re.I) else
                     "streamer" if re.search(r"speed|kai|lacy|jynxzi|clix|streamer|tgg|kreek", low) else
                     "tips/discovery" if re.search(r"tip|how to|money|cheat|save|secret|hidden|first|setting|grind|replay", low) else
                     "news/facts")
    if re.search(r"catch", base, re.I):
        hook = "catch"
    elif re.search(r"\d|\$", base):
        hook = "number"
    elif "?" in base:
        hook = "question"
    else:
        hook = "statement"
    out["hook"] = hook
    s = v.get("seconds") or 0
    out["length"] = "<=15 s" if s <= 15 else "16-30 s" if s <= 30 else "31-60 s" if s <= 60 else "60+ s"
    h = ts(v["published"]).astimezone(ET).hour
    out["slot (ET)"] = "morning <12" if h < 12 else "afternoon 12-17" if h < 17 else "evening 17-21" if h < 21 else "late 21+"
    return out


def script_tags(vid, ups):
    """What the episode file says about a Short we made (Nov 22): its picture (our own `chart` graphics, owner
    gameplay, or trailer/screenshot footage only) and whether its first sentence is a question. This is the test of the
    Nov 22 switch to graph Shorts (YouTube's Oct 2026 originality update) and of the "statement, not question" hook."""
    u = ups.get(vid) or {}
    try:
        ep = json.loads((ROOT / "episodes" / f"{u['slug']}.json").read_text())
    except (OSError, ValueError, KeyError):
        return {}
    item = u.get("item")
    segs = ep.get("short") if item == "short" else next(
        (x.get("segments") for x in ep.get("shorts", []) if x.get("id") == item), None)
    if not segs:
        return {}
    media = json.dumps(segs)
    pic = ("graph (our charts)" if any(x.get("chart") for x in segs) else
           "owner gameplay" if "media/gameplay" in media else "trailer/screenshots")
    first = re.split(r"(?<=[.?!])\s", (segs[0].get("text") or "").strip())[0]
    return {"picture": pic, "opener": "question" if first.endswith("?") else "statement"}


def med(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.median(xs), 1) if xs else None


def build():
    snap = json.loads((LEARN / "channel.json").read_text())
    ana = {}
    if (LEARN / "analytics.json").exists():
        ana = {r["video"]: r for r in json.loads((LEARN / "analytics.json").read_text()).get("videos", [])}
    hist = load_history()
    try:
        ups = json.loads((LEARN / "uploads.json").read_text())
    except (OSError, ValueError):
        ups = {}
    now = ts(snap["checked"])
    rows = []
    for v in snap["videos"]:
        if v["type"] != "Short":
            continue
        pub = ts(v["published"])
        age = (now - pub).total_seconds() / 3600
        extra = script_tags(v["id"], ups) if "campaign" not in tags(v)["kind"] else {}
        r = {**v, **tags(v), "picture": extra.get("picture", "-"), "opener": extra.get("opener", "-"),
             "age_h": round(age, 1),
             "v24": views_at(hist, v["id"], pub) if age >= 24 else None,
             "pct": ana.get(v["id"], {}).get("averageViewPercentage")}
        rows.append(r)
    lines = [f"# Scorecard (auto, {snap['checked'][:16]} UTC): what works for Vice Replay", "",
             "Fair numbers: **24 h views** = views in each Short's first 24 hours (from history snapshots; empty until a",
             "Short has been tracked across its first day). **v/h** = lifetime views per hour. **watched** = average %",
             "of the Short watched (YouTube Analytics, a few days behind). Medians per group; n = number of Shorts.", ""]
    overall = med([r["views_per_hour"] for r in rows])
    advice = []
    for key in ("format", "kind", "picture", "opener", "hook", "length", "slot (ET)"):
        groups = {}
        for r in rows:
            if r[key] == "-":  # campaign clips / Shorts without an episode file: no picture/opener tag
                continue
            groups.setdefault(r[key], []).append(r)
        lines += [f"## By {key}", "", "| Group | n | median v/h | median 24 h views | median watched |", "|---|---|---|---|---|"]
        for g, rs in sorted(groups.items(), key=lambda kv: -(med([r["views_per_hour"] for r in kv[1]]) or 0)):
            m = med([r["views_per_hour"] for r in rs])
            lines.append(f"| {g} | {len(rs)} | {m} | {med([r['v24'] for r in rs]) or '-'} | "
                         f"{(str(med([r['pct'] for r in rs])) + '%') if med([r['pct'] for r in rs]) else '-'} |")
            if len(rs) >= 3 and overall and m is not None:
                if m >= 1.5 * overall:
                    advice.append(f"DO MORE: {key} = {g} (median {m} v/h vs {overall} overall, n={len(rs)})")
                elif m <= 0.5 * overall:
                    advice.append(f"DO LESS: {key} = {g} (median {m} v/h vs {overall} overall, n={len(rs)})")
        lines.append("")
    best = sorted(rows, key=lambda r: -r["views_per_hour"])
    fmt = lambda r: (f"- {r['views_per_hour']} v/h, {r['views']:,} views, 24 h: {r['v24'] if r['v24'] is not None else '-'}"
                     f" · {r['kind']}, {r['hook']}, {r['length']} · {r['title'][:70]}")
    lines += ["## Best 5", ""] + [fmt(r) for r in best[:5]] + ["", "## Worst 5 (older than 24 h)", ""]
    lines += [fmt(r) for r in [r for r in best if r["age_h"] >= 24][-5:]] + [""]
    lines += ["## Auto advice", ""] + ([f"- {a}" for a in advice] or ["- Not enough Shorts per group yet."]) + [""]
    (LEARN / "scorecard.md").write_text("\n".join(lines))
    print("Scorecard: content/learn/scorecard.md" + ("".join(f"\n  {a}" for a in advice)))


if __name__ == "__main__":
    build()
