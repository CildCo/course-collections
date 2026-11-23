"""第 3 课：softmax 回归识别手写数字。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from common import BLUE, DEVICE, NAVY, OUTPUT_DIR, TEAL, accuracy, digits_tensors, ensure_dirs, set_seed, setup_plot


def main() -> None:
    setup_plot()
    ensure_dirs()
    set_seed(42)
    x_train, y_train, x_test, y_test = digits_tensors()
    train_loader = DataLoader(TensorDataset(x_train, y_train), batch_size=64, shuffle=True)

    model = nn.Sequential(nn.Flatten(), nn.Linear(8 * 8, 10)).to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    loss_fn = nn.CrossEntropyLoss()
    losses = []
    for _ in range(30):
        model.train()
        total_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            prediction = model(images)
            loss = loss_fn(prediction, labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * len(images)
        losses.append(total_loss / len(x_train))

    test_accuracy = accuracy(model, x_test, y_test)
    print(f"训练样本：{len(x_train)}，测试样本：{len(x_test)}")
    print(f"softmax 回归测试准确率：{test_accuracy:.2%}")

    model.eval()
    with torch.no_grad():
        sample_logits = model(x_test[:10].to(DEVICE))
        predictions = sample_logits.argmax(dim=1).cpu()

    fig, axes = plt.subplots(2, 5, figsize=(11, 5))
    for index, ax in enumerate(axes.flat):
        ax.imshow(x_test[index, 0].numpy(), cmap="gray_r")
        ax.set_title(f"真值 {int(y_test[index])} / 预测 {int(predictions[index])}", fontsize=9, color=TEAL if predictions[index] == y_test[index] else "red")
        ax.axis("off")
    fig.suptitle(f"softmax 回归：测试准确率 {test_accuracy:.1%}", fontsize=14, fontweight="bold", color=NAVY)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "03_softmax.png")
    plt.close(fig)

    (OUTPUT_DIR / "03_softmax.txt").write_text(
        f"softmax 回归\n训练样本：{len(x_train)}\n测试准确率：{test_accuracy:.2%}\n最终 loss：{losses[-1]:.4f}\n",
        encoding="utf-8",
    )
    print(f"图表：{OUTPUT_DIR / '03_softmax.png'}")


if __name__ == "__main__":
    main()
