"""One-screen status of the whole machine (free: YouTube API + local files). Run it for "how are we doing?".

    python -m studio.status        # prints it and writes content/learn/status.md

Shows: health (last studio.doctor), YouTube (next scheduled + last 24 h public uploads with views),
Instagram (posted today + next in content/learn/reels_queue.json), campaigns (approved ones + today's clips with views).
"""
import datetime as dt
import json
import re
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
LEARN = ROOT / "content" / "learn"
YT = "https://youtube.googleapis.com/youtube/v3/"
ET = ZoneInfo("America/New_York")


def yt_videos(ids):
    from .youtube_upload import req, token
    tok, out = token(), {}
    ids = list(dict.fromkeys(ids))
    for k in range(0, len(ids), 50):
        v, _ = req("GET", YT + "videos?part=snippet,statistics,status&id=" + ",".join(ids[k:k + 50]), tok)
        out.update({x["id"]: x for x in v.get("items", [])})
    return out


def main():
    now = dt.datetime.now(ET)
    L = [f"# Vice Replay status ({now:%a %b %-d, %-I:%M %p} ET, `python -m studio.status`)", ""]

    health = LEARN / "health.md"
    if health.exists():
        lines = health.read_text().splitlines()
        flags = [l for l in lines if l.startswith(("- 🔴", "- 🟡"))]
        L += ["## Health", lines[0].replace("# System health ", "Last check "), *(flags or ["- 🟢 all good"]), ""]

    reg = json.loads((LEARN / "uploads.json").read_text()) if (LEARN / "uploads.json").exists() else {}
    tracker = (ROOT / "content" / "campaigns" / "tracker.md").read_text()
    clip_ids = re.findall(r"(?:shorts/|youtu\.be/)([\w-]{11})", tracker)
    vids = yt_videos(list(reg)[-30:] + clip_ids)

    sched, recent = [], []
    for vid, x in vids.items():
        st, sn = x["status"], x["snippet"]
        if st.get("privacyStatus") == "private" and st.get("publishAt"):
            t = dt.datetime.fromisoformat(st["publishAt"].replace("Z", "+00:00")).astimezone(ET)
            if t > now:
                sched.append((t, sn["title"]))
        elif st.get("privacyStatus") == "public":
            pub = dt.datetime.fromisoformat(sn["publishedAt"].replace("Z", "+00:00")).astimezone(ET)
            if now - pub < dt.timedelta(hours=24) and vid not in clip_ids:
                recent.append((int(x["statistics"].get("viewCount", 0)), sn["title"]))
    try:  # extra snapshot for the scorecard's fair "first 24 h views" (studio.scorecard)
        from .scorecard import HIST
        pub_views = {vid: int(x["statistics"].get("viewCount", 0)) for vid, x in vids.items()
                     if x["status"].get("privacyStatus") == "public"}
        with HIST.open("a") as f:
            f.write(json.dumps({"t": dt.datetime.now(dt.timezone.utc).isoformat(timespec="minutes"),
                                "views": pub_views}, separators=(",", ":")) + "\n")
    except OSError:
        pass
    L.append("## YouTube")
    L += [f"- ⏰ {t:%a %-I:%M %p}: {title[:60]}" for t, title in sorted(sched)] or ["- nothing scheduled"]
    L += [f"- {v:,} views: {title[:60]}" for v, title in sorted(recent, reverse=True)[:6]]
    L.append("")

    qf = LEARN / "reels_queue.json"
    q = json.loads(qf.read_text()) if qf.exists() else []
    today = now.strftime("%Y-%m-%d")
    done = [i for i in q if i.get("posted_at", "").startswith(today) and str(i.get("posted", "")).startswith("http")]
    nxt = [i for i in q if not i.get("posted")][:5]

    def label(i):
        return (Path(i.get("carousel") or i.get("video") or i.get("episode", "")).stem
                + (f" ({i['item']})" if i.get("item") not in (None, "short") else "")
                + (" [CAMPAIGN]" if i.get("campaign") else ""))
    L.append("## Instagram")
    L.append(f"- Posted today: {len(done)}" + "".join(f"\n  - {label(i)}: {i['posted']}" for i in done))
    L += [f"- Next {i['at'][5:]}: {label(i)}" for i in nxt] or ["- queue empty"]
    L.append("")

    L.append("## Campaigns")
    for f in sorted((ROOT / "content" / "campaigns").glob("*.json")):
        if f.name.startswith("_"):
            continue
        c = json.loads(f.read_text())
        if c.get("owner_approved"):
            L.append(f"- {c.get('name', f.stem)}: {str(c.get('status', ''))[:70]}")
    for vid in clip_ids:
        x = vids.get(vid)
        if x:
            L.append(f"  - {int(x['statistics'].get('viewCount', 0)):,} views: {x['snippet']['title'][:55]}")
    L.append("")
    text = "\n".join(L)
    (LEARN / "status.md").write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
