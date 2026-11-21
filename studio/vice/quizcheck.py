"""Quiz give-away check (added Nov 21, 2026).

A "guess" segment (one with `magnify` in an episode whose format is "quiz") must not show its own answer. On the first
quiz render the zoomed taillights included the "Cheetah" badge and the blurred backdrop of guess #4 still read "Squalo";
both were caught only by eye. This reads the zoomed crop and the rendered frame with RapidOCR (free, CPU, Apache-2.0)
and returns a blocker for every answer word it can read. Answer words = the next segment's headline + narration
(4+ letters), minus words the guess segment itself says. Fuzzy match, because OCR reads "Cheetah" as "Lheetah".
"""
import difflib
import json
import re
import subprocess
import tempfile
from pathlib import Path

_ENGINE = {}


def _tokens(text):
    return {w for w in re.findall(r"[a-z]{4,}", (text or "").lower())}


def _ocr(path):
    if "e" not in _ENGINE:
        try:
            import logging
            from rapidocr import RapidOCR
            for name in ("RapidOCR", "rapidocr"):
                logging.getLogger(name).setLevel(logging.ERROR)
            for lg in list(logging.Logger.manager.loggerDict):
                if "ocr" in lg.lower():
                    logging.getLogger(lg).setLevel(logging.ERROR)
            _ENGINE["e"] = RapidOCR()
        except Exception:  # noqa: BLE001 - OCR missing must not break publishing; the caller reports it
            _ENGINE["e"] = None
    eng = _ENGINE["e"]
    if eng is None:
        return None
    r = eng(str(path))
    return " ".join(r.txts or []) if getattr(r, "txts", None) else ""


def leaks(read_text, answers):
    """Answer words that appear (fuzzily) in OCR text."""
    found = set()
    for w in _tokens(read_text):
        for a in answers:
            if difflib.SequenceMatcher(None, w, a).ratio() >= 0.8:
                found.add(a)
    return sorted(found)


def problems(ep, episode_path, video, timings_file):
    """Blockers (strings) for give-aways in quiz guesses; [] when the episode isn't a quiz."""
    segs = ep.get("short", [])
    if ep.get("format") != "quiz" or not any(s.get("magnify") for s in segs):
        return []
    base = Path(episode_path).resolve().parent
    timings = json.loads(Path(timings_file).read_text()) if timings_file and Path(timings_file).exists() else []
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, s in enumerate(segs[:-1]):
            if not s.get("magnify"):
                continue
            nxt = segs[i + 1]
            answers = (_tokens(nxt.get("headline")) | _tokens(nxt.get("text"))) - _tokens(s.get("text")) - _tokens(s.get("headline"))
            if not answers:
                continue
            reads = []
            media = (base / s["media"]).resolve() if s.get("media") else None
            if media and media.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"} and media.exists():
                from PIL import Image
                im = Image.open(media); W, H = im.size; b = s["magnify"]["box"]
                crop = Path(tmp) / f"crop{i}.png"
                im.crop((int(b[0] * W), int(b[1] * H), int(b[2] * W), int(b[3] * H))).save(crop)
                reads.append(("zoomed detail", _ocr(crop)))
            if i < len(timings) and Path(video).exists():
                frame = Path(tmp) / f"frame{i}.png"
                mid = (timings[i]["start"] + timings[i]["end"]) / 2
                subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{mid:.2f}", "-i", str(video),
                                "-frames:v", "1", str(frame)], check=False)
                if frame.exists():
                    reads.append(("rendered frame", _ocr(frame)))
            if any(t is None for _, t in reads):
                return ["quiz check: RapidOCR is not installed (pip install rapidocr), so give-aways can't be checked"]
            for where, text in reads:
                hit = leaks(text, answers)
                if hit:
                    out.append(f"quiz give-away: guess {i + 1} ({s.get('headline')}) shows the answer "
                               f"{', '.join(hit)} in the {where}; change the magnify box, media or focus")
    return out
