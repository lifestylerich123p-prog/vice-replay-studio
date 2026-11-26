"""Owner, Nov 26: autonomous publishing only when every mandatory check passes (studio/approvals.py)."""
import datetime as dt
import json

import pytest

from studio import approvals as ap

ET = ap.ET
NOW = dt.datetime(2026, 11, 27, 2, 0, tzinfo=ET)
SLOT = ("2026-11-28", "8:00 AM")


@pytest.fixture
def world(tmp_path, monkeypatch):
    """A tiny project: one map Short, rendered, sources, fact re-check, tests passed, auto-publishing on."""
    for name in ("STORE", "TESTS", "FACTS", "CONFIG"):
        pass
    monkeypatch.setattr(ap, "ROOT", tmp_path)
    monkeypatch.setattr(ap, "STORE", tmp_path / "approvals.json")
    monkeypatch.setattr(ap, "TESTS", tmp_path / "tests_status.json")
    monkeypatch.setattr(ap, "FACTS", tmp_path / "factchecks.json")
    monkeypatch.setattr(ap, "CONFIG", tmp_path / "channel.json")
    (tmp_path / "content" / "learn").mkdir(parents=True)
    (tmp_path / "content" / "learn" / "uploads.json").write_text("{}")
    ap.CONFIG.write_text(json.dumps({"auto_publish": {"on": True, "max_per_day": 2}}))
    ep = {"slug": "gta6-x", "short_title": "GTA 6 x location 🗺️ #GTA6 #Shorts", "short_description": "Where x is.",
          "sources": ["A - a", "B - b"], "short": [{"text": "X is here.", "chart": {"type": "kinetic"}},
                                                    {"text": "In Key Lento.", "chart": {"type": "map", "at": "Key Lento"}}]}
    (tmp_path / "episodes").mkdir()
    epf = tmp_path / "episodes" / "gta6-x.json"
    epf.write_text(json.dumps(ep))
    out = tmp_path / "output" / "gta6-x"
    out.mkdir(parents=True)
    (out / "gta6-x-short.mp4").write_bytes(b"video")
    (out / "gta6-x-short.txt").write_text(f"TITLE\n{ep['short_title']}\n\nDESCRIPTION\nWhere x is.\n")
    ap.FACTS.write_text(json.dumps({"gta6-x": {"date": "2026-11-26", "note": "ok"}}))
    ap.TESTS.write_text(json.dumps({"passed": True, "code": ap.code_hash(), "at": NOW.isoformat()}))
    monkeypatch.setattr(ap, "_probe", lambda v: {"w": 1080, "h": 1920, "audio": True, "dur": 15.0})
    monkeypatch.setattr(ap, "gate", lambda p: ([], []))
    return {"ep": epf, "out": out}


def evaluate(world, publish=SLOT):
    return ap.evaluate(world["ep"], "short", "youtube-en", publish, now=NOW)


def test_all_checks_pass_then_upload_allowed(world):
    assert evaluate(world)["state"] == "AUTO_APPROVED"
    ap.require("gta6-x", "short", "youtube-en", title="GTA 6 x location 🗺️ #GTA6 #Shorts", publish=SLOT, now=NOW)


def test_case1_never_checked_video_is_blocked(world):
    with pytest.raises(ap.Blocked, match="has not passed the publishing gate"):
        ap.require("gta6-x", "short", "youtube-en", now=NOW)


def test_case2_qa_failure_blocks(world, monkeypatch):
    monkeypatch.setattr(ap, "gate", lambda p: (["QC black frames: 1.2 s"], []))
    r = evaluate(world)
    assert r["state"] == "BLOCKED" and "black frames" in r["blockers"][0]
    with pytest.raises(ap.Blocked):
        ap.require("gta6-x", "short", "youtube-en", now=NOW)


