"""Channel home pages (Nov 22, 2026; owner: "continue to check and find ways to upgrade the channel, all the best").

    python -m studio.channel_layout            # show both channels' sections and trailer (1-2 quota units)
    python -m studio.channel_layout apply      # make the changes below (~50 units each, only what's missing)

What it sets, once:
- English channel: a "Vice Replay en Español" section featuring the Spanish channel (cross-promotion), and the
  trailer for non-subscribers -> the newest public weekly recap (TRAILER) instead of a long video with 0 views.
- Spanish channel (its home page had no sections at all): the "GTA 6 en Español" playlist, popular uploads, and a
  "Vice Replay (English)" section featuring the English channel.
Each step checks what is already there first, so running it twice changes nothing.
"""
import sys

from .youtube_es import config
from .youtube_upload import req, token, token_for

TRAILER = "EJOdYW3sx44"  # "GTA 6 This Week: $3.79 Billion, a 99 and 68M Views" (public Sun Nov 22, 2:30 PM ET)
ES_PLAYLIST = "PLf81PGcQlKHM"
API = "https://youtube.googleapis.com/youtube/v3"


def sections(tok):
    r, _ = req("GET", f"{API}/channelSections?part=snippet,contentDetails&mine=true", tok)
    return r.get("items", [])


def has_channel_section(items, channel_id):
    return any(channel_id in (it.get("contentDetails") or {}).get("channels", []) for it in items)


def add_section(tok, body, label):
    req("POST", f"{API}/channelSections?part=snippet,contentDetails", tok, body)
    print(f"added: {label}")


def set_trailer(tok, video_id):
    v, _ = req("GET", f"{API}/videos?part=status&id={video_id}", tok)
    items = v.get("items") or []
    if not items or items[0]["status"].get("privacyStatus") != "public":
        print(f"trailer: {video_id} isn't public yet; left as it is")
        return
    c, _ = req("GET", f"{API}/channels?part=brandingSettings&mine=true", tok)
    ch = c["items"][0]
    b = ch["brandingSettings"]
    if b.get("channel", {}).get("unsubscribedTrailer") == video_id:
        print("trailer: already set")
        return
    b.setdefault("channel", {})["unsubscribedTrailer"] = video_id
    req("PUT", f"{API}/channels?part=brandingSettings", tok, {"id": ch["id"], "brandingSettings": {"channel": b["channel"]}})
    print(f"trailer: set to {video_id}")


def main():
    cfg = config()
    en_id, es_id = cfg["vice-replay"]["channel_id"], cfg["vice-replay-es"]["channel_id"]
    en, es = token(), token_for(es_id, "YT_SPANISH_REFRESH_TOKEN")
    en_s, es_s = sections(en), sections(es)
    for label, items in (("English", en_s), ("Spanish", es_s)):
        print(f"{label}: " + (", ".join(f"{it['snippet']['type']}:{it['snippet'].get('title') or ''}" for it in items) or "no sections"))
    if len(sys.argv) < 2 or sys.argv[1] != "apply":
        return
    if not has_channel_section(en_s, es_id):
        add_section(en, {"snippet": {"type": "multiplechannels", "title": "Vice Replay en Español"},
                         "contentDetails": {"channels": [es_id]}}, "English channel -> Spanish channel section")
    if not any(ES_PLAYLIST in (it.get("contentDetails") or {}).get("playlists", []) for it in es_s):
        add_section(es, {"snippet": {"type": "singleplaylist", "position": 0},
                         "contentDetails": {"playlists": [ES_PLAYLIST]}}, "Spanish channel -> GTA 6 en Español playlist")
    if not any(it["snippet"]["type"] == "popularuploads" for it in es_s):
        add_section(es, {"snippet": {"type": "popularuploads"}}, "Spanish channel -> popular uploads")
    if not has_channel_section(es_s, en_id):
        add_section(es, {"snippet": {"type": "multiplechannels", "title": "Vice Replay (English)"},
                         "contentDetails": {"channels": [en_id]}}, "Spanish channel -> English channel section")
    set_trailer(en, TRAILER)


if __name__ == "__main__":
    main()
