"""第 2 课：量化闭环——从数据到策略。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common import OUTPUT_DIR, add_features, ensure_data, setup_plot


def main() -> None:
    setup_plot()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = ensure_data()
    features = add_features(df)
    target_col = "Target_Class_5d"
    distribution = features[target_col].value_counts().sort_index()
    labels = {0: "大跌", 1: "震荡", 2: "大涨"}

    steps = [
        ("1. 数据采集", "把沪金、白银、铜、原油、豆粕对齐到同一张日线表"),
        ("2. 数据清洗", "处理缺失、非正价格和休市，统一时间轴"),
        ("3. 探索分析", "看趋势、波动、相关性和极端值"),
        ("4. 特征工程", "把盘感翻译成均线乖离、RSI、波动率和跨资产比率"),
        ("5. 目标定义", "用滚动波动率定义大涨、震荡、大跌三分类"),
        ("6. 模型训练", "按时间切分并留出空窗期，避免未来数据泄露"),
        ("7. 回测验证", "信号滞后一天，计入手续费、滑点和保证金"),
        ("8. 报告复盘", "把收益、回撤、胜率和盈亏比放在一起看"),
    ]

    lines = [
        "黄金量化研究闭环",
        "=" * 46,
        f"样本：{len(df)} 个交易日，{df.index.min().date()} 至 {df.index.max().date()}",
        f"字段：{len(df.columns)} 列",
        "",
    ]
    lines += [f"{name}：{detail}" for name, detail in steps]
    lines += [
        "",
        "三分类样本分布（未来 5 个交易日）：",
    ]
    for key, count in distribution.items():
        lines.append(f"  {labels.get(int(key), key)}：{int(count)} 条，{count / len(features) * 100:.1f}%")

    text = "\n".join(lines)
    (OUTPUT_DIR / "量化闭环说明.txt").write_text(text, encoding="utf-8")
    print(text)
    print("\n提示：先跑通闭环，再谈参数。没有回测和风控的预测，只是数字游戏。")


if __name__ == "__main__":
    main()
