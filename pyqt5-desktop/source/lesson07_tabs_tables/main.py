"""第 7 课：Tab 页签、分页表格和树状结构。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from common import create_app, finish, page_header

ORDERS = [
    ("ORD-1001", "星河科技", "企业版", "¥12,800", "已支付"),
    ("ORD-1002", "云图设计", "专业版", "¥6,400", "已支付"),
    ("ORD-1003", "远山贸易", "基础版", "¥1,980", "待支付"),
    ("ORD-1004", "青禾教育", "企业版", "¥15,600", "已支付"),
    ("ORD-1005", "北岸物流", "专业版", "¥7,200", "已退款"),
    ("ORD-1006", "光年传媒", "专业版", "¥6,800", "已支付"),
    ("ORD-1007", "海风餐饮", "基础版", "¥2,100", "待支付"),
    ("ORD-1008", "木棉医疗", "企业版", "¥18,900", "已支付"),
    ("ORD-1009", "拾光影像", "基础版", "¥1,680", "已支付"),
    ("ORD-1010", "知行咨询", "专业版", "¥8,600", "已支付"),
    ("ORD-1011", "一叶民宿", "基础版", "¥1,980", "待支付"),
    ("ORD-1012", "南山制造", "企业版", "¥21,500", "已支付"),
]


class DataWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("复杂控件")
        self.resize(1000, 680)
        self.page = 0
        self.page_size = 5

        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(30, 24, 30, 24)
        root.setSpacing(16)
        root.addWidget(page_header("复杂界面，也能拆成简单模块", "QTabWidget · QTableWidget · 分页 · QTreeWidget"))

        self.tabs = QTabWidget()
        self.tabs.addTab(self.build_table_page(), "订单管理")
        self.tabs.addTab(self.build_tree_page(), "组织架构")
        self.tabs.addTab(self.build_settings_page(), "系统设置")
        root.addWidget(self.tabs)
        self.setCentralWidget(central)
        self.render_table()

    def build_table_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["订单号", "客户", "套餐", "金额", "状态"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        footer = QHBoxLayout()
        self.page_label = QLabel()
        self.page_label.setObjectName("Subtitle")
        prev_button = QPushButton("上一页")
        prev_button.setObjectName("Ghost")
        next_button = QPushButton("下一页")
        prev_button.clicked.connect(self.prev_page)
        next_button.clicked.connect(self.next_page)
        footer.addWidget(self.page_label)
        footer.addStretch()
        footer.addWidget(prev_button)
        footer.addWidget(next_button)
        layout.addLayout(footer)
        return page

    def build_tree_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        tree = QTreeWidget()
        tree.setHeaderLabels(["部门 / 成员", "角色", "本月订单"])
        root = QTreeWidgetItem(["小李科技", "", ""])
        sales = QTreeWidgetItem(["销售部", "负责人：陈晨", "268"])
        sales.addChildren([
            QTreeWidgetItem(["华东组", "组长：李敏", "96"]),
            QTreeWidgetItem(["华南组", "组长：王磊", "82"]),
        ])
        product = QTreeWidgetItem(["产品部", "负责人：赵婷", "0"])
        product.addChildren([
            QTreeWidgetItem(["设计组", "组长：周凯", "0"]),
            QTreeWidgetItem(["研发组", "组长：孙悦", "0"]),
        ])
        root.addChildren([sales, product])
        tree.addTopLevelItem(root)
        tree.expandAll()
        tree.header().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(tree)
        return page

    def build_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        title = QLabel("分页设置")
        title.setObjectName("SectionTitle")
        hint = QLabel("表格页每页显示 5 条，点击上一页/下一页切换。真实项目可以从数据库分页查询。")
        hint.setObjectName("Subtitle")
        hint.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addStretch()
        return page

    def render_table(self):
        start = self.page * self.page_size
        rows = ORDERS[start : start + self.page_size]
        self.table.setRowCount(len(rows))
        for row, values in enumerate(rows):
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 4:
                    item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, column, item)
        pages = (len(ORDERS) + self.page_size - 1) // self.page_size
        self.page_label.setText(f"第 {self.page + 1} / {pages} 页 · 共 {len(ORDERS)} 条")

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            self.render_table()

    def next_page(self):
        if (self.page + 1) * self.page_size < len(ORDERS):
            self.page += 1
            self.render_table()


def main():
    app = create_app()
    finish(app, DataWindow(), "07_复杂控件")


if __name__ == "__main__":
    main()
