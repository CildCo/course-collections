"""第 1 课：环境检查与张量基础。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import torch

from common import BLUE, DEVICE, GOLD, NAVY, OUTPUT_DIR, TEAL, ensure_dirs, setup_plot


def main() -> None:
    setup_plot()
    ensure_dirs()
    torch.manual_seed(42)

    a = torch.tensor([1, 2, 3])
    b = torch.zeros(2, 3)
    c = torch.ones(2, 3)
    d = torch.eye(4)
    e = torch.randn(2, 3)
    f = torch.arange(10)
    g = torch.linspace(0, 1, 5)
    x = torch.arange(12, dtype=torch.float32).reshape(3, 4)
    v = torch.tensor([10.0, 20.0, 30.0, 40.0])

    lines = [
        "PyTorch 环境与张量",
        "=" * 46,
        f"PyTorch 版本：{torch.__version__}",
        f"CUDA 可用：{torch.cuda.is_available()}",
        f"当前设备：{DEVICE}",
        "",
        f"列表张量：{a.tolist()}，shape={tuple(a.shape)}",
        f"全零矩阵 shape：{tuple(b.shape)}",
        f"单位矩阵 shape：{tuple(d.shape)}",
        f"随机矩阵 shape：{tuple(e.shape)}",
        f"arange：{f.tolist()}",
        f"linspace：{[round(float(v), 2) for v in g]}",
        "",
        f"矩阵 shape：{tuple(x.shape)}",
        f"第 0 行：{x[0].tolist()}",
        f"第 1 列：{x[:, 1].tolist()}",
        f"左上 2x2：{x[:2, :2].tolist()}",
        f"大于 5 的元素：{x[x > 5].tolist()}",
        f"展平后 shape：{tuple(x.view(-1).shape)}",
        f"矩阵 + 向量广播：{(x + v).tolist()}",
    ]

    sizes = [100, 300, 500]
    cpu_times = []
    for size in sizes:
        left = torch.randn(size, size)
        right = torch.randn(size, size)
        started = time.perf_counter()
        left @ right
        cpu_times.append(time.perf_counter() - started)
    lines.append("")
    lines.append("CPU 矩阵乘法耗时（秒）：")
    lines.extend(f"  {size}x{size}：{elapsed:.4f}" for size, elapsed in zip(sizes, cpu_times))

    if torch.cuda.is_available():
        gpu_times = []
        for size in sizes:
            left = torch.randn(size, size, device="cuda")
            right = torch.randn(size, size, device="cuda")
            torch.cuda.synchronize()
            started = time.perf_counter()
            left @ right
            torch.cuda.synchronize()
            gpu_times.append(time.perf_counter() - started)
        lines.append("GPU 矩阵乘法耗时（秒）：")
        lines.extend(f"  {size}x{size}：{elapsed:.4f}" for size, elapsed in zip(sizes, gpu_times))
    else:
        gpu_times = []

    text = "\n".join(lines)
    (OUTPUT_DIR / "01_环境与张量.txt").write_text(text, encoding="utf-8")
    print(text)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    positions = range(len(sizes))
    width = 0.36 if gpu_times else 0.5
    ax.bar([p - (width / 2 if gpu_times else 0) for p in positions], cpu_times, width, color=BLUE, label="CPU")
    if gpu_times:
        ax.bar([p + width / 2 for p in positions], gpu_times, width, color=TEAL, label="GPU")
    ax.set_xticks(list(positions), [f"{size}×{size}" for size in sizes])
    ax.set_ylabel("耗时（秒）")
    ax.set_title("矩阵乘法耗时对比", fontsize=14, fontweight="bold", color=NAVY)
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.2)
    fig.savefig(OUTPUT_DIR / "01_环境与张量.png")
    plt.close(fig)
    print(f"\n图表：{OUTPUT_DIR / '01_环境与张量.png'}")


if __name__ == "__main__":
    main()
