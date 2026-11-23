# 课程公用工具：统一中文字体、配色、输出目录和保存方式。

from pathlib import Path

import matplotlib

# 必须在导入 pyplot 之前设置，保证无界面环境也能正常出图
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

ROOT_DIR = Path(__file__).resolve().parent

# 按优先级挑选本机可用的中文字体，最后用 DejaVu Sans 兜底
FONT_LIST = [
    "Microsoft YaHei",
    "SimHei",
    "Noto Sans CJK SC",
    "Source Han Sans CN",
    "Arial Unicode MS",
    "DejaVu Sans",
]

COLORS = {
    "blue": "#2E86C1",
    "dark_blue": "#1F4E79",
    "orange": "#F39C12",
    "red": "#E74C3C",
    "green": "#27AE60",
    "purple": "#8E44AD",
    "teal": "#16A085",
    "gray": "#7F8C8D",
    "light_gray": "#BDC3C7",
    "cream": "#F4F6F7",
}


def setup_chinese_font():
    """设置中文字体和负号显示，返回当前首选字体名。"""
    plt.rcParams["font.sans-serif"] = FONT_LIST
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["axes.facecolor"] = "white"
    return plt.rcParams["font.sans-serif"][0]


def prepare_dir(path):
    """创建目录并返回绝对路径。"""
    path = Path(path).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def data_dir(lesson_dir):
    """每课自己的 data 目录。"""
    return prepare_dir(Path(lesson_dir) / "data")


def output_dir(lesson_dir):
    """每课自己的 output 目录。"""
    return prepare_dir(Path(lesson_dir) / "output")


def style_axes(ax, grid_axis="y"):
    """去掉上、右边框，并加一层很淡的虚线网格。"""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis=grid_axis, linestyle="--", alpha=0.30)
    ax.set_axisbelow(True)


def add_bar_labels(ax, bars, fmt="{:.0f}", dy=3, fontsize=10):
    """在柱子顶部批量写数值。"""
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            fmt.format(height),
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, dy),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=fontsize,
            fontweight="bold",
        )


def save_figure(fig, path, dpi=200):
    """保存图片后关闭画布，避免图片越画越多占用内存。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"已保存图片：{path}")
    return path


# 导入本模块时就完成字体配置，后续课程不用重复写
setup_chinese_font()
