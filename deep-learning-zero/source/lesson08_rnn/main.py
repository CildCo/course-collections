"""第 8 课：RNN 循环神经网络预测序列。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn

from common import BLUE, DEVICE, NAVY, OUTPUT_DIR, RED, ensure_dirs, set_seed, setup_plot


class RNNModel(nn.Module):
    def __init__(self, hidden=32):
        super().__init__()
        self.rnn = nn.RNN(input_size=1, hidden_size=hidden, batch_first=True)
        self.fc = nn.Linear(hidden, 1)

    def forward(self, x):
        output, _ = self.rnn(x)
        return self.fc(output[:, -1, :])


def main() -> None:
    setup_plot()
    ensure_dirs()
    set_seed(42)
    steps = np.arange(0, 1200)
    series = np.sin(steps * 0.05) + 0.12 * np.sin(steps * 0.31) + np.random.normal(0, 0.04, len(steps))
    window = 20

    features, targets = [], []
    for index in range(len(series) - window):
        features.append(series[index : index + window])
        targets.append(series[index + window])
    features = torch.tensor(np.array(features), dtype=torch.float32).unsqueeze(-1)
    targets = torch.tensor(np.array(targets), dtype=torch.float32).unsqueeze(-1)
    split = int(len(features) * 0.8)
    x_train, y_train = features[:split].to(DEVICE), targets[:split].to(DEVICE)
    x_test, y_test = features[split:].to(DEVICE), targets[split:].to(DEVICE)

    model = RNNModel().to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    loss_fn = nn.MSELoss()
    losses = []
    for _ in range(60):
        model.train()
        permutation = torch.randperm(len(x_train))
        total = 0.0
        for start in range(0, len(x_train), 64):
            index = permutation[start : start + 64]
            loss = loss_fn(model(x_train[index]), y_train[index])
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total += loss.item() * len(index)
        losses.append(total / len(x_train))

    model.eval()
    with torch.no_grad():
        prediction = model(x_test).cpu().numpy().flatten()
    actual = y_test.cpu().numpy().flatten()
    mse = float(np.mean((prediction - actual) ** 2))
    print(f"测试 MSE：{mse:.5f}")
    print(f"测试 MAE：{np.mean(np.abs(prediction - actual)):.5f}")

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
    axes[0].plot(losses, color=BLUE, linewidth=2)
    axes[0].set_title("RNN 训练 Loss", loc="left", color=NAVY)
    axes[0].set_xlabel("轮次")
    axes[0].grid(alpha=0.2)
    axes[1].plot(actual[:180], color=BLUE, linewidth=1.8, label="真实")
    axes[1].plot(prediction[:180], color=RED, linewidth=1.5, linestyle="--", label="预测")
    axes[1].set_title("序列预测结果（局部）", loc="left", color=NAVY)
    axes[1].legend(frameon=False)
    axes[1].grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "08_RNN.png")
    plt.close(fig)
    (OUTPUT_DIR / "08_RNN.txt").write_text(f"RNN 序列预测\n测试 MSE：{mse:.5f}\n", encoding="utf-8")
    print(f"图表：{OUTPUT_DIR / '08_RNN.png'}")


if __name__ == "__main__":
    main()
