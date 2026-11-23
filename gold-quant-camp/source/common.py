"""黄金量化课程共用工具：示例数据、指标和绘图设置。

课程默认使用本地生成的示例数据，保证断网也能跑通。
数据形态参考沪金主力、白银、铜、原油和豆粕的日线关系，
不构成任何投资建议。
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = ROOT / "output"
RAW_FILE = RAW_DIR / "gold_pure_futures_final.csv"

GOLD = "#C9A227"
NAVY = "#1F3A5F"
BLUE = "#2E6F9E"
RED = "#C0392B"
GREEN = "#1E8449"
GRAY = "#7F8C8D"

FEATURE_COLUMNS = [
    "Return",
    "Volatility_20",
    "RSI_14",
    "BIAS_5",
    "BIAS_10",
    "BIAS_20",
    "BIAS_30",
    "BIAS_60",
    "Mom_5",
    "Mom_10",
    "Mom_20",
    "Volatility_20_Log",
    "Channel_Breakout",
    "Gold_Silver_Ratio",
    "Copper_Gold_Ratio",
    "CG_Ratio_ZScore",
    "Oil_Gold_Ratio",
    "Oil_Gold_Trend",
    "Meal_Gold_Relative",
    "Meal_Gold_Trend",
    "Open_Interest_Change",
    "Volume_Change",
]


def ensure_dirs() -> None:
    for path in (RAW_DIR, PROCESSED_DIR, OUTPUT_DIR):
        path.mkdir(parents=True, exist_ok=True)


def setup_plot() -> None:
    plt.rcParams["font.sans-serif"] = [
        "Microsoft YaHei",
        "SimHei",
        "Arial Unicode MS",
        "DejaVu Sans",
    ]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.dpi"] = 150
    plt.rcParams["savefig.bbox"] = "tight"
    plt.rcParams["axes.edgecolor"] = "#D5D8DC"
    plt.rcParams["axes.labelcolor"] = "#2C3E50"
    plt.rcParams["xtick.color"] = "#5D6D7E"
    plt.rcParams["ytick.color"] = "#5D6D7E"


def _rescale_log_path(log_path: np.ndarray, final_price: float) -> np.ndarray:
    return log_path + (np.log(final_price) - log_path[-1])


def build_sample_data(
    start: str = "2018-01-01",
    end: str = "2026-03-20",
    seed: int = 20260320,
    final_price: float = 1002.0,
) -> pd.DataFrame:
    """生成一套可复现的黄金与关联资产日线数据。"""
    dates = pd.bdate_range(start=start, end=end)
    n = len(dates)
    rng = np.random.default_rng(seed)
    t = np.arange(n)

    regime = 0.00050 + 0.00038 * np.sin(t / 210) + 0.00018 * np.sin(t / 41)
    vol = 0.0075 + 0.0030 * (0.5 + 0.5 * np.sin(t / 97))
    shocks = rng.standard_t(df=6, size=n) * 0.80
    jumps = np.where(rng.random(n) < 0.006, rng.normal(0, 0.022, n), 0.0)
    log_ret = regime + vol * shocks + jumps

    # 加入很弱的短期动量，让技术指标有可学习的结构，但不足以稳定赚钱。
    for i in range(1, n):
        log_ret[i] += 0.03 * log_ret[i - 1]

    log_path = _rescale_log_path(np.cumsum(log_ret), final_price)
    close = np.exp(log_path)

    gap = rng.normal(0, 0.0012, n)
    open_price = np.empty(n)
    open_price[0] = close[0] * (1 + gap[0])
    open_price[1:] = close[:-1] * np.exp(gap[1:])
    body_high = np.maximum(open_price, close) * (1 + np.abs(rng.normal(0, 0.004, n)))
    body_low = np.minimum(open_price, close) * (1 - np.abs(rng.normal(0, 0.004, n)))

    volume = (160000 * np.exp(rng.normal(0, 0.25, n))).astype(int)
    open_interest = (240000 * np.exp(np.cumsum(rng.normal(0, 0.004, n)))).astype(int)

    ratio = 78 + 7.5 * np.sin(t / 85) + rng.normal(0, 2.2, n)
    silver = close * 1000 / ratio

    copper_ret = 0.45 * log_ret + rng.normal(0.00018, 0.0085, n)
    copper = 52000 * np.exp(np.cumsum(copper_ret))
    oil_ret = 0.22 * log_ret + rng.normal(0.00005, 0.015, n)
    oil = 480 * np.exp(np.cumsum(oil_ret))
    meal_ret = 0.10 * log_ret + rng.normal(0.00012, 0.010, n)
    meal = 3100 * np.exp(np.cumsum(meal_ret))

    df = pd.DataFrame(
        {
            "open": open_price,
            "high": body_high,
            "low": body_low,
            "close": close,
            "volume": volume,
            "open_interest": open_interest,
            "Silver_Close": silver,
            "Copper_Close": copper,
            "Oil_Close": oil,
            "Meal_Soybean_Close": meal,
        },
        index=pd.Index(dates, name="date"),
    )
    return df.round(4)


def ensure_data(refresh: bool = False) -> pd.DataFrame:
    ensure_dirs()
    if RAW_FILE.exists() and not refresh:
        return pd.read_csv(RAW_FILE, index_col=0, parse_dates=True)
    df = build_sample_data()
    df.to_csv(RAW_FILE, encoding="utf-8-sig")
    return df


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    close = data["close"]

    data["Return"] = close.pct_change()
    data["Volatility_20"] = data["Return"].rolling(20).std() * np.sqrt(252)
    data["MA_20"] = close.rolling(20).mean()
    data["MA_60"] = close.rolling(60).mean()

    delta = close.diff()
    gain = delta.where(delta > 0, 0).ewm(span=14, adjust=False).mean()
    loss = -delta.where(delta < 0, 0).ewm(span=14, adjust=False).mean()
    rs = gain / loss.replace(0, 1e-8)
    data["RSI_14"] = 100 - 100 / (1 + rs)

    if "Silver_Close" in data:
        data["Gold_Silver_Ratio"] = data["close"] * 1000 / data["Silver_Close"]
    if "Copper_Close" in data:
        data["Copper_Gold_Ratio"] = data["Copper_Close"] / (data["close"] * 1000)
    if "Oil_Close" in data:
        data["Oil_Gold_Ratio"] = data["Oil_Close"] / data["close"]
    if "Meal_Soybean_Close" in data:
        data["Meal_Gold_Relative"] = data["Meal_Soybean_Close"] / data["close"]
    return data


def add_features(df: pd.DataFrame, horizon: int = 5) -> pd.DataFrame:
    data = add_indicators(df)
    close = data["close"]

    for window in (5, 10, 20, 30, 60):
        ma = close.rolling(window=window, min_periods=1).mean()
        data[f"BIAS_{window}"] = (close - ma) / ma
    for window in (5, 10, 20):
        data[f"Mom_{window}"] = close.pct_change(window)

    log_ret = np.log(close / close.shift(1))
    data["Volatility_20_Log"] = log_ret.rolling(20, min_periods=10).std() * np.sqrt(252)

    upper = close.rolling(10).max()
    lower = close.rolling(10).min()
    data["Channel_Breakout"] = (close - lower) / (upper - lower + 1e-8)

    if "Copper_Gold_Ratio" in data:
        mean = data["Copper_Gold_Ratio"].rolling(120, min_periods=60).mean()
        std = data["Copper_Gold_Ratio"].rolling(120, min_periods=60).std()
        data["CG_Ratio_ZScore"] = (data["Copper_Gold_Ratio"] - mean) / (std + 1e-8)
    if "Oil_Gold_Ratio" in data:
        data["Oil_Gold_Trend"] = data["Oil_Gold_Ratio"].pct_change(20)
    if "Meal_Gold_Relative" in data:
        data["Meal_Gold_Trend"] = data["Meal_Gold_Relative"].pct_change(60)

    data["Open_Interest_Change"] = data["open_interest"].pct_change()
    data["Volume_Change"] = data["volume"].pct_change()

    future = close.shift(-horizon) / close - 1
    rolling_vol = close.pct_change().rolling(20).std()
    threshold = (rolling_vol * 0.5).shift(-horizon)
    data[f"Target_Return_{horizon}d"] = future
    data[f"Target_Class_{horizon}d"] = np.select(
        [future > threshold, future < -threshold],
        [2, 0],
        default=1,
    )
    data.loc[future.isna() | threshold.isna(), f"Target_Class_{horizon}d"] = np.nan
    return data


def save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def format_pct(value: float, digits: int = 2) -> str:
    return f"{value * 100:.{digits}f}%"
