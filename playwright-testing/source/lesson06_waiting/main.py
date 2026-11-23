"""第 6 课：Playwright 智能等待。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from playwright.sync_api import expect, sync_playwright

from common import ensure_server, goto, launch, screenshot


def main() -> None:
    ensure_server()
    with sync_playwright() as p:
        browser, context = launch(p)
        page = context.new_page()
        goto(page, "/wait")

        started = time.perf_counter()
        page.locator("#btn-load").click()
        page.locator("#slow-content").wait_for(state="visible", timeout=5000)
        elapsed = time.perf_counter() - started

        expect(page.locator("#slow-title")).to_have_text("数据加载完成")
        expect(page.locator("#status-text")).to_contain_text("完成")
        print(f"等待耗时：{elapsed:.2f} 秒")
        print(f"慢内容：{page.locator('#slow-text').inner_text()}")
        print(f"状态：{page.locator('#status-text').inner_text()}")
        screenshot(page, "06_智能等待")
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
