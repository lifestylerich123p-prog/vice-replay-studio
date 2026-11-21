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


DIRECT = "https://drive.usercontent.google.com/download?id={}&export=download&confirm=t"


def fetch(file_id, dest):
    """Download one Drive file through drive.usercontent.google.com (a fixed host the cloud proxy allows;
    gdown's own downloads redirect to doc-*.googleusercontent.com hosts, which the proxy blocks)."""
    import requests
    dest = Path(dest)
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with requests.get(DIRECT.format(file_id), stream=True, timeout=120) as r:
        r.raise_for_status()
        if "text/html" in r.headers.get("Content-Type", ""):
            raise RuntimeError(f"Drive returned a web page for {dest.name}: is the folder shared 'Anyone with the link'?")
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    tmp.rename(dest)
    print(f"  downloaded {dest.relative_to(RAW)} ({dest.stat().st_size / 1e6:.1f} MB)")
    return dest


def list_folder(folder_id, rel="", depth=0):
    """[(file id, relative path)] of a shared Drive folder and its subfolders, from Drive's public folder view.
    (Nov 21, 2026: gdown's lister tried to export the Google Doc shot list in the drop zone through a blocked host
    and crashed before reaching any video, so the drop zone could never be pulled.)"""
    import html
    import requests
    r = requests.get(f"https://drive.google.com/embeddedfolderview?id={folder_id}", timeout=60)
    r.raise_for_status()
    out = []
    for m in re.finditer(r'id="entry-([\w-]+)".*?href="([^"]+)".*?flip-entry-title">([^<]*)', r.text, re.S):
        fid, href, title = m.group(1), m.group(2), html.unescape(m.group(3)).strip()
        if "/folders/" in href:
            if depth < 3:
                out += list_folder(fid, f"{rel}{title}/", depth + 1)
        elif "/file/d/" in href:  # real files; Google Docs/Sheets (docs.google.com links) are skipped
            out.append((fid, f"{rel}{title}"))
    return out


def download(link):
    RAW.mkdir(parents=True, exist_ok=True)
    if "/folders/" in link:
        folder = re.search(r"/folders/([\w-]+)", link).group(1)
        for fid, rel in list_folder(folder):
            if Path(rel).suffix.lower() in VIDEO_EXT | {".png", ".jpg"}:
                try:
                    fetch(fid, RAW / rel)
                except Exception as e:  # one bad file shouldn't stop the rest
                    print(f"  skipped {rel}: {e}")
    else:
        m = re.search(r"/d/([\w-]+)|id=([\w-]+)", link)
        fid = next(g for g in m.groups() if g) if m else link
        fetch(fid, RAW / f"{fid}.mp4")


CATEGORIES = {"wild": "Wildest moments", "chase": "Chases & crashes", "funny": "Funny & fails",
              "glitch": "Glitches", "beauty": "Scenery & cars"}


def category(src):
    """Subfolder the owner dropped the clip in (e.g. '2 - Chases & crashes'), used to pick Short angles."""
    rel = src.relative_to(RAW).parts
    name = rel[0].lower() if len(rel) > 1 else ""
    return next((v for k, v in CATEGORIES.items() if k in name), "Unsorted")


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
        made.append({"file": str(out.relative_to(ROOT)), "from": src.name, "start": round(start, 1), "score": score,
                     "category": category(src)})
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
            print(f"  {h['file']}  [{h.get('category', 'Unsorted')}] (from {h['from']} at {h['start']}s, score {h['score']})")


if __name__ == "__main__":
    main()
