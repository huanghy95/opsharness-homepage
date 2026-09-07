import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "index.html"


def contrast_ratio(foreground, background):
    def luminance(value):
        channels = [int(value[index:index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [
            channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
            for channel in channels
        ]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    light, dark = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.images = []
        self.i18n_keys = set()
        self.i18n_aria_keys = set()

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
        if values.get("data-i18n-aria-label"):
            self.i18n_aria_keys.add(values["data-i18n-aria-label"])


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
            if "data-lightbox-target" in image:
                self.assertEqual(image.get("alt"), "")
                continue
            self.assertTrue(image.get("alt", "").strip(), image)

    def test_paper_figures_are_lazy_and_reserve_layout_space(self):
        paper_images = [image for image in self.parser.images if "data-lightbox-target" not in image]
        for image in paper_images:
            self.assertEqual(image.get("loading"), "lazy", image.get("src"))
            self.assertEqual(image.get("decoding"), "async", image.get("src"))
            self.assertTrue(image.get("width", "").isdigit(), image.get("src"))
            self.assertTrue(image.get("height", "").isdigit(), image.get("src"))

    def test_local_assets_resolve(self):
        for image in self.parser.images:
            src = image.get("src", "")
            if src.startswith("static/"):
                self.assertTrue((ROOT / src).is_file(), src)

    def test_raster_asset_extensions_match_their_file_signatures(self):
        for asset in (ROOT / "static/images").iterdir():
            if asset.suffix == ".png":
                self.assertEqual(asset.read_bytes()[:8], b"\x89PNG\r\n\x1a\n", asset.name)
            if asset.suffix in {".jpg", ".jpeg"}:
                self.assertEqual(asset.read_bytes()[:2], b"\xff\xd8", asset.name)
            if asset.suffix == ".webp":
                signature = asset.read_bytes()[:12]
                self.assertEqual(signature[:4], b"RIFF", asset.name)
                self.assertEqual(signature[8:], b"WEBP", asset.name)

    def test_deployable_figure_payload_is_web_sized(self):
        extensions = {".png", ".jpg", ".jpeg", ".webp"}
        assets = [asset for asset in (ROOT / "static/images").iterdir() if asset.suffix in extensions]
        self.assertLess(sum(asset.stat().st_size for asset in assets), 2_500_000)

    def test_favicon_is_declared_and_resolves(self):
        favicon = "static/images/favicon.svg"
        self.assertIn(f'<link rel="icon" href="{favicon}" type="image/svg+xml">', self.source)
        self.assertTrue((ROOT / favicon).is_file())

    def test_claims_match_the_paper(self):
        for claim in ("59.0%", "+63.4%", "4.02×", "0.83", "0.43", "0.74", "0.24"):
            self.assertIn(claim, self.source)

    def test_incident_story_does_not_merge_distinct_paper_cases(self):
        catalog_source = (ROOT / "static/js/i18n.js").read_text(encoding="utf-8")
        combined = self.source + catalog_source
        for conflated_claim in (
            "under two minutes",
            "ranks the true CPU saturation only third",
            "Feedback: Top-3 is correct",
            "Proposal: atomic + reviewable",
            "Result: Top-1 diagnosis",
            "evolved harness reuses verified experience",
            "两分钟内",
        ):
            self.assertNotIn(conflated_claim, combined)
        self.assertIn("The SRE records the CPU-to-RemoteProcess propagation chain", self.source)
        self.assertIn("the recorded experience leads the SRE", self.source)

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

    def test_css_has_responsive_and_accessibility_contracts(self):
        css_path = ROOT / "static/css/style.css"
        self.assertTrue(css_path.is_file())
        css = css_path.read_text(encoding="utf-8")
        for token in ("--violet", "--verified", "--paper", "--ink", "--mono"):
            self.assertIn(token, css)
        self.assertIn("@media (max-width: 760px)", css)
        self.assertIn("prefers-reduced-motion: reduce", css)
        self.assertIn(":focus-visible", css)

    def test_terminal_secondary_text_meets_wcag_aa_contrast(self):
        css = (ROOT / "static/css/style.css").read_text(encoding="utf-8")
        comment = re.search(r"\.code-comment\s*\{[^}]*color:\s*(#[0-9a-fA-F]{6})", css, re.S)
        inactive_tab = re.search(r"(?m)^\.usage-tab \{([^}]*)\}", css, re.S)
        self.assertIsNotNone(comment)
        self.assertIsNotNone(inactive_tab)
        tab_color = re.search(r"color:\s*(#[0-9a-fA-F]{6})", inactive_tab.group(1))
        self.assertIsNotNone(tab_color)
        self.assertGreaterEqual(contrast_ratio(comment.group(1), "#101014"), 4.5)
        self.assertGreaterEqual(contrast_ratio(tab_color.group(1), "#18171c"), 4.5)

    def test_every_markup_i18n_key_has_both_languages(self):
        js_path = ROOT / "static/js/i18n.js"
        self.assertTrue(js_path.is_file())
        js = js_path.read_text(encoding="utf-8")
        match = re.search(r"window\.OPSHARNESS_I18N\s*=\s*(\{.*\});", js, re.S)
        self.assertIsNotNone(match)
        catalog = json.loads(match.group(1))
        self.assertEqual(set(catalog), {"en", "zh"})
        self.assertEqual(set(catalog["en"]), set(catalog["zh"]))
        self.assertGreater(len(self.parser.i18n_keys), 40)
        markup_keys = self.parser.i18n_keys | self.parser.i18n_aria_keys
        self.assertTrue(markup_keys.issubset(catalog["en"]))

    def test_no_javascript_fallback_shows_both_usage_examples(self):
        self.assertNotRegex(self.source, r'id="claude-panel"[^>]*\shidden(?:\s|>)')
        self.assertIn('<h3 class="fallback-panel-label">Codex</h3>', self.source)
        self.assertIn('<h3 class="fallback-panel-label">Claude Code</h3>', self.source)
        js = (ROOT / "static/js/main.js").read_text(encoding="utf-8")
        self.assertIn("panel.hidden = !selected", js)
        self.assertIn("tabs.find", js)
        self.assertIn("activate(selectedTab)", js)

    def test_copy_feedback_has_a_live_region(self):
        self.assertIn('role="status" aria-live="polite" data-copy-status', self.source)
        js = (ROOT / "static/js/main.js").read_text(encoding="utf-8")
        self.assertIn('querySelector("[data-copy-status]")', js)

    def test_interaction_hooks_and_fallbacks_exist(self):
        js_path = ROOT / "static/js/main.js"
        self.assertTrue(js_path.is_file())
        js = js_path.read_text(encoding="utf-8")
        for contract in (
            "localStorage",
            "IntersectionObserver",
            "navigator.clipboard",
            "prefers-reduced-motion",
            "Escape",
            "aria-expanded",
            "aria-selected",
            'event.key === "Tab"',
            'setAttribute("inert"',
            'removeAttribute("inert"',
        ):
            self.assertIn(contract, js)

    def test_interactive_controls_are_labeled(self):
        for attribute in (
            "data-language-toggle",
            "data-nav-toggle",
            'role="tablist"',
            "data-copy-target",
            'role="dialog"',
            'aria-modal="true"',
        ):
            self.assertIn(attribute, self.source)

    def test_readme_documents_preview_and_validation(self):
        readme_path = ROOT / "README.md"
        self.assertTrue(readme_path.is_file())
        readme = readme_path.read_text(encoding="utf-8")
        self.assertIn("python3 -m http.server 8000", readme)
        self.assertIn("python3 -m unittest discover -s tests -v", readme)
        self.assertIn("python3 tests/browser_qa.py", readme)
        self.assertIn("https://arxiv.org/abs/2608.25661", readme)
        self.assertTrue((ROOT / "tests/browser_qa.py").is_file())


if __name__ == "__main__":
    unittest.main()
