"""第 1 课：第一个 Playwright 脚本。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from playwright.sync_api import sync_playwright

from common import BASE_URL, ensure_server, goto, launch, screenshot


def main() -> None:
    ensure_server()
    with sync_playwright() as p:
        browser, context = launch(p)
        page = context.new_page()
        goto(page, "/")
        print(f"页面标题：{page.title()}")
        print(f"当前地址：{page.url}")
        print(f"导航数量：{page.locator('header nav a').count()}")
        screenshot(page, "01_第一个脚本")
        context.close()
        browser.close()
    print(f"本地练习站：{BASE_URL}")


if __name__ == "__main__":
    main()
