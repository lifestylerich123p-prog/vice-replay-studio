"""Post an approved Short to Instagram as a Reel (Instagram API with Instagram Login; Creator/Business account).

    python -m studio.instagram_upload output/<slug>/<file>.mp4 --caption "..."        # post now
    python -m studio.instagram_upload --check                                          # test the connection

Setup (once, owner): see content/instagram-setup.md. Needs:
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
    a = ap.parse_args()
    uid = os.environ.get("IG_USER_ID")
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
        sys.exit("IG_USER_ID is not set: Instagram isn't connected yet (content/instagram-setup.md).")
    if not a.video:
        sys.exit("Give the video file.")
    url, dest = host_publicly(a.video)
    try:
        c = call("POST", f"{uid}/media", {"media_type": "REELS", "video_url": url, "caption": a.caption[:2200],
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
        print(f"Posted Reel: {info.get('permalink', pub['id'])}")
    finally:
        unhost(dest)


if __name__ == "__main__":
    main()
