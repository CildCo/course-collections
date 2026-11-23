"""第 9 课：最终复盘——胜率、盈亏比和基准。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import pandas as pd

from common import GOLD, GREEN, NAVY, OUTPUT_DIR, PROCESSED_DIR, RED, load_json, setup_plot


def main() -> None:
    setup_plot()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    metrics = load_json(PROCESSED_DIR / "metrics.json")
    trades = pd.read_csv(PROCESSED_DIR / "trades.csv")
    wins = trades[trades["pnl"] > 0]
    losses = trades[trades["pnl"] < 0]
    win_rate = len(wins) / len(trades) if len(trades) else 0
    payoff = wins["pnl"].mean() / abs(losses["pnl"].mean()) if len(wins) and len(losses) else 0

    findings = []
    if win_rate >= 0.45 and payoff < 1.1:
        findings.append(
            f"胜率 {win_rate:.1%} 看起来不差，但盈亏比只有 {payoff:.2f}。"
            "赚一次和亏一次差不多大，手续费和滑点会把优势磨平。"
        )
    if metrics["annual_return"] < metrics["benchmark_return"]:
        findings.append(
            f"策略年化 {metrics['annual_return']:.2%}，买入持有基准 {metrics['benchmark_return']:.2%}。"
            "在单边上涨行情里，频繁进出很容易踏空主升浪。"
        )
    if metrics["max_drawdown"] < -0.12:
        findings.append(
            f"最大回撤 {metrics['max_drawdown']:.2%}，对期货账户来说已经需要认真控制仓位。"
        )
    if metrics["max_consecutive_losses"] >= 3:
        findings.append(
            f"最大连续亏损 {metrics['max_consecutive_losses']} 次，震荡市里的假信号是主要来源。"
        )

    lessons = [
        "数据质量比模型花哨更重要：缺失、单位和时间对齐错一处，后面全错。",
        "特征要能解释：金银比、铜金比、油金比代表的是不同的宏观逻辑。",
        "时间序列必须按时间切分，并在训练集和验证集之间留空窗期。",
        "回测必须滞后信号，计入手续费、滑点和保证金，否则只是纸上收益。",
        "胜率高不等于赚钱，最终要看盈亏比、回撤和资金曲线。",
        "一次回测不能证明策略有效，至少要换时间段、换品种、换参数复核。",
    ]

    lines = [
        "黄金量化策略最终复盘",
        "=" * 52,
        f"回测区间：{metrics['period']}",
        f"策略年化：{metrics['annual_return']:.2%}",
        f"基准收益：{metrics['benchmark_return']:.2%}",
        f"最大回撤：{metrics['max_drawdown']:.2%}",
        f"夏普比率：{metrics['sharpe']:.2f}",
        f"交易次数：{len(trades)}，胜率：{win_rate:.2%}，盈亏比：{payoff:.2f}",
        "",
        "一、这份成绩单说明了什么",
    ]
    lines += [f"  - {item}" for item in findings] if findings else ["  - 本次样本中没有出现明显的胜率陷阱，但仍需扩大样本复核。"]
    lines += ["", "二、可以继续改进的方向"]
    lines += [
        "  - 加入美元指数、实际利率、地缘风险等真正的宏观因子。",
        "  - 用波动率目标控制仓位，在高波动阶段主动降杠杆。",
        "  - 增加趋势过滤，只在中期趋势明确时接受模型信号。",
        "  - 对止损、止盈和最大持仓时间做参数敏感性分析。",
        "  - 用多个品种和多个时间段做样本外验证，而不是只盯一段行情。",
        "",
        "三、这门课真正要记住的",
    ]
    lines += [f"  {index}. {item}" for index, item in enumerate(lessons, 1)]
    lines += [
        "",
        "回测不好看不是失败，它帮你用很低的成本排除了一个不稳健的想法。",
        "量化研究的目标不是找到一个永远赚钱的模型，而是建立一套可复现、可证伪、可迭代的流程。",
        "本课程使用示例数据演示流程，不构成任何投资建议。",
    ]
    report = "\n".join(lines)
    (OUTPUT_DIR / "最终复盘.txt").write_text(report, encoding="utf-8")
    print(report)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    axes[0].bar(["策略年化", "买入持有"], [metrics["annual_return"] * 100, metrics["benchmark_return"] * 100], color=[GOLD, NAVY])
    axes[0].axhline(0, color="#2C3E50", linewidth=0.8)
    axes[0].set_ylabel("%")
    axes[0].set_title("收益对比", loc="left", color=NAVY)
    axes[1].bar(["胜率", "盈亏比"], [win_rate, payoff], color=[GREEN, RED])
    axes[1].axhline(0.5, color=NAVY, linestyle="--", linewidth=0.8)
    axes[1].set_title("胜率与盈亏比", loc="left", color=NAVY)
    for ax in axes:
        ax.grid(axis="y", alpha=0.2)
    fig.suptitle("黄金量化策略复盘", fontsize=14, fontweight="bold", color=NAVY)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "复盘对比.png")
    plt.close(fig)
    print(f"\n复盘已保存：{OUTPUT_DIR / '最终复盘.txt'}")


if __name__ == "__main__":
    main()
