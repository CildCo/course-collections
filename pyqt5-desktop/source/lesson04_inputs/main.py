"""第 4 课：输入框、下拉框、勾选框等常用控件。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from common import create_app, finish, page_header


class InputWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("常用输入控件")
        self.resize(960, 640)
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(34, 28, 34, 28)
        root.setSpacing(16)
        root.addWidget(page_header("把用户输入收进来", "QLineEdit · QComboBox · QCheckBox · QRadioButton · QSpinBox · QSlider · QTextEdit"))

        grid = QGridLayout()
        grid.setSpacing(18)

        form_card = QFrame()
        form_card.setObjectName("Card")
        form = QGridLayout(form_card)
        form.setContentsMargins(24, 20, 24, 20)
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(12)

        self.name = QLineEdit()
        self.name.setPlaceholderText("请输入客户名称")
        self.name.setText("星河科技")
        self.category = QComboBox()
        self.category.addItems(["企业版", "专业版", "基础版"])
        self.vip = QCheckBox("标记为重点客户")
        self.vip.setChecked(True)
        self.plan_a = QRadioButton("按年付费")
        self.plan_b = QRadioButton("按月付费")
        self.plan_a.setChecked(True)
        self.seats = QSpinBox()
        self.seats.setRange(1, 500)
        self.seats.setValue(25)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(68)
        self.note = QTextEdit()
        self.note.setPlaceholderText("备注信息")
        self.note.setPlainText("需要在本周五前完成部署。")
        self.note.setMinimumHeight(90)

        rows = [
            ("客户名称", self.name),
            ("套餐", self.category),
            ("购买人数", self.seats),
            ("满意度", self.slider),
        ]
        for row, (label, widget) in enumerate(rows):
            form.addWidget(QLabel(label), row, 0)
            form.addWidget(widget, row, 1)
        plan_row = QWidget()
        plan_layout = QHBoxLayout(plan_row)
        plan_layout.setContentsMargins(0, 0, 0, 0)
        plan_layout.addWidget(self.plan_a)
        plan_layout.addWidget(self.plan_b)
        plan_layout.addStretch()
        form.addWidget(QLabel("付费方式"), 4, 0)
        form.addWidget(plan_row, 4, 1)
        form.addWidget(self.vip, 5, 1)
        form.addWidget(QLabel("备注"), 6, 0)
        form.addWidget(self.note, 6, 1)
        grid.addWidget(form_card, 0, 0, 2, 2)

        preview_card = QFrame()
        preview_card.setObjectName("Card")
        preview = QVBoxLayout(preview_card)
        preview.setContentsMargins(22, 20, 22, 20)
        preview.setSpacing(10)
        title = QLabel("实时预览")
        title.setObjectName("SectionTitle")
        self.preview = QLabel()
        self.preview.setWordWrap(True)
        self.preview.setObjectName("Subtitle")
        preview.addWidget(title)
        preview.addWidget(self.preview)
        preview.addStretch()
        grid.addWidget(preview_card, 0, 2)

        summary_card = QFrame()
        summary_card.setObjectName("Card")
        summary = QVBoxLayout(summary_card)
        summary.setContentsMargins(22, 20, 22, 20)
        summary_title = QLabel("控件要点")
        summary_title.setObjectName("SectionTitle")
        summary.addWidget(summary_title)
        for text in (
            "QLineEdit：单行文本，可设占位和密码模式",
            "QComboBox：省空间的单选下拉",
            "QCheckBox：可以多选",
            "QRadioButton：一组里只能选一个",
            "QSpinBox / QSlider：数字输入和拖动",
        ):
            label = QLabel("•  " + text)
            label.setObjectName("Subtitle")
            summary.addWidget(label)
        summary.addStretch()
        grid.addWidget(summary_card, 1, 2)
        grid.setColumnStretch(0, 3)
        grid.setColumnStretch(1, 2)
        grid.setColumnStretch(2, 2)
        root.addLayout(grid)
        root.addStretch()
        self.setCentralWidget(central)

        self.name.textChanged.connect(lambda *_: self.refresh())
        self.category.currentTextChanged.connect(lambda *_: self.refresh())
        self.vip.stateChanged.connect(lambda *_: self.refresh())
        self.plan_a.toggled.connect(lambda *_: self.refresh())
        self.seats.valueChanged.connect(lambda *_: self.refresh())
        self.slider.valueChanged.connect(lambda *_: self.refresh())
        self.note.textChanged.connect(lambda: self.refresh())
        self.refresh()

    def refresh(self):
        plan = "按年付费" if self.plan_a.isChecked() else "按月付费"
        vip = "重点客户" if self.vip.isChecked() else "普通客户"
        self.preview.setText(
            f"{self.name.text() or '未命名客户'}\n"
            f"套餐：{self.category.currentText()} · {self.seats.value()} 人\n"
            f"付费方式：{plan} · {vip}\n"
            f"满意度：{self.slider.value()} 分\n"
            f"备注：{self.note.toPlainText() or '无'}"
        )


def main():
    app = create_app()
    finish(app, InputWindow(), "04_输入控件")


if __name__ == "__main__":
    main()
