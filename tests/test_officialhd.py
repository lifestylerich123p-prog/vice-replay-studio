from pathlib import Path

from studio import mappins, officialhd


def test_unknown_files_fall_back_to_the_original():
    assert officialhd.best("media/official/not-a-shot.jpg") == Path("media/official/not-a-shot.jpg")


def test_every_mapped_name_is_one_of_our_screenshots():
    root = Path(__file__).resolve().parent.parent
    names = set(officialhd.mapping())
    assert names and all((root / "media" / "official" / n).exists() for n in names)


def test_spread_pushes_overlapping_pins_apart():
    a, b = mappins._spread([(100, 100), (101, 100)], gap=50)
    assert ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5 >= 49
