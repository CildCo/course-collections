"""第 5 课：决策树和随机森林做客户流失预警。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from common import NAVY, OUTPUT_DIR, PROCESSED_DIR, RED, TEAL, customer_features, save_json, setup_plot

FEATURES = ["R_最近间隔", "F_购买次数", "M_累计金额", "平均客单价", "累计数量", "品类数", "在网天数", "月均购买"]


def main() -> None:
    setup_plot()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    customers = customer_features()
    x = customers[FEATURES]
    y = customers["流失客户"]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)

    tree = DecisionTreeClassifier(max_depth=4, min_samples_leaf=18, class_weight="balanced", random_state=42)
    forest = RandomForestClassifier(
        n_estimators=260,
        max_depth=6,
        min_samples_leaf=10,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    tree.fit(x_train, y_train)
    forest.fit(x_train, y_train)
    tree_pred = tree.predict(x_test)
    forest_pred = forest.predict(x_test)
    forest_prob = forest.predict_proba(x_test)[:, 1]

    metrics = {
        "churn_ratio": float(y.mean()),
        "tree": {
            "accuracy": float(accuracy_score(y_test, tree_pred)),
            "f1": float(f1_score(y_test, tree_pred, zero_division=0)),
            "auc": float(roc_auc_score(y_test, tree.predict_proba(x_test)[:, 1])),
        },
        "forest": {
            "accuracy": float(accuracy_score(y_test, forest_pred)),
            "f1": float(f1_score(y_test, forest_pred, zero_division=0)),
            "auc": float(roc_auc_score(y_test, forest_prob)),
        },
    }
    save_json(PROCESSED_DIR / "churn_metrics.json", metrics)

    results = customers.loc[x_test.index, ["客户ID", "客户名称", "地区", "R_最近间隔", "F_购买次数", "M_累计金额", "流失客户"]].copy()
    results["预测流失"] = forest_pred
    results["流失概率"] = forest_prob.round(4)
    results.to_csv(PROCESSED_DIR / "churn_predictions.csv", index=False, encoding="utf-8-sig")

    importance = pd.Series(forest.feature_importances_, index=FEATURES).sort_values()
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    matrix = confusion_matrix(y_test, forest_pred)
    axes[0].imshow(matrix, cmap="Oranges")
    for row in range(2):
        for column in range(2):
            axes[0].text(column, row, matrix[row, column], ha="center", va="center", fontsize=13)
    axes[0].set_xticks([0, 1], ["留存", "流失"])
    axes[0].set_yticks([0, 1], ["留存", "流失"])
    axes[0].set_xlabel("预测")
    axes[0].set_ylabel("真实")
    axes[0].set_title("随机森林混淆矩阵", loc="left", color=NAVY)

    axes[1].barh(importance.index, importance.values, color=TEAL)
    axes[1].set_title("流失预警特征重要性", loc="left", color=NAVY)
    axes[1].grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "客户流失预警.png")
    plt.close(fig)

    print("客户流失预警")
    print(f"流失客户占比：{y.mean():.1%}")
    print(f"决策树：准确率 {metrics['tree']['accuracy']:.3f}，F1 {metrics['tree']['f1']:.3f}，AUC {metrics['tree']['auc']:.3f}")
    print(f"随机森林：准确率 {metrics['forest']['accuracy']:.3f}，F1 {metrics['forest']['f1']:.3f}，AUC {metrics['forest']['auc']:.3f}")
    print(f"预测结果：{PROCESSED_DIR / 'churn_predictions.csv'}")


if __name__ == "__main__":
    main()
