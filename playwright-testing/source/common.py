"""Playwright 课程共用工具：本地站点、浏览器和截图。"""
from __future__ import annotations

import atexit
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
BASE_URL = "http://127.0.0.1:5011"
_server_process = None


def ensure_server() -> None:
    """本地练习站没启动时自动拉起来。"""
    global _server_process
    try:
        with urllib.request.urlopen(BASE_URL + "/health", timeout=1) as response:
            if response.status == 200:
                return
    except Exception:
        pass
    _server_process = subprocess.Popen(
        [sys.executable, str(ROOT / "app.py")],
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(50):
        try:
            with urllib.request.urlopen(BASE_URL + "/health", timeout=1) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.2)
    raise RuntimeError("本地练习站启动失败：http://127.0.0.1:5011")


def stop_server() -> None:
    global _server_process
    if _server_process and _server_process.poll() is None:
        _server_process.terminate()
        _server_process = None


atexit.register(stop_server)


def launch(p):
    headless = os.environ.get("PLAYWRIGHT_HEADLESS", "1") != "0"
    browser = p.chromium.launch(headless=headless)
    context = browser.new_context(viewport={"width": 1280, "height": 800}, locale="zh-CN")
    return browser, context


def screenshot(page, name: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(OUTPUT_DIR / f"{name}.png"), full_page=True)
    print(f"截图：{OUTPUT_DIR / (name + '.png')}")


def goto(page, path: str = "/") -> None:
    page.goto(BASE_URL + path, wait_until="domcontentloaded")
