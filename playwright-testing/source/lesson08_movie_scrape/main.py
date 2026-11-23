"""第 8 课：抓取 30 部电影并导出 CSV。"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from playwright.sync_api import sync_playwright

from common import BASE_URL, ROOT, ensure_server, goto, launch, screenshot


def main() -> None:
    ensure_server()
    rows = []
    with sync_playwright() as p:
        browser, context = launch(p)
        page = context.new_page()
        for page_number in range(1, 4):
            goto(page, f"/movies?page={page_number}")
            cards = page.locator(".movie-card")
            count = cards.count()
            for index in range(count):
                card = cards.nth(index)
                rows.append(
                    {
                        "片名": card.locator(".movie-title").inner_text(),
                        "年份": card.locator(".movie-year").inner_text(),
                        "评分": card.locator(".movie-rating").inner_text(),
                        "类型": card.locator(".movie-genre").inner_text(),
                        "导演": card.locator(".movie-director").inner_text(),
                        "时长": card.locator(".movie-duration").inner_text(),
                    }
                )
            print(f"第 {page_number} 页：{count} 部")
        screenshot(page, "08_电影数据")
        context.close()
        browser.close()

    output = ROOT / "data" / "movies.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"共抓取：{len(rows)} 部电影")
    print(f"CSV：{output}")
    print(f"最高分：{max(rows, key=lambda item: float(item['评分']))['片名']}")


if __name__ == "__main__":
    main()
