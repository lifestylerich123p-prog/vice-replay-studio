"""Competitor learning (owner Phase 9 #6-#9): public upload data of comparable GTA 6 channels, normalized so channels
of different sizes and uploads of different ages can be compared, turned into HYPOTHESES (never rules) to test on our
own channels.

    python -m studio.competitors            # pull, normalize, write content/learn/competitors-data-<date>.json + .md
    python -m studio.competitors --dry-run  # same from the last saved pull (no API calls)

Method: for each channel in content/learn/competitor-channels.json, its last 50 uploads (playlistItems + videos.list,
about 3 quota units a channel, YouTube Data API key via studio.learn.call). Each video gets views/hour since upload
(videos 6 h - 30 days old only) and RATIO = its views/hour / the channel's own median views/hour. A title feature
(number, "secret/secreto", location words, question, map scale) is compared by the median ratio of videos WITH vs
WITHOUT it, with n on both sides. A feature becomes a "testable hypothesis" only with n >= 8 on each side across 3+
channels and a ratio gap >= 1.5x; otherwise "insufficient". Correlation, not causation: it says what to TEST.
"""
import argparse
import datetime as dt
import json
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEARN = ROOT / "content" / "learn"
CHANNELS = LEARN / "competitor-channels.json"
FEATURES = {
    "number": r"(^|\D)[2-9](\D|$)|\b(three|five|seven|tres|cinco|siete)\b",
    "secret": r"\b(secret\w*|secreto\w*|hidden|escondid\w*|oculto\w*)\b",
    "location": r"\b(location|where|ubicaci[oó]n\w*|d[oó]nde|lugar\w*)\b",
    "question": r"\?",
    "map_scale": r"\b(map size|how big|tamaño|grande|empty|vac[ií]o|fit inside)\b",
    "caps_word": r"\b[A-ZÁÉÍÓÚÑ]{4,}\b",
}


def _now():
    return dt.datetime.now(dt.timezone.utc)


def pull(handles, call=None):
    from .learn import call as default_call, iso_dur
    call = call or default_call
    rows = []
    for h in handles:
        ch = call("channels", part="id,contentDetails,statistics", forHandle=h.lstrip("@"))
        items = ch.get("items") or []
        if not items:
            continue
        c = items[0]
        uploads = c["contentDetails"]["relatedPlaylists"]["uploads"]
        pl = call("playlistItems", part="contentDetails", playlistId=uploads, maxResults=50)
        ids = [i["contentDetails"]["videoId"] for i in pl.get("items", [])]
        if not ids:
            continue
        vs = call("videos", part="snippet,statistics,contentDetails", id=",".join(ids))
        for v in vs.get("items", []):
            rows.append({"channel": h, "subs": int(c["statistics"].get("subscriberCount", 0) or 0),
                         "id": v["id"], "title": v["snippet"]["title"], "published": v["snippet"]["publishedAt"],
                         "views": int(v["statistics"].get("viewCount", 0) or 0),
                         "seconds": iso_dur(v["contentDetails"].get("duration"))})
    return rows


def normalize(rows, now=None):
    now = now or _now()
    by = {}
    for r in rows:
        age_h = (now - dt.datetime.fromisoformat(r["published"].replace("Z", "+00:00"))).total_seconds() / 3600
        if not 6 <= age_h <= 720:
            continue
        r = dict(r, age_h=round(age_h, 1), vph=r["views"] / age_h)
        by.setdefault(r["channel"], []).append(r)
    out = []
    for ch, rs in by.items():
        if len(rs) < 5:
            continue
        base = statistics.median(x["vph"] for x in rs) or 1e-9
        for x in rs:
            out.append(dict(x, ratio=round(x["vph"] / base, 2), channel_median_vph=round(base, 1)))
    return out


def features(title):
    t = re.sub(r"\b(gta|grand theft auto)\s*(6|vi|5|v|iv|4|seis)\b", "", title, flags=re.I)  # the game's name isn't a number
    t = re.sub(r"\bgta\s*(6|vi)\b|#\S+", "", t, flags=re.I)
    return {k: bool(re.search(p, t, re.I if k != "caps_word" else 0)) for k, p in FEATURES.items()}


def compare(rows, min_n=8, min_channels=3, min_gap=1.5):
    res = {}
    for f in FEATURES:
        w = [r for r in rows if features(r["title"])[f]]
        wo = [r for r in rows if not features(r["title"])[f]]
        if not w or not wo:
            res[f] = {"n_with": len(w), "n_without": len(wo), "verdict": "insufficient"}
            continue
        mw, mo = statistics.median(r["ratio"] for r in w), statistics.median(r["ratio"] for r in wo)
        chans = len({r["channel"] for r in w})
        gap = mw / mo if mo else None
        ok = len(w) >= min_n and len(wo) >= min_n and chans >= min_channels and gap and (gap >= min_gap or gap <= 1 / min_gap)
        res[f] = {"n_with": len(w), "n_without": len(wo), "channels_with": chans, "median_ratio_with": round(mw, 2),
                  "median_ratio_without": round(mo, 2), "gap": round(gap, 2) if gap else None,
                  "verdict": "testable hypothesis" if ok else "insufficient"}
    return res


def outliers(rows, k=3.0, top=10):
    return sorted([r for r in rows if r["ratio"] >= k], key=lambda r: -r["ratio"])[:top]


def report(rows, lang_of):
    groups = {"en": [r for r in rows if lang_of.get(r["channel"]) == "en"],
              "es": [r for r in rows if lang_of.get(r["channel"]) == "es"]}
    return {lg: {"videos": len(rs), "channels": len({r["channel"] for r in rs}), "features": compare(rs),
                 "outliers": [{k: r[k] for k in ("channel", "title", "ratio", "age_h", "seconds")} for r in outliers(rs)]}
            for lg, rs in groups.items()}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m studio.competitors")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    cfg = json.loads(CHANNELS.read_text())
    lang_of = {h: lg for lg in ("en", "es") for h in cfg.get(lg, [])}
    day = dt.date.today().isoformat()
    raw_path = LEARN / f"competitors-data-{day}.json"
    if a.dry_run:
        prev = sorted(LEARN.glob("competitors-data-*.json"))
        if not prev:
            print("no saved pull yet")
            return
        rows = json.loads(prev[-1].read_text())["rows"]
    else:
        rows = pull(list(lang_of))
    norm = normalize(rows)
    rep = report(norm, lang_of)
    raw_path.write_text(json.dumps({"pulled": _now().isoformat()[:19], "rows": rows, "report": rep}, ensure_ascii=False) + "\n")
    L = [f"# Competitor learning {day} (hypotheses to test, not rules)", "",
         "Ratio = a video's views/hour vs its own channel's median (videos 6 h-30 days old). n on both sides."]
    for lg, r in rep.items():
        L += ["", f"## {lg.upper()}: {r['videos']} videos, {r['channels']} channels", "",
              "| Title feature | n with / without | channels | median ratio with / without | verdict |", "|---|---|---|---|---|"]
        for f, d in r["features"].items():
            L.append(f"| {f} | {d['n_with']} / {d['n_without']} | {d.get('channels_with', '-')} | "
                     f"{d.get('median_ratio_with', '-')} / {d.get('median_ratio_without', '-')} | {d['verdict']} |")
        L += ["", "Outliers (3x+ their channel):"] + [f"- {o['ratio']}x {o['channel']}: {o['title'][:80]} ({o['seconds']} s)"
                                                    for o in r["outliers"]] or ["- none"]
    (LEARN / f"competitors-learning-{day}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:40]))


if __name__ == "__main__":
    main()
