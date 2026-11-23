"""Views check before publishing (Nov 21, 2026): rules from our own post-launch Shorts, so a Short that looks like the
ones that died never goes out unnoticed.

Data (public Shorts posted after launch, Nov 19-21, views by Nov 21 evening):
- opening on a moving clip: median 91.5 views (8 Shorts); opening on a still picture: median 17.5 (4 Shorts);
- winners were streamer stories and number "verdicts" (IShowSpeed family name 1,188; PS5 vs PS5 Pro 1,200; Chapter 1
  money catch 559); plain tips died (settings 5, money cheat list 8, won't connect 27, lifeguard dog 32);
- the dead ones ran 79-117 words; the winners 63-96 with a number or a name up front.
Small samples, so most rules are warnings; only a still first frame with no motion at all blocks.
"""
import datetime as dt
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
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
    if seg.get("chart") or seg.get("shots") or (media and not media.endswith(STILL)):  # charts are animated
        return True
    return bool(seg.get("magnify") or seg.get("zoom"))


MONTHS = {m: k + 1 for k, m in enumerate(("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov",
                                          "dec"))}
MESES = {"ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6, "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11,
         "dic": 12}


def note_dates(text, today):
    """Dates a chart note states ("Nov 22", "22 de nov."), as dates in today's year (or last year if in the future)."""
    out = []
    for mon, day in re.findall(r"\b([A-Z][a-z]{2})[a-z]*\.? (\d{1,2})\b", text or ""):
        if mon.lower() in MONTHS:
            out.append((MONTHS[mon.lower()], int(day)))
    for day, mes in re.findall(r"\b(\d{1,2}) de ([a-z]{3})", (text or "").lower()):
        if mes in MESES:
            out.append((MESES[mes], int(day)))
    dates = []
    for m, d in out:
        try:
            x = dt.date(today.year, m, d)
        except ValueError:
            continue
        dates.append(x if x <= today else x.replace(year=today.year - 1))
    return dates


def stale_charts(ep, today=None, days=3):
    """Warnings for chart notes dated `days`+ days ago (Nov 22: "view counts, Nov 22" on a Short posting Nov 25)."""
    today = today or dt.date.today()
    warns = []
    for key, _title, segs in _shorts(ep):
        for k, x in enumerate(segs):
            for c in (x.get("chart"), x.get("chart_es")):
                for d in note_dates((c or {}).get("note"), today):
                    if (today - d).days >= days:
                        warns.append(f"facts: Short '{key}' segment {k + 1} chart says {d:%b %d} ({(today - d).days} days "
                                     f"ago): re-read the numbers and update the note before posting")
                        break
    return sorted(set(warns), key=warns.index)


def layout(segs):
    """The picture order of a Short: chart types, 'clip' for anything else (e.g. counter > bars > counter > clip)."""
    return tuple(x["chart"].get("type", "bars") if x.get("chart") else "clip" for x in segs)


def _recent_layouts(slug, n=4):
    """Layouts of the last n uploaded Shorts (content/learn/uploads.json, newest last), skipping this episode and
    retired/hidden uploads."""
    try:
        ups = json.loads((ROOT / "content" / "learn" / "uploads.json").read_text())
    except (OSError, ValueError):
        return []
    out = []
    for u in reversed(list(ups.values())):
        if u.get("slug") == slug or u.get("item") == "main" or u.get("retired") or u.get("hidden"):
            continue
        try:
            other = json.loads((ROOT / "episodes" / f"{u['slug']}.json").read_text())
        except (OSError, ValueError, KeyError):
            continue
        segs = other.get("short") if u.get("item") == "short" else next(
            (x.get("segments") for x in other.get("shorts", []) if x.get("id") == u.get("item")), None)
        if segs:
            out.append((u["slug"], layout(segs)))
        if len(out) >= n:
            break
    return out


