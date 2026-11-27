"""The numbered map series (owner APPROVE, Nov 26: "number the map Shorts as a series, each ending with the next
one, and pin the map playlist at the top of the channel").

Members: English Shorts whose episode says `"series": "Map Spots"` (the main `short`), or an extra `shorts[]` item
that says it itself. They are numbered in posting order (content/learn/approved_queue.json): spot #1 is the first
one posted. Each one not uploaded yet gets, in its episode file:
  - `"spot": N`: the map card shows a "MAP SPOT #N" badge ("LUGAR #N" in Spanish; studio/charts.py map_frame)
  - `"cta"` / `"cta_es"`: the follow pill on the last card promises the next one ("SPOT #N+1 NEXT: FOLLOW")
  - a "📍 Map Spot #N" line in the English and Spanish descriptions

    python -m studio.mapseries            # the series in order, and what is out of date
    python -m studio.mapseries number     # write the numbers into the episodes not uploaded yet (then re-render)
    python -m studio.mapseries sync       # YouTube: retitle scheduled ones to the episode title, add the spot line,
                                          # keep the map playlist in spot order (~50 units per change)
    python -m studio.mapseries sync --home   # ...and put the map playlist first on the channel's home tab

`studio.doctor` warns when a booked spot's number no longer matches its place in the schedule (a Short was moved):
run `number` and re-render it with `python -m studio.ship`.
"""
import argparse
import datetime as dt
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE = ROOT / "content" / "learn" / "approved_queue.json"
UPLOADS = ROOT / "content" / "learn" / "uploads.json"
EPISODES = ROOT / "episodes"
SERIES = "Map Spots"
PLAYLIST = "GTA 6 Map: Where to Find It"
LINE = re.compile(r"^📍 (Map Spot|Lugar) #\d+.*$", re.M)


UPLOADS_ES = ROOT / "content" / "learn" / "uploads-es.json"
LANGS = {"en": "english", "es": "spanish"}


def registry(lang="en"):
    """The channel's series settings (config/channel.json `series_registry`, owner Phase 10 #4): playlist name/id, or
    None when that channel has no map-series playlist."""
    try:
        cfg = json.loads((ROOT / "config" / "channel.json").read_text()).get("series_registry") or {}
    except (OSError, ValueError):
        cfg = {}
    default = {"playlist": PLAYLIST, "playlist_id": None} if lang == "en" else {"playlist": None, "playlist_id": None}
    return (cfg.get(LANGS[lang]) or {}).get("map_spots") or default


def cta(n, lang="en"):
    """The follow pill on a spot's last card: promises the next spot (under ~26 characters)."""
    return f"LUGAR #{n + 1} PRONTO: SÍGUENOS" if lang == "es" else f"SPOT #{n + 1} NEXT: FOLLOW"


def desc_line(n, lang="en", playlist="default"):
    """The description line. It names a playlist only when that channel really has one (never the other channel's)."""
    pl = registry(lang).get("playlist") if playlist == "default" else playlist
    if lang == "es":
        return (f"📍 Lugar #{n} de nuestra serie del mapa de GTA 6: todos están en la lista \"{pl}\"." if pl
                else f"📍 Lugar #{n} de nuestra serie del mapa de GTA 6.")
    return (f"📍 Map Spot #{n} of our GTA 6 map series: every spot is in the playlist \"{pl}\"." if pl
            else f"📍 Map Spot #{n} of our GTA 6 map series.")


def with_line(text, line):
    """The description with our spot line (replaced if it is already there, else added after the first paragraph)."""
    text = text or ""
    if LINE.search(text):
        return LINE.sub(line, text, count=1)
    head, sep, rest = text.partition("\n\n")
    return f"{head}\n\n{line}" + (f"\n\n{rest}" if sep else "")


def without_line(text):
    """The description without our spot line (and the blank line it brought)."""
    return re.sub(r"\n\n" + LINE.pattern.lstrip("^").rstrip("$") + r"(?=\n|$)", "", text or "", flags=re.M)


def _when(slot):
    d, t = slot
    return dt.datetime.strptime(f"{d} {t}", "%Y-%m-%d %I:%M %p")


