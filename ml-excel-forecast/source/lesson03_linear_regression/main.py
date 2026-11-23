"""第 3 课：线性回归预测下季度销量。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

from common import BLUE, GOLD, NAVY, OUTPUT_DIR, PROCESSED_DIR, RED, ensure_orders, save_json, setup_plot


def feature_row(history: pd.Series, date: pd.Timestamp) -> dict:
    values = history.to_numpy(dtype=float)
    return {
        "月份": date.month,
        "季度": date.quarter,
        "月份Sin": np.sin(2 * np.pi * date.month / 12),
        "月份Cos": np.cos(2 * np.pi * date.month / 12),
        "滞后1": values[-1],
        "滞后2": values[-2],
        "滞后3": values[-3],
        "滞后12": values[-12] if len(values) >= 12 else float(np.mean(values)),
        "滚动3月均值": float(np.mean(values[-3:])),
        "滚动6月均值": float(np.mean(values[-6:])),
        "趋势": len(values),
    }


def main() -> None:
    setup_plot()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    orders = ensure_orders()
    monthly = orders.groupby(orders["下单日期"].dt.to_period("M"))["销售额"].sum()
    monthly.index = monthly.index.to_timestamp()
    monthly = monthly.sort_index()

    rows = []
    for index, date in enumerate(monthly.index):
        if index < 3:
            continue
        rows.append(feature_row(monthly.iloc[:index], date))
    features = pd.DataFrame(rows, index=monthly.index[3:])
    features["销售额"] = monthly.values[3:]
    features.to_csv(PROCESSED_DIR / "sales_monthly_features.csv", encoding="utf-8-sig")

    train = features.iloc[:-6]
    validation = features.iloc[-6:]
    columns = ["月份", "季度", "月份Sin", "月份Cos", "滞后1", "滞后2", "滞后3", "滞后12", "滚动3月均值", "滚动6月均值", "趋势"]
    model = LinearRegression()
    model.fit(train[columns], train["销售额"])
    prediction = model.predict(validation[columns])
    mae = mean_absolute_error(validation["销售额"], prediction)
    r2 = r2_score(validation["销售额"], prediction)

    # 用全部历史重新训练，递归预测 2026 年 Q1。
    final_model = LinearRegression().fit(features[columns], features["销售额"])
    history = monthly.copy()
    future_dates = pd.date_range("2026-01-01", periods=3, freq="MS")
    future_rows = []
    for date in future_dates:
        row = feature_row(history, date)
        value = float(final_model.predict(pd.DataFrame([row])[columns])[0])
        future_rows.append({"月份": date, "预测销售额": value})
        history.loc[date] = value
    forecast = pd.DataFrame(future_rows)
    forecast.to_csv(PROCESSED_DIR / "sales_forecast.csv", index=False, encoding="utf-8-sig")
    save_json(
        PROCESSED_DIR / "sales_forecast_metrics.json",
        {
            "validation_mae": float(mae),
            "validation_r2": float(r2),
            "forecast_q1_2026": float(forecast["预测销售额"].sum()),
            "forecast": {row["月份"].strftime("%Y-%m"): float(row["预测销售额"]) for _, row in forecast.iterrows()},
        },
    )

    print("线性回归销量预测")
    print(f"训练样本：{len(train)}，验证样本：{len(validation)}")
    print(f"验证集 MAE：{mae:,.0f} 元")
    print(f"验证集 R2：{r2:.3f}")
    print("2026 年 Q1 预测：")
    for _, row in forecast.iterrows():
        print(f"  {row['月份']:%Y-%m}：{row['预测销售额']:,.0f} 元")

    fig, ax = plt.subplots(figsize=(13, 5))
    ax.plot(monthly.index, monthly.values / 10000, color=BLUE, linewidth=1.8, label="实际")
    ax.plot(forecast["月份"], forecast["预测销售额"] / 10000, color=RED, marker="o", linestyle="--", linewidth=2, label="预测")
    ax.fill_between(forecast["月份"], forecast["预测销售额"] / 10000 * 0.9, forecast["预测销售额"] / 10000 * 1.1, color=RED, alpha=0.12)
    ax.axvline(pd.Timestamp("2026-01-01"), color=GOLD, linestyle=":", linewidth=1)
    ax.set_title("线性回归：下季度销售额预测", fontsize=14, fontweight="bold", color=NAVY)
    ax.set_ylabel("万元")
    ax.legend(frameon=False)
    ax.grid(alpha=0.22)
    fig.savefig(OUTPUT_DIR / "销量预测.png")
    plt.close(fig)
    print(f"\n预测图已保存：{OUTPUT_DIR / '销量预测.png'}")


if __name__ == "__main__":
    main()
