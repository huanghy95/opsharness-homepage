#!/usr/bin/env python3
"""End-to-end browser checks for the dependency-free OpsHarness homepage."""

from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

try:
    from playwright.sync_api import Error, expect, sync_playwright
except ImportError as exc:  # pragma: no cover - only reached without the optional QA tool
    raise SystemExit(
        "Browser QA requires Playwright: python3 -m pip install playwright"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, _format, *_args):
        pass


@contextmanager
def local_site():
    server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def scroll_through(page):
    height = page.evaluate("document.documentElement.scrollHeight")
    for position in range(0, height + 1, 700):
        page.evaluate("value => window.scrollTo(0, value)", position)
        page.wait_for_timeout(35)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(100)


def assert_no_overflow(page):
    metrics = page.evaluate(
        """() => ({
            documentWidth: document.documentElement.scrollWidth,
            viewportWidth: window.innerWidth,
            offenders: [...document.querySelectorAll("body *")]
                .map(node => {
                    const rect = node.getBoundingClientRect();
                    return {
                        tag: node.tagName,
                        className: String(node.className || ""),
                        left: Math.round(rect.left),
                        right: Math.round(rect.right)
                    };
                })
                .filter(item => item.left < -1 || item.right > window.innerWidth + 1)
                .slice(0, 12)
        })"""
    )
    assert metrics["documentWidth"] <= metrics["viewportWidth"], metrics


def assert_table_scrolls_within_page(page):
    scroller = page.locator(".results-table-scroll")
    dimensions = scroller.evaluate(
        "node => ({scrollWidth: node.scrollWidth, clientWidth: node.clientWidth})"
    )
    assert dimensions["scrollWidth"] > dimensions["clientWidth"], dimensions
    scroller.evaluate("node => { node.scrollLeft = 240; }")
    assert scroller.evaluate("node => node.scrollLeft") > 0
    assert_no_overflow(page)


def launch_browser(playwright):
    options = {"headless": True, "args": ["--no-proxy-server"]}
    try:
        return playwright.chromium.launch(channel="chrome", **options)
    except Error:
        return playwright.chromium.launch(**options)


