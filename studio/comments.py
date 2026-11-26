"""Our own top comment on a video, posted safely (owner Nov 26, Phase 6 #8: "Permission preflight, correct channel
verification, existing-comment detection, duplicate prevention, relevant comment generation, affiliate compliance
checks, comment posting confirmation, failed-operation reporting... Do not claim that a comment has been pinned unless
pinning has actually been verified.").

    python -m studio.comments check <video_id> [--lang en|es]                  # preflight only, posts nothing
    python -m studio.comments post <video_id> --slug <episode> [--lang en|es]   # the episode's pinned-comment text
    python -m studio.comments post <video_id> --text "..." [--lang en|es]

Steps (stops at the first failure, prints COMMENT FAILED: <step>: <why>, records it, exits 1):
  1 token: the token belongs to the expected channel (English: Vice Replay, Spanish: Vice Replay en Español)
  2 video: exists, is OURS on that channel, and is public
  3 duplicates: no top-level comment from our channel on it yet (YouTube) and none in content/learn/our-comments.json
  4 text: not empty, <= 500 characters, not generic; Amazon links only if studio.affiliate allows them for THIS video
  5 post, then read the comment back from YouTube (id + text) and record it
Pinning: YouTube's API has no pin call, so this never says "pinned"; the owner pins in YouTube Studio.
"""
import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "content" / "learn" / "our-comments.json"  # comments.json = viewer comments (studio.learn)
API = "https://youtube.googleapis.com/youtube/v3"
GENERIC = ("great video", "check out my", "subscribe", "first!")


class Fail(Exception):
    def __init__(self, step, why):
        super().__init__(f"{step}: {why}")
        self.step, self.why = step, why


def channel_id(lang):
    cfg = json.loads((ROOT / "config" / "channel.json").read_text())["channels"]
    return cfg["vice-replay-es" if lang == "es" else "vice-replay"]["channel_id"]


def token(lang):
    if lang == "es":
        from . import youtube_es as y
        return y.token_for(channel_id("es"), y.ENV)
    from .youtube_upload import token as t
    return t()


def _req():
    from .youtube_upload import req
    return req


def ledger():
    try:
        return json.loads(LEDGER.read_text())
    except (OSError, ValueError):
        return {"posted": {}, "failed": []}


def save(led):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(led, indent=1, ensure_ascii=False) + "\n")


def episode_text(slug, lang):
    ep = json.loads((ROOT / "episodes" / f"{slug}.json").read_text())
    text = ep.get("short_pinned_comment_es" if lang == "es" else "pinned_comment") or (
        ep.get("pinned_comment_es") if lang == "es" else None)
    from . import affiliate
    return text, affiliate.episode_text(ep)


def check_text(text, topic):
    if not text or not text.strip():
        raise Fail("text", "empty comment")
    if len(text) > 500:
        raise Fail("text", f"{len(text)} characters (keep it under 500)")
    if any(g in text.lower() for g in GENERIC):
        raise Fail("text", "generic/self-promo wording; the comment should add something about this video")
    from . import affiliate
    probs = affiliate.check(text, topic)
    if probs:
        raise Fail("affiliate", "; ".join(probs))


def preflight(vid, lang, req=None, tok=None):
    """Steps 1-3. Returns (tok, video snippet). Raises Fail."""
    req = req or _req()
    want = channel_id(lang)
    try:
        tok = tok or token(lang)
    except SystemExit as e:
        raise Fail("token", str(e))
    mine, _ = req("GET", f"{API}/channels?part=id&mine=true", tok)
    got = (mine.get("items") or [{}])[0].get("id")
    if got != want:
        raise Fail("token", f"the {lang.upper()} token belongs to {got}, not {want}")
    v, _ = req("GET", f"{API}/videos?part=status,snippet&id={vid}", tok)
    items = v.get("items") or []
    if not items:
        raise Fail("video", f"{vid} not found")
    sn, st = items[0]["snippet"], items[0]["status"]
    if sn.get("channelId") != want:
        raise Fail("video", f"{vid} belongs to channel {sn.get('channelId')}, not ours ({want})")
    if st.get("privacyStatus") != "public":
        raise Fail("video", f"{vid} is {st.get('privacyStatus')} (publishAt {st.get('publishAt')}): post after it goes public")
    if vid in ledger().get("posted", {}):
        raise Fail("duplicate", f"already commented on {vid} (content/learn/our-comments.json)")
    threads, _ = req("GET", f"{API}/commentThreads?part=snippet&maxResults=100&order=time&videoId={vid}", tok)
    for t in threads.get("items", []):
        top = t["snippet"]["topLevelComment"]["snippet"]
        if (top.get("authorChannelId") or {}).get("value") == want:
            raise Fail("duplicate", f"our channel already has a comment on {vid}: {top.get('textOriginal', '')[:60]!r}")
    return tok, sn


