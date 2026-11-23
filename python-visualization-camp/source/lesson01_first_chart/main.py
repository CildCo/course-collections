# 第1课：选图思路、环境检查与第一张专业销售趋势图
# 运行：python main.py

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR.parent))

import matplotlib
from common import COLORS, output_dir, plt, save_figure, setup_chinese_font, style_axes


# 职场常见场景和对应图表，先选对图再动手
CHART_GUIDE = [
    ("看趋势", "折线图", "月度销售额、用户增长、访问量"),
    ("比大小", "柱状图", "部门业绩、渠道对比、季度目标"),
    ("看占比", "饼图/环形图", "渠道结构、费用构成"),
    ("看分布", "箱线图/散点图", "绩效分布、客户消费、异常值"),
    ("看关系", "散点图/热力图", "广告投入与销量、时段活跃度"),
]

MONTHS = ["1月", "2月", "3月", "4月", "5月", "6月"]
SALES = [118, 126, 139, 133, 158, 176]
TARGET = 160


def show_guide():
    print("职场选图清单")
    print("-" * 54)
    for scene, chart, example in CHART_GUIDE:
        print(f"{scene:<6} | {chart:<8} | {example}")
    print("-" * 54)
    print("原则：一张图只讲一个故事。\n")


def draw_sales_trend():
    """画一张带目标线、数值标签和重点标注的销售趋势图。"""
    setup_chinese_font()
    x = list(range(len(MONTHS)))

    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    ax.plot(
        x,
        SALES,
        color=COLORS["blue"],
        linewidth=2.8,
        marker="o",
        markersize=8,
        markerfacecolor="white",
        markeredgewidth=2.2,
        label="实际销售额",
    )

    # 线下浅色填充，让趋势更有层次
    ax.fill_between(x, SALES, min(SALES) - 12, color=COLORS["blue"], alpha=0.10)

    # 目标线放在背景层，不抢主角
    ax.axhline(
        y=TARGET,
        color=COLORS["red"],
        linestyle="--",
        linewidth=1.4,
        alpha=0.85,
        label=f"月度目标 {TARGET} 万元",
    )

    # 每个点上方标数值
    for xi, value in zip(x, SALES):
        ax.annotate(
            f"{value}",
            xy=(xi, value),
            xytext=(0, 11),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=11,
            color=COLORS["dark_blue"],
            fontweight="bold",
        )

    # 标出最高点，汇报时直接讲重点
    peak_index = SALES.index(max(SALES))
    ax.annotate(
        f"最高点 {SALES[peak_index]} 万元",
        xy=(peak_index, SALES[peak_index]),
        xytext=(-70, 28),
        textcoords="offset points",
        fontsize=10,
        color=COLORS["orange"],
        arrowprops=dict(arrowstyle="->", color=COLORS["orange"], lw=1.4),
    )

    ax.set_xticks(x)
    ax.set_xticklabels(MONTHS, fontsize=11)
    ax.set_ylim(min(SALES) - 20, max(SALES) + 25)
    ax.set_title("2026年上半年销售业绩趋势", fontsize=19, fontweight="bold", pad=18)
    ax.set_xlabel("月份", fontsize=12)
    ax.set_ylabel("销售额（万元）", fontsize=12)
    ax.tick_params(axis="y", labelsize=10)
    style_axes(ax)
    ax.legend(frameon=False, loc="upper left", fontsize=11)

    fig.text(
        0.5,
        0.005,
        "数据来源：销售部月度汇总  |  单位：万元",
        ha="center",
        fontsize=9,
        color="#777777",
    )

    path = output_dir(BASE_DIR) / "销售趋势图.png"
    save_figure(fig, path, dpi=220)
    return path


def main():
    print("=" * 60)
    print("第1课：告别丑图与乱码，画出第一张专业报表")
    print("=" * 60)

    show_guide()
    print(f"Matplotlib 版本：{matplotlib.__version__}")
    print(f"当前绘图后端：{matplotlib.get_backend()}（只出图，不弹窗）")
    print(f"首选中文字体：{setup_chinese_font()}")
    print("提示：如需换字体，改 common.py 里的 FONT_LIST 顺序即可。\n")

    path = draw_sales_trend()
    print(f"\n完成。打开图片查看效果：{path}")


if __name__ == "__main__":
    main()
