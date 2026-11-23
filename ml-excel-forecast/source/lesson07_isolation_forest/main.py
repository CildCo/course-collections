"""第 7 课：孤立森林揪出异常报销单。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from common import BLUE, NAVY, OUTPUT_DIR, PROCESSED_DIR, RED, ensure_expenses, save_json, setup_plot


def main() -> None:
    setup_plot()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    data = ensure_expenses().copy()
    data["金额对数"] = np.log1p(data["金额"])
    monthly_mean = data.groupby(["申请人", "月份"])["金额"].transform("mean")
    data["个人月均金额"] = monthly_mean
    data["金额偏差"] = data["金额"] - data["个人月均金额"]
    data["金额倍数"] = data["金额"] / (data["个人月均金额"] + 1)

    features = ["金额", "金额对数", "是否周末", "金额偏差", "金额倍数"]
    model = IsolationForest(n_estimators=240, contamination=0.03, random_state=42)
    data["异常"] = model.fit_predict(data[features])
    data["异常分数"] = -model.decision_function(data[features])
    data["异常"] = (data["异常"] == -1).astype(int)
    anomalies = data[data["异常"] == 1].sort_values("异常分数", ascending=False)
    anomalies.to_csv(PROCESSED_DIR / "expense_anomalies.csv", index=False, encoding="utf-8-sig")
    data.to_csv(PROCESSED_DIR / "expenses_scored.csv", index=False, encoding="utf-8-sig")
    save_json(
        PROCESSED_DIR / "expense_metrics.json",
        {
            "total": int(len(data)),
            "anomalies": int(len(anomalies)),
            "ratio": float(len(anomalies) / len(data)),
            "amount_anomalies": float(anomalies["金额"].sum()),
            "amount_total": float(data["金额"].sum()),
        },
    )

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    normal = data[data["异常"] == 0]
    axes[0].scatter(normal["日期"], normal["金额"], s=10, color=BLUE, alpha=0.45, label="正常")
    axes[0].scatter(anomalies["日期"], anomalies["金额"], s=40, color=RED, alpha=0.9, label="异常")
    axes[0].set_yscale("log")
    axes[0].set_title("报销金额与异常标记", loc="left", color=NAVY)
    axes[0].set_ylabel("金额（元，对数轴）")
    axes[0].legend(frameon=False)
    axes[0].grid(alpha=0.2)

    top = anomalies.head(12).sort_values("金额")
    axes[1].barh(top["报销单号"], top["金额"] / 10000, color=RED)
    axes[1].set_title("异常报销单 Top 12", loc="left", color=NAVY)
    axes[1].set_xlabel("万元")
    axes[1].grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "异常报销检测.png")
    plt.close(fig)

    print("异常报销单检测")
    print(f"总报销单：{len(data)}，标记异常：{len(anomalies)}（{len(anomalies) / len(data):.1%}）")
    print(f"异常金额合计：{anomalies['金额'].sum():,.0f} 元")
    print("异常单 Top 5：")
    for _, row in anomalies.head(5).iterrows():
        print(f"  {row['报销单号']} {row['日期']:%Y-%m-%d} {row['部门']} {row['金额']:,.0f} 元")
    print(f"\n明细：{PROCESSED_DIR / 'expense_anomalies.csv'}")


if __name__ == "__main__":
    main()
