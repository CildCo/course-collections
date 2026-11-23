# 第6课示例数据与 Word 模板

from pathlib import Path

import pandas as pd
from docx import Document
from docx.shared import Pt
from PIL import Image, ImageDraw

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TEMPLATE_DIR = BASE_DIR / "templates"
ASSET_DIR = BASE_DIR / "assets"


def ensure_samples():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    ASSET_DIR.mkdir(parents=True, exist_ok=True)

    employees = pd.DataFrame(
        {
            "姓名": ["张三", "李四", "王五"],
            "身份证号": ["110101199001011000", "110101199002022000", "110101199003033000"],
            "部门": ["销售部", "技术部", "市场部"],
            "职位": ["销售专员", "Python 工程师", "市场助理"],
            "工资": [8000, 12000, 9000],
        }
    )
    employees.to_excel(DATA_DIR / "员工名单.xlsx", index=False)

    contract = Document()
    contract.add_heading("劳动合同", level=1)
    contract.add_paragraph("甲方：{{name}}")
    contract.add_paragraph("身份证号：{{id_card}}")
    contract.add_paragraph("入职部门：{{department}}")
    contract.add_paragraph("职位：{{position}}")
    contract.add_paragraph("薪资：{{salary}} 元")
    contract.add_paragraph("本合同自双方签字之日起生效。")
    contract.save(TEMPLATE_DIR / "合同模板.docx")

    offer = Document()
    offer.add_heading("录用通知书", level=1)
    offer.add_paragraph("{{name}} 先生/女士：")
    offer.add_paragraph("恭喜你通过面试，拟录用岗位为 {{position}}。")
    offer.add_paragraph("入职日期：{{date}}。")
    offer.add_paragraph("期待你的加入。")
    offer.save(TEMPLATE_DIR / "录用通知书.docx")

    handbook = Document()
    handbook.add_heading("员工手册", level=1)
    handbook.add_paragraph("员工姓名：{{name}}")
    handbook.add_paragraph("欢迎加入公司，请认真阅读本手册。")
    handbook.add_paragraph("第一章 考勤制度")
    handbook.add_paragraph("第二章 薪酬福利")
    handbook.save(TEMPLATE_DIR / "员工手册.docx")

    logo = Image.new("RGB", (240, 80), (47, 95, 224))
    draw = ImageDraw.Draw(logo)
    draw.text((24, 26), "MAHE  CODE", fill="white")
    logo.save(ASSET_DIR / "logo.png")

    print("示例 Word 模板已生成：", TEMPLATE_DIR)


if __name__ == "__main__":
    ensure_samples()
