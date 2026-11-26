"""Owner APPROVE, Nov 26: numbered map series (studio/mapseries.py)."""
from studio.make_video import with_spot
from studio.mapseries import apply_number, cta, members, stale, with_line

EPS = {
    "crab": {"series": "Map Spots", "short": [{}]},
    "tiers": {"series": "Tier List", "short": [{}]},
    "atm": {"series": "Explained", "short": [{}], "shorts": [{"id": "tips", "series": "Map Spots", "segments": []}]},
    "ufo": {"series": "Map Spots", "short": [{}], "spot": 9},
    "gators": {"series": "Map Spots", "short": [{}], "spot": 4},
}
QUEUE = [
    {"slug": "ufo", "item": "short", "en": ["2026-11-29", "12:30 PM"]},
    {"slug": "crab", "item": "short", "en": ["2026-11-27", "12:30 PM"]},
    {"slug": "tiers", "item": "short", "en": ["2026-11-27", "9:30 AM"]},        # not in the series
    {"slug": "atm", "item": "tips", "en": ["2026-11-25", "3:45 PM"]},          # an extra Short that is
    {"slug": "atm", "item": "short", "en": ["2026-12-08", "9:30 AM"]},         # ...its main Short is not
    {"slug": "crab", "item": "short", "es_only": True, "es": ["2026-11-30", "1:30 PM"]},
    {"slug": "gators", "item": "short", "en": ["2026-11-30", "9:30 AM"]},
    {"slug": "gone", "item": "short", "en": ["2026-11-28", "9:30 AM"]},        # no episode file
]
UPLOADS = {"vidATM": {"slug": "atm", "item": "tips"}, "vidCRAB": {"slug": "crab", "item": "short"}}


def test_members_in_posting_order():
    ms = members(QUEUE, UPLOADS, EPS.__getitem__)
    assert [(m["slug"], m["n"]) for m in ms] == [("atm", 1), ("crab", 2), ("ufo", 3), ("gators", 4)]
    assert [m["slug"] for m in stale(ms)] == ["ufo"]  # uploaded ones never count; gators already says 4


def test_number_writes_badge_pill_and_lines():
    ep = {"short_description": "Where the crab is.\n\nSources: X", "short_es": {"description": "Dónde está."},
          "cta": "PART 2 TOMORROW: FOLLOW"}
    apply_number(ep, 7)
    assert ep["spot"] == 7 and ep["cta"] == "PART 2 TOMORROW: FOLLOW"  # a custom promise is kept
    assert ep["cta_es"] == cta(7, "es") == "LUGAR #8 PRONTO: SÍGUENOS" and len(cta(17)) <= 26
    assert ep["short_description"].startswith("Where the crab is.\n\n📍 Map Spot #7")
    assert ep["short_description"].endswith("Sources: X")
    apply_number(ep, 8)  # renumbered after a move: the line is replaced, not added twice
    assert ep["short_description"].count("📍") == 1 and "#8" in ep["short_description"]
    assert "📍 Lugar #8" in ep["short_es"]["description"]
    assert with_line("", "📍 Map Spot #1 x") == "\n\n📍 Map Spot #1 x"


def test_badge_goes_on_map_cards_only():
    seg = with_spot({"chart": {"type": "map", "n": 1}, "chart_es": {"type": "map", "n": 1}}, 5, pin=True)
    assert seg["chart"]["spot"] == 5 and seg["chart"]["n"] == 5 and seg["chart_es"]["spot_lang"] == "es"
    multi = with_spot({"chart": {"type": "map", "n": 2}}, 5, pin=False)
    assert multi["chart"]["n"] == 2
    assert "spot" not in with_spot({"chart": {"type": "tier"}}, 5)["chart"]
