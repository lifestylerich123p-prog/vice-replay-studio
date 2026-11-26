import datetime as dt
import json

from studio import quota, spend


def _setup(tmp_path, monkeypatch, items, reg):
    learn = tmp_path / "content" / "learn"
    learn.mkdir(parents=True)
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "channel.json").write_text(json.dumps({"spanish_winners_only": {"on": True, "min_views_24h": 150}}))
    (learn / "approved_queue.json").write_text(json.dumps({"items": items, "paused": []}))
    (learn / "uploads.json").write_text(json.dumps(reg))
    (learn / "uploads-es.json").write_text("{}")
    monkeypatch.setattr(spend, "ROOT", tmp_path)
    monkeypatch.setattr(spend, "LEARN", learn)
    monkeypatch.setattr(spend, "QUEUE", learn / "approved_queue.json")
    monkeypatch.setattr(spend, "es_threshold", lambda rule, days=7: 300)
    return learn


def test_spanish_waits_then_winner_gets_next_slot_and_loser_is_skipped(tmp_path, monkeypatch):
    items = [{"slug": "hit", "item": "short", "en": ["2026-11-24", "9:30 AM"], "es": ["2026-11-24", "9:30 AM"]},
             {"slug": "flop", "item": "short", "en": ["2026-11-24", "11:00 AM"], "es": ["2026-11-24", "11:00 AM"]},
             {"slug": "solo", "item": "short", "es_only": True, "es": ["2026-11-25", "12:30 PM"]}]
    learn = _setup(tmp_path, monkeypatch, items, {"V1": {"slug": "hit", "item": "short"}, "V2": {"slug": "flop", "item": "short"}})
    # English already up, Spanish waits for the 24 h check: nothing pending for them; the Spanish-only Short is
    p = {it["slug"]: (ne, ns) for it, ne, ns in spend.pending()}
    assert "hit" not in p and "flop" not in p and p["solo"] == (False, True)
    pub = dt.datetime(2026, 11, 24, 9, 30, tzinfo=quota.ET)
    stats = {"V1": (pub, 900), "V2": (pub, 40)}
    now = dt.datetime(2026, 11, 25, 10, 0, tzinfo=quota.ET)
    notes = spend.es_review(fetch=lambda v: stats[v], now=now)
    assert any(n.startswith("ES winner: hit") for n in notes) and any(n.startswith("ES skipped: flop") for n in notes)
    q = json.loads((learn / "approved_queue.json").read_text())["items"]
    hit, flop = q[0], q[1]
    assert hit["es_status"].startswith("winner") and hit["es"] == ["2026-11-25", "1:30 PM"]  # 12:30 is the Spanish-only Short's
    assert flop["es_status"].startswith("skipped")
    # the winner's Spanish upload is now pending; the skipped one never is
    p = {it["slug"]: (ne, ns) for it, ne, ns in spend.pending()}
    assert p["hit"] == (False, True) and "flop" not in p


def test_too_young_english_short_keeps_waiting(tmp_path, monkeypatch):
    items = [{"slug": "new", "item": "short", "en": ["2026-11-24", "9:30 AM"], "es": ["2026-11-24", "9:30 AM"]}]
    learn = _setup(tmp_path, monkeypatch, items, {"V": {"slug": "new", "item": "short"}})
    pub = dt.datetime(2026, 11, 24, 9, 30, tzinfo=quota.ET)
    assert spend.es_review(fetch=lambda v: (pub, 5000), now=pub + dt.timedelta(hours=10)) == []
    assert "es_status" not in json.loads((learn / "approved_queue.json").read_text())["items"][0]


def test_next_es_slot_skips_taken(monkeypatch):
    monkeypatch.setattr(spend, "es_paused_until", lambda: None)  # no Spanish pause in this test
    after = dt.datetime(2026, 11, 25, 10, 0, tzinfo=quota.ET)
    assert spend.next_es_slot(after, {("2026-11-25", "12:30 PM")}) == ["2026-11-25", "1:30 PM"]
