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


def result_row(source, backbone, framework):
    body = re.search(
        rf'<tbody data-backbone="{re.escape(backbone)}".*?</tbody>',
        source,
        re.S,
    )
    if body is None:
        return []
    row = re.search(
        rf'<tr[^>]*data-framework="{re.escape(framework)}"[^>]*>.*?</tr>',
        body.group(0),
        re.S,
    )
    if row is None:
        return []
    cells = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row.group(0), re.S)
    return [
        re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", cell)).strip()
        for cell in cells
    ]


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
        cls.i18n_source = (ROOT / "static/js/i18n.js").read_text(encoding="utf-8")
        cls.parser = SiteParser()
        cls.parser.feed(cls.source)

    def test_custom_domain_metadata_matches_pages_configuration(self):
        self.assertEqual((ROOT / "CNAME").read_text().strip(), "opsharness.org")
        self.assertIn('<link rel="canonical" href="https://opsharness.org/">', self.source)
        self.assertIn('<meta property="og:url" content="https://opsharness.org/">', self.source)
        self.assertIn(
            'content="https://opsharness.org/static/images/intro-superpowers.webp"',
            self.source,
        )

    def test_required_sections_exist(self):
        expected = {
            "overview",
            "method",
            "results",
            "usage",
            "abstract",
            "citation",
        }
        self.assertTrue(expected.issubset(self.parser.ids))
        self.assertNotIn("evolution", self.parser.ids)

    def test_reviewed_hero_and_affiliations_are_exact(self):
        self.assertIn(
            "OpsHarness: <em>A Self-Evolving Harness</em> for Root Cause Analysis",
            self.source,
        )
        for capability in ("Skills", "Knowledge", "Tools", "Verification", "Self-Evolve"):
            self.assertIn(f"<span>{capability}</span>", self.source)
        self.assertNotIn("Individual Researcher", self.source)
        self.assertIn(
            "The Chinese University of Hong Kong · ByteDance",
            self.source,
        )

    def test_official_paper_links_are_exact(self):
        hrefs = {link.get("href") for link in self.parser.links}
        self.assertIn("https://arxiv.org/abs/2608.25661", hrefs)
        self.assertIn("https://arxiv.org/pdf/2608.25661", hrefs)

    def test_official_title_is_preserved_in_metadata_and_bibtex(self):
        official = (
            "From General Agents to RCA Experts: "
            "A Self-Evolving Harness for Root Cause Analysis"
        )
        self.assertIn(f"<title>{official}</title>", self.source)
        self.assertIn(f'<meta property="og:title" content="{official}">', self.source)
        self.assertIn(f'<meta name="twitter:title" content="{official}">', self.source)
        self.assertIn(f"title={{{official}}}", self.source)

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

    def test_motivation_and_self_evolution_use_reviewed_paper_figures(self):
        self.assertIn('src="static/images/motivation-case.webp"', self.source)
        self.assertIn('src="static/images/self-evolve-loop.webp"', self.source)
        self.assertNotIn('src="static/images/incident-learning.webp"', self.source)
        self.assertNotIn('class="incident-story"', self.source)

    def test_shift_copy_names_the_model_and_the_harness_gap(self):
        catalog_source = (ROOT / "static/js/i18n.js").read_text(encoding="utf-8")
        combined = self.source + catalog_source
        self.assertIn("General models are capable.", self.source)
        self.assertIn("The RCA gap is a harness that learns.", self.source)
        self.assertNotIn("The agent is capable.", combined)

    def test_full_table_ii_is_rendered_as_semantic_html(self):
        self.assertEqual(self.source.count('class="results-table"'), 1)
        self.assertIn(
            'class="results-table-hint" data-i18n="results.tableHint"',
            self.source,
        )
        self.assertIn(
            '"results.tableHint": "Scroll horizontally to view all metrics →"',
            self.i18n_source,
        )
        self.assertIn(
            '"results.tableHint": "横向滚动以查看全部指标 →"',
            self.i18n_source,
        )
        for backbone in (
            "gpt-5.5",
            "claude-sonnet-4.6",
            "glm-5.2",
            "deepseek-v4",
        ):
            self.assertIn(f'data-backbone="{backbone}"', self.source)
        self.assertEqual(
            len(re.findall(r'<tr[^>]*data-framework="[^"]+"', self.source)),
            24,
        )
        for backbone in (
            "gpt-5.5",
            "claude-sonnet-4.6",
            "glm-5.2",
            "deepseek-v4",
        ):
            for framework in (
                "rca-agent",
                "mabc",
                "direct",
                "icl",
                "opsharness-no-evolve",
                "opsharness",
            ):
                self.assertEqual(len(result_row(self.source, backbone, framework)), 20)

        sentinels = {
            "gpt-5.5": (
                "OpsHarness 72.7 72.7 77.0 64.2 71.4 78.0 37.1 66.5 72.0 "
                "72.2 88.9 96.0 77.8 88.9 93.0 72.2 94.4 96.0 66.0"
            ),
            "claude-sonnet-4.6": (
                "OpsHarness 63.6 63.6 73.0 57.1 63.7 81.9 35.7 64.2 72.0 "
                "61.1 83.3 95.0 55.6 77.8 89.0 61.1 77.8 93.0 55.7"
            ),
            "glm-5.2": (
                "OpsHarness 72.7 81.8 87.0 57.1 64.3 74.0 42.9 50.0 61.0 "
                "77.8 88.9 89.0 55.6 66.7 76.0 88.9 94.4 98.0 65.8"
            ),
            "deepseek-v4": (
                "OpsHarness 45.5 63.6 68.0 46.4 50.0 64.0 28.6 42.9 60.0 "
                "53.3 73.3 80.0 50.0 72.2 90.0 66.7 77.8 89.0 48.4"
            ),
        }
        for backbone, expected in sentinels.items():
            self.assertEqual(
                " ".join(result_row(self.source, backbone, "opsharness")),
                expected,
            )

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
        for token in (
            ".editorial-media",
            ".results-table-shell",
            ".results-table",
            "position: sticky",
            "overflow-x: auto",
        ):
            self.assertIn(token, css)

    def test_accent_card_body_meets_wcag_aa_contrast(self):
        css = (ROOT / "static/css/style.css").read_text(encoding="utf-8")
        card = re.search(
            r"\.comparison-card--accent\s*\{[^}]*background:\s*(#[0-9a-fA-F]{6})",
            css,
            re.S,
        )
        body = re.search(
            r"\.comparison-card--accent p\s*\{[^}]*color:\s*(#[0-9a-fA-F]{6})",
            css,
            re.S,
        )
        self.assertIsNotNone(card)
        self.assertIsNotNone(body)
        self.assertGreaterEqual(contrast_ratio(body.group(1), card.group(1)), 4.5)

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
