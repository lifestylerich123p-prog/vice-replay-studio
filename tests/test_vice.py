"""Tests for the Vice Replay system (python -m pytest tests -q). Offline: no YouTube calls, temp database."""
import json
import subprocess

import pytest

from studio.vice import campaigns, channels, db, dedupe, factcheck, qc, rights, scoring


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "vice.db")
    yield


def make_video(path, seconds=4, black=None, silent=False, src="testsrc2", vertical=True):
    """Synthetic test video (optionally with a black stretch [a, b] and/or silence)."""
    size = "1080x1920" if vertical else "1920x1080"
    vf = f"drawbox=enable='between(t,{black[0]},{black[1]})':color=black:t=fill" if black else "null"
    audio = "anullsrc=r=48000:cl=stereo" if silent else "sine=frequency=440:sample_rate=48000"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "lavfi", "-i", f"{src}=size={size}:rate=30",
                    "-f", "lavfi", "-i", audio, "-t", str(seconds), "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-ac", "2", str(path)], check=True)
    return path


# ---------- scoring + rights gate ----------

def test_score_total_and_validation():
    assert scoring.total({k: 10 for k in scoring.WEIGHTS}) == 100
    assert scoring.total({"curiosity": 8, "payoff": 6, "context": 10, "audio": 5, "visual": 7, "contribution": 0}) == 65  # 64.5 rounds up
    with pytest.raises(ValueError):
        scoring.total({"curiosity": 11, "payoff": 1, "context": 1, "audio": 1, "visual": 1, "contribution": 1})
    with pytest.raises(ValueError):
        scoring.total({"curiosity": 5})


def test_high_score_is_still_blocked_without_rights():
    cand = {"source_url": "https://www.youtube.com/watch?v=random-creator", "scores": {k: 10 for k in scoring.WEIGHTS}}
    r = scoring.evaluate(cand, "vice-replay")
    assert r["total"] == 100 and r["gate"] == "BLOCKED"


def test_rights_gate_destinations():
    assert rights.check("media/trailer/extended-look-skyline-blimp.mp4", "vice-replay")["ok"]
    assert rights.check("../media/official/car-grotti-cheetah-01.jpg", "vice-replay")["ok"]
    assert not rights.check("media/trailer/extended-look-skyline-blimp.mp4", "clipcircuit")["ok"]
    assert not rights.check("campaign:lacy-gta6", "vice-replay")["ok"]  # owner rule Nov 20
    assert rights.check("campaign:lacy-gta6", "clipcircuit")["ok"]
    assert not rights.check("campaign:lacy-gta6", "clipcircuit", ai_voice=True)["ok"]  # Lacy bans AI content
    assert not rights.check("campaign:lacy-gta6", "clipcircuit", branding=True)["ok"]  # no logos
    assert not rights.check("campaign:tomo-gta6", "clipcircuit")["ok"]  # paused
    assert not rights.check("https://www.youtube.com/watch?v=xyz", "vice-replay")["ok"]  # default deny
    assert not rights.check("music:gta6-official", "vice-replay")["ok"]


def test_rights_conditions_drop_trailer_audio():
    c = rights.check("media/trailer/extended-look-avenue-skyline.mp4", "vice-replay")
    assert any("audio" in x for x in c["conditions"])


# ---------- channel separation ----------

def test_channel_validation():
    assert not channels.validate("vice-replay", "campaign-clip", check_token=False)["ok"]
    assert channels.validate("clipcircuit", "campaign-clip", check_token=False)["ok"]
    assert not channels.validate("what-if-arena", "original-narrated", check_token=False)["ok"]
    ok = channels.validate("vice-replay", "original-narrated", token_channel="UCzk9Wts3WFynOHZQJRWOQIw")
    assert ok["ok"]
    wrong = channels.validate("vice-replay", "original-narrated", token_channel="UC_some_other_channel")
    assert not wrong["ok"] and "belongs to" in wrong["problems"][0]


# ---------- dedupe ----------

def test_same_event_text():
    a = {"creator": "lacy", "published": "2026-11-19T10:00:00", "description": "Lacy found a shoe store in GTA 6"}
    b = {"creator": "lacy", "published": "2026-11-19T18:00:00", "description": "LACY finds the SHOE STORE 😭 #gta6"}
    c = {"creator": "lacy", "published": "2026-11-19T18:00:00", "description": "Lacy fights an alligator"}
    d = {"creator": "kai", "published": "2026-11-19T18:00:00", "description": "Kai found a shoe store"}
    assert dedupe.same_event(a, b)
    assert not dedupe.same_event(a, c)
    assert not dedupe.same_event(a, d)


def test_footage_fingerprint(tmp_path):
    v1 = make_video(tmp_path / "a.mp4", 6, src="testsrc2")
    v2 = tmp_path / "a_reencoded.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(v1), "-vf", "scale=720:1280,eq=brightness=0.03",
                    "-c:v", "libx264", "-crf", "30", str(v2)], check=True)
    v3 = make_video(tmp_path / "c.mp4", 6, src="mandelbrot")
    h1, h2, h3 = (dedupe.video_hash(v) for v in (v1, v2, v3))
    assert dedupe.same_footage(h1, h2)
    assert not dedupe.same_footage(h1, h3)


# ---------- fact checks ----------

