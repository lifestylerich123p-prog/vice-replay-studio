"""Tests for the second stage: framing engine, source provenance + audit, starter workflow, caption alignment,
control dashboard. Offline, temp database; uses ffmpeg, OpenCV YuNet and faster-whisper when installed."""
import json
import shutil
import sqlite3
import subprocess
from pathlib import Path

import pytest

from studio.vice import db, framing, sources, workflow

ROOT = db.ROOT
GAME = ROOT / "media" / "trailer" / "extended-look-night-street-race.mp4"
FACE = ROOT / "media" / "official" / "cal-hampton-03.jpg"
needs_cv = pytest.mark.skipif(not framing.MODEL.exists(), reason="YuNet model missing")


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "vice.db")
    yield


@pytest.fixture(scope="module")
def mock_stream(tmp_path_factory):
    d = tmp_path_factory.mktemp("stream")
    truth = framing.make_stream_mock(d / "mock.mp4", GAME, FACE, seconds=5)
    return d / "mock.mp4", truth


# ---------- framing ----------

@needs_cv
def test_detects_webcam_and_ignores_plain_gameplay(mock_stream):
    path, truth = mock_stream
    det = framing.detect_facecam(path)
    assert det and framing.iou(truth["cam"], det["box"]) > 0.85
    assert framing.detect_facecam(ROOT / "media" / "trailer" / "extended-look-walk-to-car-palms.mp4") is None


@needs_cv
def test_stack_layout_keeps_webcam_out_of_gameplay_and_logo_visible(mock_stream, tmp_path):
    path, truth = mock_stream
    det = framing.detect_facecam(path)
    info = framing.render(path, tmp_path / "s.mp4", layout="stack", cam=det["box"], keep=[truth["logo"]])
    gb, cam = info["game_box"], det["box"]
    assert gb[0] >= cam[0] + cam[2] - 0.01 or gb[0] + gb[2] <= cam[0] + 0.01  # no webcam in the gameplay panel
    out = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "json",
                                     str(tmp_path / "s.mp4")], capture_output=True, text=True).stdout)["streams"][0]
    assert (out["width"], out["height"]) == (1080, 1920)


