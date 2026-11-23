"""第 6 课：K-Means 给客户画一张精准像。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from common import BLUE, NAVY, OUTPUT_DIR, PROCESSED_DIR, TEAL, customer_features, setup_plot

FEATURES = ["R_最近间隔", "F_购买次数", "M_累计金额", "平均客单价", "品类数"]


def label_cluster(row, med_m, med_r):
    if row["平均累计金额"] >= 60000:
        return "高价值活跃" if row["平均最近间隔"] <= 90 else "高价值沉睡"
    if row["平均最近间隔"] > 90:
        return "流失风险"
    return "成长客户"


def main() -> None:
    setup_plot()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    customers = customer_features()
    x = StandardScaler().fit_transform(customers[FEATURES])

    scores = {}
    for k in range(2, 7):
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = model.fit_predict(x)
        scores[k] = float(silhouette_score(x, labels))
    k = max(scores, key=scores.get)
    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    customers["聚类"] = model.fit_predict(x)

    summary = customers.groupby("聚类").agg(
        客户数=("客户ID", "count"),
        平均最近间隔=("R_最近间隔", "mean"),
        平均购买次数=("F_购买次数", "mean"),
        平均累计金额=("M_累计金额", "mean"),
        平均客单价=("平均客单价", "mean"),
    ).reset_index()
    med_m = customers["M_累计金额"].median()
    med_r = customers["R_最近间隔"].median()
    summary["客户画像"] = summary.apply(lambda row: label_cluster(row, med_m, med_r), axis=1)
    customers = customers.merge(summary[["聚类", "客户画像"]], on="聚类", how="left")
    customers.to_csv(PROCESSED_DIR / "customer_segments.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(PROCESSED_DIR / "segment_summary.csv", index=False, encoding="utf-8-sig")

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    axes[0].plot(list(scores), list(scores.values()), marker="o", color=BLUE, linewidth=2)
    axes[0].axvline(k, color=TEAL, linestyle="--", linewidth=1)
    axes[0].set_title("轮廓系数选择 k", loc="left", color=NAVY)
    axes[0].set_xlabel("聚类数")
    axes[0].set_ylabel("轮廓系数")
    axes[0].grid(alpha=0.2)

    scatter = axes[1].scatter(
        customers["R_最近间隔"],
        customers["M_累计金额"] / 10000,
        c=customers["聚类"],
        cmap="viridis",
        s=18,
        alpha=0.75,
    )
    axes[1].set_title("客户分群：最近间隔 × 累计金额", loc="left", color=NAVY)
    axes[1].set_xlabel("距最近购买天数")
    axes[1].set_ylabel("累计金额（万元）")
    axes[1].grid(alpha=0.2)
    fig.colorbar(scatter, ax=axes[1], label="聚类")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "客户分群.png")
    plt.close(fig)

    print(f"选择聚类数：{k}，轮廓系数：{scores[k]:.3f}")
    print("\n客户画像：")
    for _, row in summary.iterrows():
        print(
            f"  聚类 {int(row['聚类'])}（{row['客户画像']}）：{int(row['客户数'])} 人，"
            f"平均金额 {row['平均累计金额']:.0f} 元，平均间隔 {row['平均最近间隔']:.0f} 天"
        )
    print(f"\n分群结果：{PROCESSED_DIR / 'customer_segments.csv'}")


if __name__ == "__main__":
    main()
