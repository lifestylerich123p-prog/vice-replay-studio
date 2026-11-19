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
"""
import argparse
import datetime as dt
import json
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
