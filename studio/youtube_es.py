"""Spanish channel: post the Spanish-voice versions of our Shorts to "Vice Replay en Español" (Nov 21, 2026).

    python -m studio.youtube_es whoami                                   # which channel YT_ES_REFRESH_TOKEN belongs to
    python -m studio.youtube_es episodes/<slug>.json --approve short,news [--date YYYY-MM-DD] [--at "9:30 AM"]

studio.ship already renders `<name>-es.mp4` for every Short (Kokoro em_alex + text_es), and they were never posted.
Spanish GTA 6 Shorts are among the biggest in the market report (4-6M views each), so each Short gets a second chance
in a second feed at no extra production cost.

Setup (once, owner): create the channel in YouTube (Your channel -> Settings -> Add or manage channels -> Create a
channel), run tools/youtube_auth.py on the Mac and pick THAT channel on Google's screen, save the refresh token as
YT_ES_REFRESH_TOKEN in the environment settings, then run `whoami` and put the printed id in config/channel.json
("vice-replay-es" -> "channel_id"). Uploads refuse to run until the token's channel matches that id and is not the
English channel, so nothing Spanish can land on the main channel by mistake.

Same approval rule as the main channel: only items the owner approved in chat. Registry: content/learn/uploads-es.json
(kept apart so the main channel's stats, retention and dashboard stay clean).
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from . import postguard
from .review_page import extra_time, times_for
from .youtube_upload import (ET, ROOT, add_to_playlist, comment, req, slot, srt_from_timings, token, upload,
                             upload_caption, yt_safe)

ENV = "YT_ES_REFRESH_TOKEN"
REGISTRY = ROOT / "content" / "learn" / "uploads-es.json"
PLAYLIST = "GTA 6 en Español"
NOT_AFFILIATED = "Canal de fans: no afiliado a Rockstar Games ni a Take-Two Interactive."


def config():
    return json.loads((ROOT / "config" / "channel.json").read_text())["channels"]


def whoami(tok):
    r, _ = req("GET", "https://youtube.googleapis.com/youtube/v3/channels?part=snippet&mine=true", tok)
    it = (r.get("items") or [{}])[0]
    return it.get("id"), it.get("snippet", {}).get("title")


def check_channel(tok):
    """Refuse unless the Spanish token belongs to the registered Spanish channel (never the English one)."""
    cid, title = whoami(tok)
    cfg = config()
    want = cfg.get("vice-replay-es", {}).get("channel_id")
    if cid == cfg["vice-replay"]["channel_id"]:
        sys.exit(f"{ENV} belongs to the ENGLISH channel ({title}). Reconnect and pick the Spanish channel on Google's screen.")
    if not want:
        sys.exit(f"{ENV} belongs to '{title}' ({cid}). If that's the Spanish channel, put {cid} in config/channel.json "
                 f"(vice-replay-es -> channel_id), then run this again.")
    if cid != want:
        sys.exit(f"{ENV} belongs to '{title}' ({cid}), not the registered Spanish channel ({want}).")
    return cid


def jobs(ep, approved):
    """[(key, video name, es meta, pinned comment)] for the approved Shorts that have a Spanish title."""
    shorts = ([{"id": "", "es": ep.get("short_es"), "pinned_comment_es": ep.get("short_pinned_comment_es")
                or ep.get("pinned_comment_es")}] if ep.get("short") else []) + ep.get("shorts", [])
    out = []
    for sh in shorts:
        key = sh.get("id") or "short"
        if "all" not in approved and key not in approved:
            continue
        es = sh.get("es") or {}
        if not es.get("title"):
            print(f"skip {key}: no Spanish title in the episode (`short_es` / `es`)")
            continue
        name = f"{ep['slug']}-short" + (f"-{sh['id']}" if sh.get("id") else "") + "-es"
        out.append((key, name, es, sh.get("pinned_comment_es")))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode", help="episodes/<slug>.json, or 'whoami'")
    ap.add_argument("--approve", default="", help="short, news, ... or all (owner approval in chat only)")
    ap.add_argument("--date", help="posting date YYYY-MM-DD (default today, ET)")
    ap.add_argument("--at", help='posting time for every item, e.g. "9:30 AM" (ET)')
    a = ap.parse_args()
    tok = token(ENV)
    if a.episode == "whoami":
        cid, title = whoami(tok)
        print(f"{ENV} belongs to: {title} ({cid})")
        return
    check_channel(tok)
    ep = json.loads(Path(a.episode).read_text())
    slug, out = ep["slug"], ROOT / "output" / ep["slug"]
    day = dt.date.fromisoformat(a.date) if a.date else dt.datetime.now(ET).date()
    _main_t, short_t, news_t = times_for(day)
    approved = {x.strip() for x in a.approve.split(",") if x.strip()}
    done_file = out / "uploaded-es.json"
    done = json.loads(done_file.read_text()) if done_file.exists() else {}
    reg = json.loads(REGISTRY.read_text()) if REGISTRY.exists() else {}
    live = postguard.channel_titles(tok, req)
    for k, (key, name, es, pin) in enumerate(jobs(ep, approved)):
        video = out / f"{name}.mp4"
        if not video.exists():
            print(f"skip {key}: {video.name} not rendered (python -m studio.make_video {a.episode} --short --es)")
            continue
        if key in done or any(r.get("slug") == slug and r.get("item") == key for r in reg.values()):
            print(f"skip {key}: already on the Spanish channel")
            continue
        title = yt_safe(es["title"])
        if postguard.norm(title) in live:
            print(f"skip {key}: the Spanish channel already has '{title}'")
            continue
        when = a.at or (short_t if key == "short" else news_t if key == "news" else extra_time(day))
        publish_at = slot(day, when)
        desc = yt_safe((es.get("description") or "").strip() + f"\n\n{NOT_AFFILIATED}")
        tags = ["GTA 6", "GTA VI", "GTA 6 español", "Grand Theft Auto VI", "Vice City", "Leonida"]
        print(f"uploading {key} (es): {title} -> {'now' if not publish_at else when + ' ET'}")
        v = upload(tok, video, title, desc, tags, publish_at, lang="es")
        vid = v["id"]
        done[key] = {"id": vid, "url": f"https://www.youtube.com/watch?v={vid}", "title": title,
                     "scheduled_et": when if publish_at else "published now"}
        done_file.write_text(json.dumps(done, indent=2, ensure_ascii=False))
        reg[vid] = {"slug": slug, "item": key, "title": title, "uploaded": dt.datetime.now(dt.timezone.utc).isoformat()[:19]}
        REGISTRY.write_text(json.dumps(reg, indent=1, ensure_ascii=False))
        srt = srt_from_timings(out / f"{name}.timings.json", "text")
        for step, fn in (("subtitles", lambda: srt and upload_caption(tok, vid, srt, lang="es", name="Español")),
                         ("playlist", lambda: add_to_playlist(tok, vid, PLAYLIST)),
                         ("comment", lambda: pin and not publish_at and comment(tok, vid, pin))):
            try:
                fn()
                done[key][step] = "ok"
            except SystemExit as e:
                done[key][step] = f"failed: {e}"
        if pin and publish_at:
            done[key]["comment"] = f"pending: post after {when} ET"
        done_file.write_text(json.dumps(done, indent=2, ensure_ascii=False))
    print(json.dumps(done, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
