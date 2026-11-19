"""Comment replies for the Vice Replay channel (standing owner approval for auto-replies; see content/owner.md).

    python -m studio.replies list                  # unreplied comments on our videos -> output/replies.json
    python -m studio.replies post output/replies.json   # post the "reply" filled in for each item (skips empty)

`list` writes [{"id", "video", "video_title", "author", "comment", "reply": ""}] for top-level comments from other
people that have no reply from our channel yet. Fill in "reply" (or set "skip": true for spam, hate or trolls so they never come back; an empty reply
without skip just waits for a later run), then
`post`. Posted ids are remembered in content/learn/replied.json so nothing is answered twice.
"""
import json
import sys
from pathlib import Path

from .youtube_upload import reply, req, token

ROOT = Path(__file__).resolve().parent.parent
YT = "https://youtube.googleapis.com/youtube/v3/"
DONE = ROOT / "content" / "learn" / "replied.json"


def unreplied(tok):
    ch, _ = req("GET", YT + "channels?part=id&mine=true", tok)
    cid = ch["items"][0]["id"]
    done = set(json.loads(DONE.read_text())) if DONE.exists() else set()
    r, _ = req("GET", YT + f"commentThreads?part=snippet,replies&allThreadsRelatedToChannelId={cid}&maxResults=100", tok)
    out = []
    for t in r.get("items", []):
        top = t["snippet"]["topLevelComment"]["snippet"]
        if top.get("authorChannelId", {}).get("value") == cid or t["id"] in done:
            continue
        if any(c["snippet"].get("authorChannelId", {}).get("value") == cid for c in t.get("replies", {}).get("comments", [])):
            continue
        out.append({"id": t["id"], "video": top["videoId"], "author": top["authorDisplayName"],
                    "comment": top["textOriginal"], "reply": ""})
    if out:
        ids = ",".join(sorted({o["video"] for o in out}))[:2000]
        v, _ = req("GET", YT + "videos?part=snippet&id=" + ids, tok)
        titles = {x["id"]: x["snippet"]["title"] for x in v.get("items", [])}
        for o in out:
            o["video_title"] = titles.get(o["video"], "")
    return out


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("list", "post"):
        sys.exit(__doc__)
    tok = token()
    path = ROOT / "output" / "replies.json"
    if sys.argv[1] == "list":
        items = unreplied(tok)
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(items, indent=2, ensure_ascii=False))
        print(f"{len(items)} unreplied comment(s) -> {path}")
        for o in items:
            print(f"- {o['id']} | {o['video_title'][:40]} | {o['author']}: {o['comment'][:150]}")
        return
    items = json.loads(Path(sys.argv[2] if len(sys.argv) > 2 else path).read_text())
    done = set(json.loads(DONE.read_text())) if DONE.exists() else set()
    n = 0
    skipped = 0
    for o in items:
        if o.get("skip") and o["id"] not in done:
            done.add(o["id"])  # spam/troll/hate: remembered so it never shows up again
            skipped += 1
            continue
        if not o.get("reply", "").strip() or o["id"] in done:
            continue
        try:
            reply(tok, o["id"], o["reply"].strip())
            done.add(o["id"])
            n += 1
            print(f"replied to {o['author']}: {o['reply'][:70]}")
        except SystemExit as e:
            print(f"! reply to {o['author']} failed: {e}")
    DONE.parent.mkdir(parents=True, exist_ok=True)
    DONE.write_text(json.dumps(sorted(done), indent=1))
    print(f"{n} repl{'y' if n == 1 else 'ies'} posted" + (f", {skipped} skipped for good" if skipped else ""))


if __name__ == "__main__":
    main()
