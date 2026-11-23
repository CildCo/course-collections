# 第7课：实战闭环，从原始 CSV 到自动可视化报告
# 运行：python main.py

import base64
import html
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR.parent))

import numpy as np
import pandas as pd

from common import (
    COLORS,
    data_dir,
    output_dir,
    plt,
    save_figure,
    setup_chinese_font,
    style_axes,
)

try:
    from pyecharts import options as opts
    from pyecharts.charts import Bar, Line

    HAS_PYECHARTS = True
except ImportError:
    HAS_PYECHARTS = False

BRANCHES = [
    ("北京", 118, 6.0),
    ("上海", 150, 8.0),
    ("广州", 105, -3.5),
    ("成都", 82, 5.0),
    ("武汉", 92, 2.5),
]


def make_raw_data(path):
    """造一份带缺失、重复、负数和极端值的原始销售表。"""
    rng = np.random.default_rng(20261021)
    rows = []
    for branch, base, slope in BRANCHES:
        for month in range(1, 7):
            value = base + slope * month + rng.normal(0, 6)
            rows.append(
                {
                    "分公司": branch,
                    "月份": f"{month}月",
                    "销售额": round(max(value, 5), 1),
                }
            )
    df = pd.DataFrame(rows)

    # 人为制造一些常见脏数据
    df.loc[(df["分公司"] == "北京") & (df["月份"] == "3月"), "销售额"] = np.nan
    df.loc[(df["分公司"] == "成都") & (df["月份"] == "5月"), "销售额"] = np.nan
    df.loc[(df["分公司"] == "广州") & (df["月份"] == "4月"), "销售额"] = -50
    df.loc[(df["分公司"] == "上海") & (df["月份"] == "2月"), "销售额"] = 5000
    df = pd.concat([df, df.tail(1)], ignore_index=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"原始数据：{path}（{len(df)} 行，含缺失、重复、负数和极端值）")
    return df


def clean_data(raw_df):
    """去重、转数字、处理负数、补缺失、封顶异常值。"""
    stats = {}
    stats["原始行数"] = len(raw_df)

    df = raw_df.drop_duplicates().copy()
    stats["删除重复"] = stats["原始行数"] - len(df)

    df["销售额"] = pd.to_numeric(df["销售额"], errors="coerce")
    stats["负数记录"] = int((df["销售额"] < 0).sum())
    df.loc[df["销售额"] < 0, "销售额"] = np.nan

    stats["缺失值"] = int(df["销售额"].isna().sum())
    df["销售额"] = df.groupby("分公司")["销售额"].transform(
        lambda series: series.fillna(series.median())
    )
    df["销售额"] = df["销售额"].fillna(df["销售额"].median())

    # 超过本组中位数 2 倍的数值按异常处理，封顶到 2 倍中位数
    before = df["销售额"].copy()
    df["销售额"] = df.groupby("分公司")["销售额"].transform(
        lambda series: series.clip(lower=0, upper=series.median() * 2)
    )
    stats["封顶异常值"] = int((~np.isclose(before, df["销售额"])).sum())

    df["月份序号"] = df["月份"].str.replace("月", "", regex=False).astype(int)
    df = df.sort_values(["分公司", "月份序号"]).reset_index(drop=True)
    df["环比"] = df.groupby("分公司")["销售额"].pct_change()
    stats["清洗后行数"] = len(df)
    return df, stats


def summarize(df):
    """按分公司汇总总额和首尾月增长率。"""
    rows = []
    for branch, group in df.groupby("分公司"):
        group = group.sort_values("月份序号")
        total = float(group["销售额"].sum())
        first = float(group["销售额"].iloc[0])
        last = float(group["销售额"].iloc[-1])
        growth = (last - first) / first if first else 0.0
        rows.append(
            {
                "分公司": branch,
                "总销售额": total,
                "首月": first,
                "末月": last,
                "增长率": growth,
                "状态": "需关注" if growth < 0 else "正常",
            }
        )
    summary = pd.DataFrame(rows).sort_values("总销售额", ascending=False).reset_index(drop=True)
    monthly = (
        df.groupby("月份序号")["销售额"]
        .sum()
        .reset_index()
        .rename(columns={"销售额": "总销售额"})
    )
    monthly["环比"] = monthly["总销售额"].pct_change().fillna(0)
    return summary, monthly


