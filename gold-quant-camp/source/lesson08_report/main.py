"""第 8 课：自动生成可交付的策略报告。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import pandas as pd

from common import GOLD, GREEN, NAVY, OUTPUT_DIR, PROCESSED_DIR, RED, load_json, setup_plot


def money(value: float) -> str:
    return f"{value:,.0f} 元"


def main() -> None:
    setup_plot()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    metrics = load_json(PROCESSED_DIR / "metrics.json")
    trades = pd.read_csv(PROCESSED_DIR / "trades.csv")
    if trades.empty:
        raise SystemExit("没有交易记录，请先运行第 7 课")

    wins = trades[trades["pnl"] > 0]
    losses = trades[trades["pnl"] < 0]
    win_rate = len(wins) / len(trades)
    profit_factor = wins["pnl"].sum() / abs(losses["pnl"].sum()) if len(losses) and losses["pnl"].sum() != 0 else 0
    payoff = wins["pnl"].mean() / abs(losses["pnl"].mean()) if len(wins) and len(losses) else 0
    best = trades.nlargest(5, "pnl")
    worst = trades.nsmallest(5, "pnl")

    lines = [
        "黄金期货量化策略回测报告",
        "=" * 52,
        f"回测区间：{metrics['period']}",
        f"初始资金：{money(metrics['initial_capital'])}",
        f"最终资金：{money(metrics['final_equity'])}",
        "",
        "一、收益与风险",
        f"  累计收益：{metrics['total_return']:.2%}",
        f"  年化收益：{metrics['annual_return']:.2%}",
        f"  年化波动：{metrics['annual_volatility']:.2%}",
        f"  夏普比率：{metrics['sharpe']:.2f}（无风险利率 2%）",
        f"  最大回撤：{metrics['max_drawdown']:.2%}",
        f"  买入持有基准：{metrics['benchmark_return']:.2%}",
        "",
        "二、交易统计",
        f"  交易次数：{len(trades)}",
        f"  胜率：{win_rate:.2%}",
        f"  盈亏比：{payoff:.2f}",
        f"  盈利因子：{profit_factor:.2f}",
        f"  平均盈利：{money(wins['pnl'].mean()) if len(wins) else '0 元'}",
        f"  平均亏损：{money(losses['pnl'].mean()) if len(losses) else '0 元'}",
        f"  最大连续亏损：{metrics['max_consecutive_losses']} 次",
        f"  最大连续亏损金额：{money(metrics['max_consecutive_loss_amount'])}",
        f"  持仓时间占比：{metrics['exposure']:.1%}",
        "",
        "三、最差 5 笔交易",
    ]
    for _, row in worst.iterrows():
        lines.append(
            f"  {str(row['entry_date'])[:10]} → {str(row['exit_date'])[:10]}  "
            f"{row['direction']}  {money(row['pnl'])}  ({row['return']:.2%})"
        )
    lines += ["", "四、最好 5 笔交易"]
    for _, row in best.iterrows():
        lines.append(
            f"  {str(row['entry_date'])[:10]} → {str(row['exit_date'])[:10]}  "
            f"{row['direction']}  {money(row['pnl'])}  ({row['return']:.2%})"
        )

    verdict = []
    if metrics["annual_return"] < metrics["benchmark_return"]:
        verdict.append("策略跑输买入持有基准，频繁换仓没有带来超额收益。")
    if win_rate > 0.5 and payoff < 1.1:
        verdict.append("胜率不低，但盈亏比接近 1，手续费和滑点会吃掉利润。")
    if metrics["max_drawdown"] < -0.15:
        verdict.append("最大回撤超过 15%，实盘前必须降低仓位或增加止损。")
    if metrics["max_consecutive_losses"] >= 4:
        verdict.append("连续亏损次数偏多，要检查震荡行情中的假信号。")
    if not verdict:
        verdict.append("策略表现相对平稳，但仍需用更长的样本外数据复核。")

    lines += ["", "五、结论", *[f"  - {item}" for item in verdict]]
    lines += [
        "",
        "说明：以上结果为历史样本回测，不构成投资建议。",
        "真实交易还会受到流动性、涨跌停、保证金调整和极端跳空影响。",
    ]
    report = "\n".join(lines)
    (OUTPUT_DIR / "黄金期货量化策略回测报告.txt").write_text(report, encoding="utf-8")
    print(report)

    # 绩效卡片，方便放进复盘材料。
    fig = plt.figure(figsize=(12, 5.2))
    fig.patch.set_facecolor("#F7F4EA")
    cards = [
        ("年化收益", f"{metrics['annual_return']:.2%}", GOLD),
        ("最大回撤", f"{metrics['max_drawdown']:.2%}", RED),
        ("夏普比率", f"{metrics['sharpe']:.2f}", NAVY),
        ("胜率", f"{win_rate:.2%}", GREEN),
        ("盈亏比", f"{payoff:.2f}", "#8E6C88"),
        ("基准收益", f"{metrics['benchmark_return']:.2%}", "#7F8C8D"),
    ]
    for index, (label, value, color) in enumerate(cards):
        ax = fig.add_axes([0.04 + index * 0.157, 0.22, 0.135, 0.56])
        ax.set_facecolor("white")
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.text(0.5, 0.62, value, ha="center", va="center", fontsize=19, color=color, fontweight="bold")
        ax.text(0.5, 0.25, label, ha="center", va="center", fontsize=10, color="#5D6D7E")
    fig.suptitle("黄金量化策略绩效卡", fontsize=17, fontweight="bold", color=NAVY, y=0.9)
    fig.savefig(OUTPUT_DIR / "绩效卡片.png")
    plt.close(fig)
    print(f"\n报告已保存：{OUTPUT_DIR / '黄金期货量化策略回测报告.txt'}")


if __name__ == "__main__":
    main()
