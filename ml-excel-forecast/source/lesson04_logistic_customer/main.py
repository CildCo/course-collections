"""第 4 课：逻辑回归识别高价值客户。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from common import BLUE, NAVY, OUTPUT_DIR, PROCESSED_DIR, RED, TEAL, customer_features, save_json, setup_plot

FEATURES = ["R_最近间隔", "F_购买次数", "M_累计金额", "平均客单价", "累计数量", "品类数", "在网天数", "月均购买"]


def main() -> None:
    setup_plot()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    customers = customer_features()
    x = customers[FEATURES]
    y = customers["高价值客户"]

    x_train, x_test, y_train, y_test, index_train, index_test = train_test_split(
        x, y, customers.index, test_size=0.3, random_state=42, stratify=y
    )
    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)

    model = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
    model.fit(x_train_scaled, y_train)
    prediction = model.predict(x_test_scaled)
    probability = model.predict_proba(x_test_scaled)[:, 1]

    metrics = {
        "accuracy": float(accuracy_score(y_test, prediction)),
        "precision": float(precision_score(y_test, prediction, zero_division=0)),
        "recall": float(recall_score(y_test, prediction, zero_division=0)),
        "f1": float(f1_score(y_test, prediction, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, probability)),
        "high_value_ratio": float(y.mean()),
    }
    save_json(PROCESSED_DIR / "high_value_metrics.json", metrics)
    results = customers.loc[index_test, ["客户ID", "客户名称", "地区", "R_最近间隔", "F_购买次数", "M_累计金额", "高价值客户"]].copy()
    results["预测高价值"] = prediction
    results["高价值概率"] = probability.round(4)
    results.to_csv(PROCESSED_DIR / "high_value_predictions.csv", index=False, encoding="utf-8-sig")

    coefficients = pd.DataFrame({"特征": FEATURES, "系数": model.coef_[0]}).sort_values("系数")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    matrix = confusion_matrix(y_test, prediction)
    axes[0].imshow(matrix, cmap="Blues")
    for row in range(2):
        for column in range(2):
            axes[0].text(column, row, matrix[row, column], ha="center", va="center", fontsize=13)
    axes[0].set_xticks([0, 1], ["普通", "高价值"])
    axes[0].set_yticks([0, 1], ["普通", "高价值"])
    axes[0].set_xlabel("预测")
    axes[0].set_ylabel("真实")
    axes[0].set_title("高价值客户混淆矩阵", loc="left", color=NAVY)

    axes[1].barh(coefficients["特征"], coefficients["系数"], color=[RED if value < 0 else TEAL for value in coefficients["系数"]])
    axes[1].axvline(0, color=NAVY, linewidth=0.8)
    axes[1].set_title("逻辑回归系数（标准化后）", loc="left", color=NAVY)
    axes[1].grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "高价值客户.png")
    plt.close(fig)

    print("高价值客户识别")
    print(f"客户数：{len(customers)}，高价值占比：{y.mean():.1%}")
    print(f"准确率：{metrics['accuracy']:.3f}，精确率：{metrics['precision']:.3f}")
    print(f"召回率：{metrics['recall']:.3f}，F1：{metrics['f1']:.3f}，AUC：{metrics['roc_auc']:.3f}")
    print(f"输出：{PROCESSED_DIR / 'high_value_predictions.csv'}")


if __name__ == "__main__":
    main()
