# 一键运行全部 Playwright 课程示例
# 运行：python run_all.py

import os
import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from common import ensure_server, stop_server

LESSONS = [
    ("第1课 第一个 Playwright 脚本", "lesson01_first_script/main.py"),
    ("第2课 定位、输入、点击和读取", "lesson02_locators/main.py"),
    ("第3课 八种定位方式", "lesson03_eight_locators/main.py"),
    ("第4课 网页表单自动填写", "lesson04_form_fill/main.py"),
    ("第5课 弹窗处理", "lesson05_dialogs/main.py"),
    ("第6课 智能等待", "lesson06_waiting/main.py"),
    ("第7课 多标签页与 iframe", "lesson07_tabs_iframe/main.py"),
    ("第8课 电影数据抓取与 CSV", "lesson08_movie_scrape/main.py"),
    ("第9课 请求拦截与 CI 稳定性", "lesson09_network/main.py"),
]


def main() -> None:
    print("=" * 60, flush=True)
    print("Python 自动化测试：Playwright 从入门到精通", flush=True)
    print("=" * 60, flush=True)
    ensure_server()
    env = os.environ.copy()
    env["PLAYWRIGHT_HEADLESS"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    started = time.perf_counter()
    try:
        for title, script in LESSONS:
            print("\n" + "=" * 60, flush=True)
            print(f"开始 {title}", flush=True)
            print("=" * 60, flush=True)
            completed = subprocess.run(
                [sys.executable, str(BASE_DIR / script)],
                cwd=str(BASE_DIR),
                env=env,
            )
            if completed.returncode != 0:
                print(f"\n{title} 运行失败，退出码 {completed.returncode}", flush=True)
                raise SystemExit(completed.returncode)
    finally:
        stop_server()
    print("\n" + "=" * 60, flush=True)
    print(f"全部课程运行完成，用时 {time.perf_counter() - started:.1f} 秒", flush=True)
    print(f"截图和 CSV 在：{BASE_DIR / 'output'}、{BASE_DIR / 'data'}", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    main()
