"""Phase 5 #1: dates, weekdays, slots and time zones in the queue are checked mechanically."""
import datetime as dt

from studio import calcheck

NOW = dt.datetime(2026, 11, 26, 15, 0, tzinfo=calcheck.ET)


def test_labels_and_utc():
    assert calcheck.label("2026-11-30") == "Mon Nov 30" and calcheck.label("2026-11-29") == "Sun Nov 29"
    assert calcheck.to_utc("2026-11-27", "7:00 PM").strftime("%Y-%m-%d %H:%M") == "2026-11-28 00:00"


def test_wrong_weekday_note_and_off_plan_slot_are_flagged():
    q = {"items": [{"slug": "x", "item": "short", "en": ["2026-11-30", "8:00 AM"], "note": "moved to Sun Nov 30"},
                   {"slug": "y", "item": "short", "en": ["2026-11-29", "1:30 PM"]},
                   {"slug": "z", "item": "short", "es": ["2026-11-31", "12:30 PM"]}]}
    problems, rows = calcheck.check(queue=q, store={}, now=NOW)
    text = "\n".join(problems)
    assert "Nov 30 is a Mon" in text and "not a plan slot" in text and "not a valid date" in text


def test_gate_slot_mismatch_is_flagged():
    q = {"items": [{"slug": "x", "item": "short", "en": ["2026-11-30", "8:00 AM"]}]}
    store = {"x:short:youtube-en": {"state": "AUTO_APPROVED", "publish": ["2026-11-29", "8:00 AM"]}}
    problems, _ = calcheck.check(queue=q, store=store, now=NOW)
    assert any("gate approved" in p for p in problems)
