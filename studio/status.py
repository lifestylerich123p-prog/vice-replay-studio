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


def spanish_section(now):
    """Vice Replay en Español: subscribers, scheduled Shorts and views (needs its token in this session)."""
    import os
    L = ["## Vice Replay en Español"]
    try:
        from . import youtube_es
        from .youtube_upload import req, token
        if not (os.environ.get("YT_SPANISH_REFRESH_TOKEN") or os.environ.get("YT_ES_REFRESH_TOKEN")):
            return L + ["- token not loaded in this session", ""]
        from .youtube_upload import channel_ids, token_for
        tok = token_for(channel_ids()["es"], youtube_es.ENV)
        try:  # never show another channel's numbers under this heading
            youtube_es.check_channel(tok)
        except SystemExit as e:
            return L + [f"- not shown: {str(e)[:140]}", ""]
        ch, _ = req("GET", YT + "channels?part=statistics&mine=true", tok)
        st = ch["items"][0]["statistics"]
        L.append(f"- {st.get('subscriberCount', '?')} subscribers, {st.get('viewCount', '?')} views, {st.get('videoCount', '?')} videos")
        reg = json.loads(youtube_es.REGISTRY.read_text()) if youtube_es.REGISTRY.exists() else {}
        ids = list(reg)[-30:]
        if ids:
            v, _ = req("GET", YT + "videos?part=snippet,statistics,status&id=" + ",".join(ids), tok)
            for x in sorted(v.get("items", []), key=lambda x: x["status"].get("publishAt") or x["snippet"]["publishedAt"]):
                stt, sn = x["status"], x["snippet"]
                if stt.get("privacyStatus") == "private" and stt.get("publishAt"):
                    t = dt.datetime.fromisoformat(stt["publishAt"].replace("Z", "+00:00")).astimezone(ET)
                    L.append(f"- ⏰ {t:%a %-I:%M %p}: {sn['title'][:60]}")
                elif stt.get("privacyStatus") == "public":
                    L.append(f"- {int(x['statistics'].get('viewCount', 0)):,} views: {sn['title'][:60]}")
    except (SystemExit, Exception) as e:  # noqa: BLE001 - the status screen must never fail on this
        L.append(f"- couldn't read it: {str(e)[:100]}")
    return L + [""]


def momentum_lines(vph):
    """🔥 lines for Shorts that are taking off (Nov 23; .claude/commands/momentum.md rule): published in the last
    48 h, views/hour at least 2x the median of our last-7-days Shorts, and 500+ views. vph = [(age, v/h, views, title)]."""
    week = [r for r in vph if r[0] < dt.timedelta(days=7)]
    if len(week) < 3:
        return []
    import statistics
    base = statistics.median(r[1] for r in week)
    hot = [r for r in week if r[0] < dt.timedelta(hours=48) and r[2] >= 500 and r[1] >= 2 * base]
    return [f"- 🔥 TAKING OFF: {title[:55]} ({views:,} views, {rate:.0f}/h vs {base:.0f}/h median): make a follow-up "
            f"(.claude/commands/momentum.md)" for _, rate, views, title in sorted(hot, key=lambda r: -r[1])]


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

    sched, recent, vph = [], [], []
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
            if vid not in clip_ids:
                age_h = max((now - pub).total_seconds() / 3600, 0.25)
                vph.append((now - pub, int(x["statistics"].get("viewCount", 0)) / age_h,
                            int(x["statistics"].get("viewCount", 0)), sn["title"]))
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
    L += momentum_lines(vph)
    try:  # quota + free slots: what's still possible to post (python -m studio.quota for details)
        from . import quota
        by_day = {}
        for t, _ in sched:
            by_day.setdefault(t.date(), []).append(t)
        free = [(d, f) for d, f in quota.free_slots(by_day) if f]
        L.append(f"- Quota: ~{quota.left_today():,} units usable today (~{quota.left_today() // quota.UPLOAD} uploads), "
                 f"resets 3 AM ET")
        L += [f"- Free slot {d:%a}: {', '.join(f)}" for d, f in free]
    except Exception:  # noqa: BLE001 - the status screen must never fail on this
        pass
    L.append("")

    L += spanish_section(now)

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
