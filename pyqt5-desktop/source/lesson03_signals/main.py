"""第 3 课：信号与槽，用灯开关理解。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget

from common import create_app, finish, page_header


class LampWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("信号与槽")
        self.resize(860, 560)
        self.is_on = False

        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(34, 28, 34, 28)
        root.setSpacing(20)
        root.addWidget(page_header("信号 → 连线 → 槽", "按钮不是自己会亮灯，它只是发出了 clicked 信号"))

        body = QHBoxLayout()
        body.setSpacing(28)

        self.lamp = QLabel("关")
        self.lamp.setFixedSize(190, 190)
        self.lamp.setAlignment(Qt.AlignCenter)
        self.lamp.setStyleSheet(
            "background:#E5EAF0;color:#7F8C8D;border-radius:95px;font-size:28px;font-weight:700;"
        )
        body.addWidget(self.lamp, alignment=Qt.AlignCenter)

        panel = QFrame()
        panel.setObjectName("Card")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(26, 24, 26, 24)
        panel_layout.setSpacing(12)
        self.status = QLabel("灯是关着的")
        self.status.setObjectName("SectionTitle")
        hint = QLabel("connect() 把 button.clicked 信号和 switch_lamp() 槽函数连起来。")
        hint.setObjectName("Subtitle")
        hint.setWordWrap(True)
        self.switch_button = QPushButton("打开灯")
        self.switch_button.setFixedWidth(150)
        self.switch_button.clicked.connect(self.switch_lamp)
        panel_layout.addWidget(self.status)
        panel_layout.addWidget(hint)
        panel_layout.addSpacing(8)
        panel_layout.addWidget(self.switch_button)
        panel_layout.addStretch()
        body.addWidget(panel, 1)
        root.addLayout(body)
        self.setCentralWidget(central)

    def switch_lamp(self):
        self.is_on = not self.is_on
        if self.is_on:
            self.lamp.setText("开")
            self.lamp.setStyleSheet(
                "background:#FFF2B2;color:#8A6D00;border:6px solid #F1C40F;border-radius:95px;"
                "font-size:28px;font-weight:700;"
            )
            self.status.setText("灯亮了，槽函数执行成功")
            self.switch_button.setText("关闭灯")
        else:
            self.lamp.setText("关")
            self.lamp.setStyleSheet(
                "background:#E5EAF0;color:#7F8C8D;border-radius:95px;font-size:28px;font-weight:700;"
            )
            self.status.setText("灯关掉了，信号又一次触发了槽")
            self.switch_button.setText("打开灯")


def main():
    app = create_app()
    window = LampWindow()
    window.switch_lamp()  # 演示打开状态
    finish(app, window, "03_信号与槽")


if __name__ == "__main__":
    main()
