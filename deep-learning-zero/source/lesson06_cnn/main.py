"""第 6 课：CNN 卷积神经网络识别手写数字。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from common import BLUE, DEVICE, NAVY, OUTPUT_DIR, TEAL, SmallCNN, accuracy, digits_tensors, ensure_dirs, set_seed, setup_plot


def main() -> None:
    setup_plot()
    ensure_dirs()
    set_seed(42)
    x_train, y_train, x_test, y_test = digits_tensors()
    loader = DataLoader(TensorDataset(x_train, y_train), batch_size=64, shuffle=True)
    model = SmallCNN().to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    loss_fn = nn.CrossEntropyLoss()
    losses = []
    for _ in range(24):
        model.train()
        total = 0.0
        for images, labels in loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            loss = loss_fn(model(images), labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total += loss.item() * len(images)
        losses.append(total / len(x_train))

    test_accuracy = accuracy(model, x_test, y_test)
    print(f"CNN 测试准确率：{test_accuracy:.2%}")
    print(f"最终 loss：{losses[-1]:.4f}")

    model.eval()
    with torch.no_grad():
        predictions = model(x_test[:10].to(DEVICE)).argmax(dim=1).cpu()
        features = model.features(x_test[:4].to(DEVICE)).cpu()

    fig, axes = plt.subplots(2, 2, figsize=(11, 7.5))
    axes[0, 0].plot(losses, color=BLUE, linewidth=2)
    axes[0, 0].set_title("CNN 训练 Loss", loc="left", color=NAVY)
    axes[0, 0].grid(alpha=0.2)
    axes[0, 0].set_xlabel("轮次")

    sample = x_test[:10, 0].numpy()
    axes[0, 1].imshow(sample.reshape(2, 5, 8, 8).transpose(0, 2, 1, 3).reshape(16, 40), cmap="gray_r")
    axes[0, 1].set_title("预测样本", loc="left", color=NAVY)
    axes[0, 1].axis("off")

    axes[1, 0].imshow(features[0, 0].numpy(), cmap="viridis")
    axes[1, 0].set_title("第一张图的特征图", loc="left", color=NAVY)
    axes[1, 0].axis("off")
    axes[1, 1].imshow(x_test[0, 0].numpy(), cmap="gray_r")
    axes[1, 1].set_title(f"原图（真值 {int(y_test[0])} / 预测 {int(predictions[0])}）", loc="left", color=NAVY)
    axes[1, 1].axis("off")
    fig.suptitle(f"CNN：测试准确率 {test_accuracy:.1%}", fontsize=15, fontweight="bold", color=NAVY)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "06_CNN.png")
    plt.close(fig)
    (OUTPUT_DIR / "06_CNN.txt").write_text(
        f"SmallCNN（16→32 通道）\n测试准确率：{test_accuracy:.2%}\n最终 loss：{losses[-1]:.4f}\n",
        encoding="utf-8",
    )
    print(f"图表：{OUTPUT_DIR / '06_CNN.png'}")


if __name__ == "__main__":
    main()
