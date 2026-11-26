"""Phase 5 #4: recognizable recurring series get their own badge (EN/ES names) next to the channel bug."""
from studio import brand, renderdeps


def test_every_series_has_both_languages_and_draws():
    for sid, (en, es, color) in brand.SERIES.items():
        assert en and es and len(color) == 3
        for lang in ("en", "es"):
            im = brand.series_badge(sid, lang, 40)
            assert im.width > im.height > 0
    card = brand.headline_card("", 540, 960, True, None, "mythbusters", "es")
    assert card.size == (540, 960)


def test_series_is_a_render_input():
    ep = {"short": [{"text": "a"}]}
    assert renderdeps.video_inputs(dict(ep, series_id="gps"), "short", "en") != renderdeps.video_inputs(ep, "short", "en")