def test_blur_layout_has_no_empty_bars(tmp_path):
    framing.render(GAME, tmp_path / "b.mp4", layout="blur", audio=False)
    err = subprocess.run(["ffmpeg", "-nostdin", "-i", str(tmp_path / "b.mp4"), "-vf", "cropdetect=24:2:0", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    w, h = map(int, err.rsplit("crop=", 1)[1].split(":")[:2])
    assert (w, h) == (1080, 1920)  # the blurred fill covers the whole frame (the starter's 'fit' left bars here)


def test_fit_box_and_tracking_expression():
    b = framing.fit_box([0.0, 0.6, 0.3, 0.3], 1080 / 768, 1920, 1080)
    assert abs(b[2] * 1920 / (b[3] * 1080) - 1080 / 768) < 0.02 and 0 <= b[0] and b[1] + b[3] <= 1.0001
    expr = framing._piecewise([(0.0, 0.5), (1.0, 0.7)], 0.3)
    assert expr.startswith("(if(lt(t,1.0)") and expr.endswith("*iw")


# ---------- provenance + audit ----------

def make_clip(path, seconds=2):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=1280x720:rate=30",
                    "-f", "lavfi", "-i", "sine=frequency=500", "-t", str(seconds), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", str(path)], check=True)
    return path


def test_source_rules_fail_closed(tmp_path):
    f = make_clip(tmp_path / "mine.mp4")
    with pytest.raises(sources.RightsError):
        sources.add(f, "me", "local://x", "owned")  # no --confirm-owned
    with pytest.raises(sources.RightsError):
        sources.add(f, "them", "https://x", "permission")  # no proof
    sid = sources.add(f, "me", "local://x", "owned", confirm_owned=True, commercial=True, youtube=True)
    con = sources.connect()
    ok, why = sources.strict_check(sources.get(con, sid), "vice-replay", con=con)
    assert ok, why
    ok, why = sources.strict_check(sources.get(con, sid), "clipcircuit", con=con)
    assert not ok and "scope" in why[0]  # destination outside the source's scope
    f.write_bytes(f.read_bytes() + b"tampered")
    ok, why = sources.strict_check(sources.get(con, sid), "vice-replay", con=con)
    assert not ok and any("hash" in w for w in why)
    with pytest.raises(sources.RightsError):  # same file can't be registered twice
        g = make_clip(tmp_path / "g.mp4")
        sources.add(g, "me", "l", "owned", confirm_owned=True)
        sources.add(g, "me", "l", "owned", confirm_owned=True)


def test_proof_change_and_missing_flags_block(tmp_path):
    f = make_clip(tmp_path / "theirs.mp4")
    proof = tmp_path / "permission.txt"
    proof.write_text("Written permission from the creator for YouTube, commercial use (test)")
    sid = sources.add(f, "creator", "https://example.com/v", "permission", proof_path=proof, commercial=True, youtube=False)
    con = sources.connect()
    ok, why = sources.strict_check(sources.get(con, sid), "vice-replay", con=con)
    assert not ok and any("YouTube" in w for w in why)
    proof.write_text("edited")
    ok, why = sources.strict_check(sources.get(con, sid), "vice-replay", con=con)
    assert any("permission/license file changed" in w for w in why)


def test_rights_audit_is_append_only(tmp_path):
    con = sources.connect()
    sources.audit(con, "x", "vice-replay", True, [], "test")
    with pytest.raises(sqlite3.DatabaseError):
        con.execute("DELETE FROM rights_audit")
    with pytest.raises(sqlite3.DatabaseError):
        con.execute("UPDATE rights_audit SET ok=0")


def test_starter_workflow_end_to_end(tmp_path, monkeypatch):
    """add-source -> add-candidate -> rank -> create-project -> render -> qc -> package, on the new engine."""
    monkeypatch.setattr(db, "ROOT", tmp_path)
    from studio.vice import editor
    monkeypatch.setattr(editor.db, "ROOT", tmp_path)
    (tmp_path / "content" / "campaigns").mkdir(parents=True)
    f = make_clip(tmp_path / "my-gameplay.mp4", 4)
    sid = sources.add(f, "Vice Replay", "local://rec-1", "owned", confirm_owned=True, commercial=True, youtube=True)
    cid, total = workflow.add_candidate(sid, "Original getaway", 0.5, 3.5,
                                        dict(curiosity=9, payoff=9, context=8, audio=8, visuals=9, originality=9))
    assert total == 87  # 22.5+22.5+12+12+9+9
    ranked = workflow.rank()
    assert ranked[0]["rights_approved"] and ranked[0]["candidate_id"] == cid
    pid = workflow.create_project(cid, headline="My getaway")
    p, params = workflow.project_params(pid)
    params["layout"] = "blur"
    monkeypatch.setattr(editor.qc, "transcribe", lambda path: [{"w": "test", "s": 0.1, "e": 0.4, "p": 0.4}])
    p = editor.build(pid, params)
    out = tmp_path / "projects" / pid
    assert (out / f"{pid}.mp4").stat().st_size > 10000
    draft = json.loads((out / "draft.json").read_text())
    assert any("captions not reviewed" in b for b in draft["blockers"])  # review gate before publishing
    assert "Uncertain words" in (out / "captions_review.md").read_text()


# ---------- caption alignment ----------

@pytest.mark.skipif(shutil.which("espeak-ng") is None and not (ROOT / "assets" / "voice").exists(), reason="no TTS")
def test_alignment_matches_script_words(tmp_path):
    from studio import make_video as mv
    text = "Look at the corner of this GTA 6 street race."
    audio = mv.tts(text, "am_michael", "+10%", tmp_path / "vo")
    times = mv.align_words(text, audio, "en")
    assert times and len(times) == len(text.split())
    assert all(b[0] >= a[0] for a, b in zip(times, times[1:]))  # monotonic
    assert times[-1][1] <= mv.duration(audio) + 0.3


# ---------- control dashboard ----------

def test_control_allowlist_and_recovery():
    from studio.vice import control
    with pytest.raises(ValueError):
        control.enqueue("upload", "x")
    with pytest.raises(ValueError):
        control.enqueue("render", "../../etc")
    jid = control.enqueue("report", "")
    c = control.con()
    c.execute("UPDATE jobs SET status='running' WHERE id=?", (jid,))
    c.commit()
    assert control.recover() == 1
    assert control.con().execute("SELECT status FROM jobs WHERE id=?", (jid,)).fetchone()["status"] == "queued"
    assert "Vice Replay Control" in control.page()


def _webcam_stream(path, src):
    """Top 40%: the same still 'webcam room' in every clip; bottom: moving gameplay from `src`."""
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "lavfi", "-i", "smptehdbars=size=1080x768:rate=30",
                    "-f", "lavfi", "-i", f"{src}=size=1080x1152:rate=30", "-filter_complex", "[0:v][1:v]vstack=2[v]",
                    "-map", "[v]", "-t", "8", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path)], check=True)
    return path


def test_same_webcam_different_gameplay_is_not_a_repost(tmp_path):
    from studio.vice import dedupe
    a = _webcam_stream(tmp_path / "a.mp4", "testsrc2")
    b = _webcam_stream(tmp_path / "b.mp4", "mandelbrot")
    a2 = tmp_path / "a2.mp4"  # same footage, re-encoded smaller with a brightness tweak = a repost
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(a), "-vf", "scale=720:1280,eq=brightness=0.03",
                    "-c:v", "libx264", "-crf", "30", str(a2)], check=True)
    ha, hb, ha2 = (dedupe.video_hash(x) for x in (a, b, a2))
    sa, sb, sa2 = (dedupe.motion_sig(x) for x in (a, b, a2))
    assert dedupe.is_repost(ha, ha2, sa, sa2)
    assert not dedupe.is_repost(ha, hb, sa, sb)


