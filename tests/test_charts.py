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
