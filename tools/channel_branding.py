"""Vice Replay channel page: description, keywords and the trailer non-subscribers see (owner, Nov 24, 2026: "continue to
modify channel and system to help get better views").

Why (Nov 24 data): YouTube search brought 22% of our views and the map / "where to find" Shorts are the format that
works, but the description led with streamer news and the channel trailer was a long video with 0 views.

    python tools/channel_branding.py            # show what would change (1 quota unit)
    python tools/channel_branding.py --apply    # update it (~50 units)
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from studio.flops import API, get, token  # noqa: E402
from studio.youtube_upload import channel_ids, req  # noqa: E402

DESCRIPTION = """Where to find everything in GTA 6: easter eggs, secrets, bonus cars and shops, pinned on Rockstar's official map, plus the day's GTA 6 news. No story spoilers. 🗺️🌴

🗺️ Interactive GTA 6 map (zoom to street names, 30+ spots): https://vicereplay.com/guides/gta-6-map-leonida-places/
🔥 GTA 6 guides, deals & gear: https://vicereplay.com/links

New Shorts every day: where-to-find map guides, tier lists, streamer stories and the numbers behind GTA 6, every fact checked against two or more sources.

Noticias y guías de GTA 6 en español: @vicereplayes

Run it back. ⏪

Independent fan channel. Not affiliated with Rockstar Games or Take-Two Interactive. Map: Rockstar Games' official Leonida map. Sources are listed in every description."""

KEYWORDS = ('"GTA 6" "GTA VI" "GTA 6 map" "GTA 6 easter eggs" "GTA 6 secrets" "GTA 6 locations" "where to find GTA 6" '
            '"GTA 6 interactive map" "GTA 6 tips" "GTA 6 news" "Vice City" Leonida "Grand Theft Auto VI" "GTA 6 Shorts" '
            '"GTA 6 tier list" "GTA 6 Ultimate Edition" "Vice Replay"')
TRAILER = "jQbv5GPR3dk"  # "GTA 6 tier list: Vice City is only B tier" (613 views, our best recent Short); was EJOdYW3sx44 (0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    tok = token()
    cid = channel_ids()["en"]
    ch = get(tok, "channels", part="brandingSettings", id=cid)["items"][0]
    b = ch["brandingSettings"]
    cur = b.get("channel", {})
    print("trailer:", cur.get("unsubscribedTrailer"), "->", TRAILER)
    print("keywords changed:", cur.get("keywords") != KEYWORDS)
    print("description changed:", cur.get("description") != DESCRIPTION)
    if not a.apply:
        return
    b["channel"] = dict(cur, description=DESCRIPTION, keywords=KEYWORDS, unsubscribedTrailer=TRAILER)
    req("PUT", API + "channels?part=brandingSettings", tok, {"id": cid, "brandingSettings": b})
    after = get(tok, "channels", part="brandingSettings", id=cid)["items"][0]["brandingSettings"]["channel"]
    print("applied:", after.get("unsubscribedTrailer") == TRAILER, after.get("keywords") == KEYWORDS)
    log = Path(__file__).resolve().parent.parent / "content" / "learn" / "channel-branding.json"
    log.write_text(json.dumps({"applied": True, "trailer": TRAILER, "previous": {k: cur.get(k) for k in
                                ("description", "keywords", "unsubscribedTrailer")}}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
