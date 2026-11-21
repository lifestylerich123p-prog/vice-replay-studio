"""Uploads an APPROVED episode to YouTube and schedules each upload for its posting time.

    python -m studio.youtube_upload episodes/<slug>.json --approve all
    python -m studio.youtube_upload episodes/<slug>.json --approve main,short       # only some
    python -m studio.youtube_upload episodes/<slug>.json --approve all --title 2   # use title option 2
    python -m studio.youtube_upload --test                                         # private test upload

Only run this after the owner approves in chat. Campaign clips are never uploaded by this script.
Needs YT_CLIENT_ID, YT_CLIENT_SECRET and YT_REFRESH_TOKEN (environment settings; get the refresh token
once with tools/youtube_auth.py on the owner's computer).
What it sets: title, description, tags, Gaming category, not made for kids, scheduled publish time
(status.publishAt, US Eastern posting schedule), custom thumbnail A on the main video, and the pinned-comment
text posted as the first comment (pinning is manual: YouTube's API can't pin). Not possible through the API:
Test & Compare thumbnails, "Related video" on Shorts, pinning. Results go to output/<slug>/uploaded.json, and a
second run skips anything already uploaded.
"""
import argparse
import datetime as dt
import json
from urllib.parse import parse_qs, urlparse
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

from .review_page import extra_time, times_for

ROOT = Path(__file__).resolve().parent.parent
ET = ZoneInfo("America/New_York")


def token():
    need = ["YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"]
    missing = [k for k in need if not os.environ.get(k)]
    if missing:
        sys.exit("Missing " + ", ".join(missing) + ": add them in the environment's settings (see tools/youtube_auth.py).")
    data = urllib.parse.urlencode({"client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
                                   "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request("https://oauth2.googleapis.com/token", data=data), timeout=30) as r:
            return json.load(r)["access_token"]
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="ignore")
        if "invalid_grant" in body:
            sys.exit("YOUTUBE CONNECTION EXPIRED: the weekly YouTube permission ran out. Reconnect on your Mac with "
                     "tools/youtube_auth.py (Terminal step) and paste the new YT_REFRESH_TOKEN into the environment "
                     "settings. Until then, upload by hand from the review page.")
        sys.exit(f"YouTube sign-in failed ({e.code}): {body[:300]}")


def req(method, url, tok, body=None, ctype="application/json", headers=None):
    data = json.dumps(body).encode() if isinstance(body, (dict, list)) else body
    h = {"Authorization": f"Bearer {tok}", **({"Content-Type": ctype} if data is not None else {}), **(headers or {})}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, method=method, headers=h), timeout=600) as r:
            raw = r.read()
            return (json.loads(raw) if raw else {}), r.headers
    except urllib.error.HTTPError as e:
        sys.exit(f"YouTube error {e.code} on {method} {url.split('?')[0]}: {e.read().decode(errors='ignore')[:600]}")


