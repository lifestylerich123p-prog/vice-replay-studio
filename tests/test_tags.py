from studio.youtube_upload import BASE_TAGS, clean_tags


def test_topic_tags_first_then_basics_without_duplicates():
    tags = clean_tags(["GTA 6 Lucia", "gta 6", "Lucia outfits"])
    assert tags[:2] == ["GTA 6 Lucia", "gta 6"]
    assert "Lucia outfits" in tags
    assert sum(t.lower() == "gta 6" for t in tags) == 1
    assert set(BASE_TAGS[1:]) <= set(tags)


def test_no_tags_falls_back_to_channel_basics():
    assert clean_tags(None) == BASE_TAGS


def test_strips_characters_youtube_rejects():
    assert clean_tags(["<GTA 6>", "#lucia"], base=[]) == ["GTA 6", "lucia"]


def test_stays_within_500_characters():
    tags = clean_tags([f"GTA 6 long keyword number {i}" for i in range(60)])
    total = sum(len(t) + (2 if " " in t else 0) for t in tags) + len(tags) - 1
    assert total <= 500
