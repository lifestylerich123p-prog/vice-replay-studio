"""YouTube quota planner (studio/quota.py): costs, the learned daily limit, free posting slots."""
import datetime as dt
import json

from studio import quota


def test_costs_match_youtube_docs():
    assert quota.cost("POST", "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet") == 1600
    assert quota.cost("POST", "https://www.googleapis.com/upload/youtube/v3/captions?uploadType=multipart") == 400
    assert quota.cost("GET", "https://youtube.googleapis.com/youtube/v3/captions?part=snippet&videoId=x") == 50
    assert quota.cost("POST", "https://youtube.googleapis.com/youtube/v3/commentThreads?part=snippet") == 50
    assert quota.cost("GET", "https://youtube.googleapis.com/youtube/v3/videos?part=status&id=x") == 1
    assert quota.cost("GET", "https://www.googleapis.com/youtube/v3/search?q=gta") == 100
    assert quota.cost("PUT", "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&upload_id=AB") == 0
    assert quota.cost("PUT", "https://youtube.googleapis.com/youtube/v3/videos?part=snippet") == 50


def test_limit_is_learned(tmp_path, monkeypatch):
    monkeypatch.setattr(quota, "LEDGER", tmp_path / "quota.json")
    monkeypatch.setattr(quota, "uploads_today", lambda: 0)
    assert quota.limit() == 10000
    (tmp_path / "quota.json").write_text(json.dumps({"2000-01-01": {"used": 0, "registry_est": 17500}}))
    assert quota.limit() == 17500  # a clean day with more raises it
    quota.spend("POST", "https://www.googleapis.com/upload/youtube/v3/videos?x")
    assert quota.used_today() == 1600 and quota.left_today() == 17500 - 1600 - quota.MARGIN
    quota.mark_exhausted()  # a real "used up" pins the limit to what we had spent
    assert quota.limit() == 1600 and quota.left_today() == 0


def test_free_slots_skip_taken_and_past(monkeypatch):
    monkeypatch.setattr(quota, "reserved", lambda lang="en": {})  # no approved-queue bookings in this test
    tomorrow = dt.datetime.now(quota.ET).date() + dt.timedelta(days=1)
    slots = quota.slots_for(tomorrow)
    first = dt.datetime.combine(tomorrow, dt.datetime.strptime(slots[0], "%I:%M %p").time(), quota.ET)
    plan = dict(quota.free_slots({tomorrow: [first + dt.timedelta(minutes=30)]}, days=2))
    assert slots[0] not in plan[tomorrow] and len(plan[tomorrow]) == len(slots) - 1


def test_free_slots_count_the_approved_queue(monkeypatch):
    tomorrow = dt.datetime.now(quota.ET).date() + dt.timedelta(days=1)
    slots = quota.slots_for(tomorrow)
    at = dt.datetime.combine(tomorrow, dt.datetime.strptime(slots[1], "%I:%M %p").time(), quota.ET)
    monkeypatch.setattr(quota, "reserved", lambda lang="en": {tomorrow: [at]})
    plan = dict(quota.free_slots({}, days=2))
    assert slots[1] not in plan[tomorrow]
