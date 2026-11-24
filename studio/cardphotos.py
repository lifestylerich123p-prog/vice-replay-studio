"""Real GTA 6 pictures behind our lettering cards (owner, Nov 24, 2026: "if you think what I said doesn't work, change
it and upgrade it").

Why: since the Nov 23 switch to text-only cards on the synthwave set, Shorts get swiped past (median 431 views at 24 h
for the old screenshot Shorts vs ~20-80 for cards, one tier-list hit aside). The owner wanted lettering and a modern
style, not trailer imaging; this keeps the lettering and puts an official Rockstar screenshot (allowed by CLAUDE.md
and Rockstar's fan policy for commentary) behind it: slow zoom, darkened so the words stay readable. Trailer CLIPS
stay out. The pool below was viewed one by one on Nov 24: places and cars only, nothing with a gun, a revealing pose,
swimwear, drinking or a character close-up (first-7-seconds ad safety + the owner's no-sexualized-images rule).

    from studio import cardphotos
    cardphotos.pick("GTA 6's best rides, ranked", 0)   # -> "media/official/car-grotti-cheetah-01.jpg"

Turn off per episode with "card_photos": false, per card with an explicit "bg"; everywhere with
config/channel.json "card_photos": {"on": false}.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OFFICIAL = ROOT / "media" / "official"

POOL = {
    "cars": ["car-grotti-cheetah-01", "car-grotti-cheetah-02", "car-grotti-cheetah-03", "car-grotti-cheetah-04",
             "car-canis-one-eyed-willie-01", "car-canis-one-eyed-willie-02", "car-canis-one-eyed-willie-03",
             "car-vapid-buggy-01", "car-vapid-buggy-02", "car-vapid-buggy-03", "car-vapid-buggy-04",
             "car-vapid-ganado-01", "car-vapid-stanier-01", "rideout-customs-01", "rideout-customs-02",
             "rideout-customs-03", "safehouse-vehicles-01", "safehouse-vehicles-02", "wyman-car-collection-02",
             "wyman-car-collection-03", "wyman-car-collection-04", "wyman-car-collection-05", "wyman-car-collection-06",
             "vintage-vice-city-pack-vapid-stanier-01", "vintage-vice-city-pack-vapid-stanier-03",
             "vintage-vice-city-pack-vapid-stanier-04"],
    "water": ["car-squalo-01", "car-squalo-02", "car-squalo-03", "leonida-keys-01", "leonida-keys-04",
              "leonida-keys-06", "leonida-keys-07", "vice-city-15"],
    "world": ["leonida-map-poster", "grassrivers-02", "grassrivers-03", "grassrivers-04", "grassrivers-05",
              "mount-kalaga-01", "mount-kalaga-02", "mount-kalaga-04", "mount-kalaga-05", "mount-kalaga-06",
              "ambrosia-01", "ambrosia-02", "ambrosia-04", "port-gellhorn-01", "port-gellhorn-06", "leonida-keys-02"],
    "city": ["vice-city-01", "vice-city-03", "vice-city-08", "vice-city-10", "vice-city-11", "vice-city-17",
             "vice-city-22", "vice-city-26", "vice-city-27", "stock-305-03"],
}
TOPICS = [  # first match wins
    ("cars", r"\b(car|cars|ride|rides|drive|driv\w+|vehicle|garage|impound|key cloner|steal|stolen|race|races|"
             r"supercar|truck|bike|motor\w*|fastest|speed)\b"),
    ("water", r"\b(boat|boats|yacht|ocean|sea|island|keys|beach|dive|diving|fish\w*|water|squalo)\b"),
    ("world", r"\b(map|leonida|world|size|bigger|places?|swamp|nature|animal\w*|gator|alligator|wildlife|"
              r"mount|kalaga|ambrosia|grassrivers|port gellhorn|easter egg\w*|secret\w*|hidden)\b"),
]
HOOK = ["vice-city-27", "car-grotti-cheetah-01", "vice-city-01", "vice-city-10", "vice-city-22",
        "car-vapid-stanier-01", "leonida-keys-01", "vice-city-08"]


def enabled(ep=None):
    if ep is not None and ep.get("card_photos") is False:
        return False
    try:
        cfg = json.loads((ROOT / "config" / "channel.json").read_text()).get("card_photos", {"on": True})
    except (OSError, ValueError):
        cfg = {"on": True}
    return bool(cfg.get("on", True)) if isinstance(cfg, dict) else bool(cfg)


def _exists(name):
    return (OFFICIAL / f"{name}.jpg").exists()


def pick(text, index, used=()):
    """A safe official screenshot for one card: topic-matched (cars / water / world / city), varied by the card's
    text and position, never repeating one already used in the same video when another is free."""
    t = (text or "").lower()
    group = next((g for g, rx in TOPICS if re.search(rx, t)), "city")
    names = [n for n in (HOOK if index == 0 and group == "city" else POOL[group]) if _exists(n)] or \
            [n for g in POOL.values() for n in g if _exists(n)]
    if not names:
        return None
    h = int(hashlib.md5(f"{t}|{index}".encode()).hexdigest(), 16)
    order = names[h % len(names):] + names[:h % len(names)]
    choice = next((n for n in order if f"media/official/{n}.jpg" not in used), order[0])
    return f"media/official/{choice}.jpg"