def run():
    with local_site() as url, sync_playwright() as playwright:
        browser = launch_browser(playwright)
        context = browser.new_context(
            viewport={"width": 1440, "height": 1000},
            permissions=["clipboard-read", "clipboard-write"],
        )
        page = context.new_page()
        console_errors = []
        page.on(
            "console",
            lambda message: console_errors.append(message.text)
            if message.type == "error"
            else None,
        )
        page.goto(url, wait_until="networkidle")

        assert page.title() == "From General Agents to RCA Experts: A Self-Evolving Harness for Root Cause Analysis"
        assert page.locator("html").get_attribute("lang") == "en"
        assert page.locator("#evolution").count() == 0
        assert page.locator(".results-table").count() == 1
        assert page.locator("[data-framework]").count() == 24
        expect(page.locator(".results-table-hint")).to_have_text(
            "Scroll horizontally to view all metrics →"
        )
        assert (
            page.locator(".results-table tbody tr[data-framework] th").first.evaluate(
                "node => getComputedStyle(node).position"
            )
            == "sticky"
        )
        assert page.locator(".visual-legend span").all_text_contents() == [
            "Skills",
            "Knowledge",
            "Tools",
            "Verification",
            "Self-Evolve",
        ]
        assert page.locator(".comparison-card--accent p").evaluate(
            "node => getComputedStyle(node).color"
        ) == "rgb(245, 242, 255)"
        assert_no_overflow(page)

        page.evaluate("localStorage.setItem('opsharness-language', 'invalid')")
        page.reload(wait_until="networkidle")
        assert page.locator("html").get_attribute("lang") == "en"

        page.locator("[data-language-toggle]").click()
        assert page.locator("html").get_attribute("lang") == "zh-CN"
        expect(page.locator("nav")).to_have_attribute("aria-label", "主导航")
        expect(page.locator("[data-lightbox-image]").first).to_have_attribute(
            "aria-label", "展开图 1"
        )
        expect(page.locator(".results-table-hint")).to_have_text(
            "横向滚动以查看全部指标 →"
        )
        assert page.locator("[data-lightbox-image] img").first.get_attribute("alt").startswith(
            "Illustration showing"
        )
        assert "$setup" in page.locator("#codex-panel").inner_text()
        assert page.evaluate("localStorage.getItem('opsharness-language')") == "zh"

        page.reload(wait_until="networkidle")
        assert page.locator("html").get_attribute("lang") == "zh-CN"
        expect(page.locator("[data-language-toggle]")).to_have_attribute(
            "aria-label", "切换到英文"
        )

        page.locator("#claude-tab").click()
        expect(page.locator("#claude-tab")).to_have_attribute("aria-selected", "true")
        expect(page.locator("#claude-panel")).to_be_visible()
        expect(page.locator("#codex-panel")).to_be_hidden()
        page.locator("#claude-tab").press("ArrowLeft")
        expect(page.locator("#codex-tab")).to_have_attribute("aria-selected", "true")
        expect(page.locator("#codex-tab")).to_be_focused()

        copy_button = page.locator("[data-copy-target]")
        copy_button.click()
        expect(copy_button).to_have_text("已复制")
        expect(page.locator("[data-copy-status]")).to_have_text("已复制")

        first_figure = page.locator("[data-lightbox-image]").first
        first_figure.click()
        expect(page.locator("[data-lightbox]")).to_have_attribute("aria-hidden", "false")
        assert page.locator("main").get_attribute("inert") is not None
        page.keyboard.press("Tab")
        expect(page.locator("[data-lightbox-close]")).to_be_focused()
        page.keyboard.press("Escape")
        expect(page.locator("[data-lightbox]")).to_have_attribute("aria-hidden", "true")
        expect(first_figure).to_be_focused()
        assert page.locator("main").get_attribute("inert") is None

        scroll_through(page)
        assert page.locator("img:not([data-lightbox-target])").evaluate_all(
            "images => images.every(image => image.complete && image.naturalWidth > 0)"
        )
        assert_no_overflow(page)
        assert not console_errors, console_errors
        context.close()

        no_javascript = browser.new_context(
            viewport={"width": 768, "height": 900}, java_script_enabled=False
        )
        static_page = no_javascript.new_page()
        static_page.goto(url, wait_until="networkidle")
        expect(static_page.locator("#codex-panel")).to_be_visible()
        expect(static_page.locator("#claude-panel")).to_be_visible()
        expect(static_page.get_by_text("Codex", exact=True).last).to_be_visible()
        expect(static_page.get_by_text("Claude Code", exact=True).last).to_be_visible()
        assert static_page.locator("[data-reveal]").evaluate_all(
            "nodes => nodes.every(node => getComputedStyle(node).opacity === '1')"
        )
        assert_table_scrolls_within_page(static_page)
        no_javascript.close()

        mobile = browser.new_context(viewport={"width": 390, "height": 844})
        mobile_page = mobile.new_page()
        mobile_page.goto(url, wait_until="networkidle")
        mobile_page.locator("[data-nav-toggle]").click()
        expect(mobile_page.locator("[data-nav-toggle]")).to_have_attribute(
            "aria-expanded", "true"
        )
        expect(mobile_page.locator("#primary-navigation")).to_be_visible()
        mobile_page.keyboard.press("Escape")
        expect(mobile_page.locator("[data-nav-toggle]")).to_have_attribute(
            "aria-expanded", "false"
        )
        assert_table_scrolls_within_page(mobile_page)
        mobile.close()

        reduced = browser.new_context(
            viewport={"width": 768, "height": 900}, reduced_motion="reduce"
        )
        reduced_page = reduced.new_page()
        reduced_page.goto(url, wait_until="networkidle")
        assert reduced_page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
        assert reduced_page.locator("[data-reveal].reveal-ready").count() == 0
        assert_no_overflow(reduced_page)
        reduced.close()
        browser.close()


if __name__ == "__main__":
    run()
    print(
        "Browser QA PASS: no-JS, bilingual ARIA, tabs, live copy feedback, "
        "modal focus, responsive layout, reduced motion"
    )
