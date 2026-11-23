# 一键运行全部课程示例
# 运行：python run_all.py

import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

LESSONS = [
    ("第1课 合并 36 份报表并清洗", "lesson01_merge_clean/main.py"),
    ("第2课 特征工程与销售可视化", "lesson02_features_visual/main.py"),
    ("第3课 线性回归预测下季度销量", "lesson03_linear_regression/main.py"),
    ("第4课 逻辑回归识别高价值客户", "lesson04_logistic_customer/main.py"),
    ("第5课 决策树与随机森林流失预警", "lesson05_churn_forest/main.py"),
    ("第6课 K-Means 客户分群", "lesson06_kmeans_segment/main.py"),
    ("第7课 孤立森林异常报销检测", "lesson07_isolation_forest/main.py"),
    ("第8课 模型持久化与重新加载", "lesson08_model_persistence/main.py"),
    ("第9课 预测结果自动回填 Excel", "lesson09_excel_report/main.py"),
]


def main() -> None:
    print("=" * 60, flush=True)
    print("Python 机器学习：让 Excel 拥有预测未来的大脑", flush=True)
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
    print("\n" + "=" * 60, flush=True)
    print(f"全部课程运行完成，用时 {time.perf_counter() - started:.1f} 秒", flush=True)
    print(f"图片和报表在：{BASE_DIR / 'output'}", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    main()
