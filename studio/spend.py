"""Use the rest of the day's YouTube quota (owner, Nov 22 night: "every posting credit must be used posting or answering
comments").

    python -m studio.spend           # plan: units left today, which approved Shorts fit, how many comments wait
    python -m studio.spend upload    # MAIN CHAT: upload the approved Shorts that fit, earliest slot first (scheduled)

Order: (1) approved Shorts from content/learn/approved_queue.json that aren't up yet, uploaded early and scheduled
for their own slots (each upload is checked with `studio.vice publish` first; studio.ship's duplicate guard skips
anything already posted); (2) every unanswered comment on both channels (`studio.replies list` / `list --es`, the
standing auto-reply approval). Subtitle files on Shorts are off (config/channel.json `shorts_subtitles`), so a Short
costs ~1,750 units per channel. Facts are re-checked by the chat right before running `upload`.
"""
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

from . import quota

ROOT = Path(__file__).resolve().parent.parent
LEARN = ROOT / "content" / "learn"
QUEUE = LEARN / "approved_queue.json"
PER_CHANNEL = 1750  # videos.insert 1,600 + playlist 50 + thumbnail 50 + duplicate-guard reads
KEEP = 300          # left for comments posted after Shorts go live


def _registry(name):
    try:
        return {(r.get("slug"), r.get("item")) for r in json.loads((LEARN / name).read_text()).values()}
    except (OSError, ValueError):
        return set()


def pending():
    """Approved queue items with the channels still to upload: [(item, needs_en, needs_es)], earliest slot first."""
    q = json.loads(QUEUE.read_text())["items"]
    en, es = _registry("uploads.json"), _registry("uploads-es.json")
    out = []
    for it in q:
        key = (it["slug"], it.get("item", "short"))
        need_en = bool(it.get("en")) and not it.get("es_only") and key not in en
        need_es = bool(it.get("es")) and key not in es
        if need_en or need_es:
            out.append((it, need_en, need_es))
    first = lambda it: min(dt.datetime.strptime(f"{d} {t}", "%Y-%m-%d %I:%M %p") for d, t in
                           [x for x in (it.get("en"), it.get("es")) if x])
    return sorted(out, key=lambda x: first(x[0]))


def plan():
    left = quota.left_today()
    print(f"YouTube units left today: ~{left:,} (resets in {quota.reset_in()})")
    budget = left - KEEP
    fits = []
    for it, ne, ns in pending():
        cost = PER_CHANNEL * (ne + ns)
        if cost <= budget:
            fits.append((it, ne, ns))
            budget -= cost
    rest = [x for x in pending() if x not in fits]
    for it, ne, ns in fits:
        print(f"- FITS: {it['slug']} ({'EN ' + ' '.join(it['en']) if ne else ''}{' + ' if ne and ns else ''}"
              f"{'ES ' + ' '.join(it['es']) if ns else ''})")
    for it, ne, ns in rest:
        print(f"- waits: {it['slug']}")
    print(f"After uploads: ~{max(0, budget):,} units for comment replies (50 each): run python -m studio.replies list "
          f"and list --es, answer every real comment, then post.")
    return fits


def commands(it, ne, ns):
    ep = f"episodes/{it['slug']}.json"
    key = it.get("item", "short")
    if ne and ns and it["en"] == it["es"]:
        return [["python", "-m", "studio.ship", ep, "--upload", key, "--date", it["en"][0], "--at", it["en"][1]]]
    cmds = []
    if ne:
        cmds.append(["python", "-m", "studio.ship", ep, "--upload", key, "--date", it["en"][0], "--at", it["en"][1],
                     "--no-es-upload"])
    if ns:
        cmds.append(["python", "-m", "studio.youtube_es", ep, "--approve", key, "--date", it["es"][0], "--at", it["es"][1]])
    return cmds


def renders_needed(it, ne, ns):
    """Short videos the upload needs that aren't on disk (output/ isn't committed; a fresh container has none).
    Everything to rebuild them is committed: the episode, its cards and any voice files in media/voice/."""
    slug, key = it["slug"], it.get("item", "short")
    out = ROOT / "output" / slug
    if key == "main":  # the weekly hub video (Nov 23)
        return [] if (out / f"{slug}.mp4").exists() else [["python", "-m", "studio.make_video", f"episodes/{slug}.json"]]
    if key != "short":
        return []
    need = []
    if ne and not (out / f"{slug}-short.mp4").exists():
        need.append(["python", "-m", "studio.make_video", f"episodes/{slug}.json", "--short"])
    if ns and not (out / f"{slug}-short-es.mp4").exists():
        need.append(["python", "-m", "studio.make_video", f"episodes/{slug}.json", "--short", "--es"])
    return need


def upload():
    for it, ne, ns in plan():
        for cmd in renders_needed(it, ne, ns):
            print("$", " ".join(cmd), "(video missing: rendering it first)")
            subprocess.run(cmd, cwd=ROOT)
        gate = subprocess.run(["python", "-m", "studio.vice", "publish", f"episodes/{it['slug']}.json"],
                              cwd=ROOT, capture_output=True, text=True)
        out = gate.stdout + gate.stderr
        i = out.find('"blockers"')
        blockers = out[i:out.find("]", i)] if i >= 0 else ""
        if blockers.strip() not in ('"blockers": [', ""):
            print(f"! skip {it['slug']}: publish check has blockers: {blockers[13:300]}")
            continue
        for cmd in commands(it, ne, ns):
            print("$", " ".join(cmd))
            r = subprocess.run(cmd, cwd=ROOT)
            if r.returncode:
                print(f"! {it['slug']}: upload step failed (exit {r.returncode}); stopping")
                return
    print("Done. Schedule each printed COMMENTS TO POST for 10 min after its slot, commit uploads*.json, quota.json.")


if __name__ == "__main__":
    upload() if sys.argv[1:2] == ["upload"] else plan()