def test_case3_timeout_after_upload_is_reconciled_not_reposted(world):
    evaluate(world)
    ap.set_state("gta6-x", "short", "youtube-en", "UPLOADING")
    ap.set_state("gta6-x", "short", "youtube-en", "FAILED", "timeout")
    with pytest.raises(ap.Blocked, match="reconcile"):
        ap.require("gta6-x", "short", "youtube-en", now=NOW)
    r = ap.reconcile("gta6-x", "short", "youtube-en", found_id="abc123")  # YouTube says it's already there
    assert r["state"] == "SCHEDULED" and r["video_id"] == "abc123"
    with pytest.raises(ap.Blocked):
        ap.require("gta6-x", "short", "youtube-en", now=NOW)


def test_case4_change_after_approval_needs_new_evaluation(world):
    evaluate(world)
    ep = json.loads(world["ep"].read_text())
    ep["short"][1]["text"] = "In Vice City."
    world["ep"].write_text(json.dumps(ep))
    with pytest.raises(ap.Blocked, match="changed after"):
        ap.require("gta6-x", "short", "youtube-en", now=NOW)
    assert json.loads(ap.STORE.read_text())["gta6-x:short:youtube-en"]["state"] == "NEEDS_REVIEW"


def test_case5_missing_sources_or_recheck_hold_the_video(world):
    ep = json.loads(world["ep"].read_text())
    ep["sources"] = ["only one"]
    world["ep"].write_text(json.dumps(ep))
    (world["out"] / "gta6-x-short.mp4").touch()
    assert evaluate(world)["state"] == "BLOCKED"
    ap.FACTS.write_text("{}")
    ep["sources"] = ["A", "B"]
    world["ep"].write_text(json.dumps(ep))
    (world["out"] / "gta6-x-short.mp4").touch()
    r = evaluate(world)
    assert r["state"] == "NEEDS_REVIEW" and any("re-checked" in x for x in r["reviews"])


def test_case7_missed_slot_is_never_posted(world):
    evaluate(world)
    later = dt.datetime(2026, 11, 28, 9, 0, tzinfo=ET)
    with pytest.raises(ap.Blocked, match="passed"):
        ap.require("gta6-x", "short", "youtube-en", now=later)
    assert ap.evaluate(world["ep"], "short", "youtube-en", SLOT, now=later)["state"] == "NEEDS_REVIEW"


def test_plan_format_tests_and_limits(world, monkeypatch):
    ep = json.loads(world["ep"].read_text())
    ep["short"][1]["chart"] = {"type": "tier"}
    world["ep"].write_text(json.dumps(ep))
    (world["out"] / "gta6-x-short.mp4").touch()
    assert any("14-day plan" in x for x in evaluate(world)["reviews"])
    ap.TESTS.write_text(json.dumps({"passed": False}))
    assert any("test suite" in x for x in evaluate(world)["reviews"])
    assert any("English YouTube" in x for x in ap.evaluate(world["ep"], "short", "youtube-es", SLOT, now=NOW)["reviews"])


def test_two_failures_pause_auto_publishing(world):
    ap.upload_result(False, "500")
    assert ap.auto_cfg()["on"]
    ap.upload_result(False, "500 again")
    assert not ap.auto_cfg()["on"]
    with pytest.raises(ap.Blocked, match="paused"):
        ap.require("gta6-x", "short", "youtube-en", now=NOW)


def test_states_only_move_forward_through_the_gate():
    with pytest.raises(ap.Blocked):
        ap.transition({"state": "RENDERED"}, "UPLOADING")
    with pytest.raises(ap.Blocked):
        ap.transition({"state": "NEEDS_REVIEW"}, "UPLOADING")
    rec = {"state": "AUTO_APPROVED"}
    ap.transition(rec, "UPLOADING")
    ap.transition(rec, "SCHEDULED")
    ap.transition(rec, "PUBLISHED")
    assert rec["state"] == "PUBLISHED"


def test_fact_recheck_does_not_change_the_fingerprint(world):
    ep = json.loads(world["ep"].read_text())
    before = ap.spec_hash(ep, "short")
    ep["facts_checked"] = "2026-11-27"
    assert ap.spec_hash(ep, "short") == before
