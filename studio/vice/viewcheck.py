"""Views check before publishing (Nov 21, 2026): rules from our own post-launch Shorts, so a Short that looks like the
ones that died never goes out unnoticed.

Data (public Shorts posted after launch, Nov 19-21, views by Nov 21 evening):
- opening on a moving clip: median 91.5 views (8 Shorts); opening on a still picture: median 17.5 (4 Shorts);
- winners were streamer stories and number "verdicts" (IShowSpeed family name 1,188; PS5 vs PS5 Pro 1,200; Chapter 1
  money catch 559); plain tips died (settings 5, money cheat list 8, won't connect 27, lifeguard dog 32);
- the dead ones ran 79-117 words; the winners 63-96 with a number or a name up front.
Small samples, so most rules are warnings; only a still first frame with no motion at all blocks.
"""
import re

STILL = (".jpg", ".jpeg", ".png", ".webp")
TIPS = re.compile(r"\b(settings?|tips?|how to|won'?t connect|cheat codes?|codes|do this first|beginner)\b", re.I)


def _shorts(ep):
    out = []
    if ep.get("short"):
        out.append(("short", ep.get("short_title") or ep.get("title", ""), ep["short"]))
    for sh in ep.get("shorts", []):
        out.append((sh.get("id", "?"), sh.get("title", ""), sh.get("segments", [])))
    return out


def _moves(seg):
    """Does the first picture move? A clip, cuts between clips, or an animated zoom/magnifier on a still."""
    media = (seg.get("media") or "").lower()
    if seg.get("shots") or (media and not media.endswith(STILL)):
        return True
    return bool(seg.get("magnify") or seg.get("zoom"))


def check(ep, gameplay_available=False):
    """(blockers, warnings) for every Short in an episode. With owner gameplay highlights available, Shorts swap them in
    for segments without `keep_media` (unless the episode sets `"use_gameplay": false`)."""
    blockers, warnings = [], []
    for key, title, segs in _shorts(ep):
        if not segs:
            continue
        first = segs[0]
        swapped = gameplay_available and ep.get("use_gameplay", True) is not False and not first.get("keep_media")
        if not swapped and not _moves(first):
            blockers.append(f"views: Short '{key}' opens on a still picture with no zoom/magnifier. Since launch, Shorts "
                            f"that open on a moving clip got ~5x the views (median 92 vs 18): use a media/trailer clip "
                            f"or `shots` for segment 1, or add a `zoom`")
        words = sum(len((s.get("text") or "").split()) for s in segs)
        secs = round(words / 2.7)
        if words > 80:  # Nov 22 research: 11-20 s Shorts have the best median views (Quso, 108k Shorts); ours lose half by 30 s
            blockers.append(f"views: Short '{key}' is {words} words (~{secs} s). Cut it to one fact in 13-20 s (about 35-55 "
                            f"words): our real-moment clips held 86-92% at 13-17 s, our ~30 s explainers ~57%")
        elif words > 55:
            warnings.append(f"views: Short '{key}' is {words} words (~{secs} s); target 13-20 s (35-55 words), payoff as the "
                            f"last line, last line loops into the first")
        text = f"{title} {first.get('headline', '')} {ep.get('format', '')}"
        if TIPS.search(text) and not re.search(r"\d", first.get("headline", "")):
            warnings.append(f"views: Short '{key}' reads like a plain tip ({TIPS.search(text).group(0)!r}). Tips Shorts got "
                            f"5-27 views since launch; lead with a number, a streamer or a catch, or move the tip to the "
                            f"website guide")
    # Nov 22 (owner: "check titles and tags are perfect"): Short-only episodes had uploaded with no tags at all
    if _shorts(ep) and not ep.get("tags") and not all(sh.get("tags") for sh in ep.get("shorts", [])):
        warnings.append("titles/tags: no `tags` in the episode: add 8-15 search phrases people type (\"GTA 6 Lucia\", "
                        "\"GTA 6 outfits\"...), topic first; uploads otherwise get only the 4 channel basics")
    es_meta = [ep.get("short_es") or {}] + [sh.get("es") or {} for sh in ep.get("shorts", [])]
    if any(m.get("title") for m in es_meta) and not ep.get("tags_es") and not all(
            m.get("tags") for m in es_meta if m.get("title")):
        warnings.append("titles/tags: Spanish versions have no tags (`short_es.tags` / each Short's `es.tags`): add the "
                        "Spanish search phrases (\"GTA 6 español\", \"outfits de Lucia\"...)")
    return blockers, warnings
