"""第 2 课：2017-2026 市场趋势仪表盘。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import numpy as np

from common import (
    BLUE,
    BRAND_COLORS,
    GOLD,
    MODEL_COLORS,
    NAVY,
    OUTPUT_DIR,
    TEAL,
    brand_rank,
    ensure_data,
    model_rank,
    setup_plot,
    yearly_sales,
)


def style_axis(ax) -> None:
    ax.grid(True, axis="y", linestyle="--", alpha=0.28)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def main() -> None:
    setup_plot()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    data = ensure_data()
    yearly = yearly_sales(data)
    brands = brand_rank(data, 6)
    models = model_rank(data, 10)
    top3 = brands.head(3)["品牌/厂商"].tolist()
    stack = (
        data[data["品牌/厂商"].isin(top3)]
        .pivot_table(index="年份", columns="品牌/厂商", values="销量", aggfunc="sum", fill_value=0)
    )

    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor("#F7FAFC")
    fig.suptitle("新能源汽车市场趋势复盘（2017-2026）", fontsize=22, fontweight="bold", color=NAVY, y=0.97)

    ax1 = fig.add_subplot(2, 2, 1)
    ax1.plot(yearly["年份"], yearly["销量"] / 10000, color=NAVY, marker="o", linewidth=2.2, markersize=6)
    ax1.fill_between(yearly["年份"], yearly["销量"] / 10000, color=NAVY, alpha=0.10)
    for x, y in zip(yearly["年份"], yearly["销量"] / 10000):
        ax1.text(x, y + yearly["销量"].max() / 10000 * 0.025, f"{y:.0f}", ha="center", fontsize=8, color="#566573")
    ax1.set_title("年度销量趋势", loc="left", fontsize=13, color=NAVY, fontweight="bold")
    ax1.set_ylabel("万辆")
    ax1.text(0.01, 0.92, "2026 为 1-4 月", transform=ax1.transAxes, fontsize=8, color="#7F8C8D")
    style_axis(ax1)

    ax2 = fig.add_subplot(2, 2, 2)
    stack.plot(kind="bar", stacked=True, ax=ax2, color=[NAVY, TEAL, "#E74C3C"], width=0.68)
    ax2.set_title("Top 3 品牌年度构成", loc="left", fontsize=13, color=NAVY, fontweight="bold")
    ax2.set_ylabel("万辆")
    ax2.set_yticklabels([f"{int(tick / 10000)}" for tick in ax2.get_yticks()])
    ax2.legend(title="品牌", loc="upper left", frameon=False, fontsize=8)
    ax2.tick_params(axis="x", rotation=0)
    style_axis(ax2)

    ax3 = fig.add_subplot(2, 2, 3)
    short_models = models["车型"].str.replace("比亚迪", "").str.replace("特斯拉", "").tolist()
    bars = ax3.barh(short_models[::-1], models["销量"][::-1] / 10000, color=MODEL_COLORS)
    for bar in bars:
        ax3.text(bar.get_width() * 1.01, bar.get_y() + bar.get_height() / 2, f"{bar.get_width():.0f}", va="center", fontsize=8, color="#566573")
    ax3.set_title("历史爆款车型 Top 10", loc="left", fontsize=13, color=NAVY, fontweight="bold")
    ax3.set_xlabel("万辆")
    ax3.grid(axis="x", linestyle="--", alpha=0.25)
    ax3.spines["top"].set_visible(False)
    ax3.spines["right"].set_visible(False)

    ax4 = fig.add_subplot(2, 2, 4)
    bars = ax4.bar(brands["品牌/厂商"], brands["销量"] / 10000, color=BRAND_COLORS)
    for bar in bars:
        ax4.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + brands["销量"].max() / 10000 * 0.02, f"{bar.get_height():.0f}", ha="center", fontsize=8, color="#566573")
    ax4.set_title("品牌累计销量 Top 6", loc="left", fontsize=13, color=NAVY, fontweight="bold")
    ax4.set_ylabel("万辆")
    ax4.tick_params(axis="x", rotation=18)
    style_axis(ax4)

    fig.tight_layout(rect=[0, 0.01, 1, 0.95])
    fig.savefig(OUTPUT_DIR / "市场仪表盘.png")
    plt.close(fig)

    print("2017-2026 市场概览")
    print(f"累计销量：{data['销量'].sum() / 10000:.0f} 万辆")
    print(f"品牌数：{data['品牌/厂商'].nunique()}，车型数：{data['车型'].nunique()}")
    print(f"2025 年销量：{yearly.loc[yearly['年份'] == 2025, '销量'].iloc[0] / 10000:.0f} 万辆")
    print(f"2026 年 1-4 月：{yearly.loc[yearly['年份'] == 2026, '销量'].iloc[0] / 10000:.0f} 万辆")
    print(f"累计第一品牌：{brands.iloc[0]['品牌/厂商']} {brands.iloc[0]['销量'] / 10000:.0f} 万辆")
    print(f"\n仪表盘已保存：{OUTPUT_DIR / '市场仪表盘.png'}")


if __name__ == "__main__":
    main()
