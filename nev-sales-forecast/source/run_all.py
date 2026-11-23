# 一键运行全部课程示例
# 运行：python run_all.py

import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

LESSONS = [
    ("第1课 数据基石：采集、清洗与校验", "lesson01_data_pipeline/main.py"),
    ("第2课 市场洞察：2017-2026 趋势复盘", "lesson02_market_dashboard/main.py"),
    ("第3课 特征工程：时间、滞后与滚动", "lesson03_features/main.py"),
    ("第4课 预测引擎：季节趋势 + 梯度提升", "lesson04_forecast/main.py"),
    ("第5课 工程落地：Flask + ECharts 大屏", "lesson05_web_dashboard/main.py"),
    ("第6课 智能决策：2026 年情景与节奏", "lesson06_decision/main.py"),
]


def main() -> None:
    print("=" * 60, flush=True)
    print("Python 驱动新能源车销售预测：从数据建模到智能决策", flush=True)
    print("=" * 60, flush=True)

    started = time.perf_counter()
    for title, script in LESSONS:
        print("\n" + "=" * 60, flush=True)
        print(f"开始 {title}", flush=True)
        print("=" * 60, flush=True)
        completed = subprocess.run([sys.executable, str(BASE_DIR / script)], cwd=str(BASE_DIR))
        if completed.returncode != 0:
            print(f"\n{title} 运行失败，退出码 {completed.returncode}", flush=True)
            raise SystemExit(completed.returncode)

    elapsed = time.perf_counter() - started
    print("\n" + "=" * 60, flush=True)
    print(f"全部课程运行完成，用时 {elapsed:.1f} 秒", flush=True)
    print(f"图片和报告在：{BASE_DIR / 'output'}", flush=True)
    print("大屏：python dashboard_app.py，然后打开 http://127.0.0.1:5000", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    main()
