"""第 5 课：过拟合、Dropout 和权重衰减。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from common import BLUE, DEVICE, GOLD, NAVY, OUTPUT_DIR, RED, accuracy, digits_tensors, ensure_dirs, set_seed, setup_plot


class BigMLP(nn.Module):
    def __init__(self, dropout=0.0):
        super().__init__()
        self.net = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64, 512),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(512, 10),
        )

    def forward(self, x):
        return self.net(x)


def train_model(model, train_x, train_y, val_x, val_y, epochs=80, weight_decay=0.0):
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=weight_decay)
    loss_fn = nn.CrossEntropyLoss()
    loader = DataLoader(TensorDataset(train_x, train_y), batch_size=32, shuffle=True)
    train_losses, val_losses = [], []
    for _ in range(epochs):
        model.train()
        total = 0.0
        for images, labels in loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            loss = loss_fn(model(images), labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total += loss.item() * len(images)
        train_losses.append(total / len(train_x))
        model.eval()
        with torch.no_grad():
            val_loss = loss_fn(model(val_x.to(DEVICE)), val_y.to(DEVICE)).item()
        val_losses.append(val_loss)
    return train_losses, val_losses


def main() -> None:
    setup_plot()
    ensure_dirs()
    set_seed(42)
    x_train, y_train, x_test, y_test = digits_tensors()
    train_x, train_y = x_train[:300], y_train[:300]
    val_x, val_y = x_train[300:600], y_train[300:600]

    overfit_model = BigMLP().to(DEVICE)
    overfit_train, overfit_val = train_model(overfit_model, train_x, train_y, val_x, val_y, epochs=80)

    regular_model = BigMLP(dropout=0.4).to(DEVICE)
    regular_train, regular_val = train_model(
        regular_model, train_x, train_y, val_x, val_y, epochs=80, weight_decay=1e-3
    )

    overfit_acc = accuracy(overfit_model, x_test, y_test)
    regular_acc = accuracy(regular_model, x_test, y_test)
    print(f"无正则：训练 loss {overfit_train[-1]:.3f}，验证 loss {overfit_val[-1]:.3f}，测试准确率 {overfit_acc:.2%}")
    print(f"Dropout + 权重衰减：训练 loss {regular_train[-1]:.3f}，验证 loss {regular_val[-1]:.3f}，测试准确率 {regular_acc:.2%}")

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(overfit_train, color=BLUE, linewidth=2, label="无正则-训练")
    ax.plot(overfit_val, color=RED, linewidth=2, linestyle="--", label="无正则-验证")
    ax.plot(regular_train, color="#5DADE2", linewidth=1.4, alpha=0.8, label="有正则-训练")
    ax.plot(regular_val, color=GOLD, linewidth=1.8, linestyle="--", label="有正则-验证")
    ax.set_title("小数据 + 大模型：过拟合与正则化", fontsize=14, fontweight="bold", color=NAVY)
    ax.set_xlabel("轮次")
    ax.set_ylabel("交叉熵")
    ax.legend(frameon=False, ncol=2)
    ax.grid(alpha=0.2)
    fig.savefig(OUTPUT_DIR / "05_过拟合.png")
    plt.close(fig)
    (OUTPUT_DIR / "05_过拟合.txt").write_text(
        f"无正则：训练 {overfit_train[-1]:.3f} / 验证 {overfit_val[-1]:.3f} / 测试 {overfit_acc:.2%}\n"
        f"有正则：训练 {regular_train[-1]:.3f} / 验证 {regular_val[-1]:.3f} / 测试 {regular_acc:.2%}\n",
        encoding="utf-8",
    )
    print(f"图表：{OUTPUT_DIR / '05_过拟合.png'}")


if __name__ == "__main__":
    main()
