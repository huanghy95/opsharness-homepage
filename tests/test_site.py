import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "index.html"


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.images = []
        self.i18n_keys = set()

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "a":
            self.links.append(values)
        if tag == "img":
            self.images.append(values)
        if values.get("data-i18n"):
            self.i18n_keys.add(values["data-i18n"])


class HomepageContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = HTML.read_text(encoding="utf-8") if HTML.exists() else ""
        cls.parser = SiteParser()
        cls.parser.feed(cls.source)

    def test_required_sections_exist(self):
        expected = {
            "overview",
            "method",
            "evolution",
            "results",
            "usage",
            "abstract",
            "citation",
        }
        self.assertTrue(expected.issubset(self.parser.ids))

    def test_official_paper_links_are_exact(self):
        hrefs = {link.get("href") for link in self.parser.links}
        self.assertIn("https://arxiv.org/abs/2608.25661", hrefs)
        self.assertIn("https://arxiv.org/pdf/2608.25661", hrefs)

    def test_coming_soon_resources_are_not_links(self):
        self.assertIn('data-resource="code" aria-disabled="true"', self.source)
        self.assertIn('data-resource="demo" aria-disabled="true"', self.source)
        self.assertNotRegex(
            self.source,
            r'<a[^>]+data-resource="(?:code|demo)"',
        )

    def test_every_image_has_alt_text(self):
        self.assertGreater(len(self.parser.images), 0)
        for image in self.parser.images:
            self.assertTrue(image.get("alt", "").strip(), image)

    def test_local_assets_resolve(self):
        for image in self.parser.images:
            src = image.get("src", "")
            if src.startswith("static/"):
                self.assertTrue((ROOT / src).is_file(), src)

    def test_claims_match_the_paper(self):
        for claim in ("59.0%", "+63.4%", "4.02×", "0.83", "0.43", "0.74", "0.24"):
            self.assertIn(claim, self.source)

    def test_authors_are_complete_and_ordered(self):
        authors = [
            "Haiyu Huang",
            "Jiewei Lyu",
            "Zhihan Jiang",
            "Jinyang Liu",
            "Xiao He",
            "Tieying Zhang",
            "Wu Xiang",
            "Michael R. Lyu",
        ]
        positions = [self.source.index(author) for author in authors]
        self.assertEqual(positions, sorted(positions))


if __name__ == "__main__":
    unittest.main()
