"""第 2 课：特征工程与销售可视化。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from common import BLUE, GOLD, NAVY, OUTPUT_DIR, PROCESSED_DIR, RED, TEAL, ensure_orders, setup_plot


def main() -> None:
    setup_plot()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    data = ensure_orders()
    data = data.copy()
    data["月份名称"] = data["下单日期"].dt.strftime("%Y-%m")
    data["客单价"] = data["销售额"] / data["数量"].clip(lower=1)
    data.to_csv(PROCESSED_DIR / "orders_features.csv", index=False, encoding="utf-8-sig")

    quarterly = data.groupby(["年份", "季度"], as_index=False)["销售额"].sum()
    quarterly["期间"] = quarterly["年份"].astype(str) + "Q" + quarterly["季度"].astype(str)
    category_quarter = data.pivot_table(index="产品类别", columns="季度", values="销售额", aggfunc="sum", fill_value=0)
    region = data.groupby("地区", as_index=False)["销售额"].sum().sort_values("销售额", ascending=False)
    category = data.groupby("产品类别", as_index=False)["销售额"].sum().sort_values("销售额", ascending=False)

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle("销售数据特征分析与可视化", fontsize=17, fontweight="bold", color=NAVY)

    ax1 = axes[0, 0]
    ax1.plot(quarterly["期间"], quarterly["销售额"] / 10000, color=BLUE, marker="o", linewidth=2)
    for x, y in zip(quarterly["期间"], quarterly["销售额"] / 10000):
        ax1.text(x, y + quarterly["销售额"].max() / 10000 * 0.02, f"{y:.0f}", ha="center", fontsize=7, color="#566573")
    ax1.set_title("季度销售额趋势", loc="left", color=NAVY)
    ax1.set_ylabel("万元")
    ax1.tick_params(axis="x", rotation=35, labelsize=7)
    ax1.grid(alpha=0.22)

    ax2 = axes[0, 1]
    sns.heatmap(category_quarter / 10000, annot=True, fmt=".0f", cmap="YlGnBu", linewidths=0.5, ax=ax2, cbar=False)
    ax2.set_title("品类 × 季度销售额（万元）", loc="left", color=NAVY)
    ax2.set_xlabel("季度")
    ax2.set_ylabel("")

    ax3 = axes[1, 0]
    sns.boxplot(data=data, x="是否周末", y="销售额", color=TEAL, ax=ax3, showfliers=False)
    ax3.set_xticks([0, 1], ["工作日", "周末"])
    ax3.set_title("工作日 vs 周末客单价分布", loc="left", color=NAVY)
    ax3.set_xlabel("")
    ax3.grid(axis="y", alpha=0.2)

    ax4 = axes[1, 1]
    bars = ax4.bar(region["地区"], region["销售额"] / 10000, color=[BLUE, TEAL, GOLD, "#8E44AD", RED])
    for bar in bars:
        ax4.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{bar.get_height():.0f}", ha="center", va="bottom", fontsize=8)
    ax4.set_title("地区销售额排行", loc="left", color=NAVY)
    ax4.set_ylabel("万元")
    ax4.grid(axis="y", alpha=0.2)

    for ax in axes.flat:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(OUTPUT_DIR / "销售分析仪表盘.png")
    plt.close(fig)

    print("特征工程完成")
    print(f"订单数：{len(data)}，客户数：{data['客户ID'].nunique()}")
    print(f"销售额合计：{data['销售额'].sum() / 10000:.1f} 万元")
    print(f"最高季度：{quarterly.loc[quarterly['销售额'].idxmax(), '期间']}")
    print(f"第一品类：{category.iloc[0]['产品类别']}")
    print(f"周末订单占比：{data['是否周末'].mean():.1%}")
    print(f"\n仪表盘已保存：{OUTPUT_DIR / '销售分析仪表盘.png'}")


if __name__ == "__main__":
    main()
