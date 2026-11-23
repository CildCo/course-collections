# 第2课：用 openpyxl 把 Excel 默认图升级成高管版
# 运行：python main.py

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR.parent))

from common import data_dir, output_dir

from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.chart.axis import ChartLines
from openpyxl.chart.data_source import AxDataSource, StrRef
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.marker import Marker
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.drawing.line import LineProperties
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(name="Microsoft YaHei", color="FFFFFF", bold=True, size=11)
BODY_FONT = Font(name="Microsoft YaHei", size=10)
TOTAL_FONT = Font(name="Microsoft YaHei", size=10, bold=True, color="1F4E79")
CENTER = Alignment(horizontal="center", vertical="center")
THIN = Side(style="thin", color="D9E2F3")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

MONTHS = ["1月", "2月", "3月", "4月", "5月", "6月"]
DIRECT = [120, 138, 132, 156, 172, 190]
PARTNER = [86, 92, 101, 108, 118, 126]
TARGET = [110, 115, 120, 130, 140, 150]


def make_workbook():
    """先生成数据表，再在右侧放柱状图和折线图。"""
    wb = Workbook()
    ws = wb.active
    ws.title = "销售看板"

    headers = ["月份", "直营渠道", "分销渠道", "合计", "月度目标"]
    ws.append(headers)
    for month, direct, partner, target in zip(MONTHS, DIRECT, PARTNER, TARGET):
        ws.append([month, direct, partner, direct + partner, target])
    ws.append(["合计", sum(DIRECT), sum(PARTNER), sum(DIRECT) + sum(PARTNER), sum(TARGET)])

    # 表头和数据区的基础美化
    for cell in ws[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = CENTER
        cell.border = BORDER

    for row in ws.iter_rows(min_row=2, max_row=7, min_col=1, max_col=5):
        for cell in row:
            cell.font = BODY_FONT
            cell.alignment = CENTER
            cell.border = BORDER
            if cell.column_letter in ("B", "C", "D", "E"):
                cell.number_format = '0" 万元"'

    for cell in ws[8]:
        cell.font = TOTAL_FONT
        cell.fill = PatternFill("solid", fgColor="EAF1F8")
        cell.border = BORDER
        cell.alignment = CENTER
        if cell.column_letter in ("B", "C", "D", "E"):
            cell.number_format = '0" 万元"'

    widths = {"A": 10, "B": 14, "C": 14, "D": 12, "E": 14}
    for column, width in widths.items():
        ws.column_dimensions[column].width = width
    ws.freeze_panes = "A2"
    ws.sheet_view.showGridLines = False

    # 柱状图：对比两个渠道
    bar = BarChart()
    bar.type = "col"
    bar.style = 10
    bar.title = "2026年上半年渠道销售对比"
    bar.y_axis.title = "销售额（万元）"
    bar.x_axis.title = "月份"
    bar.width = 19
    bar.height = 9.5
    bar.gapWidth = 55
    bar.overlap = -8
    bar.legend.position = "b"

    data = Reference(ws, min_col=2, max_col=3, min_row=1, max_row=7)
    categories = Reference(ws, min_col=1, min_row=2, max_row=7)
    bar.add_data(data, titles_from_data=True)
    bar.set_categories(categories)
    use_text_categories(bar, ws, 2, 7)
    bar.series[0].graphicalProperties = GraphicalProperties(solidFill="2E86C1")
    bar.series[1].graphicalProperties = GraphicalProperties(solidFill="F39C12")
    bar.dataLabels = DataLabelList()
    bar.dataLabels.showVal = True
    bar.dataLabels.showSerName = False
    bar.dataLabels.showCatName = False
    bar.dataLabels.showLegendKey = False
    bar.dataLabels.position = "outEnd"
    style_axis(bar)

    # 折线图：合计与目标的走势
    line = LineChart()
    line.style = 12
    line.title = "合计销售额与月度目标"
    line.y_axis.title = "销售额（万元）"
    line.x_axis.title = "月份"
    line.width = 19
    line.height = 9.5
    line.legend.position = "b"

    data_line = Reference(ws, min_col=4, max_col=5, min_row=1, max_row=7)
    line.add_data(data_line, titles_from_data=True)
    line.set_categories(categories)
    use_text_categories(line, ws, 2, 7)
    for series, color in zip(line.series, ["1F4E79", "E74C3C"]):
        series.graphicalProperties.line = LineProperties(solidFill=color, w=28575)
        series.marker = Marker(symbol="circle", size=7)
        series.marker.graphicalProperties = GraphicalProperties(solidFill=color)
        series.smooth = False
    line.dataLabels = DataLabelList()
    line.dataLabels.showVal = True
    line.dataLabels.showSerName = False
    line.dataLabels.showCatName = False
    line.dataLabels.showLegendKey = False
    line.dataLabels.position = "t"
    style_axis(line)

    ws.add_chart(bar, "G2")
    ws.add_chart(line, "G22")

    return wb, ws


def use_text_categories(chart, ws, min_row, max_row):
    """把分类轴显式指向文本单元格，避免月份显示成 1、2、3。"""
    formula = f"'{ws.title}'!$A${min_row}:$A${max_row}"
    for series in chart.series:
        series.cat = AxDataSource(strRef=StrRef(f=formula))


def style_axis(chart):
    """统一坐标轴、网格线和刻度样式。"""
    chart.x_axis.delete = False
    chart.y_axis.delete = False
    chart.x_axis.majorTickMark = "out"
    chart.y_axis.majorTickMark = "out"
    chart.y_axis.majorGridlines = ChartLines()
    chart.y_axis.majorGridlines.spPr = GraphicalProperties(
        ln=LineProperties(solidFill="D9D9D9", w=9525)
    )
    chart.x_axis.spPr = GraphicalProperties(
        ln=LineProperties(solidFill="7F7F7F", w=9525)
    )


def main():
    print("=" * 60)
    print("第2课：把 Excel 默认图升级成高管特供版")
    print("=" * 60)

    data_dir(BASE_DIR)
    out = output_dir(BASE_DIR)
    path = out / "高管销售图表.xlsx"

    wb, ws = make_workbook()
    wb.save(path)

    print(f"数据表：{ws.max_row - 2} 个月 + 合计行，共 {ws.max_column} 列")
    print(f"已生成柱状图 + 折线图，工作表：{ws.title}")
    print(f"文件位置：{path}")
    print("打开后可在 Excel/WPS 中直接看到原生图表，颜色、标题、坐标轴、数据标签和网格线都已设置。")


if __name__ == "__main__":
    main()
