"""第 1 课：金价速览与数据初识。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt

from common import GOLD, NAVY, OUTPUT_DIR, add_indicators, ensure_data, setup_plot


def main() -> None:
    setup_plot()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = add_indicators(ensure_data())
    latest = df.iloc[-1]
    previous = df.iloc[-2]

    change = latest["close"] / previous["close"] - 1
    high_52w = df["close"].tail(252).max()
    low_52w = df["close"].tail(252).min()

    lines = [
        "黄金期货日线速览",
        f"数据区间：{df.index.min().date()} 至 {df.index.max().date()}",
        f"最新交易日：{df.index[-1].date()}",
        f"收盘价：{latest['close']:.2f} 元/克",
        f"单日涨跌：{change * 100:+.2f}%",
        f"20 日均线：{latest['MA_20']:.2f}",
        f"60 日均线：{latest['MA_60']:.2f}",
        f"RSI(14)：{latest['RSI_14']:.2f}",
        f"近一年区间：{low_52w:.2f} - {high_52w:.2f}",
        f"近一年位置：{(latest['close'] - low_52w) / (high_52w - low_52w + 1e-8) * 100:.1f}%",
    ]
    text = "\n".join(lines)
    (OUTPUT_DIR / "金价速览.txt").write_text(text, encoding="utf-8")
    print(text)

    view = df.tail(260)
    fig, ax = plt.subplots(figsize=(12, 5.2))
    ax.plot(view.index, view["close"], color=GOLD, linewidth=1.8, label="收盘价")
    ax.plot(view.index, view["MA_20"], color=NAVY, linewidth=1.0, linestyle="--", label="MA20")
    ax.plot(view.index, view["MA_60"], color="#B03A2E", linewidth=1.0, linestyle=":", label="MA60")
    ax.fill_between(view.index, view["close"], view["close"].min(), color=GOLD, alpha=0.08)
    ax.set_title("沪金主力近一年走势", fontsize=15, fontweight="bold", color=NAVY)
    ax.set_ylabel("元/克")
    ax.legend(loc="upper left", frameon=False)
    ax.grid(alpha=0.25)
    fig.savefig(OUTPUT_DIR / "金价走势.png")
    plt.close(fig)
    print(f"\n图表已保存：{OUTPUT_DIR / '金价走势.png'}")


if __name__ == "__main__":
    main()
