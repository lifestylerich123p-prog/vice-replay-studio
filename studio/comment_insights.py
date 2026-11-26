"""What GTA 6 players are talking about, from comments (owner, Nov 26: "learn from comments, see what people are talking
about and we can learn from it").

Reads the most-liked comments on the hottest GTA 6 videos of the last 48 hours (the newest content/learn/market-*.md,
written by `python -m studio.learn`) plus the newest comments on our own channel, sorts them into themes, and pulls
out the questions people keep asking: a "where is X / how do I" question with likes is a ready-made map/how-to Short.

    python -m studio.comment_insights            # 15 hot videos x 100 comments + ours (~16 quota units)
    python -m studio.comment_insights --videos 8

Writes content/learn/comment-insights-<date>.md (+ .json). Public data only; commenter names are not stored.
"""
import argparse
import collections
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEARN = ROOT / "content" / "learn"

# theme -> regex (English + Spanish); a comment can count for several themes
THEMES = {
    "performance (FPS, graphics, PS5 Pro)": r"\b(fps|30 ?fps|60 ?fps|frame ?rate|framerate|lag|laggy|stutter|graphics?|"
                                            r"resolution|ps5 pro|pro mode|gráficos|cuadros)\b",
    "PC version": r"\b(pc|steam|pc port|pc release|pc version|mods?)\b",
    "price / money / editions": r"(\$\s?\d+|\b(price|expensive|cheap|ultimate edition|standard edition|refund|precio|"
                                r"caro|barato)\b)",
    "where is it / map": r"\b(where|location|map|find|found|spot|dónde|donde|mapa|ubicación)\b",
    "how do I / help": r"\b(how (do|to|can)|can you|is there a way|cómo|como se|tutorial|help)\b",
    "cars / vehicles": r"\b(car|cars|vehicle|bike|boat|plane|helicopter|drive|driving|coche|carro|auto)\b",
    "police / wanted": r"\b(cops?|police|wanted|stars?|policía|policia)\b",
    "NPCs / physics / realism": r"\b(npcs?|physics|realistic|realism|detail|details|animation|ragdoll|física|realista)\b",
    "Jason & Lucia": r"\b(jason|lucia|lucía)\b",
    "story / ending / missions": r"\b(story|ending|endings|mission|missions|chapter|campaign|final|historia|misión)\b",
    "GTA Online": r"\b(online|multiplayer|gta online)\b",
    "bugs / glitches / crashes": r"\b(bug|bugs|glitch|glitches|crash|crashes|broken|patch|update|error)\b",
    "streamers": r"\b(speed|ishowspeed|kai|cenat|lacy|caseoh|xqc|nick ?eh ?30|ibai|rubius|illojuan|streamer)\b",
    "vs GTA 5 / RDR2": r"\b(gta ?5|gta ?v\b|rdr ?2|red dead|rdr)\b",
    "music / radio": r"\b(radio|music|song|songs|soundtrack|canción|música)\b",
    "animals / wildlife": r"\b(gator|alligator|animal|animals|shark|dog|cat|lion|zoo|caimán|cocodrilo)\b",
    "shops / clothes / style": r"\b(shoe|shoes|store|shop|clothes|outfit|outfits|hair|tattoo|tienda|ropa)\b",
}
QUESTION = re.compile(r"^\W*(where|how|can|does|do|is|are|when|what|why|which|who|anyone|dónde|donde|cómo|como|"
                      r"cuándo|qué|que|alguien|se puede)\b.*\?", re.I | re.S)
CLEAN = re.compile(r"https?://\S+|@\S+")
SPAM = re.compile(r"subscrib|my channel|check out my|steam key|giveaway|free robux|link in bio|suscr[ií]b|mi canal", re.I)


def themes_of(text):
    t = (text or "").lower()
    return [name for name, rx in THEMES.items() if re.search(rx, t)]


def is_question(text):
    return bool(QUESTION.match(CLEAN.sub("", text or "").strip())) and len(text) < 300


def market_videos(limit):
    """[(video_id, title)] from the newest market-*.md (English market files only)."""
    files = sorted(f for f in LEARN.glob("market-2*.md"))
    if not files:
        return []
    rows = re.findall(r"\[(.+?)\]\(https://www\.youtube\.com/watch\?v=([\w-]{11})\)", files[-1].read_text())
    return [(vid, title) for title, vid in rows][:limit]


