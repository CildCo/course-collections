"""第 9 课：把预测结果自动回填到 Excel 报表。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from common import OUTPUT_DIR, PROCESSED_DIR, ensure_orders, load_json, setup_plot

HEADER_FILL = PatternFill("solid", fgColor="1F3A5F")
ACCENT_FILL = PatternFill("solid", fgColor="16A085")
HEADER_FONT = Font(color="FFFFFF", bold=True, size=11)
TITLE_FONT = Font(color="1F3A5F", bold=True, size=18)
BODY_FONT = Font(color="333333", size=10)
THIN = Side(style="thin", color="D5D8DC")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def write_table(worksheet, frame: pd.DataFrame, start_row: int = 1) -> int:
    for column_index, column in enumerate(frame.columns, start=1):
        cell = worksheet.cell(row=start_row, column=column_index, value=str(column))
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = BORDER
    for row_index, row in enumerate(frame.itertuples(index=False), start=start_row + 1):
        for column_index, value in enumerate(row, start=1):
            cell = worksheet.cell(row=row_index, column=column_index, value=value)
            cell.font = BODY_FONT
            cell.border = BORDER
    for column_index, column in enumerate(frame.columns, start=1):
        width = max(12, min(28, max(len(str(column)), *(len(str(value)) for value in frame[column].head(40))) + 2))
        worksheet.column_dimensions[get_column_letter(column_index)].width = width
    return start_row + len(frame)


def style_title(worksheet, text: str, end_column: int = 6) -> None:
    worksheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=end_column)
    cell = worksheet.cell(row=1, column=1, value=text)
    cell.font = TITLE_FONT
    cell.alignment = Alignment(horizontal="left", vertical="center")
    worksheet.row_dimensions[1].height = 30


def main() -> None:
    setup_plot()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    orders = ensure_orders()
    forecast = pd.read_csv(PROCESSED_DIR / "sales_forecast.csv", parse_dates=["月份"])
    high_value = pd.read_csv(PROCESSED_DIR / "high_value_predictions.csv")
    churn = pd.read_csv(PROCESSED_DIR / "churn_predictions.csv").sort_values("流失概率", ascending=False)
    segments = pd.read_csv(PROCESSED_DIR / "segment_summary.csv")
    anomalies = pd.read_csv(PROCESSED_DIR / "expense_anomalies.csv").sort_values("异常分数", ascending=False)
    sales_metrics = load_json(PROCESSED_DIR / "sales_forecast_metrics.json")
    value_metrics = load_json(PROCESSED_DIR / "high_value_metrics.json")
    churn_metrics = load_json(PROCESSED_DIR / "churn_metrics.json")
    expense_metrics = load_json(PROCESSED_DIR / "expense_metrics.json")

    workbook = Workbook()
    summary = workbook.active
    summary.title = "经营摘要"
    style_title(summary, "机器学习预测与客户洞察报表", 6)
    summary["A3"] = "数据区间"
    summary["B3"] = f"{orders['下单日期'].min():%Y-%m} 至 {orders['下单日期'].max():%Y-%m}"
    summary["A4"] = "订单数"
    summary["B4"] = int(orders["订单编号"].nunique())
    summary["A5"] = "客户数"
    summary["B5"] = int(orders["客户ID"].nunique())
    summary["A6"] = "2026Q1 预测销售额"
    summary["B6"] = round(sales_metrics["forecast_q1_2026"], 2)
    summary["B6"].number_format = '#,##0.00'
    summary["A7"] = "高价值客户模型 AUC"
    summary["B7"] = round(value_metrics["roc_auc"], 3)
    summary["A8"] = "流失模型 AUC"
    summary["B8"] = round(churn_metrics["forest"]["auc"], 3)
    summary["A9"] = "异常报销单"
    summary["B9"] = f"{expense_metrics['anomalies']} 张 / {expense_metrics['ratio']:.1%}"
    for row in range(3, 10):
        summary.cell(row=row, column=1).font = Font(bold=True, color="1F3A5F")
        summary.cell(row=row, column=2).font = BODY_FONT
    summary.column_dimensions["A"].width = 24
    summary.column_dimensions["B"].width = 32

    # 销量预测：最近 12 个月实际 + 3 个月预测。
    monthly = orders.groupby(orders["下单日期"].dt.to_period("M"))["销售额"].sum()
    monthly.index = monthly.index.to_timestamp()
    actual = monthly.tail(12).reset_index()
    actual.columns = ["月份", "销售额"]
    actual["类型"] = "实际"
    future = forecast.rename(columns={"预测销售额": "销售额"})
    future["类型"] = "预测"
    path = pd.concat([actual, future], ignore_index=True)
    sheet = workbook.create_sheet("销量预测")
    style_title(sheet, "2026 年 Q1 销售额预测", 4)
    write_table(sheet, path, start_row=3)
    chart = LineChart()
    chart.title = "实际与预测销售额"
    chart.y_axis.title = "销售额（元）"
    chart.x_axis.title = "月份"
    data = Reference(sheet, min_col=2, min_row=3, max_row=3 + len(path))
    categories = Reference(sheet, min_col=1, min_row=4, max_row=3 + len(path))
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(categories)
    chart.height = 8
    chart.width = 18
    sheet.add_chart(chart, "F3")

    sheet = workbook.create_sheet("高价值客户")
    style_title(sheet, "高价值客户识别（按概率排序）", 6)
    top_value = high_value.sort_values("高价值概率", ascending=False).head(50)
    write_table(sheet, top_value, start_row=3)
    if len(top_value):
        probability_column = list(top_value.columns).index("高价值概率") + 1
        sheet.conditional_formatting.add(
            f"{get_column_letter(probability_column)}4:{get_column_letter(probability_column)}{3 + len(top_value)}",
            ColorScaleRule(start_type="num", start_value=0, start_color="FFFFFF", end_type="num", end_value=1, end_color="16A085"),
        )

    sheet = workbook.create_sheet("流失预警")
    style_title(sheet, "客户流失预警（按风险排序）", 6)
    top_churn = churn.head(50)
    write_table(sheet, top_churn, start_row=3)
    if len(top_churn):
        probability_column = list(top_churn.columns).index("流失概率") + 1
        sheet.conditional_formatting.add(
            f"{get_column_letter(probability_column)}4:{get_column_letter(probability_column)}{3 + len(top_churn)}",
            ColorScaleRule(start_type="num", start_value=0, start_color="FFFFFF", end_type="num", end_value=1, end_color="C0392B"),
        )

    sheet = workbook.create_sheet("客户分群")
    style_title(sheet, "K-Means 客户画像", 6)
    write_table(sheet, segments, start_row=3)

    sheet = workbook.create_sheet("异常报销")
    style_title(sheet, "孤立森林异常报销单", 7)
    write_table(sheet, anomalies.head(50), start_row=3)

    output = OUTPUT_DIR / "机器学习预测报表.xlsx"
    workbook.save(output)
    print(f"Excel 报表已生成：{output}")
    print(f"包含工作表：{workbook.sheetnames}")


if __name__ == "__main__":
    main()
