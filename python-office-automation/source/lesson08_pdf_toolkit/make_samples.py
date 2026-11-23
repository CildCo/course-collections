# 第8课示例 PDF

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

FONT_PATH = Path("C:/Windows/Fonts/simhei.ttf")
if FONT_PATH.exists():
    pdfmetrics.registerFont(TTFont("SimHei", str(FONT_PATH)))
    FONT_NAME = "SimHei"
else:
    FONT_NAME = "Helvetica"


def simple_pdf(path: Path, pages, title):
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(path), pagesize=A4)
    for index in range(1, pages + 1):
        pdf.setFont(FONT_NAME, 18)
        pdf.drawString(72, 760, title)
        pdf.setFont(FONT_NAME, 12)
        pdf.drawString(72, 720, f"第 {index} 页 / 共 {pages} 页")
        pdf.drawString(72, 690, "这是用于 Python PDF 课程练习的示例文件。")
        pdf.showPage()
    pdf.save()


def invoice_pdf(path: Path, number, date, amount, supplier):
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(path), pagesize=A4)
    pdf.setFont(FONT_NAME, 18)
    pdf.drawString(72, 760, "增值税电子普通发票")
    pdf.setFont(FONT_NAME, 12)
    pdf.drawString(72, 710, f"发票号码：{number}")
    pdf.drawString(72, 680, f"开票日期：{date}")
    pdf.drawString(72, 650, f"金额：¥{amount}")
    pdf.drawString(72, 620, f"销售方：{supplier}")
    pdf.save()


def table_pdf(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(path), pagesize=A4)
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontName = FONT_NAME
    data = [
        ["产品", "单价", "库存"],
        ["手机", "3999", "120"],
        ["电脑", "6999", "60"],
        ["平板", "2599", "90"],
    ]
    table = Table(data)
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2F5FE0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.8, colors.grey),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]
        )
    )
    doc.build([Paragraph("产品目录", style), table])


def ensure_samples():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    simple_pdf(DATA_DIR / "月度报告" / "1月.pdf", 2, "1 月销售报告")
    simple_pdf(DATA_DIR / "月度报告" / "2月.pdf", 2, "2 月销售报告")
    simple_pdf(DATA_DIR / "员工手册.pdf", 5, "员工手册")

    invoice_pdf(DATA_DIR / "发票PDF" / "发票001.pdf", "10001", "2025年1月15日", "1,234.56", "北京甲公司")
    invoice_pdf(DATA_DIR / "发票PDF" / "发票002.pdf", "10002", "2025年1月20日", "2,345.67", "上海乙公司")
    invoice_pdf(DATA_DIR / "发票PDF" / "发票003.pdf", "10003", "2025年2月08日", "3,456.78", "广州丙公司")

    table_pdf(DATA_DIR / "产品目录" / "产品目录1.pdf")
    print("示例 PDF 已生成：", DATA_DIR)


if __name__ == "__main__":
    ensure_samples()
