"""第 1 课：合并 36 个月度报表并完成清洗。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import pandas as pd

from common import (
    BLUE,
    GOLD,
    NAVY,
    OUTPUT_DIR,
    PROCESSED_DIR,
    clean_orders,
    ensure_dirs,
    merge_monthly_files,
    setup_plot,
)


def main() -> None:
    setup_plot()
    ensure_dirs()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = merge_monthly_files()
    clean, report = clean_orders(raw)
    clean.to_csv(PROCESSED_DIR / "orders_merged.csv", index=False, encoding="utf-8-sig")
    clean.to_excel(PROCESSED_DIR / "全年汇总数据.xlsx", index=False)

    lines = ["订单数据合并与清洗报告", "=" * 44]
    for key, value in report.items():
        lines.append(f"{key}：{value}")
    lines += [
        "",
        "清洗规则：",
        "  - 按订单编号去重，保留第一次出现；",
        "  - 销售额为空时用 数量 × 单价 补全；",
        "  - 删除负销售额和无法解析日期的记录；",
        "  - 从日期中拆出年份、月份、季度、星期和是否周末。",
        f"合并文件：{PROCESSED_DIR / '全年汇总数据.xlsx'}",
    ]
    text = "\n".join(lines)
    (OUTPUT_DIR / "数据质量报告.txt").write_text(text, encoding="utf-8")
    print(text)

    monthly = clean.groupby(clean["下单日期"].dt.to_period("M"))["销售额"].sum()
    monthly.index = monthly.index.astype(str)
    fig, ax = plt.subplots(figsize=(13, 4.8))
    ax.plot(monthly.index, monthly.values / 10000, color=BLUE, linewidth=1.7)
    ax.fill_between(range(len(monthly)), monthly.values / 10000, color=BLUE, alpha=0.12)
    ax.set_xticks(range(0, len(monthly), 3), monthly.index[::3], rotation=35, fontsize=8)
    ax.set_title("合并后的月度销售额（2023-2025）", fontsize=14, fontweight="bold", color=NAVY)
    ax.set_ylabel("万元")
    ax.grid(alpha=0.22)
    for year in (2024, 2025):
        if f"{year}-01" in monthly.index:
            ax.axvline(list(monthly.index).index(f"{year}-01"), color=GOLD, linewidth=0.6, alpha=0.3)
    fig.savefig(OUTPUT_DIR / "月度销售.png")
    plt.close(fig)
    print(f"\n图表已保存：{OUTPUT_DIR / '月度销售.png'}")


if __name__ == "__main__":
    main()
