# 一键运行全部课程示例（无界面模式，自动截图）
# 运行：python run_all.py

import os
import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

LESSONS = [
    ("第1课 第一个窗口", "lesson01_first_window/main.py"),
    ("第2课 控件和布局", "lesson02_layouts/main.py"),
    ("第3课 信号与槽", "lesson03_signals/main.py"),
    ("第4课 常用输入控件", "lesson04_inputs/main.py"),
    ("第5课 弹窗与对话框", "lesson05_dialogs/main.py"),
    ("第6课 菜单栏、工具栏、状态栏", "lesson06_mainwindow/main.py"),
    ("第7课 Tab、表格与树", "lesson07_tabs_tables/main.py"),
    ("第8课 数据仪表盘", "lesson08_dashboard/main.py"),
]


def main() -> None:
    print("=" * 60, flush=True)
    print("PyQt5 从入门到实战：8 天打造专业桌面应用", flush=True)
    print("=" * 60, flush=True)
    env = os.environ.copy()
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    env["PYTHONIOENCODING"] = "utf-8"
    started = time.perf_counter()
    for title, script in LESSONS:
        print("\n" + "=" * 60, flush=True)
        print(f"开始 {title}", flush=True)
        print("=" * 60, flush=True)
        completed = subprocess.run(
            [sys.executable, str(BASE_DIR / script), "--auto"],
            cwd=str(BASE_DIR),
            env=env,
        )
        if completed.returncode != 0:
            print(f"\n{title} 运行失败，退出码 {completed.returncode}", flush=True)
            raise SystemExit(completed.returncode)
    print("\n" + "=" * 60, flush=True)
    print(f"全部课程运行完成，用时 {time.perf_counter() - started:.1f} 秒", flush=True)
    print(f"截图在：{BASE_DIR / 'output'}", flush=True)
    print("单独运行某一课且不带 --auto，会正常显示桌面窗口。", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    main()
