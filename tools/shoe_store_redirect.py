"""Answer the "gta 6 shoe store" searchers on the video they land on (Nov 24, 2026: our #1 YouTube search phrase, ~4,000
views in 28 days, all to the LACY clip aYBokm3TIYE, which never says where the store is).

Adds one line to that video's description (once) and posts one comment with the answer. ~100 quota units.

    python tools/shoe_store_redirect.py            # dry run
    python tools/shoe_store_redirect.py --apply
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from studio.flops import API, get, token  # noqa: E402
from studio.youtube_upload import req  # noqa: E402

VIDEO = "aYBokm3TIYE"
LINE = ("👟 Where is the shoe store in GTA 6? The first one is Flip Flop House, off Sunbelt Highway in Key Lento. "
        "Map + every shoe store: https://vicereplay.com/guides/gta-6-shoe-stores/")
COMMENT = ("Where's the shoe store? 👟 Flip Flop House, off Sunbelt Highway in Key Lento. The rest: open the map → Style → "
           "Footwear. Pinned on our map: vicereplay.com/guides/gta-6-shoe-stores/")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    tok = token()
    v = get(tok, "videos", part="snippet", id=VIDEO)["items"][0]
    sn = v["snippet"]
    has = "Flip Flop House" in sn.get("description", "")
    print("description already has it:", has)
    if not a.apply:
        return
    if not has:
        body = {k: sn[k] for k in ("title", "categoryId", "description") if k in sn}
        body["tags"] = sn.get("tags", [])
        body["description"] = LINE + "\n\n" + sn.get("description", "")
        req("PUT", API + "videos?part=snippet", tok, {"id": VIDEO, "snippet": body})
        print("description updated")
    req("POST", API + "commentThreads?part=snippet", tok,
        {"snippet": {"videoId": VIDEO, "topLevelComment": {"snippet": {"textOriginal": COMMENT}}}})
    print("comment posted (pin it in Studio)")


if __name__ == "__main__":
    main()
