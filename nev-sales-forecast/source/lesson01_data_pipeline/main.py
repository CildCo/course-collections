"""第 1 课：从原始销量表到可建模的数据集。"""
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
    RAW_DIR,
    build_sample_data,
    clean_sales,
    ensure_dirs,
    setup_plot,
)


def main() -> None:
    setup_plot()
    ensure_dirs()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    raw = build_sample_data()
    raw_file = RAW_DIR / "historical_car_sales_2017_to_2026.csv"
    raw.to_csv(raw_file, index=False, encoding="utf-8-sig")
    clean, report = clean_sales(raw)
    clean_file = PROCESSED_DIR / "cleaned_sales_data.csv"
    clean.to_csv(clean_file, index=False, encoding="utf-8-sig")

    lines = [
        "新能源车销量数据质量报告",
        "=" * 42,
    ]
    for key, value in report.items():
        lines.append(f"{key}：{value}")
    lines += [
        "",
        "清洗规则：",
        "  - 月份统一转成日期，车型和品牌去掉首尾空格；",
        "  - 销量转成数值，删除缺失、负数和重复记录；",
        "  - 按月份重新计算排名；",
        "  - 保留 0 销量记录，表示车型当月没有成交。",
        f"原始文件：{raw_file}",
        f"清洗后文件：{clean_file}",
    ]
    text = "\n".join(lines)
    (OUTPUT_DIR / "数据质量报告.txt").write_text(text, encoding="utf-8")
    print(text)

    monthly = clean.groupby("统计月份", as_index=False)["销量"].sum()
    fig, ax = plt.subplots(figsize=(13, 4.8))
    ax.plot(monthly["统计月份"], monthly["销量"] / 10000, color=BLUE, linewidth=1.6)
    ax.fill_between(monthly["统计月份"], monthly["销量"] / 10000, color=BLUE, alpha=0.12)
    ax.set_title("新能源乘用车月度销量（2017-01 至 2026-04）", fontsize=14, fontweight="bold", color=NAVY)
    ax.set_ylabel("万辆")
    ax.grid(alpha=0.22)
    for year in range(2018, 2027):
        ax.axvline(pd.Timestamp(f"{year}-01-01"), color=GOLD, linewidth=0.5, alpha=0.25)
    fig.savefig(OUTPUT_DIR / "月度销量.png")
    plt.close(fig)
    print(f"\n图表已保存：{OUTPUT_DIR / '月度销量.png'}")


if __name__ == "__main__":
    main()
