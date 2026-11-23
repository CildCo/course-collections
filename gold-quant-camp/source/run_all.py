# 一键运行全部课程示例
# 运行：python run_all.py

import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

LESSONS = [
    ("第1课 金价速览与数据初识", "lesson01_gold_snapshot/main.py"),
    ("第2课 量化闭环：从数据到策略", "lesson02_workflow/main.py"),
    ("第3课 数据采集与宏观因子", "lesson03_data_pipeline/main.py"),
    ("第4课 EDA：看懂黄金数据", "lesson04_eda/main.py"),
    ("第5课 特征工程与三分类目标", "lesson05_features/main.py"),
    ("第6课 防泄露的时间序列模型", "lesson06_model/main.py"),
    ("第7课 回测：信号变成资金曲线", "lesson07_backtest/main.py"),
    ("第8课 自动生成策略报告", "lesson08_report/main.py"),
    ("第9课 最终复盘：胜率与基准", "lesson09_review/main.py"),
]


def main() -> None:
    print("=" * 60, flush=True)
    print("Python 量化实战：机器学习赋能黄金期货交易策略", flush=True)
    print("=" * 60, flush=True)

    started = time.perf_counter()
    for title, script in LESSONS:
        print("\n" + "=" * 60, flush=True)
        print(f"开始 {title}", flush=True)
        print("=" * 60, flush=True)
        completed = subprocess.run(
            [sys.executable, str(BASE_DIR / script)],
            cwd=str(BASE_DIR),
        )
        if completed.returncode != 0:
            print(f"\n{title} 运行失败，退出码 {completed.returncode}", flush=True)
            raise SystemExit(completed.returncode)

    elapsed = time.perf_counter() - started
    print("\n" + "=" * 60, flush=True)
    print(f"全部课程运行完成，用时 {elapsed:.1f} 秒", flush=True)
    print(f"图片和报告在：{BASE_DIR / 'output'}", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    main()
