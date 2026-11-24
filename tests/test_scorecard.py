from studio import scorecard


def test_card_type_picks_main_card_not_hook_cards():
    charts = [{"type": "kinetic"}, {"type": "tier"}, {"type": "tier"}, {"type": "tier"}, {"type": "kinetic"}]
    assert scorecard.card_type(charts) == "tier"
    assert scorecard.card_type([{"type": "kinetic"}, {"type": "versus"}, {"type": "versus"}, {"type": "list"}]) == "versus"
    assert scorecard.card_type([{"type": "kinetic"}]) == "kinetic only"
    assert scorecard.card_type([]) == "-"


def test_retired_groups_are_known():
    assert ("picture", "trailer/screenshots") in scorecard.RETIRED
    assert ("kind", "campaign clip") in scorecard.RETIRED


def test_script_tags_lettering_vs_older_charts(tmp_path, monkeypatch):
    import json
    monkeypatch.setattr(scorecard, "ROOT", tmp_path)
    (tmp_path / "episodes").mkdir()
    vice = {"style": "vice", "short": [{"text": "Vice City is B tier.", "chart": {"type": "kinetic"}},
                                       {"text": "B tier.", "chart": {"type": "tier"}}]}
    old = {"short": [{"text": "Darts are out.", "chart": {"type": "quote"}}]}
    (tmp_path / "episodes" / "a.json").write_text(json.dumps(vice))
    (tmp_path / "episodes" / "b.json").write_text(json.dumps(old))
    ups = {"A": {"slug": "a", "item": "short"}, "B": {"slug": "b", "item": "short"}}
    a, b = scorecard.script_tags("A", ups), scorecard.script_tags("B", ups)
    assert a["picture"] == "lettering cards" and a["card"] == "tier" and a["opener"] == "statement"
    assert b["picture"] == "graph (older charts)" and b["card"] == "quote"


def test_status_momentum_flags_only_real_risers():
    import datetime as dt
    from studio import status
    h = lambda x: dt.timedelta(hours=x)
    vph = [(h(3), 170.0, 510, "Tier list"), (h(5), 3.0, 15, "Darts"), (h(30), 4.0, 120, "Old"),
           (h(60), 5.0, 300, "Older"), (h(10), 60.0, 600, "Fast but older than... no, 10 h")]
    lines = status.momentum_lines(vph)
    assert any("Tier list" in l for l in lines)
    assert not any("Darts" in l for l in lines)
    assert status.momentum_lines(vph[:2]) == []  # not enough Shorts for a baseline


def test_status_cold_lines():
    import datetime as dt
    from studio.status import cold_lines
    rows = [(dt.timedelta(hours=3), 1.0, 3, "cold one"), (dt.timedelta(hours=3), 50.0, 150, "fine one"),
            (dt.timedelta(minutes=30), 0.0, 0, "too young"), (dt.timedelta(hours=20), 0.1, 2, "too old")]
    out = cold_lines(rows)
    assert len(out) == 1 and "cold one" in out[0]
