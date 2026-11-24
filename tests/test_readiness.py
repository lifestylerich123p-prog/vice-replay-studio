from studio import readiness


def test_missing_render_is_reported(tmp_path):
    assert readiness.check(tmp_path / "nope.mp4") == "not rendered"


def test_booked_rows_are_sorted_and_have_paths():
    rows = readiness.booked()
    assert rows == sorted(rows)
    assert all(str(p).endswith(".mp4") for *_, p in rows)
