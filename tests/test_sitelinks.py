"""Video -> website short links (Phase 5 #11): measurable /v/ pages, noindex, UTM kept, no English page for
Spanish-channel-only Shorts."""
import tempfile
import unittest
from pathlib import Path

from studio import sitelinks


class SiteLinksTest(unittest.TestCase):
    def test_page_is_noindex_with_utm_and_canonical(self):
        ep = {"slug": "x-where", "short_title": "GTA 6 X location", "site_target": "/guides/x/#spot"}
        html = sitelinks.page(ep, "en")
        self.assertIn('name="robots" content="noindex"', html)
        self.assertIn('rel="canonical" href="https://vicereplay.com/guides/x/"', html)
        self.assertIn("utm_source=youtube&amp;utm_medium=short&amp;utm_campaign=x-where#spot", html)

    def test_spanish_path_and_line(self):
        ep = {"slug": "x-where", "site_target": "/guides/x/", "short_es": {"title": "GTA 6: X"}}
        self.assertEqual(sitelinks.short_path("x-where", "es"), "/v/x-where-es/")
        self.assertIn("/v/x-where-es/", sitelinks.line(ep, "es"))

    def test_spanish_only_episode_gets_no_english_page(self):
        es_only = [p for p in (sitelinks.ROOT / "episodes").glob("*.json")
                   if '"es_only": true' in p.read_text() and '"site_target' in p.read_text()]
        if not es_only:
            self.skipTest("no Spanish-only episode with a site target")
        with tempfile.TemporaryDirectory() as d:
            sitelinks.build(d)
            for p in es_only:
                self.assertFalse((Path(d) / "v" / p.stem / "index.html").exists(), p.stem)


if __name__ == "__main__":
    unittest.main()
