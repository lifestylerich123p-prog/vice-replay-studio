"""Views check (studio/vice/viewcheck.py): rules learned from our own post-launch Shorts."""
from studio.vice import viewcheck


def ep(first, words=40, title="GTA 6 just did 52 HOURS", headline="52 HOURS", **kw):
    seg1 = {"headline": headline, "text": "word " * words, **first}
    return {"short_title": title, "short": [seg1, {"headline": "B", "text": "x"}], "originality": "test", **kw}


def test_still_first_frame_blocks_unless_it_moves():
    b, _ = viewcheck.check(ep({"media": "../media/official/car.jpg"}))
    assert b and "still picture" in b[0]
    for ok in ({"media": "../media/trailer/extended-look-x.mp4"}, {"media": "a.jpg", "zoom": {"to": 1.4}},
               {"media": "a.jpg", "magnify": {"box": [0, 0, 1, 1]}}, {"shots": [{"media": "a.mp4", "start": 0}]}):
        assert viewcheck.check(ep(ok))[0] == []


def test_owner_gameplay_counts_as_motion_unless_kept_picture():
    assert viewcheck.check(ep({"media": "a.jpg"}), gameplay_available=True)[0] == []
    assert viewcheck.check(ep({"media": "a.jpg", "keep_media": True}), gameplay_available=True)[0]
    assert viewcheck.check(ep({"media": "a.jpg"}, use_gameplay=False), gameplay_available=True)[0]


def test_long_scripts_and_plain_tips_warn():
    b, _ = viewcheck.check(ep({"media": "a.mp4"}, words=100))
    assert any("words" in x for x in b)  # over ~30 s blocks
    _, w = viewcheck.check(ep({"media": "a.mp4"}, words=60))
    assert any("words" in x for x in w)  # 20-30 s warns
    _, w = viewcheck.check(ep({"media": "a.mp4"}, title="Change these GTA 6 settings NOW", headline="SETTINGS"))
    assert any("plain tip" in x for x in w)
    _, w = viewcheck.check(ep({"media": "a.mp4"}, title="GTA 6 settings: 3 that cost you 20 FPS", headline="20 FPS"))
    assert not any("plain tip" in x for x in w)  # a number up front turns a tip into a verdict


def test_missing_tags_warn_once_per_episode_not_per_short():
    two = {"shorts": [{"id": "news", "title": "GTA 6 52 HOURS", "es": {"title": "GTA 6 52 HORAS"},
                       "segments": [{"headline": "52", "text": "x", "media": "a.mp4"}]},
                      {"id": "tips", "title": "GTA 6 20 FPS", "es": {"title": "GTA 6 20 FPS"},
                       "segments": [{"headline": "20", "text": "x", "media": "a.mp4"}]}]}
    _, w = viewcheck.check(two)
    assert sum("no `tags`" in x for x in w) == 1
    assert sum("Spanish versions have no tags" in x for x in w) == 1
    assert viewcheck.check_tags(dict(two, tags=["GTA 6 hours"], tags_es=["GTA 6 horas"])) == []


def test_trailer_only_shorts_need_a_chart_or_gameplay():
    plain = {"short": [{"headline": "52", "text": "x", "media": "../media/trailer/a.mp4"}]}
    b, _ = viewcheck.check(plain)
    assert any(x.startswith("originality") for x in b)
    with_chart = {"short": [{"headline": "52", "text": "x", "chart": {"type": "counter", "value": 52}}]}
    assert not any(x.startswith("originality") for x in viewcheck.check(with_chart)[0])
    gameplay = {"short": [{"headline": "52", "text": "x", "media": "../media/gameplay/clip.mp4"}]}
    assert not any(x.startswith("originality") for x in viewcheck.check(gameplay)[0])
    waived = dict(plain, originality="owner-approved montage")
    assert not any(x.startswith("originality") for x in viewcheck.check(waived)[0])