def _item_spec(ep, item):
    if item == "short":
        return ep
    return next((s for s in ep.get("shorts", []) if s.get("id") == item), {})


def members(queue_items, uploads, load, lang="en"):
    """One channel's series in its own posting order: [{slug, item, when, vid, n, stored}] (`stored` = the number the
    episode holds for that channel: `spot` in English, `spot_es` in Spanish).

    English: numbered 1, 2, 3... in English posting order. Spanish (owner Phase 10 #4): its own sequence in Spanish
    posting order; a Spanish video already uploaded keeps the number it shows (`spot_es`, or for the three uploaded
    before Nov 27 the number baked in from `spot`), and every new one continues after the highest number so far, so
    published numbering is never reset to 1 and never copies the English order."""
    up = {(u.get("slug"), u.get("item") or "short"): vid for vid, u in uploads.items() if isinstance(u, dict)}
    out = []
    for it in queue_items:
        item = it.get("item", "short")
        slot = it.get(lang)
        if item == "main" or not slot or (lang == "en" and it.get("es_only")):
            continue
        try:
            ep = load(it["slug"])
        except (OSError, KeyError, ValueError):
            continue
        spec = _item_spec(ep, item)
        if (spec.get("series") if item != "short" else ep.get("series")) != SERIES:
            continue
        out.append({"slug": it["slug"], "item": item, "when": _when(slot), "vid": up.get((it["slug"], item)),
                    "stored": spec.get("spot" if lang == "en" else "spot_es"), "legacy": spec.get("spot"),
                    "lang": lang})
    out.sort(key=lambda m: m["when"])
    if lang == "en":
        for i, m in enumerate(out, 1):
            m["n"] = i
        return out
    for m in out:
        if m["vid"]:
            m["n"] = m["stored"] if m["stored"] is not None else m["legacy"]
    last = max([m["n"] or 0 for m in out if m["vid"]] or [0])  # new numbers always continue after the highest shown
    for m in out:
        if not m["vid"]:
            last += 1
            m["n"] = last
    return out


def stale(ms):
    """Booked spots (not uploaded yet) whose number no longer matches their place in the schedule."""
    return [m for m in ms if not m["vid"] and m["stored"] != m["n"]]


def apply_number(ep, n, lang="en"):
    """Writes one channel's spot number, its next-spot pill and its description line into an episode dict (main
    Short). English touches only English fields, Spanish only Spanish fields (owner Phase 10 #4)."""
    if lang == "es":
        ep["spot_es"] = n
        if not ep.get("cta_es") or ep["cta_es"].startswith("LUGAR #"):
            ep["cta_es"] = cta(n, "es")
        if isinstance(ep.get("short_es"), dict) and ep["short_es"].get("description") is not None:
            ep["short_es"]["description"] = with_line(ep["short_es"]["description"], desc_line(n, "es"))
        return ep
    ep["spot"] = n
    if not ep.get("cta") or ep["cta"].startswith("SPOT #"):
        ep["cta"] = cta(n, "en")
    ep["short_description"] = with_line(ep.get("short_description", ""), desc_line(n))
    return ep


def clear_es(ep):
    """An English series member with no Spanish slot: no Spanish number, pill or series line (they used to copy the
    English number)."""
    ep.pop("spot_es", None)
    if (ep.get("cta_es") or "").startswith("LUGAR #"):
        ep.pop("cta_es")
    if isinstance(ep.get("short_es"), dict) and ep["short_es"].get("description"):
        ep["short_es"]["description"] = without_line(ep["short_es"]["description"])
    return ep


def _load(slug):
    return json.loads((EPISODES / f"{slug}.json").read_text())


def _save(slug, ep):
    p = EPISODES / f"{slug}.json"
    raw = p.read_text()
    indent = 2 if raw.startswith('{\n  "') else (1 if raw.startswith('{\n "') else None)
    p.write_text(json.dumps(ep, ensure_ascii=False, indent=indent) + "\n")


def current(lang="en"):
    reg = UPLOADS if lang == "en" else UPLOADS_ES
    try:
        uploads = json.loads(reg.read_text())
    except (OSError, ValueError):
        uploads = {}
    return members(json.loads(QUEUE.read_text())["items"], uploads if isinstance(uploads, dict) else {}, _load, lang)


