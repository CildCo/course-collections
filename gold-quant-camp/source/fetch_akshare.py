"""可选：用 akshare 拉取真实期货日线，覆盖本地示例数据。

默认课程不依赖网络，直接运行 run_all.py 会生成示例数据。
需要真实行情时：
    pip install akshare
    python fetch_akshare.py
脚本会把同一套字段写到 data/raw/gold_pure_futures_final.csv。
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd

from common import RAW_FILE, ensure_dirs


def _pick(columns, *keys):
    for column in columns:
        text = str(column).lower()
        if any(key in text for key in keys):
            return column
    return None


def fetch_symbol(ak, symbol: str, start: pd.Timestamp, end: pd.Timestamp):
    frame = ak.futures_zh_daily_sina(symbol=symbol)
    if frame is None or frame.empty:
        return None
    columns = list(frame.columns)
    date_col = _pick(columns, "date", "日期")
    close_col = _pick(columns, "close", "收盘")
    if not date_col or not close_col:
        return None
    result = pd.DataFrame({"date": pd.to_datetime(frame[date_col]), "close": frame[close_col]})
    for name, keys in (
        ("open", ("open", "开盘")),
        ("high", ("high", "最高")),
        ("low", ("low", "最低")),
        ("volume", ("volume", "成交量")),
        ("open_interest", ("hold", "持仓")),
    ):
        column = _pick(columns, *keys)
        if column:
            result[name] = frame[column]
    result = result[(result["date"] >= start) & (result["date"] <= end)]
    result = result.dropna(subset=["date"]).sort_values("date").set_index("date")
    return result


def main() -> None:
    try:
        import akshare as ak
    except ImportError:
        print("没有安装 akshare。先执行：pip install akshare")
        return

    ensure_dirs()
    start = pd.Timestamp("2018-01-01")
    end = pd.Timestamp(datetime.now().date())
    main_frame = fetch_symbol(ak, "AU0", start, end)
    if main_frame is None:
        print("没有获取到沪金主力数据，保留本地示例数据。")
        return

    for symbol, column in (
        ("AG0", "Silver_Close"),
        ("CU0", "Copper_Close"),
        ("SC0", "Oil_Close"),
        ("M0", "Meal_Soybean_Close"),
    ):
        asset = fetch_symbol(ak, symbol, start, end)
        if asset is not None:
            main_frame[column] = asset["close"]
            print(f"已获取 {symbol}")
        else:
            print(f"跳过 {symbol}：没有返回数据")

    for column, default in (
        ("open", main_frame["close"]),
        ("high", main_frame["close"]),
        ("low", main_frame["close"]),
        ("volume", 0),
        ("open_interest", 0),
    ):
        if column not in main_frame:
            main_frame[column] = default

    ordered = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "open_interest",
        "Silver_Close",
        "Copper_Close",
        "Oil_Close",
        "Meal_Soybean_Close",
    ]
    main_frame = main_frame[[column for column in ordered if column in main_frame]]
    main_frame.to_csv(RAW_FILE, encoding="utf-8-sig")
    print(f"真实行情已保存：{RAW_FILE}")
    print("现在可以运行 python run_all.py。")


if __name__ == "__main__":
    main()
