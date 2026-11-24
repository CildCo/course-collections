# Python 办公自动化入门课 · 配套源码

这套代码按课程顺序整理，每一课都是一个可以单独运行的小项目。  
示例数据会在第一次运行时自动生成，不需要手动准备 Excel、Word 或 PDF。

## 安装

```bash
cd python-office-automation/source
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

如果你的电脑已经装了 Python，也可以直接用：

```bash
pip install -r requirements.txt
```

## 课次与代码

| 课次 | 目录 | 内容 |
|---|---|---|
| 第1课 | `lesson01_intro/` | 变量、列表、循环、判断、工资计算器 |
| 第2课 | `lesson02_data_structures/` | 列表、字典、列表套字典、客户消费统计 |
| 第3课 | `lesson03_functions_classes/` | 循环、函数、类、自动化薪资结算 |
| 第4课 | `lesson04_excel_basics/` | pandas 读写 Excel、筛选、清洗、分组、合并 |
| 第5课 | `lesson05_excel_report/` | 透视表、增长率、openpyxl 美化、柱状图 |
| 第6课 | `lesson06_word_automation/` | python-docx 读文档、批量合同、格式、表格、入职礼包 |
| 第7课 | `lesson07_file_organizer/` | os / shutil 批量重命名、分类、清理、备份、归档 |
| 第8课 | `lesson08_pdf_toolkit/` | PDF 合并、拆分、发票提取、表格提取、加密解密 |
| 第9课 | `lesson09_scheduled_task/` | 日报脚本、日志、Windows 任务计划程序 |

> 课程中的“安装 Python”那一课没有独立项目，安装步骤见课程正文；这里从第1课的基础语法开始。

## 一键运行全部

```bash
python run_all.py
```

它会按第1课到第9课的顺序运行，并在每一步打印结果。如果想单独调试，再用下面的逐课命令。

## 逐课运行

```bash
python lesson01_intro/main.py
python lesson02_data_structures/main.py
python lesson03_functions_classes/main.py
python lesson04_excel_basics/main.py
python lesson05_excel_report/main.py
python lesson06_word_automation/main.py
python lesson07_file_organizer/main.py
python lesson08_pdf_toolkit/main.py
python lesson09_scheduled_task/daily_report.py
```

每个目录里的 `data/`、`output/`、`templates/` 都是运行时生成的，可以随时删除重跑。

## 目录说明

```
python-office-automation/
├── lesson01_intro/
├── lesson02_data_structures/
├── lesson03_functions_classes/
├── lesson04_excel_basics/
│   ├── make_samples.py      生成示例 Excel
│   └── main.py
├── lesson05_excel_report/
│   ├── make_samples.py      生成销售数据
│   └── main.py
├── lesson06_word_automation/
│   ├── make_samples.py      生成 Word 模板和员工数据
│   └── main.py
├── lesson07_file_organizer/
│   ├── make_samples.py      生成可安全练习的文件目录
│   └── main.py
├── lesson08_pdf_toolkit/
│   ├── make_samples.py      生成示例 PDF
│   └── main.py
├── lesson09_scheduled_task/
│   ├── make_samples.py
│   ├── daily_report.py
│   ├── run_task.bat
│   └── README.md
├── requirements.txt
├── LICENSE.md
└── README.md
```

## 说明

- 代码注释只保留关键步骤，尽量简单直白。
- 所有文件操作都限制在项目自己的 `workspace/`、`data/`、`output/` 目录，不会碰电脑上的其他文件。
- PDF 课程处理的是文字版 PDF；扫描版需要额外接 OCR。
- 第9课的 `run_task.bat` 里路径是占位符，使用前改成你自己的实际路径。
- 如果 Windows 没有中文字体，PDF 示例可能显示方框；脚本会优先使用 `C:/Windows/Fonts/simhei.ttf`。