def number(langs=("en", "es")):
    """Writes both channels' numbers into the episodes not uploaded yet on that channel (then re-render)."""
    changed = []
    es_members = current("es") if "es" in langs else []
    for lang in langs:
        for m in (current(lang) if lang == "en" else es_members):
            if m["vid"] or m["item"] != "short":
                continue
            ep = _load(m["slug"])
            before = json.dumps(ep, ensure_ascii=False)
            apply_number(ep, m["n"], lang)
            if json.dumps(ep, ensure_ascii=False) != before:
                _save(m["slug"], ep)
                changed.append(m)
    if "es" in langs:
        in_es = {m["slug"] for m in es_members}
        for m in current("en"):
            if m["slug"] in in_es or m["item"] != "short":
                continue
            ep = _load(m["slug"])
            before = json.dumps(ep, ensure_ascii=False)
            clear_es(ep)
            if json.dumps(ep, ensure_ascii=False) != before:
                _save(m["slug"], ep)
                changed.append(dict(m, lang="es", n=None))
    return changed


def sync(home=False):
    """YouTube side: scheduled members take the episode's (search-phrase) title, every uploaded member gets the spot
    line, the map playlist follows spot order (any other video in it, e.g. the long guide, goes after), and with
    `home` the playlist is the first section on the channel's home tab."""
    from .youtube_upload import add_to_playlist, req, token
    yt = "https://youtube.googleapis.com/youtube/v3/"
    tok = token()
    ms = [m for m in current("en") if m["vid"]]
    if not ms:
        return []
    r, _ = req("GET", yt + "videos?part=snippet,status&id=" + ",".join(m["vid"] for m in ms), tok)
    cur = {v["id"]: v for v in r.get("items", [])}
    done = []
    now = dt.datetime.now(dt.timezone.utc)
    for m in ms:
        v = cur.get(m["vid"])
        if not v:
            continue
        sn, st = v["snippet"], v.get("status", {})
        spec = _item_spec(_load(m["slug"]), m["item"])
        title = sn["title"]
        scheduled = st.get("privacyStatus") == "private" and st.get("publishAt") and \
            dt.datetime.fromisoformat(st["publishAt"].replace("Z", "+00:00")) > now
        want = spec.get("short_title") if m["item"] == "short" else spec.get("title")
        if scheduled and want and want != title:
            title = want  # live videos keep their title: only booked ones are retitled
        desc = with_line(sn.get("description", ""), desc_line(m["n"]))
        if title != sn["title"] or desc != sn.get("description", ""):
            body = {"id": m["vid"], "snippet": {"title": title, "description": desc[:4900],
                                                  "categoryId": sn.get("categoryId", "20"), "tags": sn.get("tags", []),
                                                  "defaultLanguage": sn.get("defaultLanguage") or "en"}}
            if sn.get("defaultAudioLanguage"):
                body["snippet"]["defaultAudioLanguage"] = sn["defaultAudioLanguage"]
            req("PUT", yt + "videos?part=snippet", tok, body)
            done.append(f"#{m['n']} {m['vid']}: " + ("title + " if title != sn["title"] else "") + "spot line")
        add_to_playlist(tok, m["vid"], PLAYLIST)
    # playlist order = spot order
    from .youtube_upload import _playlist_cache
    pid = _playlist_cache[PLAYLIST]
    r, _ = req("GET", yt + f"playlistItems?part=snippet&playlistId={pid}&maxResults=50", tok)
    items = sorted(r.get("items", []), key=lambda p: p["snippet"]["position"])
    rank = {m["vid"]: m["n"] for m in ms}
    want = sorted(items, key=lambda p: (rank.get(p["snippet"]["resourceId"]["videoId"], 10 ** 6),
                                        p["snippet"]["position"]))
    for pos, p in enumerate(want):
        if p["snippet"]["position"] != pos:
            req("PUT", yt + "playlistItems?part=snippet", tok,
                {"id": p["id"], "snippet": {"playlistId": pid, "position": pos,
                                            "resourceId": p["snippet"]["resourceId"]}})
            done.append(f"playlist: {p['snippet']['resourceId']['videoId']} -> position {pos}")
            r, _ = req("GET", yt + f"playlistItems?part=snippet&playlistId={pid}&maxResults=50", tok)
            items = {q["id"]: q for q in r.get("items", [])}
            want = [items.get(q["id"], q) for q in want]
    if home:
        r, _ = req("GET", yt + "channelSections?part=snippet,contentDetails&mine=true", tok)
        secs = r.get("items", [])
        if not any(pid in (s.get("contentDetails") or {}).get("playlists", []) for s in secs):
            req("POST", yt + "channelSections?part=snippet,contentDetails", tok,
                {"snippet": {"type": "singlePlaylist", "position": 0},
                 "contentDetails": {"playlists": [pid]}})
            done.append(f"channel home: \"{PLAYLIST}\" added as the first section")
    return done


