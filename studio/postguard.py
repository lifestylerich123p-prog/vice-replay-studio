"""Never post the same thing twice, even when two chats (or a chat and a scheduled run) work at once (Nov 21, 2026).

Each Claude chat has its own copy of the repo: output/<slug>/uploaded.json is local, and the committed registry
(content/learn/uploads.json) or Instagram queue can be stale in another chat or on another branch. So before posting,
the uploaders ask the real sources:
- YouTube: the committed registry on EVERY branch on GitHub (slug + item), and the channel's own upload list, which
  includes scheduled/private videos (same title = already there).
- Instagram: the account's latest posts (same first caption line = already there), and today's real post count for
  the 4-per-day limit.
"""
import datetime as dt
import json
import re
import subprocess
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
ET = ZoneInfo("America/New_York")


def norm(text):
    """Compare titles/captions loosely: case, spacing, hashtags and the "<>" YouTube rejects don't matter."""
    t = re.sub(r"#\w+", "", (text or "").lower()).replace("→", ">").replace("‹", "<")
    return re.sub(r"[^a-z0-9$%']+", " ", t).strip()


def registry_entries():
    """{video id: record} from content/learn/uploads.json on this checkout and on every branch on GitHub."""
    reg = {}
    local = ROOT / "content" / "learn" / "uploads.json"
    if local.exists():
        reg.update(json.loads(local.read_text()))
    try:
        subprocess.run(["git", "-C", str(ROOT), "fetch", "-q", "origin"], timeout=60, check=False,
                       capture_output=True)
        refs = subprocess.run(["git", "-C", str(ROOT), "for-each-ref", "--format=%(refname)", "refs/remotes/origin"],
                              capture_output=True, text=True, timeout=30).stdout.split()
    except (OSError, subprocess.SubprocessError):
        refs = []
    for ref in refs:
        if ref.endswith("/HEAD"):
            continue
        r = subprocess.run(["git", "-C", str(ROOT), "show", f"{ref}:content/learn/uploads.json"],
                           capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            try:
                for vid, rec in json.loads(r.stdout).items():
                    reg.setdefault(vid, rec)
            except ValueError:
                pass
    return reg


def channel_titles(tok, req):
    """{normalized title: video id} for every upload on the channel (scheduled and private ones included)."""
    ch, _ = req("GET", "https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&mine=true", tok)
    up = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    out, page = {}, ""
    for _ in range(20):  # 1,000 videos max; 1 quota unit per page
        r, _ = req("GET", "https://youtube.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50"
                          f"&playlistId={up}" + (f"&pageToken={page}" if page else ""), tok)
        for it in r.get("items", []):
            out.setdefault(norm(it["snippet"]["title"]), it["snippet"]["resourceId"]["videoId"])
        page = r.get("nextPageToken")
        if not page:
            break
    return out


def youtube_duplicate(slug, key, titles, reg, live):
    """Reason string if this episode item is already on YouTube (or scheduled), else None."""
    for vid, rec in reg.items():
        if rec.get("slug") == slug and rec.get("item") == key:
            return f"registry says {slug} {key} is already uploaded: https://youtu.be/{vid}"
    for t in titles:
        if t and norm(t) in live:
            return f"the channel already has a video titled {t!r}: https://youtu.be/{live[norm(t)]}"
    return None


STORY_STOP = set("gta 6 vi the a an and or of to in on for is it its it's just already now this that with your you our "
                 "shorts short here why how what when who new official".split())


def story_words(title):
    """Key words of a title for 'same story' checks: lowercased, no hashtags/stop words; numbers kept (39, 3.79)."""
    t = re.sub(r"#\w+", "", (title or "").lower())
    return {w for w in re.findall(r"[a-z]+|\d+(?:\.\d+)?", t) if w not in STORY_STOP and (len(w) > 2 or w.isdigit())}


def channel_recent(tok, req, hours=72, pages=2):
    """[(title, video id, published)] for the channel's uploads in the last `hours` (newest first; 1 unit per page)."""
    ch, _ = req("GET", "https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&mine=true", tok)
    up = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    cut = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)
    out, page = [], ""
    for _ in range(pages):
        r, _ = req("GET", "https://youtube.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50"
                          f"&playlistId={up}" + (f"&pageToken={page}" if page else ""), tok)
        for it in r.get("items", []):
            sn = it["snippet"]
            when = dt.datetime.fromisoformat(sn["publishedAt"].replace("Z", "+00:00"))
            if when >= cut:
                out.append((sn["title"], sn["resourceId"]["videoId"], when))
        page = r.get("nextPageToken")
        if not page:
            break
    return out


def same_story(titles, recent):
    """Reason string if a recent upload tells the same story (Nov 24: two breaking-news runs posted '39 million PS5
    players' twice in 3 hours with different wording, because the first run couldn't push the registry). Same story =
    the same key number (2+ digits, e.g. 39 / 3.79 / 212) and half the key words shared, or 70% shared without one."""
    for t in titles:
        a = story_words(t)
        if len(a) < 3:
            continue
        for rt, vid, when in recent:
            b = story_words(rt)
            if not b:
                continue
            j = len(a & b) / len(a | b)
            big = {w for w in a & b if w.replace(".", "").isdigit() and len(w.replace(".", "")) >= 2}
            if (big and j >= 0.4) or j >= 0.7:
                return (f"the channel posted the same story {when:%b %d %H:%M} UTC: {rt!r} (https://youtu.be/{vid}); "
                        "a near-identical video hurts the channel")
    return None


CAPTION_KEY = 120  # normalized characters compared: the title plus the start of the description


def caption_key(caption):
    """The whole caption, normalized, cut to CAPTION_KEY characters. Not just the first line: two different posts
    can open with the same line ("GTA 6 is out now." / "GTA 6 is out now. Day two: ...")."""
    return norm((caption or "")[:2200])[:CAPTION_KEY]


def instagram_recent(call, uid, limit=40):
    """[(caption key, permalink, timestamp)] of the account's latest posts."""
    r = call("GET", f"{uid}/media", {"fields": "caption,permalink,timestamp", "limit": str(limit)})
    return [(caption_key(m.get("caption")), m.get("permalink", ""), m.get("timestamp", "")) for m in r.get("data", [])]


def instagram_duplicate(caption, recent):
    """Permalink of an existing post with the same caption (same first 120 normalized characters), else None.
    Short captions (under 40 characters) must match completely."""
    key = caption_key(caption)
    if not key:
        return None
    for k, link, _ in recent:
        if k == key and (len(key) >= 40 or norm(caption) == k):
            return link or "already posted"
    return None


def instagram_posted_today(recent):
    """Posts the account made today (US Eastern), whoever made them."""
    today = dt.datetime.now(ET).date()
    n = 0
    for _, _, ts in recent:
        try:
            when = dt.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S%z").astimezone(ET).date()
        except ValueError:
            continue
        n += when == today
    return n
