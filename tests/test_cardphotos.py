from studio import cardphotos


def test_exact_names_win():
    assert cardphotos.exact("The Grotti Cheetah is GTA 6's fastest car")[0].startswith("car-grotti-cheetah")
    assert cardphotos.exact("How big is the GTA 6 map?") == ["leonida-map-poster"]
    assert cardphotos.pick("Ranking the Squalo boat", 0).startswith("media/official/car-squalo")


def test_video_picks_stay_in_the_vetted_pool():
    for text in ["Lucia's best outfits", "Jason in Vice City", "GTA 6 news", "bank vaults pay the most"]:
        name = cardphotos.pick(text, 0).rsplit("/", 1)[-1][:-4]
        assert name in cardphotos.SAFE, (text, name)
