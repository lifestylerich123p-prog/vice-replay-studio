"""`python -m studio.vice publish` for episodes with several Shorts ("shorts": [...]): the gate runs once per Short
(its own segments, title, description, pinned comment and render) and returns one combined result.
Offline: temp database and output folder, stubbed speech-to-text and YouTube token check."""
import json
import subprocess
from pathlib import Path

import pytest

from studio.vice import channels, db, qc, viewcheck
from studio.vice.__main__ import publish_draft

SLUG = "gta6-test-week"
CLIP_A = "../media/trailer/extended-look-aerial-bay.mp4"
CLIP_B = "../media/trailer/extended-look-avenue-skyline.mp4"
STILL = "../media/official/jason-01.jpg"


@pytest.fixture
def studio(tmp_path, monkeypatch):
    """Temp ROOT/database; the 'speech' heard in each render is whatever the test puts in heard[<file stem>]."""
    monkeypatch.setattr(db, "ROOT", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "vice.db")
    ours = channels.config()["channels"]["vice-replay"]["channel_id"]
    monkeypatch.setattr(channels, "authenticated_channel_id", lambda: ours)
    heard = {}
    monkeypatch.setattr(qc, "transcribe", lambda path, lang="en": [{"w": w, "s": 0.0, "e": 0.1, "p": 1.0}
                                                                   for w in heard[Path(path).stem].split()])
    (tmp_path / "episodes").mkdir()
    (tmp_path / "output" / SLUG).mkdir(parents=True)
    return tmp_path, heard


def segs(name, first_media=CLIP_A):
    return [{"headline": f"{name.upper()} NOW", "text": f"the {name} short opens on a moving clip", "media": first_media},
            {"headline": "TELL ME", "text": f"which {name} moment wins tell me below", "media": CLIP_B}]


def short(sid, first_media=CLIP_A, **kw):
    return {"id": sid, "title": f"GTA 6 {sid} test #Shorts", "title_options": [f"{sid} A", f"{sid} B"],
            "description": f"{sid} description", "pinned_comment": f"{sid} pinned", "segments": segs(sid, first_media), **kw}


def write_episode(root, **ep):
    ep = {"title": "GTA 6: test week", "slug": SLUG, "music": "none",
          "sources": ["https://www.rockstargames.com/newswire"],
          "segments": [{"headline": "MAIN", "text": "the main video", "media": CLIP_A}], **ep}
    p = root / "episodes" / f"{SLUG}.json"
    p.write_text(json.dumps(ep))
    return str(p)


def render(root, heard, name, segments):
    """Synthetic 1080x1920 render + timings, whose 'speech' is exactly that Short's script."""
    out = root / "output" / SLUG / f"{name}.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=1080x1920:rate=30",
                    "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000", "-t", "4", "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-ac", "2", str(out)], check=True)
    out.with_suffix(".timings.json").write_text(json.dumps([{"start": 0.0, "end": 2.0}, {"start": 2.0, "end": 4.0}]))
    heard[name] = " ".join(s["text"] for s in segments)
    return out


def qc_checks(root, name):
    return json.loads((root / "output" / SLUG / f"{name}.qc.json").read_text())["checks"]


def test_two_shorts_rendered_give_one_combined_result(studio):
    root, heard = studio
    news, tips = short("news"), short("tips", first_media=STILL, title="GTA 6 tips nobody tells you #Shorts")
    episode = write_episode(root, shorts=[news, tips])
    render(root, heard, f"{SLUG}-short-news", news["segments"])
    render(root, heard, f"{SLUG}-short-tips", tips["segments"])

    draft = publish_draft(episode, "vice-replay")

    # one result for the episode, blocked because one Short is
    assert draft["status"] == "BLOCKED"
    assert draft["blockers"] and all(b.startswith("tips: ") for b in draft["blockers"])
    still = [b for b in draft["blockers"] if "still picture" in b]
    assert len(still) == 1 and "Short 'tips'" in still[0]  # views check reported once, for its own Short
    assert any(a.startswith("tips: ") and "plain tip" in a for a in draft["advice"])
    assert not any(a.startswith("news: ") and "plain tip" in a for a in draft["advice"])
    assert json.loads((root / "output" / SLUG / "draft.json").read_text()) == draft

    # each Short gated with its own text and its own render
    by_id = {s["id"]: s for s in draft["shorts"]}
    assert list(by_id) == ["news", "tips"]
    assert by_id["news"]["status"] == "awaiting owner approval" and by_id["news"]["blockers"] == []
    assert by_id["tips"]["status"] == "BLOCKED"
    for sid in ("news", "tips"):
        s = by_id[sid]
        assert s["video"] == f"output/{SLUG}/{SLUG}-short-{sid}.mp4"
        assert s["spanish_video"] == f"output/{SLUG}/{SLUG}-short-{sid}-es.mp4"
        assert s["title_options"] == [f"{sid} A", f"{sid} B"]
        assert s["description"] == f"{sid} description" and s["pinned_comment"] == f"{sid} pinned"
        assert s["rights"] is True
        assert s["qc_report"] == f"output/{SLUG}/{SLUG}-short-{sid}.qc.md"
        assert f"--upload {sid}" in s["upload_command_after_approval"]
        captions = [c for c in qc_checks(root, f"{SLUG}-short-{sid}") if c["check"] == "captions"]
        assert captions and captions[0]["status"] == "pass"  # speech vs THIS Short's script
    assert "news,tips" in draft["upload_command_after_approval"]


