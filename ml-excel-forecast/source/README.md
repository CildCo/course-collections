# Python 机器学习：让 Excel 拥有“预测未来”的大脑

这是《Python机器学习：让Excel拥有“预测未来”的大脑》的配套源码。  
9 节课从合并 36 份月度报表开始，依次完成清洗、特征工程、销量预测、客户分类、流失预警、客户分群、异常报销检测、模型持久化和 Excel 自动回填。

课程默认在本地生成订单、客户和报销单示例数据，断网也能跑通。数据只用于演示机器学习流程，不代表任何真实企业。

> 课程中的预测和客户结论均为示例，不构成经营或投资建议。

## 安装

```bash
cd ml-excel-forecast/source
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

第一次运行会生成 2023-2025 年 36 份月度 Excel 和一份报销单。全部跑完约 20-40 秒。

## 逐课运行

```bash
python lesson01_merge_clean/main.py
python lesson02_features_visual/main.py
python lesson03_linear_regression/main.py
python lesson04_logistic_customer/main.py
python lesson05_churn_forest/main.py
python lesson06_kmeans_segment/main.py
python lesson07_isolation_forest/main.py
python lesson08_model_persistence/main.py
python lesson09_excel_report/main.py
```

## 课次与输出

| 课次 | 目录 | 主要内容 | 主要输出 |
|---|---|---|---|
| 第1课 | `lesson01_merge_clean/` | 合并 36 份月度报表、去重、补全、校验 | `orders_merged.csv`、`全年汇总数据.xlsx` |
| 第2课 | `lesson02_features_visual/` | 季度、月份、周末特征和四张分析图 | `销售分析仪表盘.png` |
| 第3课 | `lesson03_linear_regression/` | 线性回归预测 2026 年 Q1 销售额 | `sales_forecast.csv`、`销量预测.png` |
| 第4课 | `lesson04_logistic_customer/` | RFM 特征 + 逻辑回归识别高价值客户 | `high_value_predictions.csv`、`高价值客户.png` |
| 第5课 | `lesson05_churn_forest/` | 决策树 vs 随机森林，客户流失预警 | `churn_predictions.csv`、`客户流失预警.png` |
| 第6课 | `lesson06_kmeans_segment/` | 轮廓系数选 k，K-Means 客户分群 | `customer_segments.csv`、`客户分群.png` |
| 第7课 | `lesson07_isolation_forest/` | 孤立森林检测异常报销单 | `expense_anomalies.csv`、`异常报销检测.png` |
| 第8课 | `lesson08_model_persistence/` | joblib 保存模型、重新加载、版本元数据 | `models/churn_model.joblib`、`模型持久化说明.txt` |
| 第9课 | `lesson09_excel_report/` | 预测结果、客户名单和异常单自动回填 Excel | `机器学习预测报表.xlsx` |

## 目录说明

```text
ml-excel-forecast/
├── collection.json
└── source/
    ├── common.py                 数据生成、清洗、RFM 特征和配色
    ├── run_all.py                一键运行
    ├── requirements.txt
    └── lesson01_merge_clean/     每课一个目录
        └── main.py
```

`data/raw/monthly/` 是 36 份月度 Excel，`data/processed/` 是清洗后的表和模型结果，`models/` 保存训练好的模型，`output/` 保存图片和最终报表。

## 三个容易踩的坑

1. **先清洗再建模**：重复订单、负销售额和空日期会直接让模型报错或失真。
2. **特征不能偷看未来**：销量预测里的滞后和滚动特征只能用历史月份。
3. **模型文件要管版本**：joblib 加载时特征顺序必须和训练时一致，模型更新后要重新校验。

## 换成自己的 Excel

把 `data/raw/monthly/` 里的文件替换成你自己的月度报表，保持表头包含：

```text
订单编号, 下单日期, 客户ID, 客户名称, 地区, 产品类别, 数量, 单价, 销售额
```

然后删除 `data/processed/` 和 `output/`，重新运行 `run_all.py`。真实业务数据要先脱敏，再用于课程练习。