def check(ep, gameplay_available=False, recent=None):
    """(blockers, warnings) for every Short in an episode. With owner gameplay highlights available, Shorts swap them in
    for segments without `keep_media` (unless the episode sets `"use_gameplay": false`). `recent`: [(slug, layout)] of
    the last uploaded Shorts (read from uploads.json when None)."""
    blockers, warnings = [], []
    recent = _recent_layouts(ep.get("slug")) if recent is None else recent
    for key, title, segs in _shorts(ep):
        b, w = check_short(ep, key, title, segs, gameplay_available)
        blockers += b
        warnings += w
        # Nov 22: the first four graph Shorts were all counter > bars > counter > clip. YouTube's repetitive-content
        # checks look at the whole channel, and one template can't tell us which layout works: vary it.
        mine = layout(segs)
        same = [slug for slug, lay in recent if lay == mine and any(t != "clip" for t in mine)]
        if same:
            warnings.append(f"layout: Short '{key}' has the same picture order as {', '.join(same)} "
                            f"({' > '.join(mine)}). Vary it: a `line` chart for trends, bars first, a clip in the middle")
    # long videos follow the same no-trailer-images rule (owner Nov 23: "stop posting the video with trailer imaging")
    for k, what in footage_segments(ep, ep.get("segments"), gameplay_available):
        blockers.append(f"footage: main video segment {k + 1} uses {what}. No trailer images in our videos (owner, "
                        f"Nov 23): use chart / text / list / quote / quiz cards or owner gameplay")
    # "#8" in a title becomes a clickable YouTube hashtag (Nov 22: the Lucia title had "#8 you can't get now")
    titles = [ep.get("short_title"), *(ep.get("short_title_options") or []), (ep.get("short_es") or {}).get("title")]
    for sh in ep.get("shorts") or []:
        titles += [sh.get("title"), *(sh.get("title_options") or []), (sh.get("es") or {}).get("title")]
    for t in filter(None, titles):
        if re.search(r"#\d", t):
            blockers.append(f"title: {t!r} has '#' + a number, which YouTube turns into a hashtag; write 'No. 8' or reword")
    return blockers, warnings + check_tags(ep) + stale_charts(ep)


def _uses_gameplay(segs):
    return any("media/gameplay" in str(x.get("media") or "") or any("media/gameplay" in str(y.get("media") or "")
               for y in x.get("shots") or []) for x in segs)


def footage_segments(ep, segs, gameplay_available=False):
    """[(index, what)] for segments that would show trailer clips or official screenshots: no `chart` card and no owner
    gameplay. A segment with no media named still counts (the renderer picks stock footage for it). Owner, Nov 23:
    "stop posting the video with trailer imaging, we're moving to the ones with lettering and more modern style"; an
    episode `originality` note waives it only with the owner's new, explicit approval (none since Nov 23)."""
    if ep.get("originality"):
        return []
    swap = gameplay_available and ep.get("use_gameplay", True) is not False
    out = []
    for k, x in enumerate(segs or []):
        if x.get("chart"):
            continue
        files = [f for f in [x.get("media")] + [y.get("media") for y in x.get("shots") or []] if f]
        if any("media/gameplay" in str(f) for f in files) or (swap and not x.get("keep_media")):
            continue
        out.append((k, str(files[0]).rsplit("/", 1)[-1] if files else "stock footage the renderer picks itself"))
    return out


