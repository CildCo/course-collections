"""第 1 课：第一个 PyQt5 窗口。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget

from common import card, create_app, finish, page_header


class FirstWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("我的第一个 PyQt5 窗口")
        self.resize(880, 560)
        self.count = 0

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(34, 28, 34, 28)
        layout.setSpacing(18)
        layout.addWidget(page_header("你好，桌面应用", "8 天从零做一个专业 PyQt5 应用 · 第 1 天"))

        metrics = QHBoxLayout()
        metrics.setSpacing(14)
        metrics.addWidget(card("窗口宽度", "880 px", "可拖动缩放"))
        metrics.addWidget(card("窗口高度", "560 px", "布局会自动适配"))
        metrics.addWidget(card("代码行数", "约 40 行", "第一个可运行界面"))
        layout.addLayout(metrics)

        panel = QWidget()
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 10, 0, 0)
        title = QLabel("点击按钮，看看信号与槽的最简单用法")
        title.setObjectName("SectionTitle")
        self.result = QLabel("还没有点击")
        self.result.setObjectName("Subtitle")
        button = QPushButton("点我一下")
        button.setFixedWidth(150)
        button.clicked.connect(self.on_click)
        panel_layout.addWidget(title)
        panel_layout.addWidget(self.result)
        panel_layout.addWidget(button, alignment=Qt.AlignLeft)
        layout.addWidget(panel)
        layout.addStretch()
        self.setCentralWidget(central)

    def on_click(self):
        self.count += 1
        self.result.setText(f"按钮已经被点击 {self.count} 次，信号成功连接到了槽函数。")


def main():
    app = create_app()
    finish(app, FirstWindow(), "01_第一个窗口")


if __name__ == "__main__":
    main()
