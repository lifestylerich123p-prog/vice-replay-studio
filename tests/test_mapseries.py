"""Owner APPROVE, Nov 26: numbered map series (studio/mapseries.py)."""
from studio.make_video import with_spot
from studio.make_video import spot_for
from studio.mapseries import apply_number, clear_es, cta, desc_line, members, stale, with_line, without_line

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
    assert ep["short_description"].startswith("Where the crab is.\n\n📍 Map Spot #7")
    assert ep["short_description"].endswith("Sources: X")
    assert "spot_es" not in ep and "cta_es" not in ep and "📍" not in ep["short_es"]["description"]  # EN only
    apply_number(ep, 8)  # renumbered after a move: the line is replaced, not added twice
    assert ep["short_description"].count("📍") == 1 and "#8" in ep["short_description"]
    apply_number(ep, 31, "es")  # the Spanish channel's own number
    assert ep["spot_es"] == 31 and ep["cta_es"] == cta(31, "es") == "LUGAR #32 PRONTO: SÍGUENOS"
    assert "📍 Lugar #31" in ep["short_es"]["description"] and ep["spot"] == 8 and len(cta(17)) <= 26
    assert with_line("", "📍 Map Spot #1 x") == "\n\n📍 Map Spot #1 x"


def test_badge_goes_on_map_cards_only():
    seg = with_spot({"chart": {"type": "map", "n": 1}, "chart_es": {"type": "map", "n": 1}}, 5, pin=True)
    assert seg["chart"]["spot"] == 5 and seg["chart"]["n"] == 5 and seg["chart_es"]["spot_lang"] == "es"
    multi = with_spot({"chart": {"type": "map", "n": 2}}, 5, pin=False)
    assert multi["chart"]["n"] == 2
    assert "spot" not in with_spot({"chart": {"type": "tier"}}, 5)["chart"]


# ---- Phase 10 #4: English and Spanish keep independent series (channel separation + rescheduling) ----
ES_EPS = {
    "ninja": {"series": "Map Spots", "short": [{}], "spot": 25, "spot_es": 25},   # uploaded on ES with "LUGAR #25"
    "hotel": {"series": "Map Spots", "short": [{}], "spot": 26},                    # uploaded before spot_es existed
    "back": {"series": "Map Spots", "short": [{}], "spot": 6, "spot_es": 6},
    "tattoo": {"series": "Map Spots", "short": [{}], "spot": 7},
    "fox": {"series": "Map Spots", "short": [{}], "spot": 10},
    "tiers": {"series": "Tier List", "short": [{}]},
}
ES_QUEUE = [
    {"slug": "ninja", "item": "short", "en": ["2026-12-12", "8:00 AM"], "es": ["2026-11-27", "7:00 PM"]},
    {"slug": "hotel", "item": "short", "en": ["2026-12-12", "6:00 PM"], "es": ["2026-11-28", "12:30 PM"]},
    {"slug": "back", "item": "short", "en": ["2026-11-28", "8:00 AM"], "es": ["2026-11-28", "7:00 PM"]},
    {"slug": "tattoo", "item": "short", "en": ["2026-11-29", "6:00 PM"], "es": ["2026-12-01", "7:00 PM"]},
    {"slug": "fox", "item": "short", "en": ["2026-12-02", "8:00 AM"], "es": ["2026-12-11", "12:30 PM"]},
    {"slug": "tiers", "item": "short", "en": ["2026-11-30", "8:00 AM"], "es": ["2026-11-30", "12:30 PM"]},
]
ES_UP = {"E1": {"slug": "ninja", "item": "short"}, "E2": {"slug": "hotel", "item": "short"},
         "E3": {"slug": "back", "item": "short"}}


def test_spanish_series_is_independent_of_english_order():
    en = {m["slug"]: m["n"] for m in members(ES_QUEUE, {}, ES_EPS.__getitem__, "en")}
    es = {m["slug"]: m["n"] for m in members(ES_QUEUE, ES_UP, ES_EPS.__getitem__, "es")}
    assert en == {"back": 1, "tattoo": 2, "fox": 3, "ninja": 4, "hotel": 5}   # English posting order
    # uploaded Spanish videos keep the number they show; new ones continue after the highest (never reset to 1)
    assert es == {"ninja": 25, "hotel": 26, "back": 6, "tattoo": 27, "fox": 28}
    assert "tiers" not in es  # not in the series on either channel


