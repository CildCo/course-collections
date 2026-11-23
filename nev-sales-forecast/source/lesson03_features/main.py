"""第 3 课：时间特征、滞后特征和滚动特征。"""
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
    save_json,
    setup_plot,
)

FEATURES = [
    "Year",
    "Month",
    "Quarter",
    "Month_Sin",
    "Month_Cos",
    "Trend",
    "Trend_Squared",
    "Lag_1",
    "Lag_2",
    "Lag_3",
    "Lag_6",
    "Lag_12",
    "Rolling_Mean_3",
    "Rolling_Mean_6",
    "Rolling_Mean_12",
    "Rolling_Std_3",
    "Rolling_Std_6",
    "Rolling_Std_12",
    "Rolling_Max_3",
    "Rolling_Max_6",
    "Rolling_Max_12",
    "Growth_1",
    "Growth_12",
    "Brand_Share",
]


def feature_rows(frame: pd.DataFrame, market_total: pd.Series) -> pd.DataFrame:
    frame = frame.sort_values("统计月份").reset_index(drop=True)
    sales = frame["销量"].astype(float).to_numpy()
    rows = []
    for index, row in frame.iterrows():
        date = row["统计月份"]
        history = sales[:index]
        if len(history) < 12:
            continue
        record = {
            "统计月份": date,
            "品牌/厂商": row["品牌/厂商"],
            "销量": sales[index],
            "Year": date.year,
            "Month": date.month,
            "Quarter": date.quarter,
            "Month_Sin": np.sin(2 * np.pi * date.month / 12),
            "Month_Cos": np.cos(2 * np.pi * date.month / 12),
            "Trend": index,
            "Trend_Squared": index ** 2,
        }
        for lag in (1, 2, 3, 6, 12):
            record[f"Lag_{lag}"] = sales[index - lag]
        for window in (3, 6, 12):
            window_values = history[-window:]
            record[f"Rolling_Mean_{window}"] = float(np.mean(window_values))
            record[f"Rolling_Std_{window}"] = float(np.std(window_values, ddof=1))
            record[f"Rolling_Max_{window}"] = float(np.max(window_values))
        record["Growth_1"] = sales[index - 1] / sales[index - 2] - 1 if sales[index - 2] else 0.0
        record["Growth_12"] = sales[index - 1] / sales[index - 13] - 1 if sales[index - 13] else 0.0
        previous_month = date - pd.DateOffset(months=1)
        total = market_total.get(previous_month, np.nan)
        record["Brand_Share"] = sales[index - 1] / total if total and not pd.isna(total) else np.nan
        rows.append(record)
    return pd.DataFrame(rows)


def main() -> None:
    setup_plot()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    data = ensure_data()
    last_month = data["统计月份"].max()
    recent_start = last_month - pd.DateOffset(months=12)
    recent = data[data["统计月份"] > recent_start]
    top_brands = recent.groupby("品牌/厂商")["销量"].sum().nlargest(5).index.tolist()
    print(f"最近 12 个月 Top 5 品牌：{top_brands}")

    brand_month = (
        data[data["品牌/厂商"].isin(top_brands)]
        .groupby(["统计月份", "品牌/厂商"], as_index=False)["销量"].sum()
    )
    market_total = data.groupby("统计月份")["销量"].sum()

    frames = []
    for brand in top_brands:
        frames.append(feature_rows(brand_month[brand_month["品牌/厂商"] == brand], market_total))
    features = pd.concat(frames, ignore_index=True).dropna(subset=FEATURES + ["销量"])
    features.to_csv(PROCESSED_DIR / "features.csv", index=False, encoding="utf-8-sig")
    save_json(PROCESSED_DIR / "feature_list.json", {"features": FEATURES, "top_brands": top_brands})

    print(f"特征表：{len(features)} 行 × {len(features.columns)} 列")
    for brand in top_brands:
        count = len(features[features["品牌/厂商"] == brand])
        print(f"  {brand}：{count} 条可用样本")

    # 品牌份额趋势
    share = data.pivot_table(index="统计月份", columns="品牌/厂商", values="销量", aggfunc="sum").fillna(0)
    share = share.div(share.sum(axis=1), axis=0) * 100
    years = data.groupby("年份")["统计月份"].max()
    yearly_share = share.groupby(share.index.year).mean()
    fig, ax = plt.subplots(figsize=(10, 5.2))
    for brand, color in zip(top_brands, [TEAL, BLUE, GOLD, RED, "#8E44AD"]):
        if brand in yearly_share:
            ax.plot(yearly_share.index, yearly_share[brand], marker="o", linewidth=1.8, label=brand, color=color)
    ax.set_title("Top 5 品牌市场份额变化", fontsize=14, fontweight="bold", color=NAVY)
    ax.set_ylabel("%")
    ax.legend(frameon=False, ncol=3, fontsize=9)
    ax.grid(alpha=0.22)
    fig.savefig(OUTPUT_DIR / "品牌份额.png")
    plt.close(fig)

    # 滞后相关：过去几个月与当前销量的关系
    sample_brand = top_brands[0]
    sample = brand_month[brand_month["品牌/厂商"] == sample_brand].sort_values("统计月份")
    series = sample["销量"].astype(float).reset_index(drop=True)
    correlations = [series.autocorr(lag=lag) for lag in range(1, 13)]
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.bar(range(1, 13), correlations, color=[TEAL if value > 0 else RED for value in correlations])
    ax.set_title(f"{sample_brand} 销量的滞后相关性", fontsize=14, fontweight="bold", color=NAVY)
    ax.set_xlabel("滞后月数")
    ax.set_ylabel("相关系数")
    ax.grid(axis="y", alpha=0.22)
    fig.savefig(OUTPUT_DIR / "滞后相关性.png")
    plt.close(fig)

    print(f"\n特征表：{PROCESSED_DIR / 'features.csv'}")
    print(f"图表已保存：{OUTPUT_DIR / '品牌份额.png'}、{OUTPUT_DIR / '滞后相关性.png'}")


if __name__ == "__main__":
    main()
