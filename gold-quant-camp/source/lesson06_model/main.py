"""第 6 课：防泄露的时间序列模型。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score

from common import (
    NAVY,
    OUTPUT_DIR,
    PROCESSED_DIR,
    load_json,
    save_json,
    setup_plot,
)

LABELS = ["大跌", "震荡", "大涨"]


class PurgedTimeSeriesSplit:
    """时间序列切分，训练集和验证集之间留出 gap 天空窗。"""

    def __init__(self, n_splits: int = 5, gap: int = 5):
        self.n_splits = n_splits
        self.gap = gap

    def split(self, length: int):
        test_size = length // (self.n_splits + 1)
        for index in range(self.n_splits):
            test_start = length - (self.n_splits - index) * test_size
            test_end = test_start + test_size
            train_end = test_start - self.gap
            if train_end < 120:
                continue
            yield np.arange(0, train_end), np.arange(test_start, test_end)


def build_models() -> dict:
    return {
        "RandomForest": RandomForestClassifier(
            n_estimators=120,
            max_depth=5,
            min_samples_leaf=20,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
        "GradientBoosting": HistGradientBoostingClassifier(
            max_iter=160,
            max_depth=4,
            learning_rate=0.05,
            l2_regularization=1.0,
            random_state=42,
        ),
    }


def main() -> None:
    setup_plot()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    feature_file = PROCESSED_DIR / "feature_names.json"
    if not feature_file.exists():
        raise SystemExit("请先运行第 5 课生成特征表")
    features = load_json(feature_file)["features"]

    data = pd.read_csv(PROCESSED_DIR / "gold_features.csv", index_col=0, parse_dates=True)
    target = "Target_Class_5d"
    data = data.dropna(subset=features + [target]).sort_index()
    x = data[features].to_numpy(dtype=float)
    y = data[target].to_numpy(dtype=int)

    print(f"样本：{len(data)}，特征：{len(features)}")
    splitter = PurgedTimeSeriesSplit(n_splits=5, gap=5)
    scores = {}
    for name, model in build_models().items():
        fold_scores = []
        for train_index, test_index in splitter.split(len(x)):
            model.fit(x[train_index], y[train_index])
            prediction = model.predict(x[test_index])
            fold_scores.append(f1_score(y[test_index], prediction, average="macro", zero_division=0))
        scores[name] = float(np.mean(fold_scores)) if fold_scores else 0.0
        print(f"{name} 交叉验证 macro-F1：{scores[name]:.4f}")

    best_name = max(scores, key=scores.get)
    best_params = build_models()[best_name]
    print(f"胜出模型：{best_name}")

    # 滚动训练：每次只用当前时点之前的数据，训练完预测未来 20 天。
    # 样本外从 2023-10-11 开始，和课程最终报告的口径保持一致。
    start = max(260, int(data.index.searchsorted(pd.Timestamp("2023-10-11"))))
    step = 20
    gap = 5
    rows = []
    for test_start in range(start, len(data), step):
        test_end = min(test_start + step, len(data))
        train_end = test_start - gap
        if train_end < 200:
            continue
        model = build_models()[best_name]
        model.fit(x[:train_end], y[:train_end])
        probabilities = model.predict_proba(x[test_start:test_end])
        classes = list(model.classes_)
        for offset, row_index in enumerate(range(test_start, test_end)):
            prob_map = {int(cls): float(prob) for cls, prob in zip(classes, probabilities[offset])}
            rows.append(
                {
                    "date": data.index[row_index],
                    "prob_down": prob_map.get(0, 0.0),
                    "prob_flat": prob_map.get(1, 0.0),
                    "prob_up": prob_map.get(2, 0.0),
                    "pred_class": int(model.predict(x[row_index : row_index + 1])[0]),
                }
            )

    predictions = pd.DataFrame(rows).set_index("date").sort_index()
    predictions.to_csv(PROCESSED_DIR / "predictions.csv", encoding="utf-8-sig")

    actual = y[-len(predictions) :]
    predicted = predictions["pred_class"].to_numpy()
    accuracy = accuracy_score(actual, predicted)
    macro_f1 = f1_score(actual, predicted, average="macro", zero_division=0)
    matrix = confusion_matrix(actual, predicted, labels=[0, 1, 2])

    print(f"滚动预测样本：{len(predictions)}")
    print(f"样本外准确率：{accuracy:.2%}")
    print(f"样本外 macro-F1：{macro_f1:.4f}")
    print("混淆矩阵（行=真实，列=预测）：")
    print(matrix)

    fig, ax = plt.subplots(figsize=(6.4, 5.3))
    image = ax.imshow(matrix, cmap="YlGnBu")
    for row in range(3):
        for column in range(3):
            ax.text(column, row, matrix[row, column], ha="center", va="center", fontsize=12)
    ax.set_xticks(range(3), LABELS)
    ax.set_yticks(range(3), LABELS)
    ax.set_xlabel("预测")
    ax.set_ylabel("真实")
    ax.set_title("Walk-Forward 混淆矩阵", fontsize=14, fontweight="bold", color=NAVY)
    fig.colorbar(image, ax=ax, fraction=0.046)
    fig.savefig(OUTPUT_DIR / "混淆矩阵.png")
    plt.close(fig)

    # 用最后一个训练窗口做特征重要性，避免看未来数据。
    final_model = build_models()[best_name]
    train_end = len(data) - 20 - gap
    final_model.fit(x[:train_end], y[:train_end])
    if hasattr(final_model, "feature_importances_"):
        importance = final_model.feature_importances_
    else:
        sample = permutation_importance(
            final_model,
            x[train_end : train_end + 60],
            y[train_end : train_end + 60],
            n_repeats=5,
            random_state=42,
        )
        importance = sample.importances_mean
    order = np.argsort(importance)[-15:]
    fig, ax = plt.subplots(figsize=(8.5, 6))
    ax.barh(np.array(features)[order], importance[order], color="#2E6F9E")
    ax.set_title("特征重要性（最后一个训练窗口）", fontsize=13, fontweight="bold", color=NAVY)
    ax.grid(axis="x", alpha=0.2)
    fig.savefig(OUTPUT_DIR / "特征重要性.png")
    plt.close(fig)

    save_json(
        PROCESSED_DIR / "model_metrics.json",
        {
            "best_model": best_name,
            "cv_macro_f1": scores,
            "walk_forward_accuracy": accuracy,
            "walk_forward_macro_f1": macro_f1,
            "predictions": int(len(predictions)),
            "confusion_matrix": matrix.tolist(),
            "class_distribution": {LABELS[i]: int((predicted == i).sum()) for i in range(3)},
        },
    )
    print(f"\n预测结果：{PROCESSED_DIR / 'predictions.csv'}")
    print("注意：准确率高不等于赚钱，下一课会把信号放进回测。")


if __name__ == "__main__":
    main()