def test_rescheduling_english_never_renumbers_spanish():
    moved = [dict(it, en=["2026-12-20", "8:00 AM"]) if it["slug"] == "tattoo" else it for it in ES_QUEUE]
    before = {m["slug"]: m["n"] for m in members(ES_QUEUE, ES_UP, ES_EPS.__getitem__, "es")}
    after = {m["slug"]: m["n"] for m in members(moved, ES_UP, ES_EPS.__getitem__, "es")}
    assert before == after
    en_after = {m["slug"]: m["n"] for m in members(moved, {}, ES_EPS.__getitem__, "en")}
    assert en_after["tattoo"] == 5  # English renumbers in its own order


def test_rescheduling_spanish_renumbers_only_booked_spanish_items():
    moved = [dict(it, es=["2026-11-26", "12:30 PM"]) if it["slug"] == "fox" else it for it in ES_QUEUE]
    es = {m["slug"]: m["n"] for m in members(moved, ES_UP, ES_EPS.__getitem__, "es")}
    # fox now posts before every uploaded one: it still continues after the highest number shown (never #1 again),
    # uploaded numbers stay as published, and only booked Spanish items are renumbered
    assert es["ninja"] == 25 and es["hotel"] == 26 and es["back"] == 6
    assert es["fox"] == 27 and es["tattoo"] == 28
    assert [m["slug"] for m in stale(members(moved, ES_UP, ES_EPS.__getitem__, "es"))] == ["fox", "tattoo"]


def test_spanish_lines_never_name_a_missing_playlist():
    assert desc_line(5, "es", playlist=None) == "📍 Lugar #5 de nuestra serie del mapa de GTA 6."
    assert "Where to Find It" not in desc_line(5, "es", playlist=None)
    assert "Where to Find It" in desc_line(5, "en", playlist="GTA 6 Map: Where to Find It")
    ep = {"short_es": {"description": "Hola.\n\n📍 Lugar #9 de nuestra serie del mapa de GTA 6: todos están en la "
                                      "lista \"GTA 6 Map: Where to Find It\".\n\nFuentes: X"},
          "cta_es": "LUGAR #10 PRONTO: SÍGUENOS", "spot_es": 9}
    clear_es(ep)  # an English-only series member: nothing Spanish borrowed from English
    assert "spot_es" not in ep and "cta_es" not in ep
    assert ep["short_es"]["description"] == "Hola.\n\nFuentes: X"
    assert without_line("A\n\n📍 Map Spot #3 x") == "A"


def test_spanish_render_uses_its_own_number_or_none():
    assert spot_for({"spot": 7, "spot_es": 29}, "en") == 7
    assert spot_for({"spot": 7, "spot_es": 29}, "es") == 29
    assert spot_for({"spot": 7}, "es") is None  # no Spanish number = no badge (never the English one)


def test_series_number_is_a_per_language_render_input():
    from studio import renderdeps
    ep = {"short": [{"text": "a", "text_es": "b"}], "spot": 7, "spot_es": 29}
    en, es = renderdeps.h(renderdeps.video_inputs(ep, "short", "en")), renderdeps.h(renderdeps.video_inputs(ep, "short", "es"))
    ep2 = dict(ep, spot=8)          # English renumbered: only the English render goes stale
    assert renderdeps.h(renderdeps.video_inputs(ep2, "short", "en")) != en
    assert renderdeps.h(renderdeps.video_inputs(ep2, "short", "es")) == es
    ep3 = dict(ep, spot_es=30)      # Spanish renumbered: only the Spanish render goes stale
    assert renderdeps.h(renderdeps.video_inputs(ep3, "short", "en")) == en
    assert renderdeps.h(renderdeps.video_inputs(ep3, "short", "es")) != es
