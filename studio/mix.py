"""Content mix vs the owner's targets (Phase 3, Nov 26: "40% location guides, 25% secrets and Easter eggs, 15% gameplay
experiments and discoveries, 10% interactive map tutorials, 10% experimental content. Adjust these percentages based
on actual performance. Do not permanently eliminate a format based on one unsuccessful video").

    python -m studio.mix            # booked Shorts in the next 14 days per channel, share per category vs target

Targets live in config/channel.json `content_mix` (edit there when results say so). An episode can name its
category with "category"; otherwise it's inferred: media/site demo or map tutorial -> map_tutorial; owner gameplay or
"gameplay_experiment" -> gameplay; "experiment" -> experimental; a secret / easter egg / creature (claim_status set on a
sensitive topic) -> secrets; a map card or "where/location" -> location; anything else -> experimental.
"""
import datetime as dt
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT = {"location": 40, "secrets": 25, "gameplay": 15, "map_tutorial": 10, "experimental": 10}
SECRET = re.compile(r"easter egg|secret|secreto|hidden|bigfoot|skunk ape|ufo|ghost|portal|backrooms|silent hill|turtles|"
                    r"red dead|dexter|crab|panther|bear|fox|alligator", re.I)


def targets():
    try:
        t = json.loads((ROOT / "config" / "channel.json").read_text()).get("content_mix") or DEFAULT
        return {k: v for k, v in t.items() if not k.startswith("_")}
    except (OSError, ValueError):
        return DEFAULT


def category(ep):
    if ep.get("category"):
        return ep["category"]
    blob = json.dumps(ep.get("short") or [], ensure_ascii=False)
    if "media/site/" in blob or (ep.get("format") == "tutorial" and "interactive map" in (ep.get("short_title") or "").lower()):
        return "map_tutorial"
    if "media/gameplay" in blob or ep.get("gameplay_experiment"):
        return "gameplay"
    if ep.get("experiment"):
        return "experimental"
    text = " ".join([ep.get("slug", ""), ep.get("short_title") or ""])
    if SECRET.search(text):
        return "secrets"
    if '"type": "map"' in blob or re.search(r"where|location|d[oó]nde|dealership|shop|store", text, re.I):
        return "location"
    return "experimental"


def booked(days=14, now=None):
    now = now or dt.datetime.now()
    end = (now + dt.timedelta(days=days)).date().isoformat()
    q = json.loads((ROOT / "content" / "learn" / "approved_queue.json").read_text())["items"]
    out = {"en": Counter(), "es": Counter()}
    for it in q:
        for lang in ("en", "es"):
            slot = it.get(lang)
            if slot and now.date().isoformat() <= slot[0] <= end and it.get("item", "short") == "short":
                p = ROOT / "episodes" / f"{it['slug']}.json"
                if p.exists():
                    out[lang][category(json.loads(p.read_text()))] += 1
    return out


def main():
    t = targets()
    for lang, c in booked().items():
        n = sum(c.values()) or 1
        print(f"{'English' if lang == 'en' else 'Spanish'} channel, next 14 days ({sum(c.values())} Shorts):")
        for k, want in t.items():
            have = round(100 * c.get(k, 0) / n)
            flag = "" if abs(have - want) <= 10 else ("  <- under" if have < want else "  <- over")
            print(f"  {k:13} {have:3}% (target {want}%){flag}")
    print("gameplay needs the owner's recordings (media/gameplay); until then that share goes to location + secrets.")


if __name__ == "__main__":
    main()