def fetch(call, video_id, n=100):
    r = call("commentThreads", part="snippet", videoId=video_id, maxResults=n, order="relevance",
             textFormat="plainText")
    out = []
    for th in r.get("items", []):
        top = th["snippet"]["topLevelComment"]["snippet"]
        out.append({"video": video_id, "text": top.get("textOriginal") or top.get("textDisplay") or "",
                    "likes": int(top.get("likeCount", 0)), "replies": int(th["snippet"].get("totalReplyCount", 0))})
    return out


def analyse(comments):
    """Theme counts (by comments and by likes), example lines, and the most-liked questions. Self-promo spam
    ("subscribe to my channel", fake Steam keys) is dropped first."""
    comments = [c for c in comments if not SPAM.search(c["text"] or "")]
    by_count, by_likes, examples = collections.Counter(), collections.Counter(), collections.defaultdict(list)
    for c in comments:
        for th in themes_of(c["text"]):
            by_count[th] += 1
            by_likes[th] += 1 + c["likes"]
            examples[th].append(c)
    qs = sorted((c for c in comments if is_question(c["text"])), key=lambda c: -(c["likes"] + c["replies"]))
    return {"total": len(comments), "by_count": by_count, "by_likes": by_likes,
            "examples": {k: sorted(v, key=lambda c: -c["likes"])[:3] for k, v in examples.items()},
            "questions": qs[:25]}


def short(text, n=140):
    t = re.sub(r"\s+", " ", CLEAN.sub("", text)).strip()
    return t if len(t) <= n else t[: n - 1] + "…"


def report(res, own, sources, day):
    lines = [f"# What GTA 6 players are talking about ({day})", "",
             f"From {res['total']} top comments on {len(sources)} of the hottest GTA 6 videos (last 48 h, "
             f"`studio.comment_insights`) and {len(own)} recent comments on our own channel. Themes overlap; "
             "\"weight\" = comments + their likes.", "", "| Theme | Comments | Weight | Most-liked example |",
             "|---|---|---|---|"]
    for th, w in res["by_likes"].most_common():
        ex = res["examples"][th][0]
        lines.append(f"| {th} | {res['by_count'][th]} | {w:,} | \"{short(ex['text'], 90)}\" ({ex['likes']:,} likes) |")
    lines += ["", "## Questions people ask (most liked first)", ""]
    for q in res["questions"][:15]:
        lines.append(f"- \"{short(q['text'])}\" ({q['likes']:,} likes, {q['replies']} replies)")
    if own:
        o = analyse(own)
        lines += ["", "## On our own channel", "",
                  "Themes: " + ", ".join(f"{k} {v}" for k, v in o["by_count"].most_common(6)), ""]
        for c in own[:8]:
            lines.append(f"- \"{short(c['text'])}\"")
    lines += ["", "## Sources", ""] + [f"- {t} (https://www.youtube.com/watch?v={v})" for v, t in sources]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--videos", type=int, default=15)
    a = ap.parse_args()
    from .learn import call
    vids = market_videos(a.videos)
    if not vids:
        sys.exit("No content/learn/market-*.md yet: run python -m studio.learn first")
    comments, used = [], []
    for vid, title in vids:
        try:
            got = fetch(call, vid)
        except SystemExit as e:  # comments off on that video, or quota: skip it
            print(f"  skip {vid}: {str(e)[:90]}")
            continue
        comments += got
        used.append((vid, title))
    try:
        own = json.loads((LEARN / "comments.json").read_text())
    except (OSError, ValueError):
        own = []
    res = analyse(comments)
    day = dt.date.today().isoformat()
    (LEARN / f"comment-insights-{day}.md").write_text(report(res, own, used, day))
    (LEARN / f"comment-insights-{day}.json").write_text(json.dumps({
        "day": day, "videos": [v for v, _ in used], "total": res["total"],
        "themes": [{"theme": k, "comments": res["by_count"][k], "weight": w} for k, w in res["by_likes"].most_common()],
        "questions": [{"text": short(q["text"], 200), "likes": q["likes"], "replies": q["replies"], "video": q["video"]}
                      for q in res["questions"]]}, ensure_ascii=False, indent=1))
    print(f"{res['total']} comments from {len(used)} videos -> content/learn/comment-insights-{day}.md")
    for k, w in res["by_likes"].most_common(8):
        print(f"  {k}: {res['by_count'][k]} comments, weight {w:,}")


if __name__ == "__main__":
    main()
