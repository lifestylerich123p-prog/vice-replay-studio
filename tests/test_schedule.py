"""Phase 4 #3/#11: a verified high-priority item takes a weaker unproduced item's slot; uploaded, scheduled and
gate-approved items never move (studio/schedule.py)."""
import datetime as dt

from studio import schedule

NOW = dt.datetime(2026, 11, 26, 15, 0)
T = {"location": 45, "secrets": 25, "gameplay": 0, "map_tutorial": 20, "experimental": 10}
SH = {"location": 43, "secrets": 40, "gameplay": 0, "map_tutorial": 3, "experimental": 14}


def q(*items):
    return {"items": [dict(i) for i in items]}


def run(qq, slug, cats, **kw):
    schedule.category_of = lambda s: cats.get(s, "location")
    return schedule.place(slug, "en", now=NOW, queue=qq, uploaded=kw.pop("uploaded", set()), store=kw.pop("store", {}),
                          shares=SH, targets=T, write=False, **kw)


def full(days=14):
    items = []
    for d in range(1, days + 1):
        day = (NOW.date() + dt.timedelta(days=d)).isoformat()
        items += [{"slug": f"loc-{d}-a", "en": [day, "8:00 AM"]}, {"slug": f"loc-{d}-b", "en": [day, "6:00 PM"]}]
    return items


def test_takes_first_free_slot():
    qq = q({"slug": "a", "en": ["2026-11-27", "8:00 AM"]})
    r = run(qq, "new", {"new": "map_tutorial"})
    assert r["placed"]["en"] == ["2026-11-27", "6:00 PM"] and r["moved"] is None


def test_moves_an_over_target_unproduced_item_not_a_location_one():
    items = full()
    items[5]["slug"] = "secret-x"   # day 3, 6 PM
    qq = q(*items)
    r = run(qq, "tut", {"tut": "map_tutorial", "secret-x": "secrets"})
    assert r["placed"]["en"] == items[5]["en"] and r["moved"]["slug"] == "secret-x"
    assert r["moved"]["en"][0] > "2026-12-10" and "over target" in r["moved"]["moved_by"]


def test_never_moves_uploaded_or_gate_approved_items():
    items = full()
    items[0]["slug"], items[1]["slug"] = "secret-up", "secret-ok"
    qq = q(*items)
    store = {"secret-ok:short:youtube-en": {"state": "AUTO_APPROVED"}}
    try:
        r = run(qq, "tut", {"tut": "map_tutorial", "secret-up": "secrets", "secret-ok": "secrets"},
                uploaded={("secret-up", "short")}, store=store)
        assert r["moved"] is None or r["moved"]["slug"] not in ("secret-up", "secret-ok")
    except ValueError:
        pass  # nothing else movable: refusing is correct


def test_never_moves_a_numbered_map_short_or_a_finished_video(monkeypatch):
    """Phase 10 (Nov 27): place moved the numbered, rendered tattoo Short #7 to make room; now the new item takes the
    first FREE slot instead, and only unproduced, unnumbered concepts can make way."""
    items = full(3)
    items[1]["slug"] = "secret-mapspot"   # numbered map Short
    items[3]["slug"] = "secret-rendered"  # finished video
    monkeypatch.setattr(schedule, "_series_member", lambda it: it["slug"] == "secret-mapspot")
    monkeypatch.setattr(schedule, "_rendered", lambda it, lang: it["slug"] == "secret-rendered")
    qq = q(*items)
    r = run(qq, "tut", {"tut": "map_tutorial", "secret-mapspot": "secrets", "secret-rendered": "secrets"}, within=5)
    assert r["moved"] is None
    assert r["placed"]["en"] == [(NOW.date() + dt.timedelta(days=4)).isoformat(), "8:00 AM"]  # first free slot
    assert {i["slug"]: i["en"] for i in qq["items"]}["secret-mapspot"] == items[1]["en"]
