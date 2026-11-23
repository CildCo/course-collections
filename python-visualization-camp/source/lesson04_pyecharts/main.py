# 第4课：用 Pyecharts 做会动的交互报表
# 运行：python main.py

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR.parent))

from common import output_dir

from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Timeline

MONTHS = ["1月", "2月", "3月", "4月", "5月", "6月"]
DIRECT = [120, 140, 132, 160, 180, 200]
PARTNER = [86, 94, 102, 110, 124, 136]
TARGET = [125, 135, 145, 155, 170, 185]

PRODUCTS = ["A款", "B款", "C款", "D款"]
PRODUCT_SALES = {
    "1月": [42, 31, 25, 18],
    "2月": [48, 35, 28, 22],
    "3月": [45, 38, 30, 25],
    "4月": [55, 42, 33, 28],
    "5月": [61, 48, 36, 31],
    "6月": [68, 53, 40, 35],
}


def build_bar():
    """双系列交互柱状图，带工具栏和悬停提示。"""
    chart = (
        Bar(init_opts=opts.InitOpts(width="1000px", height="560px", theme="light"))
        .add_xaxis(MONTHS)
        .add_yaxis(
            "直营渠道",
            DIRECT,
            label_opts=opts.LabelOpts(is_show=True, position="top"),
        )
        .add_yaxis(
            "分销渠道",
            PARTNER,
            label_opts=opts.LabelOpts(is_show=True, position="top"),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="2026年上半年渠道销售",
                subtitle="鼠标悬停看明细，点击图例可隐藏系列",
                pos_left="2%",
            ),
            xaxis_opts=opts.AxisOpts(name="月份"),
            yaxis_opts=opts.AxisOpts(name="销售额（万元）"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
            toolbox_opts=opts.ToolboxOpts(is_show=True),
            legend_opts=opts.LegendOpts(pos_top="6%"),
        )
    )
    path = output_dir(BASE_DIR) / "interactive_bar.html"
    chart.render(str(path))
    print(f"已生成交互柱状图：{path}")
    return path


def build_timeline():
    """把 6 个月拆成 6 帧，点播放就能看柱子变化。"""
    timeline = Timeline(
        init_opts=opts.InitOpts(width="1000px", height="560px", theme="light")
    )
    timeline.add_schema(
        play_interval=1200,
        is_auto_play=True,
        is_loop_play=True,
        is_timeline_show=True,
    )
    for month in MONTHS:
        frame = (
            Bar()
            .add_xaxis(PRODUCTS)
            .add_yaxis(
                "销量",
                PRODUCT_SALES[month],
                label_opts=opts.LabelOpts(is_show=True, position="top"),
                itemstyle_opts=opts.ItemStyleOpts(color="#2E86C1"),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title=f"{month} 产品销量", pos_left="2%"),
                xaxis_opts=opts.AxisOpts(name="产品"),
                yaxis_opts=opts.AxisOpts(name="销量（件）", max_=80),
                legend_opts=opts.LegendOpts(is_show=False),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
            )
        )
        timeline.add(frame, month)

    path = output_dir(BASE_DIR) / "timeline_sales.html"
    timeline.render(str(path))
    print(f"已生成时间轴动画：{path}")
    return path


def build_line():
    """多系列折线图，支持区域缩放和图片下载。"""
    chart = (
        Line(init_opts=opts.InitOpts(width="1000px", height="560px", theme="light"))
        .add_xaxis(MONTHS)
        .add_yaxis(
            "实际销售额",
            [direct + partner for direct, partner in zip(DIRECT, PARTNER)],
            is_smooth=True,
            symbol="circle",
            symbol_size=8,
            label_opts=opts.LabelOpts(is_show=True),
            linestyle_opts=opts.LineStyleOpts(color="#2E86C1", width=3),
            itemstyle_opts=opts.ItemStyleOpts(color="#2E86C1"),
        )
        .add_yaxis(
            "月度目标",
            TARGET,
            is_smooth=True,
            symbol="emptyCircle",
            symbol_size=7,
            label_opts=opts.LabelOpts(is_show=False),
            linestyle_opts=opts.LineStyleOpts(color="#E74C3C", width=2, type_="dashed"),
            itemstyle_opts=opts.ItemStyleOpts(color="#E74C3C"),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="销售完成情况", subtitle="可滚动缩放查看细节"),
            xaxis_opts=opts.AxisOpts(name="月份"),
            yaxis_opts=opts.AxisOpts(name="销售额（万元）"),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            toolbox_opts=opts.ToolboxOpts(is_show=True),
            datazoom_opts=[opts.DataZoomOpts(range_start=0, range_end=100)],
            legend_opts=opts.LegendOpts(pos_top="6%"),
        )
    )
    path = output_dir(BASE_DIR) / "multi_line.html"
    chart.render(str(path))
    print(f"已生成多系列折线图：{path}")
    return path


def main():
    print("=" * 60)
    print("第4课：用 Pyecharts 制作会动的报表")
    print("=" * 60)
    print("生成的都是独立 HTML 文件，双击即可在浏览器中打开。\n")

    paths = [build_bar(), build_timeline(), build_line()]

    print("\n完成。三个文件都可以直接发给同事：")
    for path in paths:
        print(" -", path)
    print("\n提示：HTML 里的 ECharts 脚本默认从公共 CDN 加载，首次打开需要联网。")


if __name__ == "__main__":
    main()
