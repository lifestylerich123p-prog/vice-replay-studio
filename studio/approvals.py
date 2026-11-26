"""The publishing gate (owner, Nov 26, 2026, "Autonomous publishing authorization update": a finished video publishes
automatically at its slot ONLY when every mandatory check passes; anything uncertain is held, never published).

    RESEARCHED -> VERIFIED -> PRODUCED -> RENDERED -> QA_PASSED -> AUTO_APPROVED -> SCHEDULED -> PUBLISHED
    any critical problem -> BLOCKED (must be fixed) or NEEDS_REVIEW (a person/next run must decide); FAILED = an upload
    error (the platform is asked before any retry, so nothing is ever posted twice).

evaluate() runs the owner's 10 conditions for one video, platform and slot:
  1 facts: 2+ sources in the episode and a fact re-check stamped within 2 days of the slot (`factcheck` command)
  2-5 spoilers/safety/copyright, visual/technical defects, narration vs captions, audio: `studio.vice publish`
      (rights registry, fact flags, QC: black/frozen frames, loudness, captions vs speech, hooks) + 1080x1920, audio
      stream, 8-60 s
  6 title + description final (rendered .txt = episode title, "GTA 6" first, <= 100 chars, description present)
  7 no duplicate (registry on every branch is checked again by the uploader; here: slug/item and title not posted)
  8 real value: a map/location card, a how-to/tutorial, or an episode marked "experiment" (14-day plan: 70% location
    guides, 20% map tutorials, 10% experiments); generic tier/versus/headline Shorts go to NEEDS_REVIEW
  9 the test suite passed on the current code (`tests` command; cached by a hash of the code)
 10 limits: auto-publishing switched on (config/channel.json `auto_publish`), the slot in the future, at most
    `max_per_day` auto-published Shorts that day, only at the plan's slot times (`slots`: EN 8:00 AM / 6:00 PM,
    ES 12:30 PM / 7:00 PM), YouTube only: English (`auto_publish`) and Vice Replay en Español (`auto_publish_es`, its
    own switch, Spanish render + title); TikTok and Instagram keep their own arrangements
The approval is bound to a fingerprint of the content (spec_hash): change the script, cards, pins, sources,
description, pinned comment, series number or a voice file and it must be evaluated again before it can post.
Two upload failures in a row switch auto-publishing off and tell the owner (directive section 7).

    python -m studio.approvals evaluate episodes/<slug>.json --at "2026-11-28 8:00 AM"
    python -m studio.approvals factcheck episodes/<slug>.json --note "re-checked: GTABase + Game8 still agree"
    python -m studio.approvals tests            # run the suite now and record the result
    python -m studio.approvals status           # every video's state
    python -m studio.approvals verify           # SCHEDULED videos whose slot passed: public on YouTube? -> PUBLISHED
    python -m studio.approvals pause "why" | resume
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo
from . import renderdeps

ROOT = Path(__file__).resolve().parent.parent
STORE = ROOT / "content" / "learn" / "approvals.json"
TESTS = ROOT / "content" / "learn" / "tests_status.json"
FACTS = ROOT / "content" / "learn" / "factchecks.json"  # {slug: {"date", "note"}}: kept outside the episode so a
# re-check doesn't make the rendered video look older than its episode
CONFIG = ROOT / "config" / "channel.json"
ET = ZoneInfo("America/New_York")
PLATFORMS = ("youtube-en", "youtube-es", "instagram")
ALLOWED = {
    "RESEARCHED": {"VERIFIED", "BLOCKED", "NEEDS_REVIEW"},
    "VERIFIED": {"PRODUCED", "RENDERED", "BLOCKED", "NEEDS_REVIEW"},
    "PRODUCED": {"RENDERED", "BLOCKED", "NEEDS_REVIEW"},
    "RENDERED": {"QA_PASSED", "BLOCKED", "NEEDS_REVIEW"},
    "QA_PASSED": {"AUTO_APPROVED", "BLOCKED", "NEEDS_REVIEW"},
    "AUTO_APPROVED": {"UPLOADING", "RENDERED", "BLOCKED", "NEEDS_REVIEW"},
    "UPLOADING": {"SCHEDULED", "PUBLISHED", "FAILED"},
    "SCHEDULED": {"PUBLISHED", "BLOCKED"},
    "PUBLISHED": set(),
    "BLOCKED": {"RENDERED"},
    "NEEDS_REVIEW": {"RENDERED"},
    "FAILED": {"AUTO_APPROVED", "SCHEDULED", "PUBLISHED", "RENDERED"},  # via reconcile(): the platform is asked first
}
DONE = {"UPLOADING", "SCHEDULED", "PUBLISHED"}
# fields that don't change the video or its package (internal notes, unused title options, rule texts, stamps)
IGNORED = {"series", "facts_note", "title_rule", "comment_rule", "short_title_options", "title_options",
           "voice_es_note", "style", "moved", "moved_8am", "facts_checked", "facts_checked_note"}


class Blocked(Exception):
    """This video must not be uploaded now; the message says why."""


# ---------- storage, config, state machine ----------

def _load(path=None):
    path = path or STORE  # looked up at call time (tests point STORE elsewhere)
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def _save(d, path=None):
    path = path or STORE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")


def auto_cfg(platform="youtube-en"):
    """auto_publish (English) / auto_publish_es (Vice Replay en Español, owner Nov 26: its own autonomous channel)."""
    key = "auto_publish_es" if platform == "youtube-es" else "auto_publish"
    try:
        c = json.loads(CONFIG.read_text()).get(key) or {}
    except (OSError, ValueError):
        c = {}
    default = ["12:30 PM", "7:00 PM"] if platform == "youtube-es" else ["8:00 AM", "6:00 PM"]
    return {"on": bool(c.get("on")), "max_per_day": int(c.get("max_per_day", 2)), "paused_reason": c.get("paused_reason"),
            "failures": int(c.get("consecutive_failures", 0)), "slots": list(c.get("slots") or default)}


def _set_cfg(platform="youtube-en", **kw):
    raw = CONFIG.read_text()
    cfg = json.loads(raw)
    cfg.setdefault("auto_publish_es" if platform == "youtube-es" else "auto_publish", {}).update(kw)
    indent = 2 if raw.startswith('{\n  "') else (1 if raw.startswith('{\n "') else None)
    CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=indent) + "\n")


def key_of(slug, item, platform):
    return f"{slug}:{item}:{platform}"


def transition(rec, new, note=""):
    old = rec.get("state") or "PRODUCED"
    if new not in ALLOWED.get(old, set()):
        raise Blocked(f"invalid state change {old} -> {new}")
    rec["state"] = new
    rec.setdefault("history", []).append([dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), old, new, note[:200]])
    del rec["history"][:-30]
    return rec


def set_state(slug, item, platform, new, note="", **info):
    d = _load()
    rec = d.setdefault(key_of(slug, item, platform), {"slug": slug, "item": item, "platform": platform,
                                                       "state": "PRODUCED"})
    transition(rec, new, note)
    rec.update(info)
    _save(d)
    return rec


# ---------- fingerprints ----------

def _file_hash(p):
    p = Path(p) if Path(p).is_absolute() else ROOT / p
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def item_spec(ep, item):
    """The parts of an episode that make up one video item and its package."""
    if item == "short":
        return {k: v for k, v in ep.items() if k not in IGNORED and k not in ("shorts", "segments", "title",
                                                                              "description", "es", "thumbnail")}
    if item == "main":
        return {k: v for k, v in ep.items() if k not in IGNORED and k not in ("short", "shorts", "short_title",
                                                                              "short_description", "short_es")}
    sh = next((s for s in ep.get("shorts", []) if s.get("id") == item), None)
    if sh is None:
        raise KeyError(f"no item {item!r} in {ep.get('slug')}")
    return {"item": {k: v for k, v in sh.items() if k not in IGNORED}, "sources": ep.get("sources"),
            "tags": ep.get("tags")}


EN_PACKAGE = ("short_title", "short_description", "tags", "hashtags", "pinned_comment", "related_video")
ES_PACKAGE = ("short_es", "short_pinned_comment_es", "pinned_comment_es")


def spec_hash(ep, item, platform=None):
    """Fingerprint of what one channel would post. With a YouTube platform and the main Short it covers only what that
    language uses (Phase 3 #10): that render's inputs (studio/renderdeps.py), its title/description/tags/pinned comment,
    and the shared facts (sources, claim status). An English-only wording fix leaves the Spanish approval valid; a
    shared change (cards, pictures, sources, spot number) invalidates both."""
    if platform in ("youtube-en", "youtube-es") and item == "short":
        lang = "es" if platform == "youtube-es" else "en"
        spec = {"video": renderdeps.video_inputs(ep, item, lang),
                "package": {k: ep.get(k) for k in (ES_PACKAGE if lang == "es" else EN_PACKAGE)},
                "facts": {k: ep.get(k) for k in ("sources", "claim_status", "claims")}}
        return hashlib.sha256(json.dumps(spec, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    spec = item_spec(ep, item)
    audio = sorted(set(re.findall(r'"audio(?:_es)?": "([^"]+)"', json.dumps(spec))))
    blob = json.dumps({"spec": spec, "audio": {a: _file_hash(a) for a in audio}}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode()).hexdigest()


def code_hash():
    """The code the tests ran against: studio/ and tools/ Python files (a change means the tests must run again)."""
    h = hashlib.sha256()
    for p in sorted([*(ROOT / "studio").rglob("*.py"), *(ROOT / "tools").glob("*.py")]):
        h.update(p.relative_to(ROOT).as_posix().encode())
        h.update(p.read_bytes())
    return h.hexdigest()


# ---------- checks ----------

def _when(publish):
    if publish in (None, "now"):
        return None
    d, t = publish
    return dt.datetime.strptime(f"{d} {t}", "%Y-%m-%d %I:%M %p").replace(tzinfo=ET)


def _video_path(slug, item, platform="youtube-en"):
    out = ROOT / "output" / slug
    if item == "main":
        return out / f"{slug}.mp4"
    return out / (f"{slug}-short" + ("" if item == "short" else f"-{item}") + ("-es" if platform == "youtube-es" else "")
                  + ".mp4")


def postguard_norm(t):
    import re as _re
    return _re.sub(r"[^a-z0-9áéíóúñü$%']+", " ", _re.sub(r"#\w+", "", (t or "").lower())).strip()


def _title_desc(video):
    p = video.with_suffix(".txt")
    if not p.exists():
        return None, None
    m = re.search(r"TITLE\n(.+?)\n\nDESCRIPTION\n(.*)", p.read_text(), re.S)
    return (m.group(1).strip(), m.group(2).strip()) if m else (None, None)


def _probe(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
                        "-of", "json", str(video)], capture_output=True, text=True)
    try:
        j = json.loads(r.stdout)
    except ValueError:
        return None
    v = next((s for s in j.get("streams", []) if s.get("codec_type") == "video"), {})
    return {"w": v.get("width"), "h": v.get("height"), "audio": any(s.get("codec_type") == "audio" for s in j.get("streams", [])),
            "dur": float(j.get("format", {}).get("duration") or 0)}


def segments(ep, item):
    if item == "short":
        return ep.get("short") or []
    if item == "main":
        return ep.get("segments") or []
    return next((s.get("segments", []) for s in ep.get("shorts", []) if s.get("id") == item), [])


def plan_format_ok(ep, item, platform="youtube-en"):
    """Condition 8. English (directive v2.0 allocation): location guides, map tutorials, or a marked experiment.
    Spanish (owner Nov 26, its own identity): secrets, guides, tips, quizzes, comparisons, Miami vs Vice City,
    Latino humour... anything with a real angle; only bare headline/news cards are held."""
    types = {(s.get("chart") or {}).get("type") for s in segments(ep, item)}
    if platform == "youtube-es":
        return bool(types - {None, "headline"}) or bool(ep.get("experiment"))
    return "map" in types or ep.get("format") in ("tips", "tutorial") or bool(ep.get("experiment"))


def _registry(platform="youtube-en"):
    name = "uploads-es.json" if platform == "youtube-es" else "uploads.json"
    try:
        return json.loads((ROOT / "content" / "learn" / name).read_text())
    except (OSError, ValueError):
        return {}


def tests_ok(now=None):
    t = _load(TESTS)
    if not t.get("passed") or t.get("code") != code_hash():
        return False, "the test suite hasn't passed on the current code (python -m studio.approvals tests)"
    when = dt.datetime.fromisoformat(t["at"])
    if (now or dt.datetime.now(ET)) - when > dt.timedelta(hours=36):
        return False, "the last passing test run is older than 36 h (python -m studio.approvals tests)"
    return True, ""


def run_tests():
    env = dict(os.environ, OPENAI_API_KEY="", PEXELS_API_KEY="", PIXABAY_API_KEY="")
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "tests"], cwd=ROOT, capture_output=True, text=True,
                       env=env, timeout=1800)
    tail = (r.stdout.strip().splitlines() or [""])[-1]
    _save({"passed": r.returncode == 0, "summary": tail, "code": code_hash(),
           "at": dt.datetime.now(ET).isoformat(timespec="seconds")}, TESTS)
    return r.returncode == 0, tail


def gate(ep_path, platform="youtube-en"):
    """studio.vice publish -> (blockers, advice). Any blocker fails conditions 2-5. The Spanish channel's QA runs on
    the Spanish render (QC: frames, loudness, Spanish captions vs Spanish speech)."""
    lang = ["--lang", "es"] if platform == "youtube-es" else []
    r = subprocess.run([sys.executable, "-m", "studio.vice", "publish", str(ep_path), *lang], cwd=ROOT,
                       capture_output=True, text=True)
    out = r.stdout + r.stderr
    try:
        j = json.loads(out[out.find("{"):out.rfind("}") + 1])
        return j.get("blockers", []), j.get("advice", [])
    except ValueError:
        return [f"publish check did not run: {out[-200:]}"], []


def checks(ep_path, item="short", platform="youtube-en", publish=None, now=None, run_gate=True, store=None):
    """The 10 conditions. Returns (blockers, reviews, info): blockers = must be fixed; reviews = must be decided."""
    ep_path = Path(ep_path)
    ep = json.loads(ep_path.read_text())
    slug, now = ep["slug"], now or dt.datetime.now(ET)
    block, review, info = [], [], {}
    cfg = auto_cfg(platform)
    # 10: scope and switches
    if platform not in ("youtube-en", "youtube-es"):
        review.append("auto-publishing covers YouTube only (TikTok and Instagram keep their own arrangements)")
    if not cfg["on"]:
        review.append(f"auto-publishing is paused ({cfg['paused_reason'] or 'switched off'})")
    when = _when(publish)
    if publish is None:
        review.append("no publishing slot")
    elif when is not None and when <= now:
        review.append(f"the slot {publish} has passed: never post a missed slot automatically")
    if when is not None and when.strftime("%-I:%M %p") not in cfg["slots"]:
        # Nov 26: the authorization covers the plan's slots only (EN 8:00 AM / 6:00 PM, ES 12:30 PM / 7:00 PM)
        review.append(f"{publish[1]} is not an auto-publishing slot ({' / '.join(cfg['slots'])}): book a plan slot")
    if when is not None:
        d = store if store is not None else _load()
        same_day = [r for k, r in d.items() if r.get("platform") == platform and r.get("state") in
                    ("AUTO_APPROVED", "UPLOADING", "SCHEDULED", "PUBLISHED") and str(r.get("publish", [""])[0]) ==
                    when.date().isoformat() and k != key_of(slug, item, platform)]
        if len(same_day) >= cfg["max_per_day"]:
            review.append(f"already {len(same_day)} auto-published Shorts on {when.date()} (max {cfg['max_per_day']})")
    # 1: facts
    if len(ep.get("sources") or []) < 2:
        block.append("fewer than 2 sources in the episode")
    # Phase 6 #5: claim-level ledger (studio/sources.py): unsupported material claims or non-confirmed claims said as
    # fact are held; from `claims_required_from` on, a Short needs its ledger (written at the 2-day re-check)
    from . import sources
    if ep.get("claims"):
        sv = sources.evaluate(ep)
        block.extend("sources: " + b for b in sv["blockers"])
    else:
        try:
            req_from = json.loads((ROOT / "config" / "channel.json").read_text()).get("claims_required_from")
        except (OSError, ValueError):
            req_from = None
        if req_from and (when or now).date().isoformat() >= req_from:
            review.append("no claim ledger (\"claims\": source type, direct or search-summary, independence, "
                          "confidence, wording; python -m studio.sources episodes/<slug>.json)")
    fc = (_load(FACTS).get(slug) or {}).get("date") or ep.get("facts_checked")
    target = (when or now).date()
    if not fc:
        review.append("facts not re-checked before posting (python -m studio.approvals factcheck ...)")
    elif (target - dt.date.fromisoformat(fc)).days > 2:
        review.append(f"facts last re-checked {fc}: re-check within 2 days of the slot")
    # 8: plan / value
    if not plan_format_ok(ep, item, platform):
        review.append("format outside the 14-day plan (location guide, map tutorial or marked experiment)")
    # 9: tests
    ok, why = tests_ok(now)
    if not ok:
        review.append(why)
    # render: exists, fresh, 1080x1920, audio, 8-60 s
    video = _video_path(slug, item, platform)
    if platform == "youtube-es":  # the Spanish channel only ever gets a Spanish render with Spanish text everywhere
        segs = segments(ep, item)
        if not segs or not all(x.get("text_es") for x in segs):
            block.append("a segment has no Spanish line (text_es): no Spanish render possible")
        missing = [x["audio_es"] for x in segs if x.get("audio_es") and not _file_hash(x["audio_es"])]
        if missing:
            block.append(f"Spanish voice files missing: {missing[:2]}")
        es_meta = (ep.get("short_es") if item == "short" else
                   next((x.get("es") for x in ep.get("shorts", []) if x.get("id") == item), None)) or ep.get("es") or {}
        if not es_meta.get("title"):
            block.append("no Spanish title (short_es.title)")
    if not video.exists():
        block.append(f"no rendered video {video.name}")
    else:
        # Phase 3: per-language inputs (studio/renderdeps.py); an English-only edit no longer stales the Spanish video
        lang = "es" if platform == "youtube-es" else "en"
        st = renderdeps.status(video, ep, item, lang, ep_path) if item != "main" else (
            "stale-mtime" if video.stat().st_mtime < ep_path.stat().st_mtime else "current-mtime")
        info["render_status"] = st
        if st in ("stale-video", "stale-mtime"):
            block.append(f"{video.name}: what it's made of changed since it was rendered: re-render (python -m "
                         f"studio.make_video {ep_path.relative_to(ROOT) if ep_path.is_relative_to(ROOT) else ep_path} "
                         f"--short{' --es' if lang == 'es' else ''})")
        elif st == "stale-package":
            block.append(f"{video.name}: title/description changed: python -m studio.make_video "
                         f"episodes/{slug}.json --short{' --es' if lang == 'es' else ''} --meta-only")
        p = _probe(video) or {}
        if (p.get("w"), p.get("h")) != (1080, 1920) and item != "main":
            block.append(f"video is {p.get('w')}x{p.get('h')}, not 1080x1920")
        if not p.get("audio"):
            block.append("no audio stream")
        if item != "main" and not 8 <= p.get("dur", 0) <= 60:
            block.append(f"duration {p.get('dur', 0):.1f} s is outside 8-60 s")
        info["video"], info["duration"] = str(video.relative_to(ROOT)), round(p.get("dur", 0), 1)
        # 6: title and description
        title, desc = _title_desc(video)
        want = ep.get("short_title") if item == "short" and platform == "youtube-en" else None
        if platform == "youtube-es":
            want = ((ep.get("short_es") or {}).get("title") if item == "short" else None)
            if title and title.strip() == (ep.get("short_title") or "").strip():
                block.append("the Spanish render carries the English title")
        if not title or not desc:
            block.append("rendered title/description missing (render with studio.ship)")
        else:
            if not title.startswith("GTA"):
                review.append(f"title doesn't start with GTA 6: {title!r}")
            if len(title) > 100:
                block.append("title longer than 100 characters")
            if want and title.strip() != want.strip() and postguard_norm(title) != postguard_norm(want):
                block.append(f"rendered title {title!r} differs from the episode's {want!r}: re-render")
        info["title"], info["description"] = title, desc
    # 7: duplicates
    reg = _registry(platform)
    if any((r.get("slug"), r.get("item")) == (slug, item) for r in reg.values()):
        block.append("already uploaded (registry)")
    if info.get("title") and any((r.get("title") or "").strip() == info["title"].strip() for r in reg.values()):
        block.append("a video with this exact title is already on the channel")
    # 2-5: rights, spoilers/safety, QC (frames, loudness, captions vs speech), hooks
    if run_gate and not block:
        b, advice = gate(ep_path, platform)
        block += [f"QA: {x}" for x in b]
        info["advice"] = advice
    return block, review, info


def evaluate(ep_path, item="short", platform="youtube-en", publish=None, now=None, run_gate=True):
    """Runs the checks and records the verdict: AUTO_APPROVED, BLOCKED or NEEDS_REVIEW (with the reasons)."""
    ep = json.loads(Path(ep_path).read_text())
    slug = ep["slug"]
    block, review, info = checks(ep_path, item, platform, publish, now, run_gate)
    d = _load()
    k = key_of(slug, item, platform)
    rec = d.get(k) or {"slug": slug, "item": item, "platform": platform, "state": "PRODUCED"}
    if rec.get("state") in DONE:
        raise Blocked(f"{slug} ({item}) is already {rec['state']} on {platform}")
    if rec["state"] in ("FAILED",):
        raise Blocked(f"{slug} ({item}): the last upload failed; reconcile with the platform first")
    if rec["state"] != "RENDERED":
        transition(rec, "RENDERED", "evaluating")
    rec.update({"publish": "now" if publish == "now" else list(publish) if publish else None,
                "title": info.get("title"), "video": info.get("video"), "duration": info.get("duration"),
                "spec_hash": spec_hash(ep, item, platform), "evaluated_at": dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"),
                "blockers": block, "reviews": review, "advice": info.get("advice", [])})
    if info.get("video"):
        rec["video_sha256"] = _file_hash(info["video"])
    if block:
        transition(rec, "BLOCKED", "; ".join(block)[:200])
    elif review:
        transition(rec, "QA_PASSED", "technical checks passed")
        transition(rec, "NEEDS_REVIEW", "; ".join(review)[:200])
    else:
        transition(rec, "QA_PASSED", "all technical checks passed")
        transition(rec, "AUTO_APPROVED", "all 10 publishing conditions passed")
    d[k] = rec
    _save(d)
    return rec


def require(slug, item, platform, title=None, publish=None, video=None, ep=None, now=None, store=None):
    """What every uploader asks right before sending. Returns the record or raises Blocked."""
    d = store if store is not None else _load()
    rec = d.get(key_of(slug, item, platform))
    cfg = auto_cfg(platform)
    if not cfg["on"]:
        raise Blocked(f"auto-publishing is paused ({cfg['paused_reason'] or 'switched off'})")
    if not rec:
        raise Blocked(f"{slug} ({item}) has not passed the publishing gate on {platform} (python -m studio.approvals "
                      f"evaluate ...)")
    if rec.get("state") == "FAILED":
        raise Blocked(f"{slug} ({item}): the last upload failed; reconcile with {platform} first (never upload blindly)")
    if rec.get("state") != "AUTO_APPROVED":
        raise Blocked(f"{slug} ({item}) on {platform} is {rec.get('state')}: "
                      f"{'; '.join(rec.get('blockers') or rec.get('reviews') or []) or 'not approved'}")
    ep = ep if ep is not None else json.loads((ROOT / "episodes" / f"{slug}.json").read_text())
    if spec_hash(ep, item, platform) != rec.get("spec_hash"):
        transition(rec, "NEEDS_REVIEW", "content changed after the gate passed: evaluate again")
        if store is None:
            _save(d)
        raise Blocked(f"{slug} ({item}) changed after it passed the gate: evaluate it again")
    if video is not None and rec.get("video_sha256") and _file_hash(video) != rec["video_sha256"]:
        # Phase 3 #15: the file being sent must be byte-for-byte the one that passed QA
        transition(rec, "NEEDS_REVIEW", "video file changed after the gate passed (SHA-256 mismatch)")
        if store is None:
            _save(d)
        raise Blocked(f"{slug} ({item}): the video file differs from the one that passed QA (SHA-256): evaluate again")
    if title is not None and title.strip() != (rec.get("title") or "").strip():
        raise Blocked(f"title {title!r} differs from the checked {rec.get('title')!r}")
    if publish is not None and str(publish if publish == "now" else list(publish)) != str(rec.get("publish")):
        raise Blocked(f"slot {publish} differs from the checked {rec.get('publish')}")
    when = _when(rec.get("publish"))
    if when is not None and when <= (now or dt.datetime.now(ET)):
        raise Blocked(f"the slot {rec['publish']} has passed: a missed slot is never posted automatically")
    return rec


def allowed(slug, item, platform, **kw):
    try:
        require(slug, item, platform, **kw)
        return True, ""
    except Blocked as e:
        return False, str(e)


def reconcile(slug, item, platform, found_id=None):
    """After a failed or timed-out upload the caller asked the platform: found -> SCHEDULED/PUBLISHED with that id,
    not found -> back to AUTO_APPROVED so the same checked package can be sent once."""
    d = _load()
    rec = d.get(key_of(slug, item, platform))
    if not rec or rec.get("state") not in ("FAILED", "UPLOADING"):
        return rec
    if found_id:
        transition(rec, "SCHEDULED", f"reconciled: already on {platform} ({found_id})")
        rec["video_id"] = found_id
    elif rec["state"] == "FAILED":
        transition(rec, "AUTO_APPROVED", f"reconciled: not on {platform}; the checked package may be sent once")
    _save(d)
    return rec


def upload_result(ok, note="", platform="youtube-en"):
    """Count failures in a row; two pause that channel's auto-publishing (directive section 7)."""
    cfg = auto_cfg(platform)
    if ok:
        if cfg["failures"]:
            _set_cfg(platform, consecutive_failures=0)
        return
    n = cfg["failures"] + 1
    if n >= 2:
        _set_cfg(platform, consecutive_failures=n, on=False, paused_reason=f"{n} upload failures in a row: {note[:120]}")
    else:
        _set_cfg(platform, consecutive_failures=n)


def verify(now=None):
    """Directive section 6: never report a video as published without checking the platform. SCHEDULED videos whose
    slot passed are looked up on YouTube; public ones become PUBLISHED. Returns report lines."""
    from .youtube_upload import req, token
    d, now = _load(), now or dt.datetime.now(ET)
    due = {k: r for k, r in d.items() if r.get("platform") == "youtube-en" and r.get("state") == "SCHEDULED"
           and r.get("video_id") and (_when(r.get("publish")) or now) <= now}
    lines = []
    if not due:
        return lines
    ids = ",".join(r["video_id"] for r in due.values())
    res, _ = req("GET", f"https://youtube.googleapis.com/youtube/v3/videos?part=status,snippet&id={ids}", token())
    live = {v["id"]: v for v in res.get("items", [])}
    for k, r in due.items():
        v = live.get(r["video_id"])
        status = (v or {}).get("status", {}).get("privacyStatus")
        if status == "public":
            transition(r, "PUBLISHED", "verified public on YouTube")
            r["published_verified"] = now.strftime("%Y-%m-%d %H:%M ET")
            lines.append(f"PUBLISHED {r['publish'][0]} {r['publish'][1]} ET  https://youtube.com/shorts/{r['video_id']}  "
                         f"{r.get('title')}")
        else:
            lines.append(f"! NOT PUBLIC YET ({status or 'not found'}): {r.get('title')} ({r['video_id']})")
    _save(d)
    return lines


def stamp_factcheck(ep_path, note):
    """Record that the episode's facts were re-checked today against its sources (condition 1)."""
    slug = json.loads(Path(ep_path).read_text())["slug"]
    d = _load(FACTS)
    d[slug] = {"date": dt.datetime.now(ET).date().isoformat(), "note": note[:300]}
    _save(d, FACTS)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["evaluate", "factcheck", "tests", "status", "pause", "resume", "verify"])
    ap.add_argument("target", nargs="?")
    ap.add_argument("--item", default="short")
    ap.add_argument("--platform", default="youtube-en")
    ap.add_argument("--at", help='"YYYY-MM-DD H:MM AM" (ET) or "now"')
    ap.add_argument("--note", default="")
    a = ap.parse_args()
    if a.cmd == "evaluate":
        at = "now" if a.at == "now" else (tuple(a.at.split(" ", 1)) if a.at else None)
        try:
            r = evaluate(a.target, a.item, a.platform, at)
        except Blocked as e:
            sys.exit(f"BLOCKED: {e}")
        print(f"{r['state']}: {r['slug']} ({r['item']}) {r.get('publish')}  {r.get('title')}")
        for x in r.get("blockers", []) + r.get("reviews", []):
            print("  -", x)
    elif a.cmd == "factcheck":
        if not a.note.strip():
            sys.exit("say what was re-checked (--note)")
        stamp_factcheck(a.target, a.note)
        print(f"facts re-checked today: {a.target}")
    elif a.cmd == "tests":
        ok, tail = run_tests()
        print(("PASSED: " if ok else "FAILED: ") + tail)
        sys.exit(0 if ok else 1)
    elif a.cmd == "verify":
        for line in verify() or ["nothing due to verify"]:
            print(line)
    elif a.cmd == "pause":
        _set_cfg(a.platform, on=False, paused_reason=a.target or "paused by hand")
        print(f"auto-publishing paused ({a.platform})")
    elif a.cmd == "resume":
        _set_cfg(a.platform, on=True, paused_reason=None, consecutive_failures=0)
        print(f"auto-publishing on ({a.platform})")
    else:
        for pf in ("youtube-en", "youtube-es"):
            cfg = auto_cfg(pf)
            print(f"auto-publishing {pf}: {'ON' if cfg['on'] else 'PAUSED: ' + str(cfg['paused_reason'])}, "
                  f"max {cfg['max_per_day']}/day")
        for k, r in sorted(_load().items(), key=lambda kv: str(kv[1].get("publish"))):
            print(f"{r.get('state', '?'):14} {k:52} {r.get('publish')}  {(r.get('title') or '')[:50]}")
            for x in (r.get("blockers") or []) + (r.get("reviews") or []):
                print(f"{'':16}- {x[:110]}")


if __name__ == "__main__":
    main()
