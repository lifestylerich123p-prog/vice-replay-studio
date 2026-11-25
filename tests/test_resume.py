"""studio/make_video.py resume: a restarted render reuses a card only when its inputs match and its clip is whole."""
import json
import subprocess

from studio import cardphotos, make_video as mv


def _clip(path, secs):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=black:s=64x64:d={secs}",
                    "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo", "-t", str(secs), "-c:v", "libx264",
                    "-c:a", "aac", "-shortest", str(path)], check=True)


def test_resume_hit_only_on_same_key_and_whole_clip(tmp_path, monkeypatch):
    monkeypatch.delenv("VR_NO_RESUME", raising=False)
    clip = tmp_path / "seg_03.mp4"
    _clip(clip, 2)
    mv.resume_save(tmp_path, 3, "k1", clip, 2.0, [0.5], ["media/official/a.jpg"])
    hit = mv.resume_hit(tmp_path, 3, "k1")
    assert hit and abs(hit["d"] - 2.0) < 0.01 and hit["hits"] == [0.5] and hit["photos"] == ["media/official/a.jpg"]
    assert mv.resume_hit(tmp_path, 3, "other-key") is None          # inputs changed: render again
    monkeypatch.setenv("VR_NO_RESUME", "1")
    assert mv.resume_hit(tmp_path, 3, "k1") is None                 # switched off
    monkeypatch.delenv("VR_NO_RESUME")
    _clip(clip, 1)                                                   # clip shorter than recorded (crash mid-write)
    assert mv.resume_hit(tmp_path, 3, "k1") is None


def test_segment_key_tracks_spec_and_used_photos():
    cardphotos.reset()
    seg = {"headline": "X", "text": "hello", "chart": {"type": "text", "text": "hi"}}
    k1 = mv.segment_key(0, seg, 1920, 1080, False, ["-c:v", "libx264"], "af_heart", 1.0)
    assert k1 == mv.segment_key(0, dict(seg), 1920, 1080, False, ["-c:v", "libx264"], "af_heart", 1.0)
    assert k1 != mv.segment_key(0, {**seg, "text": "changed"}, 1920, 1080, False, ["-c:v", "libx264"], "af_heart", 1.0)
    cardphotos.mark_used(["media/official/b.jpg"])                   # an earlier card took a picture
    assert k1 != mv.segment_key(0, seg, 1920, 1080, False, ["-c:v", "libx264"], "af_heart", 1.0)
    cardphotos.reset()


def test_follow_badge_language_follows_the_render_not_matching_lines():
    """Nov 25: an English quiz Short with answers that read the same in Spanish got the Spanish badge."""
    import inspect
    src = inspect.getsource(mv.build)
    assert 'langs = {s.get("_lang")' in src and "all(s.get(\"text\") == s.get(\"text_es\")" in src
