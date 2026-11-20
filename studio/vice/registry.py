"""Fingerprints of everything already published, so QC can refuse a repost (same footage, any edit).

    python -m studio.vice fingerprint      # hash every published file we still have locally (free, ~1 s each)
"""
import json

from . import db, dedupe

ROOT = db.ROOT
ITEM_FILE = {"short": "{slug}-short.mp4", "main": "{slug}.mp4", "news": "{slug}-news.mp4", "tips": "{slug}-tips.mp4"}


def published_files():
    out = []
    uploads = json.loads((ROOT / "content" / "learn" / "uploads.json").read_text())
    for vid, u in uploads.items():
        f = ROOT / "output" / u["slug"] / ITEM_FILE.get(u.get("item", "short"), "{slug}-short.mp4").format(slug=u["slug"])
        if f.exists():
            out.append((vid, f))
    tracker = ROOT / "content" / "campaigns" / "tracker.md"
    if tracker.exists():
        for clip in sorted((ROOT / "output" / "clips").rglob("*.mp4")):
            # campaign clips: the tracker row that links it (by file stem words) gives the video URL
            for line in tracker.read_text().splitlines():
                stem_words = clip.stem.split("-", 1)[-1].replace("-", " ")
                if stem_words.split()[0] in line.lower() and "http" in line:
                    url = next((c.strip() for c in line.split("|") if c.strip().startswith("http")), None)
                    out.append((url or clip.name, clip))
                    break
            else:
                out.append((clip.name, clip))
    return out


def fingerprint_all():
    con = db.connect()
    known = {r["source"] for r in db.rows(con, "SELECT source FROM used_footage")}
    added = 0
    for vid, f in published_files():
        src = str(f.relative_to(ROOT))
        if src in known:
            continue
        con.execute("INSERT INTO used_footage VALUES (?,?,?,?,?)", (dedupe.video_hash(f), src, vid, None, db.now()))
        added += 1
    con.commit()
    return added


def remember(path, video_id, project_id=None):
    con = db.connect()
    con.execute("INSERT INTO used_footage VALUES (?,?,?,?,?)",
                (dedupe.video_hash(path), str(path), video_id, project_id, db.now()))
    con.commit()
