"""第 11 课：模型部署，TorchScript + Flask API。"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from common import DEVICE, MODEL_DIR, NAVY, OUTPUT_DIR, TEAL, SmallCNN, accuracy, digits_tensors, ensure_dirs, save_json, set_seed, setup_plot


def main() -> None:
    setup_plot()
    ensure_dirs()
    set_seed(42)
    x_train, y_train, x_test, y_test = digits_tensors()
    loader = DataLoader(TensorDataset(x_train, y_train), batch_size=64, shuffle=True)
    model = SmallCNN().to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    loss_fn = nn.CrossEntropyLoss()
    for _ in range(12):
        model.train()
        for images, labels in loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            loss = loss_fn(model(images), labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
    test_accuracy = accuracy(model, x_test, y_test)
    model.eval()

    example = torch.randn(1, 1, 8, 8)
    traced = torch.jit.trace(model.cpu(), example)
    model_path = MODEL_DIR / "digit_cnn.pt"
    # TorchScript 在 Windows 中文路径下保存会误报父目录不存在，先写临时目录再复制。
    temp_path = Path(tempfile.gettempdir()) / "digit_cnn.pt"
    traced.save(str(temp_path))
    shutil.copy2(temp_path, model_path)
    temp_path.unlink(missing_ok=True)
    save_json(
        MODEL_DIR / "model_metadata.json",
        {
            "name": "digit_cnn",
            "version": "1.0.0",
            "input": "1x1x8x8, 0-16 灰度",
            "output": "10 类 softmax",
            "accuracy": round(test_accuracy, 4),
            "file": model_path.name,
        },
    )
    print(f"模型已导出：{model_path}（{model_path.stat().st_size / 1024:.1f} KB）")
    print(f"测试准确率：{test_accuracy:.2%}")

    # 用 Flask test client 直接验证 API。
    from deploy_app import app

    client = app.test_client()
    health = client.get("/health").get_json()
    print(f"健康检查：{health}")
    samples = []
    for index in range(3):
        response = client.post(
            "/predict",
            json={"pixels": (x_test[index, 0] * 16).round().flatten().tolist()},
        )
        body = response.get_json()
        samples.append(body)
        print(f"样本 {index}：预测 {body['digit']}，置信度 {body['confidence']:.2%}，真实 {int(y_test[index])}")

    lines = [
        "模型部署",
        "=" * 44,
        f"模型文件：{model_path}",
        f"模型大小：{model_path.stat().st_size / 1024:.1f} KB",
        f"测试准确率：{test_accuracy:.2%}",
        f"健康检查：{health}",
        "接口：POST /predict",
        "请求：{\"pixels\": [64 个 0-16 的数字]}",
        "响应：{\"digit\": 7, \"confidence\": 0.98, \"probabilities\": [...]}",
        "",
        "启动：python deploy_app.py，访问 http://127.0.0.1:5012",
    ]
    (OUTPUT_DIR / "11_部署.txt").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))

    figure, axes = plt.subplots(1, 3, figsize=(11, 3.8))
    for index, ax in enumerate(axes):
        ax.imshow(x_test[index, 0].numpy(), cmap="gray_r")
        ax.set_title(f"真值 {int(y_test[index])} / 预测 {samples[index]['digit']}", fontsize=10, color=TEAL)
        ax.axis("off")
    figure.suptitle("TorchScript 模型推理结果", fontsize=14, fontweight="bold", color=NAVY)
    figure.tight_layout()
    figure.savefig(OUTPUT_DIR / "11_部署.png")
    plt.close(figure)
    print(f"图表：{OUTPUT_DIR / '11_部署.png'}")


if __name__ == "__main__":
    main()
