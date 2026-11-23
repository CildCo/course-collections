# 第9课：无人值守日报
# 运行：python daily_report.py

import logging
import os
from datetime import datetime
from pathlib import Path

import pandas as pd

from make_samples import ensure_samples

BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)

logging.basicConfig(
    filename=BASE_DIR / "run_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)


def main():
    try:
        logging.info("=== 任务开始 ===")
        ensure_samples()

        source = BASE_DIR / "data" / "sales.xlsx"
        df = pd.read_excel(source)
        df["日期"] = pd.to_datetime(df["日期"])
        latest_date = df["日期"].max().strftime("%Y-%m-%d")
        today = df[df["日期"] == df["日期"].max()]

        summary = today.groupby("部门", as_index=False)["销售额"].sum()
        total = int(summary["销售额"].sum())

        output_dir = BASE_DIR / "output"
        output_dir.mkdir(exist_ok=True)
        output = output_dir / f"日报_{latest_date}.xlsx"
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            summary.to_excel(writer, sheet_name="部门汇总", index=False)
            pd.DataFrame(
                [{"日期": latest_date, "总销售额": total, "生成时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]
            ).to_excel(writer, sheet_name="总览", index=False)

        logging.info("日报已生成：%s，总销售额：%s", output, total)
        print("日报已生成：", output)
        print("总销售额：", total)
    except Exception as error:
        logging.error("任务执行失败：%s", error)
        print("任务执行失败：", error)
    finally:
        logging.info("=== 任务结束 ===")


if __name__ == "__main__":
    main()