def plot_monthly(monthly, path):
    setup_chinese_font()
    labels = [f"{int(m)}月" for m in monthly["月份序号"]]
    values = monthly["总销售额"].tolist()
    fig, ax = plt.subplots(figsize=(10, 5.6), dpi=200)
    x = list(range(len(labels)))
    ax.plot(
        x,
        values,
        color=COLORS["blue"],
        linewidth=2.6,
        marker="o",
        markersize=8,
        markerfacecolor="white",
        markeredgewidth=2,
    )
    ax.fill_between(x, values, min(values) - 50, color=COLORS["blue"], alpha=0.10)
    for xi, value in zip(x, values):
        ax.annotate(
            f"{value:.0f}",
            xy=(xi, value),
            xytext=(0, 10),
            textcoords="offset points",
            ha="center",
            fontsize=10,
            fontweight="bold",
            color=COLORS["dark_blue"],
        )
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(min(values) - 80, max(values) + 70)
    ax.set_title("2026年上半年分公司总销售额趋势", fontsize=17, fontweight="bold", pad=14)
    ax.set_xlabel("月份")
    ax.set_ylabel("销售额（万元）")
    style_axes(ax)
    return save_figure(fig, path)


def plot_branches(summary, path):
    setup_chinese_font()
    names = summary["分公司"].tolist()
    totals = summary["总销售额"].tolist()
    growths = summary["增长率"].tolist()
    colors = [COLORS["red"] if value < 0 else COLORS["blue"] for value in growths]

    fig, ax = plt.subplots(figsize=(10, 5.6), dpi=200)
    bars = ax.barh(names[::-1], totals[::-1], color=colors[::-1], height=0.55, alpha=0.88)
    ax.bar_label(bars, fmt="%.0f", padding=4, fontsize=10, fontweight="bold")
    for bar, growth in zip(bars, growths[::-1]):
        ax.text(
            bar.get_width() + 22,
            bar.get_y() + bar.get_height() / 2,
            f"{growth:+.1%}",
            va="center",
            fontsize=10,
            color=COLORS["red"] if growth < 0 else COLORS["green"],
            fontweight="bold",
        )
    ax.set_xlim(0, max(totals) * 1.22)
    ax.set_title("分公司销售总额与首尾月增长率", fontsize=17, fontweight="bold", pad=14)
    ax.set_xlabel("总销售额（万元）")
    ax.set_ylabel("分公司")
    style_axes(ax, grid_axis="x")
    return save_figure(fig, path)


def plot_heatmap(df, branch_order, path):
    setup_chinese_font()
    pivot = df.pivot_table(
        index="分公司", columns="月份序号", values="销售额", aggfunc="sum"
    ).reindex(branch_order)

    fig, ax = plt.subplots(figsize=(10, 5.4), dpi=200)
    image = ax.imshow(pivot.values, cmap="YlGnBu", aspect="auto")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([f"{int(m)}月" for m in pivot.columns])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_title("分公司月度销售额热力图", fontsize=17, fontweight="bold", pad=14)
    ax.set_xlabel("月份")
    ax.set_ylabel("分公司")

    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            value = pivot.values[i, j]
            color = "white" if value > np.nanmax(pivot.values) * 0.62 else "#1B2631"
            ax.text(j, i, f"{value:.0f}", ha="center", va="center", fontsize=9, color=color)

    colorbar = fig.colorbar(image, ax=ax, fraction=0.035, pad=0.02)
    colorbar.set_label("销售额（万元）")
    return save_figure(fig, path)


def build_interactive(monthly, path):
    """用 Pyecharts 生成柱状图 + 右轴增长率的交互页。"""
    months = [f"{int(m)}月" for m in monthly["月份序号"]]
    totals = [round(value, 1) for value in monthly["总销售额"]]
    growth = [round(value * 100, 1) for value in monthly["环比"]]

    bar = (
        Bar(init_opts=opts.InitOpts(width="1000px", height="540px", theme="light"))
        .add_xaxis(months)
        .add_yaxis(
            "总销售额",
            totals,
            label_opts=opts.LabelOpts(is_show=True, position="top"),
        )
        .extend_axis(
            yaxis=opts.AxisOpts(
                name="环比（%）",
                type_="value",
                position="right",
                axislabel_opts=opts.LabelOpts(formatter="{value}%"),
            )
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="月度销售总览",
                subtitle="柱状看金额，折线看环比",
            ),
            xaxis_opts=opts.AxisOpts(name="月份"),
            yaxis_opts=opts.AxisOpts(name="销售额（万元）"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
            legend_opts=opts.LegendOpts(pos_top="6%"),
            toolbox_opts=opts.ToolboxOpts(is_show=True),
        )
    )
    line = (
        Line()
        .add_xaxis(months)
        .add_yaxis(
            "环比增长",
            growth,
            yaxis_index=1,
            is_smooth=True,
            symbol="circle",
            symbol_size=7,
            label_opts=opts.LabelOpts(is_show=True, formatter="{c}%"),
            linestyle_opts=opts.LineStyleOpts(color="#E74C3C", width=2.5),
            itemstyle_opts=opts.ItemStyleOpts(color="#E74C3C"),
        )
    )
    bar.overlap(line)
    bar.render(str(path))
    print(f"已生成交互图表：{path}")
    return path


