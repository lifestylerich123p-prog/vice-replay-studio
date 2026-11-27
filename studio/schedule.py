"""Flexible slots (owner Nov 26, Phase 4 #3/#11: "Reserve a flexible scheduling slot for timely, high-potential content.
Allow the scheduling engine to move weaker, unproduced concepts when a verified opportunity appears... Do not interfere
with videos that are already publicly scheduled without a documented reason").

    python -m studio.schedule place <slug> --lang en|es [--within 14] [--priority timely|followup|evergreen|experiment]

Puts an item into the earliest plan slot (EN 8:00 AM / 6:00 PM, ES 12:30 PM / 7:00 PM; config auto_publish*.slots)
that is free, or held by a WEAKER item that can still move: not uploaded (registry), not past the gate into
UPLOADING / SCHEDULED / PUBLISHED, no "pinned": true, not a numbered map-series Short and not already rendered
(owner Phase 4: only unproduced concepts move; Phase 10: never displace approved videos unnecessarily), and weaker = lower priority class or (same class) a category
that's over its content_mix target while the new one is under. The moved item goes to the first free plan slot after
the window, with "moved_by" + reason on it. Never touches an uploaded or scheduled video.
"""
import argparse
import datetime as dt
import json
from pathlib import Path

from . import approvals, mix

ROOT = Path(__file__).resolve().parent.parent
QUEUE = ROOT / "content" / "learn" / "approved_queue.json"
PRIORITY = {"timely": 1, "followup": 2, "evergreen": 3, "experiment": 4, "scheduled": 5}


def _registry(lang):
    try:
        reg = json.loads((ROOT / "content" / "learn" / ("uploads-es.json" if lang == "es" else "uploads.json")).read_text())
    except (OSError, ValueError):
        return set()
    return {(r.get("slug"), r.get("item", "short")) for r in reg.values()}


def _series_member(it):
    """A numbered map Short (studio/mapseries.py): moving it would renumber every later spot."""
    try:
        ep = json.loads((ROOT / "episodes" / f"{it['slug']}.json").read_text())
    except (OSError, ValueError):
        return False
    return ep.get("series") == "Map Spots" or ep.get("spot") is not None or ep.get("spot_es") is not None


def _rendered(it, lang):
    """The item's video for this language is already produced (owner Phase 4: only UNPRODUCED concepts may move)."""
    slug = it["slug"]
    return (ROOT / "output" / slug / f"{slug}-short{'-es' if lang == 'es' else ''}.mp4").exists()


def movable(it, lang, uploaded, store):
    if it.get("pinned") or (it["slug"], it.get("item", "short")) in uploaded:
        return False
    rec = store.get(approvals.key_of(it["slug"], it.get("item", "short"), "youtube-es" if lang == "es" else "youtube-en"))
    # anything that already passed the gate keeps its slot (its approval is bound to it)
    if rec and rec.get("state") in ("AUTO_APPROVED", "UPLOADING", "SCHEDULED", "PUBLISHED"):
        return False
    # Phase 10 (Nov 27: it moved the numbered, rendered tattoo Short #7 to Dec 15): never displace a numbered map Short
    # or a finished video; only weaker, unproduced concepts make way, otherwise the new item takes a free slot
    return not _series_member(it) and not _rendered(it, lang)


def category_of(slug):
    p = ROOT / "episodes" / f"{slug}.json"
    return mix.category(json.loads(p.read_text())) if p.exists() else "experimental"


def place(slug, lang="en", priority="evergreen", within=14, now=None, queue=None, uploaded=None, store=None,
          shares=None, targets=None, write=True):
    now = now or dt.datetime.now(approvals.ET)
    q = queue if queue is not None else json.loads(QUEUE.read_text())
    uploaded = uploaded if uploaded is not None else _registry(lang)
    store = store if store is not None else approvals._load()
    slots = approvals.auto_cfg("youtube-es" if lang == "es" else "youtube-en")["slots"]
    targets = targets or mix.targets()
    if shares is None:
        c = mix.booked(within, now.replace(tzinfo=None))[lang]
        n = sum(c.values()) or 1
        shares = {k: 100 * c.get(k, 0) / n for k in targets}
    item = next((i for i in q["items"] if i["slug"] == slug and i.get("item", "short") == "short"), None)
    if item is None:
        item = {"slug": slug, "item": "short"}
        q["items"].append(item)
    mine_cat, mine_pri = category_of(slug), PRIORITY[priority]
    held = {tuple(i[lang]): i for i in q["items"] if i.get(lang) and i is not item}
    moved = None
    day0 = now.date()
    for d in range(1, within + 1):
        day = (day0 + dt.timedelta(days=d)).isoformat()
        for t in slots:
            other = held.get((day, t))
            if other is None:
                item[lang] = [day, t]
                return _done(q, item, None, write)
            if not movable(other, lang, uploaded, store):
                continue
            o_cat, o_pri = category_of(other["slug"]), PRIORITY.get(other.get("priority", "evergreen"), 3)
            over = shares.get(o_cat, 0) > targets.get(o_cat, 0)
            under = shares.get(mine_cat, 0) < targets.get(mine_cat, 0)
            # weaker: an experiment/low item below us, or a same-or-lower class item whose category is over target
            # while ours is under (booked verified items default to "evergreen")
            weaker = (o_pri >= 4 and o_pri > mine_pri) or (o_pri >= mine_pri and over and (under or o_pri > mine_pri))
            if weaker:
                item[lang] = [day, t]
                moved = other
                # the moved item takes the first free plan slot after the window
                taken = {tuple(i[lang]) for i in q["items"] if i.get(lang)}
                for k in range(within + 1, within + 60):
                    nd = (day0 + dt.timedelta(days=k)).isoformat()
                    free = [s for s in slots if (nd, s) not in taken]
                    if free:
                        other[lang] = [nd, free[0]]
                        other["moved_by"] = (f"{dt.date.today()}: studio.schedule gave {day} {t} to {slug} "
                                             f"({priority}, {mine_cat}); this one is {o_cat}"
                                             f"{' (over target)' if shares.get(o_cat, 0) > targets.get(o_cat, 0) else ''}"
                                             f" and wasn't uploaded yet")
                        break
                return _done(q, item, moved, write)
    raise ValueError(f"no free or movable {lang} slot in the next {within} days")


def _done(q, item, moved, write):
    if write:
        raw = QUEUE.read_text()
        QUEUE.write_text(json.dumps(q, ensure_ascii=False, indent=1 if raw.startswith('{\n "') else 2) + "\n")
    return {"placed": item, "moved": moved}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m studio.schedule")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("place")
    p.add_argument("slug")
    p.add_argument("--lang", choices=("en", "es"), default="en")
    p.add_argument("--priority", choices=list(PRIORITY), default="evergreen")
    p.add_argument("--within", type=int, default=14)
    a = ap.parse_args(argv)
    r = place(a.slug, a.lang, a.priority, a.within)
    print(f"{a.slug} -> {a.lang} {r['placed'][a.lang]}")
    if r["moved"]:
        print(f"moved {r['moved']['slug']} -> {r['moved'][a.lang]} ({r['moved']['moved_by']})")


if __name__ == "__main__":
    main()
