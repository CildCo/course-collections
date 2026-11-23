# 一键运行全部课程示例
# 运行：python run_all.py

import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

LESSONS = [
    ("第1课 第一张专业图表", "lesson01_first_chart/main.py"),
    ("第2课 Excel 高管图表", "lesson02_excel_chart/main.py"),
    ("第3课 Seaborn 统计图", "lesson03_seaborn/main.py"),
    ("第4课 Pyecharts 交互报表", "lesson04_pyecharts/main.py"),
    ("第5课 双轴图与子图布局", "lesson05_dual_axis/main.py"),
    ("第6课 图表插入 Excel 和 PPT", "lesson06_excel_ppt/main.py"),
    ("第7课 可视化报告实战", "lesson07_visual_report/main.py"),
    ("第8课 避坑与安全机制", "lesson08_safety/main.py"),
]


def main():
    print("=" * 60, flush=True)
    print("Python 办公自动化进阶：职场可视化实战营", flush=True)
    print("=" * 60, flush=True)

    started = time.perf_counter()
    for title, script in LESSONS:
        print("\n" + "=" * 60, flush=True)
        print(title, flush=True)
        print("=" * 60, flush=True)
        sys.stdout.flush()
        result = subprocess.run(
            [sys.executable, str(BASE_DIR / script)],
            cwd=str(BASE_DIR),
        )
        if result.returncode != 0:
            print(f"\n{title} 运行失败，退出码：{result.returncode}", flush=True)
            raise SystemExit(result.returncode)

    elapsed = time.perf_counter() - started
    print("\n" + "=" * 60, flush=True)
    print(f"8 节课全部运行完成，总用时 {elapsed:.1f} 秒。", flush=True)
    print("每课的输出文件都在各自的 output 目录中。", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    main()
