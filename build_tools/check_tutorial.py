"""Exercise the generated offline guide in Chromium. Requires Playwright for this check only."""
from pathlib import Path
import argparse
import shutil
import sys

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app_info import VERSION
from i18n import CATALOGS, LANGUAGES


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    parser.add_argument("--screens", type=Path)
    args = parser.parse_args()
    errors, external = [], []
    with sync_playwright() as driver:
        chrome = shutil.which("google-chrome") or shutil.which("chromium")
        browser = driver.chromium.launch(executable_path=chrome)
        context = browser.new_context(viewport={"width": 1400, "height": 900},
                                      locale="pt-BR", reduced_motion="reduce", offline=True)
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda req: external.append(req.url) if req.url.startswith(("http:", "https:")) else None)
        page.goto(args.html.resolve().as_uri() + "?lang=pt")
        for code in LANGUAGES:
            page.select_option("#language", code)
            assert page.locator("html").get_attribute("lang") == {"pt":"pt-BR","zh":"zh-CN"}.get(code, code)
            assert page.locator("#version").inner_text() == "v" + VERSION
            assert page.locator("#chapters a").count() == 6
            assert page.locator("#steps h2").count() == 6
            assert page.locator("#external a").count() == 4
            assert CATALOGS[code]["open"] in page.locator("#install .copy").inner_text()
            assert "Open GIF / video" in page.locator("#install .copy").inner_text()
            assert "undefined" not in page.locator("main").inner_text()
            for i in range(4):
                shot = page.locator(".shot").nth(i)
                shot.click()
                assert page.locator("#viewer").is_visible()
                page.locator("#fullshot").evaluate("(img) => img.decode()")
                assert page.locator("#fullshot").evaluate("(img) => img.naturalWidth") == 1250
                page.keyboard.press("Escape")
                assert not page.locator("#viewer").is_visible()
            page.locator("summary").first.click()
            assert page.locator("details[open]").count() == 1
            for width in (360, 1280):
                page.set_viewport_size({"width":width,"height":850})
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), code
        page.select_option("#language","pt")
        page.reload()
        assert page.locator("#language").input_value() == "pt"
        assert page.locator("#get").get_attribute("href").endswith("/releases/tag/v"+VERSION)
        for selector, suffix in ((".packages a:first-child", "Windows-x64.zip"), (".packages a:last-child", "Linux-x86_64.tar.gz")):
            assert page.locator(selector).get_attribute("href").endswith(f"/v{VERSION}/Framosik-{VERSION}-{suffix}")
        slider = page.locator("#scrub")
        page.locator("#demoPlay").click()
        assert page.locator("#demoPlay").get_attribute("aria-pressed") == "true"
        page.locator("#demoPlay").click()
        assert page.locator("#demoPlay").get_attribute("aria-pressed") == "false"
        slider.focus()
        page.keyboard.press("Home")
        assert page.locator("#position").inner_text() == "01 / 37"
        page.keyboard.press("End")
        assert page.locator("#position").inner_text() == "37 / 37"
        assert page.locator("#band").evaluate("(el) => parseFloat(el.style.top)") == 0
        if args.screens:
            args.screens.mkdir(parents=True, exist_ok=True)
            page.reload()
            for name, width, height in (("desktop",1400,900),("mobile",390,844)):
                page.set_viewport_size({"width":width,"height":height})
                page.evaluate("window.scrollTo(0,0)")
                page.screenshot(path=args.screens / f"{name}.png")
        browser.close()
    assert not errors and not external, (errors, external)
    print("Offline tutorial passed in all ten languages on desktop and mobile widths.")


if __name__ == "__main__":
    main()
