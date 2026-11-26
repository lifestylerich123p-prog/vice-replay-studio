"""Footage provenance manifest (owner Nov 26, Phase 4 #5: "Maintain a footage provenance manifest that records:
original source, creator, license or permission, usage restrictions, attribution requirements, associated episodes").

    python -m studio.provenance            # writes rights/provenance.json + prints a summary (unlicensed files first)
    python -m studio.provenance --check    # exit 1 if an episode uses a file with no rights record or a blocked one

One record per media file, from rights/registry.json (the same records the publish gate's rights check uses) plus the
episodes that reference the file. Card photos chosen automatically by studio/cardphotos.py come from the vetted
media/official pool and are covered by its class record. AI images are never shown as gameplay
(studio/vice/factcheck.py requires a visible label).
"""
import argparse
import fnmatch
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "rights" / "registry.json"
OUT = ROOT / "rights" / "provenance.json"
MEDIA_DIRS = ("media", "assets/music", "assets/ai-backgrounds", "assets/intro", "assets/brand")
EXTS = {".mp4", ".mov", ".webm", ".jpg", ".jpeg", ".png", ".webp", ".wav", ".mp3", ".m4a"}
SKIP = ("media/official-hd/",)  # full-size copies of media/official (same record)


def record_for(rel, registry):
    for r in registry:
        if any(fnmatch.fnmatch(rel, m) for m in r.get("match", []) if not m.startswith(("http", "campaign:", "voice:",
                                                                                       "music:", "vice:"))):
            return r
    return None


def episode_refs():
    refs = defaultdict(set)
    for p in sorted((ROOT / "episodes").glob("*.json")):
        text = p.read_text()
        for m in re.finditer(r'"(?:photo:)?(?:\.\./)?((?:media|assets)/[^"]+\.\w{2,4})"', text):
            refs[m.group(1)].add(p.stem)
    return refs


def build():
    registry = json.loads(REGISTRY.read_text())
    refs = episode_refs()
    files = []
    for d in MEDIA_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for f in sorted(base.rglob("*")):
            rel = f.relative_to(ROOT).as_posix()
            if f.is_file() and f.suffix.lower() in EXTS and not rel.startswith(SKIP):
                files.append(rel)
    for rel in refs:  # referenced but missing on disk (e.g. owner gameplay not pulled here)
        if rel not in files:
            files.append(rel)
    out, unlicensed, blocked_use = [], [], []
    for rel in sorted(files):
        r = record_for(rel, registry)
        row = {"file": rel, "exists": (ROOT / rel).exists(), "episodes": sorted(refs.get(rel, ())),
               "rights_id": r["id"] if r else None,
               "source": (r or {}).get("asset_class"), "creator": (r or {}).get("owner"),
               "license": (r or {}).get("permission"), "license_url": (r or {}).get("license_url"),
               "restrictions": (r or {}).get("creator_restrictions"), "attribution": (r or {}).get("attribution"),
               "status": (r or {}).get("status", "UNREGISTERED")}
        out.append(row)
        if not r:
            unlicensed.append(rel)
        elif r.get("status") == "blocked" and row["episodes"]:
            blocked_use.append(rel)
    res = {"note": "Built by python -m studio.provenance from rights/registry.json + episodes/*.json. Never repost "
                   "another creator's gameplay without written permission recorded in rights/registry.json.",
           "files": out, "unregistered": unlicensed, "blocked_in_use": blocked_use,
           "counts": {k: sum(1 for x in out if x["rights_id"] == k) for k in sorted({x["rights_id"] or "-" for x in out})}}
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m studio.provenance")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    res = build()
    print(f"{len(res['files'])} media files -> {OUT.relative_to(ROOT)}")
    for k, v in res["counts"].items():
        print(f"  {k}: {v}")
    for f in res["unregistered"][:20]:
        print(f"  UNREGISTERED: {f}")
    for f in res["blocked_in_use"]:
        print(f"  BLOCKED SOURCE USED BY AN EPISODE: {f}")
    if a.check and (res["blocked_in_use"] or [f for f in res["unregistered"] if any(
            f == x["file"] and x["episodes"] for x in res["files"])]):
        sys.exit(1)


if __name__ == "__main__":
    main()
