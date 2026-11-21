"""Two chats must never post the same thing twice (studio/postguard.py)."""
import datetime as dt

from studio import postguard


def test_registry_match_blocks_same_episode_item():
    reg = {"abc123": {"slug": "gta6-quiz", "item": "short"}}
    assert "abc123" in postguard.youtube_duplicate("gta6-quiz", "short", ["New title"], reg, {})
    assert postguard.youtube_duplicate("gta6-quiz", "news", ["New title"], reg, {}) is None


def test_live_title_match_ignores_case_hashtags_and_safe_arrows():
    live = {postguard.norm("GTA 6: Settings > Gameplay fix #GTA6 #Shorts"): "vid1"}
    assert "vid1" in postguard.youtube_duplicate("s", "short", ["gta 6: settings → gameplay FIX #Shorts"], {}, live)
    assert postguard.youtube_duplicate("s", "short", ["GTA 6: a different video"], {}, live) is None


def test_instagram_duplicate_and_daily_count():
    today = dt.datetime.now(postguard.ET).replace(hour=12).strftime("%Y-%m-%dT%H:%M:%S%z")
    posted = "Only real GTA 6 fans get 4/4\n\nFour rides, one detail each. What did you score?\n#gta6"
    recent = [(postguard.caption_key(posted), "https://instagram.com/p/x", today),
              (postguard.caption_key("Old post"), "https://instagram.com/p/y", "2026-01-01T12:00:00+0000")]
    assert postguard.instagram_duplicate(posted.replace("#gta6", "#gta6 #quiz"), recent) == "https://instagram.com/p/x"
    # same first line, different post: must NOT count as a duplicate
    assert postguard.instagram_duplicate("Only real GTA 6 fans get 4/4\n\nRound two: four new rides.", recent) is None
    assert postguard.instagram_duplicate("Something new\n\nbody", recent) is None
    assert postguard.instagram_duplicate("Old post", recent) == "https://instagram.com/p/y"
    assert postguard.instagram_duplicate("", recent) is None
    assert postguard.instagram_posted_today(recent) == 1
