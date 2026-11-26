"""Owner Nov 26 Phase 3 #4: follow-ups only for real winners (3x+ a matched baseline), never duplicates, verified facts
only, right audience, within budget (studio/opportunities.py)."""
import datetime as dt

from studio import opportunities as op

FAM = {"shopping": {"keywords": ["shoe", "store", "barber", "clothing"]}, "money": {"keywords": ["money", "treasure"]}}
CANDS = [
    {"key": "barber-shops", "family": "shopping", "keywords": ["barber"], "status": "verified",
     "sources": ["a https://game8.co/x", "b https://www.gtabase.com/y"], "langs": ["en", "es"], "credits": 0},
    {"key": "clothing-stores", "family": "shopping", "keywords": ["clothing store"], "status": "idea", "sources": []},
    {"key": "mask-shop", "family": "shopping", "keywords": ["mask"], "status": "verified",
     "sources": ["a https://game8.co/x", "b https://www.gtabase.com/y"]},
    {"key": "rare-outfits", "family": "shopping", "keywords": ["rare outfit"], "status": "verified",
     "sources": ["a https://game8.co/x", "b https://game8.co/z"]},          # one site twice: not verified
    {"key": "paid-thing", "family": "shopping", "keywords": ["paid"], "status": "verified", "credits": 5,
     "sources": ["a https://game8.co/x", "b https://www.gtabase.com/y"]},
]
INDEX = [("gta6-mask-where", "gta6 mask where gta 6 mask location", "the mask shop is here"),
         ("gta6-shoe-store-where", "gta6 shoe store where gta 6 shoe store", "the barber is next door")]
WIN = {"sufficient": True, "baseline": 50, "ratio": 13.6, "family": "shopping"}


def test_rule_needs_a_real_winner():
    assert op.evaluate_follow_up({**WIN, "ratio": 2.9}, CANDS, INDEX) == ([], [])
    assert op.evaluate_follow_up({**WIN, "sufficient": False}, CANDS, INDEX) == ([], [])
    assert op.evaluate_follow_up({**WIN, "baseline": 0}, CANDS, INDEX) == ([], [])


def test_rule_filters_duplicates_unverified_and_budget():
    ready, research = op.evaluate_follow_up(WIN, CANDS, INDEX)
    assert [c["key"] for c in ready] == ["barber-shops"]               # verified, new, free
    assert {c["key"] for c in research} == {"clothing-stores", "rare-outfits"}  # needs research (or a 2nd site)
    # mask-shop: already made (title names it); paid-thing: over the 0-credit budget
    assert "barber-shops" not in [c["key"] for c in op.evaluate_follow_up({**WIN, "family": "money"}, CANDS, INDEX)[0]]


def test_script_mention_is_related_not_duplicate():
    c = CANDS[0]
    assert op.already_produced(c, INDEX) is None and op.related(c, INDEX) == ["gta6-shoe-store-where"]


def test_family_and_matched_age_baseline():
    assert op.family_of("GTA 6 shoe store: where to buy shoes", FAM) == "shopping"
    now = dt.datetime(2026, 11, 27, 12, 0, tzinfo=dt.timezone.utc)
    vids, hist_rows = [], []
    for i in range(5):  # peers posted 2-6 days ago, ~50 views at 24 h
        pub = now - dt.timedelta(days=2 + i)
        vids.append({"id": f"p{i}", "title": f"GTA 6 fact {i}", "published": pub.isoformat(), "type": "Short", "views": 80})
        hist_rows += [(pub + dt.timedelta(hours=23), {f"p{i}": 48}), (pub + dt.timedelta(hours=25), {f"p{i}": 52})]
    hot = now - dt.timedelta(hours=10)
    vids.append({"id": "hot", "title": "GTA 6 shoe store location", "published": hot.isoformat(), "type": "Short",
                 "views": 600})
    hist = sorted(hist_rows, key=lambda x: x[0])
    # peers at 10 h: interpolate from the closest snapshots -> give them explicit 10 h points
    hist += [(dt.datetime.fromisoformat(v["published"]) + dt.timedelta(hours=10), {v["id"]: 30}) for v in vids[:5]]
    hist.sort(key=lambda x: x[0])
    rows = op.youtube_winners(snap={"videos": vids}, hist=hist, ups={}, now=now)
    hot_row = next(r for r in rows if r["id"] == "hot")
    assert hot_row["sufficient"] and hot_row["baseline"] == 30 and hot_row["ratio"] == 20.0
