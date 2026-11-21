"""Data files for the Vice Replay Dashboard artifact (https://claude.ai/artifact/UZSJWSBJbXBByZvWcxrxiF).

    python -m studio.dashboard        # writes output/dashboard/{channel,uploads,schedule,campaigns}.json

Then (main chat) upload each file to the artifact with the Artifact tool (`asset: true`) and point its dataset at the
new /_blob/ url with ArtifactData `update` (datasets/<id>.source.url + updated: {at, by}). See
.claude/commands/dashboard.md. Free: YouTube API reads only, no AI.
"""
import datetime as dt
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from .youtube_upload import req, token

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output" / "dashboard"
YT = "https://youtube.googleapis.com/youtube/v3/"
ET = ZoneInfo("America/New_York")


def main():
    tok = token()
    ch, _ = req("GET", YT + "channels?part=contentDetails,statistics&mine=true", tok)
    c = ch["items"][0]
    up = c["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, page = [], ""
    while True:  # every upload, not just the newest 50 (the channel passed 50 on Nov 21 and old videos fell off)
        r, _ = req("GET", YT + f"playlistItems?part=contentDetails&maxResults=50&playlistId={up}" + (f"&pageToken={page}" if page else ""), tok)
        ids += [i["contentDetails"]["videoId"] for i in r.get("items", [])]
        page = r.get("nextPageToken")
        if not page:
            break
    v = {"items": []}
    for k in range(0, len(ids), 50):
        part, _ = req("GET", YT + "videos?part=snippet,statistics,status,contentDetails&id=" + ",".join(ids[k:k + 50]), tok)
        v["items"] += part.get("items", [])
    now = dt.datetime.now(dt.timezone.utc)
    uploads, schedule = [], []
    for x in v.get("items", []):
        sn, st, stat = x["snippet"], x["status"], x["statistics"]
        title = sn["title"]
        import re as _re
        m = _re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", x.get("contentDetails", {}).get("duration", ""))
        secs = sum(int(g or 0) * k for g, k in zip(m.groups(), (3600, 60, 1))) if m else 0
        kind = "Short" if (secs and secs <= 180 and "#shorts" in title.lower()) or (secs and secs <= 60) else "Long video"
        clean = title.replace("#GTA6", "").replace("#Shorts", "").replace("#Short", "").strip()
        if st["privacyStatus"] == "private" and st.get("publishAt"):
            when = dt.datetime.fromisoformat(st["publishAt"].replace("Z", "+00:00")).astimezone(ET)
            schedule.append({"when_et": when.strftime("%a %b %-d, %-I:%M %p"), "sort": when.isoformat(), "title": clean,
                             "kind": kind, "link": f"https://youtu.be/{x['id']}"})
            continue
        if st["privacyStatus"] != "public":
            continue
        pub = dt.datetime.fromisoformat(sn["publishedAt"].replace("Z", "+00:00"))
        hours = max(1.0, (now - pub).total_seconds() / 3600)
        views = int(stat.get("viewCount", 0))
        uploads.append({"title": clean, "kind": kind, "posted": pub.astimezone(ET).strftime("%b %-d"),
                        "views": views, "likes": int(stat.get("likeCount", 0)),
                        "comments": int(stat.get("commentCount", 0)), "views_per_hour": round(views / hours, 1),
                        "link": f"https://youtu.be/{x['id']}", "id": x["id"]})
    uploads.sort(key=lambda u: u["views"], reverse=True)
    schedule.sort(key=lambda s: s["sort"])
    for s in schedule:
        s.pop("sort")
    s = c["statistics"]
    day_ago = [u for u in uploads]  # views on uploads (lifetime); channel total lags a few hours on YouTube
    channel = [{"subscribers": int(s.get("subscriberCount", 0)), "channel_views": int(s.get("viewCount", 0)),
                "upload_views": sum(u["views"] for u in day_ago), "public_videos": len(uploads),
                "scheduled": len(schedule), "updated_et": now.astimezone(ET).strftime("%b %-d, %-I:%M %p ET")}]
    campaigns = []
    for f in sorted((ROOT / "content" / "campaigns").glob("*.json")):
        if f.name.startswith("_"):
            continue
        cj = json.loads(f.read_text())
        campaigns.append({"campaign": cj.get("name", f.stem), "status": cj.get("status", ""),
                          "approved": "yes" if cj.get("owner_approved") else "no",
                          "rate_per_1k": cj.get("rate_per_1000_views"), "min_views": cj.get("min_views_to_pay"),
                          "budget_left": cj.get("budget_left_nov18") or cj.get("budget")})
    OUT.mkdir(parents=True, exist_ok=True)
    for name, rows in (("channel", channel), ("uploads", uploads), ("schedule", schedule), ("campaigns", campaigns)):
        (OUT / f"{name}.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
    print(f"subs {channel[0]['subscribers']}, {len(uploads)} public uploads ({channel[0]['upload_views']} views), "
          f"{len(schedule)} scheduled, {len(campaigns)} campaign(s) -> {OUT}")


if __name__ == "__main__":
    main()
