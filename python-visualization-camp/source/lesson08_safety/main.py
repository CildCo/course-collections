# 第8课：避坑与安全，别让图表脚本把你坑了
# 运行：python main.py

import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR.parent))

import matplotlib
import numpy as np
import pandas as pd

from common import COLORS, data_dir, output_dir, plt, save_figure, setup_chinese_font, style_axes

OUTPUT_DIR = output_dir(BASE_DIR)
DATA_DIR = data_dir(BASE_DIR)
ALLOWED_SUFFIXES = {".png", ".jpg", ".jpeg", ".csv", ".html", ".xlsx"}
BAD_CHARS = set('<>:"/\\|?*')
CHECKS = []


def check(label, condition, detail=""):
    """记录并打印一条检查结果。"""
    ok = bool(condition)
    CHECKS.append(ok)
    line = f"[{'通过' if ok else '失败'}] {label}"
    if detail:
        line += f"：{detail}"
    print(line)
    return ok


def safe_output_path(filename):
    """只允许在本课 output 目录下写入白名单类型的文件。"""
    if not filename or filename in {".", ".."}:
        raise ValueError("文件名为空或非法")
    if Path(filename).is_absolute():
        raise ValueError("不允许使用绝对路径")
    if ".." in filename or any(char in filename for char in BAD_CHARS):
        raise ValueError("文件名包含路径分隔符或非法字符")
    if Path(filename).name != filename:
        raise ValueError("只允许写在 output 根目录，不能带子目录")
    if Path(filename).suffix.lower() not in ALLOWED_SUFFIXES:
        raise ValueError("文件类型不在白名单内")

    target = (OUTPUT_DIR / filename).resolve()
    if target.parent != OUTPUT_DIR.resolve():
        raise ValueError("目标路径超出 output 目录")
    return target


def ensure_output_dir(path):
    """确认目录位于本课 output 下，再创建。"""
    target = Path(path).resolve()
    root = OUTPUT_DIR.resolve()
    if target != root and root not in target.parents:
        raise ValueError("目录不在本课 output 下")
    target.mkdir(parents=True, exist_ok=True)
    return target


def make_big_data(rows=120_000):
    """模拟一张十万行级别的明细表。"""
    rng = np.random.default_rng(8)
    ad_spend = rng.normal(50, 12, rows)
    sales = 0.8 * ad_spend + rng.normal(0, 16, rows) + 20
    times = pd.date_range("2026-01-01", periods=rows, freq="min")
    return pd.DataFrame({"时间": times, "广告投入": ad_spend, "销售额": sales})


def sample_and_plot(df, path):
    """先采样再画图，避免几十万个点把内存和界面拖垮。"""
    start = time.perf_counter()
    sample = df.sample(n=5000, random_state=42)
    sample_seconds = time.perf_counter() - start

    step = max(1, len(df) // 5000)
    even_sample = df.iloc[::step]
    sample.to_csv(DATA_DIR / "big_data_sample.csv", index=False, encoding="utf-8-sig")

    setup_chinese_font()
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=190)
    ax.scatter(
        sample["广告投入"],
        sample["销售额"],
        s=9,
        alpha=0.35,
        color=COLORS["blue"],
        edgecolors="none",
    )
    ax.set_title(
        f"采样后的散点图（{len(sample):,} / {len(df):,} 行）",
        fontsize=16,
        fontweight="bold",
        pad=14,
    )
    ax.set_xlabel("广告投入（万元）")
    ax.set_ylabel("销售额（万元）")
    style_axes(ax, grid_axis="both")
    save_figure(fig, path)

    print(f"随机采样：{len(sample):,} 行，用时 {sample_seconds * 1000:.1f} 毫秒")
    print(f"等间距采样：每 {step} 行取 1 行，共 {len(even_sample):,} 行")
    print("全量数据只参与统计，不直接绘制，避免长时间卡顿。")
    return sample, even_sample


def main():
    print("=" * 60)
    print("第8课：避坑与安全机制")
    print("=" * 60)

    # 1. 后端检查：服务器和定时任务里不能弹窗
    backend = matplotlib.get_backend()
    check("Agg 无界面后端", backend.lower() == "agg", f"当前后端 {backend}")

    # 2. 绝对路径：所有读写都从脚本位置出发
    script_path = Path(__file__).resolve()
    check("使用绝对路径", script_path.is_absolute() and OUTPUT_DIR.is_absolute(), str(OUTPUT_DIR))

    # 3. 输出目录校验：只能写本课 output
    try:
        ensure_output_dir(OUTPUT_DIR / "charts")
        check("output 子目录可创建", True, "output/charts")
    except ValueError as exc:
        check("output 子目录可创建", False, str(exc))

    outside = BASE_DIR.parent / "outside_output"
    try:
        ensure_output_dir(outside)
        check("拦截 output 之外的目录", False, "不应创建该目录")
    except ValueError as exc:
        check("拦截 output 之外的目录", True, str(exc))

    # 4. 非法文件名和路径拦截
    cases = [
        ("正常图片名", "采样散点图.png", True),
        ("上级目录逃逸", "../逃逸.png", False),
        ("绝对路径", r"C:\Windows\evil.png", False),
        ("非法扩展名", "report.exe", False),
        ("带子目录", "sub/chart.png", False),
        ("通配符", "data?.png", False),
    ]
    for label, filename, should_pass in cases:
        try:
            target = safe_output_path(filename)
            passed = True
            detail = str(target)
        except ValueError as exc:
            passed = False
            detail = str(exc)
        check(label, passed == should_pass, detail)

    # 5. 大数据采样
    print("\n生成 120,000 行模拟数据...")
    big_df = make_big_data()
    print(f"数据规模：{len(big_df):,} 行 × {len(big_df.columns)} 列")
    image_path = safe_output_path("采样散点图.png")
    sample, even_sample = sample_and_plot(big_df, image_path)
    check("采样后数据量可控", len(sample) == 5000 and len(even_sample) <= 5001, f"{len(sample):,} / {len(even_sample):,}")

    # 6. 画完关闭画布，释放内存
    plt.close("all")
    check("画布已全部关闭", len(plt.get_fignums()) == 0, f"当前画布数 {len(plt.get_fignums())}")

    # 7. 汇总
    failed = CHECKS.count(False)
    print("\n" + "-" * 60)
    print(f"检查完成：{len(CHECKS)} 项，通过 {len(CHECKS) - failed} 项，失败 {failed} 项")
    print(f"示例图片：{image_path}")
    print("-" * 60)

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
