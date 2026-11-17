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
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

from .review_page import times_for

ROOT = Path(__file__).resolve().parent.parent
ET = ZoneInfo("America/New_York")


def token():
    need = ["YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"]
    missing = [k for k in need if not os.environ.get(k)]
    if missing:
        sys.exit("Missing " + ", ".join(missing) + ": add them in the environment's settings (see tools/youtube_auth.py).")
    data = urllib.parse.urlencode({"client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
                                   "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"}).encode()
    with urllib.request.urlopen(urllib.request.Request("https://oauth2.googleapis.com/token", data=data), timeout=30) as r:
        return json.load(r)["access_token"]


def req(method, url, tok, body=None, ctype="application/json", headers=None):
    data = json.dumps(body).encode() if isinstance(body, (dict, list)) else body
    h = {"Authorization": f"Bearer {tok}", **({"Content-Type": ctype} if data is not None else {}), **(headers or {})}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, method=method, headers=h), timeout=600) as r:
            raw = r.read()
            return (json.loads(raw) if raw else {}), r.headers
    except urllib.error.HTTPError as e:
        sys.exit(f"YouTube error {e.code} on {method} {url.split('?')[0]}: {e.read().decode(errors='ignore')[:600]}")


def upload(tok, path, title, description, tags, publish_at=None, privacy="public"):
    status = {"selfDeclaredMadeForKids": False, "embeddable": True}
    if publish_at:
        status.update(privacyStatus="private", publishAt=publish_at)
    else:
        status["privacyStatus"] = privacy
    meta = {"snippet": {"title": title[:100], "description": description[:4900], "tags": tags[:30],
                        "categoryId": "20", "defaultLanguage": "en", "defaultAudioLanguage": "en"},
            "status": status}
    size = Path(path).stat().st_size
    _, h = req("POST", "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
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
        req("POST", "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet", tok,
            {"snippet": {"videoId": vid, "topLevelComment": {"snippet": {"textOriginal": text}}}})


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
    ap.add_argument("--approve", default="", help="all, or a comma list of: main, short, news (or a Short id)")
    ap.add_argument("--title", type=int, default=1, help="which title option to use for the main video (1-3)")
    ap.add_argument("--date", help="posting date YYYY-MM-DD (default today, ET)")
    ap.add_argument("--test", action="store_true", help="upload a 5-second private test video and report its status")
    a = ap.parse_args()
    tok = token()

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
    want = {x.strip() for x in a.approve.split(",")}
    allow = lambda key: "all" in want or key in want
    done_file = out / "uploaded.json"
    done = json.loads(done_file.read_text()) if done_file.exists() else {}
    tags = [t.strip() for t in (out / "tags.txt").read_text().split(",")] if (out / "tags.txt").exists() else []

    jobs = []
    if allow("main") and (out / f"{slug}.mp4").exists():
        titles = ep.get("title_options") or [ep["title"]]
        title = titles[min(a.title, len(titles)) - 1]
        jobs.append(("main", out / f"{slug}.mp4", title, (out / "description.txt").read_text(), tags, t_main,
                     out / "thumbnail-a.jpg", ep.get("pinned_comment")))
    shorts = ([{"id": "", "pinned_comment": ep.get("pinned_comment")}] if ep.get("short") else []) + ep.get("shorts", [])
    for k, sh in enumerate(shorts):
        key = "short" if not sh.get("id") else sh["id"]
        name = f"{slug}-short" + (f"-{sh['id']}" if sh.get("id") else "")
        if not allow(key) or not (out / f"{name}.mp4").exists():
            continue
        title, desc = parse_short_txt(out / f"{name}.txt")
        jobs.append((key, out / f"{name}.mp4", title or sh.get("title") or ep["title"], desc, tags,
                     t_short if k == 0 else t_news, None, sh.get("pinned_comment")))

    for key, path, title, desc, tg, when, thumb, pin in jobs:
        if key in done:
            print(f"skip {key}: already uploaded ({done[key]['url']})")
            continue
        publish_at = slot(day, when)
        print(f"uploading {key}: {title}  ->  {'now' if not publish_at else when + ' ET'}")
        v = upload(tok, path, title, desc, tg, publish_at)
        vid = v["id"]
        if thumb:
            set_thumbnail(tok, vid, thumb)
        comment(tok, vid, pin)
        done[key] = {"id": vid, "url": f"https://www.youtube.com/watch?v={vid}", "title": title,
                     "scheduled_et": when if publish_at else "published now",
                     "privacy_returned": v.get("status", {}).get("privacyStatus")}
        done_file.write_text(json.dumps(done, indent=2))
    print(json.dumps(done, indent=2))


if __name__ == "__main__":
    main()
