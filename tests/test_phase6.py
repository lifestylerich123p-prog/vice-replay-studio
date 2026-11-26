"""Phase 6 safety: affiliate links only when the account is confirmed + relevant + disclosed; our comments only on our
own public videos, once, read back from YouTube, never called pinned."""
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from studio import affiliate, comments, cycle

ACTIVE = {"enabled": True, "account_status": "active", "tag": "vicereplay-20", "heading": "GEAR (affiliate links)",
          "disclosure": "As an Amazon Associate I earn from qualifying purchases.",
          "sets": {"storage": [["PS5 storage upgrade (2TB SSD)", "https://www.amazon.com/s?k=ps5+ssd"]],
                   "deals": [["DualSense (about $54 this week)", "https://www.amazon.com/dp/X"]]}}
UNCONFIRMED = dict(ACTIVE, account_status="unconfirmed")
SSD = "PS5 storage: https://www.amazon.com/s?k=ps5+ssd&tag=vicereplay-20 (affiliate link)"


class AffiliateTest(unittest.TestCase):
    def test_unconfirmed_account_blocks_every_link(self):
        self.assertIn("unconfirmed", affiliate.check(SSD, "GTA 6 storage size: 150 GB SSD", UNCONFIRMED)[0])
        self.assertEqual(affiliate.block({"affiliate": ["storage"], "title": "GTA 6 storage size"}, UNCONFIRMED), [])
        self.assertEqual(affiliate.url("https://www.amazon.com/dp/X?tag=vicereplay-20", UNCONFIRMED),
                         "https://www.amazon.com/dp/X")

    def test_irrelevant_link_refused_even_when_active(self):
        probs = affiliate.check(SSD, "GTA 6: How to Rob ATMs With a Winch", ACTIVE)
        self.assertTrue(any("isn't about" in p for p in probs))

    def test_relevant_disclosed_link_ok_when_active(self):
        self.assertEqual(affiliate.check(SSD, "GTA 6 install size: free up SSD storage", ACTIVE), [])
        self.assertIn("disclosure", affiliate.check(SSD.replace(" (affiliate link)", ""), "GTA 6 SSD storage", ACTIVE)[0])

    def test_block_only_relevant_sets_and_no_prices(self):
        ep = {"title": "GTA 6 storage: how much space", "affiliate": ["storage", "deals"]}
        lines = affiliate.block(ep, ACTIVE)
        self.assertTrue(any("tag=vicereplay-20" in x for x in lines))
        self.assertFalse(any("$54" in x for x in lines))
        self.assertEqual(affiliate.block({"title": "GTA 6 ATM robbery guide", "affiliate": ["storage"]}, ACTIVE), [])
        self.assertEqual(affiliate.url("https://www.amazon.com/dp/X", ACTIVE), "https://www.amazon.com/dp/X?tag=vicereplay-20")

    def test_text_without_links_is_fine(self):
        self.assertEqual(affiliate.check("Winch pickup or tow truck? 👇", "ATM guide", UNCONFIRMED), [])


EN = "UCzk9Wts3WFynOHZQJRWOQIw"


def fake_req(channel=EN, owner=EN, privacy="public", existing=None, listed_after=0):
    calls = {"posted": 0, "reads": 0}

    def req(method, url, tok, body=None, **kw):
        if "channels?" in url:
            return {"items": [{"id": channel}]}, None
        if "videos?" in url:
            return {"items": [{"snippet": {"channelId": owner, "title": "GTA 6 ATM guide"},
                               "status": {"privacyStatus": privacy}}]}, None
        if method == "POST":
            calls["posted"] += 1
            return {"id": "C1"}, None
        if "commentThreads?part=snippet&id=" in url:
            calls["reads"] += 1
            if calls["reads"] <= listed_after:
                return {"items": []}, None
            return {"items": [{"snippet": {"videoId": "V1", "topLevelComment": {"snippet": {"textOriginal": "hi?"}}}}]}, None
        return {"items": [{"snippet": {"topLevelComment": {"snippet": {"authorChannelId": {"value": a},
                                                                       "textOriginal": "x"}}}} for a in (existing or [])]}, None
    return req, calls


class CommentsTest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.p = mock.patch.object(comments, "LEDGER", Path(self.d.name) / "our-comments.json")
        self.p.start()
        mock.patch.object(comments.time, "sleep", lambda s: None).start()

    def tearDown(self):
        mock.patch.stopall()
        self.d.cleanup()

    def test_wrong_token_channel(self):
        req, _ = fake_req(channel="UCother")
        with self.assertRaises(comments.Fail) as c:
            comments.preflight("V1", "en", req, tok="t")
        self.assertEqual(c.exception.step, "token")

    def test_not_our_video_or_not_public(self):
        for kw, step in (({"owner": "UCother"}, "video"), ({"privacy": "private"}, "video")):
            req, _ = fake_req(**kw)
            with self.assertRaises(comments.Fail) as c:
                comments.preflight("V1", "en", req, tok="t")
            self.assertEqual(c.exception.step, step)

    def test_existing_comment_of_ours_blocks(self):
        req, calls = fake_req(existing=[EN])
        with self.assertRaises(comments.Fail) as c:
            comments.post("V1", "Winch or tow truck?", "en", req=req, tok="t")
        self.assertEqual((c.exception.step, calls["posted"]), ("duplicate", 0))

    def test_posts_once_reads_back_and_never_claims_pinned(self):
        req, calls = fake_req(listed_after=1)  # first read-back is empty (YouTube lag)
        rec = comments.post("V1", "Winch or tow truck?", "en", req=req, tok="t")
        self.assertEqual(calls["posted"], 1)
        self.assertIn("not verified", rec["pinned"])
        with self.assertRaises(comments.Fail):  # ledger stops a second post
            comments.post("V1", "Winch or tow truck?", "en", req=req, tok="t")
        self.assertEqual(calls["posted"], 1)

    def test_irrelevant_affiliate_comment_refused_before_posting(self):
        req, calls = fake_req()
        with mock.patch.object(affiliate, "cfg", lambda: ACTIVE):
            with self.assertRaises(comments.Fail) as c:
                comments.post("V1", "Which one? " + SSD, "en", req=req, tok="t")
        self.assertEqual((c.exception.step, calls["posted"]), ("affiliate", 0))


class CycleVerdictTest(unittest.TestCase):
    def test_operational_only_when_all_pass(self):
        self.assertTrue(cycle.verdict([("a", "PASS", ""), ("b", "PASS", "")]).startswith("OPERATIONAL"))
        self.assertTrue(cycle.verdict([("a", "PASS", ""), ("b", "WAIT", "")]).startswith("NOT VERIFIED"))
        self.assertTrue(cycle.verdict([("a", "FAIL", ""), ("b", "PASS", "")]).startswith("NOT OPERATIONAL"))


if __name__ == "__main__":
    unittest.main()
