# 一键运行全部课程示例
# 运行：python run_all.py

import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

LESSONS = [
    ("第1课 基础语法", "lesson01_intro/main.py"),
    ("第2课 列表与字典", "lesson02_data_structures/main.py"),
    ("第3课 循环/函数/类", "lesson03_functions_classes/main.py"),
    ("第4课 Excel 基础", "lesson04_excel_basics/main.py"),
    ("第5课 Excel 报表", "lesson05_excel_report/main.py"),
    ("第6课 Word 自动化", "lesson06_word_automation/main.py"),
    ("第7课 文件整理", "lesson07_file_organizer/main.py"),
    ("第8课 PDF 工具", "lesson08_pdf_toolkit/main.py"),
    ("第9课 定时任务", "lesson09_scheduled_task/daily_report.py"),
]


def main():
    for title, script in LESSONS:
        print("\n" + "=" * 60)
        print(title)
        print("=" * 60)
        result = subprocess.run(
            [sys.executable, str(BASE_DIR / script)],
            cwd=BASE_DIR,
        )
        if result.returncode != 0:
            print(f"{title} 运行失败，退出码：{result.returncode}")
            raise SystemExit(result.returncode)

    print("\n全部课程示例运行完成。")


if __name__ == "__main__":
    main()
