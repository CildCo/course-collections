"""第 7 课：迁移学习，冻结卷积层做新分类。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import copy

import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from common import BLUE, DEVICE, GOLD, NAVY, OUTPUT_DIR, TEAL, SmallCNN, accuracy, digits_tensors, ensure_dirs, set_seed, setup_plot


def train(model, x, y, epochs=12):
    loader = DataLoader(TensorDataset(x, y), batch_size=64, shuffle=True)
    optimizer = torch.optim.Adam([parameter for parameter in model.parameters() if parameter.requires_grad], lr=0.002)
    loss_fn = nn.CrossEntropyLoss()
    losses = []
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
        losses.append(total / len(x))
    return losses


def main() -> None:
    setup_plot()
    ensure_dirs()
    set_seed(42)
    x_train, y_train, x_test, y_test = digits_tensors()

    source_mask = y_train < 5
    source_x, source_y = x_train[source_mask], y_train[source_mask]
    target_train_mask = y_train >= 5
    target_x, target_y = x_train[target_train_mask], y_train[target_train_mask] - 5
    target_test_mask = y_test >= 5
    target_test_x, target_test_y = x_test[target_test_mask], y_test[target_test_mask] - 5

    source_model = SmallCNN(num_classes=5).to(DEVICE)
    source_losses = train(source_model, source_x, source_y, epochs=12)
    print(f"源任务（0-4）训练完成，最终 loss {source_losses[-1]:.3f}")

    frozen_model = SmallCNN(num_classes=5).to(DEVICE)
    frozen_model.load_state_dict(copy.deepcopy(source_model.state_dict()))
    for parameter in frozen_model.parameters():
        parameter.requires_grad = False
    frozen_model.classifier[-1] = nn.Linear(64, 5).to(DEVICE)
    frozen_losses = train(frozen_model, target_x, target_y, epochs=12)

    finetune_model = SmallCNN(num_classes=5).to(DEVICE)
    finetune_model.load_state_dict(copy.deepcopy(source_model.state_dict()))
    finetune_model.classifier[-1] = nn.Linear(64, 5).to(DEVICE)
    for parameter in finetune_model.parameters():
        parameter.requires_grad = True
    finetune_losses = train(finetune_model, target_x, target_y, epochs=12)

    scratch_model = SmallCNN(num_classes=5).to(DEVICE)
    scratch_losses = train(scratch_model, target_x, target_y, epochs=12)

    frozen_acc = accuracy(frozen_model, target_test_x, target_test_y)
    finetune_acc = accuracy(finetune_model, target_test_x, target_test_y)
    scratch_acc = accuracy(scratch_model, target_test_x, target_test_y)
    print(f"冻结卷积：测试准确率 {frozen_acc:.2%}")
    print(f"全参数微调：测试准确率 {finetune_acc:.2%}")
    print(f"从零训练：测试准确率 {scratch_acc:.2%}")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    axes[0].plot(frozen_losses, color="#95A5A6", linewidth=1.5, label="冻结卷积")
    axes[0].plot(finetune_losses, color=TEAL, linewidth=2, label="全参数微调")
    axes[0].plot(scratch_losses, color=GOLD, linewidth=2, linestyle="--", label="从零训练")
    axes[0].set_title("目标任务训练 Loss", loc="left", color=NAVY)
    axes[0].set_xlabel("轮次")
    axes[0].legend(frameon=False)
    axes[0].grid(alpha=0.2)

    labels = ["冻结卷积", "全参数微调", "从零训练"]
    values = [frozen_acc * 100, finetune_acc * 100, scratch_acc * 100]
    bars = axes[1].bar(labels, values, color=["#95A5A6", TEAL, GOLD])
    for bar in bars:
        axes[1].text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{bar.get_height():.1f}%", ha="center", va="bottom")
    axes[1].set_ylim(0, 105)
    axes[1].set_title("目标任务测试准确率", loc="left", color=NAVY)
    axes[1].grid(axis="y", alpha=0.2)
    fig.suptitle("迁移学习：站在已有特征的肩膀上", fontsize=14, fontweight="bold", color=NAVY)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "07_迁移学习.png")
    plt.close(fig)
    report = chr(10).join([
        "源任务 0-4，目标任务 5-9",
        f"冻结卷积准确率：{frozen_acc:.2%}",
        f"全参数微调准确率：{finetune_acc:.2%}",
        f"从零训练准确率：{scratch_acc:.2%}",
    ])
    (OUTPUT_DIR / "07_迁移学习.txt").write_text(report + chr(10), encoding="utf-8")
    print(f"图表：{OUTPUT_DIR / '07_迁移学习.png'}")


if __name__ == "__main__":
    main()
