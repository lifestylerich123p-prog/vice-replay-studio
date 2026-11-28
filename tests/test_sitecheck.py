import json
import tempfile
import unittest
from pathlib import Path

from studio.sitecheck import check_pins, check_site

D = "https://vicereplay.com"


def page(title, canon, extra="", alts=""):
    return (f'<html><head><meta name="viewport" content="width=device-width"><title>{title}</title>'
            f'<meta name="description" content="d"><link rel="canonical" href="{D}{canon}">{alts}</head>'
            f'<body>{extra}<footer>As an Amazon Associate I earn from qualifying purchases.</footer></body></html>')


class SiteCheck(unittest.TestCase):
    def build(self, pages, sitemap):
        tmp = Path(tempfile.mkdtemp())
        for path, doc in pages.items():
            f = tmp / path.lstrip("/") / "index.html" if path.endswith("/") else tmp / path.lstrip("/")
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(doc)
        (tmp / "sitemap.xml").write_text("".join(f"<url><loc>{D}{u}</loc></url>" for u in sitemap))
        return tmp

    def test_clean_site_has_no_problems(self):
        alt = lambda: (f'<link rel="alternate" hreflang="en" href="{D}/guides/a/">'
                       f'<link rel="alternate" hreflang="es" href="{D}/es/guias/a/">')
        site = self.build({"/": page("Home", "/", '<a href="/guides/a/">a</a>'),
                           "/guides/a/": page("A", "/guides/a/", alts=alt()),
                           "/es/guias/a/": page("A es", "/es/guias/a/", alts=alt())},
                          ["/", "/guides/a/", "/es/guias/a/"])
        r = check_site(site)
        self.assertEqual(r["problems"], [])
        self.assertEqual(r["indexable"], 3)

    def test_broken_link_missing_hreflang_and_untagged_amazon(self):
        site = self.build({"/": page("Home", "/", '<a href="/guides/gone/">x</a>'
                                     '<a href="https://www.amazon.com/dp/B0TEST">buy</a>'
                                     '<a href="https://amzn.to/abc">short</a>',
                                     alts=f'<link rel="alternate" hreflang="es" href="{D}/es/missing/">')}, ["/"])
        text = " | ".join(check_site(site)["problems"])
        self.assertIn("broken link / -> /guides/gone/", text)
        self.assertIn("hreflang es on / points to a missing page", text)
        self.assertIn("without tag=vicereplay-20", text)
        self.assertIn("not a direct amazon.com link", text)

    def test_non_reciprocal_hreflang_and_secret(self):
        site = self.build({"/guides/a/": page("A", "/guides/a/",
                                              alts=f'<link rel="alternate" hreflang="es" href="{D}/es/guias/a/">'),
                           "/es/guias/a/": page("A es", "/es/guias/a/", alts="<!-- no link back -->"),
                           "/js/x.js": 'const k = "AIza' + "A" * 35 + '";'}, ["/guides/a/", "/es/guias/a/"])
        text = " | ".join(check_site(site)["problems"])
        self.assertIn("hreflang not reciprocal", text)
        self.assertIn("secret-looking string", text)

    def test_cut_claim_on_site_is_a_problem(self):
        import studio.sitecheck as sc
        tmp = Path(tempfile.mkdtemp())
        (tmp / "content" / "learn").mkdir(parents=True)
        (tmp / "content" / "learn" / "cut-claims.json").write_text(json.dumps({"claims": [{"phrase": "Benny Moré"}]}))
        site = self.build({"/": page("Home", "/", "<p>On the radio: Benny Mor&eacute;</p>")}, ["/"])
        old, sc.ROOT = sc.ROOT, tmp
        try:
            text = " | ".join(check_site(site)["problems"])
        finally:
            sc.ROOT = old
        self.assertIn("cut claim still on the site: 'Benny Moré'", text)

    def test_pins_need_two_sources_unless_official(self):
        f = Path(tempfile.mkdtemp()) / "pins.json"
        f.write_text(json.dumps({"cats": [{"id": "eggs"}, {"id": "places"}], "pins": [
            {"cat": "places", "at": "Vice City", "src": ["Rockstar Games"], "en": {"t": "Vice City"}, "es": {"t": "VC"}},
            {"cat": "eggs", "at": "G7", "src": ["one guide"], "en": {"t": "Egg"}, "es": {"t": "Huevo"}},
            {"cat": "nope", "at": "G8", "src": ["a", "b"], "en": {"t": "X"}, "es": {"t": "X"}}]}))
        out = " | ".join(check_pins(f))
        self.assertNotIn("Vice City", out)
        self.assertIn("map pin Egg: 1 source(s)", out)
        self.assertIn("unknown category nope", out)


if __name__ == "__main__":
    unittest.main()
