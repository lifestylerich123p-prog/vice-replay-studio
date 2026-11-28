import datetime as dt
import unittest
from zoneinfo import ZoneInfo

from studio.ship import free_reel_time

ET = ZoneInfo("America/New_York")


def t(s):
    return dt.datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=ET)


class FreeReelTime(unittest.TestCase):
    def test_free_time_is_kept(self):
        q = [{"at": "2026-11-29 08:05", "episode": "a"}]
        self.assertEqual(free_reel_time(q, t("2026-11-29 18:05")).strftime("%H:%M"), "18:05")

    def test_taken_time_moves_later(self):
        q = [{"at": "2026-11-29 08:05", "episode": "a"}, {"at": "2026-11-29 08:20", "episode": "b"}]
        self.assertEqual(free_reel_time(q, t("2026-11-29 08:05")).strftime("%H:%M"), "08:35")

    def test_posted_and_campaign_items_do_not_block(self):
        q = [{"at": "2026-11-29 08:05", "episode": "a", "posted": "https://instagram.com/reel/x"},
             {"at": "2026-11-29 08:05", "video": "c.mp4", "campaign": "lacy"}]
        self.assertEqual(free_reel_time(q, t("2026-11-29 08:05")).strftime("%H:%M"), "08:05")


if __name__ == "__main__":
    unittest.main()
