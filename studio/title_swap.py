"""Swap the title of an underperforming upload to its next title option (owner's standing approval, content/owner.md).

    python -m studio.title_swap            # swap where it makes sense
    python -m studio.title_swap --dry-run  # only show what it would do

Rules (stateless, so it's safe to run from any session):
- Only our uploads with an episode file and output/<slug>/uploaded.json, public, 24-96 hours old.
- Underperforming = views per hour below 40% of the median of our same-kind uploads (Shorts vs long) from the last
  7 days, and fewer than 1,000 views.
- Only swaps once: the current title must still be the original (option 1). New title = option 2 from
  `title_options` (main video), `short_title_options` (main Short) or `title_options` inside a `shorts` item.
- Keeps description, tags, category and language exactly as they are.
"""
import argparse
import datetime as dt
import json
import statistics
from pathlib import Path

from .youtube_upload import req, token

ROOT = Path(__file__).resolve().parent.parent
YT = "https://youtube.googleapis.com/youtube/v3/"


def candidates():
    out = {}
    for f in sorted((ROOT / "episodes").glob("*.json")):
        try:
            ep = json.loads(f.read_text())
        except ValueError:
            continue
        reg = json.loads((ROOT / "content/learn/uploads.json").read_text()) if (ROOT / "content/learn/uploads.json").exists() else {}
        mine = {vid: r["item"] for vid, r in reg.items() if r.get("slug") == ep.get("slug")}
        for vid, key in mine.items():
            v = {"id": vid}
            if key == "main":
                opts = ep.get("title_options") or []
            elif key == "short":
                opts = ep.get("short_title_options") or []
            else:
                sh = next((s for s in ep.get("shorts", []) if s.get("id") == key), {})
                opts = sh.get("title_options") or []
            if len(opts) >= 2:
                out[v["id"]] = {"kind": "long" if key == "main" else "short", "options": opts, "slug": ep.get("slug")}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    tok = token()
    ch, _ = req("GET", YT + "channels?part=contentDetails&mine=true", tok)
    up = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    r, _ = req("GET", YT + f"playlistItems?part=contentDetails&maxResults=50&playlistId={up}", tok)
    ids = [i["contentDetails"]["videoId"] for i in r.get("items", [])]
    v, _ = req("GET", YT + "videos?part=snippet,statistics,status,contentDetails&id=" + ",".join(ids), tok)
    now = dt.datetime.now(dt.timezone.utc)
    rows = []
    for x in v.get("items", []):
        if x["status"]["privacyStatus"] != "public":
            continue
        pub = dt.datetime.fromisoformat(x["snippet"]["publishedAt"].replace("Z", "+00:00"))
        hours = max(1.0, (now - pub).total_seconds() / 3600)
        views = int(x["statistics"].get("viewCount", 0))
        kind = "short" if "#shorts" in x["snippet"]["title"].lower() else "long"
        rows.append({"x": x, "hours": hours, "views": views, "vph": views / hours, "kind": kind})
    cands = candidates()
    changed = 0
    for kind in ("short", "long"):
        recent = [r["vph"] for r in rows if r["kind"] == kind and r["hours"] <= 24 * 7]
        if len(recent) < 3:
            continue
        med = statistics.median(recent)
        for r in rows:
            x = r["x"]
            c = cands.get(x["id"])
            if not c or r["kind"] != kind or not (24 <= r["hours"] <= 96):
                continue
            if r["views"] >= 1000 or r["vph"] >= 0.4 * med:
                continue
            sn = x["snippet"]
            if sn["title"].strip() != c["options"][0].strip():
                continue  # already swapped (or edited by the owner): leave it
            new = c["options"][1][:100]
            print(f"{'WOULD SWAP' if a.dry_run else 'SWAP'} {x['id']} ({r['views']} views, {r['vph']:.1f}/h vs median "
                  f"{med:.1f}/h): '{sn['title']}' -> '{new}'")
            if not a.dry_run:
                body = {"id": x["id"], "snippet": {"title": new, "description": sn.get("description", ""),
                                                   "categoryId": sn["categoryId"], "tags": sn.get("tags", []),
                                                   "defaultLanguage": sn.get("defaultLanguage", "en")}}
                if sn.get("defaultAudioLanguage"):
                    body["snippet"]["defaultAudioLanguage"] = sn["defaultAudioLanguage"]
                req("PUT", YT + "videos?part=snippet", tok, body)
                changed += 1
    print(f"{changed} title(s) swapped" if not a.dry_run else "dry run done")


if __name__ == "__main__":
    main()
