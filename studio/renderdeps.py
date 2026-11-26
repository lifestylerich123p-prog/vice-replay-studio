"""What each rendered Short actually depends on, per language (owner Nov 26, Phase 3 #10: "English-language changes
should invalidate Spanish renders only when shared factual claims, visual assets, or other relevant dependencies have
changed").

Before: a render counted as stale whenever its episode file was newer, so fixing an English title made the Spanish
video "stale" and the Spanish gate waited for an English re-render. Now make_video writes `<video>.inputs.json` with
two fingerprints:
* video: the segments as that language renders them (EN: text/headline/chart/media/audio; ES: text_es/headline_es/
  chart_es where present + the shared visuals/media/audio_es), the render-relevant episode settings (spot, cta or
  cta_es, music, voice for that language, sources shown on cards...), and the voice files' SHA-256.
* package: the title/description that go into the .txt next to the video (a change there needs only
  `python -m studio.make_video <ep> --short [--es] --meta-only`, not a new render).
No manifest (renders made before Nov 26) -> the old rule (file times) applies.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# top-level episode keys the renderer reads (studio/make_video.py, cardphotos.py); the rest is package/metadata
SHARED_KEYS = ("use_gameplay", "spot", "sfx", "rate", "payoff_hook", "outro_card", "music_level", "music_duck", "music",
               "mood", "format", "follow_cta", "card_photos", "sources", "map_style")
LANG_KEYS = {"en": ("cta", "voice", "voice_override"), "es": ("cta_es", "voice_es")}


def _sha(p):
    p = Path(p) if Path(p).is_absolute() else ROOT / p
    if not p.exists():
        return None
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _cfg_voice(lang):
    try:
        c = json.loads((ROOT / "config" / "channel.json").read_text())
    except (OSError, ValueError):
        return None
    return c.get("voice_es" if lang == "es" else "voice")


def segments(ep, item="short"):
    if item == "short":
        return ep.get("short") or []
    sh = next((s for s in ep.get("shorts", []) if s.get("id") == item), None)
    return (sh or {}).get("segments") or []


def seg_view(seg, lang):
    """A segment as one language's render sees it."""
    if lang == "es":
        v = {k: seg.get(f"{k}_es", val) for k, val in seg.items() if not k.endswith("_es") and k != "audio"}
        v.update({k: val for k, val in seg.items() if k.endswith("_es")})
        return v
    return {k: val for k, val in seg.items() if not k.endswith("_es")}


def lexicon_hash(lang):
    p = ROOT / "config" / f"pronounce-{lang}.json"
    return _sha(p) if p.exists() else None


def video_inputs(ep, item="short", lang="en"):
    segs = [seg_view(s, lang) for s in segments(ep, item)]
    audio = sorted({s[k] for s in segs for k in ("audio", "audio_es") if s.get(k)})
    keys = SHARED_KEYS + LANG_KEYS[lang]
    return {"lang": lang, "item": item, "segments": segs,
            "episode": {k: ep[k] for k in keys if k in ep and not (k == "spot" and item != "short")},
            "voice_config": _cfg_voice(lang), "lexicon": lexicon_hash(lang),
            "audio_files": {a: _sha(a) for a in audio}}


def package(ep, item="short", lang="en"):
    if item == "short":
        if lang == "es":
            es = ep.get("short_es") or {}
            return {"title": es.get("title") or ep.get("short_title"), "description": es.get("description") or
                    ep.get("short_description", "")}
        return {"title": ep.get("short_title"), "description": ep.get("short_description", "")}
    sh = next((s for s in ep.get("shorts", []) if s.get("id") == item), {}) or {}
    es = sh.get("es") or {}
    if lang == "es":
        return {"title": es.get("title") or sh.get("title"), "description": es.get("description") or sh.get("description", "")}
    return {"title": sh.get("title"), "description": sh.get("description", "")}


def h(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def manifest_path(video):
    return Path(video).with_suffix(".inputs.json")


def write(video, ep, item="short", lang="en", used_footage=None):
    m = {"video": h(video_inputs(ep, item, lang)), "package": h(package(ep, item, lang)), "lang": lang,
         "item": item, "video_sha256": _sha(video)}
    if used_footage is not None:
        m["used_footage"] = bool(used_footage)
    manifest_path(video).write_text(json.dumps(m, indent=1) + "\n")
    return m


def write_package(video, ep, item="short", lang="en"):
    """--meta-only: the .txt was rewritten; the video fingerprint stays what it was (never marks a stale video current)."""
    mp = manifest_path(video)
    m = json.loads(mp.read_text()) if mp.exists() else {"lang": lang, "item": item}
    m["package"] = h(package(ep, item, lang))
    mp.write_text(json.dumps(m, indent=1) + "\n")
    return m


def status(video, ep, item="short", lang="en", ep_path=None):
    """missing | stale-video | stale-package | current | (no manifest) stale-mtime / current-mtime."""
    video = Path(video)
    if not video.exists():
        return "missing"
    mp = manifest_path(video)
    if not mp.exists():
        if ep_path and video.stat().st_mtime < Path(ep_path).stat().st_mtime:
            return "stale-mtime"
        return "current-mtime"
    try:
        m = json.loads(mp.read_text())
    except ValueError:
        return "stale-video"
    if m.get("video") != h(video_inputs(ep, item, lang)):
        return "stale-video"
    if m.get("video_sha256") and m["video_sha256"] != _sha(video):
        return "stale-video"  # the file on disk isn't the one this manifest describes
    if m.get("package") != h(package(ep, item, lang)):
        return "stale-package"
    return "current"


def needs_render(status_):
    return status_ in ("missing", "stale-video", "stale-mtime")


def adopt(slugs=None):
    """One-off for renders made before manifests existed: a render newer than its episode (the old rule's 'current')
    gets a manifest describing the episode as it is now. Older renders are left stale."""
    done = []
    for ep_path in sorted((ROOT / "episodes").glob("*.json")):
        try:
            ep = json.loads(ep_path.read_text())
        except ValueError:
            continue
        slug = ep.get("slug") or ep_path.stem
        if slugs and slug not in slugs or not ep.get("short"):
            continue
        for lang, sfx in (("en", ""), ("es", "-es")):
            video = ROOT / "output" / slug / f"{slug}-short{sfx}.mp4"
            if status(video, ep, "short", lang, ep_path) == "current-mtime":
                write(video, ep, "short", lang)
                done.append(video.name)
    return done


if __name__ == "__main__":
    import sys
    if sys.argv[1:2] == ["adopt"]:
        print("\n".join(adopt(sys.argv[2:] or None)) or "nothing to adopt")
