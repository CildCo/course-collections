# Python 量化实战：机器学习赋能黄金期货交易策略

这是《Python 量化实战：机器学习赋能黄金期货交易策略》的配套源码。  
9 节课从金价速览开始，依次完成数据管道、EDA、特征工程、时间序列模型、回测、报告和最终复盘。

课程默认使用本地生成的示例数据，断网也能跑通；示例数据模仿黄金、白银、铜、原油和豆粕的日线关系，不是真实行情。  
如果要换成真实数据，把 `data/raw/gold_pure_futures_final.csv` 替换成同字段的 CSV 即可，列名和日期索引保持不变。

> 课程只用于学习量化研究流程，不构成投资建议。期货有杠杆，回测结果不代表未来收益。

## 安装

```bash
cd 码袋子/content/collections/gold-quant-camp/source
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

脚本按第1课到第9课顺序执行，哪一课失败就停在哪一课。第一次运行会自动生成示例数据，全部跑完约 1—2 分钟。

## 逐课运行

```bash
python lesson01_gold_snapshot/main.py
python lesson02_workflow/main.py
python lesson03_data_pipeline/main.py
python lesson04_eda/main.py
python lesson05_features/main.py
python lesson06_model/main.py
python lesson07_backtest/main.py
python lesson08_report/main.py
python lesson09_review/main.py
```

## 课次与输出

| 课次 | 目录 | 主要内容 | 主要输出 |
|---|---|---|---|
| 第1课 | `lesson01_gold_snapshot/` | 金价速览、均线、近一年位置 | `output/金价速览.txt`、`金价走势.png` |
| 第2课 | `lesson02_workflow/` | 数据到策略的 8 步闭环、三分类样本分布 | `output/量化闭环说明.txt` |
| 第3课 | `lesson03_data_pipeline/` | 数据对齐、金银比、铜金比、油金比、RSI | `output/宏观因子.png`、`data/processed/gold_pipeline.csv` |
| 第4课 | `lesson04_eda/` | 价格、收益率分布、波动率、相关性热力图 | 3 张 PNG、`eda_statistics.csv` |
| 第5课 | `lesson05_features/` | 均线乖离、动量、通道、跨资产因子、三分类目标 | `gold_features.csv`、`三分类分布.png` |
| 第6课 | `lesson06_model/` | PurgedTimeSeriesSplit、RF/梯度提升对比、Walk-Forward | `predictions.csv`、混淆矩阵、特征重要性 |
| 第7课 | `lesson07_backtest/` | T+1 执行、手续费、滑点、动态仓位、资金曲线 | `策略总览.png`、`K线信号.png`、`trades.csv` |
| 第8课 | `lesson08_report/` | 胜率、盈亏比、最差交易、自动报告 | `黄金期货量化策略回测报告.txt`、`绩效卡片.png` |
| 第9课 | `lesson09_review/` | 收益对比、胜率陷阱、改进清单 | `最终复盘.txt`、`复盘对比.png` |

`data/raw/` 保存原始行情，`data/processed/` 保存中间表和模型结果，`output/` 保存图片、报告和文本。

## 目录说明

```text
gold-quant-camp/
├── collection.json
└── source/
    ├── common.py                 示例数据、指标、字体和路径
    ├── run_all.py                一键运行
    ├── requirements.txt
    └── lesson01_gold_snapshot/   每课一个目录
        └── main.py
```

## 三个容易踩的坑

1. **未来数据泄露**：训练集和验证集之间要留空窗期，回测信号要滞后一天。
2. **单位换算**：沪金是元/克，沪银是元/千克，算金银比时白银要乘 1000。
3. **只看胜率**：胜率高但盈亏比接近 1，手续费和滑点会把利润磨平，必须同时看回撤和资金曲线。

## 换成真实行情

示例数据是为了让所有人不配置账号也能跑通流程。需要真实数据时，先安装 akshare：

```bash
pip install akshare
python fetch_akshare.py
```

脚本会尝试拉取沪金主力、白银、铜、原油和豆粕，覆盖 `data/raw/gold_pure_futures_final.csv`。接口不可用时，继续用示例数据也能跑完整套流程。

也可以自己准备 CSV，保持下面这些列即可：

```text
date, open, high, low, close, volume, open_interest,
Silver_Close, Copper_Close, Oil_Close, Meal_Soybean_Close
```

`date` 设为索引，按交易日升序排列。数据源不同，字段单位和缺失处理要先核对，再跑 `run_all.py`。
