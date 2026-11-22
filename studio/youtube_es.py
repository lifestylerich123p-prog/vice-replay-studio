"""Spanish channel: post the Spanish-voice versions of our Shorts to "Vice Replay en Español" (Nov 21, 2026).

    python -m studio.youtube_es whoami                                   # which channel YT_ES_REFRESH_TOKEN belongs to
    python -m studio.youtube_es brand                                    # Spanish description, keywords, banner
    python -m studio.youtube_es comment VIDEO_ID "texto"                 # pinned question, once the Short is public
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
from .youtube_upload import (ET, ROOT, add_to_playlist, clean_tags, comment, req, slot, srt_from_timings, token,
                             token_for, upload, upload_caption, yt_safe)

import os

# YT_SPANISH_REFRESH_TOKEN wins when set (Nov 22: the settings page wouldn't take a second YT_ES_REFRESH_TOKEN line
# while the first one still held the English key from a wrong pick on Google's screen).
ENV = "YT_SPANISH_REFRESH_TOKEN" if os.environ.get("YT_SPANISH_REFRESH_TOKEN") else "YT_ES_REFRESH_TOKEN"
REGISTRY = ROOT / "content" / "learn" / "uploads-es.json"
PLAYLIST = "GTA 6 en Español"
TAGS_ES = ["GTA 6", "GTA 6 español", "GTA 6 en español", "noticias GTA 6", "GTA VI", "Grand Theft Auto VI", "Vice City"]
NOT_AFFILIATED = "Canal de fans: no afiliado a Rockstar Games ni a Take-Two Interactive."
EN_LINK = "🇺🇸 Vice Replay en inglés: https://www.youtube.com/@ViceReplayTV-q8s"
SITE_ES = "🌴 Guías de GTA 6 en español: https://vicereplay.com/es/"


DESCRIPTION = (
    "Vice Replay en Español: noticias de GTA 6 cada mañana, en español. Streamers, récords, quizzes, el mapa de Leonida "
    "contra la vida real y los detalles que casi nadie ve. Sin spoilers de la historia.\n\n"
    "Shorts nuevos todos los días. Suscríbete para no perderte nada de Vice City.\n\n"
    "🌴 Guías en español: vicereplay.com/es/\n🎮 Equipo para GTA 6 (Amazon): vicereplay.com/es/equipo/\n"
    "📩 Contacto: vicereplay.com/contact/\n\n"
    "Canal de fans: no afiliado a Rockstar Games ni a Take-Two Interactive. Las imágenes oficiales pertenecen a sus "
    "dueños y las usamos con comentario propio.")
KEYWORDS = ['GTA 6', 'GTA VI', 'GTA 6 español', 'noticias GTA 6', 'GTA 6 en español', 'Grand Theft Auto VI', 'Vice City',
            'Leonida', 'Lucia', 'Jason', 'Rockstar Games', 'GTA 6 Shorts']
BANNER = ROOT / "assets" / "brand" / "youtube-banner-es-2560x1440.jpg"


def brand(tok, cid):
    """Description, keywords, language and banner for the Spanish channel (the profile picture is set by hand in
    Studio: the API can't change it)."""
    ch, _ = req("GET", "https://youtube.googleapis.com/youtube/v3/channels?part=brandingSettings&mine=true", tok)
    bs = ch["items"][0]["brandingSettings"]
    bs.setdefault("channel", {}).update(
        description=DESCRIPTION, defaultLanguage="es",
        keywords=" ".join(f'"{k}"' if " " in k else k for k in KEYWORDS))
    up, _ = req("POST", "https://www.googleapis.com/upload/youtube/v3/channelBanners/insert?uploadType=media", tok,
                BANNER.read_bytes(), ctype="image/jpeg")
    bs["image"] = {"bannerExternalUrl": up["url"]}
    r, _ = req("PUT", "https://youtube.googleapis.com/youtube/v3/channels?part=brandingSettings", tok,
               {"id": cid, "brandingSettings": {"channel": bs["channel"], "image": bs["image"]}})
    c = r["brandingSettings"]["channel"]
    print(f"Spanish channel branded: description {len(c.get('description', ''))} chars, keywords set, banner set.")


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
    ap.add_argument("episode", help="episodes/<slug>.json, 'whoami', 'brand' or 'comment'")
    ap.add_argument("rest", nargs="*", help="for comment: VIDEO_ID TEXT")
    ap.add_argument("--approve", default="", help="short, news, ... or all (owner approval in chat only)")
    ap.add_argument("--date", help="posting date YYYY-MM-DD (default today, ET)")
    ap.add_argument("--at", help='posting time for every item, e.g. "9:30 AM" (ET)')
    a = ap.parse_args()
    if a.episode == "whoami":  # what the preferred setting holds, exactly
        cid, title = whoami(token(ENV))
        print(f"{ENV} belongs to: {title} ({cid})")
        return
    es_id = config().get("vice-replay-es", {}).get("channel_id")
    tok = token_for(es_id, ENV) if es_id else token(ENV)
    if a.episode == "whoami":
        cid, title = whoami(tok)
        print(f"{ENV} belongs to: {title} ({cid})")
        return
    cid = check_channel(tok)
    if a.episode == "brand":
        brand(tok, cid)
        return
    if a.episode == "comment":  # python -m studio.youtube_es comment VIDEO_ID "texto" (as the Spanish channel)
        vid, text = a.rest[0], a.rest[1]
        v, _ = req("GET", f"https://youtube.googleapis.com/youtube/v3/videos?part=status,snippet&id={vid}", tok)
        it = (v.get("items") or [{}])[0]
        if it.get("snippet", {}).get("channelId") != cid:
            sys.exit(f"{vid} is not a video of the Spanish channel: no comment posted.")
        if it.get("status", {}).get("privacyStatus") != "public":
            sys.exit(f"{vid} isn't public yet: post the comment after it goes live.")
        comment(tok, vid, text)
        print(f"commented on {vid} (Spanish channel)")
        return
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
        desc = yt_safe((es.get("description") or "").strip() + f"\n\n{SITE_ES}\n{EN_LINK}\n\n{NOT_AFFILIATED}")
        # the topic's own Spanish tags first (es.tags / tags_es), then the channel basics (Nov 22: every Spanish
        # upload had the same 6 generic tags)
        tags = clean_tags(es.get("tags") or ep.get("tags_es"), base=TAGS_ES)
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