def test_still_image_shot_finishes_and_pans(tmp_path):
    """Nov 21 regression: a .jpg inside "shots" used -stream_loop, whose timestamps never advance, so ffmpeg ran
    forever. Stills must render to the requested length quickly, and drift (not sit frozen)."""
    import numpy as np
    from PIL import Image
    from studio import make_video as mv
    img = tmp_path / "still.jpg"
    Image.fromarray((np.random.default_rng(1).random((360, 640, 3)) * 255).astype("uint8")).save(img)
    seg = {"shots": [{"media": str(img), "focus": 0.5, "dur": 1.5}]}
    out = mv.shots_background(0, seg, 1.2, 270, 480, tmp_path, tmp_path)
    assert abs(mv.duration(out) - 1.5) < 0.2
    f = [tmp_path / f"f{n}.png" for n in (1, 40)]
    for n, p in zip((1, 40), f):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(out), "-vf", f"select=eq(n\\,{n})", "-frames:v", "1", str(p)], check=True)
    a, b = (np.asarray(Image.open(p).convert("L"), dtype=float) for p in f)
    assert np.abs(a - b).mean() > 1.0  # the picture moved


def test_quiz_giveaway_is_blocked(tmp_path):
    """Nov 21 regression: a quiz 'guess' zoom that shows the answer word (the 'Cheetah' badge) must block publishing."""
    pytest.importorskip("rapidocr")
    from PIL import Image, ImageDraw, ImageFont
    from studio.vice import quizcheck
    img = Image.new("RGB", (1600, 900), (230, 230, 235))
    d = ImageDraw.Draw(img)
    d.text((420, 330), "CHEETAH", font=ImageFont.truetype("assets/fonts/Anton.ttf", 170), fill=(20, 20, 20))
    img.save(tmp_path / "car.jpg")
    ep = {"format": "quiz", "short": [
        {"headline": "GUESS #1", "text": "Number one: a famous badge.", "media": "car.jpg",
         "magnify": {"box": [0.2, 0.3, 0.8, 0.65]}},
        {"headline": "GROTTI CHEETAH", "text": "The Grotti Cheetah.", "media": "car.jpg"}]}
    (tmp_path / "ep.json").write_text(json.dumps(ep))
    found = quizcheck.problems(ep, tmp_path / "ep.json", tmp_path / "none.mp4", None)
    assert found and "cheetah" in found[0]
    ep["short"][0]["magnify"]["box"] = [0.0, 0.7, 0.2, 0.95]  # an empty corner: nothing to read
    assert quizcheck.problems(ep, tmp_path / "ep.json", tmp_path / "none.mp4", None) == []


def test_caption_numbers_become_digits_only_when_clearly_numbers():
    from studio.make_video import display_tokens
    show = lambda t: " | ".join(x[0] for x in display_tokens(t.split()))
    assert show("IShowSpeed beat GTA 6 in one stream. Fifty two hours.") == "IShowSpeed | beat | GTA 6 | in | one | stream. | 52 | hours."
    assert show("his ninety eight percent save") == "his | 98% | save"
    assert show("Number four: this one floats.") == "Number | four: | this | one | floats."
    assert show("only three hundred forty five feet.") == "only | 345 | feet."
    assert show("GTA 5 vs GTA 6") == "GTA 5 | vs | GTA 6"


def test_animated_captions_never_overlap(tmp_path, monkeypatch):
    import re as _re
    from studio import make_video as mv
    monkeypatch.setenv("VR_CAPTIONS", "animated")
    text = "IShowSpeed beat GTA 6 in one stream. Fifty two hours and thirty one minutes, live."
    words = text.split()
    times = [(0.1 + i * 0.3, 0.1 + i * 0.3 + 0.45) for i in range(len(words))]  # deliberately overlapping words
    f = mv.caption_file(text, 0.2, 6, tmp_path / "c.ass", 1080, 1920, True, times=times)
    ev = [l.split(",", 3) for l in f.read_text().splitlines() if l.startswith("Dialogue:")]
    def secs(t):
        h, m, s = t.split(":"); return int(h) * 3600 + int(m) * 60 + float(s)
    spans = [(secs(e[1]), secs(e[2])) for e in ev]
    assert all(a[1] <= b[0] + 1e-6 for a, b in zip(spans, spans[1:]))
    body = f.read_text()
    assert "52" in body and "&H8E1FFF&" in body and _re.search(r"\\t\(0,80", body)


def test_spanish_captions_keep_number_words():
    from studio.make_video import display_tokens
    es = [t[0] for t in display_tokens("Ten cuidado con GTA 6, tiene cincuenta y dos horas.".split(), "es")]
    assert es[0] == "Ten" and "GTA 6," in es and "10" not in es
    assert [t[0] for t in display_tokens("ten hours".split())] == ["10", "hours"]
