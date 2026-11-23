# 第6课：自动化闭环，把图表插入 Excel 和 PPT
# 运行：python main.py
# 说明：邮件发送和定时任务只打印操作步骤，本脚本不会联网，也不会启动死循环。

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR.parent))

from common import COLORS, add_bar_labels, data_dir, output_dir, plt, save_figure, setup_chinese_font, style_axes

from PIL import Image as PILImage
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

WEEKDAYS = ["周一", "周二", "周三", "周四", "周五"]
ONLINE = [124, 131, 109, 148, 183]
OFFLINE = [88, 97, 91, 103, 121]

HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(name="Microsoft YaHei", color="FFFFFF", bold=True, size=11)
BODY_FONT = Font(name="Microsoft YaHei", size=10)
CENTER = Alignment(horizontal="center", vertical="center")
THIN = Side(style="thin", color="D9E2F3")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def draw_trend(path):
    """本周总销量趋势。"""
    setup_chinese_font()
    totals = [online + offline for online, offline in zip(ONLINE, OFFLINE)]
    fig, ax = plt.subplots(figsize=(10, 5.6), dpi=200)
    x = list(range(len(WEEKDAYS)))
    ax.plot(
        x,
        totals,
        color=COLORS["blue"],
        linewidth=2.6,
        marker="o",
        markersize=8,
        markerfacecolor="white",
        markeredgewidth=2,
    )
    ax.fill_between(x, totals, min(totals) - 30, color=COLORS["blue"], alpha=0.10)
    for xi, value in zip(x, totals):
        ax.annotate(
            f"{value}",
            xy=(xi, value),
            xytext=(0, 10),
            textcoords="offset points",
            ha="center",
            fontsize=10,
            fontweight="bold",
            color=COLORS["dark_blue"],
        )
    ax.set_xticks(x)
    ax.set_xticklabels(WEEKDAYS)
    ax.set_ylim(min(totals) - 40, max(totals) + 35)
    ax.set_title("本周总销量趋势", fontsize=17, fontweight="bold", pad=14)
    ax.set_xlabel("日期")
    ax.set_ylabel("销量（件）")
    style_axes(ax)
    return save_figure(fig, path)