def image_base64(path):
    return base64.b64encode(Path(path).read_bytes()).decode("ascii")


def build_report(path, summary, stats, image_paths, interactive_path):
    """把指标、清洗结果、图片和交互页拼成一个 HTML 报告。"""
    total_sales = float(summary["总销售额"].sum())
    warning_count = int((summary["增长率"] < 0).sum())

    card_html = f"""
    <div class="cards">
      <div class="card"><span>总销售额</span><strong>{total_sales:,.0f} 万元</strong></div>
      <div class="card"><span>分公司数量</span><strong>{len(summary)} 家</strong></div>
      <div class="card"><span>清洗后记录</span><strong>{stats['清洗后行数']} 行</strong></div>
      <div class="card warning"><span>需关注</span><strong>{warning_count} 家</strong></div>
    </div>
    """

    rows = []
    for _, row in summary.iterrows():
        status_class = "bad" if row["增长率"] < 0 else "good"
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(row['分公司']))}</td>"
            f"<td>{row['总销售额']:.1f}</td>"
            f"<td>{row['首月']:.1f}</td>"
            f"<td>{row['末月']:.1f}</td>"
            f"<td class='{status_class}'>{row['增长率']:+.1%}</td>"
            f"<td><span class='tag {status_class}'>{html.escape(str(row['状态']))}</span></td>"
            "</tr>"
        )
    table_html = "".join(rows)

    stat_rows = "".join(
        f"<li><span>{html.escape(str(key))}</span><b>{value}</b></li>"
        for key, value in stats.items()
    )

    image_blocks = []
    captions = ["月度总销售额趋势", "分公司销售对比", "分公司月度热力图"]
    for image_path, caption in zip(image_paths, captions):
        encoded = image_base64(image_path)
        image_blocks.append(
            f"<figure><img src='data:image/png;base64,{encoded}' alt='{caption}'>"
            f"<figcaption>{caption}</figcaption></figure>"
        )
    image_html = "".join(image_blocks)

    if interactive_path and Path(interactive_path).exists():
        interactive_html = (
            "<iframe src='interactive_charts.html' title='交互图表'></iframe>"
            "<p class='note'>交互页支持悬停查看数值、图例筛选和工具栏下载。</p>"
        )
    else:
        interactive_html = "<p class='note'>当前环境未安装 pyecharts，本报告只包含静态图。</p>"

    style = """
    * { box-sizing: border-box; }
    body { margin: 0; background: #EEF2F7; color: #1F2933;
           font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif; }
    .page { max-width: 1080px; margin: 0 auto; padding: 32px 24px 60px; }
    header { background: linear-gradient(135deg, #1F4E79, #2E86C1);
             color: #fff; border-radius: 16px; padding: 28px 32px; }
    header h1 { margin: 0 0 8px; font-size: 28px; }
    header p { margin: 0; opacity: .86; }
    .cards { display: grid; grid-template-columns: repeat(4, 1fr);
             gap: 14px; margin: 22px 0; }
    .card { background: #fff; border-radius: 12px; padding: 18px;
            box-shadow: 0 4px 14px rgba(31, 78, 121, .08); }
    .card span { display: block; color: #6B7280; font-size: 13px; margin-bottom: 8px; }
    .card strong { font-size: 24px; color: #1F4E79; }
    .card.warning strong { color: #C0392B; }
    h2 { font-size: 20px; margin: 30px 0 12px; color: #1F4E79; }
    table { width: 100%; border-collapse: collapse; background: #fff;
            border-radius: 12px; overflow: hidden; }
    th, td { padding: 12px 14px; text-align: center; border-bottom: 1px solid #E5EAF1; }
    th { background: #1F4E79; color: #fff; font-weight: 600; }
    tr:last-child td { border-bottom: none; }
    .good { color: #1E8449; font-weight: 600; }
    .bad { color: #C0392B; font-weight: 600; }
    .tag { display: inline-block; padding: 3px 9px; border-radius: 20px;
           font-size: 12px; font-weight: 600; }
    .tag.good { background: #E8F8F0; }
    .tag.bad { background: #FDEDEC; }
    ul.clean { list-style: none; padding: 0; display: grid;
               grid-template-columns: repeat(3, 1fr); gap: 10px; }
    ul.clean li { background: #fff; border-radius: 10px; padding: 12px 14px;
                  display: flex; justify-content: space-between; }
    ul.clean b { color: #1F4E79; }
    figure { margin: 0 0 20px; background: #fff; border-radius: 12px; padding: 14px;
             box-shadow: 0 4px 14px rgba(31, 78, 121, .06); }
    figure img { width: 100%; display: block; border-radius: 8px; }
    figcaption { text-align: center; color: #6B7280; font-size: 13px; padding-top: 10px; }
    iframe { width: 100%; height: 600px; border: 0; background: #fff;
             border-radius: 12px; box-shadow: 0 4px 14px rgba(31, 78, 121, .08); }
    .note { color: #6B7280; font-size: 13px; }
    footer { margin-top: 32px; color: #7B8794; font-size: 12px; text-align: center; }
    """

    document = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>2026年上半年经营分析报告</title>
