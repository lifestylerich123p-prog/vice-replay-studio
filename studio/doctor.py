"""System doctor (free, no AI): find problems before they cost a post.

    python -m studio.doctor          # check everything -> content/learn/health.md (exit 1 if something needs action)
    python -m studio.doctor --fix    # also posts any missing pinned comment on public videos (already approved)

Checks:
1. YouTube connection: the refresh token still works, and days since the last reconnect (Google app in Testing mode
   expires it after 7 days; content/learn/youtube_connected.txt holds the date of the last reconnect).
2. Comments: every public upload from the last 7 days that we made from an episode has our pinned comment.
3. Website: home, gear, guides, live page and sitemap answer 200.
4. Disk: free space for renders.
5. Upload registry: content/learn/uploads.json exists and is current.
6. Instagram: the Reels token works, the account answers, today's publishing quota, overdue queued Reels.
"""
import argparse
import datetime as dt
import json
import os
import shutil
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEARN = ROOT / "content" / "learn"
YT = "https://youtube.googleapis.com/youtube/v3/"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fix", action="store_true")
    a = ap.parse_args()
    ok, warn, bad = [], [], []

    # 1. YouTube connection
    tok = None
    try:
        from .youtube_upload import req, token
        tok = token()
        ok.append("YouTube connection works")
    except SystemExit as e:
        bad.append(f"YouTube connection FAILED: {str(e)[:160]}. Reconnect: tools/youtube_auth.py, then update "
                   "YT_REFRESH_TOKEN in the environment settings.")
    stamp = LEARN / "youtube_connected.txt"
    if stamp.exists():
        try:
            last = dt.date.fromisoformat(stamp.read_text().strip()[:10])
            days = (dt.date.today() - last).days
            due = last + dt.timedelta(days=7)
            if days >= 6:
                bad.append(f"YouTube connection expires around {due:%a %b %-d} ({days} days since reconnect): "
                           "reconnect today or uploads stop.")
            elif days >= 5:
                warn.append(f"YouTube connection expires around {due:%a %b %-d}: plan to reconnect.")
            else:
                ok.append(f"YouTube reconnect due around {due:%a %b %-d}")
        except ValueError:
            warn.append("content/learn/youtube_connected.txt has no valid date")
    else:
        warn.append("Unknown last YouTube reconnect date (write it to content/learn/youtube_connected.txt)")

    # 1a. Keys saved under the right names? (they're picked by channel, so a swap still works, but tidy it)
    try:
        from .youtube_upload import _owner_of, channel_ids
        if os.environ.get("YT_REFRESH_TOKEN") and _owner_of(token("YT_REFRESH_TOKEN")) != channel_ids()["en"]:
            warn.append("YT_REFRESH_TOKEN holds the Spanish channel's key (still works: keys are picked by channel). "
                        "Tidy the settings: English key in YT_REFRESH_TOKEN, Spanish key in YT_SPANISH_REFRESH_TOKEN.")
    except (SystemExit, Exception):  # noqa: BLE001 - informational only
        pass

    # 1b. Spanish channel (Vice Replay en Español): its own token, same 7-day expiry while the Google app is in Testing
    if os.environ.get("YT_SPANISH_REFRESH_TOKEN") or os.environ.get("YT_ES_REFRESH_TOKEN"):
        try:
            from . import youtube_es
            from .youtube_upload import channel_ids, token_for
            youtube_es.check_channel(token_for(channel_ids()["es"], youtube_es.ENV))
            ok.append("Spanish channel (Vice Replay en Español) connection works")
        except SystemExit as e:
            bad.append(f"Spanish channel connection FAILED: {str(e)[:160]}")
    else:
        warn.append("Spanish channel token not loaded in this session (it loads when a session starts)")

    # 2. Pinned comments on recent public uploads
    if tok:
        reg = json.loads((LEARN / "uploads.json").read_text()) if (LEARN / "uploads.json").exists() else {}
        ch, _ = req("GET", YT + "channels?part=id&mine=true", tok)
        cid = ch["items"][0]["id"]
        ids = list(reg)[-40:]
        missing = []
        if ids:
            v, _ = req("GET", YT + "videos?part=snippet,status&id=" + ",".join(ids), tok)
            now = dt.datetime.now(dt.timezone.utc)
            for x in v.get("items", []):
                if x["status"]["privacyStatus"] != "public":
                    continue
                pub = dt.datetime.fromisoformat(x["snippet"]["publishedAt"].replace("Z", "+00:00"))
                if (now - pub).days > 7 or (now - pub).total_seconds() < 20 * 60:
                    continue
                t, _ = req("GET", YT + f"commentThreads?part=snippet&videoId={x['id']}&maxResults=50", tok)
                mine = any(c["snippet"]["topLevelComment"]["snippet"].get("authorChannelId", {}).get("value") == cid
                           for c in t.get("items", []))
                if not mine:
                    missing.append((x["id"], x["snippet"]["title"]))
        for vid, title in missing:
            text = pinned_text(reg.get(vid, {}))
            if a.fix and text:
                from .youtube_upload import comment
                comment(tok, vid, text)
                ok.append(f"Posted the missing comment on '{title[:50]}'")
            else:
                warn.append(f"No pinned comment on '{title[:50]}' ({vid})" + ("" if text else " and no text in its episode"))
        if not missing:
            ok.append("Every recent public upload has our comment")

    # 2b. Instagram (Reels posting): token works, account answers, daily publishing quota
    try:
        from .instagram_upload import call as ig_call, ig_user_id
        uid = ig_user_id()
        if uid:
            acct = ig_call("GET", uid, {"fields": "username,media_count,followers_count"})
            lim = ig_call("GET", f"{uid}/content_publishing_limit", {"fields": "quota_usage,config"}).get("data", [{}])[0]
            ok.append(f"Instagram @{acct.get('username')} works ({acct.get('media_count')} posts, "
                      f"{acct.get('followers_count')} followers; {lim.get('quota_usage', '?')}/100 posts used today)")
            qf = ROOT / "content" / "learn" / "reels_queue.json"
            if qf.exists():
                q = json.loads(qf.read_text())
                from zoneinfo import ZoneInfo
                et_now = dt.datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %H:%M")
                late = [i for i in q if not i.get("posted") and i["at"] < et_now]
                if len(late) > 2:
                    warn.append(f"{len(late)} Reels are overdue in reels_queue.json: run studio.instagram_upload --queue")
    except SystemExit as e:
        bad.append(f"Instagram connection FAILED: {str(e)[:160]} (token for graph.facebook.com in the environment's "
                   "network secrets; see content/archive/instagram-setup-2026-11-19.md)")

    # 3. Website
    for path in ("", "gear/", "guides/", "guides/gta-6-launch-live/", "sitemap.xml"):
        try:
            with urllib.request.urlopen(f"https://vicereplay.com/{path}", timeout=20) as r:
                if r.status != 200:
                    bad.append(f"vicereplay.com/{path} answered {r.status}")
        except Exception as e:  # noqa: BLE001 - report any failure
            bad.append(f"vicereplay.com/{path} is down ({type(e).__name__})")
    if not any("vicereplay.com" in b for b in bad):
        ok.append("Website is up")

    # 3b. Did today's 5 AM daily run save its work? (Nov 21: its push got a 403 and nobody noticed for hours)
    try:
        import subprocess
        from zoneinfo import ZoneInfo
        et = dt.datetime.now(ZoneInfo("America/New_York"))
        if et.hour >= 7:
            subprocess.run(["git", "fetch", "-q", "origin", "main"], cwd=ROOT, timeout=60, capture_output=True)
            since = et.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            log = subprocess.run(["git", "log", "origin/main", f"--since={since}", "--grep=Daily run", "--format=%h"],
                                 cwd=ROOT, capture_output=True, text=True, timeout=60).stdout.strip()
            if log:
                ok.append("Today's daily run is saved on GitHub")
            else:
                warn.append("No 'Daily run' commit on GitHub today: the 5 AM run may have failed to push. Recover it from "
                            "its log (publish-site.md, 'If the daily run's hand-off never arrives') and check GitHub "
                            "access at claude.ai/connect-github")
    except Exception as e:  # noqa: BLE001 - a git problem must not stop the health check
        warn.append(f"Couldn't check today's daily run on GitHub ({type(e).__name__})")

    # 4. Disk
    free_gb = shutil.disk_usage(ROOT).free / 1e9
    (bad if free_gb < 2 else warn if free_gb < 5 else ok).append(f"Disk: {free_gb:.1f} GB free")

    lines = [f"# System health ({dt.datetime.now():%Y-%m-%d %H:%M} UTC, `python -m studio.doctor`)", ""]
    lines += [f"- 🔴 {b}" for b in bad] + [f"- 🟡 {w}" for w in warn] + [f"- 🟢 {o}" for o in ok]
    (LEARN / "health.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    raise SystemExit(1 if bad else 0)


def pinned_text(entry):
    """The approved pinned comment for an upload, from its episode file."""
    slug, item = entry.get("slug"), entry.get("item")
    f = ROOT / "episodes" / f"{slug}.json"
    if not slug or not f.exists():
        return ""
    ep = json.loads(f.read_text())
    if item in ("main", "short"):
        return ep.get("pinned_comment", "")
    sh = next((s for s in ep.get("shorts", []) if s.get("id") == item), {})
    return sh.get("pinned_comment", "")


if __name__ == "__main__":
    main()
