import json
import subprocess

from studio import charts
from studio.vice import rights, viewcheck

BARS = {"type": "bars", "items": [["IShowSpeed", 68.7], ["CarryMinati", 18.1]], "unit": "M", "note": "test"}
VS = {"type": "counter", "value": 3.79, "prefix": "$", "unit": "B", "label": "GTA 6",
      "vs": {"value": 800, "prefix": "$", "unit": "M", "label": "GTA 5"}}


def test_frames_are_full_size_and_count_up():
    base = charts._backdrop(108, 192, 1)
    early, done = charts.bars_frame(base, BARS, 0.1, 108, 192), charts.bars_frame(base, BARS, 3.0, 108, 192)
    assert early.size == done.size == (108, 192)
    assert early.tobytes() != done.tobytes()  # the bars grow
    assert charts.counter_frame(base, VS, 2.0, 108, 192).size == (108, 192)


def test_number_format():
    assert charts._fmt(68.7, 1, "", "M") == "68.7M"
    assert charts._fmt(800, 0, "$", "M") == "$800M"
    assert charts._fmt(68716978, 0) == "68,716,978"


def test_render_writes_a_video(tmp_path):
    out = charts.render(BARS, 0.4, 108, 192, tmp_path / "c.mp4")
    frames = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                             "stream=nb_read_frames", "-of", "csv=p=0", str(out)], capture_output=True, text=True)
    assert int(frames.stdout.strip()) == 12  # 0.4 s at 30 fps


def test_chart_opening_counts_as_motion():
    ep = {"short": [{"headline": "68M", "text": "One stream, sixty eight million views.", "chart": BARS}]}
    assert viewcheck.check(ep)[0] == []


def test_rights_gate_sees_shots_and_multi_short_episodes():
    ep = {"shorts": [{"id": "news", "segments": [{"text": "x", "shots": [{"media": "../media/not-registered.mp4"}]}]}]}
    checked = json.dumps(rights.check_episode(ep))
    assert "not-registered" in checked


def test_own_chart_frames_never_count_as_repost():
    from studio.vice import dedupe
    same = "-".join(["0f0f0f0f0f0f0f0f"] * 10)
    assert dedupe.overlap(same, same) == 1.0  # a real repost still matches fully
    assert dedupe.overlap(same, same, own=set(range(8))) == 0.2  # 8 of 10 frames are our charts
    assert not dedupe.is_repost(same, same, own=set(range(8)))
    assert dedupe.is_repost(same, same)


LINE = {"type": "line", "items": [["GTA 3\n2001", 95], ["GTA 5\n2013", 86], ["GTA 6\n2026", 80]], "prefix": "$",
        "floor": 70, "note": "Launch price in Oct 2026 dollars; axis starts at $70"}


def test_line_chart_draws_itself():
    base = charts._backdrop(108, 192, 2)
    early, done = charts.line_frame(base, LINE, 0.2, 108, 192), charts.line_frame(base, LINE, 3.0, 108, 192)
    assert early.size == done.size == (108, 192)
    assert early.tobytes() != done.tobytes()
    assert charts.DRAW["line"] is charts.line_frame


def test_spanish_chart_text_and_layout_repeat_warnings():
    seg = {"headline": "99", "text": "Only two games scored ninety nine.", "text_es": "Solo dos juegos.",
           "chart": {"type": "counter", "value": 99, "label": "GTA 6 on Metacritic"}}
    ep = {"short": [seg]}
    warns = viewcheck.check(ep, recent=[("other-short", ("counter",))])[1]
    assert any(w.startswith("spanish:") for w in warns)
    assert any(w.startswith("layout:") for w in warns)
    seg["chart_es"] = dict(seg["chart"], label="GTA 6 en Metacritic")
    warns = viewcheck.check(ep, recent=[("other-short", ("bars",))])[1]
    assert not any(w.startswith(("spanish:", "layout:")) for w in warns)


def test_flop_review_skips_campaign_clips_and_young_shorts():
    import datetime as dt
    from studio import flops
    now = dt.datetime(2026, 11, 24, 12, tzinfo=dt.timezone.utc)
    vids = [{"id": "a", "title": "GTA 6 tip #GTA6 #Shorts", "published": "2026-11-21T12:00:00Z", "views": 12,
             "seconds": 20, "short": True, "status": {}},
            {"id": "b", "title": "LACY vs a shark #LACY #GTA6", "published": "2026-11-21T12:00:00Z", "views": 3,
             "seconds": 15, "short": True, "status": {}},
            {"id": "c", "title": "GTA 6 new #GTA6 #Shorts", "published": "2026-11-23T12:00:00Z", "views": 4,
             "seconds": 15, "short": True, "status": {}},
            {"id": "d", "title": "GTA 6 hit #GTA6 #Shorts", "published": "2026-11-21T12:00:00Z", "views": 900,
             "seconds": 15, "short": True, "status": {}}]
    found, kept = flops.review(vids, {}, now=now)
    assert [f["id"] for f in found] == ["a"]
    assert [v["id"] for v, _ in kept] == ["b"]


def test_stale_chart_note_dates():
    import datetime as dt
    ep = {"short": [{"text": "x", "chart": {"type": "bars", "items": [["a", 1]], "note": "YouTube counts, Nov 22"},
                     "chart_es": {"type": "bars", "items": [["a", 1]], "note": "Vistas, 22 de nov."}}]}
    assert viewcheck.stale_charts(ep, today=dt.date(2026, 11, 23)) == []
    warns = viewcheck.stale_charts(ep, today=dt.date(2026, 11, 25))
    assert len(warns) == 1 and "Nov 22" in warns[0]
    assert viewcheck.note_dates("Metascore, bars start at 90", dt.date(2026, 11, 25)) == []


def test_quote_card_reveals_words_then_speaker():
    q = {"type": "quote", "text": "We did not have unlimited money or time", "pink": ["unlimited"], "who": "Someone"}
    base = charts._backdrop(108, 192, 3)
    early, done = charts.quote_frame(base, q, 0.3, 108, 192), charts.quote_frame(base, q, 3.0, 108, 192)
    assert early.size == done.size == (108, 192) and early.tobytes() != done.tobytes()
    assert charts.DRAW["quote"] is charts.quote_frame
    ep = {"short": [{"text": "x", "text_es": "y", "chart": q}]}
    assert any(w.startswith("spanish:") for w in viewcheck.check(ep, recent=[])[1])
