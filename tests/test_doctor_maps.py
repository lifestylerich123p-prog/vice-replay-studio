"""Owner, Nov 25: "Start posting the maps videos at least one a day" -> studio.doctor warns about days without one."""
import datetime as dt

from studio.doctor import map_gaps

MAP = {"short": [{"chart": {"type": "kinetic"}}, {"chart": {"type": "map", "pins": ["G7"]}}]}
TIER = {"short": [{"chart": {"type": "tier"}}]}
EXTRA = {"short": [{"chart": {"type": "tier"}}], "shorts": [{"id": "tips", "segments": [{"chart": {"type": "map"}}]}]}
EPS = {"crab": MAP, "tiers": TIER, "atm": EXTRA, "guide": {"segments": [{"chart": {"type": "map"}}]}}


def test_days_without_a_map_short_are_reported():
    items = [
        {"slug": "crab", "item": "short", "en": ["2026-11-26", "8:00 AM"]},
        {"slug": "tiers", "item": "short", "en": ["2026-11-27", "9:30 AM"]},
        {"slug": "guide", "item": "main", "en": ["2026-11-27", "3:30 PM"]},       # long video: not a Short
        {"slug": "atm", "item": "tips", "en": ["2026-11-28", "11:00 AM"]},        # extra Short with a map card
        {"slug": "crab", "item": "short", "es_only": True, "es": ["2026-11-29", "1:30 PM"]},
        {"slug": "missing", "item": "short", "en": ["2026-11-29", "9:30 AM"]},    # no episode file
    ]
    gaps = map_gaps(items, EPS.__getitem__, dt.date(2026, 11, 26), days=4)
    assert gaps == ["2026-11-27", "2026-11-29"]
