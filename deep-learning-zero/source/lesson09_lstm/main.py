"""第 9 课：LSTM 字符级文本生成。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import torch
import torch.nn as nn

from common import BLUE, DEVICE, NAVY, OUTPUT_DIR, ensure_dirs, poetry_text, set_seed, setup_plot


class CharLSTM(nn.Module):
    def __init__(self, vocab_size, embed_dim=48, hidden_dim=96):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x, hidden=None):
        embedded = self.embedding(x)
        output, hidden = self.lstm(embedded, hidden)
        return self.fc(output), hidden


def main() -> None:
    setup_plot()
    ensure_dirs()
    set_seed(42)
    text = poetry_text()
    chars = sorted(set(text))
    stoi = {char: index for index, char in enumerate(chars)}
    itos = {index: char for char, index in stoi.items()}
    encoded = torch.tensor([stoi[char] for char in text])
    sequence_length = 20
    inputs, targets = [], []
    for index in range(len(encoded) - sequence_length):
        inputs.append(encoded[index : index + sequence_length])
        targets.append(encoded[index + sequence_length])
    x = torch.stack(inputs)
    y = torch.stack(targets)

    model = CharLSTM(len(chars)).to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.003)
    loss_fn = nn.CrossEntropyLoss()
    losses = []
    for _ in range(35):
        model.train()
        permutation = torch.randperm(len(x))
        total = 0.0
        for start in range(0, len(x), 64):
            index = permutation[start : start + 64]
            batch_x, batch_y = x[index].to(DEVICE), y[index].to(DEVICE)
            logits, _ = model(batch_x)
            loss = loss_fn(logits[:, -1, :], batch_y)
            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total += loss.item() * len(index)
        losses.append(total / len(x))
    print(f"训练样本：{len(x)}，字符表：{len(chars)}，最终 loss：{losses[-1]:.3f}")

    def generate(seed="明月", length=40, temperature=0.8):
        model.eval()
        current = torch.tensor([[stoi.get(char, 0) for char in seed]], device=DEVICE)
        result = list(seed)
        hidden = None
        with torch.no_grad():
            logits, hidden = model(current, hidden)
            for _ in range(length):
                probabilities = torch.softmax(logits[0, -1] / temperature, dim=0)
                next_index = int(torch.multinomial(probabilities, 1).item())
                result.append(itos[next_index])
                current = torch.tensor([[next_index]], device=DEVICE)
                logits, hidden = model(current, hidden)
        return "".join(result)

    poem = generate("明月", 48)
    print(f"生成结果：{poem}")

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(losses, color=BLUE, linewidth=2)
    ax.set_title("LSTM 字符级训练 Loss", fontsize=14, fontweight="bold", color=NAVY)
    ax.set_xlabel("轮次")
    ax.set_ylabel("交叉熵")
    ax.grid(alpha=0.2)
    fig.savefig(OUTPUT_DIR / "09_LSTM.png")
    plt.close(fig)

    (OUTPUT_DIR / "09_LSTM.txt").write_text(
        f"字符表大小：{len(chars)}\n训练序列：{len(x)}\n最终 loss：{losses[-1]:.4f}\n生成：{poem}\n",
        encoding="utf-8",
    )
    print(f"图表：{OUTPUT_DIR / '09_LSTM.png'}")


if __name__ == "__main__":
    main()
