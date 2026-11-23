# 一键运行全部深度学习课程示例
# 运行：python run_all.py

import os
import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

LESSONS = [
    ("第1课 环境与张量", "lesson01_environment/main.py"),
    ("第2课 自动求导与线性回归", "lesson02_autograd/main.py"),
    ("第3课 softmax 手写数字", "lesson03_softmax/main.py"),
    ("第4课 多层感知机 MLP", "lesson04_mlp/main.py"),
    ("第5课 过拟合与正则化", "lesson05_overfitting/main.py"),
    ("第6课 CNN 卷积神经网络", "lesson06_cnn/main.py"),
    ("第7课 迁移学习", "lesson07_transfer/main.py"),
    ("第8课 RNN 序列预测", "lesson08_rnn/main.py"),
    ("第9课 LSTM 写诗", "lesson09_lstm/main.py"),
    ("第10课 Word2Vec 字向量", "lesson10_word2vec/main.py"),
    ("第11课 模型部署", "lesson11_deploy/main.py"),
]


def main() -> None:
    print("=" * 60, flush=True)
    print("Python 深度学习零基础实战：从环境搭建到模型部署", flush=True)
    print("=" * 60, flush=True)
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    started = time.perf_counter()
    for title, script in LESSONS:
        print("\n" + "=" * 60, flush=True)
        print(f"开始 {title}", flush=True)
        print("=" * 60, flush=True)
        completed = subprocess.run([sys.executable, str(BASE_DIR / script)], cwd=str(BASE_DIR), env=env)
        if completed.returncode != 0:
            print(f"\n{title} 运行失败，退出码 {completed.returncode}", flush=True)
            raise SystemExit(completed.returncode)
    print("\n" + "=" * 60, flush=True)
    print(f"全部课程运行完成，用时 {time.perf_counter() - started:.1f} 秒", flush=True)
    print(f"图片、模型和日志在：{BASE_DIR / 'output'}、{BASE_DIR / 'models'}", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    main()
