# 第5课：双轴图与 2x2 子图布局，一页看懂复杂报表
# 运行：python main.py

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR.parent))

import numpy as np

from common import (
    COLORS,
    add_bar_labels,
    output_dir,
    plt,
    save_figure,
    setup_chinese_font,
    style_axes,
)

MONTHS = ["1月", "2月", "3月", "4月", "5月", "6月"]
SALES = [105, 118, 136, 129, 152, 171]
GROWTH = [6, 7, -3, 14, 9, 11]

QUARTERS = ["Q1", "Q2", "Q3", "Q4"]
QUARTER_SALES = [158, 196, 184, 226]
QUARTER_TARGET = 190
DIRECT_Q = [88, 112, 104, 126]
PARTNER_Q = [62, 88, 76, 94]
CHANNEL_SHARE = [48, 34, 18]
CHANNEL_NAMES = ["直营", "分销", "线上"]


def draw_dual_axis():
    """左轴看金额，右轴看百分比，两个维度放在同一张图里。"""
    setup_chinese_font()
    fig, ax1 = plt.subplots(figsize=(10, 6), dpi=200)

    bars = ax1.bar(
        MONTHS,
        SALES,
        width=0.52,
        color=COLORS["blue"],
        alpha=0.88,
        edgecolor="white",
        linewidth=1.2,
        label="销售额",
        zorder=2,
    )
    add_bar_labels(ax1, bars, fmt="{:.0f}", dy=4)
    ax1.set_ylim(0, max(SALES) * 1.28)
    ax1.set_xlabel("月份", fontsize=12)
    ax1.set_ylabel("销售额（万元）", color=COLORS["blue"], fontsize=12)
    ax1.tick_params(axis="y", labelcolor=COLORS["blue"])
    style_axes(ax1)

    ax2 = ax1.twinx()
    line = ax2.plot(
        MONTHS,
        GROWTH,
        color=COLORS["red"],
        marker="o",
        markersize=8,
        linewidth=2.3,
        label="增长率",
        zorder=3,
    )[0]
    ax2.set_ylim(min(GROWTH) - 6, max(GROWTH) + 8)
    ax2.set_ylabel("增长率（%）", color=COLORS["red"], fontsize=12)
    ax2.tick_params(axis="y", labelcolor=COLORS["red"])
    ax2.axhline(0, color=COLORS["gray"], linestyle="--", linewidth=0.9, alpha=0.5)
    ax2.spines["top"].set_visible(False)

    for month, value in zip(MONTHS, GROWTH):
        ax2.annotate(
            f"{value}%",
            xy=(month, value),
            xytext=(0, 10),
            textcoords="offset points",
            ha="center",
            fontsize=10,
            color=COLORS["red"],
            fontweight="bold",
        )

    ax1.set_title("2026年1-6月销售额与增长率", fontsize=18, fontweight="bold", pad=18)
    handles = [bars, line]
    labels = ["销售额（左轴）", "增长率（右轴）"]
    ax1.legend(handles, labels, loc="upper left", frameon=False, fontsize=10)

    path = output_dir(BASE_DIR) / "双轴图_销售与增长.png"
    return save_figure(fig, path)


def draw_dashboard():
    """2x2 布局：总览、趋势、投入产出、渠道占比。"""
    setup_chinese_font()
    fig, axs = plt.subplots(2, 2, figsize=(12, 9), dpi=200)
    fig.suptitle("2026年度经营分析仪表盘", fontsize=20, fontweight="bold", y=0.98)

    # 左上：季度达标情况，低于目标红色，达标绿色
    colors = [COLORS["red"] if value < QUARTER_TARGET else COLORS["green"] for value in QUARTER_SALES]
    bars = axs[0, 0].bar(QUARTERS, QUARTER_SALES, color=colors, width=0.55, alpha=0.85)
    axs[0, 0].axhline(
        QUARTER_TARGET,
        color=COLORS["red"],
        linestyle="--",
        linewidth=1.2,
        label=f"目标 {QUARTER_TARGET}",
    )
    add_bar_labels(axs[0, 0], bars, fmt="{:.0f}", dy=4, fontsize=9)
    axs[0, 0].set_title("季度销售额与目标", fontsize=13, fontweight="bold")
    axs[0, 0].set_ylabel("销售额（万元）")
    axs[0, 0].set_ylim(0, max(QUARTER_SALES) * 1.3)
    axs[0, 0].legend(frameon=False, fontsize=9)
    style_axes(axs[0, 0])

    # 右上：两个渠道的季度走势
    axs[0, 1].plot(
        QUARTERS,
        DIRECT_Q,
        marker="o",
        linewidth=2.2,
        color=COLORS["blue"],
        label="直营",
    )
    axs[0, 1].plot(
        QUARTERS,
        PARTNER_Q,
        marker="s",
        linewidth=2.0,
        color=COLORS["orange"],
        label="分销",
    )
    axs[0, 1].set_title("渠道季度趋势", fontsize=13, fontweight="bold")
    axs[0, 1].set_ylabel("销售额（万元）")
    axs[0, 1].legend(frameon=False, fontsize=9)
    style_axes(axs[0, 1])

    # 左下：广告投入与销售额的关系
    rng = np.random.default_rng(42)
    ad_spend = rng.uniform(10, 60, 45)
    sales_scatter = 2.6 * ad_spend + rng.normal(0, 16, 45) + 35
    axs[1, 0].scatter(
        ad_spend,
        sales_scatter,
        s=34,
        alpha=0.65,
        color=COLORS["teal"],
        edgecolors="white",
        linewidths=0.6,
    )
    slope, intercept = np.polyfit(ad_spend, sales_scatter, 1)
    x_line = np.linspace(ad_spend.min(), ad_spend.max(), 100)
    axs[1, 0].plot(x_line, slope * x_line + intercept, color=COLORS["red"], linewidth=1.5, linestyle="--")
    axs[1, 0].set_title("广告投入与销售额", fontsize=13, fontweight="bold")
    axs[1, 0].set_xlabel("广告投入（万元）")
    axs[1, 0].set_ylabel("销售额（万元）")
    style_axes(axs[1, 0], grid_axis="both")

    # 右下：渠道占比
    axs[1, 1].pie(
        CHANNEL_SHARE,
        labels=CHANNEL_NAMES,
        autopct="%1.1f%%",
        startangle=90,
        colors=[COLORS["blue"], COLORS["orange"], COLORS["green"]],
        wedgeprops={"edgecolor": "white", "linewidth": 2},
        textprops={"fontsize": 11},
    )
    axs[1, 1].set_title("渠道销售占比", fontsize=13, fontweight="bold")

    fig.tight_layout(rect=(0, 0, 1, 0.94))
    path = output_dir(BASE_DIR) / "经营仪表盘_2x2.png"
    return save_figure(fig, path)


def main():
    print("=" * 60)
    print("第5课：双轴图 + 2x2 子图布局")
    print("=" * 60)
    print(f"月度销售额：{SALES}")
    print(f"月度增长率：{GROWTH}")
    print("说明：左轴金额用柱状图，右轴百分比用折线图，互不挤压。\n")

    p1 = draw_dual_axis()
    p2 = draw_dashboard()

    print("\n完成：")
    print(" -", p1)
    print(" -", p2)


if __name__ == "__main__":
    main()
