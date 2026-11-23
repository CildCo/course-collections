"""PyQt5 桌面应用课程共用工具：主题、窗口和自绘图表。"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Windows 下 PyQt5 有时找不到自带的 platform 插件，先补上路径再导入 QtWidgets。
try:
    import PyQt5

    _QT_PLUGIN_DIR = Path(PyQt5.__file__).resolve().parent / "Qt5" / "plugins"
    if _QT_PLUGIN_DIR.exists():
        os.environ.setdefault("QT_QPA_PLATFORM_PLUGIN_PATH", str(_QT_PLUGIN_DIR))
except Exception:
    pass

from PyQt5.QtCore import QPointF, QRectF, Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"

NAVY = "#1F3A5F"
TEAL = "#16A085"
BLUE = "#2E86C1"
GOLD = "#D4AC0D"
RED = "#C0392B"
GRAY = "#7F8C8D"
BG = "#F4F7FB"

APP_QSS = """
QWidget {
    background: #F4F7FB;
    color: #243447;
    font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI";
    font-size: 13px;
}
QMainWindow, QDialog { background: #F4F7FB; }
QFrame#Card {
    background: #FFFFFF;
    border: 1px solid #E3EAF2;
    border-radius: 14px;
}
QFrame#Hero {
    background: #FFFFFF;
    border: 1px solid #E3EAF2;
    border-radius: 20px;
}
QLabel#Title { font-size: 26px; font-weight: 700; color: #1F3A5F; }
QLabel#Subtitle { color: #7F8C8D; font-size: 13px; }
QLabel#SectionTitle { font-size: 15px; font-weight: 700; color: #1F3A5F; }
QLabel#Metric { font-size: 30px; font-weight: 700; color: #16A085; }
QLabel#Small { color: #7F8C8D; font-size: 11px; }
QPushButton {
    background: #16A085;
    color: white;
    border: none;
    border-radius: 9px;
    padding: 9px 18px;
    font-weight: 600;
}
QPushButton:hover { background: #12876F; }
QPushButton:pressed { background: #0E6B58; }
QPushButton#Ghost {
    background: #FFFFFF;
    color: #1F3A5F;
    border: 1px solid #D6E0EA;
}
QPushButton#Ghost:hover { background: #EEF5FA; }
QPushButton#Danger { background: #C0392B; }
QPushButton#Danger:hover { background: #A93226; }
QLineEdit, QComboBox, QSpinBox, QTextEdit {
    background: #FFFFFF;
    border: 1px solid #D6E0EA;
    border-radius: 8px;
    padding: 8px 10px;
    selection-background-color: #16A085;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus { border: 1px solid #16A085; }
QComboBox::drop-down { border: none; width: 22px; }
QCheckBox, QRadioButton { spacing: 8px; }
QCheckBox::indicator, QRadioButton::indicator { width: 16px; height: 16px; }
QSlider::groove:horizontal { height: 6px; background: #D6E0EA; border-radius: 3px; }
QSlider::handle:horizontal { width: 16px; margin: -5px 0; background: #16A085; border-radius: 8px; }
QTabWidget::pane { border: 1px solid #E3EAF2; border-radius: 12px; background: #FFFFFF; }
QTabBar::tab {
    background: transparent;
    color: #7F8C8D;
    padding: 9px 18px;
    margin-right: 4px;
    border-radius: 8px;
}
QTabBar::tab:selected { background: #E8F6F2; color: #12876F; font-weight: 700; }
QTableWidget, QTreeWidget {
    background: #FFFFFF;
    border: 1px solid #E3EAF2;
    border-radius: 10px;
    gridline-color: #EEF3F8;
    alternate-background-color: #F8FBFD;
}
QHeaderView::section {
    background: #F1F6FA;
    color: #1F3A5F;
    border: none;
    padding: 8px;
    font-weight: 700;
}
QMenuBar { background: #FFFFFF; }
QMenuBar::item { padding: 6px 12px; background: transparent; }
QMenuBar::item:selected { background: #E8F6F2; border-radius: 6px; }
QMenu { background: #FFFFFF; border: 1px solid #E3EAF2; padding: 6px; }
QMenu::item { padding: 7px 26px 7px 18px; border-radius: 6px; }
QMenu::item:selected { background: #E8F6F2; color: #12876F; }
QToolBar { background: #FFFFFF; border: none; spacing: 6px; padding: 4px; }
QStatusBar { background: #FFFFFF; color: #7F8C8D; }
"""

DARK_QSS = """
QWidget { background: #111827; color: #D7E2EE; font-family: "Microsoft YaHei"; font-size: 13px; }
QFrame#Sidebar { background: #0B1220; border: none; }
QFrame#DarkCard { background: #172235; border: 1px solid #24344D; border-radius: 14px; }
QLabel#DarkTitle { color: #FFFFFF; font-size: 24px; font-weight: 700; }
QLabel#DarkMuted { color: #8194AB; font-size: 11px; }
QLabel#DarkMetric { color: #2EE6B8; font-size: 28px; font-weight: 700; }
QPushButton#NavButton {
    text-align: left; background: transparent; color: #9FB0C5;
    border: none; padding: 11px 16px; border-radius: 9px;
}
QPushButton#NavButton:hover { background: #172235; color: white; }
QPushButton#NavActive { text-align: left; background: #123C36; color: #2EE6B8; border: none; padding: 11px 16px; border-radius: 9px; font-weight: 700; }
QPushButton#DarkAction { background: #16A085; color: white; border: none; padding: 9px 16px; border-radius: 9px; }
QTableWidget { background: #172235; alternate-background-color: #1B2A40; border: none; color: #D7E2EE; gridline-color: #24344D; }
QHeaderView::section { background: #0F1B2D; color: #93A7BE; border: none; padding: 8px; }
QStatusBar { background: #0B1220; color: #8194AB; }
"""


def is_auto() -> bool:
    return "--auto" in sys.argv


def create_app(dark: bool = False) -> QApplication:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_QSS if dark else APP_QSS)
    app.setFont(QFont("Microsoft YaHei", 10))
    return app


def finish(app: QApplication, window: QWidget, name: str, delay: int = 900) -> None:
    """显示窗口；--auto 模式自动截图并退出，方便批量回归。"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    window.show()
    if is_auto():
        def capture() -> None:
            window.grab().save(str(OUTPUT_DIR / f"{name}.png"))
            app.quit()

        QTimer.singleShot(delay, capture)
    app.exec_()


def page_header(title: str, subtitle: str) -> QWidget:
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)
    title_label = QLabel(title)
    title_label.setObjectName("Title")
    subtitle_label = QLabel(subtitle)
    subtitle_label.setObjectName("Subtitle")
    layout.addWidget(title_label)
    layout.addWidget(subtitle_label)
    return container


def card(title: str, value: str, hint: str = "", accent: str = TEAL) -> QFrame:
    frame = QFrame()
    frame.setObjectName("Card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(18, 16, 18, 16)
    layout.setSpacing(6)
    title_label = QLabel(title)
    title_label.setObjectName("Small")
    value_label = QLabel(value)
    value_label.setObjectName("Metric")
    value_label.setStyleSheet(f"color: {accent};")
    layout.addWidget(title_label)
    layout.addWidget(value_label)
    if hint:
        hint_label = QLabel(hint)
        hint_label.setObjectName("Small")
        layout.addWidget(hint_label)
    layout.addStretch()
    return frame


class LineChart(QWidget):
    """用 QPainter 自绘折线图，避免额外安装 QtCharts。"""

    def __init__(self, labels: list[str], values: list[float], color: str = TEAL, dark: bool = False, parent=None):
        super().__init__(parent)
        self.labels = labels
        self.values = values
        self.color = QColor(color)
        self.dark = dark
        self.setMinimumHeight(210)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(42, 18, -18, -34)
        background = QColor("#172235") if self.dark else QColor("#FFFFFF")
        grid_color = QColor("#24344D") if self.dark else QColor("#E8EEF5")
        text_color = QColor("#8194AB") if self.dark else QColor("#9AA9BA")
        painter.fillRect(self.rect(), background)
        if not self.values:
            return
        low, high = min(self.values), max(self.values)
        span = max(high - low, 1)
        painter.setPen(QPen(grid_color, 1))
        for index in range(5):
            y = rect.top() + rect.height() * index / 4
            painter.drawLine(rect.left(), int(y), rect.right(), int(y))
            painter.setPen(text_color)
            painter.setFont(QFont("Microsoft YaHei", 8))
            painter.drawText(4, int(y) + 4, f"{high - span * index / 4:,.0f}")
            painter.setPen(QPen(grid_color, 1))
        points = []
        for index, value in enumerate(self.values):
            x = rect.left() + rect.width() * index / max(len(self.values) - 1, 1)
            y = rect.bottom() - (value - low) / span * rect.height()
            points.append(QPointF(x, y))
        gradient = QLinearGradient(0, rect.top(), 0, rect.bottom())
        gradient.setColorAt(0, QColor(22, 160, 133, 90))
        gradient.setColorAt(1, QColor(22, 160, 133, 5))
        area = points + [QPointF(points[-1].x(), rect.bottom()), QPointF(points[0].x(), rect.bottom())]
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(*area)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(self.color, 2.4))
        for start, end in zip(points, points[1:]):
            painter.drawLine(start, end)
        painter.setBrush(self.color)
        for point in points:
            painter.drawEllipse(point, 3.4, 3.4)
        painter.setPen(text_color)
        painter.setFont(QFont("Microsoft YaHei", 8))
        step = max(len(self.labels) // 7, 1)
        for index in range(0, len(self.labels), step):
            x = rect.left() + rect.width() * index / max(len(self.labels) - 1, 1)
            painter.drawText(QRectF(x - 24, rect.bottom() + 8, 48, 18), Qt.AlignCenter, self.labels[index])


class BarChart(QWidget):
    def __init__(self, labels: list[str], values: list[float], colors: list[str] | None = None, dark: bool = False, parent=None):
        super().__init__(parent)
        self.labels = labels
        self.values = values
        self.colors = colors or [TEAL, BLUE, GOLD, "#8E44AD", RED]
        self.dark = dark
        self.setMinimumHeight(210)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        background = QColor("#172235") if self.dark else QColor("#FFFFFF")
        grid_color = QColor("#24344D") if self.dark else QColor("#E8EEF5")
        text_color = QColor("#8194AB") if self.dark else QColor("#9AA9BA")
        painter.fillRect(self.rect(), background)
        rect = self.rect().adjusted(42, 18, -18, -34)
        if not self.values:
            return
        high = max(self.values) or 1
        painter.setPen(QPen(grid_color, 1))
        for index in range(5):
            y = rect.top() + rect.height() * index / 4
            painter.drawLine(rect.left(), int(y), rect.right(), int(y))
            painter.setPen(text_color)
            painter.setFont(QFont("Microsoft YaHei", 8))
            painter.drawText(4, int(y) + 4, f"{high * (4 - index) / 4:,.0f}")
            painter.setPen(QPen(grid_color, 1))
        count = len(self.values)
        slot = rect.width() / max(count, 1)
        bar_width = slot * 0.52
        painter.setFont(QFont("Microsoft YaHei", 8))
        for index, value in enumerate(self.values):
            x = rect.left() + slot * index + (slot - bar_width) / 2
            height = value / high * rect.height()
            color = QColor(self.colors[index % len(self.colors)])
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(QRectF(x, rect.bottom() - height, bar_width, height), 4, 4)
            painter.setPen(text_color)
            painter.drawText(QRectF(x - 12, rect.bottom() - height - 18, bar_width + 24, 16), Qt.AlignCenter, f"{value:,.0f}")
            painter.drawText(QRectF(x - 18, rect.bottom() + 8, bar_width + 36, 18), Qt.AlignCenter, self.labels[index])


def metric_row(items: list[tuple[str, str, str]]) -> QWidget:
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(14)
    for title, value, hint in items:
        layout.addWidget(card(title, value, hint))
    return container
