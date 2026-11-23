"""第 4 课：多层感知机，从线性到非线性。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from common import BLUE, DEVICE, NAVY, OUTPUT_DIR, TEAL, accuracy, digits_tensors, ensure_dirs, set_seed, setup_plot


class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 10),
        )

    def forward(self, x):
        return self.net(x)


def main() -> None:
    setup_plot()
    ensure_dirs()
    set_seed(42)
    x_train, y_train, x_test, y_test = digits_tensors()
    loader = DataLoader(TensorDataset(x_train, y_train), batch_size=64, shuffle=True)

    model = MLP().to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    loss_fn = nn.CrossEntropyLoss()
    losses = []
    for _ in range(40):
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
    print(f"MLP 测试准确率：{test_accuracy:.2%}")
    print(f"最终 loss：{losses[-1]:.4f}")

    model.eval()
    with torch.no_grad():
        predictions = model(x_test[:10].to(DEVICE)).argmax(dim=1).cpu()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    axes[0].plot(losses, color=BLUE, linewidth=2)
    axes[0].set_title("MLP 训练 Loss", loc="left", color=NAVY)
    axes[0].set_xlabel("轮次")
    axes[0].set_ylabel("交叉熵")
    axes[0].grid(alpha=0.2)

    sample = x_test[:10, 0].numpy()
    axes[1].imshow(sample.reshape(2, 5, 8, 8).transpose(0, 2, 1, 3).reshape(16, 40), cmap="gray_r")
    axes[1].set_title("预测样本（左到右：0-4 / 5-9）", loc="left", color=NAVY)
    axes[1].axis("off")
    fig.suptitle(f"MLP：测试准确率 {test_accuracy:.1%}", fontsize=14, fontweight="bold", color=NAVY)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "04_MLP.png")
    plt.close(fig)
    (OUTPUT_DIR / "04_MLP.txt").write_text(
        f"MLP（64→128→64→10）\n测试准确率：{test_accuracy:.2%}\n最终 loss：{losses[-1]:.4f}\n",
        encoding="utf-8",
    )
    print(f"图表：{OUTPUT_DIR / '04_MLP.png'}")


if __name__ == "__main__":
    main()
