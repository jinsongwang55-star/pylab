"""2.0 练习：用 pathlib 扫描并分类直接子文件。"""

from pathlib import Path

CATEGORIES = {
    "images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"},
    "documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".csv"},
    "code": {".py", ".js", ".ts", ".html", ".css", ".json"},
    "archives": {".zip", ".tar", ".gz", ".bz2", ".7z"},
}
CATEGORY_ORDER = ["images", "documents", "code", "archives", "others"]


def classify_files(directory: Path) -> dict[str, list[str]]:
    """扫描直接子文件并按扩展名分类，规则见右侧课程正文。"""
    raise NotImplementedError("删掉这一行，开始实现")
