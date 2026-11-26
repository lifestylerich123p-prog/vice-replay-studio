"""Phase 4 #5: every media file has a rights record; blocked sources used by an episode fail the check."""
from studio import provenance

REG = [{"id": "rockstar-official-screens", "match": ["media/official/*"], "status": "conditional", "owner": "Rockstar"},
       {"id": "official-music", "match": ["music:gta6-official"], "status": "blocked"},
       {"id": "site", "match": ["media/site/*"], "status": "conditional"}]


def test_record_lookup():
    assert provenance.record_for("media/official/vice-beach-02.jpg", REG)["id"] == "rockstar-official-screens"
    assert provenance.record_for("media/site/map-demo-shoe-en.mp4", REG)["id"] == "site"
    assert provenance.record_for("media/downloads/someone-elses-clip.mp4", REG) is None


def test_real_manifest_has_no_unregistered_file_in_use():
    res = provenance.build()
    used = {x["file"] for x in res["files"] if x["episodes"]}
    assert not (used & set(res["unregistered"])) and not res["blocked_in_use"]
