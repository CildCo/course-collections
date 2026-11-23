# 第8课：PDF 合并、拆分、提取与加密
# 运行：python main.py

import os
import re
from pathlib import Path

import pandas as pd
import pdfplumber
from PyPDF2 import PdfReader, PdfWriter

from make_samples import ensure_samples

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"


def merge_pdfs():
    """把月度报告合并成一个文件。"""
    folder = DATA_DIR / "月度报告"
    files = sorted(folder.glob("*.pdf"))
    writer = PdfWriter()
    for file in files:
        writer.append(str(file))
        print("已添加：", file.name)
    output = OUTPUT_DIR / "年度汇总报告.pdf"
    output.parent.mkdir(parents=True, exist_ok=True)
    writer.write(str(output))
    writer.close()
    print("合并完成：", output)


def split_pdf():
    """按章节拆分员工手册。"""
    reader = PdfReader(str(DATA_DIR / "员工手册.pdf"))
    chapters = {
        "01_总则": (0, 1),
        "02_考勤制度": (1, 2),
        "03_薪酬福利": (2, 3),
        "04_绩效考核": (3, 4),
        "05_附则": (4, 5),
    }
    target = OUTPUT_DIR / "拆分结果"
    target.mkdir(parents=True, exist_ok=True)

    for name, (start, end) in chapters.items():
        writer = PdfWriter()
        for page_number in range(start, end):
            writer.add_page(reader.pages[page_number])
        output = target / f"{name}.pdf"
        with open(output, "wb") as file:
            writer.write(file)
        print("已拆分：", output.name)


def extract_invoices():
    """从发票 PDF 中提取号码、日期、金额和销售方。"""
    folder = DATA_DIR / "发票PDF"
    rows = []
    for file in sorted(folder.glob("*.pdf")):
        with pdfplumber.open(file) as pdf:
            text = pdf.pages[0].extract_text() or ""

        number = re.search(r"发票号码[：:]\s*(\d+)", text)
        date = re.search(r"开票日期[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日)", text)
        amount = re.search(r"金额.*?[：:]\s*[^\d]*([\d,]+\.\d{2})", text)
        supplier = re.search(r"销售方[：:]\s*(.+?)(?:\n|$)", text)

        rows.append(
            {
                "文件名": file.name,
                "发票号码": number.group(1) if number else "未找到",
                "开票日期": date.group(1) if date else "未找到",
                "金额": amount.group(1) if amount else "0.00",
                "销售方": supplier.group(1).strip() if supplier else "未找到",
            }
        )
        print("已提取：", file.name)

    output = OUTPUT_DIR / "发票汇总.xlsx"
    pd.DataFrame(rows).to_excel(output, index=False)
    print("发票汇总：", output)
    return rows


def extract_tables():
    """提取产品目录里的表格。"""
    path = DATA_DIR / "产品目录" / "产品目录1.pdf"
    tables = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                if table:
                    tables.append(pd.DataFrame(table))

    if not tables:
        print("没有找到表格")
        return

    result = pd.concat(tables, ignore_index=True)
    output = OUTPUT_DIR / "产品价目表.xlsx"
    result.to_excel(output, index=False, header=False)
    print("表格已提取：", output)


def encrypt_pdf(password="123456"):
    """给 PDF 加密。"""
    reader = PdfReader(str(OUTPUT_DIR / "年度汇总报告.pdf"))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(password)
    output = OUTPUT_DIR / "年度汇总报告_加密版.pdf"
    with open(output, "wb") as file:
        writer.write(file)
    print("已加密：", output)


def decrypt_pdf(password="123456"):
    """解密刚才生成的加密 PDF。"""
    reader = PdfReader(str(OUTPUT_DIR / "年度汇总报告_加密版.pdf"))
    if reader.is_encrypted:
        reader.decrypt(password)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    output = OUTPUT_DIR / "年度汇总报告_解密版.pdf"
    with open(output, "wb") as file:
        writer.write(file)
    print("已解密：", output)


def process_invoices():
    """综合实战：提取发票、按月份合并。"""
    rows = []
    monthly = {}
    for file in sorted((DATA_DIR / "发票PDF").glob("*.pdf")):
        with pdfplumber.open(file) as pdf:
            text = pdf.pages[0].extract_text() or ""

        number = re.search(r"发票号码[：:]\s*(\d+)", text)
        date = re.search(r"开票日期[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日)", text)
        amount = re.search(r"金额.*?[：:]\s*[^\d]*([\d,]+\.\d{2})", text)
        supplier = re.search(r"销售方[：:]\s*(.+?)(?:\n|$)", text)

        month = "未知"
        if date:
            month_match = re.search(r"(\d{4}年\d{1,2}月)", date.group(1))
            if month_match:
                month = month_match.group(1)

        rows.append(
            {
                "文件名": file.name,
                "发票号码": number.group(1) if number else "N/A",
                "开票日期": date.group(1) if date else "N/A",
                "月份": month,
                "金额": amount.group(1) if amount else "0.00",
                "供应商": supplier.group(1).strip() if supplier else "N/A",
            }
        )
        monthly.setdefault(month, []).append(file)

    output_dir = OUTPUT_DIR / "发票处理结果"
    output_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_excel(output_dir / "发票汇总.xlsx", index=False)

    for month, files in monthly.items():
        writer = PdfWriter()
        for file in files:
            writer.append(str(file))
        safe_month = month.replace("年", "_").replace("月", "")
        output = output_dir / f"{safe_month}_发票合并.pdf"
        writer.write(str(output))
        writer.close()
        print("已合并：", output.name)


def main():
    ensure_samples()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    merge_pdfs()
    split_pdf()
    extract_invoices()
    extract_tables()
    encrypt_pdf()
    decrypt_pdf()
    process_invoices()


if __name__ == "__main__":
    main()
