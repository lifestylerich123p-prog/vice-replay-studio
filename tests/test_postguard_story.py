import datetime as dt
from studio.postguard import same_story

NOW = dt.datetime(2026, 11, 24, tzinfo=dt.timezone.utc)


def test_catches_the_39_million_repeat():
    recent = [("GTA 6: 39 million PS5 players in 4 days #GTA6 #Shorts", "kQ_OUxG_GYk", NOW)]
    assert same_story(["GTA 6: 39 million players on PS5, a PlayStation record #GTA6"], recent)


def test_different_stories_pass():
    recent = [("GTA 6 tier list: Vice City is only B tier #GTA6 #Shorts", "a", NOW),
              ("GTA 6 finally has patch notes: 7 fixes #GTA6 #Shorts", "b", NOW),
              ("GTA 6 is the CHEAPEST GTA ever (inflation) #GTA6 #Shorts", "c", NOW)]
    for t in ["Every GTA ranked by sales: GTA 5 is alone #GTA6 #Shorts",
              "GTA 6's Platinum trophy is already taken #GTA6 #Shorts",
              "GTA 6 Black Friday: Take-Two says no discount #GTA6 #Shorts",
              "GTA 6's first trailer STILL wins (309M views) #GTA6 #Shorts"]:
        assert same_story([t], recent) is None, t
