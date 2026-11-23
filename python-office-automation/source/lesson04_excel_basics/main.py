# 第4课：用 pandas 自动处理 Excel
# 运行：python main.py

from pathlib import Path

import pandas as pd

from make_samples import ensure_samples

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"


def read_and_raise():
    """读取员工表，给每个人涨薪 10%，另存新文件。"""
    df = pd.read_excel(DATA_DIR / "employees.xlsx")
    df["新工资"] = df["工资"] * 1.1
    output = OUTPUT_DIR / "员工信息_涨薪版.xlsx"
    df.to_excel(output, index=False)
    print("已生成：", output)
    print(df[["姓名", "工资", "新工资"]].to_string(index=False))


def filter_sales():
    """筛选销售部且工资大于 7800 的员工。"""
    df = pd.read_excel(DATA_DIR / "sales.xlsx")
    result = df[(df["部门"] == "销售部") & (df["工资"] > 7800)]
    print("\n销售部且工资 > 7800：")
    print(result.to_string(index=False))


def clean_data():
    """清洗空格、手机号横杠、空姓名和空备注。"""
    df = pd.read_excel(DATA_DIR / "dirty.xlsx")
    df["姓名"] = df["姓名"].str.strip()
    df["手机号"] = df["手机号"].str.replace("-", "", regex=False)
    df = df.dropna(subset=["姓名"])
    df["备注"] = df["备注"].fillna("未知")
    output = OUTPUT_DIR / "清洗后的数据.xlsx"
    df.to_excel(output, index=False)
    print("\n清洗后的数据：")
    print(df.to_string(index=False))


def group_salary():
    """按部门统计平均工资。"""
    df = pd.read_excel(DATA_DIR / "sales.xlsx")
    result = df.groupby("部门")["工资"].mean().reset_index()
    output = OUTPUT_DIR / "部门薪资报告.xlsx"
    result.to_excel(output, index=False)
    print("\n部门平均工资：")
    print(result.to_string(index=False))


def merge_tables():
    """按姓名合并员工名单和工资表，类似 VLOOKUP。"""
    names = pd.read_excel(DATA_DIR / "员工名单.xlsx")
    salaries = pd.read_excel(DATA_DIR / "工资表.xlsx")
    result = pd.merge(names, salaries, on="姓名", how="left")
    result["月薪"] = result["月薪"].fillna("未提供")
    output = OUTPUT_DIR / "员工薪资合并.xlsx"
    result.to_excel(output, index=False)
    print("\n合并后的员工薪资：")
    print(result.to_string(index=False))


def combine_monthly():
    """合并多个结构相同的分表，并标记来源月份。"""
    rows = []
    for file in sorted((DATA_DIR / "monthly").glob("*.xlsx")):
        df = pd.read_excel(file)
        df["月份"] = file.stem
        rows.append(df)
    result = pd.concat(rows, ignore_index=True)
    output = OUTPUT_DIR / "全年汇总.xlsx"
    result.to_excel(output, index=False)
    print("\n全年汇总：")
    print(result.to_string(index=False))


def main():
    ensure_samples()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    read_and_raise()
    filter_sales()
    clean_data()
    group_salary()
    merge_tables()
    combine_monthly()


if __name__ == "__main__":
    main()
