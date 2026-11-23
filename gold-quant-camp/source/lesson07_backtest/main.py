"""第 7 课：把预测信号变成资金曲线。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle

from common import (
    GOLD,
    GRAY,
    GREEN,
    NAVY,
    OUTPUT_DIR,
    PROCESSED_DIR,
    RED,
    ensure_data,
    save_json,
    setup_plot,
)

INITIAL_CAPITAL = 1_000_000.0
MARGIN_RATIO = 0.12
COMMISSION_RATE = 0.0002
SLIPPAGE_RATE = 0.0001


def max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    drawdown = equity / peak - 1
    return float(drawdown.min())


def main() -> None:
    setup_plot()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    raw = ensure_data()
    predictions = pd.read_csv(PROCESSED_DIR / "predictions.csv", index_col=0, parse_dates=True)
    data = raw.join(predictions[["prob_down", "prob_flat", "prob_up", "pred_class"]], how="inner").dropna()
    data = data.sort_index()
    if len(data) < 60:
        raise SystemExit("预测样本不足，请先运行第 6 课")

    # T 日收盘后得到信号，T+1 日开盘执行。
    data["signal"] = data["pred_class"].shift(1).fillna(1).astype(int)
    data["position"] = data["signal"].map({2: 1, 0: -1, 1: 0}).astype(int)
    data["confidence"] = data[["prob_down", "prob_up"]].max(axis=1)

    equity = INITIAL_CAPITAL
    previous_position = 0
    previous_close = float(data["close"].iloc[0])
    equity_rows = []
    trades = []
    open_trade = None

    for index, row in data.iterrows():
        open_price = float(row["open"])
        close_price = float(row["close"])
        position = int(row["position"])
        confidence = float(row["confidence"])

        overnight = open_price / previous_close - 1
        intraday = close_price / open_price - 1
        pnl = previous_position * equity * overnight + position * equity * intraday

        turnover = abs(position - previous_position)
        cost = turnover * equity * (COMMISSION_RATE + SLIPPAGE_RATE)
        equity = equity + pnl - cost

        if position != previous_position:
            if open_trade is not None:
                direction, entry_price, entry_equity, entry_date = open_trade
                raw_return = direction * (open_price / entry_price - 1)
                trade_pnl = raw_return * entry_equity
                trades.append(
                    {
                        "entry_date": entry_date,
                        "exit_date": index,
                        "direction": "多" if direction > 0 else "空",
                        "entry_price": entry_price,
                        "exit_price": open_price,
                        "return": raw_return,
                        "pnl": trade_pnl,
                    }
                )
                open_trade = None
            if position != 0:
                risk_fraction = 0.10 + 0.10 * np.clip((confidence - 0.5) / 0.3, 0, 1)
                notional = min(equity * risk_fraction / MARGIN_RATIO, equity * 1.8)
                open_trade = (position, open_price, notional, index)

        equity_rows.append(
            {
                "date": index,
                "equity": equity,
                "position": position,
                "close": close_price,
            }
        )
        previous_position = position
        previous_close = close_price

    if open_trade is not None:
        direction, entry_price, notional, entry_date = open_trade
        exit_price = float(data["close"].iloc[-1])
        raw_return = direction * (exit_price / entry_price - 1)
        trades.append(
            {
                "entry_date": entry_date,
                "exit_date": data.index[-1],
                "direction": "多" if direction > 0 else "空",
                "entry_price": entry_price,
                "exit_price": exit_price,
                "return": raw_return,
                "pnl": raw_return * notional,
            }
        )

    curve = pd.DataFrame(equity_rows).set_index("date")
    curve["benchmark"] = INITIAL_CAPITAL * curve["close"] / data["close"].iloc[0]
    curve["strategy_return"] = curve["equity"].pct_change()
    curve["drawdown"] = curve["equity"] / curve["equity"].cummax() - 1

    trade_frame = pd.DataFrame(trades)
    trade_frame.to_csv(PROCESSED_DIR / "trades.csv", index=False, encoding="utf-8-sig")
    curve.to_csv(PROCESSED_DIR / "equity_curve.csv", encoding="utf-8-sig")

    years = max((curve.index[-1] - curve.index[0]).days / 365.25, 1 / 252)
    total_return = curve["equity"].iloc[-1] / INITIAL_CAPITAL - 1
    annual_return = (1 + total_return) ** (1 / years) - 1
    annual_vol = curve["strategy_return"].std() * np.sqrt(252)
    sharpe = (annual_return - 0.02) / annual_vol if annual_vol > 0 else 0.0
    benchmark_return = curve["benchmark"].iloc[-1] / INITIAL_CAPITAL - 1
    drawdown = max_drawdown(curve["equity"])

    wins = trade_frame[trade_frame["pnl"] > 0]["pnl"] if not trade_frame.empty else pd.Series(dtype=float)
    losses = trade_frame[trade_frame["pnl"] < 0]["pnl"] if not trade_frame.empty else pd.Series(dtype=float)
    win_rate = len(wins) / len(trade_frame) if len(trade_frame) else 0.0
    profit_factor = float(wins.sum() / abs(losses.sum())) if len(losses) and losses.sum() != 0 else 0.0
    consecutive = 0
    max_consecutive = 0
    consecutive_amount = 0.0
    max_consecutive_amount = 0.0
    for value in trade_frame["pnl"] if not trade_frame.empty else []:
        if value < 0:
            consecutive += 1
            consecutive_amount += value
            max_consecutive = max(max_consecutive, consecutive)
            max_consecutive_amount = min(max_consecutive_amount, consecutive_amount)
        else:
            consecutive = 0
            consecutive_amount = 0.0

    metrics = {
        "period": f"{curve.index[0].date()} 至 {curve.index[-1].date()}",
        "initial_capital": INITIAL_CAPITAL,
        "final_equity": float(curve["equity"].iloc[-1]),
        "total_return": float(total_return),
        "annual_return": float(annual_return),
        "annual_volatility": float(annual_vol),
        "sharpe": float(sharpe),
        "max_drawdown": float(drawdown),
        "benchmark_return": float(benchmark_return),
        "trades": int(len(trade_frame)),
        "win_rate": float(win_rate),
        "profit_factor": float(profit_factor),
        "avg_win": float(wins.mean()) if len(wins) else 0.0,
        "avg_loss": float(losses.mean()) if len(losses) else 0.0,
        "payoff_ratio": float(wins.mean() / abs(losses.mean())) if len(wins) and len(losses) else 0.0,
        "max_consecutive_losses": int(max_consecutive),
        "max_consecutive_loss_amount": float(max_consecutive_amount),
        "exposure": float((curve["position"] != 0).mean()),
    }
    save_json(PROCESSED_DIR / "metrics.json", metrics)

    print(f"回测区间：{metrics['period']}")
    print(f"初始资金：{INITIAL_CAPITAL:,.0f}  最终资金：{metrics['final_equity']:,.0f}")
    print(f"总收益：{total_return:.2%}  年化：{annual_return:.2%}")
    print(f"基准收益（买入持有）：{benchmark_return:.2%}")
    print(f"最大回撤：{drawdown:.2%}  夏普：{sharpe:.2f}")
    print(f"交易次数：{len(trade_frame)}  胜率：{win_rate:.2%}  盈亏比：{metrics['payoff_ratio']:.2f}")

    # 总览图：资金曲线、回撤、价格信号、月度收益。
    monthly = curve["equity"].resample("ME").last().pct_change().dropna()
    fig, axes = plt.subplots(2, 2, figsize=(13, 8.2))
    axes[0, 0].plot(curve.index, curve["equity"] / INITIAL_CAPITAL, color=GOLD, linewidth=1.7, label="策略")
    axes[0, 0].plot(curve.index, curve["benchmark"] / INITIAL_CAPITAL, color=NAVY, linewidth=1.0, linestyle="--", label="买入持有")
    axes[0, 0].set_title("资金曲线", loc="left", fontsize=12, color=NAVY)
    axes[0, 0].legend(frameon=False, fontsize=8)
    axes[0, 0].grid(alpha=0.2)

    axes[0, 1].fill_between(curve.index, curve["drawdown"] * 100, 0, color=RED, alpha=0.35)
    axes[0, 1].plot(curve.index, curve["drawdown"] * 100, color=RED, linewidth=1.0)
    axes[0, 1].set_title("回撤（%）", loc="left", fontsize=12, color=NAVY)
    axes[0, 1].grid(alpha=0.2)

    view = curve.tail(220)
    axes[1, 0].plot(view.index, view["close"], color=GRAY, linewidth=1.1)
    longs = view[view["position"] == 1]
    shorts = view[view["position"] == -1]
    axes[1, 0].scatter(longs.index, longs["close"], marker="^", color=GREEN, s=18, label="多")
    axes[1, 0].scatter(shorts.index, shorts["close"], marker="v", color=RED, s=18, label="空")
    axes[1, 0].set_title("价格与持仓信号（局部）", loc="left", fontsize=12, color=NAVY)
    axes[1, 0].legend(frameon=False, fontsize=8)
    axes[1, 0].grid(alpha=0.2)

    axes[1, 1].bar(monthly.index, monthly.values * 100, width=18, color=[GREEN if v >= 0 else RED for v in monthly.values])
    axes[1, 1].axhline(0, color=NAVY, linewidth=0.8)
    axes[1, 1].set_title("月度收益（%）", loc="left", fontsize=12, color=NAVY)
    axes[1, 1].grid(axis="y", alpha=0.2)
    for ax in axes.flat:
        ax.tick_params(labelsize=8)
    fig.suptitle("黄金量化策略回测总览", fontsize=15, fontweight="bold", color=NAVY)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "策略总览.png")
    plt.close(fig)

    # K 线图：最近 180 个交易日，标注多空信号。
    kline = data.tail(180).copy()
    fig, ax = plt.subplots(figsize=(13, 5.8))
    for offset, (index, row) in enumerate(kline.iterrows()):
        color = RED if row["close"] >= row["open"] else GREEN
        ax.vlines(offset, row["low"], row["high"], color=color, linewidth=0.8)
        bottom = min(row["open"], row["close"])
        height = max(abs(row["close"] - row["open"]), 0.05)
        ax.add_patch(Rectangle((offset - 0.3, bottom), 0.6, height, facecolor=color, edgecolor=color, alpha=0.8))
    positions = kline["position"].to_numpy()
    ax.scatter(np.arange(len(kline))[positions == 1], kline["low"].to_numpy()[positions == 1] * 0.997, marker="^", color=GREEN, s=22)
    ax.scatter(np.arange(len(kline))[positions == -1], kline["high"].to_numpy()[positions == -1] * 1.003, marker="v", color=RED, s=22)
    tick_positions = np.arange(0, len(kline), max(1, len(kline) // 6))
    ax.set_xticks(tick_positions, [kline.index[i].strftime("%Y-%m") for i in tick_positions])
    ax.set_title("沪金主力 K 线与策略信号（最近 180 个交易日）", fontsize=14, fontweight="bold", color=NAVY)
    ax.set_ylabel("元/克")
    ax.grid(alpha=0.18)
    fig.savefig(OUTPUT_DIR / "K线信号.png")
    plt.close(fig)

    print(f"\n资金曲线：{PROCESSED_DIR / 'equity_curve.csv'}")
    print(f"交易记录：{PROCESSED_DIR / 'trades.csv'}")
    print(f"总览图：{OUTPUT_DIR / '策略总览.png'}")


if __name__ == "__main__":
    main()
