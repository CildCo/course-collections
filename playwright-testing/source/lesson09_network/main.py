"""第 9 课：请求拦截与 CI 稳定性。"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from playwright.sync_api import sync_playwright

from common import OUTPUT_DIR, ensure_server, goto, launch, screenshot


def main() -> None:
    ensure_server()
    blocked = []
    with sync_playwright() as p:
        browser, context = launch(p)
        page = context.new_page()

        def block(route):
            blocked.append(route.request.url)
            route.abort()

        page.route("**/tracking.js", block)
        page.route("**/api/analytics", block)
        page.route(
            "**/api/products",
            lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(
                    {"items": [{"id": 99, "name": "测试商品", "price": 199}]},
                    ensure_ascii=False,
                ),
            ),
        )

        goto(page, "/network")
        page.locator("#btn-products").click()
        page.locator("text=测试商品").wait_for(state="visible", timeout=5000)
        print(f"页面商品：{page.locator('#product-list').inner_text()}")
        print(f"已拦截请求：{len(blocked)} 个")
        for url in blocked:
            print(f"  - {url}")

        output = OUTPUT_DIR / "请求拦截报告.txt"
        output.write_text(
            "请求拦截报告\n"
            f"拦截数量：{len(blocked)}\n"
            + "\n".join(f"- {url}" for url in blocked)
            + "\n\n原则：只拦截埋点、统计和无关静态资源，不要拦截业务接口。\n",
            encoding="utf-8",
        )
        screenshot(page, "09_请求拦截")
        context.close()
        browser.close()
    print(f"报告：{OUTPUT_DIR / '请求拦截报告.txt'}")


if __name__ == "__main__":
    main()
