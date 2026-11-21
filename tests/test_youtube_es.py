"""Spanish channel uploader: never posts to the English channel, only approved Shorts with Spanish titles."""
import pytest

from studio import youtube_es

EP = {"slug": "gta6-x", "short": [{"text": "a"}], "short_es": {"title": "GTA 6 en español #Shorts"},
      "shorts": [{"id": "news", "segments": [], "es": {"title": "Noticia GTA 6"}, "pinned_comment_es": "¿Sí o no?"},
                 {"id": "tips", "segments": []}]}


def test_jobs_only_approved_with_spanish_title(capsys):
    got = youtube_es.jobs(EP, {"all"})
    assert [(k, n) for k, n, _, _ in got] == [("short", "gta6-x-short-es"), ("news", "gta6-x-short-news-es")]
    assert got[1][3] == "¿Sí o no?"
    assert "skip tips" in capsys.readouterr().out
    assert [k for k, *_ in youtube_es.jobs(EP, {"news"})] == ["news"]


def cfg(es_id):
    return {"vice-replay": {"channel_id": "UC_EN"}, "vice-replay-es": {"channel_id": es_id}}


def test_refuses_english_token_and_unregistered_channel(monkeypatch):
    monkeypatch.setattr(youtube_es, "whoami", lambda tok: ("UC_EN", "Vice Replay"))
    monkeypatch.setattr(youtube_es, "config", lambda: cfg("UC_ES"))
    with pytest.raises(SystemExit, match="ENGLISH"):
        youtube_es.check_channel("t")
    monkeypatch.setattr(youtube_es, "whoami", lambda tok: ("UC_ES", "Vice Replay en Español"))
    monkeypatch.setattr(youtube_es, "config", lambda: cfg(""))
    with pytest.raises(SystemExit, match="put UC_ES"):
        youtube_es.check_channel("t")
    monkeypatch.setattr(youtube_es, "config", lambda: cfg("UC_ES"))
    assert youtube_es.check_channel("t") == "UC_ES"
