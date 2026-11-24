"""第 2 课：控件和布局。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt5.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from common import create_app, finish, page_header


class LayoutWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("布局管理器")
        self.resize(920, 600)
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(34, 28, 34, 28)
        root.setSpacing(18)
        root.addWidget(page_header("布局，让界面自己呼吸", "QVBoxLayout · QHBoxLayout · QGridLayout · QFormLayout"))

        grid = QGridLayout()
        grid.setSpacing(16)

        form_card = QFrame()
        form_card.setObjectName("Card")
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(22, 20, 22, 20)
        form_layout.setSpacing(14)
        title = QLabel("新建项目")
        title.setObjectName("SectionTitle")
        form_layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)
        form.addRow("项目名称", QLineEdit("数据看板"))
        form.addRow("项目类型", QComboBox())
        form.itemAt(1, QFormLayout.FieldRole).widget().addItems(["桌面应用", "数据工具", "自动化脚本"])
        form.addRow("负责人", QLineEdit("小李"))
        form.addRow("目标平台", QLineEdit("Windows / macOS"))
        form_layout.addLayout(form)
        form_layout.addStretch()

        actions = QHBoxLayout()
        actions.addStretch()
        cancel = QPushButton("取消")
        cancel.setObjectName("Ghost")
        save = QPushButton("创建项目")
        actions.addWidget(cancel)
        actions.addWidget(save)
        form_layout.addLayout(actions)

        grid.addWidget(form_card, 0, 0, 2, 2)

        info_card = QFrame()
        info_card.setObjectName("Card")
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(20, 18, 20, 18)
        info_layout.setSpacing(10)
        info_title = QLabel("布局规则")
        info_title.setObjectName("SectionTitle")
        info_layout.addWidget(info_title)
        for text in (
            "QVBoxLayout：从上到下排列",
            "QHBoxLayout：从左到右排列",
            "QGridLayout：按行列对齐",
            "QFormLayout：标签 + 输入框",
        ):
            label = QLabel("•  " + text)
            label.setObjectName("Subtitle")
            info_layout.addWidget(label)
        info_layout.addStretch()
        grid.addWidget(info_card, 0, 2)

        preview = QFrame()
        preview.setObjectName("Card")
        preview_layout = QVBoxLayout(preview)
        preview_layout.setContentsMargins(20, 18, 20, 18)
        preview_title = QLabel("窗口缩放时，卡片和表单会自动调整")
        preview_title.setObjectName("SectionTitle")
        preview_hint = QLabel("不要再用 setGeometry 写死坐标。用布局管理器，控件会跟着窗口一起伸缩。")
        preview_hint.setObjectName("Subtitle")
        preview_hint.setWordWrap(True)
        preview_layout.addWidget(preview_title)
        preview_layout.addWidget(preview_hint)
        preview_layout.addStretch()
        grid.addWidget(preview, 1, 2)

        grid.setColumnStretch(0, 2)
        grid.setColumnStretch(1, 2)
        grid.setColumnStretch(2, 3)
        root.addLayout(grid)
        root.addStretch()
        self.setCentralWidget(central)


def main():
    app = create_app()
    finish(app, LayoutWindow(), "02_控件与布局")


if __name__ == "__main__":
    main()
