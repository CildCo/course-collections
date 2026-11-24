"""第 4 课：网页表单自动填写。"""
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
        goto(page, "/form")

        page.get_by_label("姓名").fill("小李")
        page.get_by_label("手机号").fill("13800138000")
        page.get_by_label("城市").select_option("上海")
        page.get_by_label("线上").check()
        page.get_by_label("同意活动须知").check()
        page.get_by_label("参加日期").fill("2026-06-18")
        page.locator("#level").fill("9")
        page.get_by_label("备注").fill("希望安排靠前排座位。")
        page.get_by_role("button", name="提交报名").click()

        print(f"提交结果：{page.locator('#form-result').inner_text()}")
        print(f"城市：{page.locator('#city').input_value()}")
        mode = page.locator("input[name='mode']:checked").input_value()
        print(f"线下/线上：{mode}")
        screenshot(page, "04_表单填写")
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