def check_short(ep, key, title, segs, gameplay_available=False):
    """(blockers, warnings) for one Short: `key` names it in the messages; `ep` gives `use_gameplay` and `format`."""
    blockers, warnings = [], []
    # Original first (owner Nov 22: "graph, real evidence based... change the system to match"). YouTube's Oct 2026
    # update ranks original Shorts higher; narration over reused trailer footage doesn't count. A Short needs at least
    # one `chart` segment (our graphic of checked numbers) or owner gameplay, unless the episode carries an
    # owner-approved "originality" note (e.g. the curated Lucia outfit montage).
    gameplay = _uses_gameplay(segs) or (gameplay_available and ep.get("use_gameplay", True) is not False)
    if segs and not any(x.get("chart") for x in segs) and not gameplay and not ep.get("originality"):
        blockers.append(f"originality: Short '{key}' is narration over trailer footage only. Add a `chart` segment "
                        f"(leaderboard / counter / VS of numbers we checked, studio/charts.py) or owner gameplay; "
                        f"trailer clips only as cutaways")
    # Facts only (owner, Nov 22 evening: "we're doing the other type of Shorts now, not the ones with footage, facts
    # with a strong hook"): no trailer clips or official screenshots in a Short, not even as cutaways. Our own charts
    # and cards (bars, counter, line, quote, list, text) or the owner's gameplay only; an owner-approved
    # `originality` note (Lucia montage, top-3 rides, approved before this rule) still waives it.
    for k, what in footage_segments(ep, segs, gameplay_available):
        blockers.append(f"footage: Short '{key}' segment {k + 1} uses {what}. No trailer images in our videos "
                        f"(owner, Nov 22 + Nov 23: lettering and modern cards only): make it a chart or a `text` / "
                        f"`list` / `quote` / `quiz` card, or use owner gameplay")
    # Nov 23 research: YouTube (Halprin, July 2026) won't pay for "generic, repetitive content easily made with ...
    # templates, with little variation"; a visible source and a verdict make a card Short read as research
    if segs and any(x.get("chart") for x in segs) and not any((x.get("chart") or {}).get("src") or
                                                             (x.get("chart") or {}).get("note") for x in segs):
        warnings.append(f"originality: Short '{key}' shows no source on screen; add \"src\": \"VGC · Metacritic\" to "
                        f"the card with the main fact (and say your verdict in the script)")
    # Nov 23: "seventy nine ninety nine" is read like a year by the caption step and shows "7,999"; say prices as
    # "seventy nine dollars and ninety nine cents"
    try:
        from ..make_video import display_tokens
        for k, x in enumerate(segs):
            words = (x.get("text") or "").split()
            for tok, a, b, isnum in display_tokens(words):
                digits = re.sub(r"[^0-9]", "", tok)
                scaled = any(re.sub(r"[^a-z]", "", w.lower()) in ("hundred", "thousand") for w in words[a:b + 1])
                spoken = all(re.sub(r"[^\w]", "", w).isalpha() for w in words[a:b + 1])
                if isnum and spoken and len(digits) == 4 and not 1900 <= int(digits) <= 2099 and not scaled:
                    warnings.append(f"captions: Short '{key}' segment {k + 1} shows '{tok}' on screen (spoken like a "
                                    f"year); for a price say 'seventy nine dollars and ninety nine cents'")
    except ImportError:
        pass
    # Nov 23: on the GTA 6-style lettering cards a headline that wraps to 2 lines runs into the big lettering
    from .. import vicecards
    for k, x in enumerate(segs):
        if (x.get("chart") or {}).get("type") in vicecards.DRAW:
            for lab, hl in (("", x.get("headline")), (" (Spanish)", x.get("headline_es"))):
                if hl and len(hl) > 19:
                    warnings.append(f"headline: Short '{key}' segment {k + 1}{lab} headline '{hl}' wraps to 2 lines and "
                                    f"runs into the lettering card; keep it to 19 characters")
    if segs:
        # Hook (Nov 22, owner: "research hooks to get the viewers' attention"): our 20 Shorts with retention data:
        # a question as the first sentence kept 35% (median 130 views) vs 60% for a statement (858). Best openers state
        # the surprising result at once ("Eighteen hours early." 82%; "GTA 6 cheats are real, but there's a catch" 75%).
        opener = re.split(r"(?<=[.?!])\s", (segs[0].get("text") or "").strip())[0]
        if opener.endswith("?"):
            blockers.append(f"hook: Short '{key}' opens with a question ({opener!r}). Questions first kept 35% of viewers "
                            f"vs 60% for a statement: open with the surprising result itself, then the catch")
        if not re.search(r"\d", segs[0].get("headline") or "") and not segs[0].get("chart"):
            warnings.append(f"hook: Short '{key}' opens without a number on screen; our Shorts with a number in the first "
                            f"headline kept 65% of viewers vs 49% (put the number in the headline or open on a `chart`)")
        core = re.sub(r"#\S+", "", title or "").strip()
        if len(core) > 45:
            warnings.append(f"title: '{core}' is {len(core)} characters; the top GTA 6 Shorts with titles of 40 or less "
                            f"averaged 95K views/h vs 70K for longer ones")
        if len(opener.split()) > 14:
            warnings.append(f"hook: Short '{key}' first sentence is {len(opener.split())} words; the best openers say "
                            f"the result in 3-10 words")
        first = segs[0]
        swapped = gameplay_available and ep.get("use_gameplay", True) is not False and not first.get("keep_media")
        if not swapped and not _moves(first):
            blockers.append(f"views: Short '{key}' opens on a still picture with no zoom/magnifier. Since launch, Shorts "
                            f"that open on a moving clip got ~5x the views (median 92 vs 18): use a media/trailer clip "
                            f"or `shots` for segment 1, or add a `zoom`")
        words = sum(len((s.get("text") or "").split()) for s in segs)
        secs = round(words / 2.7)
        if words > 75:  # Nov 22: our Shorts with 76+ words: median 404 views, 3/10 under 50; 56-75 words: median 836, 1/14
            blockers.append(f"views: Short '{key}' is {words} words (~{secs} s). Cut it to one fact in 13-20 s (about 35-55 "
                            f"words): our real-moment clips held 86-92% at 13-17 s, our ~30 s explainers ~57%")
        elif words > 55:
            warnings.append(f"views: Short '{key}' is {words} words (~{secs} s); target 13-20 s (35-55 words), payoff as the "
                            f"last line, last line loops into the first")
        for k, x in enumerate(segs):  # Nov 22: Spanish Shorts showed the English chart labels and notes
            c = x.get("chart") or {}
            words = [y for y in (c.get("label"), c.get("note"), (c.get("vs") or {}).get("label"), c.get("text"),
                                 c.get("who"), c.get("q"), c.get("title"), c.get("sub")) if y]
            if x.get("text_es") and words and not x.get("chart_es") and c.get("locale") != "es":
                warnings.append(f"spanish: Short '{key}' segment {k + 1} chart shows English text in the Spanish "
                                f"version ({words[0]!r}...): add `chart_es` with Spanish label/note")
        text = f"{title} {first.get('headline', '')} {ep.get('format', '')}"
        if TIPS.search(text) and not re.search(r"\d", first.get("headline", "")):
            warnings.append(f"views: Short '{key}' reads like a plain tip ({TIPS.search(text).group(0)!r}). Tips Shorts got "
                            f"5-27 views since launch; lead with a number, a streamer or a catch, or move the tip to the "
                            f"website guide")
    return blockers, warnings


def check_tags(ep):
    """Title/tag warnings for the whole episode: once per episode, not once per Short."""
    warnings = []
    # Nov 22 (owner: "check titles and tags are perfect"): Short-only episodes had uploaded with no tags at all
    if _shorts(ep) and not ep.get("tags") and not all(sh.get("tags") for sh in ep.get("shorts", [])):
        warnings.append("titles/tags: no `tags` in the episode: add 8-15 search phrases people type (\"GTA 6 Lucia\", "
                        "\"GTA 6 outfits\"...), topic first; uploads otherwise get only the 4 channel basics")
    es_meta = [ep.get("short_es") or {}] + [sh.get("es") or {} for sh in ep.get("shorts", [])]
    if any(m.get("title") for m in es_meta) and not ep.get("tags_es") and not all(
            m.get("tags") for m in es_meta if m.get("title")):
        warnings.append("titles/tags: Spanish versions have no tags (`short_es.tags` / each Short's `es.tags`): add the "
                        "Spanish search phrases (\"GTA 6 español\", \"outfits de Lucia\"...)")
    return warnings
