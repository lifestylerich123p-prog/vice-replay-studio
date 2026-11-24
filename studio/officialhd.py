"""4K versions of our official screenshots (owner, Nov 24, 2026: "make sure images are HD and readable").

media/official/ holds Rockstar's screenshots at 1920-2304 px (committed). A vertical Short crops a 9:16 slice out of a
16:9 picture, so those were blown up ~2.2x and looked soft. Rockstar's own download packs (rockstargames.com/VI/downloads,
the same pictures) are 3840 x 2160; this module keeps those in media/official-hd/ (gitignored, ~250 MB) and hands the
renderers the 4K file when it exists:

    from studio import officialhd
    officialhd.best("media/official/vice-city-01.jpg")   # -> media/official-hd/vice-city-01.jpg (fetched once)

media/official-hd.json maps each of our file names to its member in Rockstar's zip (matched by image fingerprint on
Nov 24: 174 of 174). A fresh machine downloads the three zips once (~220 MB) on first use; if that fails, the normal
files are used and nothing breaks.
"""
import fcntl
import json
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HD = ROOT / "media" / "official-hd"
MAP = ROOT / "media" / "official-hd.json"
BASE = "https://media-rockstargames-com.akamaized.net/VI/downloads/screenshots/"
_TRIED = {"done": False}


def mapping():
    try:
        return json.loads(MAP.read_text())
    except (OSError, ValueError):
        return {}


def ensure():
    """Fetch the 4K files once per machine. Returns how many HD files exist."""
    m = mapping()
    missing = {k: v for k, v in m.items() if not (HD / k).exists()}
    if not missing or _TRIED["done"]:
        return len(m) - len(missing)
    _TRIED["done"] = True
    HD.mkdir(parents=True, exist_ok=True)
    with open(HD / ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)  # several renders at once: only one downloads
        missing = {k: v for k, v in m.items() if not (HD / k).exists()}
        for zname in sorted({v[0] for v in missing.values()}):
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    zpath = Path(tmp) / f"{zname}.zip"
                    with urllib.request.urlopen(BASE + zname + ".zip", timeout=600) as r, open(zpath, "wb") as f:
                        shutil.copyfileobj(r, f)
                    with zipfile.ZipFile(zpath) as z:
                        for ours, (zn, member) in missing.items():
                            if zn == zname:
                                with z.open(member) as src, open(HD / ours, "wb") as dst:
                                    shutil.copyfileobj(src, dst)
            except Exception as e:  # noqa: BLE001 - fall back to the committed files
                print(f"4K screenshots unavailable ({zname}: {type(e).__name__}); using the normal ones")
    return sum(1 for k in m if (HD / k).exists())


def best(path):
    """The 4K file for media/official/<name>.jpg when we have (or can fetch) it, else the path itself."""
    p = Path(path)
    name = p.name
    if name not in mapping():
        return p
    if not (HD / name).exists():
        ensure()
    return HD / name if (HD / name).exists() else p
