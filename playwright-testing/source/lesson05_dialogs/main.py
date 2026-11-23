"""第 5 课：处理 alert、confirm、prompt 弹窗。"""
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
        goto(page, "/dialogs")

        page.once("dialog", lambda dialog: (print(f"alert：{dialog.message}"), dialog.accept()))
        page.locator("#btn-alert").click()
        page.wait_for_timeout(100)
        print(page.locator("#dialog-output").inner_text())

        page.once("dialog", lambda dialog: (print(f"confirm：{dialog.message}"), dialog.accept()))
        page.locator("#btn-confirm").click()
        page.wait_for_timeout(100)
        print(page.locator("#dialog-output").inner_text())

        page.once("dialog", lambda dialog: (print(f"prompt：{dialog.message}"), dialog.accept("小居")))
        page.locator("#btn-prompt").click()
        page.wait_for_timeout(100)
        print(page.locator("#dialog-output").inner_text())

        screenshot(page, "05_弹窗处理")
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
