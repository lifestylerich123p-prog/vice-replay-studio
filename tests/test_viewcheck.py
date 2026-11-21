"""Views check (studio/vice/viewcheck.py): rules learned from our own post-launch Shorts."""
from studio.vice import viewcheck


def ep(first, words=40, title="GTA 6 just did 52 HOURS", headline="52 HOURS", **kw):
    seg1 = {"headline": headline, "text": "word " * words, **first}
    return {"short_title": title, "short": [seg1, {"headline": "B", "text": "x"}], **kw}


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
    _, w = viewcheck.check(ep({"media": "a.mp4"}, words=100))
    assert any("words" in x for x in w)
    _, w = viewcheck.check(ep({"media": "a.mp4"}, title="Change these GTA 6 settings NOW", headline="SETTINGS"))
    assert any("plain tip" in x for x in w)
    _, w = viewcheck.check(ep({"media": "a.mp4"}, title="GTA 6 settings: 3 that cost you 20 FPS", headline="20 FPS"))
    assert not any("plain tip" in x for x in w)  # a number up front turns a tip into a verdict
