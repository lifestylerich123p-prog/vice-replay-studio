from studio import cardphotos


def test_exact_names_win():
    assert cardphotos.exact("The Grotti Cheetah is GTA 6's fastest car")[0].startswith("car-grotti-cheetah")
    assert cardphotos.exact("How big is the GTA 6 map?") == ["leonida-map-poster"]
    assert cardphotos.pick("Ranking the Squalo boat", 0).startswith("media/official/car-squalo")


def test_video_picks_stay_in_the_vetted_pool():
    for text in ["Lucia's best outfits", "Jason in Vice City", "GTA 6 news", "bank vaults pay the most"]:
        name = cardphotos.pick(text, 0).rsplit("/", 1)[-1][:-4]
        assert name in cardphotos.SAFE, (text, name)


def test_photo_background_is_darkened_and_zooms():
    from studio import charts
    base = charts._photo_base("media/official/car-grotti-cheetah-01.jpg", 108, 192)
    assert base.size == (int(108 * charts.ZOOM), int(192 * charts.ZOOM))
    first, last = charts._photo_frame(base, 0, 108, 192), charts._photo_frame(base, 1, 108, 192)
    assert first.size == last.size == (108, 192) and first.tobytes() != last.tobytes()
    assert charts._photo_base("media/official/missing.jpg", 108, 192) is None


def test_no_repeat_within_a_video():
    cardphotos.reset()
    picks = [cardphotos.pick("GTA 6 news", i) for i in range(6)]
    assert len(set(picks)) == len(picks)


def test_map_poster_is_not_a_video_background():
    assert "leonida-map-poster" not in cardphotos.SAFE


def test_hook_card_punches_in():
    from studio import charts
    base = charts._photo_base("media/official/car-grotti-cheetah-01.jpg", 108, 192)
    a = charts._photo_frame(base, 0.0, 108, 192, t=0.0, hook=True)
    b = charts._photo_frame(base, 0.1, 108, 192, t=0.45, hook=True)
    assert a.tobytes() != b.tobytes()


def test_duplicate_slab_is_dropped_on_the_hook():
    from studio.make_video import _said_by_card
    assert _said_by_card("A REAL UFO", {"type": "kinetic", "lines": ["GTA 6 HAS", "A REAL UFO"]})
    assert not _said_by_card("JASON'S SECRET", {"type": "text", "text": "Jason was inspired by Steve McQueen"})
