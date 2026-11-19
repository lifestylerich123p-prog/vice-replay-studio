"""Post an approved Short to Instagram as a Reel (Instagram API with Instagram Login; Creator/Business account).

    python -m studio.instagram_upload output/<slug>/<file>.mp4 --caption "..."        # post now
    python -m studio.instagram_upload --check                                          # test the connection

Setup (once, owner): see content/instagram-setup.md. Needs:
- env var IG_USER_ID (the Instagram account's numeric id; not secret),
- an Instagram access token for graph.instagram.com saved as a network secret (Authorization: Bearer) via
  request_credential, so it never appears in files or chat.
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
API = "https://graph.instagram.com/v21.0/"


def call(method, path, params=None):
    data = urllib.parse.urlencode(params or {}).encode() if method == "POST" else None
    url = API + path + ("?" + urllib.parse.urlencode(params) if method == "GET" and params else "")
    # The proxy injects "Authorization: Bearer <token>" for graph.instagram.com; a dummy keeps clients happy.
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
    if not uid:
        sys.exit("IG_USER_ID is not set: Instagram isn't connected yet (content/instagram-setup.md).")
    if a.check:
        print(json.dumps(call("GET", "me", {"fields": "user_id,username,account_type"}), indent=1))
        return
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
