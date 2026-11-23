# 第9课示例销售数据

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def ensure_samples():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rows = [
        ("2026-10-18", "销售部", 12000),
        ("2026-10-18", "技术部", 8000),
        ("2026-10-18", "市场部", 6000),
        ("2026-10-19", "销售部", 15000),
        ("2026-10-19", "技术部", 9000),
        ("2026-10-19", "市场部", 7000),
    ]
    df = pd.DataFrame(rows, columns=["日期", "部门", "销售额"])
    df["日期"] = pd.to_datetime(df["日期"])
    df.to_excel(DATA_DIR / "sales.xlsx", index=False)
    print("示例数据已生成：", DATA_DIR / "sales.xlsx")


if __name__ == "__main__":
    ensure_samples()
