"""Give already-uploaded videos their own search tags (Nov 22, 2026; owner: "check titles and tags are perfect").

    python -m studio.retag                 # apply every pending entry in content/learn/retag.json
    python -m studio.retag --before 2026-11-23T05:00   # only videos going public before this UTC time (most urgent)
    python -m studio.retag --limit 5

content/learn/retag.json: {video_id: {"channel": "en" | "es", "tags": [...], "done": "<UTC time>"?}}. Each update is a
videos.update on the snippet (50 quota units + 1 to read it); title, description, category and languages are kept as
they are. Tags have a small effect on discovery (titles matter far more), so this spends spare quota only: run it
after the day's uploads.
"""
import argparse
import datetime as dt
import json

from .youtube_upload import ROOT, clean_tags, req, token, token_for
from .youtube_es import TAGS_ES, config

REG = ROOT / "content" / "learn" / "retag.json"
KEEP = ("title", "description", "categoryId", "defaultLanguage", "defaultAudioLanguage")


def set_tags(tok, vid, tags, channel_id):
    v, _ = req("GET", f"https://youtube.googleapis.com/youtube/v3/videos?part=snippet,status&id={vid}", tok)
    items = v.get("items") or []
    if not items:
        return "not found"
    it = items[0]
    if it["snippet"].get("channelId") != channel_id:
        return "belongs to another channel: skipped"
    snip = {k: it["snippet"][k] for k in KEEP if k in it["snippet"]}
    snip["tags"] = tags
    req("PUT", "https://youtube.googleapis.com/youtube/v3/videos?part=snippet", tok, {"id": vid, "snippet": snip})
    return "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", help="only videos whose publishAt is before this UTC time (YYYY-MM-DDTHH:MM)")
    ap.add_argument("--limit", type=int, default=50)
    a = ap.parse_args()
    reg = json.loads(REG.read_text())
    cfg = config()
    ids = {"en": cfg["vice-replay"]["channel_id"], "es": cfg["vice-replay-es"]["channel_id"]}
    toks = {"en": token(), "es": token_for(ids["es"], "YT_SPANISH_REFRESH_TOKEN")}
    n = 0
    for vid, e in reg.items():
        if e.get("done") or n >= a.limit:
            continue
        if a.before and e.get("publish_at") and e["publish_at"] >= a.before:
            continue
        ch = e["channel"]
        tags = clean_tags(e["tags"], base=TAGS_ES) if ch == "es" else clean_tags(e["tags"])
        res = set_tags(toks[ch], vid, tags, ids[ch])
        print(f"{vid} ({ch}): {res} ({len(tags)} tags)")
        if res == "ok":
            e["done"] = dt.datetime.now(dt.timezone.utc).isoformat()[:19]
            n += 1
        REG.write_text(json.dumps(reg, indent=1, ensure_ascii=False))
    print(f"{n} video(s) retagged; {sum(not e.get('done') for e in reg.values())} pending")


if __name__ == "__main__":
    main()
