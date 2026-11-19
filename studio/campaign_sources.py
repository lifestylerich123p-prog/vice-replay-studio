"""Find new source footage for the campaigns we're in (free: YouTube API, about 2 quota units per campaign).

    python -m studio.campaign_sources            # print new GTA 6 videos/streams per active campaign

For every content/campaigns/*.json with owner_approved true, a "youtube_handle" or "youtube_channel_id" and a status that isn't paused or
ended, lists that creator's latest uploads (live-stream replays appear there too) whose title says
GTA 6, newest first, and marks the ones not yet in the campaign's "source_queue" or "used_sources".
Writes output/campaign_sources.json. It never downloads, clips or posts anything.
"""
import json
import re
from pathlib import Path

from .youtube_upload import req, token

ROOT = Path(__file__).resolve().parent.parent
YT = "https://youtube.googleapis.com/youtube/v3/"
GTA = re.compile(r"gta\s*(6|vi)\b|grand theft auto|leonida|vice city", re.I)


def iso_minutes(d):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d or "")
    return (int(m.group(1) or 0) * 60 + int(m.group(2) or 0)) if m else 0


def main():
    tok = token()
    report = {}
    for f in sorted((ROOT / "content" / "campaigns").glob("*.json")):
        c = json.loads(f.read_text())
        status = str(c.get("status", "")).lower()
        if not c.get("owner_approved") or status.startswith(("paused", "ended")):
            continue
        if c.get("youtube_channel_id"):
            ch, _ = req("GET", YT + f"channels?part=contentDetails&id={c['youtube_channel_id']}", tok)
        elif c.get("youtube_handle"):
            ch, _ = req("GET", YT + f"channels?part=contentDetails&forHandle={c['youtube_handle']}", tok)
        else:
            continue
        up = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        p, _ = req("GET", YT + f"playlistItems?part=snippet&maxResults=15&playlistId={up}", tok)
        ids = [i["snippet"]["resourceId"]["videoId"] for i in p.get("items", [])]
        v, _ = req("GET", YT + "videos?part=snippet,contentDetails,liveStreamingDetails&id=" + ",".join(ids), tok) if ids else ({}, None)
        seen = {u.split()[0] for u in c.get("source_queue", []) + c.get("used_sources", [])}
        rows = []
        for x in v.get("items", []):
            s = x["snippet"]
            if not GTA.search(s["title"]):  # titles only: descriptions mention GTA 6 in non-GTA videos
                continue
            url = f"https://www.youtube.com/watch?v={x['id']}"
            rows.append({"url": url, "title": s["title"], "published": s["publishedAt"][:16],
                         "minutes": iso_minutes(x["contentDetails"].get("duration")),
                         "stream_replay": "liveStreamingDetails" in x, "new": url not in seen})
        report[f.stem] = rows
        print(f"{f.stem} ({c.get('youtube_handle') or c.get('youtube_channel_id')}): {len(rows)} GTA 6 video(s)"
              + "".join(f"\n  {'NEW ' if r['new'] else '    '}{r['published']} {r['minutes']:>4} min "
                        f"{'stream ' if r['stream_replay'] else ''}{r['title'][:60]}  {r['url']}" for r in rows[:6]))
    out = ROOT / "output" / "campaign_sources.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
