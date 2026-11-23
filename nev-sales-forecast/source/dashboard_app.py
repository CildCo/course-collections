"""新能源车销量预测大屏：Flask 后端 + 离线预测结果。

先运行 lesson05_web_dashboard/main.py 生成 dashboard/index.html，
再运行：
    python dashboard_app.py
浏览器打开 http://127.0.0.1:5000
"""
from __future__ import annotations

from pathlib import Path

import json
import pandas as pd
from flask import Flask, jsonify, send_from_directory

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "processed" / "cleaned_sales_data.csv"
FORECAST_FILE = ROOT / "data" / "processed" / "forecast_2026.csv"
METRICS_FILE = ROOT / "data" / "processed" / "forecast_metrics.json"
DASHBOARD_DIR = ROOT / "dashboard"

app = Flask(__name__)

print("正在加载数据和预测结果...")
DATA = pd.read_csv(DATA_FILE, parse_dates=["统计月份"]) if DATA_FILE.exists() else pd.DataFrame()
FORECAST = pd.read_csv(FORECAST_FILE, parse_dates=["统计月份"]) if FORECAST_FILE.exists() else pd.DataFrame()
print(f"历史数据：{len(DATA)} 行；预测数据：{len(FORECAST)} 行")


@app.route("/")
def index():
    if not (DASHBOARD_DIR / "index.html").exists():
        return "请先运行 lesson05_web_dashboard/main.py 生成大屏页面", 404
    return send_from_directory(DASHBOARD_DIR, "index.html")


@app.route("/api/summary")
def summary():
    if DATA.empty or FORECAST.empty:
        return jsonify({"error": "数据未准备好"}), 500
    yearly = DATA.groupby("年份")["销量"].sum()
    full_years = [int(year) for year in yearly.index if year < 2026]
    last_year = max(full_years) if full_years else int(yearly.index.max())
    last_year_sales = int(yearly.loc[last_year])
    forecast_total = int(FORECAST["融合预测"].sum())
    if METRICS_FILE.exists():
        forecast_total = int(json.loads(METRICS_FILE.read_text(encoding="utf-8")).get("forecast_2026_total", forecast_total))
    top_brand = DATA.groupby("品牌/厂商")["销量"].sum().idxmax()
    return jsonify(
        {
            "last_year": last_year,
            "last_year_sales": last_year_sales,
            "forecast_total": forecast_total,
            "top_brand": top_brand,
            "brands": int(DATA["品牌/厂商"].nunique()),
            "models": int(DATA["车型"].nunique()),
        }
    )


@app.route("/api/yearly")
def yearly():
    if DATA.empty:
        return jsonify({"error": "数据未准备好"}), 500
    rows = DATA.groupby("年份")["销量"].sum().reset_index()
    return jsonify({"years": rows["年份"].astype(str).tolist(), "sales": rows["销量"].tolist()})


@app.route("/api/brands")
def brands():
    if DATA.empty:
        return jsonify({"error": "数据未准备好"}), 500
    rows = DATA.groupby("品牌/厂商")["销量"].sum().nlargest(8).reset_index()
    return jsonify({"brands": rows["品牌/厂商"].tolist(), "sales": rows["销量"].tolist()})


@app.route("/api/models")
def models():
    if DATA.empty:
        return jsonify({"error": "数据未准备好"}), 500
    rows = DATA.groupby("车型")["销量"].sum().nlargest(10).reset_index()
    return jsonify({"models": rows["车型"].tolist(), "sales": rows["销量"].tolist()})


@app.route("/api/forecast")
def forecast():
    if FORECAST.empty:
        return jsonify({"error": "预测结果未准备好"}), 500
    rows = []
    for brand, part in FORECAST.groupby("品牌/厂商"):
        rows.append(
            {
                "brand": brand,
                "dates": part["统计月份"].dt.strftime("%Y-%m").tolist(),
                "values": part["融合预测"].tolist(),
                "lower": part["下限"].tolist(),
                "upper": part["上限"].tolist(),
            }
        )
    return jsonify(rows)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