def test_claims_and_risks():
    assert factcheck.claims("Which one are you racing first? It sold 25 million copies.") == ["It sold 25 million copies."]
    ep = {"short_title": "GTA 6 ending explained", "sources": [],
          "short": [{"headline": "LEAKED", "text": "Leakers say the map is confirmed bigger. It has 6 regions."}]}
    f = factcheck.check_episode(ep)
    levels = {(x["level"], x["where"]) for x in f}
    assert ("fail", "sources") in levels
    assert any(x["level"] == "fail" and "confirmed" in x["fix"] for x in f)
    assert ("fail", "title") in levels  # spoiler wording in the title
    assert "sexual content" in factcheck.content_risks("KreekCraft reacts to the shower scene")


# ---------- campaign math ----------

def test_payout_math():
    c = {"rate_per_1000_views": 1.0, "min_views_to_pay": 3000, "min_payout_per_clip": 3.0, "max_payout_per_clip": 300.0,
         "budget_left": 5900}
    assert campaigns.payout(c, 2999)["gross"] == 0.0
    assert campaigns.payout(c, 10000) == {"type": "per-view", "gross": 10.0, "net": 9.0,
                                          "note": "net assumes a 10% platform fee"}
    assert campaigns.payout(c, 1_000_000)["gross"] == 300.0
    assert campaigns.payout({"pay_type": "pool", "pool": 12500}, 50000)["gross"] is None


def test_money_states_are_separate():
    campaigns.record("kreekcraft-gta6", "clip1", "estimated", 9.0, 10000)
    campaigns.record("kreekcraft-gta6", "clip1", "approved", 8.1, 9000)
    led = {r["status"]: r["usd"] for r in campaigns.ledger(db.connect())}
    assert led == {"estimated": 9.0, "approved": 8.1}
    with pytest.raises(Exception):
        campaigns.record("x", "y", "paid-maybe", 1, 1)


# ---------- QC ----------

def test_qc_catches_black_frames_and_silence(tmp_path):
    v = make_video(tmp_path / "bad.mp4", 5, black=(0.0, 1.0), silent=True)
    rep = qc.check(v, dest="vice-replay", use_whisper=False,
                   project={"id": "t", "rights_sources": ["media/trailer/extended-look-aerial-bay.mp4"]})
    by = {}
    for c in rep["checks"]:
        by.setdefault(c["check"], []).append(c)
    assert not rep["passed"]
    assert by["black frames"][0]["status"] == "fail" and by["black frames"][0]["at"] == pytest.approx(0.0, abs=0.1)
    assert by["opening"][0]["status"] == "fail"
    assert any(c["status"] == "warn" for c in by["silence"])
    assert by["format"][0]["status"] == "pass"


def test_qc_wrong_aspect_and_blocked_rights(tmp_path):
    v = make_video(tmp_path / "wide.mp4", 3, vertical=False)
    rep = qc.check(v, dest="vice-replay", use_whisper=False,
                   project={"id": "t", "rights_sources": ["https://twitch.tv/someone/clip/abc"]})
    assert rep["passed"] is False
    assert any(c["check"] == "rights" and c["status"] == "fail" for c in rep["checks"])


def test_wer():
    assert qc.wer(["a", "b", "c", "d"], ["a", "b", "c", "d"]) == 0
    assert qc.wer(["a", "b", "c", "d"], ["a", "x", "c"]) == 0.5


# ---------- storage ----------

def test_cache_ttl_and_snapshots_append_only():
    con = db.connect()
    db.cache_put(con, "k", {"v": 1}, ttl_hours=1)
    assert db.cache_get(con, "k") == {"v": 1}
    db.cache_put(con, "old", {"v": 2}, ttl_hours=-1)
    assert db.cache_get(con, "old") is None
    con.execute("INSERT INTO metric_snapshots (video_id, taken_at, views) VALUES ('v', '2026-11-20T10:00:00Z', 5)")
    con.execute("INSERT INTO metric_snapshots (video_id, taken_at, views) VALUES ('v', '2026-11-20T11:00:00Z', 9)")
    assert [r["views"] for r in db.rows(con, "SELECT views FROM metric_snapshots WHERE video_id='v' ORDER BY taken_at")] == [5, 9]


def test_project_resume_steps():
    con = db.connect()
    p = db.project_save(con, {"id": "p1", "kind": "clip", "steps": [], "files": {}})
    p = db.project_get(con, "p1")
    db.step_done(con, p, "cut", cut="x.mp4")
    p = db.project_get(con, "p1")
    assert p["steps"] == ["cut"] and p["files"]["cut"] == "x.mp4"


def test_calendar_is_28_distinct_ideas():
    from studio.vice import calendar
    items = calendar.load()
    assert len(items) == 28 and len({i["topic"] for i in items}) == 28
    assert len({i["date"] for i in items}) == 14
    for i in items:
        for k in calendar.COLS:
            assert i.get(k), (i["id"], k)


def test_spoilers_and_leaks_flags_downgrade_script_but_not_revealing_titles():
    """Owner Nov 24: a warned spoiler round and labeled leak news are allowed per episode; titles never reveal."""
    from studio.vice import factcheck
    base = {"sources": ["https://example.com/a"], "segments": [
        {"headline": "SPOILERS", "text": "Last round. Story spoilers. The final mission is called The End of the Road."},
        {"headline": "THE LEAKS", "text": "Round five. The leaks, as reported."}]}
    fails = lambda e: [f for f in factcheck.check_episode(e) if f["level"] == "fail"]
    assert fails(dict(base, title="GTA 6 Trivia: Leaks & Spoilers"))          # old rule: blocked
    ok = dict(base, title="GTA 6 Trivia: Leaks & Spoilers", spoilers_ok="owner", leaks_ok="owner")
    assert not fails(ok)                                                       # new rule: allowed in a warned round
    assert fails(dict(ok, title="GTA 6: the ending where Jason dies"))         # a title that reveals still fails
