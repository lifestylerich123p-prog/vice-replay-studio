import datetime as dt
import sqlite3

from studio import tidy


def test_youtube_retention_deletes_only_old_other_channel_data(tmp_path, monkeypatch):
    monkeypatch.setattr(tidy, "ROOT", tmp_path)
    learn = tmp_path / "content" / "learn"
    learn.mkdir(parents=True)
    (learn / "market-2026-10-01.md").write_text("old")
    (learn / "market-es-2026-11-20.md").write_text("new")
    (learn / "lessons.md").write_text("ours")
    comp = tmp_path / "research" / "competitors"
    comp.mkdir(parents=True)
    (comp / "competitors-2026-10-10.json").write_text("{}")
    (tmp_path / "database").mkdir()
    con = sqlite3.connect(tmp_path / "database" / "vice.db")
    con.execute("CREATE TABLE competitor_videos (video_id TEXT, fetched_at TEXT)")
    con.execute("CREATE TABLE metric_snapshots (video_id TEXT, taken_at TEXT)")
    con.executemany("INSERT INTO competitor_videos VALUES (?, ?)", [("a", "2026-10-01T00:00:00Z"), ("b", "2026-11-20T00:00:00Z")])
    con.execute("INSERT INTO metric_snapshots VALUES ('ours', '2026-09-01T00:00:00Z')")
    con.commit()
    con.close()
    gone = []
    tidy.youtube_retention(False, gone, today=dt.date(2026, 11, 23))
    assert not (learn / "market-2026-10-01.md").exists()
    assert (learn / "market-es-2026-11-20.md").exists() and (learn / "lessons.md").exists()
    assert not (comp / "competitors-2026-10-10.json").exists()
    con = sqlite3.connect(tmp_path / "database" / "vice.db")
    assert [r[0] for r in con.execute("SELECT video_id FROM competitor_videos")] == ["b"]
    assert con.execute("SELECT COUNT(*) FROM metric_snapshots").fetchone()[0] == 1  # our own numbers stay
