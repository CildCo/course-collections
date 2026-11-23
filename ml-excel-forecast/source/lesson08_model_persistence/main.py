"""第 8 课：给模型装上长期记忆（持久化与重新加载）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from common import MODEL_DIR, OUTPUT_DIR, PROCESSED_DIR, customer_features, save_json, setup_plot

FEATURES = ["R_最近间隔", "F_购买次数", "M_累计金额", "平均客单价", "累计数量", "品类数", "在网天数", "月均购买"]


def main() -> None:
    setup_plot()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    customers = customer_features()
    x = customers[FEATURES]
    y = customers["流失客户"]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
    model = RandomForestClassifier(
        n_estimators=260,
        max_depth=6,
        min_samples_leaf=10,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(x_train, y_train)

    model_path = MODEL_DIR / "churn_model.joblib"
    joblib.dump(model, model_path, compress=3)
    metadata = {
        "model_name": "churn_random_forest",
        "version": "1.0.0",
        "features": FEATURES,
        "train_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "target": "流失客户",
        "file": str(model_path.name),
    }
    save_json(MODEL_DIR / "model_metadata.json", metadata)

    # 模拟下一次启动：不重新训练，直接从磁盘加载。
    loaded = joblib.load(model_path)
    sample = x_test.head(20)
    original = model.predict_proba(sample)[:, 1]
    restored = loaded.predict_proba(sample)[:, 1]
    max_diff = float(abs(original - restored).max())

    output = customers.loc[x_test.index, ["客户ID", "客户名称", "R_最近间隔", "M_累计金额", "流失客户"]].copy()
    output["流失概率"] = model.predict_proba(x_test)[:, 1].round(4)
    output.to_csv(PROCESSED_DIR / "persisted_model_predictions.csv", index=False, encoding="utf-8-sig")

    lines = [
        "模型持久化说明",
        "=" * 44,
        f"模型文件：{model_path}",
        f"模型大小：{model_path.stat().st_size / 1024:.1f} KB",
        f"版本：{metadata['version']}",
        f"训练样本：{len(x_train)}，测试样本：{len(x_test)}",
        f"特征数：{len(FEATURES)}",
        f"重新加载后的最大概率误差：{max_diff:.10f}",
        "",
        "使用方式：",
        "  import joblib",
        "  model = joblib.load('models/churn_model.joblib')",
        "  model.predict_proba(new_customers[FEATURES])",
        "",
        "注意：特征顺序必须和训练时一致，模型版本变化后要重新校验。",
    ]
    text = "\n".join(lines)
    (OUTPUT_DIR / "模型持久化说明.txt").write_text(text, encoding="utf-8")
    print(text)

    if max_diff > 1e-9:
        raise SystemExit("模型重新加载后预测不一致")
    print(f"\n预测结果：{PROCESSED_DIR / 'persisted_model_predictions.csv'}")


if __name__ == "__main__":
    main()
