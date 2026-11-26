"""Owner Nov 26 Phase 3: verified balance vs ledger, never an estimate shown as exact (studio/credits.py)."""
import datetime as dt

from studio import credits as cr

T0 = dt.datetime(2026, 11, 26, 19, 0, tzinfo=dt.timezone.utc)
ROWS = [{"t": "2026-11-26T14:19:21Z", "job": "voice:a:es", "act": "claim", "credits": 4, "what": "x"},
        {"t": "2026-11-26T14:20:50Z", "job": "voice:a:es", "act": "done", "credits": 4, "balance": "?"},
        {"t": "2026-11-26T20:00:00Z", "job": "voice:b:es", "act": "claim", "credits": 3},
        {"t": "2026-11-26T20:05:00Z", "job": "voice:b:es", "act": "done", "credits": 3},
        {"t": "2026-11-26T21:00:00Z", "job": "image:c:thumb", "act": "claim", "credits": 2},
        {"t": "2026-11-26T21:01:00Z", "job": "image:c:thumb", "act": "release", "reason": "provider error"},
        {"t": "2026-11-26T22:00:00Z", "job": "voice:d:es", "act": "claim", "credits": 5}]


def test_fresh_reading_with_no_spend_since_is_verified():
    snaps = [{"t": "2026-11-26T19:03:48Z", "remaining": 74}]
    s = cr.summary(rows=ROWS[:2], snaps=snaps, now=T0 + dt.timedelta(hours=1))
    assert s["balance"]["verified"] and s["balance"]["remaining"] == 74


def test_spend_after_the_reading_makes_it_an_estimate_not_a_balance():
    snaps = [{"t": "2026-11-26T19:03:48Z", "remaining": 74}]
    s = cr.summary(rows=ROWS, snaps=snaps, now=T0 + dt.timedelta(hours=4))
    b = s["balance"]
    assert not b["verified"] and b["remaining"] is None and b["estimate"] == 71 and b["spent_since"] == 3
    assert "UNVERIFIED" in cr.lines(s)[0] and "ESTIMATE 71" in cr.lines(s)[0]


def test_old_reading_is_unverified():
    snaps = [{"t": "2026-11-20T10:00:00Z", "remaining": 90}]
    assert not cr.summary(rows=[], snaps=snaps, now=T0)["balance"]["verified"]
    assert "UNVERIFIED, no provider reading" in cr.lines(cr.summary(rows=[], snaps=[], now=T0))[0]


def test_ledger_pending_failed_per_day_and_episode():
    led = cr.ledger_summary(ROWS, now=T0 + dt.timedelta(hours=10))
    assert [p["job"] for p in led["pending"]] == ["voice:d:es"]
    assert led["failed"][0]["job"] == "image:c:thumb" and led["failed"][0]["credits_claimed"] == 2
    assert led["per_day"]["2026-11-26"] == 7 and led["per_episode"] == {"a": 4, "b": 3}


def test_reconcile_flags_spend_outside_the_ledger():
    snaps = [{"t": "2026-11-26T19:00:00Z", "remaining": 74}, {"t": "2026-11-26T23:00:00Z", "remaining": 61}]
    led = cr.ledger_summary(ROWS)
    r = cr.reconcile(snaps, led["spends"])[0]
    assert r["balance_drop"] == 13 and r["ledger_spent"] == 3 and r["unexplained"] == 10 and "outside" in r["note"]


def test_record_appends_a_provider_reading(tmp_path):
    p = tmp_path / "c.jsonl"
    cr.record(74, purchased=74, sub_remaining=0, path=p, t=T0)
    assert cr.snapshots(p)[0]["remaining"] == 74 and cr.snapshots(p)[0]["source"].startswith("everygen")
