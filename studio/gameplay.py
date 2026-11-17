"""Gameplay pipeline: download the owner's clips from a shared Google Drive folder and turn them into
highlight clips for the footage library (media/gameplay/) and "wildest moment" Shorts.

    python -m studio.gameplay                 # uses the Drive link in content/owner.md
    python -m studio.gameplay --link URL      # a specific Drive folder or file link
    python -m studio.gameplay --top 3         # highlights per recording (default 3)

Recordings are cached in media/gameplay/raw/ (not committed); a recording is only processed once.
Highlights land in media/gameplay/ as 16:9 clips (no voice, game sound only), so make_video uses them
as backgrounds automatically, and their paths are listed for "wildest moment" Shorts.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "media" / "gameplay" / "raw"
OUT = ROOT / "media" / "gameplay"
DONE = OUT / "processed.json"
VIDEO_EXT = {".mp4", ".mov", ".mkv", ".webm", ".m4v"}


def drive_link_from_owner():
    txt = (ROOT / "content" / "owner.md").read_text()
    m = re.search(r"https://drive\.google\.com/\S+", txt)
    return m.group(0).rstrip(").,") if m else None


def download(link):
    import gdown
    RAW.mkdir(parents=True, exist_ok=True)
    if "/folders/" in link:
        gdown.download_folder(url=link, output=str(RAW), quiet=False, resume=True, retries=2)
    else:
        gdown.download(url=link, output=str(RAW) + "/", quiet=False, fuzzy=True, resume=True)


def highlights(src, top):
    """Use the clip finder's scoring, then cut 16:9 clips (no reframing) into media/gameplay/."""
    from .clip import find_moments, probe
    total, _, _ = probe(src)
    length = min(12.0, total)
    made = []
    for k, (start, score) in enumerate(find_moments(src, top, length, total), 1):
        out = OUT / f"{re.sub(r'[^a-z0-9]+', '-', src.stem.lower()).strip('-')}-{k:02d}.mp4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{start:.2f}", "-t", f"{length:.2f}", "-i", str(src),
                        "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "160k", str(out)], check=True)
        made.append({"file": str(out.relative_to(ROOT)), "from": src.name, "start": round(start, 1), "score": score})
    return made


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--link")
    ap.add_argument("--top", type=int, default=3)
    a = ap.parse_args()
    link = a.link or drive_link_from_owner()
    if not link:
        sys.exit("No Google Drive link: add one to content/owner.md (Gameplay Drive folder) or pass --link.")
    print(f"Downloading gameplay from {link} ...")
    download(link)
    done = json.loads(DONE.read_text()) if DONE.exists() else {}
    new = [p for p in sorted(RAW.rglob("*")) if p.suffix.lower() in VIDEO_EXT and p.name not in done]
    if not new:
        print("No new recordings.")
        return
    for src in new:
        print(f"Finding highlights in {src.name} ...")
        done[src.name] = highlights(src, a.top)
        DONE.write_text(json.dumps(done, indent=2))
    print("\nNew highlight clips:")
    for src in new:
        for h in done[src.name]:
            print(f"  {h['file']}  (from {h['from']} at {h['start']}s, score {h['score']})")


if __name__ == "__main__":
    main()
