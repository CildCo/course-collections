"""第 10 课：Word2Vec Skip-gram 字向量。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
from sklearn.decomposition import PCA

from common import BLUE, DEVICE, NAVY, OUTPUT_DIR, TEAL, ensure_dirs, poetry_text, set_seed, setup_plot


class SkipGram(nn.Module):
    def __init__(self, vocab_size, embed_dim=64):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.fc = nn.Linear(embed_dim, vocab_size)

    def forward(self, center):
        return self.fc(self.embedding(center))


def main() -> None:
    setup_plot()
    ensure_dirs()
    set_seed(42)
    text = poetry_text()
    chars = sorted(set(text))
    stoi = {char: index for index, char in enumerate(chars)}
    itos = {index: char for char, index in stoi.items()}
    window = 3
    centers, contexts = [], []
    for index, char in enumerate(text):
        for offset in range(-window, window + 1):
            neighbor = index + offset
            if offset == 0 or neighbor < 0 or neighbor >= len(text):
                continue
            centers.append(stoi[char])
            contexts.append(stoi[text[neighbor]])
    centers = torch.tensor(centers)
    contexts = torch.tensor(contexts)
    print(f"语料字数：{len(text)}，字表：{len(chars)}，训练对：{len(centers)}")

    model = SkipGram(len(chars)).to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.003)
    loss_fn = nn.CrossEntropyLoss()
    losses = []
    for _ in range(25):
        model.train()
        permutation = torch.randperm(len(centers))
        total = 0.0
        for start in range(0, len(centers), 256):
            index = permutation[start : start + 256]
            logits = model(centers[index].to(DEVICE))
            loss = loss_fn(logits, contexts[index].to(DEVICE))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total += loss.item() * len(index)
        losses.append(total / len(centers))
    print(f"最终 loss：{losses[-1]:.3f}")

    vectors = model.embedding.weight.detach().cpu().numpy()
    normalized = vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-8)

    def similar(char, topn=6):
        if char not in stoi:
            return []
        index = stoi[char]
        scores = normalized @ normalized[index]
        order = np.argsort(scores)[::-1]
        result = []
        for item in order:
            if int(item) == index:
                continue
            result.append((itos[int(item)], float(scores[item])))
            if len(result) >= topn:
                break
        return result

    def analogy(a, b, c):
        if not all(char in stoi for char in (a, b, c)):
            return []
        vector = normalized[stoi[a]] - normalized[stoi[b]] + normalized[stoi[c]]
        vector = vector / (np.linalg.norm(vector) + 1e-8)
        scores = normalized @ vector
        result = []
        for item in np.argsort(scores)[::-1]:
            char = itos[int(item)]
            if char in {a, b, c}:
                continue
            result.append((char, float(scores[item])))
            if len(result) >= 5:
                break
        return result

    lines = ["Word2Vec Skip-gram 字向量", "=" * 44, f"语料：{len(text)} 字，字表：{len(chars)}", f"最终 loss：{losses[-1]:.3f}", ""]
    for char in ["月", "山", "花", "风", "夜", "云"]:
        neighbors = similar(char)
        lines.append(f"{char} → " + "，".join(f"{item}({score:.2f})" for item, score in neighbors))
    lines.append("")
    lines.append("类比：明 - 光 + 暗 → " + "，".join(f"{item}({score:.2f})" for item, score in analogy("明", "光", "暗")))

    # PCA 可视化：选高频字和几个关键词。
    from collections import Counter

    frequent = [char for char, _ in Counter(text).most_common(45)]
    selected = list(dict.fromkeys(frequent + list("月夜山水花风雲春雨秋明暗光日君")))
    selected = [char for char in selected if char in stoi][:55]
    matrix = vectors[[stoi[char] for char in selected]]
    points = PCA(n_components=2, random_state=42).fit_transform(matrix)
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(points[:, 0], points[:, 1], s=28, color=TEAL, alpha=0.7)
    for (x, y), char in zip(points, selected):
        ax.annotate(char, (x, y), fontsize=11, color=NAVY, xytext=(3, 3), textcoords="offset points")
    ax.set_title("唐诗字向量 PCA 投影", fontsize=15, fontweight="bold", color=NAVY)
    ax.grid(alpha=0.15)
    fig.savefig(OUTPUT_DIR / "10_Word2Vec.png")
    plt.close(fig)

    text_output = "\n".join(lines)
    (OUTPUT_DIR / "10_Word2Vec.txt").write_text(text_output, encoding="utf-8")
    print(text_output)
    print(f"图表：{OUTPUT_DIR / '10_Word2Vec.png'}")


if __name__ == "__main__":
    main()
