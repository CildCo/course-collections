# 第5课：Excel 透视表、增长率与报表美化
# 运行：python main.py

from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from make_samples import ensure_samples

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

HEADER_FILL = PatternFill("solid", fgColor="2F5FE0")
HEADER_FONT = Font(name="微软雅黑", color="FFFFFF", bold=True, size=11)
LOW_FILL = PatternFill("solid", fgColor="FFC7CE")
LOW_FONT = Font(color="9C0006")
CENTER = Alignment(horizontal="center", vertical="center")
THIN = Side(style="thin", color="D6DCE6")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def pivot_report():
    """按地区和产品生成销售透视表。"""
    df = pd.read_excel(DATA_DIR / "sales_data.xlsx")
    report = pd.pivot_table(
        df,
        index="地区",
        columns="产品",
        values="销售额",
        aggfunc="sum",
        fill_value=0,
        margins=True,
        margins_name="合计",
    )
    output = OUTPUT_DIR / "部门业绩透视表.xlsx"
    report.to_excel(output)
    print("已生成透视表：", output)
    return output


def format_report(path):
    """美化表头、边框、列宽，并把低于 10000 的数字标红。"""
    wb = load_workbook(path)
    ws = wb.active

    for cell in ws[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = CENTER
        cell.border = BORDER

    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, max_col=ws.max_column):
        for cell in row:
            cell.alignment = CENTER
            cell.border = BORDER
            if isinstance(cell.value, (int, float)) and cell.value < 10000:
                cell.fill = LOW_FILL
                cell.font = LOW_FONT

    for column in ws.columns:
        width = max(len(str(cell.value or "")) for cell in column) + 3
        ws.column_dimensions[column[0].column_letter].width = min(width, 18)

    wb.save(path)
    print("已美化：", path)


def growth_report():
    """计算同比增长率并格式化为百分比。"""
    df = pd.read_excel(DATA_DIR / "growth.xlsx")
    df["增长率"] = (df["今年"] - df["去年"]) / df["去年"]
    df["增长率数值"] = df["增长率"].round(2)
    df["增长率展示"] = df["增长率"].apply(lambda x: f"{x:.2%}")
    output = OUTPUT_DIR / "增长率分析.xlsx"
    df.to_excel(output, index=False)
    print("\n同比增长：")
    print(df[["月份", "今年", "去年", "增长率展示"]].to_string(index=False))


def complex_pivot():
    """地区 + 季度的多层级透视表。"""
    df = pd.read_excel(DATA_DIR / "sales_data.xlsx")
    df["日期"] = pd.to_datetime(df["日期"])
    df["季度"] = df["日期"].dt.quarter
    report = pd.pivot_table(
        df,
        index=["地区", "季度"],
        values="销售额",
        aggfunc="sum",
        margins=True,
        margins_name="总计",
    )
    output = OUTPUT_DIR / "地区季度透视表.xlsx"
    report.to_excel(output)
    print("\n地区季度透视表：")
    print(report)


def chart_report():
    """生成带柱状图的销售周报。"""
    df = pd.read_excel(DATA_DIR / "sales_data.xlsx")
    report = pd.pivot_table(
        df,
        index="地区",
        columns="产品",
        values="销售额",
        aggfunc="sum",
        fill_value=0,
    )
    output = OUTPUT_DIR / "销售周报.xlsx"
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        report.to_excel(writer, sheet_name="汇总")

    format_report(output)

    wb = load_workbook(output)
    ws = wb["汇总"]
    chart = BarChart()
    chart.title = "各地区产品销售情况"
    chart.y_axis.title = "销售额"
    chart.x_axis.title = "地区"
    data = Reference(ws, min_col=2, min_row=1, max_col=ws.max_column, max_row=ws.max_row)
    categories = Reference(ws, min_col=1, min_row=2, max_row=ws.max_row)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(categories)
    ws.add_chart(chart, "H2")
    wb.save(output)
    print("\n已生成带图表的周报：", output)


def main():
    ensure_samples()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = pivot_report()
    format_report(path)
    growth_report()
    complex_pivot()
    chart_report()


if __name__ == "__main__":
    main()
