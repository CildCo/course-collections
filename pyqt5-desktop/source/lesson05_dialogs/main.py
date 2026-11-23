"""第 5 课：消息框、输入框、文件选择和自定义对话框。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt5.QtWidgets import (
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from common import create_app, finish, page_header


class FeedbackDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("提交反馈")
        self.resize(420, 300)
        layout = QVBoxLayout(self)
        title = QLabel("告诉我们哪里可以做得更好")
        title.setObjectName("SectionTitle")
        form = QFormLayout()
        self.kind = QComboBox()
        self.kind.addItems(["功能建议", "使用问题", "数据错误"])
        self.content = QTextEdit()
        self.content.setPlaceholderText("请描述你遇到的问题")
        form.addRow("反馈类型", self.kind)
        form.addRow("反馈内容", self.content)
        layout.addWidget(title)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class DialogWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("弹窗示例")
        self.resize(920, 620)
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(34, 28, 34, 28)
        root.setSpacing(18)
        root.addWidget(page_header("别只会 alert", "不同场景用不同弹窗，用户才知道下一步做什么"))

        grid = QGridLayout()
        grid.setSpacing(14)
        items = [
            ("信息提示", "QMessageBox.information", self.info, "#16A085"),
            ("警告提示", "QMessageBox.warning", self.warning, "#D4AC0D"),
            ("错误提示", "QMessageBox.critical", self.error, "#C0392B"),
            ("确认操作", "QMessageBox.question", self.confirm, "#2E86C1"),
            ("文本输入", "QInputDialog.getText", self.ask_text, "#8E44AD"),
            ("选择文件", "QFileDialog.getOpenFileName", self.choose_file, "#2E86C1"),
            ("选择颜色", "QColorDialog.getColor", self.choose_color, "#D4AC0D"),
            ("自定义表单", "FeedbackDialog", self.custom, "#16A085"),
        ]
        for index, (title, api, handler, color) in enumerate(items):
            card = QFrame()
            card.setObjectName("Card")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(18, 16, 18, 16)
            title_label = QLabel(title)
            title_label.setObjectName("SectionTitle")
            api_label = QLabel(api)
            api_label.setObjectName("Small")
            button = QPushButton("打开")
            button.setStyleSheet(f"background:{color};")
            button.clicked.connect(handler)
            layout.addWidget(title_label)
            layout.addWidget(api_label)
            layout.addStretch()
            layout.addWidget(button)
            grid.addWidget(card, index // 4, index % 4)

        root.addLayout(grid)
        self.status = QLabel("弹窗会阻塞当前窗口，直到用户处理完；所以只在必要时使用。")
        self.status.setObjectName("Subtitle")
        root.addWidget(self.status)
        root.addStretch()
        self.setCentralWidget(central)

    def info(self):
        QMessageBox.information(self, "提示", "数据已保存。")
        self.status.setText("信息提示：告诉用户操作成功。")

    def warning(self):
        QMessageBox.warning(self, "警告", "当前文件格式不受支持。")
        self.status.setText("警告提示：提醒风险，但还可以继续。")

    def error(self):
        QMessageBox.critical(self, "错误", "数据库连接失败，请检查配置。")
        self.status.setText("错误提示：告诉用户操作失败的原因。")

    def confirm(self):
        reply = QMessageBox.question(
            self, "确认", "确定要删除这条记录吗？", QMessageBox.Yes | QMessageBox.No
        )
        self.status.setText("用户选择了确定" if reply == QMessageBox.Yes else "用户取消了操作")

    def ask_text(self):
        text, ok = QInputDialog.getText(self, "重命名", "请输入新名称：")
        self.status.setText(f"输入内容：{text}" if ok else "取消输入")

    def choose_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择 Excel", "", "Excel (*.xlsx *.xls);;所有文件 (*)")
        self.status.setText(f"选择了：{path}" if path else "没有选择文件")

    def choose_color(self):
        color = QColorDialog.getColor(parent=self)
        self.status.setText(f"选择了颜色：{color.name()}" if color.isValid() else "没有选择颜色")

    def custom(self):
        dialog = FeedbackDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.status.setText("自定义反馈已提交")


def main():
    app = create_app()
    finish(app, DialogWindow(), "05_弹窗与对话框")


if __name__ == "__main__":
    main()
