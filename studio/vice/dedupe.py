"""Duplicate detection: identical footage (perceptual hash of frames) and the same event in a different edit
(text similarity of the moment's description from the same creator within a few days).

Free and local: ffmpeg grabs 3 small frames, Pillow computes a 64-bit difference hash (dHash) per frame.
"""
import datetime as dt
import re
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

STOP = set("the a an to of in on and is it for with you your this that his he her she my was what when how why just "
           "gta 6 vi gta6 gtavi grand theft auto shorts short viral fyp funny clips clip stream streamer first time "
           "gets got goes went day did does not no be at by from into out up so i im its it's he's s new in game "
           "lacy kreekcraft kreek xqc speed ishowspeed kai cenat n3on 😭 💀".split())


def tokens(text):
    t = re.sub(r"#\w+|@\w+|https?://\S+", " ", (text or "").lower())
    t = re.sub(r"[^\w\s]", " ", t)
    words = [w for w in t.split() if w not in STOP and len(w) > 2]
    return {w[:-1] if w.endswith("s") and len(w) > 4 else w for w in words}  # crude plural folding


def event_key(creator, description):
    return f"{(creator or '').lower()}:{' '.join(sorted(tokens(description)))}"


def jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a and b else 0.0


def same_event(c1, c2, threshold=0.5, days=3):
    """Two candidates describe the same real event: same creator, close dates, overlapping description words."""
    if (c1.get("creator") or "").lower() != (c2.get("creator") or "").lower():
        return False
    d1, d2 = c1.get("published"), c2.get("published")
    if d1 and d2:
        t1 = dt.datetime.fromisoformat(d1[:19].replace("Z", ""))
        t2 = dt.datetime.fromisoformat(d2[:19].replace("Z", ""))
        if abs((t1 - t2).total_seconds()) > days * 86400:
            return False
    return jaccard(tokens(c1.get("description")), tokens(c2.get("description"))) >= threshold


def dhash_image(img, size=8):
    g = img.convert("L").resize((size + 1, size), Image.LANCZOS)
    px = list(g.getdata())
    bits = 0
    for r in range(size):
        for c in range(size):
            bits = (bits << 1) | (px[r * (size + 1) + c] > px[r * (size + 1) + c + 1])
    return f"{bits:016x}"


def video_hash(path, every=1.0, max_frames=60):
    """dHash of one frame per `every` seconds (one ffmpeg call, 9x8 grey frames), joined with '-'."""
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(path), "-vf",
                          f"fps=1/{every},scale=9:8:flags=area,format=gray", "-frames:v", str(max_frames),
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    hashes = []
    for k in range(0, len(raw) - 71, 72):
        px = raw[k:k + 72]
        bits = 0
        for r in range(8):
            for c in range(8):
                bits = (bits << 1) | (px[r * 9 + c] > px[r * 9 + c + 1])
        hashes.append(f"{bits:016x}")
    return "-".join(hashes)


def hamming(h1, h2):
    return bin(int(h1, 16) ^ int(h2, 16)).count("1")


def overlap(vh1, vh2, max_bits=18):
    """Share of the shorter video's sampled frames that have a near-identical frame in the other video."""
    if not vh1 or not vh2:
        return 0.0
    a, b = vh1.split("-"), vh2.split("-")
    if len(a) > len(b):
        a, b = b, a
    a = [x for x in a if x not in ("0000000000000000", "ffffffffffffffff")]  # flat/black frames match anything
    if not a:
        return 0.0
    return sum(1 for x in a if any(hamming(x, y) <= max_bits for y in b)) / len(a)


def same_footage(vh1, vh2, threshold=0.7):
    """Repost: most frames of one video appear in the other (re-encoded, re-captioned, trimmed or extended)."""
    return overlap(vh1, vh2) >= threshold
