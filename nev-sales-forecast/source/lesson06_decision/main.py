"""第 6 课：从预测结果到 2026 年经营决策。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import (
    BLUE,
    GOLD,
    NAVY,
    OUTPUT_DIR,
    PROCESSED_DIR,
    RED,
    TEAL,
    ensure_data,
    load_json,
    setup_plot,
)


def main() -> None:
    setup_plot()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    data = ensure_data()
    forecast = pd.read_csv(PROCESSED_DIR / "forecast_2026.csv", parse_dates=["统计月份"])
    market_forecast = pd.read_csv(PROCESSED_DIR / "market_forecast.csv", parse_dates=["date"])
    metrics = load_json(PROCESSED_DIR / "forecast_metrics.json")
    brands = metrics["brands"]

    actual = data.groupby("统计月份")["销量"].sum().sort_index()
    actual_2025 = int(actual[actual.index.year == 2025].sum())
    actual_2026 = actual[actual.index.year == 2026]
    future_total = market_forecast["forecast"].sum()
    annual_2026 = int(actual_2026.sum() + future_total)
    yoy = annual_2026 / actual_2025 - 1

    brand_future = forecast.groupby("品牌/厂商", as_index=False)["融合预测"].sum()
    brand_future["份额"] = brand_future["融合预测"] / future_total
    top5_share = brand_future["份额"].sum()
    top_brand = brand_future.sort_values("融合预测", ascending=False).iloc[0]

    scenarios = {
        "基准": future_total,
        "乐观 +8%": future_total * 1.08,
        "保守 -8%": future_total * 0.92,
    }

    monthly_path = pd.concat(
        [
            actual_2026.rename("销量").reset_index().assign(类型="实际"),
            market_forecast.rename(columns={"date": "统计月份", "forecast": "销量"})[["统计月份", "销量"]].assign(类型="预测"),
        ]
    )
    monthly_path.to_csv(PROCESSED_DIR / "monthly_path_2026.csv", index=False, encoding="utf-8-sig")
    brand_future.to_csv(PROCESSED_DIR / "brand_forecast_2026.csv", index=False, encoding="utf-8-sig")

    quarters = {
        "Q2（5-6月）": market_forecast[market_forecast["date"].dt.month.isin([5, 6])]["forecast"].sum(),
        "Q3（7-9月）": market_forecast[market_forecast["date"].dt.month.isin([7, 8, 9])]["forecast"].sum(),
        "Q4（10-12月）": market_forecast[market_forecast["date"].dt.month.isin([10, 11, 12])]["forecast"].sum(),
    }

    lines = [
        "2026 年新能源车市决策报告",
        "=" * 52,
        f"历史区间：{data['统计月份'].min():%Y-%m} 至 {data['统计月份'].max():%Y-%m}",
        f"2025 年销量：{actual_2025 / 10000:.1f} 万辆",
        f"2026 年 1-4 月实际：{actual_2026.sum() / 10000:.1f} 万辆",
        f"2026 年全年预测：{annual_2026 / 10000:.1f} 万辆（同比 {yoy:+.1%}）",
        f"预测区间：5-12 月，Top 5 品牌融合模型",
        "",
        "一、三条关键判断",
        f"  1. 头部集中：Top 5 品牌拿走预测增量的 {top5_share:.1%}，{top_brand['品牌/厂商']} 仍是第一。",
        "  2. 季节波动：9-12 月是全年高点，Q4 备货和交付能力决定全年成败。",
        f"  3. 增长降速：2026 年预计同比 {yoy:+.1%}，市场从增量扩张转向存量博弈。",
        "",
        "二、季度节奏",
    ]
    for quarter, value in quarters.items():
        lines.append(f"  {quarter}：{value / 10000:.1f} 万辆")
    lines += [
        "",
        "三、经营建议",
        f"  - Q3 备货按基准预测上浮 8%-10%，重点保障 {top_brand['品牌/厂商']} 等头部品牌的热销车型。",
        "  - Q4 不要把全部希望押在12月冲量，10月和11月就要完成大部分交付。",
        "  - 对中小品牌设置止损线：连续两个月低于预测下限，就收缩渠道和库存。",
        "  - 用月度滚动预测替换年度一次性预算，每月更新一次模型。",
        "",
        "四、情景分析",
        f"  基准：{scenarios['基准'] / 10000:.1f} 万辆（5-12月）",
        f"  乐观：{scenarios['乐观 +8%'] / 10000:.1f} 万辆",
        f"  保守：{scenarios['保守 -8%'] / 10000:.1f} 万辆",
        "",
        "说明：示例数据用于演示方法，不构成投资或经营建议。",
        "真实决策还要结合价格战、补贴政策、产能和渠道库存。",
    ]
    report = "\n".join(lines)
    (OUTPUT_DIR / "2026决策报告.txt").write_text(report, encoding="utf-8")
    print(report)

    fig, axes = plt.subplots(2, 2, figsize=(13, 8.2))
    axes[0, 0].plot(actual_2026.index, actual_2026 / 10000, color=NAVY, marker="o", linewidth=1.6, label="实际")
    axes[0, 0].plot(market_forecast["date"], market_forecast["forecast"] / 10000, color=GOLD, linestyle="--", marker="o", linewidth=1.6, label="基准预测")
    axes[0, 0].fill_between(market_forecast["date"], market_forecast["lower"] / 10000, market_forecast["upper"] / 10000, color=GOLD, alpha=0.16)
    axes[0, 0].set_title("2026 年月度销量路径", loc="left", color=NAVY)
    axes[0, 0].legend(frameon=False, fontsize=8)
    axes[0, 0].grid(alpha=0.2)

    axes[0, 1].barh(brand_future.sort_values("融合预测")["品牌/厂商"], brand_future.sort_values("融合预测")["份额"] * 100, color=TEAL)
    axes[0, 1].set_title("Top 5 品牌 5-12 月预测份额", loc="left", color=NAVY)
    axes[0, 1].set_xlabel("%")
    axes[0, 1].grid(axis="x", alpha=0.2)

    labels = list(scenarios)
    values = [value / 10000 for value in scenarios.values()]
    axes[1, 0].bar(labels, values, color=[TEAL, BLUE, RED])
    for index, value in enumerate(values):
        axes[1, 0].text(index, value, f"{value:.1f}", ha="center", va="bottom", fontsize=9)
    axes[1, 0].set_title("5-12 月情景分析（万辆）", loc="left", color=NAVY)
    axes[1, 0].grid(axis="y", alpha=0.2)

    axes[1, 1].bar(list(quarters), [value / 10000 for value in quarters.values()], color=[TEAL, BLUE, GOLD])
    for index, value in enumerate(quarters.values()):
        axes[1, 1].text(index, value / 10000, f"{value / 10000:.1f}", ha="center", va="bottom", fontsize=9)
    axes[1, 1].set_title("季度销量预测（万辆）", loc="left", color=NAVY)
    axes[1, 1].set_xticks(range(len(quarters)), list(quarters), rotation=12)
    axes[1, 1].grid(axis="y", alpha=0.2)

    for ax in axes.flat:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(labelsize=8)
    fig.suptitle("2026 新能源车市决策总览", fontsize=15, fontweight="bold", color=NAVY)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "决策总览.png")
    plt.close(fig)
    print(f"\n报告已保存：{OUTPUT_DIR / '2026决策报告.txt'}")


if __name__ == "__main__":
    main()
