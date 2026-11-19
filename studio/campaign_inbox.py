"""Campaign clip inbox (free): the owner drops stream recordings into a Google Drive folder, this cuts the clips.

    python -m studio.campaign_inbox            # download new recordings and cut 2 clips from each
    python -m studio.campaign_inbox --top 3    # more clips per recording

Drive folder (content/owner.md, "Campaign clips folder"), shared once as "Anyone with the link can view", with one
subfolder per campaign: "Lacy" -> content/campaigns/lacy-gta6.json, "KreekCraft" -> kreekcraft-gta6.json (add more in
SUBFOLDERS). Owner's only job: screen-record the moment (phone sideways, 1-5 min), Share -> Drive -> the right
subfolder. Recordings go to output/campaign_footage/ (never media/, so streamer footage can't reach our videos);
clips land in output/clips/<campaign>/ with clips.md. Each recording is cut once (output/campaign_footage/done.json).
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "output" / "campaign_footage"
DONE = DEST / "done.json"
SUBFOLDERS = {"lacy": "lacy-gta6", "kreekcraft": "kreekcraft-gta6"}
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".mkv", ".webm"}


def folder_link():
    m = re.search(r"Campaign clips folder: (https://drive\.google\.com/\S+)", (ROOT / "content" / "owner.md").read_text())
    return m.group(1).rstrip(").,") if m else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--top", type=int, default=2)
    a = ap.parse_args()
    link = folder_link()
    if not link:
        sys.exit("No 'Campaign clips folder:' link in content/owner.md.")
    import gdown
    DEST.mkdir(parents=True, exist_ok=True)
    try:
        gdown.download_folder(url=link, output=str(DEST), quiet=True, resume=True, retries=2)
    except Exception as e:  # noqa: BLE001 - gdown raises several types; the message is what matters
        sys.exit(f"Couldn't read the Drive folder ({type(e).__name__}). Is it shared 'Anyone with the link can view'?")
    done = set(json.loads(DONE.read_text())) if DONE.exists() else set()
    new = [p for p in sorted(DEST.rglob("*")) if p.suffix.lower() in VIDEO_EXT and str(p.relative_to(DEST)) not in done]
    if not new:
        print("No new recordings in the campaign clips folder.")
        return
    for p in new:
        camp = next((c for k, c in SUBFOLDERS.items() if k in str(p.relative_to(DEST)).lower()), None)
        if not camp:
            print(f"skip {p.name}: put it in a campaign subfolder ({', '.join(SUBFOLDERS)})")
            continue
        print(f"== {p.relative_to(DEST)} -> {camp}")
        r = subprocess.run([sys.executable, "-m", "studio.clip", str(p), "--campaign", camp, "--top", str(a.top)], cwd=ROOT)
        if r.returncode == 0:
            done.add(str(p.relative_to(DEST)))
            DONE.write_text(json.dumps(sorted(done), indent=1))


if __name__ == "__main__":
    main()
