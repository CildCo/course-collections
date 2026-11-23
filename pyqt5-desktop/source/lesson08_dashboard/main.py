"""第 8 课：完整数据仪表盘项目。"""
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from common import BarChart, LineChart, create_app, finish


class MetricCard(QFrame):
    def __init__(self, title, value, change, accent):
        super().__init__()
        self.setObjectName("DarkCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 15, 18, 15)
        layout.setSpacing(5)
        title_label = QLabel(title)
        title_label.setObjectName("DarkMuted")
        value_label = QLabel(value)
        value_label.setObjectName("DarkMetric")
        value_label.setStyleSheet(f"color:{accent};")
        change_label = QLabel(change)
        change_label.setObjectName("DarkMuted")
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(change_label)


class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("销售数据驾驶舱")
        self.resize(1180, 760)
        central = QWidget()
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self.build_sidebar())

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(28, 24, 28, 20)
        content_layout.setSpacing(16)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("销售数据驾驶舱")
        title.setObjectName("DarkTitle")
        subtitle = QLabel("数据更新频率：5 分钟 · 当前展示 2026 年 5 月")
        subtitle.setObjectName("DarkMuted")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()
        self.clock = QLabel()
        self.clock.setObjectName("DarkMuted")
        refresh = QPushButton("刷新数据")
        refresh.setObjectName("DarkAction")
        refresh.clicked.connect(lambda: self.statusBar().showMessage("数据已刷新 · " + datetime.now().strftime("%H:%M:%S")))
        header.addWidget(self.clock)
        header.addWidget(refresh)
        content_layout.addLayout(header)

        metrics = QGridLayout()
        metrics.setSpacing(14)
        cards = [
            ("今日访客", "12,480", "较昨日 +8.2%", "#2EE6B8"),
            ("今日订单", "3,286", "较昨日 +4.6%", "#5DADE2"),
            ("转化率", "26.3%", "较昨日 -0.8%", "#F4D03F"),
            ("今日收入", "¥286,400", "较昨日 +12.4%", "#2EE6B8"),
        ]
        for index, (title_text, value, change, accent) in enumerate(cards):
            metrics.addWidget(MetricCard(title_text, value, change, accent), 0, index)
        content_layout.addLayout(metrics)

        charts = QHBoxLayout()
        charts.setSpacing(14)
        line_card = QFrame()
        line_card.setObjectName("DarkCard")
        line_layout = QVBoxLayout(line_card)
        line_layout.setContentsMargins(18, 14, 18, 10)
        line_title = QLabel("最近 7 天订单趋势")
        line_title.setObjectName("DarkMuted")
        line_layout.addWidget(line_title)
        line_layout.addWidget(LineChart(["05-10", "05-11", "05-12", "05-13", "05-14", "05-15", "05-16"], [2180, 2460, 2310, 2890, 3100, 2980, 3286], dark=True))
        charts.addWidget(line_card, 3)

        bar_card = QFrame()
        bar_card.setObjectName("DarkCard")
        bar_layout = QVBoxLayout(bar_card)
        bar_layout.setContentsMargins(18, 14, 18, 10)
        bar_title = QLabel("各品类销量")
        bar_title.setObjectName("DarkMuted")
        bar_layout.addWidget(bar_title)
        bar_layout.addWidget(BarChart(["电子", "服装", "家居", "图书", "其他"], [980, 860, 620, 410, 416], dark=True))
        charts.addWidget(bar_card, 2)
        content_layout.addLayout(charts)

        table_card = QFrame()
        table_card.setObjectName("DarkCard")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(18, 14, 18, 14)
        table_title = QLabel("最近订单")
        table_title.setObjectName("DarkMuted")
        table_layout.addWidget(table_title)
        table = QTableWidget(6, 4)
        table.setHorizontalHeaderLabels(["订单号", "客户", "金额", "状态"])
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.setAlternatingRowColors(True)
        rows = [
            ("ORD-20260516-01", "星河科技", "¥12,800", "已支付"),
            ("ORD-20260516-02", "远山贸易", "¥1,980", "待支付"),
            ("ORD-20260516-03", "青禾教育", "¥15,600", "已支付"),
            ("ORD-20260516-04", "北岸物流", "¥7,200", "已退款"),
            ("ORD-20260516-05", "光年传媒", "¥6,800", "已支付"),
            ("ORD-20260516-06", "南山制造", "¥21,500", "已支付"),
        ]
        for row, values in enumerate(rows):
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 3:
                    item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, column, item)
        table_layout.addWidget(table)
        content_layout.addWidget(table_card, 1)
        root.addWidget(content, 1)
        self.setCentralWidget(central)
        self.statusBar().showMessage("系统运行正常 · 自动刷新已开启")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()

    def build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(210)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 24, 18, 20)
        layout.setSpacing(7)
        brand = QLabel("小居数据台")
        brand.setObjectName("DarkTitle")
        brand.setStyleSheet("font-size:20px;")
        caption = QLabel("DESKTOP ANALYTICS")
        caption.setObjectName("DarkMuted")
        layout.addWidget(brand)
        layout.addWidget(caption)
        layout.addSpacing(22)
        for index, text in enumerate(["概览", "销售分析", "客户洞察", "报表中心", "系统设置"]):
            button = QPushButton(text)
            button.setObjectName("NavActive" if index == 0 else "NavButton")
            button.clicked.connect(lambda _=False, name=text: self.statusBar().showMessage(f"切换到：{name}"))
            layout.addWidget(button)
        layout.addStretch()
        user = QLabel("当前用户\n小居 · 管理员")
        user.setObjectName("DarkMuted")
        layout.addWidget(user)
        return sidebar

    def update_clock(self):
        self.clock.setText(datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))


def main():
    app = create_app(dark=True)
    finish(app, DashboardWindow(), "08_数据仪表盘", delay=1200)


if __name__ == "__main__":
    main()
