# 第4课示例数据
# 首次运行 main.py 会自动调用这里生成 Excel 文件。

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def ensure_samples():
    """生成课程练习用的 Excel 文件。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    monthly_dir = DATA_DIR / "monthly"
    monthly_dir.mkdir(parents=True, exist_ok=True)

    employees = pd.DataFrame(
        {
            "序号": [1, 2, 3, 4],
            "姓名": ["张三", "李四", "王五", "赵六"],
            "部门": ["销售部", "技术部", "销售部", "行政部"],
            "工资": [8000, 12000, 7500, 6000],
            "入职日期": ["2021-01-01", "2020-05-15", "2022-03-10", "2021-11-20"],
        }
    )
    employees.to_excel(DATA_DIR / "employees.xlsx", index=False)

    sales = pd.DataFrame(
        {
            "姓名": ["张三", "李四", "王五", "赵六", "张三", "李四"],
            "部门": ["销售部", "技术部", "销售部", "行政部", "销售部", "技术部"],
            "工资": [8000, 12000, 7500, 6000, 8200, 12500],
        }
    )
    sales.to_excel(DATA_DIR / "sales.xlsx", index=False)

    dirty = pd.DataFrame(
        {
            "姓名": ["  张三  ", "李四", "王五", None],
            "手机号": ["138-0000-0000", "139-1111-1111", "137-2222-2222", "136-3333-3333"],
            "备注": ["正常", None, "试用", "离职"],
        }
    )
    dirty.to_excel(DATA_DIR / "dirty.xlsx", index=False)

    names = pd.DataFrame(
        {
            "姓名": ["张三", "李四", "王五", "赵六"],
            "部门": ["销售部", "技术部", "市场部", "行政部"],
        }
    )
    names.to_excel(DATA_DIR / "员工名单.xlsx", index=False)

    salary_table = pd.DataFrame(
        {
            "姓名": ["张三", "李四", "赵六"],
            "月薪": [8000, 12000, 6000],
        }
    )
    salary_table.to_excel(DATA_DIR / "工资表.xlsx", index=False)

    january = pd.DataFrame({"姓名": ["刘备", "关羽"], "销售额": [5000, 8000]})
    february = pd.DataFrame({"姓名": ["张飞", "赵云"], "销售额": [6000, 9000]})
    january.to_excel(monthly_dir / "1月.xlsx", index=False)
    february.to_excel(monthly_dir / "2月.xlsx", index=False)

    print("示例 Excel 已生成：", DATA_DIR)
