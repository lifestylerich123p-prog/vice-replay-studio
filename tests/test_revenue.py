"""Associates Central report import (owner Phase 8 #11). Synthetic fixtures only: never real revenue."""
import datetime as dt
import tempfile
import unittest
from pathlib import Path

from studio import revenue

EARN = """Fee-Earnings reports from 11-01-2026 to 11-26-2026
Category,Name,ASIN,Seller,Tracking ID,Date Shipped,Price($),Items Shipped,Returns,Revenue($),Ad Fees($),Device Type Group,Direct
Electronics,Example SSD,B0TESTSSD1,Amazon.com,vicereplay-20,2026-11-24 10:00:00,100.00,1,0,100.00,3.00,DESKTOP,Y
Electronics,Example SSD,B0TESTSSD1,Amazon.com,vicereplay-20,2026-11-25 10:00:00,100.00,1,1,0.00,0.00,PHONE,Y
"""
ORDERS = """Fee-Orders reports from 11-01-2026 to 11-26-2026
Category,Name,ASIN,Date,Qty,Price($),Link Type,Tag,Indirect Sales,Device Type Group
Electronics,Example SSD,B0TESTSSD1,2026-11-23 09:00:00,2,100.00,Text,vicereplay-20,No,DESKTOP
Electronics,Example SSD,B0TESTSSD1,2026-12-30 09:00:00,1,100.00,Text,vicereplay-20,No,DESKTOP
"""


class RevenueTest(unittest.TestCase):
    def _file(self, text):
        f = Path(self.d.name) / f"r{len(list(Path(self.d.name).iterdir()))}.csv"
        f.write_text(text)
        return f

    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.led = {"imports": {}, "records": {}}

    def tearDown(self):
        self.d.cleanup()

    def test_earnings_are_shipped_minus_returns_and_orders_stay_separate(self):
        today = dt.date(2026, 11, 26)
        revenue.import_file(self._file(EARN), self.led, today, write=False)
        r = revenue.import_file(self._file(ORDERS), self.led, today, write=False)
        self.assertTrue(any("future" in p or "outside" in p for p in r["problems"]))  # Dec 30 row refused
        s = revenue.summary(self.led)
        self.assertEqual((s["shipped"], s["returned"], s["ordered"]), (2, 1, 2))
        self.assertEqual(s["verified_earnings_usd"], 3.0)

    def test_same_file_twice_is_refused(self):
        f = self._file(EARN)
        revenue.import_file(f, self.led, dt.date(2026, 11, 26), write=False)
        with self.assertRaises(ValueError):
            revenue.import_file(f, self.led, dt.date(2026, 11, 26), write=False)

    def test_nothing_imported_means_unavailable(self):
        self.assertIsNone(revenue.summary(self.led))

    def test_not_a_report(self):
        with self.assertRaises(ValueError):
            revenue.parse("hello,world\n1,2\n")


if __name__ == "__main__":
    unittest.main()
