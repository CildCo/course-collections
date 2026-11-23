"""第 2 课：定位元素、输入、点击、读取内容。"""
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
        goto(page, "/")

        page.locator("#search-input").fill("Playwright")
        page.locator("#btn-search").click()
        page.locator("#search-results.show").wait_for(state="visible", timeout=5000)
        header = page.locator("#result-header").inner_text()
        print(f"搜索结果：{header}")

        page.locator("#username").fill("alice")
        page.locator("#email").fill("alice@example.com")
        page.locator("#password").fill("test123456")
        page.locator("#btn-submit").click()
        print(f"表单提示：{page.locator('#pwd-hint').inner_text()}")

        print(f"文章卡片：{page.locator('.article-card').count()} 个")
        print(f"排行榜行数：{page.locator('#rank-table tbody tr').count()} 行")
        print(f"第一篇文章：{page.locator('.card-title').first.inner_text()}")
        print(f"第二行：{page.locator('#rank-table tbody tr').nth(1).inner_text()}")

        screenshot(page, "02_元素定位")
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