def sync_es(dry=False):
    """Spanish channel: uploaded Spanish series videos get the Spanish line (their own number, no English playlist).
    Only the description changes; the video itself is never re-uploaded (owner Phase 10: no re-uploads for cosmetic
    numbering). Returns what changed (~50 units per video changed)."""
    from .youtube_upload import req, token_for
    ids = {}
    try:
        es_id = json.loads((ROOT / "config" / "channel.json").read_text())["channels"]["es"]["channel_id"]
    except (OSError, ValueError, KeyError):
        es_id = "UCWPnqYqYu9_CLsJ8Bk1MPgQ"
    ms = [m for m in current("es") if m["vid"] and m["n"]]
    if not ms:
        return []
    import os
    env = "YT_SPANISH_REFRESH_TOKEN" if os.environ.get("YT_SPANISH_REFRESH_TOKEN") else "YT_ES_REFRESH_TOKEN"
    tok = token_for(es_id, env)
    yt = "https://youtube.googleapis.com/youtube/v3/"
    r, _ = req("GET", yt + "videos?part=snippet&id=" + ",".join(m["vid"] for m in ms), tok)
    cur = {v["id"]: v for v in r.get("items", [])}
    done = []
    for m in ms:
        v = cur.get(m["vid"])
        if not v or v["snippet"].get("channelId") != es_id:
            continue
        sn = v["snippet"]
        desc = with_line(sn.get("description", ""), desc_line(m["n"], "es"))
        if desc == sn.get("description", ""):
            continue
        if not dry:
            body = {"id": m["vid"], "snippet": {"title": sn["title"], "description": desc[:4900],
                                              "categoryId": sn.get("categoryId", "20"), "tags": sn.get("tags", []),
                                              "defaultLanguage": sn.get("defaultLanguage") or "es"}}
            if sn.get("defaultAudioLanguage"):
                body["snippet"]["defaultAudioLanguage"] = sn["defaultAudioLanguage"]
            req("PUT", yt + "videos?part=snippet", tok, body)
        done.append(f"ES #{m['n']} {m['vid']}: spot line fixed (Spanish number, no English playlist)")
    return done


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", nargs="?", default="show", choices=["show", "number", "sync"])
    ap.add_argument("--home", action="store_true", help="sync: also put the map playlist first on the channel home")
    a = ap.parse_args()
    if a.cmd == "number":
        for m in number():
            what = f"#{m['n']}" if m.get("n") else "no Spanish number"
            print(f"{m['lang'].upper()} {what} {m['slug']} ({m['when']:%a %b %d %I:%M %p}): re-render with studio.ship")
    elif a.cmd == "sync":
        for line in (sync(a.home) or []) + (sync_es() or []) or ["nothing to change"]:
            print(line)
    for lang in ("en", "es"):
        print(f"\n{'English' if lang == 'en' else 'Spanish'} series ({'playlist ' + str(registry(lang).get('playlist')) if registry(lang).get('playlist') else 'no playlist on this channel'}):")
        for m in current(lang):
            flag = "" if m["vid"] or m["stored"] == m["n"] else f"  <- episode says {m['stored']}: run number + re-render"
            print(f"#{m['n']:>2} {m['when']:%a %b %d %I:%M %p}  {m['slug']} ({m['item']})  "
                  f"{'uploaded ' + m['vid'] if m['vid'] else 'booked'}{flag}")


if __name__ == "__main__":
    main()
