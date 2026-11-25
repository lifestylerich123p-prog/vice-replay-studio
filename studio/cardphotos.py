"""Real GTA 6 pictures behind our lettering cards (owner, Nov 24, 2026: "if you think what I said doesn't work, change
it and upgrade it"; approved Nov 24: "Approve everything for good of the channel").

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
    "world": ["grassrivers-02", "grassrivers-03", "grassrivers-04", "grassrivers-05",
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


# Exact names first (owner, Nov 24: "when using images look for those exact images"): a title or line that names a
# car, place or character gets THAT screenshot. Only Rockstar's official pack is used (rockstargames.com/VI/downloads,
# last updated Nov 4, 2026 and fully in media/official); never other people's images.
EXACT = [
    (r"\bcheetah\b|\bgrotti\b", "car-grotti-cheetah"), (r"\bsqualo\b", "car-squalo"),
    (r"\bstanier\b", "car-vapid-stanier"), (r"\bganado\b", "car-vapid-ganado"), (r"\bbuggy\b", "car-vapid-buggy"),
    (r"one[- ]eyed willie|\bcanis\b", "car-canis-one-eyed-willie"), (r"electric fang|tattoo", "car-electric-fang"),
    (r"\brideout\b", "rideout-customs"), (r"\bwyman\b", "wyman-car-collection"), (r"sara'?s salon", "saras-salon"),
    (r"stock 305", "stock-305"), (r"port gellhorn", "port-gellhorn"), (r"grassrivers|everglades|swamp", "grassrivers"),
    (r"mount kalaga", "mount-kalaga"), (r"\bambrosia\b", "ambrosia"), (r"leonida keys|\bthe keys\b", "leonida-keys"),
    (r"\bmap\b|\bmapa\b", "leonida-map-poster"), (r"\bjason\b", "jason-duval"), (r"\blucia\b", "lucia-caminos"),
    (r"cal hampton", "cal-hampton"), (r"brian heder", "brian-heder"), (r"\braul\b", "raul-bautista"),
    (r"real dimez", "real-dimez"), (r"\bboobie\b", "boobie-ike"), (r"dre'?quan", "drequan-priest"),
    (r"vice city", "vice-city"),
]
SAFE = {n for names in POOL.values() for n in names}  # viewed Nov 24: OK as a video background


def exact(text, video=False):
    """Official screenshots that show exactly what the text names, most specific first. video=True keeps only the
    vetted SAFE set (videos need first-second ad safety; thumbnails, site cards and carousels can use any file in
    media/official, which only holds owner-approved shots)."""
    t = (text or "").lower()
    out = []
    for rx, prefix in EXACT:
        if re.search(rx, t):
            files = sorted(f.stem for f in OFFICIAL.glob(f"{prefix}*.jpg"))
            out += [f for f in files if (f in SAFE or not video) and f not in out]
    return out


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


_USED = set()
HOOK_MIN = 85  # mean luminance 0-255 of the picture; Grassrivers/Port Gellhorn night shots are 33-41
_LUMA = {}


def brightness(name):
    if name not in _LUMA:
        try:
            from PIL import Image, ImageStat
            im = Image.open(OFFICIAL / f"{name}.jpg").convert("L").resize((160, 90))
            _LUMA[name] = ImageStat.Stat(im).mean[0]
        except OSError:
            _LUMA[name] = 0
    return _LUMA[name]


def reset():
    """Start a new video: pictures may repeat across videos, not within one."""
    _USED.clear()


def used():
    """The pictures this video has taken so far (a copy)."""
    return set(_USED)


def mark_used(paths):
    """A resumed card (studio/make_video.py) took these pictures in the earlier run: keep them out of later cards."""
    _USED.update(paths)


def pick(text, index, used=()):
    """A safe official screenshot for one card: topic-matched (cars / water / world / city), varied by the card's
    text and position, never repeating one already used in the same video when another is free."""
    t = (text or "").lower()
    used = set(used) | _USED
    hits = [n for n in exact(t, video=True) if f"media/official/{n}.jpg" not in used]
    if hits:  # the exact car / place the line names
        choice = f"media/official/{hits[index % len(hits)]}.jpg"
        _USED.add(choice)
        return choice
    group = next((g for g, rx in TOPICS if re.search(rx, t)), "city")
    names = [n for n in (HOOK if index == 0 and group == "city" else POOL[group]) if _exists(n)] or \
            [n for g in POOL.values() for n in g if _exists(n)]
    if index == 0:  # Nov 24 hook v2: the opening frame needs a bright, readable picture (night shots read as black)
        names = [n for n in names if brightness(n) >= HOOK_MIN] or [n for n in HOOK if _exists(n)] or names
    if not names:
        return None
    h = int(hashlib.md5(f"{t}|{index}".encode()).hexdigest(), 16)
    order = names[h % len(names):] + names[:h % len(names)]
    choice = next((n for n in order if f"media/official/{n}.jpg" not in used), order[0])
    _USED.add(f"media/official/{choice}.jpg")
    return f"media/official/{choice}.jpg"
