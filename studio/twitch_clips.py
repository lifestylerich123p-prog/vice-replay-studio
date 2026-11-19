"""Find a streamer's top Twitch clips (free, Twitch API) so campaign clips don't need hand-copied links.

    python -m studio.twitch_clips lacy                 # top clips of the last 24 h
    python -m studio.twitch_clips kreekcraft --hours 72 --top 20
    python -m studio.twitch_clips --campaigns          # every approved campaign with a "twitch_login"

Setup (once, owner; see content/twitch-setup.md): a Twitch developer app (dev.twitch.tv/console). Its Client ID is
not secret: env var TWITCH_CLIENT_ID. Its app access token is saved as a network secret for api.twitch.tv
(Authorization: Bearer) via request_credential, never in files or chat; it lasts about 60 days.
Prints clips best first and drops titles that point at moments we never post (violence against people, sexual
content, "murder", cutscenes). Writes output/twitch_clips.json. Downloading/editing happens in the main chat
(Everygen download_video on the clip URL, free), following .claude/commands/campaign-clips.md.
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.twitch.tv/helix/"
SKIP = re.compile(r"murder|kill(s|ed|ing)? (a |the )?(woman|girl|lady|cop|man|guy)|abus|threat|nud|naked|strip|"
                  r"boob|sex|cutscene|ending|spoiler|racis|slur", re.I)


def call(path, params):
    cid = os.environ.get("TWITCH_CLIENT_ID")
    if not cid:
        sys.exit("TWITCH_CLIENT_ID is not set: Twitch isn't connected yet (content/twitch-setup.md).")
    req = urllib.request.Request(API + path + "?" + urllib.parse.urlencode(params, doseq=True),
                                 headers={"Client-Id": cid, "Authorization": "Bearer proxy-injected"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Twitch API {e.code}: {e.read().decode(errors='ignore')[:300]}"
                 + (" (token expired? make a new one: content/twitch-setup.md)" if e.code == 401 else ""))


def top_clips(login, hours=24, top=15):
    users = call("users", {"login": login}).get("data", [])
    if not users:
        sys.exit(f"No Twitch user {login!r}.")
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    clips, cursor = [], None
    for _ in range(3):  # up to 300 clips
        params = {"broadcaster_id": users[0]["id"], "started_at": since, "first": 100}
        if cursor:
            params["after"] = cursor
        page = call("clips", params)
        clips += page.get("data", [])
        cursor = page.get("pagination", {}).get("cursor")
        if not cursor:
            break
    keep = [c for c in clips if not SKIP.search(c.get("title", "")) and c.get("duration", 0) >= 8]
    keep.sort(key=lambda c: -c.get("view_count", 0))
    return [{"title": c["title"], "views": c["view_count"], "seconds": round(c["duration"]), "url": c["url"],
             "created": c["created_at"][:16], "clipper": c.get("creator_name")} for c in keep[:top]]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("login", nargs="?")
    ap.add_argument("--hours", type=int, default=24)
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--campaigns", action="store_true")
    a = ap.parse_args()
    logins = [a.login] if a.login else []
    if a.campaigns:
        for f in sorted((ROOT / "content" / "campaigns").glob("*.json")):
            c = json.loads(f.read_text())
            if c.get("owner_approved") and c.get("twitch_login") and not str(c.get("status", "")).startswith("paused"):
                logins.append(c["twitch_login"])
    if not logins:
        sys.exit("Give a Twitch login or --campaigns.")
    report = {}
    for login in logins:
        report[login] = top_clips(login, a.hours, a.top)
        print(f"\n{login}: top clips of the last {a.hours} h")
        for c in report[login]:
            print(f"  {c['views']:>7,} views {c['seconds']:>3}s {c['created']}  {c['title'][:60]}  {c['url']}")
    out = ROOT / "output" / "twitch_clips.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
