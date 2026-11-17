"""Learning loop: pull real numbers from YouTube so the machine learns what works.

    python -m studio.learn            # both reports below
    python -m studio.learn --mine     # only our channel
    python -m studio.learn --market   # only what's winning on YouTube

1. Our channel: every upload's public views, likes and comments, plus views per hour since posting (fair way to
   compare a 2-day-old Short with a 2-week-old video). Writes content/learn/channel.json and refreshes the
   auto table in content/performance.md.
2. The market: the most-viewed GTA 6 videos and Shorts from the last 48 hours on YouTube, with their titles,
   channels, length and speed. Writes content/learn/market-<date>.md, and adds today's patterns to
   content/learn/patterns.md (title words and formats that win).

Uses the free YouTube Data API v3. The key comes from YOUTUBE_API_KEY, or in Claude cloud sessions the network
proxy adds it automatically (saved as a network secret for www.googleapis.com).
"""
import argparse
import collections
import datetime as dt
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEARN = ROOT / "content" / "learn"
API = "https://www.googleapis.com/youtube/v3/"
HANDLE = "@ViceReplayTV-q8s"


def call(endpoint, **params):
    key = os.environ.get("YOUTUBE_API_KEY", "set-by-proxy")
    url = API + endpoint + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"X-Goog-Api-Key": key})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="ignore")[:400]
        sys.exit(f"YouTube API error {e.code} on {endpoint}: {body}")


def iso_dur(d):
    m = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d or "")
    if not m:
        return 0
    days, h, mi, s = (int(x or 0) for x in m.groups())
    return days * 86400 + h * 3600 + mi * 60 + s


def hours_since(ts):
    t = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return max(1.0, (dt.datetime.now(dt.timezone.utc) - t).total_seconds() / 3600)


def video_details(ids):
    out = []
    for i in range(0, len(ids), 50):
        r = call("videos", part="snippet,statistics,contentDetails", id=",".join(ids[i:i + 50]))
        for v in r.get("items", []):
            st, sn = v.get("statistics", {}), v["snippet"]
            secs = iso_dur(v["contentDetails"].get("duration"))
            views = int(st.get("viewCount", 0))
            out.append({
                "id": v["id"], "title": sn["title"], "channel": sn["channelTitle"],
                "published": sn["publishedAt"], "seconds": secs,
                "type": "Short" if secs and secs <= 180 else "Main",
                "views": views, "likes": int(st.get("likeCount", 0)), "comments": int(st.get("commentCount", 0)),
                "views_per_hour": round(views / hours_since(sn["publishedAt"]), 1),
                "url": f"https://www.youtube.com/watch?v={v['id']}",
            })
    return out


