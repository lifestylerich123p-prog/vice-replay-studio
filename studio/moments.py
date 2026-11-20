"""Which streamer moments are already clipped to death, and which are still fresh (free, YouTube Data API).

    python -m studio.moments lacy                 # Shorts about Lacy from the last 12 h, best first
    python -m studio.moments "kreekcraft" --hours 24

Lesson (Nov 19): a moment many clippers already posted gets ~1 view (duplicate suppression); fresh moments win.
Prints the top Shorts by views/hour and a "TAKEN" list: the words that show up in many titles (dog, shoe store...).
Pick a moment that is NOT in the taken list, then get its Twitch clip link (owner, or studio.twitch_clips).
"""
import argparse
import collections
import datetime as dt
import re

from .learn import call, video_details

STOP = set("the a an to of in on and is it for with you your this that his he her she my was what when how why just "
           "gta 6 vi gta6 gtavi grand theft auto shorts short viral fyp funny clips clip stream streamer first time "
           "gets got goes went day did does not no be at by from into out up so i im its it's he's s new".split())


def scan(name, hours=12, pages=2):
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ids = []
    for q in [f"{name} gta 6", f"{name} gta"]:
        for order in ("viewCount", "date"):
            r = call("search", part="id", q=q, type="video", publishedAfter=since, order=order, maxResults=50,
                     videoDuration="short")
            ids += [i["id"]["videoId"] for i in r.get("items", [])]
    vids = [v for v in video_details(list(dict.fromkeys(ids))) if name.lower() in v["title"].lower()]
    return sorted(vids, key=lambda v: -v["views_per_hour"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name")
    ap.add_argument("--hours", type=int, default=12)
    a = ap.parse_args()
    vids = scan(a.name, a.hours)
    print(f"{len(vids)} Shorts about {a.name} in the last {a.hours} h (best first):")
    for v in vids[:25]:
        print(f'  {v["views_per_hour"]:7.0f}/h {v["views"]:>8,} {v["seconds"]:>3}s  {v["channel"][:18]:18} {v["title"][:70]}')
    words = collections.Counter()
    for v in vids:
        t = re.sub(r"#\w+|@\w+|[^\w\s']", " ", v["title"].lower())
        words.update({w for w in t.split() if w not in STOP and not w.startswith(a.name.lower()) and len(w) > 2})
    taken = [f"{w} ({n})" for w, n in words.most_common(25) if n >= 3]
    print("\nTAKEN (word in 3+ titles, skip these moments): " + ", ".join(taken))
    if vids:
        lengths = sorted(v["seconds"] for v in vids[:max(5, len(vids) // 5)])
        print(f"Top 20% median length: {lengths[len(lengths) // 2]} s")


if __name__ == "__main__":
    main()
