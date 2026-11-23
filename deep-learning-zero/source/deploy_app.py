"""模型部署示例：TorchScript + Flask API。

先运行第 11 课生成 models/digit_cnn.pt，再运行：
    python deploy_app.py
预测接口：
    POST /predict  {"pixels": [64 个 0-16 的数字]}
"""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import torch
from flask import Flask, jsonify, request

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "digit_cnn.pt"

app = Flask(__name__)
if not MODEL_PATH.exists():
    raise RuntimeError(f"模型不存在：{MODEL_PATH}，请先运行 lesson11_deploy/main.py")
# TorchScript 在 Windows 中文路径下读取会失败，先复制到临时 ASCII 路径再加载。
_temp_model = Path(tempfile.gettempdir()) / "digit_cnn_deploy.pt"
shutil.copy2(MODEL_PATH, _temp_model)
model = torch.jit.load(str(_temp_model), map_location="cpu")
model.eval()
_temp_model.unlink(missing_ok=True)


@app.route("/health")
def health():
    return jsonify({"ok": True, "model": MODEL_PATH.name})


@app.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json(silent=True) or {}
    pixels = payload.get("pixels")
    if not isinstance(pixels, list) or len(pixels) != 64:
        return jsonify({"error": "pixels 必须是 64 个数字"}), 400
    tensor = torch.tensor(pixels, dtype=torch.float32).reshape(1, 1, 8, 8) / 16.0
    with torch.no_grad():
        logits = model(tensor)[0]
        probabilities = torch.softmax(logits, dim=0)
    top = int(probabilities.argmax().item())
    return jsonify(
        {
            "digit": top,
            "confidence": round(float(probabilities[top]), 4),
            "probabilities": [round(float(value), 4) for value in probabilities],
        }
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5012, debug=False, use_reloader=False)