def post(vid, text, lang="en", topic="", req=None, tok=None, dry=False):
    req = req or _req()
    tok, sn = preflight(vid, lang, req, tok)
    check_text(text, topic or sn.get("title", "") + " " + sn.get("description", "")[:300])
    if dry:
        return {"video": vid, "would_post": text}
    body = {"snippet": {"videoId": vid, "topLevelComment": {"snippet": {"textOriginal": text}}}}
    try:
        res, _ = req("POST", f"{API}/commentThreads?part=snippet", tok, body)
    except SystemExit as e:
        raise Fail("post", str(e))
    cid = res.get("id")
    if not cid:
        raise Fail("post", f"YouTube returned no comment id: {str(res)[:120]}")
    got = {}
    for wait in (0, 2, 4, 8):  # YouTube can take a few seconds to list a new comment (Nov 26: empty at 0 s)
        time.sleep(wait)
        back, _ = req("GET", f"{API}/commentThreads?part=snippet&id={cid}", tok)
        item = (back.get("items") or [{}])[0].get("snippet", {})
        if item.get("videoId") == vid:
            got = item.get("topLevelComment", {}).get("snippet", {})
            break
    if not got:  # posted (YouTube gave an id) but not listed yet: record it so nothing posts twice
        led = ledger()
        led.setdefault("posted", {})[vid] = {"comment_id": cid, "lang": lang, "text": text, "unconfirmed": True,
                                             "posted": dt.datetime.now(dt.timezone.utc).isoformat()[:19]}
        save(led)
        raise Fail("confirm", f"YouTube accepted comment {cid} but didn't list it within 14 s; recorded, NOT reposting")
    rec = {"comment_id": cid, "lang": lang, "text": got.get("textOriginal", text),
           "url": f"https://www.youtube.com/watch?v={vid}&lc={cid}", "posted": dt.datetime.now(dt.timezone.utc).isoformat()[:19],
           "pinned": "not verified (YouTube's API can't pin; pin it in YouTube Studio)"}
    led = ledger()
    led.setdefault("posted", {})[vid] = rec
    save(led)
    return rec


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m studio.comments")
    ap.add_argument("cmd", choices=["check", "post"])
    ap.add_argument("video")
    ap.add_argument("--lang", choices=["en", "es"], default="en")
    ap.add_argument("--slug")
    ap.add_argument("--text")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    text, topic = a.text, ""
    try:
        if a.slug:
            ep_text, topic = episode_text(a.slug, a.lang)
            text = text or ep_text
        if a.cmd == "check":
            _, sn = preflight(a.video, a.lang)
            if text:
                check_text(text, topic or sn.get("title", ""))
            print(f"PREFLIGHT OK: {a.video} is public on our {a.lang.upper()} channel, no comment of ours yet"
                  + (f"; text ok: {text!r}" if text else ""))
            return
        rec = post(a.video, text, a.lang, topic, dry=a.dry_run)
        if a.dry_run:
            print(f"DRY RUN OK: would post on {a.video}: {rec['would_post']!r}")
            return
        print(f"COMMENT POSTED (confirmed on YouTube): {rec['url']}\n  text: {rec['text']!r}\n  pinned: {rec['pinned']}")
    except Fail as f:
        if a.cmd == "check":  # a preflight records nothing
            print(f"COMMENT FAILED: {f.step}: {f.why}")
            sys.exit(1)
        led = ledger()
        led.setdefault("failed", []).append({"video": a.video, "lang": a.lang, "step": f.step, "why": f.why,
                                             "at": dt.datetime.now(dt.timezone.utc).isoformat()[:19]})
        led["failed"] = led["failed"][-50:]
        save(led)
        print(f"COMMENT FAILED: {f.step}: {f.why}")
        sys.exit(1)


if __name__ == "__main__":
    main()
