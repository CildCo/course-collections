"""第 2 课：自动求导、梯度下降和线性回归。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import torch
import torch.nn as nn

from common import BLUE, GOLD, NAVY, OUTPUT_DIR, RED, TEAL, ensure_dirs, setup_plot


def main() -> None:
    setup_plot()
    ensure_dirs()
    torch.manual_seed(42)

    x_demo = torch.tensor([2.0], requires_grad=True)
    y_demo = x_demo ** 2 + 3 * x_demo + 1
    y_demo.backward()
    print(f"自动求导：dy/dx = {x_demo.grad.item():.1f}（手动公式 2x+3=7）")

    X = torch.linspace(0, 10, 100).reshape(-1, 1)
    true_w, true_b = 2.0, 1.0
    y = true_w * X + true_b + torch.randn(100, 1) * 0.5

    # 手写梯度下降
    w = torch.randn(1, 1, requires_grad=True)
    b = torch.zeros(1, 1, requires_grad=True)
    manual_losses = []
    for _ in range(300):
        prediction = X @ w + b
        loss = ((prediction - y) ** 2).mean()
        loss.backward()
        with torch.no_grad():
            w -= 0.01 * w.grad
            b -= 0.01 * b.grad
        w.grad.zero_()
        b.grad.zero_()
        manual_losses.append(loss.item())

    # nn.Linear
    model = nn.Linear(1, 1)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    loss_fn = nn.MSELoss()
    api_losses = []
    for _ in range(300):
        prediction = model(X)
        loss = loss_fn(prediction, y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        api_losses.append(loss.item())

    manual_w, manual_b = w.item(), b.item()
    api_w, api_b = model.weight.item(), model.bias.item()
    print(f"手写梯度下降：w={manual_w:.3f}, b={manual_b:.3f}, loss={manual_losses[-1]:.3f}")
    print(f"nn.Linear：w={api_w:.3f}, b={api_b:.3f}, loss={api_losses[-1]:.3f}")

    lines = [
        "自动求导与线性回归",
        "=" * 44,
        f"真实参数：w={true_w}, b={true_b}",
        f"手写实现：w={manual_w:.3f}, b={manual_b:.3f}",
        f"nn.Linear：w={api_w:.3f}, b={api_b:.3f}",
        "",
        "训练五步：前向传播 → 算损失 → backward → 更新参数 → 梯度清零",
    ]
    (OUTPUT_DIR / "02_自动求导.txt").write_text("\n".join(lines), encoding="utf-8")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    axes[0].plot(manual_losses, color=BLUE, linewidth=2, label="手写梯度下降")
    axes[0].plot(api_losses, color=TEAL, linewidth=2, linestyle="--", label="nn.Linear")
    axes[0].set_title("Loss 下降曲线", loc="left", color=NAVY)
    axes[0].set_xlabel("训练轮次")
    axes[0].set_ylabel("MSE")
    axes[0].legend(frameon=False)
    axes[0].grid(alpha=0.2)

    axes[1].scatter(X.numpy(), y.numpy(), s=12, color="#BDC3C7", alpha=0.7, label="带噪声数据")
    axes[1].plot(X.numpy(), (true_w * X + true_b).numpy(), color=GOLD, linewidth=2, label="真实直线")
    axes[1].plot(X.numpy(), (api_w * X + api_b).numpy(), color=RED, linewidth=2, linestyle="--", label="模型拟合")
    axes[1].set_title("线性回归拟合结果", loc="left", color=NAVY)
    axes[1].legend(frameon=False)
    axes[1].grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "02_自动求导.png")
    plt.close(fig)
    print(f"图表：{OUTPUT_DIR / '02_自动求导.png'}")


if __name__ == "__main__":
    main()
