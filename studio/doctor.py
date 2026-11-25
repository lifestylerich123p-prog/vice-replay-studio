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



def queue_clashes():
    """Booked approved_queue items whose slug was already uploaded as a DIFFERENT video (the episode file was overwritten
    by a new Short): the uploader matches by slug and would skip the new one as already posted."""
    import re as _re
    ROOT = LEARN.parent.parent
    try:
        q = json.loads((LEARN / "approved_queue.json").read_text())["items"]
        ups = json.loads((LEARN / "uploads.json").read_text())
    except (OSError, ValueError, KeyError):
        return []
    norm = lambda s: _re.sub(r"#\w+|[^a-z0-9]+", " ", str(s).lower()).strip()

    def titles(obj, acc):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if "title" in k:
                    for x in (v if isinstance(v, list) else [v]):
                        if isinstance(x, str):
                            acc.add(norm(x))
                titles(v, acc)
        elif isinstance(obj, list):
            for v in obj:
                titles(v, acc)
        return acc
    today = dt.date.today().isoformat()
    out = []
    for i in q:
        if i.get("es_only") or (i.get("en") or [""])[0] < today:
            continue
        uploaded = [u for u in ups.values() if (u.get("slug"), u.get("item")) == (i.get("slug"), i.get("item"))]
        if not uploaded:
            continue
        try:
            ep = json.loads((ROOT / "episodes" / f"{i['slug']}.json").read_text())
        except (OSError, ValueError):
            continue
        known = titles(ep, set())
        for u in uploaded:
            if norm(u.get("title", "")) not in known:
                out.append(f"Booked {i['slug']} {i['item']} ({i['en'][0]}) shares its slug with an older upload "
                           f"(\"{u.get('title', '')[:50]}\"): the uploader would skip it as already posted; rename the episode")
                break
    return out

def item_segments(ep, item):
    """The segments one booked queue item plays: the main video, the Short, or a named extra Short (news/tips/...)."""
    if item == "main":
        return ep.get("segments") or []
    if item == "short":
        sh = ep.get("short")
        return (sh.get("segments") if isinstance(sh, dict) else sh) or []
    extra = next((s for s in ep.get("shorts") or [] if isinstance(s, dict) and s.get("id") == item), {})
    return extra.get("segments") or []


