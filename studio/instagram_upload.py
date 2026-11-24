"""Post an approved Short to Instagram as a Reel (Instagram API with Instagram Login; Creator/Business account).

    python -m studio.instagram_upload output/<slug>/<file>.mp4 --caption "..."        # post now
    python -m studio.instagram_upload --check                                          # test the connection
    python -m studio.instagram_upload --episode episodes/<slug>.json [--item news]     # post an episode's Short
    python -m studio.instagram_upload --queue        # post the next due Reel of content/learn/reels_queue.json

Setup (once, owner): see content/archive/instagram-setup-2026-11-19.md. Needs:
- env var IG_USER_ID (the Instagram account's numeric id; not secret),
- a System User access token (Meta app > Instagram > API setup with unified login) saved as a network secret for
  graph.facebook.com (Authorization: Bearer) via request_credential, so it never appears in files or chat.
  (Older Instagram-Login apps: token for graph.instagram.com and IG_GRAPH_HOST=graph.instagram.com.)
Instagram fetches the video from a public URL, so the main chat puts the file on vicereplay.com/r/<random>.mp4
(GitHub Pages) for a few minutes and removes it after publishing. Same approval rules as YouTube: only post what
the owner approved (an approved Short may go to Reels too once the owner switched Reels posting on).
"""
import argparse
import json
import os
import secrets
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT.parent / "vicereplay-site"
# Meta's newer apps use the unified login (Facebook Login for Business, System User token) on graph.facebook.com;
# older "Instagram Login" apps use graph.instagram.com. IG_GRAPH_HOST picks one (default: the unified login).
API = f"https://{os.environ.get('IG_GRAPH_HOST', 'graph.facebook.com')}/v21.0/"


