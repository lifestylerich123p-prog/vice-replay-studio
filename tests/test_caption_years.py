from studio.make_video import display_tokens


def shown(text):
    return [t for t, _, _, num in display_tokens(text.split()) if num]


def test_spoken_years_become_years():
    assert shown("Ocarina of Time, from nineteen ninety eight.") == ["1998."]
    assert shown("back in twenty thirteen") == ["2013"]
    assert shown("released in twenty twenty six") == ["2026"]
    assert shown("two thousand thirteen") == ["2013"]


def test_ordinary_numbers_unchanged():
    assert shown("fifty two hours") == ["52"]
    assert shown("eighty seven") == ["87"]
    assert shown("one hundred twenty") == ["120"]
    assert shown("ninety eight percent") == ["98%"]
    assert shown("three hundred nine million") == ["309,000,000"]
    assert shown("number one") == []