def draw_channel(path):
    """线上与线下渠道并排对比。"""
    setup_chinese_font()
    fig, ax = plt.subplots(figsize=(9, 5.6), dpi=200)
    x = list(range(len(WEEKDAYS)))
    width = 0.36
    bars1 = ax.bar([i - width / 2 for i in x], ONLINE, width, label="线上", color=COLORS["blue"])
    bars2 = ax.bar([i + width / 2 for i in x], OFFLINE, width, label="线下", color=COLORS["orange"])
    add_bar_labels(ax, bars1, fontsize=9)
    add_bar_labels(ax, bars2, fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(WEEKDAYS)
    ax.set_ylim(0, max(ONLINE + OFFLINE) * 1.22)
    ax.set_title("线上与线下销量对比", fontsize=17, fontweight="bold", pad=14)
    ax.set_xlabel("日期")
    ax.set_ylabel("销量（件）")
    ax.legend(frameon=False, loc="upper left")
    style_axes(ax)
    return save_figure(fig, path)


def image_size(path, max_width=None):
    """读取图片尺寸，按比例缩放。"""
    with PILImage.open(path) as img:
        width, height = img.size
    if max_width and width > max_width:
        height = int(height * max_width / width)
        width = max_width
    return width, height


def build_excel(trend_path, channel_path, path):
    """数据写进 Excel，再把两张图贴在右侧。"""
    wb = Workbook()
    ws = wb.active
    ws.title = "周报数据"
    ws.append(["日期", "线上销量", "线下销量", "合计"])
    for day, online, offline in zip(WEEKDAYS, ONLINE, OFFLINE):
        ws.append([day, online, offline, online + offline])

    for cell in ws[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = CENTER
        cell.border = BORDER
    for row in ws.iter_rows(min_row=2, max_row=6, min_col=1, max_col=4):
        for cell in row:
            cell.font = BODY_FONT
            cell.alignment = CENTER
            cell.border = BORDER
    for column, width in {"A": 12, "B": 13, "C": 13, "D": 12}.items():
        ws.column_dimensions[column].width = width
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = "A2"

    width1, height1 = image_size(trend_path, max_width=720)
    img1 = XLImage(str(trend_path))
    img1.width, img1.height = width1, height1
    ws.add_image(img1, "F2")

    width2, height2 = image_size(channel_path, max_width=640)
    img2 = XLImage(str(channel_path))
    img2.width, img2.height = width2, height2
    ws.add_image(img2, "F27")

    wb.save(path)
    return path


def add_picture_slide(ppt, title, image_path, notes):
    """一页 PPT：标题 + 图片 + 演讲者备注。"""
    slide = ppt.slides.add_slide(ppt.slide_layouts[5])  # 仅标题版式
    title_shape = slide.shapes.title
    title_shape.text = title
    paragraph = title_shape.text_frame.paragraphs[0]
    paragraph.font.size = Pt(28)
    paragraph.font.bold = True
    paragraph.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

    width, height = image_size(image_path)
    max_width = Inches(11.6)
    max_height = Inches(5.5)
    ratio = min(max_width / width, max_height / height)
    pic_width = int(width * ratio)
    pic_height = int(height * ratio)
    left = int((ppt.slide_width - pic_width) / 2)
    top = Inches(1.35)
    slide.shapes.add_picture(str(image_path), left, top, width=pic_width, height=pic_height)

    slide.notes_slide.notes_text_frame.text = notes
    return slide


def build_ppt(trend_path, channel_path, path):
    """生成两页汇报 PPT。"""
    ppt = Presentation()
    ppt.slide_width = Inches(13.333)
    ppt.slide_height = Inches(7.5)

    add_picture_slide(
        ppt,
        "上周销售情况",
        trend_path,
        "数据来源：销售部周报。\n整体销量从周一的212件增长到周五的304件，周五为本周高点。",
    )
    add_picture_slide(
        ppt,
        "线上与线下渠道对比",
        channel_path,
        "线上渠道周五达到183件，线下渠道整体平稳。\n建议下周增加线上活动曝光，并关注周三的低谷。",
    )

    ppt.save(path)
    return path


def show_delivery_notes():
    """只打印说明，不执行邮件和定时任务。"""
    print("\n" + "-" * 60)
    print("交付说明（仅打印，不执行）")
    print("-" * 60)
    print("1. 邮件发送：需要填写公司 SMTP 服务器、账号和授权码，")
    print("   把 xlsx 和 pptx 作为附件发送；本脚本不会连接任何邮件服务。")
    print("2. 定时执行：可以在 Windows 任务计划程序中新建任务，")
    print("   每周一 08:00 调用 python main.py；本脚本不会启动定时循环。")
    print("3. 发送前请先人工检查数据和图表，确认收件人和附件无误。")


def main():
    print("=" * 60)
    print("第6课：图表自动插入 Excel 和 PPT")
    print("=" * 60)

    data_dir(BASE_DIR)
    out = output_dir(BASE_DIR)

    print("\n[1/3] 生成图表...")
    trend_path = draw_trend(out / "本周销量趋势.png")
    channel_path = draw_channel(out / "渠道销量对比.png")

    print("\n[2/3] 写入 Excel...")
    excel_path = build_excel(trend_path, channel_path, out / "销售周报.xlsx")
    print(f"已生成 Excel：{excel_path}")

    print("\n[3/3] 生成 PPT...")
    ppt_path = build_ppt(trend_path, channel_path, out / "销售周报.pptx")
    print(f"已生成 PPT：{ppt_path}")

    print("\n输出文件检查：")
    for path in (excel_path, ppt_path):
        print(f" - {path.name}  {path.stat().st_size / 1024:.1f} KB")

    show_delivery_notes()


if __name__ == "__main__":
    main()
