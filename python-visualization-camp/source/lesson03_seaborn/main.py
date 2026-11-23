# 第3课：用 Seaborn 画统计图，少写代码也能有咨询报告质感
# 运行：python main.py

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR.parent))

import numpy as np
import pandas as pd

from common import output_dir, plt, save_figure, setup_chinese_font, style_axes

import seaborn as sns


def make_sales_data():
    """模拟 3 个渠道、12 个月、每个渠道 4 家门店的销售明细。"""
    rng = np.random.default_rng(2026)
    rows = []
    channels = [
        ("直营", 120, 5.5, 8),
        ("分销", 92, 4.0, 10),
        ("线上", 70, 8.5, 12),
    ]
    for channel, base, slope, noise in channels:
        for month in range(1, 13):
            for store in range(1, 5):
                value = base + slope * month + (store - 2) * 4 + rng.normal(0, noise)
                rows.append(
                    {
                        "月份": f"{month}月",
                        "渠道": channel,
                        "门店": f"{channel}{store}店",
                        "销售额": round(float(value), 1),
                    }
                )
    return pd.DataFrame(rows)


def make_performance_data():
    """模拟三个部门的绩效评分，方便展示分布和离群点。"""
    rng = np.random.default_rng(88)
    rows = []
    plan = [("销售部", 86, 5), ("技术部", 78, 12), ("市场部", 81, 8)]
    for dept, mean, std in plan:
        for _ in range(24):
            score = float(np.clip(rng.normal(mean, std), 45, 100))
            rows.append({"部门": dept, "绩效": round(score, 1)})
    return pd.DataFrame(rows)


def plot_trend(df):
    """带 95% 置信区间的渠道趋势图。"""
    setup_chinese_font()
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=200)
    sns.lineplot(
        data=df,
        x="月份",
        y="销售额",
        hue="渠道",
        marker="o",
        linewidth=2.2,
        markersize=6,
        errorbar=("ci", 95),
        ax=ax,
    )
    ax.set_title("2026年各渠道销售趋势（阴影为95%置信区间）", fontsize=18, fontweight="bold", pad=16)
    ax.set_xlabel("月份", fontsize=12)
    ax.set_ylabel("销售额（万元）", fontsize=12)
    ax.tick_params(axis="x", rotation=0)
    style_axes(ax)
    ax.legend(title="", frameon=False, ncol=3, loc="upper left")
    path = output_dir(BASE_DIR) / "渠道趋势_置信区间.png"
    return save_figure(fig, path)


def plot_channel_bar(df):
    """渠道平均值对比，误差线表示标准差。"""
    setup_chinese_font()
    fig, ax = plt.subplots(figsize=(9, 6), dpi=200)
    sns.barplot(
        data=df,
        x="渠道",
        y="销售额",
        hue="渠道",
        legend=False,
        estimator="mean",
        errorbar="sd",
        palette="muted",
        capsize=0.12,
        ax=ax,
    )
    ax.bar_label(ax.containers[0], fmt="%.1f", padding=4, fontsize=11, fontweight="bold")
    ax.set_title("各渠道平均销售额对比", fontsize=18, fontweight="bold", pad=16)
    ax.set_xlabel("渠道", fontsize=12)
    ax.set_ylabel("平均销售额（万元）", fontsize=12)
    ax.set_ylim(0, df["销售额"].mean() * 2.1)
    style_axes(ax)
    path = output_dir(BASE_DIR) / "渠道均值对比.png"
    return save_figure(fig, path)


def plot_performance_box(df):
    """箱线图看整体分布，散点看每个人的具体分数。"""
    setup_chinese_font()
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=200)
    sns.boxplot(
        data=df,
        x="部门",
        y="绩效",
        hue="部门",
        legend=False,
        palette="Set2",
        width=0.48,
        linewidth=1.8,
        showfliers=False,
        ax=ax,
    )
    sns.stripplot(
        data=df,
        x="部门",
        y="绩效",
        color="#2C3E50",
        size=4.5,
        alpha=0.55,
        jitter=0.16,
        ax=ax,
    )
    ax.set_title("各部门绩效分布（箱线图 + 散点）", fontsize=18, fontweight="bold", pad=16)
    ax.set_xlabel("部门", fontsize=12)
    ax.set_ylabel("绩效评分", fontsize=12)
    ax.set_ylim(40, 105)
    style_axes(ax)
    path = output_dir(BASE_DIR) / "部门绩效分布.png"
    return save_figure(fig, path)


def main():
    print("=" * 60)
    print("第3课：用 Seaborn 一键生成咨询级统计图表")
    print("=" * 60)

    # 全局风格：白底网格 + 柔和配色，适合正式汇报
    sns.set_theme(style="whitegrid", context="notebook")
    sns.set_palette("muted")
    sns.set_context("notebook", font_scale=1.05)
    setup_chinese_font()  # Seaborn 设置风格后，再把中文字体补回来

    sales_df = make_sales_data()
    perf_df = make_performance_data()

    print(f"销售明细：{len(sales_df)} 行，渠道：{', '.join(sales_df['渠道'].unique())}")
    print(f"绩效明细：{len(perf_df)} 行，部门：{', '.join(perf_df['部门'].unique())}\n")

    p1 = plot_trend(sales_df)
    p2 = plot_channel_bar(sales_df)
    p3 = plot_performance_box(perf_df)

    print("\n三张图已生成：")
    for path in (p1, p2, p3):
        print(" -", path)


if __name__ == "__main__":
    main()
