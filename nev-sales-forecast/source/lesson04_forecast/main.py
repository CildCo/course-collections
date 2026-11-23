"""第 4 课：季节趋势模型与梯度提升树的融合预测。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score

from common import (
    BLUE,
    GOLD,
    NAVY,
    OUTPUT_DIR,
    PROCESSED_DIR,
    RED,
    TEAL,
    ensure_data,
    load_json,
    save_json,
    setup_plot,
)


class SeasonalTrendModel:
    """用线性趋势 + 傅里叶季节项模拟 Prophet 的可解释预测。"""

    def __init__(self, fourier_terms: int = 2, multiplicative: bool = True):
        self.fourier_terms = fourier_terms
        self.multiplicative = multiplicative
        self.model = None
        self.origin = None
        self.center = 0.0
        self.scale = 1.0
        self.residual_std = 0.0

    def _design(self, dates: pd.DatetimeIndex) -> np.ndarray:
        t = np.array([(date.year - self.origin.year) * 12 + (date.month - self.origin.month) for date in dates], dtype=float)
        t = (t - self.center) / self.scale
        columns = [np.ones(len(t)), t, t ** 2]
        for k in range(1, self.fourier_terms + 1):
            columns.append(np.sin(2 * np.pi * k * t * self.scale / 12))
            columns.append(np.cos(2 * np.pi * k * t * self.scale / 12))
        return np.column_stack(columns)

    def fit(self, dates: pd.DatetimeIndex, values: pd.Series) -> "SeasonalTrendModel":
        self.origin = dates[0]
        raw_t = np.array([(date.year - self.origin.year) * 12 + (date.month - self.origin.month) for date in dates], dtype=float)
        self.center = float(np.mean(raw_t))
        self.scale = float(max(np.max(np.abs(raw_t - self.center)), 1.0))
        design = self._design(dates)
        target = np.log(np.maximum(values.to_numpy(dtype=float), 1.0)) if self.multiplicative else values.to_numpy(dtype=float)
        self.model = Ridge(alpha=8.0).fit(design, target)
        fitted = self.model.predict(design)
        self.residual_std = float(np.std(target - fitted))
        return self

    def predict(self, dates: pd.DatetimeIndex) -> pd.DataFrame:
        raw = self.model.predict(self._design(dates))
        if self.multiplicative:
            forecast = np.exp(raw)
            lower = np.exp(raw - 1.28 * self.residual_std)
            upper = np.exp(raw + 1.28 * self.residual_std)
        else:
            forecast = raw
            lower = raw - 1.28 * self.residual_std
            upper = raw + 1.28 * self.residual_std
        return pd.DataFrame({"date": dates, "forecast": forecast, "lower": lower, "upper": upper})


def build_feature_row(history: pd.Series, date: pd.Timestamp, market_total: float) -> dict:
    values = history.to_numpy(dtype=float)
    index = len(values)
    record = {
        "Year": date.year,
        "Month": date.month,
        "Quarter": date.quarter,
        "Month_Sin": np.sin(2 * np.pi * date.month / 12),
        "Month_Cos": np.cos(2 * np.pi * date.month / 12),
        "Trend": index,
        "Trend_Squared": index ** 2,
    }
    for lag in (1, 2, 3, 6, 12):
        record[f"Lag_{lag}"] = values[-lag]
    for window in (3, 6, 12):
        window_values = values[-window:]
        record[f"Rolling_Mean_{window}"] = float(np.mean(window_values))
        record[f"Rolling_Std_{window}"] = float(np.std(window_values, ddof=1))
        record[f"Rolling_Max_{window}"] = float(np.max(window_values))
    record["Growth_1"] = values[-1] / values[-2] - 1 if values[-2] else 0.0
    record["Growth_12"] = values[-1] / values[-13] - 1 if len(values) >= 13 and values[-13] else 0.0
    record["Brand_Share"] = values[-1] / market_total if market_total else 0.0
    return record


def main() -> None:
    setup_plot()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    features = pd.read_csv(PROCESSED_DIR / "features.csv", parse_dates=["统计月份"])
    meta = load_json(PROCESSED_DIR / "feature_list.json")
    feature_columns = meta["features"]
    top_brands = meta["top_brands"]
    data = ensure_data()
    market_total = data.groupby("统计月份")["销量"].sum().sort_index()
    last_month = data["统计月份"].max()
    future_dates = pd.date_range(last_month + pd.DateOffset(months=1), periods=8, freq="MS")

    brand_series = (
        data[data["品牌/厂商"].isin(top_brands)]
        .groupby(["统计月份", "品牌/厂商"])["销量"].sum()
        .unstack()
        .sort_index()
    )
    actual_brand_month = (
        data[data["品牌/厂商"].isin(top_brands)]
        .groupby(["统计月份", "品牌/厂商"], as_index=False)["销量"].sum()
    )

    # 市场总量预测：用于 2026 年决策和梯度模型里的份额特征。
    market_model = SeasonalTrendModel().fit(market_total.index, market_total)
    market_forecast = market_model.predict(future_dates)
    market_forecast.to_csv(PROCESSED_DIR / "market_forecast.csv", index=False, encoding="utf-8-sig")

    results = {}
    forecast_rows = []
    comparison_rows = []
    for brand in top_brands:
        series = brand_series[brand].dropna().sort_index()
        split_date = series.index[-12]
        train = series[series.index < split_date]
        validation = series[series.index >= split_date]

        seasonal = SeasonalTrendModel().fit(train.index, train)
        seasonal_validation = seasonal.predict(validation.index)["forecast"].to_numpy()
        seasonal_mae = mean_absolute_error(validation, seasonal_validation)
        seasonal_r2 = r2_score(validation, seasonal_validation)

        gradient = HistGradientBoostingRegressor(
            max_iter=260,
            max_depth=5,
            learning_rate=0.06,
            l2_regularization=1.0,
            random_state=42,
        )
        train_features = features[(features["品牌/厂商"] == brand) & (features["统计月份"] < split_date)]
        gradient.fit(train_features[feature_columns], train_features["销量"])

        history = train.copy()
        gradient_predictions = []
        for date in validation.index:
            previous_total = market_total.get(date - pd.DateOffset(months=1), market_total.mean())
            row = build_feature_row(history, date, float(previous_total))
            value = float(gradient.predict(pd.DataFrame([row])[feature_columns])[0])
            gradient_predictions.append(value)
            history.loc[date] = max(value, 0)
        gradient_predictions = np.array(gradient_predictions)
        gradient_mae = mean_absolute_error(validation, gradient_predictions)
        gradient_r2 = r2_score(validation, gradient_predictions)

        seasonal_weight = 1 / max(seasonal_mae, 1)
        gradient_weight = 1 / max(gradient_mae, 1)
        total_weight = seasonal_weight + gradient_weight

        final_seasonal = SeasonalTrendModel().fit(series.index, series)
        final_forecast = final_seasonal.predict(future_dates)
        final_features = features[features["品牌/厂商"] == brand]
        gradient_full = HistGradientBoostingRegressor(
            max_iter=260,
            max_depth=5,
            learning_rate=0.06,
            l2_regularization=1.0,
            random_state=42,
        )
        gradient_full.fit(final_features[feature_columns], final_features["销量"])
        history = series.copy()
        gradient_future = []
        for date in future_dates:
            previous_total = market_forecast.loc[
                market_forecast["date"] == date - pd.DateOffset(months=1), "forecast"
            ]
            if previous_total.empty:
                previous_total = market_total.get(date - pd.DateOffset(months=1), market_total.mean())
            row = build_feature_row(history, date, float(previous_total.iloc[0] if hasattr(previous_total, "iloc") else previous_total))
            value = max(float(gradient_full.predict(pd.DataFrame([row])[feature_columns])[0]), 0)
            gradient_future.append(value)
            history.loc[date] = value
        gradient_future = np.array(gradient_future)
        ensemble = (final_forecast["forecast"].to_numpy() * seasonal_weight + gradient_future * gradient_weight) / total_weight
        lower = np.minimum(final_forecast["lower"].to_numpy(), ensemble)
        upper = np.maximum(final_forecast["upper"].to_numpy(), ensemble)

        for date, seasonal_value, gradient_value, final_value, low, high in zip(
            future_dates, final_forecast["forecast"], gradient_future, ensemble, lower, upper
        ):
            forecast_rows.append(
                {
                    "统计月份": date,
                    "品牌/厂商": brand,
                    "季节趋势预测": round(float(seasonal_value)),
                    "梯度提升预测": round(float(gradient_value)),
                    "融合预测": round(float(final_value)),
                    "下限": round(float(low)),
                    "上限": round(float(high)),
                }
            )
        results[brand] = {
            "seasonal_mae": float(seasonal_mae),
            "seasonal_r2": float(seasonal_r2),
            "gradient_mae": float(gradient_mae),
            "gradient_r2": float(gradient_r2),
            "seasonal_weight": float(seasonal_weight / total_weight),
            "gradient_weight": float(gradient_weight / total_weight),
            "forecast_total": float(ensemble.sum()),
        }
        comparison_rows.append(
            {
                "品牌": brand,
                "季节趋势MAE": seasonal_mae,
                "梯度提升MAE": gradient_mae,
            }
        )
        print(
            f"{brand}：季节趋势 MAE {seasonal_mae:.0f} / R2 {seasonal_r2:.3f}；"
            f"梯度提升 MAE {gradient_mae:.0f} / R2 {gradient_r2:.3f}"
        )

    forecast = pd.DataFrame(forecast_rows)
    forecast.to_csv(PROCESSED_DIR / "forecast_2026.csv", index=False, encoding="utf-8-sig")
    comparison = pd.DataFrame(comparison_rows)
    comparison.to_csv(PROCESSED_DIR / "model_comparison.csv", index=False, encoding="utf-8-sig")

    total_forecast = forecast.groupby("统计月份", as_index=False)["融合预测"].sum()
    actual_2026 = data[(data["统计月份"] >= "2026-01-01") & (data["统计月份"] <= last_month)]
    annual_forecast = int(actual_2026["销量"].sum() + total_forecast["融合预测"].sum())
    save_json(
        PROCESSED_DIR / "forecast_metrics.json",
        {
            "last_month": str(last_month.date()),
            "future_months": [str(date.date()) for date in future_dates],
            "brands": results,
            "actual_2026_ytd": int(actual_2026["销量"].sum()),
            "forecast_2026_total": annual_forecast,
        },
    )

    # 2x3 预测面板
    fig, axes = plt.subplots(2, 3, figsize=(15, 8.4))
    market_history = market_total.tail(42)
    axes[0, 0].plot(market_history.index, market_history / 10000, color=NAVY, linewidth=1.8, label="实际")
    axes[0, 0].plot(market_forecast["date"], market_forecast["forecast"] / 10000, color=GOLD, linestyle="--", linewidth=1.8, label="预测")
    axes[0, 0].fill_between(market_forecast["date"], market_forecast["lower"] / 10000, market_forecast["upper"] / 10000, color=GOLD, alpha=0.18)
    axes[0, 0].set_title("市场总量", loc="left", fontsize=11, color=NAVY)
    axes[0, 0].legend(frameon=False, fontsize=7)
    panels = [axes[0, 1], axes[0, 2], axes[1, 0], axes[1, 1], axes[1, 2]]
    for ax, brand in zip(panels, top_brands):
        history = brand_series[brand].tail(36)
        part = forecast[forecast["品牌/厂商"] == brand]
        ax.plot(history.index, history / 10000, color=BLUE, linewidth=1.4, label="实际")
        ax.plot(part["统计月份"], part["融合预测"] / 10000, color=RED, linestyle="--", linewidth=1.4, label="预测")
        ax.fill_between(part["统计月份"], part["下限"] / 10000, part["上限"] / 10000, color=RED, alpha=0.12)
        ax.set_title(brand, loc="left", fontsize=11, color=NAVY)
    for ax in axes.flat:
        ax.grid(alpha=0.2)
        ax.tick_params(labelsize=7)
    fig.suptitle("2026 年新能源车销量预测（万辆）", fontsize=15, fontweight="bold", color=NAVY)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "预测趋势.png")
    plt.close(fig)

    # 模型误差对比
    fig, ax = plt.subplots(figsize=(10, 4.8))
    positions = np.arange(len(comparison))
    width = 0.36
    ax.bar(positions - width / 2, comparison["季节趋势MAE"], width, color=TEAL, label="季节趋势")
    ax.bar(positions + width / 2, comparison["梯度提升MAE"], width, color=BLUE, label="梯度提升")
    ax.set_xticks(positions, comparison["品牌"])
    ax.set_ylabel("验证集 MAE（辆）")
    ax.set_title("两个模型在最近 12 个月的误差对比", fontsize=13, fontweight="bold", color=NAVY)
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.2)
    fig.savefig(OUTPUT_DIR / "模型对比.png")
    plt.close(fig)

    print(f"\n2026 年全年预测（Top 5 品牌）：{annual_forecast / 10000:.1f} 万辆")
    print(f"预测明细：{PROCESSED_DIR / 'forecast_2026.csv'}")
    print(f"预测图：{OUTPUT_DIR / '预测趋势.png'}")


if __name__ == "__main__":
    main()