<style>{style}</style>
</head>
<body>
<div class="page">
  <header>
    <h1>2026年上半年经营分析报告</h1>
    <p>数据范围：1-6月 · 5家分公司 · 自动清洗与汇总</p>
  </header>
  {card_html}
  <h2>分公司概览</h2>
  <table>
    <thead><tr><th>分公司</th><th>总销售额（万元）</th><th>首月</th><th>末月</th><th>增长率</th><th>状态</th></tr></thead>
    <tbody>{table_html}</tbody>
  </table>
  <h2>数据清洗记录</h2>
  <ul class="clean">{stat_rows}</ul>
  <h2>图表分析</h2>
  {image_html}
  <h2>交互图表</h2>
  {interactive_html}
  <footer>报告由本地脚本自动生成 · 数据与图片均保存在本课 output 目录</footer>
</div>
</body>
</html>
"""
    path.write_text(document, encoding="utf-8")
    print(f"已生成 HTML 报告：{path}")
    return path


def main():
    print("=" * 60)
    print("第7课：从原始数据到自动可视化报告")
    print("=" * 60)

    data_path = data_dir(BASE_DIR) / "raw_sales.csv"
    out = output_dir(BASE_DIR)

    raw_df = make_raw_data(data_path)
    cleaned_df, stats = clean_data(raw_df)
    cleaned_path = data_dir(BASE_DIR) / "cleaned_sales.csv"
    cleaned_df.to_csv(cleaned_path, index=False, encoding="utf-8-sig")
    print(f"清洗后数据：{cleaned_path}")

    print("\n清洗统计：")
    for key, value in stats.items():
        print(f" - {key}: {value}")

    summary, monthly = summarize(cleaned_df)
    print("\n分公司汇总：")
    print(summary[["分公司", "总销售额", "增长率", "状态"]].to_string(index=False))

    warnings = summary[summary["增长率"] < 0]
    if not warnings.empty:
        print("\n异常提醒：以下分公司出现负增长")
        for _, row in warnings.iterrows():
            print(f" - {row['分公司']}：{row['增长率']:+.1%}，建议复查数据并制定改进计划")
    else:
        print("\n异常提醒：未发现负增长。")

    p1 = plot_monthly(monthly, out / "月度趋势.png")
    p2 = plot_branches(summary, out / "分公司对比.png")
    p3 = plot_heatmap(cleaned_df, summary["分公司"].tolist(), out / "月度热力图.png")

    interactive_path = None
    if HAS_PYECHARTS:
        interactive_path = build_interactive(monthly, out / "interactive_charts.html")
    else:
        print("未安装 pyecharts，跳过交互图表。")

    report_path = build_report(
        out / "经营分析报告.html",
        summary,
        stats,
        [p1, p2, p3],
        interactive_path,
    )

    print("\n本课输出：")
    for path in [data_path, cleaned_path, p1, p2, p3, report_path]:
        print(" -", path)
    if interactive_path:
        print(" -", interactive_path)


if __name__ == "__main__":
    main()
