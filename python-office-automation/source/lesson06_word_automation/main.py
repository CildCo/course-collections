# 第6课：Word 自动化
# 运行：python main.py

from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

from make_samples import ensure_samples

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TEMPLATE_DIR = BASE_DIR / "templates"
ASSET_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output"


def replace_text(paragraph, values):
    """替换段落中的 {{key}} 占位符。"""
    text = paragraph.text
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", str(value))
    if text != paragraph.text:
        paragraph.text = text


def replace_in_document(doc, values):
    """同时处理正文段落和表格。"""
    for paragraph in doc.paragraphs:
        replace_text(paragraph, values)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    replace_text(paragraph, values)


def read_document():
    """读取模板并打印段落。"""
    doc = Document(TEMPLATE_DIR / "合同模板.docx")
    print("模板内容：")
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            print(" ", paragraph.text)


def create_document():
    """从零创建一个项目总结。"""
    doc = Document()
    doc.add_heading("2026 年度项目总结报告", level=0)
    doc.add_paragraph("本项目由技术部主导，历时三个月，完成了所有既定目标。")
    doc.add_paragraph("主要成果：", style="List Bullet")
    doc.add_paragraph("上线了新版 App", style="List Bullet")
    doc.add_paragraph("用户增长 50%", style="List Bullet")
    output = OUTPUT_DIR / "项目总结_初稿.docx"
    doc.save(output)
    print("已生成：", output)


def batch_contracts():
    """读取 Excel，批量生成劳动合同。"""
    df = pd.read_excel(DATA_DIR / "员工名单.xlsx")
    target = OUTPUT_DIR / "生成的合同"
    target.mkdir(parents=True, exist_ok=True)

    for _, row in df.iterrows():
        doc = Document(TEMPLATE_DIR / "合同模板.docx")
        replace_in_document(
            doc,
            {
                "name": row["姓名"],
                "id_card": row["身份证号"],
                "department": row["部门"],
                "position": row["职位"],
                "salary": row["工资"],
            },
        )
        file_name = target / f"{row['姓名']}_劳动合同.docx"
        doc.save(file_name)
        print("已生成：", file_name.name)


def format_document():
    """统一字体、标题样式，并插入 logo。"""
    doc = Document(OUTPUT_DIR / "项目总结_初稿.docx")

    normal = doc.styles["Normal"]
    normal.font.name = "微软雅黑"
    normal.font.size = Pt(12)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")

    for paragraph in doc.paragraphs:
        if paragraph.style.name.startswith("Heading"):
            for run in paragraph.runs:
                run.font.bold = True
                run.font.color.rgb = RGBColor(0x2F, 0x5F, 0xE0)

    logo = ASSET_DIR / "logo.png"
    if logo.exists():
        doc.add_picture(str(logo), width=Inches(1.3))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    output = OUTPUT_DIR / "项目总结_正式.docx"
    doc.save(output)
    print("已美化：", output)


def create_salary_table():
    """在 Word 里创建薪资明细表。"""
    doc = Document()
    doc.add_heading("薪资明细单", level=1)
    table = doc.add_table(rows=4, cols=3)
    table.style = "Table Grid"

    headers = ["月份", "基本工资", "绩效"]
    for index, value in enumerate(headers):
        table.rows[0].cells[index].text = value

    data = [("1月", "5000", "1000"), ("2月", "5000", "1200"), ("3月", "5000", "1500")]
    for row_index, values in enumerate(data, 1):
        for col_index, value in enumerate(values):
            table.rows[row_index].cells[col_index].text = value

    output = OUTPUT_DIR / "薪资明细表.docx"
    doc.save(output)
    print("已生成：", output)


def onboarding_kit():
    """为每位新员工生成入职大礼包。"""
    df = pd.read_excel(DATA_DIR / "员工名单.xlsx")
    target = OUTPUT_DIR / "入职大礼包"
    target.mkdir(parents=True, exist_ok=True)

    for _, row in df.iterrows():
        name = row["姓名"]
        user_folder = target / name
        user_folder.mkdir(parents=True, exist_ok=True)

        offer = Document(TEMPLATE_DIR / "录用通知书.docx")
        replace_in_document(
            offer,
            {
                "name": name,
                "position": row["职位"],
                "date": "2026-11-01",
            },
        )
        offer.save(user_folder / f"{name}_录用通知书.docx")

        handbook = Document(TEMPLATE_DIR / "员工手册.docx")
        replace_in_document(handbook, {"name": name})
        handbook.save(user_folder / f"{name}_员工手册.docx")

        print(f"{name} 的入职大礼包已生成")


def main():
    ensure_samples()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    read_document()
    create_document()
    batch_contracts()
    format_document()
    create_salary_table()
    onboarding_kit()


if __name__ == "__main__":
    main()
