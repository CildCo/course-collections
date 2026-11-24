# Python 深度学习零基础实战：从环境搭建到模型部署

这是《Python深度学习零基础实战：从环境搭建到模型部署》的配套源码。  
11 节课从张量、自动求导开始，依次完成 softmax、MLP、过拟合、CNN、迁移学习、RNN、LSTM 写诗、Word2Vec，最后把模型导出成 TorchScript 并用 Flask 提供预测接口。

课程使用 PyTorch，默认 CPU 也能跑通。手写数字数据使用 scikit-learn 自带的 8×8 digits，首次运行不需要下载 MNIST。

> 课程中的模型和预测结果仅用于学习，不构成生产环境承诺。

## 安装

```bash
cd deep-learning-zero/source
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

如果安装的是 CPU 版 PyTorch，可以用官方 CPU 源：

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

有 NVIDIA 显卡时，按 pytorch.org 的提示选择对应 CUDA 版本。

## 一键运行

```bash
python run_all.py
```

全部课程约 2-4 分钟（CPU）。图片和日志保存到 `output/`，TorchScript 模型保存到 `models/`。

## 逐课运行

```bash
python lesson01_environment/main.py
python lesson02_autograd/main.py
python lesson03_softmax/main.py
python lesson04_mlp/main.py
python lesson05_overfitting/main.py
python lesson06_cnn/main.py
python lesson07_transfer/main.py
python lesson08_rnn/main.py
python lesson09_lstm/main.py
python lesson10_word2vec/main.py
python lesson11_deploy/main.py
```

## 课次与输出

| 课次 | 目录 | 主要内容 | 输出 |
|---|---|---|---|
| 第1课 | `lesson01_environment/` | PyTorch/CUDA 检查、张量创建、运算、形状和设备 | `01_环境与张量.png` |
| 第2课 | `lesson02_autograd/` | backward、梯度下降、手写线性回归、nn.Linear | `02_自动求导.png` |
| 第3课 | `lesson03_softmax/` | softmax 回归、交叉熵、手写数字分类 | `03_softmax.png` |
| 第4课 | `lesson04_mlp/` | 隐藏层、ReLU、MLP 分类 | `04_MLP.png` |
| 第5课 | `lesson05_overfitting/` | 小数据大模型、Dropout、权重衰减 | `05_过拟合.png` |
| 第6课 | `lesson06_cnn/` | Conv2d、池化、特征图、CNN 分类 | `06_CNN.png` |
| 第7课 | `lesson07_transfer/` | 冻结卷积层、替换分类头、迁移学习 | `07_迁移学习.png` |
| 第8课 | `lesson08_rnn/` | RNN 隐藏状态、序列预测 | `08_RNN.png` |
| 第9课 | `lesson09_lstm/` | 字符级 LSTM、Temperature 采样、写诗 | `09_LSTM.png`、`09_LSTM.txt` |
| 第10课 | `lesson10_word2vec/` | Skip-gram、余弦相似度、词类比、PCA | `10_Word2Vec.png` |
| 第11课 | `lesson11_deploy/` | TorchScript 导出、Flask API、推理测试 | `11_部署.png`、`models/digit_cnn.pt` |

## 启动预测接口

先跑第 11 课生成模型，然后：

```bash
python deploy_app.py
```

访问 `http://127.0.0.1:5012/health`，预测接口：

```bash
curl -X POST http://127.0.0.1:5012/predict -H "Content-Type: application/json" -d "{\"pixels\": [0,0,8,12, ... 共 64 个数]}"
```

响应包含预测数字、置信度和 10 类概率。

## 目录说明

```text
deep-learning-zero/
├── collection.json
└── source/
    ├── common.py                 数据、SmallCNN、唐诗语料和绘图
    ├── run_all.py                一键运行
    ├── deploy_app.py             Flask 预测接口
    ├── requirements.txt
    └── lesson01_environment/     每课一个目录
        └── main.py
```

## 三个容易踩的坑

1. **数据和模型要在同一个设备**：`model.to(device)` 之后，输入也要 `.to(device)`。
2. **每次 backward 前清梯度**：训练三件套是 `optimizer.zero_grad()` → `loss.backward()` → `optimizer.step()`。
3. **部署要脱离训练代码**：用 TorchScript 保存计算图，线上只加载模型做推理，不在请求里训练。