def mine():
    ch = call("channels", part="contentDetails,statistics", forHandle=HANDLE)
    if not ch.get("items"):
        sys.exit(f"Channel {HANDLE} not found.")
    c = ch["items"][0]
    uploads = c["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, token = [], None
    while True:
        r = call("playlistItems", part="contentDetails", playlistId=uploads, maxResults=50,
                 **({"pageToken": token} if token else {}))
        ids += [it["contentDetails"]["videoId"] for it in r.get("items", [])]
        token = r.get("nextPageToken")
        if not token:
            break
    vids = sorted(video_details(ids), key=lambda v: v["views_per_hour"], reverse=True)
    LEARN.mkdir(parents=True, exist_ok=True)
    snap = {"checked": dt.datetime.now(dt.timezone.utc).isoformat(timespec="minutes"),
            "subscribers": c["statistics"].get("subscriberCount"), "videos": vids}
    (LEARN / "channel.json").write_text(json.dumps(snap, indent=2))
    # refresh the auto table in performance.md (between markers)
    rows = ["| Video / Short | Type | Posted | Views | Views/hour | Likes | Comments |", "|---|---|---|---|---|---|---|"]
    rows += [f"| [{v['title']}]({v['url']}) | {v['type']} | {v['published'][:10]} | {v['views']:,} | "
             f"{v['views_per_hour']} | {v['likes']} | {v['comments']} |" for v in vids]
    block = f"<!-- auto:start -->\n## Live YouTube numbers (auto, {snap['checked'][:16]} UTC, {snap['subscribers']} subscribers)\n\n" \
            + "\n".join(rows) + "\n<!-- auto:end -->"
    perf = ROOT / "content" / "performance.md"
    txt = perf.read_text()
    txt = re.sub(r"<!-- auto:start -->.*?<!-- auto:end -->", block, txt, flags=re.S) if "auto:start" in txt \
        else txt.replace("\n## What's working", "\n" + block + "\n\n## What's working")
    perf.write_text(txt)
    print(f"Our channel: {len(vids)} uploads, {snap['subscribers']} subscribers")
    for v in vids[:5]:
        print(f"  {v['views_per_hour']:>7} views/h  {v['views']:>7,}  [{v['type']}] {v['title']}")
    return snap


STOP = set("the a an to of in and is it for on with you your this that i my we gta 6 vi gta6 gtavi grand theft auto "
           "shorts short".split())


def market():
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=48)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ids = []
    for duration in ("short", "medium"):
        r = call("search", part="id", q="GTA 6", type="video", order="viewCount", publishedAfter=since,
                 videoDuration=duration, maxResults=25, relevanceLanguage="en", regionCode="US")
        ids += [it["id"]["videoId"] for it in r.get("items", [])]
    vids = sorted(video_details(list(dict.fromkeys(ids))), key=lambda v: v["views_per_hour"], reverse=True)
    today = dt.date.today().isoformat()
    LEARN.mkdir(parents=True, exist_ok=True)
    words = collections.Counter()
    for v in vids[:30]:
        for w in re.findall(r"[a-z0-9']+", v["title"].lower()):
            if w not in STOP and len(w) > 2:
                words[w] += 1
    shorts = [v for v in vids if v["type"] == "Short"]
    mains = [v for v in vids if v["type"] == "Main"]
    caps = sum(1 for v in vids[:30] if re.search(r"\b[A-Z]{4,}\b", v["title"]))
    nums = sum(1 for v in vids[:30] if re.search(r"\d", v["title"]))
    lines = [f"# What's winning on YouTube: GTA 6, last 48 hours ({today})", "",
             f"Top {len(vids)} by views. Shorts: {len(shorts)}, longer videos: {len(mains)}.",
             f"Titles with a WORD IN CAPS: {caps}/30. Titles with a number: {nums}/30.",
             "Most common title words: " + ", ".join(f"{w} ({n})" for w, n in words.most_common(15)), "",
             "| Views/hour | Views | Type | Length | Title | Channel |", "|---|---|---|---|---|---|"]
    lines += [f"| {v['views_per_hour']:,} | {v['views']:,} | {v['type']} | {v['seconds'] // 60}:{v['seconds'] % 60:02d} | "
              f"[{v['title']}]({v['url']}) | {v['channel']} |" for v in vids[:40]]
    (LEARN / f"market-{today}.md").write_text("\n".join(lines) + "\n")
    with open(LEARN / "patterns.md", "a") as f:
        if f.tell() == 0:
            f.write("# Winning patterns over time (one line per day, auto)\n\n")
        top = vids[0] if vids else None
        f.write(f"- {today}: top words {', '.join(w for w, _ in words.most_common(8))}; caps {caps}/30; numbers {nums}/30; "
                f"Shorts {len(shorts)}/{len(vids)}" + (f"; #1 \"{top['title']}\" ({top['views_per_hour']:,}/h)" if top else "") + "\n")
    print(f"Market: {len(vids)} hot GTA 6 videos. Top words: {', '.join(w for w, _ in words.most_common(8))}")
    for v in vids[:5]:
        print(f"  {v['views_per_hour']:>9,} views/h [{v['type']}] {v['title']}  ({v['channel']})")
    return vids


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mine", action="store_true")
    ap.add_argument("--market", action="store_true")
    a = ap.parse_args()
    both = not (a.mine or a.market)
    if a.mine or both:
        mine()
    if a.market or both:
        market()


if __name__ == "__main__":
    main()
