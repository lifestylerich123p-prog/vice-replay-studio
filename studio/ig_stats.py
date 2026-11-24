"""What works on Instagram (@vice.replaytv): views, reach, likes, saves and shares per post (owner, Nov 24, 2026:
"continue checks and ways to help the system and our videos"; we posted up to 4 times a day with no feedback).

    IG_USER_ID=17841454790873754 python -m studio.ig_stats     # -> content/learn/ig-stats.md (+ .json)

Uses the same Graph API connection as studio.instagram_upload (token injected by the network proxy). Reels vs carousels
vs images, best and worst, and the share of followers we gain is not exposed per post, so it's not shown.
"""
import json
import os
import statistics
from pathlib import Path

from .instagram_upload import call

ROOT = Path(__file__).resolve().parent.parent
LEARN = ROOT / "content" / "learn"


def insights(media):
    metrics = "views,reach,saved,shares" if media["media_type"] != "VIDEO" else "views,reach,saved,shares"
    try:
        r = call("GET", f"{media['id']}/insights", {"metric": metrics})
        return {d["name"]: (d.get("values") or [{}])[0].get("value", d.get("total_value", {}).get("value"))
                for d in r.get("data", [])}
    except (Exception, SystemExit):  # noqa: BLE001 - no insights permission (instagram_manage_insights) or one bad post
        try:
            r = call("GET", f"{media['id']}/insights", {"metric": "reach,saved"})
            return {d["name"]: (d.get("values") or [{}])[0].get("value") for d in r.get("data", [])}
        except (Exception, SystemExit):  # noqa: BLE001
            return {}


def main():
    uid = os.environ.get("IG_USER_ID")
    if not uid:
        raise SystemExit("IG_USER_ID is not set (17841454790873754 for @vice.replaytv)")
    r = call("GET", f"{uid}/media", {"fields": "id,caption,media_type,media_product_type,timestamp,like_count,"
                                               "comments_count,permalink", "limit": 50})
    rows = []
    for m in r.get("data", []):
        ins = insights(m)
        kind = "Reel" if m.get("media_product_type") == "REELS" else ("Carousel" if m["media_type"] == "CAROUSEL_ALBUM"
                                                                       else "Image")
        rows.append({"id": m["id"], "kind": kind, "time": m["timestamp"][:16], "likes": m.get("like_count", 0),
                     "comments": m.get("comments_count", 0), "views": ins.get("views"), "reach": ins.get("reach"),
                     "saved": ins.get("saved"), "shares": ins.get("shares"), "link": m.get("permalink"),
                     "caption": (m.get("caption") or "").split("\n")[0][:70]})
    (LEARN / "ig-stats.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
    have_views = any(x.get("views") or x.get("reach") for x in rows)
    key = (lambda x: (x.get("views") or x.get("reach") or 0)) if have_views else \
        (lambda x: (x.get("likes") or 0) + 2 * (x.get("comments") or 0))
    lines = ["# Instagram stats (auto, `python -m studio.ig_stats`)", "",
             *([] if have_views else ["Views/reach need the Meta app permission instagram_manage_insights (not granted yet); "
                                      "ranked by likes + 2 x comments for now.", ""]),
             "| Kind | n | median views | median reach | median likes | median saves |", "|---|---|---|---|---|---|"]
    for kind in ("Reel", "Carousel", "Image"):
        g = [x for x in rows if x["kind"] == kind]
        if g:
            med = lambda k: statistics.median([x.get(k) or 0 for x in g])
            lines.append(f"| {kind} | {len(g)} | {med('views')} | {med('reach')} | {med('likes')} | {med('saved')} |")
    lines += ["", "## Best 5", ""] + [f"- {x.get('views') or '?'} views, {x['likes']} likes, {x['comments']} comments · {x['kind']} · {x['caption']} · {x['link']}"
                                      for x in sorted(rows, key=key, reverse=True)[:5]]
    lines += ["", "## Worst 5", ""] + [f"- {x.get('views') or '?'} views, {x['likes']} likes · {x['kind']} · {x['caption']}"
                                       for x in sorted(rows, key=key)[:5]]
    (LEARN / "ig-stats.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:8]))


if __name__ == "__main__":
    main()
