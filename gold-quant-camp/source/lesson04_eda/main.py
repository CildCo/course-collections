"""第 4 课：探索性数据分析。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from common import (
    BLUE,
    GOLD,
    NAVY,
    OUTPUT_DIR,
    PROCESSED_DIR,
    RED,
    add_indicators,
    ensure_data,
    setup_plot,
)


def main() -> None:
    setup_plot()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    processed = PROCESSED_DIR / "gold_pipeline.csv"
    if processed.exists():
        data = pd.read_csv(processed, index_col=0, parse_dates=True)
    else:
        data = add_indicators(ensure_data())
        data.to_csv(processed, encoding="utf-8-sig")

    data = data.ffill().bfill()
    data["MA_20"] = data["close"].rolling(20).mean()
    data["MA_60"] = data["close"].rolling(60).mean()
    data["Volatility_20"] = data["Return"].rolling(20).std() * (252 ** 0.5)

    print("数据体检")
    print(f"样本数：{len(data)}")
    print(f"时间范围：{data.index.min().date()} 至 {data.index.max().date()}")
    print(f"缺失值：{int(data.isna().sum().sum())}")
    print(f"重复日期：{int(data.index.duplicated().sum())}")
    print(f"年化收益：{data['Return'].mean() * 252:.2%}")
    print(f"年化波动：{data['Return'].std() * (252 ** 0.5):.2%}")

    # 1. 价格与均线
    view = data.tail(520)
    fig, ax = plt.subplots(figsize=(13, 5.4))
    ax.plot(view.index, view["close"], color=GOLD, linewidth=1.7, label="收盘价")
    ax.plot(view.index, view["MA_20"], color=NAVY, linewidth=1.0, linestyle="--", label="MA20")
    ax.plot(view.index, view["MA_60"], color=RED, linewidth=1.0, linestyle=":", label="MA60")
    ax.set_title("沪金主力价格与均线（近两年）", fontsize=15, fontweight="bold", color=NAVY)
    ax.set_ylabel("元/克")
    ax.legend(frameon=False)
    ax.grid(alpha=0.22)
    fig.savefig(OUTPUT_DIR / "价格走势.png")
    plt.close(fig)

    # 2. 收益率分布与波动率
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    returns = data["Return"].dropna()
    sns.histplot(returns, bins=45, kde=True, color=BLUE, ax=axes[0, 0])
    axes[0, 0].set_title("日收益率分布", loc="left")
    sns.boxplot(x=returns, color=GOLD, ax=axes[0, 1])
    axes[0, 1].set_title("收益率箱线图：看极端值", loc="left")
    axes[1, 0].plot(data.index, data["Volatility_20"], color=RED, linewidth=1.0)
    axes[1, 0].set_title("20 日年化波动率", loc="left")
    axes[1, 0].grid(alpha=0.22)
    axes[1, 1].plot(data.index, data["open_interest"], color=NAVY, linewidth=1.0)
    axes[1, 1].set_title("持仓量变化", loc="left")
    axes[1, 1].grid(alpha=0.22)
    for ax in axes.flat:
        ax.tick_params(labelsize=8)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "收益率分布.png")
    plt.close(fig)

    # 3. 相关性热力图
    columns = [
        "close",
        "Silver_Close",
        "Copper_Close",
        "Oil_Close",
        "Gold_Silver_Ratio",
        "Copper_Gold_Ratio",
        "Oil_Gold_Ratio",
        "Return",
        "Volatility_20",
        "RSI_14",
    ]
    columns = [column for column in columns if column in data.columns]
    corr = data[columns].corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="RdYlBu_r",
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8},
        ax=ax,
    )
    ax.set_title("关键资产与因子相关性", fontsize=15, fontweight="bold", color=NAVY, pad=16)
    fig.savefig(OUTPUT_DIR / "相关性热力图.png")
    plt.close(fig)

    stats = data.describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).T
    stats["skew"] = data.skew(numeric_only=True)
    stats["kurtosis"] = data.kurtosis(numeric_only=True)
    stats.to_csv(PROCESSED_DIR / "eda_statistics.csv", encoding="utf-8-sig")

    print(f"\n图表已保存到：{OUTPUT_DIR}")
    print("重点看三件事：收益率厚尾、波动率聚集、金银比和铜金比是否提供额外信息。")


if __name__ == "__main__":
    main()
