"""GTA 6-style lettering cards (owner, Nov 23: lettering and a modern style, no trailer images)."""
from studio import charts, vicecards
from studio.make_video import chart_words

W, H = 216, 384  # small frames keep the test fast


def _frame(spec, t=1.0, seed=0):
    still, hz = vicecards.sky(W, H, seed)
    return vicecards.DRAW[spec["type"]](vicecards.frame_bg(still, hz, t, W, H), dict(spec, _dur=3.0), t, W, H)


def test_every_card_draws_a_full_frame():
    specs = [{"type": "kinetic", "lines": ["13 YEARS", "IT'S HERE"], "pink": ["IT'S HERE"], "sub": "x"},
             {"type": "countdown", "n": 2, "of": 4, "label": "Bigfoot is real", "sub": "the Skunk Ape"},
             {"type": "versus", "a": ["GTA 5", "32 H"], "b": ["GTA 6", "80 H"], "winner": "b"},
             {"type": "tier", "title": "T", "rows": [["S", ["a", "b"]], ["A", "c"], ["B", []]], "static": ["A"]},
             {"type": "headline", "kicker": "PLAYERS REPORT", "text": "A real Easter egg", "ticker": "tower"}]
    for spec in specs:
        for t in (0.0, 1.0, 2.8):
            im = _frame(spec, t)
            assert im.size == (W, H) and im.mode == "RGB"


def test_the_grid_moves_and_the_sky_changes_with_the_seed():
    still, hz = vicecards.sky(W, H, 0)
    a, b = vicecards.frame_bg(still, hz, 0.0, W, H), vicecards.frame_bg(still, hz, 0.7, W, H)
    assert a.tobytes() != b.tobytes()                       # the floor scrolls
    assert a.crop((0, 0, W, hz)).tobytes() == b.crop((0, 0, W, hz)).tobytes()  # the sky stays
    assert vicecards.sky(W, H, 1)[0].tobytes() != still.tobytes()


def test_static_tier_rows_show_at_once():
    spec = {"type": "tier", "rows": [["S", "new"], ["A", "old"]], "static": ["A"]}
    early, late = _frame(spec, 0.0), _frame(spec, 2.9)
    assert early.tobytes() != late.tobytes()  # the S item drops in later; the A item is there from frame one


def test_render_uses_the_vice_set_for_new_cards(tmp_path):
    out = charts.render({"type": "kinetic", "lines": ["HI"]}, 0.2, W, H, tmp_path / "k.mp4")
    assert out.exists() and out.stat().st_size > 0


def test_spanish_check_sees_the_new_card_words():
    words = chart_words({"type": "versus", "a": ["GTA 5", "32"], "b": ["GTA 6", "80"], "lines": ["WHICH ONE"],
                         "kicker": "PLAYERS REPORT"})
    assert "WHICH ONE" in words and "PLAYERS REPORT" in words and "GTA 5" in words


def test_cover_shows_the_whole_hook_on_frame_one():
    spec = {"type": "kinetic", "lines": ["VICE CITY", "IS B TIER"]}
    plain, cover = _frame(spec, 0.0), _frame(dict(spec, cover=True), 0.0)
    still, hz = vicecards.sky(W, H, 0)
    empty = vicecards.frame_bg(still, hz, 0.0, W, H)
    assert plain.tobytes() == empty.tobytes()      # without cover: nothing has landed yet
    assert cover.tobytes() != empty.tobytes()      # with cover: the hook is on the first frame


def test_pops_follow_the_lettering():
    k = vicecards.hits({"type": "kinetic", "lines": ["A", "B", "C"]}, 3.0)
    assert len(k) == 3 and k == sorted(k)
    assert len(vicecards.hits({"type": "kinetic", "lines": ["A", "B", "C"], "cover": True}, 3.0)) == 2
    tier = {"type": "tier", "rows": [["S", ["x", "y"]], ["A", "z"]], "static": ["A"]}
    assert len(vicecards.hits(tier, 3.0)) == 2
    from studio import sound
    import tempfile, pathlib
    out = sound.sfx_track(pathlib.Path(tempfile.mkdtemp()) / "s.wav", 2.0, [1.0], [0.0], pops=[0.5, 1.5])
    assert pathlib.Path(out).exists()
