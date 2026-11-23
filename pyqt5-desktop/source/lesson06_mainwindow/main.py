"""第 6 课：菜单栏、工具栏和状态栏。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QAction, QLabel, QMainWindow, QMessageBox, QTextEdit, QToolBar

from common import create_app, finish


class EditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("标准桌面界面")
        self.resize(980, 640)
        self.editor = QTextEdit()
        self.editor.setPlainText(
            "项目周报\n\n"
            "本周完成：\n"
            "1. 合并 36 份月度报表\n"
            "2. 完成销售预测模型\n"
            "3. 生成客户分群名单\n\n"
            "下周计划：\n"
            "把预测结果自动回填到 Excel 报表。"
        )
        self.setCentralWidget(self.editor)

        file_menu = self.menuBar().addMenu("文件")
        file_menu.addAction("新建", self.new_file, "Ctrl+N")
        file_menu.addAction("打开", self.open_file, "Ctrl+O")
        file_menu.addSeparator()
        file_menu.addAction("保存", self.save_file, "Ctrl+S")
        file_menu.addSeparator()
        file_menu.addAction("退出", self.close, "Ctrl+Q")

        edit_menu = self.menuBar().addMenu("编辑")
        edit_menu.addAction("撤销", self.editor.undo, "Ctrl+Z")
        edit_menu.addAction("重做", self.editor.redo, "Ctrl+Y")

        help_menu = self.menuBar().addMenu("帮助")
        help_menu.addAction("关于", self.about)

        toolbar = QToolBar("常用工具")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        toolbar.addAction("新建", self.new_file)
        toolbar.addAction("打开", self.open_file)
        toolbar.addAction("保存", self.save_file)
        toolbar.addSeparator()
        toolbar.addAction("撤销", self.editor.undo)
        toolbar.addAction("重做", self.editor.redo)

        self.statusBar().showMessage("就绪")
        self.count_label = QLabel("字符数：0")
        self.statusBar().addPermanentWidget(self.count_label)
        self.editor.textChanged.connect(self.update_count)
        self.update_count()

    def update_count(self):
        text = self.editor.toPlainText()
        self.statusBar().showMessage("已修改" if self.editor.document().isModified() else "就绪")
        self.count_label.setText(f"字符数：{len(text)}")

    def new_file(self):
        self.editor.clear()
        self.statusBar().showMessage("新建文件")

    def open_file(self):
        self.statusBar().showMessage("模拟打开文件：data/项目周报.txt")

    def save_file(self):
        self.statusBar().showMessage("模拟保存成功")
        QTimer.singleShot(1500, lambda: self.statusBar().showMessage("就绪"))

    def about(self):
        QMessageBox.about(self, "关于", "PyQt5 桌面应用示例\n版本 1.0")


def main():
    app = create_app()
    finish(app, EditorWindow(), "06_标准界面")


if __name__ == "__main__":
    main()
