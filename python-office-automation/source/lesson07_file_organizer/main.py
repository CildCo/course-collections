# 第7课：文件批量整理
# 运行：python main.py

import os
import shutil
from datetime import datetime
from pathlib import Path

from make_samples import WORKSPACE, ensure_samples

BASE_DIR = Path(__file__).resolve().parent


def list_files():
    """列出课程目录里的文件。"""
    files = os.listdir(BASE_DIR)
    print("当前目录：", BASE_DIR)
    print("文件数量：", len(files))
    excel_files = [name for name in files if name.endswith(".xlsx")]
    print("Excel 文件：", excel_files)


def walk_pdfs():
    """递归查找所有 PDF。"""
    target = WORKSPACE / "项目资料"
    for root, dirs, files in os.walk(target):
        for name in files:
            if name.endswith(".pdf"):
                print("发现 PDF：", os.path.join(root, name))


def batch_rename():
    """给照片加日期前缀；先预览，不直接改名。"""
    folder = WORKSPACE / "照片备份"
    prefix = "20231027_"
    files = [name for name in os.listdir(folder) if name.endswith(".jpg")]

    for filename in files:
        if filename.startswith(prefix):
            continue
        old_path = folder / filename
        new_path = folder / f"{prefix}{filename}"
        print(f"预览重命名：{filename} -> {new_path.name}")


def classify_downloads():
    """按扩展名把下载目录里的文件移到分类文件夹。"""
    source = WORKSPACE / "Downloads"
    rules = {
        ".pdf": "文档",
        ".docx": "文档",
        ".jpg": "图片",
        ".png": "图片",
        ".exe": "安装包",
        ".zip": "压缩包",
    }

    for filename in os.listdir(source):
        file_path = source / filename
        if file_path.is_dir():
            continue
        ext = file_path.suffix.lower()
        if ext not in rules:
            continue
        target_dir = source / rules[ext]
        target_dir.mkdir(exist_ok=True)
        shutil.move(str(file_path), str(target_dir / filename))
        print(f"已移动：{filename} -> {rules[ext]}")


def clean_temp(dry_run=True):
    """清理 .tmp 文件；默认只预览。"""
    folder = WORKSPACE / "临时缓存"
    count = 0
    for filename in os.listdir(folder):
        file_path = folder / filename
        if file_path.is_dir() or not filename.endswith(".tmp"):
            continue
        if dry_run:
            print("准备删除：", filename)
        else:
            file_path.unlink()
            print("已删除：", filename)
        count += 1
    print(f"共 {count} 个临时文件" + ("（预览）" if dry_run else "（已删除）"))


def backup_folder():
    """复制整个项目资料文件夹作为备份。"""
    source = WORKSPACE / "项目资料"
    backup = WORKSPACE / "Backup" / "项目资料_备份版"
    if backup.exists():
        shutil.rmtree(backup)
    shutil.copytree(source, backup)
    print("备份完成：", backup)


def auto_archive_project(project_path, dry_run=False):
    """综合实战：文档复制、图片移动、垃圾清理、生成日志。"""
    project_path = Path(project_path)
    doc_backup = project_path / "01_文档备份"
    img_folder = project_path / "02_图片素材"
    doc_backup.mkdir(parents=True, exist_ok=True)
    img_folder.mkdir(parents=True, exist_ok=True)

    log = [f"=== 归档时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n"]
    count_doc = count_img = count_del = 0

    for file_path in list(project_path.iterdir()):
        if file_path.is_dir():
            continue
        name = file_path.name

        if name.endswith((".xlsx", ".docx")) and not name.startswith("~$"):
            if dry_run:
                print("准备复制：", name)
            else:
                shutil.copy(file_path, doc_backup / name)
            log.append(f"[复制] {name} -> 文档备份")
            count_doc += 1
        elif name.endswith((".jpg", ".png", ".jpeg")):
            if dry_run:
                print("准备移动：", name)
            else:
                shutil.move(str(file_path), str(img_folder / name))
            log.append(f"[移动] {name} -> 图片素材")
            count_img += 1
        elif name.endswith(".tmp") or name.startswith("~$"):
            if dry_run:
                print("准备删除：", name)
            else:
                file_path.unlink()
            log.append(f"[删除] {name}（垃圾文件）")
            count_del += 1

    log.append("\n=== 统计 ===")
    log.append(f"文档备份：{count_doc} 个")
    log.append(f"图片归档：{count_img} 个")
    log.append(f"垃圾清理：{count_del} 个")

    log_file = project_path / "归档日志.txt"
    log_file.write_text("\n".join(log), encoding="utf-8")
    print("归档完成，日志：", log_file)


def main():
    ensure_samples()
    list_files()
    print("\n--- 递归查找 PDF ---")
    walk_pdfs()
    print("\n--- 批量重命名预览 ---")
    batch_rename()
    print("\n--- 下载目录分类 ---")
    classify_downloads()
    print("\n--- 临时文件清理预览 ---")
    clean_temp(dry_run=True)
    print("\n--- 文件夹备份 ---")
    backup_folder()
    print("\n--- 项目自动归档 ---")
    auto_archive_project(WORKSPACE / "我的测试项目", dry_run=False)


if __name__ == "__main__":
    main()
