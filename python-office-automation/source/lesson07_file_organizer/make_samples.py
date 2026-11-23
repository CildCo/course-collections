# 第7课示例文件

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
WORKSPACE = BASE_DIR / "workspace"


def touch(path: Path, text: str = "示例文件"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def ensure_samples():
    """生成一个可以安全练习的文件夹。"""
    downloads = WORKSPACE / "Downloads"
    photos = WORKSPACE / "照片备份"
    temp = WORKSPACE / "临时缓存"
    project = WORKSPACE / "我的测试项目"
    materials = WORKSPACE / "项目资料"

    for filename in ["报告.pdf", "图片.jpg", "安装包.exe", "资料.zip", "说明.txt"]:
        touch(downloads / filename)
    touch(downloads / "临时.tmp")

    for index in range(1, 4):
        touch(photos / f"IMG_00{index}.jpg")

    touch(temp / "缓存1.tmp")
    touch(temp / "缓存2.tmp")
    touch(temp / "重要.txt")

    touch(project / "合同.docx")
    touch(project / "数据.xlsx")
    touch(project / "现场.jpg")
    touch(project / "截图.png")
    touch(project / "临时.tmp")
    touch(project / "~$合同.docx")

    touch(materials / "2024" / "报告1.pdf")
    touch(materials / "2024" / "报告2.pdf")

    print("示例目录已生成：", WORKSPACE)
