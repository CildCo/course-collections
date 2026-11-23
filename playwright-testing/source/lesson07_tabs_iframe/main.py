"""第 7 课：多标签页与 iframe。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from playwright.sync_api import sync_playwright

from common import ensure_server, goto, launch, screenshot


def main() -> None:
    ensure_server()
    with sync_playwright() as p:
        browser, context = launch(p)
        page = context.new_page()
        goto(page, "/tabs")

        with context.expect_page() as popup_info:
            page.locator("#open-tab").click()
        child = popup_info.value
        child.wait_for_load_state("domcontentloaded")
        print(f"新标签页标题：{child.locator('#child-title').inner_text()}")
        child.locator("#child-btn").click()
        print(f"子页面结果：{child.locator('#child-result').inner_text()}")
        screenshot(child, "07_新标签页")

        page.goto("http://127.0.0.1:5011/iframe", wait_until="domcontentloaded")
        frame = page.frame_locator("#demo-frame")
        print(f"iframe 标题：{frame.locator('#inner-title').inner_text()}")
        frame.locator("#inner-btn").click()
        print(f"iframe 结果：{frame.locator('#inner-result').inner_text()}")
        screenshot(page, "07_iframe")
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
