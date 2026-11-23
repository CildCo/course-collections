# PyQt5 从入门到实战：8 天打造专业桌面应用

这是《PyQt5从入门到实战：8天打造专业桌面应用》的配套源码。  
8 节课从第一个窗口开始，依次完成布局、信号与槽、常用输入控件、弹窗、标准主窗口、Tab/表格/树，最后做一个深色数据仪表盘。

课程使用 PyQt5 5.15，界面全部用代码搭建，不需要 Qt Designer。

## 安装

```bash
cd 码袋子/content/collections/pyqt5-desktop/source
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

如果下载慢，可以加清华源：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 一键运行

```bash
python run_all.py
```

批量运行使用 Qt 的 offscreen 模式，不会弹出窗口，每课结束后自动把界面截图保存到 `output/`。

## 逐课运行

```bash
python lesson01_first_window/main.py
python lesson02_layouts/main.py
python lesson03_signals/main.py
python lesson04_inputs/main.py
python lesson05_dialogs/main.py
python lesson06_mainwindow/main.py
python lesson07_tabs_tables/main.py
python lesson08_dashboard/main.py
```

逐课运行会正常显示桌面窗口，关闭窗口后程序退出。加上 `--auto` 参数则自动截图并退出。

## 课次与输出

| 课次 | 目录 | 主要内容 | 截图 |
|---|---|---|---|
| 第1课 | `lesson01_first_window/` | QApplication、QMainWindow、按钮和计数器 | `01_第一个窗口.png` |
| 第2课 | `lesson02_layouts/` | QVBox/QHBox/QGrid/QFormLayout | `02_控件与布局.png` |
| 第3课 | `lesson03_signals/` | clicked 信号、connect、灯开关 | `03_信号与槽.png` |
| 第4课 | `lesson04_inputs/` | QLineEdit、QComboBox、QCheckBox、QSlider 等 | `04_输入控件.png` |
| 第5课 | `lesson05_dialogs/` | QMessageBox、QInputDialog、QFileDialog、自定义 QDialog | `05_弹窗与对话框.png` |
| 第6课 | `lesson06_mainwindow/` | 菜单栏、工具栏、状态栏和 QAction | `06_标准界面.png` |
| 第7课 | `lesson07_tabs_tables/` | QTabWidget、分页 QTableWidget、QTreeWidget | `07_复杂控件.png` |
| 第8课 | `lesson08_dashboard/` | 深色仪表盘、侧边栏、指标卡、自绘折线/柱状图 | `08_数据仪表盘.png` |

## 目录说明

```text
pyqt5-desktop/
├── collection.json
└── source/
    ├── common.py                 主题、窗口工具和 QPainter 图表
    ├── run_all.py                一键批量截图
    ├── requirements.txt
    └── lesson01_first_window/    每课一个目录
        └── main.py
```

## 三个容易踩的坑

1. **布局不要写死坐标**：用 QVBoxLayout/QHBoxLayout/QGridLayout，窗口缩放时控件才会跟着动。
2. **信号槽参数要对齐**：`textChanged` 会传字符串，槽函数不接受参数时用 `lambda *_: ...` 包一层。
3. **批量运行用 offscreen**：服务器或 CI 没有显示器时设置 `QT_QPA_PLATFORM=offscreen`，否则 Qt 会启动失败。

## 关于图表

第8课没有依赖 QtCharts，而是用 QPainter 自绘折线和柱状图。这样只装 PyQt5 就能跑，也方便改成自己的数据源。