def test_all_shorts_clean_awaits_owner_approval(studio):
    root, heard = studio
    news, tips = short("news"), short("tips")
    episode = write_episode(root, shorts=[news, tips])
    render(root, heard, f"{SLUG}-short-news", news["segments"])
    render(root, heard, f"{SLUG}-short-tips", tips["segments"])

    draft = publish_draft(episode, "vice-replay")

    assert draft["blockers"] == []
    assert draft["status"] == "awaiting owner approval"
    tags = [a for a in draft["advice"] if "titles/tags" in a]  # episode-level advice: once, not once per Short
    assert len(tags) == 1 and tags[0].startswith("episode: titles/tags: no `tags`")


def test_short_without_render_says_render_first_and_names_it(studio):
    root, heard = studio
    news, tips = short("news"), short("tips")
    episode = write_episode(root, shorts=[news, tips])
    render(root, heard, f"{SLUG}-short-news", news["segments"])  # tips never rendered

    with pytest.raises(SystemExit) as e:
        publish_draft(episode, "vice-replay")

    msg = str(e.value)
    assert "Render first" in msg and "'tips'" in msg and "'news'" not in msg
    assert f"python -m studio.ship {episode}" in msg
    assert not (root / "output" / SLUG / f"{SLUG}-short-news.qc.md").exists()  # stops before any QC


def test_legacy_short_next_to_shorts_is_gated_too(studio):
    root, heard = studio
    news = short("news")
    episode = write_episode(root, short=segs("main cut", first_media=STILL), short_title="GTA 6 main cut #Shorts",
                            shorts=[news])
    render(root, heard, f"{SLUG}-short", segs("main cut"))
    render(root, heard, f"{SLUG}-short-news", news["segments"])

    draft = publish_draft(episode, "vice-replay")

    assert [s["id"] for s in draft["shorts"]] == ["short", "news"]
    assert draft["shorts"][0]["video"] == f"output/{SLUG}/{SLUG}-short.mp4"
    assert draft["status"] == "BLOCKED"
    assert [b for b in draft["blockers"] if "still picture" in b] == [
        next(b for b in draft["blockers"] if b.startswith("short: views: Short 'short'"))]


def test_single_short_episode_draft_is_unchanged(studio):
    root, heard = studio
    episode = write_episode(root, short=segs("main cut", first_media=STILL), short_title="GTA 6 main cut #Shorts",
                            short_title_options=["T1", "T2"], short_description="d", pinned_comment="p",
                            short_es={"title": "GTA 6 CORTE 🔥"})
    render(root, heard, f"{SLUG}-short", segs("main cut"))

    publish_draft(episode, "vice-replay")

    draft = json.loads((root / "output" / SLUG / "draft.json").read_text())
    assert set(draft) == {"episode", "destination", "channel_check", "video", "spanish_video", "cover", "title_options",
                          "description", "pinned_comment", "qc_report", "rights", "status", "blockers", "advice",
                          "upload_command_after_approval"}
    assert draft["video"] == f"output/{SLUG}/{SLUG}-short.mp4" and draft["cover"] == f"output/{SLUG}/cover.jpg"
    assert draft["title_options"] == ["T1", "T2"]
    assert draft["status"] == "BLOCKED" and draft["blockers"][0].startswith("views: Short 'short' opens on a still")
    assert draft["upload_command_after_approval"] == f"python -m studio.ship {episode} --upload short --title N"
    ep = json.loads(Path(episode).read_text())
    assert draft["advice"] == viewcheck.check(ep)[1]  # same views + titles/tags advice viewcheck gives the episode
    assert any(a.startswith("titles/tags: Spanish versions have no tags") for a in draft["advice"])


def test_main_video_text_and_footage_checked_once_as_main(studio):
    root, heard = studio
    news = short("news")
    episode = write_episode(root, shorts=[news], segments=[
        {"headline": "PC", "text": "According to leaks, Rockstar confirmed a PC date", "media": CLIP_A},
        {"headline": "THEIRS", "text": "a clip from another creator", "media": "../media/other-creator/their-clip.mp4"}])
    render(root, heard, f"{SLUG}-short-news", news["segments"])

    draft = publish_draft(episode, "vice-replay")

    assert draft["status"] == "BLOCKED"
    main = [b for b in draft["blockers"] if b.startswith("main: ")]
    assert any(b.startswith("main: rights: media/other-creator/their-clip.mp4") for b in main)
    assert any(b.startswith("main: facts: segments[0]") for b in main)
    assert draft["main"]["rights"] is False and draft["main"]["blockers"] == [b[len("main: "):] for b in main]
    assert draft["shorts"][0]["status"] == "awaiting owner approval"  # the Short itself is clean
    assert not any("their-clip" in b or "PC date" in b for b in draft["blockers"] if not b.startswith("main: "))


def test_main_video_findings_not_repeated_under_legacy_short(studio):
    root, heard = studio
    news = short("news")
    episode = write_episode(root, short=segs("main cut"), short_title="GTA 6 main cut #Shorts", shorts=[news],
                            segments=[{"headline": "THEIRS", "text": "a clip", "media": "../media/other-creator/their-clip.mp4"}])
    render(root, heard, f"{SLUG}-short", segs("main cut"))
    render(root, heard, f"{SLUG}-short-news", news["segments"])

    draft = publish_draft(episode, "vice-replay")

    assert [b for b in draft["blockers"] if "their-clip" in b] == [
        next(b for b in draft["blockers"] if b.startswith("main: rights: media/other-creator/their-clip.mp4"))]
    assert [s["status"] for s in draft["shorts"]] == ["awaiting owner approval"] * 2


def test_shorts_episode_without_main_segments_has_no_main_check(studio):
    root, heard = studio
    news = short("news")
    episode = write_episode(root, shorts=[news], segments=[])
    render(root, heard, f"{SLUG}-short-news", news["segments"])

    draft = publish_draft(episode, "vice-replay")

    assert "main" not in draft and draft["status"] == "awaiting owner approval"
