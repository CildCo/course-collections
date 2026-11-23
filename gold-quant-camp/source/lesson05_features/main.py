"""第 5 课：特征工程与三分类目标。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import pandas as pd

from common import (
    FEATURE_COLUMNS,
    GOLD,
    GREEN,
    NAVY,
    OUTPUT_DIR,
    PROCESSED_DIR,
    RED,
    add_features,
    ensure_data,
    save_json,
    setup_plot,
)

LABELS = {0: "大跌", 1: "震荡", 2: "大涨"}


def main() -> None:
    setup_plot()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    data = add_features(ensure_data())
    target = "Target_Class_5d"
    features = data.dropna(subset=FEATURE_COLUMNS + [target]).copy()
    features.to_csv(PROCESSED_DIR / "gold_features.csv", encoding="utf-8-sig")
    save_json(PROCESSED_DIR / "feature_names.json", {"features": FEATURE_COLUMNS})

    counts = features[target].value_counts().sort_index()
    print("特征工程完成")
    print(f"可用样本：{len(features)}")
    print(f"特征数量：{len(FEATURE_COLUMNS)}")
    for key, count in counts.items():
        print(f"  {LABELS.get(int(key), key)}：{int(count)} 条（{count / len(features) * 100:.1f}%）")

    colors = [RED, "#B7950B", GREEN]
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ax.bar([LABELS[int(key)] for key in counts.index], counts.values, color=colors)
    for index, value in enumerate(counts.values):
        ax.text(index, value, str(int(value)), ha="center", va="bottom", fontsize=10)
    ax.set_title("未来 5 日三分类样本分布", fontsize=14, fontweight="bold", color=NAVY)
    ax.set_ylabel("样本数")
    ax.grid(axis="y", alpha=0.2)
    fig.savefig(OUTPUT_DIR / "三分类分布.png")
    plt.close(fig)

    correlations = (
        features[FEATURE_COLUMNS + [target]]
        .corr(numeric_only=True)[target]
        .drop(target)
        .sort_values()
    )
    top = pd.concat([correlations.head(8), correlations.tail(8)]).drop_duplicates()
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(top.index, top.values, color=[RED if value < 0 else GOLD for value in top.values])
    ax.axvline(0, color=NAVY, linewidth=0.8)
    ax.set_title("特征与三分类目标的相关性（仅作筛查）", fontsize=13, fontweight="bold", color=NAVY)
    ax.grid(axis="x", alpha=0.2)
    fig.savefig(OUTPUT_DIR / "特征相关性.png")
    plt.close(fig)

    print(f"\n特征表：{PROCESSED_DIR / 'gold_features.csv'}")
    print("注意：相关性只能用来排查明显方向，不能代替滚动回测。")


if __name__ == "__main__":
    main()
