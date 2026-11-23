"""新能源车销量预测课程共用工具。

课程默认使用本地生成的月度销量数据，保证断网也能跑通。
数据形态参考 2017-2026 年国内新能源乘用车的品牌与车型结构，
不是任何一家机构的真实统计，不构成投资或经营建议。
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
RAW_FILE = RAW_DIR / "historical_car_sales_2017_to_2026.csv"
CLEAN_FILE = PROCESSED_DIR / "cleaned_sales_data.csv"

NAVY = "#0B2545"
TEAL = "#1ABC9C"
TEAL_DARK = "#0E6655"
BLUE = "#3498DB"
BLUE_LIGHT = "#AED6F1"
RED = "#E74C3C"
GOLD = "#D4AC0D"
GRAY = "#7F8C8D"
BG = "#F7FAFC"

BRAND_COLORS = ["#1ABC9C", "#16A085", "#148F77", "#117864", "#0E6655", "#0B5345"]
MODEL_COLORS = ["#3498DB", "#5DADE2", "#85C1E2", "#AED6F1", "#D6EAF8", "#EBF5FB"]

BRANDS = {
    "比亚迪": {"秦PLUS": 0.22, "宋PLUS": 0.25, "汉": 0.15, "海豚": 0.12, "海豹": 0.12, "元PLUS": 0.14},
    "特斯拉": {"Model 3": 0.45, "Model Y": 0.55},
    "上汽通用五菱": {"宏光MINIEV": 0.55, "缤果": 0.45},
    "吉利汽车": {"星愿": 0.35, "银河E5": 0.35, "极氪001": 0.30},
    "广汽埃安": {"AION Y": 0.55, "AION S": 0.45},
    "理想汽车": {"L6": 0.50, "L7": 0.30, "L9": 0.20},
    "蔚来": {"ES6": 0.55, "ET5": 0.45},
    "小鹏": {"MONA M03": 0.60, "G6": 0.40},
    "长安": {"深蓝SL03": 0.55, "启源A05": 0.45},
    "奇瑞": {"风云A8": 0.55, "iCAR 03": 0.45},
    "零跑": {"C11": 0.50, "C10": 0.50},
    "哪吒": {"哪吒L": 0.55, "哪吒S": 0.45},
}

# 2017 与 2026 的品牌份额端点，中间按年份平滑过渡。
BRAND_SHARE = {
    "比亚迪": (0.08, 0.33),
    "特斯拉": (0.03, 0.09),
    "上汽通用五菱": (0.12, 0.07),
    "吉利汽车": (0.06, 0.08),
    "广汽埃安": (0.01, 0.05),
    "理想汽车": (0.00, 0.05),
    "蔚来": (0.01, 0.03),
    "小鹏": (0.00, 0.04),
    "长安": (0.03, 0.05),
    "奇瑞": (0.02, 0.05),
    "零跑": (0.00, 0.04),
    "哪吒": (0.01, 0.02),
}

ANNUAL_TOTAL = {
    2017: 780_000,
    2018: 1_250_000,
    2019: 1_200_000,
    2020: 1_360_000,
    2021: 3_500_000,
    2022: 6_800_000,
    2023: 9_500_000,
    2024: 12_800_000,
    2025: 16_000_000,
    2026: 11_200_000,
}

MONTH_WEIGHT = np.array([0.075, 0.055, 0.085, 0.080, 0.080, 0.085, 0.075, 0.080, 0.095, 0.090, 0.095, 0.115])
MONTH_WEIGHT = MONTH_WEIGHT / MONTH_WEIGHT.sum()


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
    plt.rcParams["figure.facecolor"] = BG
    plt.rcParams["axes.facecolor"] = BG
    plt.rcParams["axes.edgecolor"] = "#D5D8DC"
    plt.rcParams["axes.labelcolor"] = "#2C3E50"
    plt.rcParams["xtick.color"] = "#5D6D7E"
    plt.rcParams["ytick.color"] = "#5D6D7E"


def _brand_share(year: int, month: int) -> dict[str, float]:
    progress = ((year - 2017) * 12 + (month - 1)) / ((2026 - 2017) * 12 + 3)
    shares = {}
    for brand, (start, end) in BRAND_SHARE.items():
        base = start + (end - start) * progress
        # 给份额加一点微小波动，但不改变长期趋势。
        shares[brand] = max(base * (1 + 0.03 * np.sin((year * 12 + month) / 7 + len(brand))), 0)
    total = sum(shares.values())
    return {brand: value / total for brand, value in shares.items()}


def build_sample_data(seed: int = 20260430) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2017-01-01", "2026-04-01", freq="MS")
    rows = []
    for date in dates:
        year, month = date.year, date.month
        total = ANNUAL_TOTAL[year] * MONTH_WEIGHT[month - 1]
        total *= np.exp(rng.normal(0, 0.025))
        if year == 2020 and month in (2, 3, 4):
            total *= 0.45
        if year == 2026 and month <= 2:
            total *= 0.65
        shares = _brand_share(year, month)
        for brand, models in BRANDS.items():
            brand_sales = total * shares[brand] * np.exp(rng.normal(0, 0.05))
            weights = np.array([models[model] for model in models])
            weights = weights / weights.sum()
            model_sales = np.maximum(np.round(brand_sales * weights * np.exp(rng.normal(0, 0.08, len(weights)))), 0)
            for model, sales in zip(models, model_sales):
                rows.append(
                    {
                        "统计月份": date,
                        "排名": 0,
                        "车型": model,
                        "品牌/厂商": brand,
                        "销量": int(sales),
                    }
                )

    frame = pd.DataFrame(rows)
    # 故意放入少量脏数据，第一章会演示清洗和校验。
    frame = pd.concat(
        [
            frame,
            frame.sample(3, random_state=seed),
        ],
        ignore_index=True,
    )
    dirty_index = frame.sample(4, random_state=seed + 1).index
    frame.loc[dirty_index[0], "销量"] = -1
    frame.loc[dirty_index[1], "销量"] = np.nan
    frame.loc[dirty_index[2], "车型"] = "  " + str(frame.loc[dirty_index[2], "车型"]) + " "
    frame["排名"] = frame.groupby("统计月份")["销量"].rank(ascending=False, method="min").fillna(0).astype(int)
    return frame.sort_values(["统计月份", "销量"], ascending=[True, False]).reset_index(drop=True)


def clean_sales(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    original = len(frame)
    data = frame.copy()
    data["统计月份"] = pd.to_datetime(data["统计月份"], errors="coerce")
    data["销量"] = pd.to_numeric(data["销量"], errors="coerce")
    data["车型"] = data["车型"].astype(str).str.strip()
    data["品牌/厂商"] = data["品牌/厂商"].astype(str).str.strip()
    data = data.dropna(subset=["统计月份", "车型", "品牌/厂商", "销量"])
    data = data[data["销量"] >= 0]
    data = data.drop_duplicates(subset=["统计月份", "车型", "品牌/厂商"])
    data["销量"] = data["销量"].round().astype(int)
    data["年份"] = data["统计月份"].dt.year
    data["月份"] = data["统计月份"].dt.month
    data["排名"] = data.groupby("统计月份")["销量"].rank(ascending=False, method="min").astype(int)
    data = data.sort_values(["统计月份", "销量"], ascending=[True, False]).reset_index(drop=True)
    report = {
        "原始行数": original,
        "清洗后行数": len(data),
        "删除行数": original - len(data),
        "时间范围": f"{data['统计月份'].min().date()} 至 {data['统计月份'].max().date()}",
        "月份数": int(data["统计月份"].nunique()),
        "品牌数": int(data["品牌/厂商"].nunique()),
        "车型数": int(data["车型"].nunique()),
        "负销量": int((data["销量"] < 0).sum()),
        "重复行": int(data.duplicated(subset=["统计月份", "车型", "品牌/厂商"]).sum()),
    }
    return data, report


def ensure_data(refresh: bool = False) -> pd.DataFrame:
    ensure_dirs()
    if CLEAN_FILE.exists() and not refresh:
        data = pd.read_csv(CLEAN_FILE, parse_dates=["统计月份"])
        return data
    if RAW_FILE.exists() and not refresh:
        raw = pd.read_csv(RAW_FILE, parse_dates=["统计月份"])
    else:
        raw = build_sample_data()
        raw.to_csv(RAW_FILE, index=False, encoding="utf-8-sig")
    data, _ = clean_sales(raw)
    data.to_csv(CLEAN_FILE, index=False, encoding="utf-8-sig")
    return data


def save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def yearly_sales(data: pd.DataFrame) -> pd.DataFrame:
    return data.groupby("年份", as_index=False)["销量"].sum()


def brand_rank(data: pd.DataFrame, top: int = 8) -> pd.DataFrame:
    return (
        data.groupby("品牌/厂商", as_index=False)["销量"]
        .sum()
        .nlargest(top, "销量")
        .reset_index(drop=True)
    )


def model_rank(data: pd.DataFrame, top: int = 10) -> pd.DataFrame:
    return (
        data.groupby("车型", as_index=False)["销量"]
        .sum()
        .nlargest(top, "销量")
        .reset_index(drop=True)
    )
