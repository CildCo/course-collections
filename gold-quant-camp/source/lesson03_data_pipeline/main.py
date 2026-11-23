"""第 3 课：数据采集与宏观因子。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt

from common import (
    BLUE,
    GOLD,
    GREEN,
    NAVY,
    OUTPUT_DIR,
    PROCESSED_DIR,
    RED,
    add_indicators,
    ensure_data,
    setup_plot,
)


def main() -> None:
    setup_plot()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    raw = ensure_data(refresh=True)
    data = add_indicators(raw)
    data.to_csv(PROCESSED_DIR / "gold_pipeline.csv", encoding="utf-8-sig")

    print("数据管道完成")
    print(f"样本数：{len(data)}")
    print(f"时间范围：{data.index.min().date()} 至 {data.index.max().date()}")
    print(f"字段数：{len(data.columns)}")
    print(f"缺失值：{int(data.isna().sum().sum())}")
    print("\n最新宏观因子：")
    for column, label in (
        ("Gold_Silver_Ratio", "金银比"),
        ("Copper_Gold_Ratio", "铜金比"),
        ("Oil_Gold_Ratio", "油金比"),
        ("RSI_14", "RSI(14)"),
    ):
        print(f"  {label}：{data[column].iloc[-1]:.3f}")

    factors = [
        ("Gold_Silver_Ratio", "金银比", GOLD),
        ("Copper_Gold_Ratio", "铜金比", RED),
        ("Oil_Gold_Ratio", "油金比", GREEN),
        ("RSI_14", "RSI(14)", BLUE),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(13, 7.2), sharex=True)
    for ax, (column, title, color) in zip(axes.flat, factors):
        ax.plot(data.index, data[column], color=color, linewidth=1.2)
        ax.set_title(title, loc="left", fontsize=12, color=NAVY)
        ax.grid(alpha=0.22)
        if column == "RSI_14":
            ax.axhline(70, color=RED, linestyle="--", linewidth=0.8, alpha=0.6)
            ax.axhline(30, color=GREEN, linestyle="--", linewidth=0.8, alpha=0.6)
    for ax in axes.flat:
        ax.tick_params(labelsize=8)
    fig.suptitle("黄金的跨资产宏观因子", fontsize=15, fontweight="bold", color=NAVY)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "宏观因子.png")
    plt.close(fig)

    summary = [
        "数据采集与清洗说明",
        f"原始表：{len(raw)} 行 × {len(raw.columns)} 列",
        "对齐方式：按交易日索引合并，休市用前值填充。",
        "单位换算：沪金元/克，白银元/千克，计算金银比时白银乘 1000。",
        "衍生因子：金银比、铜金比、油金比、豆粕-黄金相对强弱、RSI、波动率。",
        f"输出：{PROCESSED_DIR / 'gold_pipeline.csv'}",
    ]
    (OUTPUT_DIR / "数据管道说明.txt").write_text("\n".join(summary), encoding="utf-8")
    print(f"\n图表已保存：{OUTPUT_DIR / '宏观因子.png'}")


if __name__ == "__main__":
    main()
