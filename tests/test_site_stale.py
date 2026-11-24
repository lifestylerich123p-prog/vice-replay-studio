from studio.site_stale import scan


def _page(root, rel, body):
    d = root / rel
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(f"<html><body>{body}</body></html>")


def test_flags_prelaunch_wording(tmp_path):
    _page(tmp_path, "guides/old", "<p>GTA 6 comes out on November 19, 2026.</p>")
    _page(tmp_path, "es/guias/vieja", "<p>GTA 6 sale el 19 de noviembre de 2026.</p>")
    _page(tmp_path, "guides/fresh", "<p>GTA 6 came out on November 19, 2026.</p>")
    pages = {p for p, _ in scan(tmp_path)}
    assert pages == {"guides/old/", "es/guias/vieja/"}


def test_page_with_update_note_is_skipped(tmp_path):
    _page(tmp_path, "guides/kept", '<div class="note update">GTA 6 is out.</div><p>GTA 6 comes out on November 19.</p>')
    assert scan(tmp_path) == []


def test_scripts_and_styles_are_ignored(tmp_path):
    _page(tmp_path, "x", "<script>var s='comes out on';</script><p>fine</p>")
    assert scan(tmp_path) == []