def call(method, path, params=None):
    data = urllib.parse.urlencode(params or {}).encode() if method == "POST" else None
    url = API + path + ("?" + urllib.parse.urlencode(params) if method == "GET" and params else "")
    # The proxy injects "Authorization: Bearer <token>" for the Graph host; a dummy keeps clients happy.
    req = urllib.request.Request(url, data=data, method=method, headers={"Authorization": "Bearer proxy-injected"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Instagram API {e.code}: {e.read().decode(errors='ignore')[:400]}")


def host_publicly(video):
    """Copy the video to vicereplay.com/r/<random>.mp4 via the site repo; returns (url, path to remove later)."""
    name = secrets.token_hex(8) + ".mp4"
    dest = SITE / "r" / name
    dest.parent.mkdir(exist_ok=True)
    shutil.copy(video, dest)
    git = ["git", "-C", str(SITE), "-c", "user.name=Vice Replay", "-c", "user.email=noreply@anthropic.com"]
    subprocess.run(["git", "-C", str(SITE), "pull", "-q", "--rebase", "origin", "main"])
    subprocess.run(git + ["add", str(dest)], check=True)
    subprocess.run(git + ["commit", "-qm", "Temporary Reel upload"], check=True)
    subprocess.run(["git", "-C", str(SITE), "push", "-q", "origin", "HEAD"], check=True)
    url = f"https://vicereplay.com/r/{name}"
    for _ in range(60):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=15) as r:
                if r.status == 200:
                    return url, dest
        except urllib.error.URLError:
            pass
        time.sleep(5)
    sys.exit("The temporary video URL never went live on vicereplay.com.")


def host_many(files):
    """Copy several files to vicereplay.com/r/ in one commit; returns ([urls], [paths to remove later])."""
    dests = []
    for f in files:
        d = SITE / "r" / (secrets.token_hex(8) + Path(f).suffix.lower())
        d.parent.mkdir(exist_ok=True)
        shutil.copy(f, d)
        dests.append(d)
    git = ["git", "-C", str(SITE), "-c", "user.name=Vice Replay", "-c", "user.email=noreply@anthropic.com"]
    subprocess.run(["git", "-C", str(SITE), "pull", "-q", "--rebase", "origin", "main"])
    subprocess.run(git + ["add"] + [str(d) for d in dests], check=True)
    subprocess.run(git + ["commit", "-qm", "Temporary Instagram upload"], check=True)
    subprocess.run(["git", "-C", str(SITE), "push", "-q", "origin", "HEAD"], check=True)
    urls = [f"https://vicereplay.com/r/{d.name}" for d in dests]
    for _ in range(60):
        try:
            if all(urllib.request.urlopen(urllib.request.Request(u, method="HEAD"), timeout=15).status == 200
                   for u in urls):
                return urls, dests
        except urllib.error.URLError:
            pass
        time.sleep(5)
    sys.exit("The temporary files never went live on vicereplay.com.")


def unhost_many(dests):
    git = ["git", "-C", str(SITE), "-c", "user.name=Vice Replay", "-c", "user.email=noreply@anthropic.com"]
    subprocess.run(git + ["rm", "-q"] + [str(d) for d in dests])
    subprocess.run(git + ["commit", "-qm", "Remove temporary Instagram upload"])
    subprocess.run(["git", "-C", str(SITE), "push", "-q", "origin", "HEAD"])


def post_carousel(uid, images, caption, first_comment=""):
    """Post 2-10 JPEG cards as one carousel post; returns the permalink."""
    urls, dests = host_many(images)
    try:
        kids = [call("POST", f"{uid}/media", {"image_url": u, "is_carousel_item": "true"})["id"] for u in urls]
        c = call("POST", f"{uid}/media", {"media_type": "CAROUSEL", "children": ",".join(kids),
                                          "caption": caption[:2200]})
        for _ in range(30):
            if call("GET", c["id"], {"fields": "status_code"}).get("status_code") == "FINISHED":
                break
            time.sleep(5)
        pub = call("POST", f"{uid}/media_publish", {"creation_id": c["id"]})
        info = call("GET", pub["id"], {"fields": "permalink"})
        if first_comment:
            try:
                call("POST", f"{pub['id']}/comments", {"message": first_comment[:2200]})
            except SystemExit as e:
                print(f"(first comment not posted: {e})")
        return info.get("permalink", pub["id"])
    finally:
        unhost_many(dests)


def post_image(uid, image, caption, first_comment=""):
    """Post one JPEG as a single-image post; returns the permalink."""
    urls, dests = host_many([image])
    try:
        c = call("POST", f"{uid}/media", {"image_url": urls[0], "caption": caption[:2200]})
        for _ in range(30):
            if call("GET", c["id"], {"fields": "status_code"}).get("status_code") == "FINISHED":
                break
            time.sleep(5)
        pub = call("POST", f"{uid}/media_publish", {"creation_id": c["id"]})
        info = call("GET", pub["id"], {"fields": "permalink"})
        if first_comment:
            try:
                call("POST", f"{pub['id']}/comments", {"message": first_comment[:2200]})
            except SystemExit as e:
                print(f"(first comment not posted: {e})")
        return info.get("permalink", pub["id"])
    finally:
        unhost_many(dests)


def unhost(dest):
    git = ["git", "-C", str(SITE), "-c", "user.name=Vice Replay", "-c", "user.email=noreply@anthropic.com"]
    subprocess.run(git + ["rm", "-q", str(dest)])
    subprocess.run(git + ["commit", "-qm", "Remove temporary Reel upload"])
    subprocess.run(["git", "-C", str(SITE), "push", "-q", "origin", "HEAD"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", nargs="?")
    ap.add_argument("--caption", default="")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--episode", help="post this episode's Short (with --item news|tips for the extra Shorts)")
    ap.add_argument("--item", default="short")
    ap.add_argument("--queue", action="store_true", help="post the next due Reel from content/learn/reels_queue.json")
    ap.add_argument("--carousel", help="post content/carousels/<slug>.json as a carousel (cards built by studio.ig_cards)")
    a = ap.parse_args()
    uid = ig_user_id()
    if a.check:
        print(json.dumps(call("GET", "me", {"fields": "id,name"}), indent=1))
        if "facebook" in API:  # list the Instagram business accounts this token can post to
            pages = call("GET", "me/accounts", {"fields": "name,instagram_business_account{id,username}"})
            for pg in pages.get("data", []):
                ig = pg.get("instagram_business_account")
                print(f"Page {pg.get('name')}: Instagram {ig.get('username') + ' id ' + ig.get('id') if ig else 'not linked'}")
        if uid:
            print(json.dumps(call("GET", uid, {"fields": "username,media_count"}), indent=1))
        else:
            print("Set IG_USER_ID to the Instagram id above.")
        return
    if not uid:
        sys.exit("IG_USER_ID is not set: Instagram isn't connected yet (content/archive/instagram-setup-2026-11-19.md).")
    if a.queue:
        return run_queue(uid)
    if a.carousel:
        from .ig_cards import build
        spec = json.loads(Path(a.carousel).read_text())
        cards = [str(f) for f in build(a.carousel)]
        print(f"Posted carousel: {post_carousel(uid, cards, spec['caption'], spec.get('first_comment', ''))}")
        return
    if a.episode:
        a.video, a.caption = episode_reel(a.episode, a.item)
    if not a.video:
        sys.exit("Give the video file.")
    comment = episode_comment(a.episode, a.item) if a.episode else ""
    print(f"Posted Reel: {post_reel(uid, a.video, a.caption, comment)}")


def ig_user_id():
    """IG_USER_ID from the environment, else the id recorded in content/owner.md (env vars load on session start)."""
    import re
    uid = os.environ.get("IG_USER_ID")
    if not uid:
        m = re.search(r"IG_USER_ID (\d{10,})", (ROOT / "content" / "owner.md").read_text())
        uid = m.group(1) if m else None
    return uid


def post_reel(uid, video, caption, first_comment=""):
    url, dest = host_publicly(video)
    try:
        c = call("POST", f"{uid}/media", {"media_type": "REELS", "video_url": url, "caption": caption[:2200],
                                          "share_to_feed": "true"})
        cid = c["id"]
        for _ in range(60):
            st = call("GET", cid, {"fields": "status_code,status"})
            if st.get("status_code") == "FINISHED":
                break
            if st.get("status_code") == "ERROR":
                sys.exit(f"Instagram couldn't process the video: {st.get('status')}")
            time.sleep(10)
        pub = call("POST", f"{uid}/media_publish", {"creation_id": cid})
        info = call("GET", pub["id"], {"fields": "permalink"})
        if first_comment:  # same question we pin on YouTube, to start the comments
            try:
                call("POST", f"{pub['id']}/comments", {"message": first_comment[:2200]})
            except SystemExit as e:
                print(f"(first comment not posted: {e})")
        return info.get("permalink", pub["id"])
    finally:
        unhost(dest)


def episode_comment(path, item="short"):
    ep = json.loads(Path(path).read_text())
    if item in (None, "", "short"):
        return ep.get("short_pinned_comment") or ep.get("pinned_comment", "")
    return next((x.get("pinned_comment", "") for x in ep.get("shorts", []) if x.get("id") == item), "")


def episode_reel(path, item="short"):
    """The English Short of an episode and an Instagram caption built from its title, description and hashtags."""
    ep = json.loads(Path(path).read_text())
    slug = ep["slug"]
    if item in (None, "", "short"):
        name, title, desc = f"{slug}-short", ep.get("short_title", ep["title"]), ep.get("short_description", "")
    else:
        sh = next(x for x in ep.get("shorts", []) if x.get("id") == item)
        name, title, desc = f"{slug}-short-{item}", sh.get("title", ep["title"]), sh.get("description", "")
    title = title.replace("#Shorts", "").strip()
    tags = " ".join(dict.fromkeys(ep.get("tiktok_hashtags", ["#gta6", "#gtavi", "#gaming"]) + ["#gta6news"]))
    # Meta (help.instagram.com/761121959519495): realistic AI-made audio, e.g. an AI voiceover, must be disclosed; the
    # API can't set the "AI info" label, so the caption says it (Nov 23 research)
    # Nov 24 (studio.ig_stats): our best Reels were practical tips with a save/screenshot nudge ("First 3 settings"
    # 119 likes, "screenshot this" 41); where-to-find and how-to Reels get the nudge as their first line
    save = ""
    if ep.get("series") in ("Map Spots", "How To") or any(w in title.lower() for w in ("where", "how to", "steps")):
        save = "📌 Save this for when you play.\n\n"
    caption = (f"{save}{title}\n\n{desc}\n\n🎙️ AI narration · our own graphics and research\n"
               f"Follow @vice.replaytv for GTA 6 every day.\n{tags}")
    return str(ROOT / "output" / slug / f"{name}.mp4"), caption


QUEUE = ROOT / "content" / "learn" / "reels_queue.json"


MAX_PER_DAY = int(os.environ.get("IG_MAX_PER_DAY", "4"))


def run_queue(uid):
    """Post the first due, unposted item of content/learn/reels_queue.json (one per run keeps Reels spaced out).
    Items: {"at": "2026-11-19 11:30" (ET), "video": path | "episode": path + "item", "caption": ..., "campaign": ...},
    {"at", "carousel": spec path} or {"at", "image": jpg path, "caption", "comment"}."""
    import datetime as dt
    from zoneinfo import ZoneInfo
    from . import postguard
    q = json.loads(QUEUE.read_text()) if QUEUE.exists() else []
    now = dt.datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %H:%M")
    posted_today = sum(1 for i in q if str(i.get("posted_at", "")).startswith(now[:10]) and str(i.get("posted", "")).startswith("http"))
    # another chat may have posted from its own copy of the queue: count and compare against the real account
    recent = postguard.instagram_recent(call, uid)
    posted_today = max(posted_today, postguard.instagram_posted_today(recent))
    if posted_today >= MAX_PER_DAY:  # Nov 19: Meta restricted ads after 11 API posts on day one; new accounts go slow
        print(f"Daily limit reached ({posted_today}/{MAX_PER_DAY} posts today): due items wait for the next run tomorrow.")
        return
    done_at = None  # campaign clips sharing one time slot go out together (owner: "two at the time")
    for it in q:
        if it.get("posted") or it["at"] > now:
            continue
        if done_at and (it["at"] != done_at or not it.get("campaign")):
            break
        if it.get("carousel"):
            cap = json.loads((ROOT / it["carousel"]).read_text()).get("caption", "")
        elif it.get("episode"):
            from .vice import viewcheck
            ep = json.loads((ROOT / it["episode"]).read_text())
            item = it.get("item") or "short"
            segs = ep.get("short") if item == "short" else next(
                (x.get("segments") for x in ep.get("shorts", []) if x.get("id") == item), [])
            if viewcheck.footage_segments(ep, segs) or ep.get("paused"):
                it["posted"] = "skipped: the Short shows trailer images (owner Nov 23: lettering/modern cards only)"
                QUEUE.write_text(json.dumps(q, indent=1, ensure_ascii=False))
                print(f"skip {it['episode']}: trailer images (owner Nov 23 rule)")
                continue
            cap = episode_reel(it["episode"], it.get("item"))[1]
        else:
            cap = it.get("caption", "")
        dup = postguard.instagram_duplicate(cap, recent)
        if dup:  # the same caption is already on the account: another chat/run posted it from its own queue copy
            it["posted"], it["found_on_instagram"] = dup, now
            QUEUE.write_text(json.dumps(q, indent=1, ensure_ascii=False))
            print(f"Already on Instagram (same caption, posted by another chat or run): {dup}. Not re-posted.")
            continue  # nothing was posted by this run, so the next due item may still go
        if it.get("carousel"):
            from .ig_cards import build
            spec = json.loads((ROOT / it["carousel"]).read_text())
            cards = [str(f) for f in build(ROOT / it["carousel"])]
            it["posted"] = post_carousel(uid, cards, spec["caption"], spec.get("first_comment", ""))
            it["posted_at"] = now
            QUEUE.write_text(json.dumps(q, indent=1, ensure_ascii=False))
            print(f"Posted carousel: {it['posted']}")
            break
        if it.get("image"):  # single-image post: {"image": path, "caption": ..., "comment": ...}
            it["posted"] = post_image(uid, str(ROOT / it["image"]), it["caption"], it.get("comment", ""))
            it["posted_at"] = now
            QUEUE.write_text(json.dumps(q, indent=1, ensure_ascii=False))
            print(f"Posted image: {it['posted']}")
            break
        video, caption = (episode_reel(it["episode"], it.get("item")) if it.get("episode")
                          else (str(ROOT / it["video"]), it["caption"]))
        if not Path(video).exists() and it.get("episode") and (ROOT / it["episode"]).exists():
            # output/ isn't committed: after a fresh container the Short is gone, so render it again from its episode
            print(f"{Path(video).name} is missing (new container?): rendering it again from {it['episode']}")
            import subprocess, sys as _sys
            subprocess.run([_sys.executable, "-m", "studio.make_video", str(ROOT / it["episode"]), "--short"],
                           cwd=ROOT, timeout=2400)
        if not Path(video).exists():
            it["posted"] = "skipped: file missing"
            continue
        comment = episode_comment(it["episode"], it.get("item")) if it.get("episode") else it.get("comment", "")
        it["posted"] = post_reel(uid, video, caption, comment)
        it["posted_at"] = now
        QUEUE.write_text(json.dumps(q, indent=1, ensure_ascii=False))
        print(f"Posted Reel ({it.get('campaign') or 'Vice Replay'}): {it['posted']}")
        if it.get("campaign"):
            print(f"CAMPAIGN: submit this Reel on the {it['campaign']} page within 30 minutes.")
            done_at = done_at or it["at"]
            continue
        break
    if not any(i.get("posted_at") == now for i in q):
        print("No Reel due right now.")
    left = [i for i in q if not i.get("posted")]
    print(f"{len(left)} Reel(s) still queued" + (f"; next at {min(i['at'] for i in left)} ET" if left else ""))
    QUEUE.write_text(json.dumps(q, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