def upload(tok, path, title, description, tags, publish_at=None, privacy="public", es=None):
    status = {"selfDeclaredMadeForKids": False, "embeddable": True}
    if publish_at:
        status.update(privacyStatus="private", publishAt=publish_at)
    else:
        status["privacyStatus"] = privacy
    meta = {"snippet": {"title": title[:100], "description": description[:4900], "tags": tags[:30],
                        "categoryId": "20", "defaultLanguage": "en", "defaultAudioLanguage": "en"},
            "status": status}
    parts = "snippet,status"
    if es and es.get("title"):
        # Spanish title/description: YouTube shows them to Spanish-speaking viewers automatically
        meta["localizations"] = {"es": {"title": es["title"][:100], "description": (es.get("description") or "")[:4900]}}
        parts += ",localizations"
    size = Path(path).stat().st_size
    _, h = req("POST", f"https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part={parts}",
               tok, meta, headers={"X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)})
    loc = h["Location"]
    with open(path, "rb") as f:
        video, _ = req("PUT", loc, tok, f.read(), ctype="video/mp4")
    return video


def set_thumbnail(tok, vid, jpg):
    if Path(jpg).exists():
        req("POST", f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={vid}", tok,
            Path(jpg).read_bytes(), ctype="image/jpeg")


def comment(tok, vid, text):
    if text:
        req("POST", "https://youtube.googleapis.com/youtube/v3/commentThreads?part=snippet", tok,
            {"snippet": {"videoId": vid, "topLevelComment": {"snippet": {"textOriginal": text}}}})


def register_upload(slug, key, vid, title):
    """Committed registry (content/learn/uploads.json): YouTube id -> episode slug + item, so scheduled runs
    (title swaps, retention, dashboard) know which script made which video even without the output/ folder."""
    reg_file = ROOT / "content" / "learn" / "uploads.json"
    reg = json.loads(reg_file.read_text()) if reg_file.exists() else {}
    reg[vid] = {"slug": slug, "item": key, "title": title, "uploaded": dt.datetime.now(dt.timezone.utc).isoformat()[:19]}
    reg_file.parent.mkdir(parents=True, exist_ok=True)
    reg_file.write_text(json.dumps(reg, indent=1, ensure_ascii=False))


def reply(tok, parent_id, text):
    req("POST", "https://youtube.googleapis.com/youtube/v3/comments?part=snippet", tok,
        {"snippet": {"parentId": parent_id, "textOriginal": text}})


def post_replies(tok, ep, done, done_file):
    """Post the approved comment_replies (each has the comment's url with &lc=<comment id>). Skips ones already sent."""
    sent = done.setdefault("replies", [])
    for r in ep.get("comment_replies", []):
        cid = parse_qs(urlparse(r.get("url", "")).query).get("lc", [None])[0]
        if not cid or not r.get("reply") or cid in sent:
            continue
        try:
            reply(tok, cid, r["reply"])
            sent.append(cid)
            print(f"replied to {r.get('author', '?')}: {r['reply'][:60]}")
        except SystemExit as e:
            print(f"! reply to {r.get('author', '?')} failed: {e}")
    done_file.parent.mkdir(parents=True, exist_ok=True)
    done_file.write_text(json.dumps(done, indent=2))


def spanish_srt(timings_file):
    """Spanish subtitles from the episode's per-segment Spanish text, timed to the narration."""
    if not Path(timings_file).exists():
        return None
    segs = [x for x in json.loads(Path(timings_file).read_text()) if x.get("text_es")]
    if not segs:
        return None

    def ts(t):
        ms = int(round(t * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    cues, n = [], 0
    for sg in segs:
        words = sg["text_es"].split()
        k = max(1, -(-len(words) // 8))  # number of lines, then split the words evenly across them
        size = -(-len(words) // k)
        chunks = [" ".join(words[i:i + size]) for i in range(0, len(words), size)]
        span, t = sg["end"] - sg["start"], sg["start"]
        total = sum(len(c) for c in chunks) or 1
        for c in chunks:
            d = span * len(c) / total
            n += 1
            cues.append(f"{n}\n{ts(t)} --> {ts(t + d)}\n{c}\n")
            t += d
    return "\n".join(cues)


def upload_caption(tok, vid, srt, lang="es", name="Español"):
    boundary = "vrboundary7f3a"
    meta = json.dumps({"snippet": {"videoId": vid, "language": lang, "name": name, "isDraft": False}})
    body = (f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n{meta}\r\n"
            f"--{boundary}\r\nContent-Type: application/octet-stream\r\n\r\n{srt}\r\n--{boundary}--").encode()
    req("POST", "https://www.googleapis.com/upload/youtube/v3/captions?uploadType=multipart&part=snippet", tok, body,
        ctype=f"multipart/related; boundary={boundary}")


PLAYLISTS = {"main": "GTA 6 News & Guides", "short": "GTA 6 Shorts", "news": "GTA 6 Streamer & Breaking News"}
_playlist_cache = {}


def add_to_playlist(tok, vid, title):
    """Adds the video to the named playlist, creating the playlist (public) the first time."""
    yt = "https://youtube.googleapis.com/youtube/v3/"
    if not _playlist_cache:
        r, _ = req("GET", yt + "playlists?part=snippet&mine=true&maxResults=50", tok)
        _playlist_cache.update({p["snippet"]["title"]: p["id"] for p in r.get("items", [])})
    if title not in _playlist_cache:
        r, _ = req("POST", yt + "playlists?part=snippet,status", tok,
                   {"snippet": {"title": title, "description": f"{title} from Vice Replay: GTA's wildest moments. On replay.",
                                "defaultLanguage": "en"}, "status": {"privacyStatus": "public"}})
        _playlist_cache[title] = r["id"]
    existing, _ = req("GET", yt + f"playlistItems?part=id&playlistId={_playlist_cache[title]}&videoId={vid}", tok)
    if existing.get("items"):
        return  # already in this playlist
    # a brand-new playlist (or video) can briefly return 409/503; wait and retry a few times
    import time
    for attempt in range(4):
        try:
            req("POST", yt + "playlistItems?part=snippet", tok,
                {"snippet": {"playlistId": _playlist_cache[title], "resourceId": {"kind": "youtube#video", "videoId": vid}}})
            return
        except SystemExit:
            if attempt == 3:
                raise
            time.sleep(5 * (attempt + 1))


def slot(day, hhmm):
    """'3:30 PM' on day (ET) -> RFC3339 UTC, or None if that time has already passed (publish now)."""
    t = dt.datetime.strptime(hhmm, "%I:%M %p").time()
    when = dt.datetime.combine(day, t, ET)
    if when <= dt.datetime.now(ET) + dt.timedelta(minutes=20):
        return None
    return when.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_short_txt(p):
    txt = Path(p).read_text() if Path(p).exists() else ""
    title = txt.split("TITLE\n", 1)[-1].split("\n", 1)[0].strip() if "TITLE" in txt else ""
    desc = txt.split("DESCRIPTION\n", 1)[-1].strip() if "DESCRIPTION" in txt else ""
    return title, desc


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episode", nargs="?")
    ap.add_argument("--approve", default="", help="all, or a comma list of: main, short, news, replies (or a Short id); all includes replies")
    ap.add_argument("--title", type=int, default=1, help="which title option to use for the main video (1-3)")
    ap.add_argument("--date", help="posting date YYYY-MM-DD (default today, ET)")
    ap.add_argument("--at", help='override the posting time for every approved item, e.g. "9:30 PM" (ET)')
    ap.add_argument("--now", action="store_true", help="publish immediately (public) instead of at the schedule times")
    ap.add_argument("--test", action="store_true", help="upload a 5-second private test video and report its status")
    ap.add_argument("--comment", nargs=2, metavar=("VIDEO_ID", "TEXT"), action="append",
                    help="post TEXT as a comment on VIDEO_ID (repeatable); use once the video is public")
    a = ap.parse_args()
    tok = token()

    if a.comment:
        for vid, text in a.comment:
            try:
                comment(tok, vid, text)
                print(f"commented on {vid}")
            except SystemExit as e:
                print(f"! comment on {vid} failed: {e}")
        return

    if a.test:
        clip = ROOT / "output" / "_upload_test.mp4"
        clip.parent.mkdir(exist_ok=True)
        os.system(f"ffmpeg -v error -y -f lavfi -i color=c=0x0d0717:s=1080x1920:d=5 -f lavfi -i anullsrc=r=48000:cl=stereo "
                  f"-t 5 -c:v libx264 -pix_fmt yuv420p -c:a aac '{clip}'")
        v = upload(tok, clip, "Vice Replay upload test (delete me)", "Test upload from the Vice Replay machine.", [],
                   privacy="unlisted")
        print(json.dumps({"id": v["id"], "requested": "unlisted", "got": v.get("status", {}).get("privacyStatus"),
                          "url": f"https://www.youtube.com/watch?v={v['id']}"}, indent=2))
        print("If 'got' is 'private' instead of 'unlisted', YouTube locks uploads from this API project until it passes "
              "the YouTube API audit.")
        return

    if not a.episode or not a.approve:
        sys.exit("Give the episode and --approve (only after the owner approved in chat).")
    ep = json.loads(Path(a.episode).read_text())
    slug = ep["slug"]
    out = ROOT / "output" / slug
    day = dt.date.fromisoformat(a.date) if a.date else dt.datetime.now(ET).date()
    t_main, t_short, t_news = times_for(day)
    t_extra = extra_time(day)
    if a.at:
        t_main = t_short = t_news = t_extra = a.at
    want = {x.strip() for x in a.approve.split(",")}
    allow = lambda key: "all" in want or key in want
    done_file = out / "uploaded.json"
    done = json.loads(done_file.read_text()) if done_file.exists() else {}
    tags = [t.strip() for t in (out / "tags.txt").read_text().split(",")] if (out / "tags.txt").exists() else []

    if allow("replies"):
        post_replies(tok, ep, done, done_file)
    jobs = []
    if allow("main") and (out / f"{slug}.mp4").exists():
        titles = ep.get("title_options") or [ep["title"]]
        title = titles[min(a.title, len(titles)) - 1]
        pin_main = ep.get("pinned_comment")
        aff_cfg = ROOT / "content" / "affiliate.json"
        if pin_main and ep.get("pin_affiliate", True) and aff_cfg.exists():
            cfg = json.loads(aff_cfg.read_text())
            names = ep.get("affiliate", cfg.get("default_sets", []))
            first = next((it for n in names for it in cfg["sets"].get(n, [])), None) if cfg.get("enabled") else None
            if first:
                url = first[1] + ("&" if "?" in first[1] else "?") + "tag=" + cfg["tag"]
                pin_main = f"{pin_main}\n\n{first[0]}: {url} (affiliate link)"
        jobs.append(("main", out / f"{slug}.mp4", title, (out / "description.txt").read_text(), tags, t_main,
                     out / "thumbnail-a.jpg", pin_main, ep.get("es"), out / f"{slug}.timings.json",
                     ep.get("playlist") or PLAYLISTS["main"]))
    shorts = ([{"id": "", "pinned_comment": ep.get("short_pinned_comment") or ep.get("pinned_comment"),
                "playlist": ep.get("short_playlist")}]
              if ep.get("short") else []) + ep.get("shorts", [])
    for k, sh in enumerate(shorts):
        key = "short" if not sh.get("id") else sh["id"]
        name = f"{slug}-short" + (f"-{sh['id']}" if sh.get("id") else "")
        if not allow(key) or not (out / f"{name}.mp4").exists():
            continue
        title, desc = parse_short_txt(out / f"{name}.txt")
        es = sh.get("es") or (ep.get("short_es") if not sh.get("id") else None)
        playlist = sh.get("playlist") or (PLAYLISTS["short"] if not sh.get("id") else PLAYLISTS["news"])
        jobs.append((key, out / f"{name}.mp4", title or sh.get("title") or ep["title"], desc, tags,
                     (t_short if k == 0 else t_news if k == 1 else t_extra), None, sh.get("pinned_comment"), es, out / f"{name}.timings.json",
                     playlist))

    # the site guide may spell the slug "gta-6-..." while the episode says "gta6-..."
    gslug = next((g for g in (slug, slug.replace("gta6-", "gta-6-", 1))
                  if (ROOT / "site" / "guides" / f"{g}.json").exists()), "")
    guide_url = f"https://vicereplay.com/guides/{gslug}/" if gslug else ""
    for key, path, title, desc, tg, when, thumb, pin, es, timings, playlist in jobs:
        if guide_url and "vicereplay.com/guides" not in desc:
            desc = desc.rstrip() + f"\n\nGuide: {guide_url}"
        if key in done:
            print(f"skip {key}: already uploaded ({done[key]['url']})")
            continue
        publish_at = None if a.now else slot(day, when)
        print(f"uploading {key}: {title}  ->  {'now' if not publish_at else when + ' ET'}")
        v = upload(tok, path, title, desc, tg, publish_at, es=es)
        vid = v["id"]
        done[key] = {"id": vid, "url": f"https://www.youtube.com/watch?v={vid}", "title": title,
                     "scheduled_et": when if publish_at else "published now",
                     "privacy_returned": v.get("status", {}).get("privacyStatus")}
        done_file.write_text(json.dumps(done, indent=2))
        register_upload(slug, key, vid, title)
        srt = spanish_srt(timings)
        steps = [("thumbnail", lambda: thumb and set_thumbnail(tok, vid, thumb)),
                 ("spanish_subtitles", lambda: srt and upload_caption(tok, vid, srt)),
                 ("playlist", lambda: add_to_playlist(tok, vid, playlist))]
        done[key]["spanish_title"] = "yes" if es and es.get("title") else "no (episode has no 'es')"
        if publish_at:
            done[key]["comment"] = "pending: post after it goes live"
            done[key]["comment_text"] = pin or ""
        else:
            steps.append(("comment", lambda: comment(tok, vid, pin)))
        for step, fn in steps:
            try:
                fn()
                done[key][step] = "ok"
            except SystemExit as e:
                done[key][step] = f"failed: {e}"
                print(f"  ! {step} failed for {key}: {e}")
            done_file.write_text(json.dumps(done, indent=2))
    print(json.dumps(done, indent=2))
    later = [(d["id"], d["comment_text"], d["scheduled_et"]) for d in done.values()
             if isinstance(d, dict) and str(d.get("comment", "")).startswith("pending") and d.get("comment_text")]
    if later:
        last = max(later, key=lambda x: dt.datetime.strptime(x[2], "%I:%M %p"))[2]
        cmd = "python -m studio.youtube_upload " + " ".join(f"--comment {v} {json.dumps(t)}" for v, t, _ in later)
        print(f"\nCOMMENTS TO POST AFTER {last} ET (videos are private until then):\n{cmd}")


if __name__ == "__main__":
    main()
