"""Python 机器学习办公自动化课程共用工具。

课程默认在本地生成订单、客户和报销单示例数据，断网也能跑通。
数据只用于演示机器学习流程，不代表任何真实企业。
"""
from __future__ import annotations

import json
import random
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
MONTHLY_DIR = RAW_DIR / "monthly"
PROCESSED_DIR = DATA_DIR / "processed"
MODEL_DIR = ROOT / "models"
OUTPUT_DIR = ROOT / "output"
ORDERS_FILE = PROCESSED_DIR / "orders_merged.csv"
EXPENSE_FILE = RAW_DIR / "expenses_2025.xlsx"
SNAPSHOT = pd.Timestamp("2025-12-31")
FEATURE_CUTOFF = pd.Timestamp("2025-09-30")

NAVY = "#1F3A5F"
BLUE = "#2E86C1"
TEAL = "#16A085"
GOLD = "#D4AC0D"
RED = "#C0392B"
GRAY = "#7F8C8D"
BG = "#F7FAFC"

CATEGORIES = {
    "电子产品": (800, 0.28),
    "服装": (300, 0.30),
    "家居用品": (220, 0.24),
    "图书": (60, 0.18),
}
REGIONS = ["华东", "华南", "华北", "西南", "华中"]
SALESPEOPLE = ["陈晨", "李敏", "王磊", "赵婷", "周凯", "孙悦"]


def ensure_dirs() -> None:
    for path in (RAW_DIR, MONTHLY_DIR, PROCESSED_DIR, MODEL_DIR, OUTPUT_DIR):
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


def _customer_profiles(seed: int = 20251231) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for index in range(1, 601):
        if index <= 120:
            segment, frequency, multiplier = "VIP", 2.4, 1.7
        elif index <= 420:
            segment, frequency, multiplier = "常规", 1.0, 1.0
        else:
            segment, frequency, multiplier = "低频", 0.35, 0.7
        churn = rng.random() < 0.28
        stop_month = int(rng.integers(8, 34)) if churn else 36
        rows.append(
            {
                "客户ID": f"C{index:04d}",
                "客户名称": f"客户{index:03d}",
                "地区": REGIONS[int(rng.integers(0, len(REGIONS)))],
                "客户类型": segment,
                "月均下单": max(frequency * rng.normal(1, 0.18), 0.08),
                "客单价系数": max(multiplier * rng.normal(1, 0.15), 0.4),
                "停止月份": max(1, min(stop_month, 36)),
            }
        )
    return pd.DataFrame(rows)


def build_sample_data(seed: int = 20251231) -> None:
    """生成 2023-2025 年 36 个月的订单 Excel 和报销单。"""
    ensure_dirs()
    rng = np.random.default_rng(seed)
    random.seed(seed)
    customers = _customer_profiles(seed)
    months = pd.period_range("2023-01", "2025-12", freq="M")
    seasonal = {1: 0.75, 2: 0.6, 3: 0.9, 4: 0.88, 5: 0.98, 6: 1.08, 7: 0.9, 8: 0.95, 9: 1.15, 10: 1.18, 11: 1.35, 12: 1.45}
    order_seq = 1

    for month_index, period in enumerate(months, start=1):
        rows = []
        for _, customer in customers.iterrows():
            if month_index > customer["停止月份"]:
                continue
            expected = customer["月均下单"] * seasonal[period.month]
            count = int(max(0, rng.poisson(expected)))
            for _ in range(min(count, 5)):
                category = random.choices(list(CATEGORIES), weights=[value[1] for value in CATEGORIES.values()])[0]
                base_price = CATEGORIES[category][0] * customer["客单价系数"] * np.exp(rng.normal(0, 0.18))
                quantity = int(rng.integers(1, 5))
                sales = round(base_price * quantity, 2)
                day = int(rng.integers(1, period.days_in_month + 1))
                hour = int(rng.integers(9, 22))
                rows.append(
                    {
                        "订单编号": f"ORD{period.year}{period.month:02d}{order_seq:05d}",
                        "下单日期": pd.Timestamp(period.year, period.month, day, hour),
                        "客户ID": customer["客户ID"],
                        "客户名称": customer["客户名称"],
                        "地区": customer["地区"],
                        "产品类别": category,
                        "数量": quantity,
                        "单价": round(base_price, 2),
                        "销售额": sales,
                        "销售员": random.choice(SALESPEOPLE),
                    }
                )
                order_seq += 1
        frame = pd.DataFrame(rows)
        # 在少数月份放入脏数据，第 1 课会演示清洗。
        if month_index in (5, 17, 29) and not frame.empty:
            frame = pd.concat([frame, frame.sample(min(4, len(frame)), random_state=seed + month_index)], ignore_index=True)
            frame.loc[frame.index[0], "销售额"] = np.nan
            frame.loc[frame.index[1], "销售额"] = -10
        frame.to_excel(MONTHLY_DIR / f"{period.year}-{period.month:02d}.xlsx", index=False)

    # 报销单：正常金额 + 少量明显异常。
    expense_rows = []
    expense_types = ["差旅", "餐饮", "办公用品", "交通", "培训"]
    for index in range(1, 801):
        amount = round(float(np.exp(rng.normal(6.2, 0.75))), 2)
        date = pd.Timestamp("2025-01-01") + pd.Timedelta(days=int(rng.integers(0, 365)))
        expense_rows.append(
            {
                "报销单号": f"BX{index:05d}",
                "日期": date,
                "部门": random.choice(["销售部", "市场部", "财务部", "运营部", "技术部"]),
                "费用类型": random.choice(expense_types),
                "金额": amount,
                "申请人": f"员工{int(rng.integers(1, 121)):03d}",
                "备注": "",
            }
        )
    for index in range(801, 821):
        date = pd.Timestamp("2025-01-01") + pd.Timedelta(days=int(rng.integers(0, 365)))
        expense_rows.append(
            {
                "报销单号": f"BX{index:05d}",
                "日期": date,
                "部门": random.choice(["销售部", "市场部", "运营部"]),
                "费用类型": random.choice(expense_types),
                "金额": round(float(rng.uniform(30000, 90000)), 2),
                "申请人": f"员工{int(rng.integers(1, 121)):03d}",
                "备注": "大额",
            }
        )
    pd.DataFrame(expense_rows).to_excel(EXPENSE_FILE, index=False)


