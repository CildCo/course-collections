"""深度学习课程共用工具：数据、模型、绘图和随机种子。"""
from __future__ import annotations

import json
import random
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
MODEL_DIR = ROOT / "models"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

NAVY = "#1F3A5F"
TEAL = "#16A085"
BLUE = "#2E86C1"
GOLD = "#D4AC0D"
RED = "#C0392B"
GRAY = "#7F8C8D"

POEMS = """
床前明月光，疑是地上霜。举头望明月，低头思故乡。
春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少。
白日依山尽，黄河入海流。欲穷千里目，更上一层楼。
红豆生南国，春来发几枝。愿君多采撷，此物最相思。
空山不见人，但闻人语响。返景入深林，复照青苔上。
独在异乡为异客，每逢佳节倍思亲。遥知兄弟登高处，遍插茱萸少一人。
渭城朝雨浥轻尘，客舍青青柳色新。劝君更尽一杯酒，西出阳关无故人。
朝辞白帝彩云间，千里江陵一日还。两岸猿声啼不住，轻舟已过万重山。
故人西辞黄鹤楼，烟花三月下扬州。孤帆远影碧空尽，唯见长江天际流。
月落乌啼霜满天，江枫渔火对愁眠。姑苏城外寒山寺，夜半钟声到客船。
远上寒山石径斜，白云生处有人家。停车坐爱枫林晚，霜叶红于二月花。
千山鸟飞绝，万径人踪灭。孤舟蓑笠翁，独钓寒江雪。
好雨知时节，当春乃发生。随风潜入夜，润物细无声。
会当凌绝顶，一览众山小。
国破山河在，城春草木深。感时花溅泪，恨别鸟惊心。
烽火连三月，家书抵万金。白头搔更短，浑欲不胜簪。
风急天高猿啸哀，渚清沙白鸟飞回。无边落木萧萧下，不尽长江滚滚来。
八月秋高风怒号，卷我屋上三重茅。
安得广厦千万间，大庇天下寒士俱欢颜。
山重水复疑无路，柳暗花明又一村。
纸上得来终觉浅，绝知此事要躬行。
横看成岭侧成峰，远近高低各不同。不识庐山真面目，只缘身在此山中。
竹外桃花三两枝，春江水暖鸭先知。
欲把西湖比西子，淡妆浓抹总相宜。
接天莲叶无穷碧，映日荷花别样红。
小荷才露尖尖角，早有蜻蜓立上头。
等闲识得东风面，万紫千红总是春。
问渠那得清如许，为有源头活水来。
昨夜西风凋碧树，独上高楼，望尽天涯路。
衣带渐宽终不悔，为伊消得人憔悴。
众里寻他千百度，蓦然回首，那人却在灯火阑珊处。
大江东去，浪淘尽，千古风流人物。
但愿人长久，千里共婵娟。
十年生死两茫茫，不思量，自难忘。
落霞与孤鹜齐飞，秋水共长天一色。
海上生明月，天涯共此时。
春江潮水连海平，海上明月共潮生。
不知细叶谁裁出，二月春风似剪刀。
野火烧不尽，春风吹又生。
谁言寸草心，报得三春晖。
两个黄鹂鸣翠柳，一行白鹭上青天。
窗含西岭千秋雪，门泊东吴万里船。
黄四娘家花满蹊，千朵万朵压枝低。
留连戏蝶时时舞，自在娇莺恰恰啼。
黑云翻墨未遮山，白雨跳珠乱入船。
卷地风来忽吹散，望湖楼下水如天。
毕竟西湖六月中，风光不与四时同。
泉眼无声惜细流，树阴照水爱晴柔。
梅子金黄杏子肥，麦花雪白菜花稀。
日长篱落无人过，惟有蜻蜓蛱蝶飞。
儿童散学归来早，忙趁东风放纸鸢。
草长莺飞二月天，拂堤杨柳醉春烟。
""".strip()


def set_seed(seed: int = 42) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def setup_plot() -> None:
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.dpi"] = 150
    plt.rcParams["savefig.bbox"] = "tight"
    plt.rcParams["figure.facecolor"] = "#F7FAFC"


def ensure_dirs() -> None:
    for path in (DATA_DIR, OUTPUT_DIR, MODEL_DIR):
        path.mkdir(parents=True, exist_ok=True)


def digits_tensors(test_size: float = 0.2):
    dataset = load_digits()
    images = dataset.images.astype("float32") / 16.0
    labels = dataset.target.astype("int64")
    x_train, x_test, y_train, y_test = train_test_split(
        images, labels, test_size=test_size, random_state=42, stratify=labels
    )
    x_train = torch.tensor(x_train).unsqueeze(1)
    x_test = torch.tensor(x_test).unsqueeze(1)
    y_train = torch.tensor(y_train)
    y_test = torch.tensor(y_test)
    return x_train, y_train, x_test, y_test


class SmallCNN(nn.Module):
    def __init__(self, num_classes: int = 10):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(32 * 2 * 2, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, num_classes),
        )

    def forward(self, x):
        return self.classifier(self.features(x))


def poetry_text() -> str:
    return "".join(POEMS.split())


def save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def accuracy(model, x, y) -> float:
    model.eval()
    with torch.no_grad():
        prediction = model(x.to(DEVICE)).argmax(dim=1).cpu()
    return float((prediction == y).float().mean())
