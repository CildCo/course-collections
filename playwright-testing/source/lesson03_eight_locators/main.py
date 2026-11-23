"""第 3 课：八种定位方式。"""
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
        goto(page, "/login")

        # 1. label
        page.get_by_label("用户名").fill("demo_user")
        # 2. placeholder
        page.get_by_label("用户名").clear()
        page.get_by_placeholder("请输入用户名或邮箱").fill("demo_user")
        # 3. role
        page.get_by_role("checkbox", name="记住我").check()
        page.get_by_label("邮箱").fill("demo@example.com")
        # 4. CSS
        page.locator("#password").fill("pass123456")
        # 5. XPath
        page.locator("xpath=//input[@id='email']").fill("demo@example.com")
        # 6. test id
        page.get_by_test_id("username-input").fill("playwright_user")
        # 7. text / link
        print(f"忘记密码链接：{page.get_by_role('link', name='忘记密码').inner_text()}")
        # 8. 链式定位
        page.locator("#login-form").locator("button[type='button']").click()

        print(f"登录结果：{page.locator('#login-result').inner_text()}")
        print(f"复选框状态：{page.get_by_role('checkbox', name='记住我').is_checked()}")
        screenshot(page, "03_八种定位")
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
