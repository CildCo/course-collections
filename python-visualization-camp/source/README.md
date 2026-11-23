# Python 办公自动化进阶：让数据说话 · 职场可视化实战营

这是《Python 办公自动化进阶：让数据说话—职场可视化实战营》的配套源码。  
8 节课按照“先选图、再美化、然后交互、最后做成报告”的顺序编排，每一课都能单独运行，也可以一键全部跑完。

所有示例数据都在运行时自动生成，不需要提前准备 Excel、CSV 或图片。

## 安装

```bash
cd 码袋子/content/collections/python-visualization-camp/source
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

如果下载慢，可以加清华源：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 一键运行

```bash
python run_all.py
```

脚本会按第1课到第8课的顺序执行，任何一课失败都会以非 0 状态退出。运行结束后，每课的 `output/` 目录里会生成对应的图片、Excel、PPT 或 HTML。

## 逐课运行

```bash
python lesson01_first_chart/main.py
python lesson02_excel_chart/main.py
python lesson03_seaborn/main.py
python lesson04_pyecharts/main.py
python lesson05_dual_axis/main.py
python lesson06_excel_ppt/main.py
python lesson07_visual_report/main.py
python lesson08_safety/main.py
```

## 课次与输出

| 课次 | 目录 | 主要内容 | 主要输出 |
|---|---|---|---|
| 第1课 | `lesson01_first_chart/` | 选图清单、环境检查、中文配置、销售趋势折线图 | `output/销售趋势图.png` |
| 第2课 | `lesson02_excel_chart/` | openpyxl 原生柱状图、折线图、颜色、标题、坐标轴、数据标签、网格线 | `output/高管销售图表.xlsx` |
| 第3课 | `lesson03_seaborn/` | 带置信区间的趋势图、渠道均值柱状图、部门绩效箱线图 | 3 张 PNG |
| 第4课 | `lesson04_pyecharts/` | 交互柱状图、时间轴动画、多系列折线图 | 3 个 HTML |
| 第5课 | `lesson05_dual_axis/` | 双 Y 轴图、2×2 经营仪表盘 | 2 张 PNG |
| 第6课 | `lesson06_excel_ppt/` | 图表插入 Excel、生成 PPT 标题页/图片页/备注；邮件和定时只打印说明 | `销售周报.xlsx`、`销售周报.pptx`、2 张 PNG |
| 第7课 | `lesson07_visual_report/` | 脏数据清洗、指标汇总、3 张图、Pyecharts 交互页、HTML 报告 | CSV、PNG、HTML |
| 第8课 | `lesson08_safety/` | 大数据采样、绝对路径、Agg 后端、画布释放、输出目录和文件名校验 | `output/采样散点图.png` |

### 第7课详细输出

```text
lesson07_visual_report/
├── data/
│   ├── raw_sales.csv          原始脏数据
│   └── cleaned_sales.csv      清洗后数据
└── output/
    ├── 月度趋势.png
    ├── 分公司对比.png
    ├── 月度热力图.png
    ├── interactive_charts.html
    └── 经营分析报告.html
```

`经营分析报告.html` 汇总了指标卡片、分公司明细、清洗记录和静态图，并通过 iframe 嵌入交互图表。直接在浏览器中打开即可。

## 目录说明

```text
python-visualization-camp/
├── collection.json
└── source/
    ├── common.py                公共字体、配色、目录和保存工具
    ├── lesson01_first_chart/
    ├── lesson02_excel_chart/
    ├── lesson03_seaborn/
    ├── lesson04_pyecharts/
    ├── lesson05_dual_axis/
    ├── lesson06_excel_ppt/
    ├── lesson07_visual_report/
    ├── lesson08_safety/
    ├── requirements.txt
    ├── run_all.py
    ├── README.md
    ├── LICENSE.md
    └── .gitignore
```

## 运行说明

- 绘图统一使用 Matplotlib 的 `Agg` 后端，只保存图片，不弹窗，也不会卡在 `plt.show()`。
- 每课的数据和输出都写在自己的 `data/`、`output/` 目录里，可以随时删除重跑。
- 随机数据都设置了固定种子，重复运行结果基本一致。
- 第4课和第7课的 HTML 图表使用 ECharts，脚本默认从公共 CDN 加载，浏览器首次打开时需要联网。
- 第6课不会真的发送邮件，也不会启动定时循环，只打印操作步骤。真正上线前请先人工检查附件和收件人。
- 第8课会主动尝试几个非法路径，这些情况会被拦截并打印“通过”，属于预期行为。
- 如果电脑没有中文字体，图表中的中文可能显示为方框；可在 `common.py` 的 `FONT_LIST` 中换成自己电脑已有的字体。

## 环境

- Python 3.11
- pandas、numpy、matplotlib、seaborn、openpyxl、python-pptx、pyecharts、Pillow
- 已在 Windows 11 下验证