def clean_orders(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    original = len(frame)
    data = frame.copy()
    data["下单日期"] = pd.to_datetime(data["下单日期"], errors="coerce")
    for column in ("数量", "单价", "销售额"):
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data["销售额"] = data["销售额"].fillna(data["数量"] * data["单价"])
    data = data.dropna(subset=["订单编号", "下单日期", "客户ID", "销售额"])
    data = data[data["销售额"] > 0]
    data = data.drop_duplicates(subset=["订单编号"], keep="first")
    data["数量"] = data["数量"].fillna(1).clip(lower=1).astype(int)
    data["单价"] = data["单价"].fillna(data["销售额"] / data["数量"]).round(2)
    data["销售额"] = data["销售额"].round(2)
    data["年份"] = data["下单日期"].dt.year
    data["月份"] = data["下单日期"].dt.month
    data["季度"] = data["下单日期"].dt.quarter
    data["星期"] = data["下单日期"].dt.dayofweek
    data["是否周末"] = data["星期"].isin([5, 6]).astype(int)
    report = {
        "原始行数": original,
        "清洗后行数": len(data),
        "删除行数": original - len(data),
        "日期范围": f"{data['下单日期'].min():%Y-%m-%d} 至 {data['下单日期'].max():%Y-%m-%d}",
        "客户数": int(data["客户ID"].nunique()),
        "订单数": int(data["订单编号"].nunique()),
        "销售额合计": round(float(data["销售额"].sum()), 2),
        "重复订单": int(data.duplicated(subset=["订单编号"]).sum()),
        "负销售额": int((data["销售额"] <= 0).sum()),
    }
    return data.sort_values("下单日期").reset_index(drop=True), report


def merge_monthly_files() -> pd.DataFrame:
    ensure_dirs()
    files = sorted(MONTHLY_DIR.glob("*.xlsx"))
    if not files:
        build_sample_data()
        files = sorted(MONTHLY_DIR.glob("*.xlsx"))
    frames = []
    for file in files:
        frame = pd.read_excel(file)
        frame["来源文件"] = file.name
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def ensure_orders(refresh: bool = False) -> pd.DataFrame:
    ensure_dirs()
    if ORDERS_FILE.exists() and not refresh:
        return pd.read_csv(ORDERS_FILE, parse_dates=["下单日期"])
    raw = merge_monthly_files()
    clean, _ = clean_orders(raw)
    clean.to_csv(ORDERS_FILE, index=False, encoding="utf-8-sig")
    return clean


def customer_features(orders: pd.DataFrame | None = None) -> pd.DataFrame:
    """用 2025-09-30 之前的特征，预测 Q4 的未来行为，避免把答案算进特征。"""
    data = ensure_orders() if orders is None else orders
    history = data[data["下单日期"] <= FEATURE_CUTOFF]
    future = data[data["下单日期"] > FEATURE_CUTOFF]
    grouped = history.groupby("客户ID").agg(
        最近购买=("下单日期", "max"),
        首次购买=("下单日期", "min"),
        购买次数=("订单编号", "nunique"),
        累计金额=("销售额", "sum"),
        累计数量=("数量", "sum"),
        平均客单价=("销售额", "mean"),
        品类数=("产品类别", "nunique"),
        地区=("地区", "first"),
        客户名称=("客户名称", "first"),
    )
    grouped["R_最近间隔"] = (FEATURE_CUTOFF - grouped["最近购买"]).dt.days
    grouped["F_购买次数"] = grouped["购买次数"]
    grouped["M_累计金额"] = grouped["累计金额"].round(2)
    grouped["在网天数"] = (grouped["最近购买"] - grouped["首次购买"]).dt.days.clip(lower=1)
    grouped["月均购买"] = grouped["F_购买次数"] / (grouped["在网天数"] / 30.4).clip(lower=1)
    future_spend = future.groupby("客户ID")["销售额"].sum().reindex(grouped.index, fill_value=0)
    future_orders = future.groupby("客户ID")["订单编号"].nunique().reindex(grouped.index, fill_value=0)
    grouped["Q4金额"] = future_spend.round(2)
    grouped["Q4订单数"] = future_orders.astype(int)
    grouped["高价值客户"] = (future_spend >= future_spend[future_spend > 0].quantile(0.75)).astype(int)
    grouped["流失客户"] = (future_orders == 0).astype(int)
    return grouped.reset_index()


def ensure_expenses() -> pd.DataFrame:
    ensure_dirs()
    if not EXPENSE_FILE.exists():
        build_sample_data()
    data = pd.read_excel(EXPENSE_FILE)
    data["日期"] = pd.to_datetime(data["日期"])
    data["金额"] = pd.to_numeric(data["金额"], errors="coerce").fillna(0)
    data["是否周末"] = data["日期"].dt.dayofweek.isin([5, 6]).astype(int)
    data["月份"] = data["日期"].dt.month
    return data


def save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
