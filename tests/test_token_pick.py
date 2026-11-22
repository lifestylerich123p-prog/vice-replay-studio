"""Keys are picked by the channel they belong to, so swapped setting names can't post as the wrong channel."""
import pytest

from studio import youtube_upload as yu


def setup(monkeypatch, env):
    for k in list(__import__("os").environ):
        if k.startswith("YT_") and k.endswith("REFRESH_TOKEN"):
            monkeypatch.delenv(k, raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    monkeypatch.setattr(yu, "_BY_CHANNEL", {})
    real_token = yu.token
    monkeypatch.setattr(yu, "token", lambda refresh_env=None: real_token(refresh_env) if refresh_env is None
                        else "acc-" + __import__("os").environ[refresh_env])
    monkeypatch.setattr(yu, "_owner_of", lambda acc: {"acc-EN": "UC_EN", "acc-ES": "UC_ES"}[acc])
    monkeypatch.setattr(yu, "channel_ids", lambda: {"en": "UC_EN", "es": "UC_ES"})


def test_swapped_names_still_pick_the_right_channel(monkeypatch):
    setup(monkeypatch, {"YT_REFRESH_TOKEN": "ES", "YT_ES_REFRESH_TOKEN": "EN"})
    assert yu.token_for("UC_EN") == "acc-EN"
    assert yu.token_for("UC_ES", "YT_ES_REFRESH_TOKEN") == "acc-ES"


def test_missing_channel_key_stops(monkeypatch):
    setup(monkeypatch, {"YT_REFRESH_TOKEN": "ES"})
    with pytest.raises(SystemExit, match="No saved YouTube key"):
        yu.token_for("UC_EN")
