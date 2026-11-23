# Python 驱动新能源车销售预测：从数据建模到智能决策

这是《Python 驱动新能源车销售预测：从数据建模到智能决策》的配套源码。  
6 节课从 9 年销量数据开始，依次完成清洗校验、市场复盘、特征工程、融合预测、Web 大屏和 2026 年经营决策。

课程默认使用本地生成的月度销量数据，断网也能跑通。数据模仿 2017-2026 年新能源乘用车的品牌与车型结构，不是任何机构的真实统计。

> 课程和预测结果仅用于学习，不构成投资或经营建议。

## 安装

```bash
cd 码袋子/content/collections/nev-sales-forecast/source
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

下载慢可以加镜像：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 一键运行

```bash
python run_all.py
```

脚本按第1课到第6课顺序执行，全部跑完约 30-60 秒。第一次运行会自动生成示例数据。

## 逐课运行

```bash
python lesson01_data_pipeline/main.py
python lesson02_market_dashboard/main.py
python lesson03_features/main.py
python lesson04_forecast/main.py
python lesson05_web_dashboard/main.py
python lesson06_decision/main.py
```

## 课次与输出

| 课次 | 目录 | 主要内容 | 主要输出 |
|---|---|---|---|
| 第1课 | `lesson01_data_pipeline/` | 2017-2026 月度销量、清洗、去重、校验 | `data/processed/cleaned_sales_data.csv`、`数据质量报告.txt` |
| 第2课 | `lesson02_market_dashboard/` | 年度趋势、品牌构成、车型和品牌排行 | `市场仪表盘.png` |
| 第3课 | `lesson03_features/` | 时间、滞后、滚动、增长率和品牌份额 | `features.csv`、`品牌份额.png` |
| 第4课 | `lesson04_forecast/` | 季节趋势模型、梯度提升、融合预测 | `forecast_2026.csv`、`预测趋势.png` |
| 第5课 | `lesson05_web_dashboard/` | 离线预测 + Flask API + ECharts 大屏 | `dashboard/index.html` |
| 第6课 | `lesson06_decision/` | 2026 全年预测、情景分析、季度节奏 | `2026决策报告.txt`、`决策总览.png` |

## 启动大屏

先跑完第 1-5 课，然后：

```bash
python dashboard_app.py
```

浏览器打开 <http://127.0.0.1:5000>。Flask 启动时一次性加载历史数据和预测结果，请求接口时不再训练模型。

可用接口：

- `/api/summary`：年度销量、预测总量、头部品牌
- `/api/yearly`：年度销量
- `/api/brands`：品牌累计销量
- `/api/models`：车型累计销量
- `/api/forecast`：2026 年 5-12 月分品牌预测

## 目录说明

```text
nev-sales-forecast/
├── collection.json
└── source/
    ├── common.py                 数据生成、清洗、聚合和配色
    ├── run_all.py                一键运行
    ├── dashboard_app.py          Flask 后端
    ├── requirements.txt
    └── lesson01_data_pipeline/   每课一个目录
        └── main.py
```

## 三个容易踩的坑

1. **时间序列不能随机切分**：训练集必须早于验证集，否则会偷看未来。
2. **滞后特征只能用过去**：`Lag_1`、`Rolling_Mean_3` 都要先 `shift(1)`，不能把当月销量算进去。
3. **预测不等于决策**：模型给出的是概率和区间，还要结合库存、产能、价格战和政策。

## 换成真实数据

示例数据是为了让所有人不配置账号也能跑通流程。接真实数据时，保持下面这些列：

```text
统计月份, 排名, 车型, 品牌/厂商, 销量
```

`统计月份` 用每月第一天，销量用整数。数据来源不同，先去重、统一单位和处理缺失，再运行 `run_all.py`。