def map_gaps(items, load_episode, start, days=7):
    """Days (ISO dates) from `start` with no English map Short booked. Owner, Nov 25: "Start posting the maps videos at
    least one a day". A map Short is a Short with an official-map card (chart type "map")."""
    have = set()
    for i in items:
        en = i.get("en")
        if not en or i.get("es_only") or i.get("item", "short") == "main":
            continue
        try:
            segs = item_segments(load_episode(i["slug"]), i.get("item", "short"))
        except (OSError, ValueError, KeyError):
            continue
        if any(isinstance(s.get("chart"), dict) and s["chart"].get("type") == "map" for s in segs):
            have.add(en[0])
    return [d for d in ((start + dt.timedelta(days=k)).isoformat() for k in range(days)) if d not in have]


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
    # 1a. Booked Shorts that reuse an uploaded slug (Nov 24: a new "Dexter" map Short reused the slug of an old private
    # one, so the uploader would have treated it as already posted). Every booked item must be new.
    for msg in queue_clashes():
        bad.append(msg)
    # 1a2. At least one map Short a day (owner, Nov 25: "Start posting the maps videos at least one a day")
    try:
        root = LEARN.parent.parent
        gaps = map_gaps(json.loads((LEARN / "approved_queue.json").read_text())["items"],
                        lambda s: json.loads((root / "episodes" / f"{s}.json").read_text()), dt.date.today())
        if gaps:
            warn.append(f"No map Short booked on {', '.join(gaps)} (owner Nov 25: at least one map video a day): "
                        f"move one in from a day with two or more, or make a new \"where is X\" Short")
        else:
            ok.append("A map Short is booked every day for the next 7 days")
    except (OSError, ValueError, KeyError) as e:
        warn.append(f"Map-a-day check failed: {type(e).__name__}")
    # 1c. Booked videos in the next 48 h must be rendered, 30 fps and past their quality check (Nov 24)
    try:
        from . import readiness
        late = readiness.problems(hours=48)
        for w, s, it, lang, msg in late:
            bad.append(f"Booked {lang.upper()} {it} {s} ({w:%a %-I:%M %p}) isn't ready: {msg}. Re-render it now")
        if not late:
            ok.append("Every video booked in the next 48 h is rendered and passed its checks")
    except Exception as e:  # noqa: BLE001 - the health check must not crash
        warn.append(f"Readiness check failed: {type(e).__name__}")
    # 1b. The learner (Nov 23: it went 2 days without a refresh when the daily runs couldn't push)
    snap = LEARN / "channel.json"
    if snap.exists():
        try:
            checked = dt.datetime.fromisoformat(json.loads(snap.read_text())["checked"].replace("Z", "+00:00"))
            hrs = (dt.datetime.now(dt.timezone.utc) - checked).total_seconds() / 3600
            if hrs > 36:
                warn.append(f"Learner is {hrs / 24:.1f} days old (last refresh {checked:%b %-d}): run python -m "
                            f"studio.learn --mine so the scorecard sees the new Shorts")
            else:
                ok.append(f"Learner fresh ({hrs:.0f} h old)")
        except (ValueError, KeyError, OSError):
            warn.append("content/learn/channel.json can't be read: run python -m studio.learn --mine")
    stamp = LEARN / "youtube_connected.txt"
    if stamp.exists():
        try:
            text = stamp.read_text().strip()
            last = dt.date.fromisoformat(text[:10])
            days = (dt.date.today() - last).days
            due = last + dt.timedelta(days=7)
            if "production" in text:  # Nov 22: the Google app is published, so keys no longer expire after 7 days
                ok.append(f"YouTube keys from {last:%b %-d} (Google app in production: no 7-day expiry)")
            elif days >= 6:
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

    # 2c. Uploads missing from the registry (Nov 24: two breaking-news runs posted the same story because the first
    # couldn't push uploads.json). Any public video of ours that the registry doesn't know is a blind spot.
    try:
        chan = json.loads((ROOT / "content/learn/channel.json").read_text())
        reg = json.loads((ROOT / "content/learn/uploads.json").read_text())
        tracker = (ROOT / "content/campaigns/tracker.md").read_text() if (ROOT / "content/campaigns/tracker.md").exists() else ""
        unknown = [v for v in chan.get("videos", []) if v["id"] not in reg and v["id"] not in tracker
                   and not any(k in v.get("title", "") for k in ("LACY", "Lacy", "KreekCraft", "Tomo"))
                   and v.get("published", "") >= "2026-11-21"]
        if unknown:
            warn.append(f"{len(unknown)} upload(s) not in content/learn/uploads.json (posted by a run that couldn't push?): "
                        + ", ".join(f"{v['id']} {v['title'][:40]!r}" for v in unknown[:4])
                        + ". Register them so the duplicate guard and flop review see them.")
    except (OSError, ValueError):
        pass

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
    # 3a. Pre-launch wording left on the site ("comes out on November 19"...; owner Nov 24: "things are out of date")
    try:
        from .site_stale import freshness, scan
        for w in freshness(ROOT):
            warn.append("Website: " + w)
        stale = scan(ROOT.parent / "vicereplay-site")
        if stale:
            pages = sorted({p for p, _ in stale})
            warn.append(f"Website: {len(pages)} page(s) still use pre-launch wording ({', '.join(pages[:3])}): "
                        "fix in tools/site_guides.py or add a NOTICES note (python -m studio.site_stale lists them)")
    except Exception:  # noqa: BLE001 - a missing site checkout must not break the health check
        pass

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
