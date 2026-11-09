"""2.4 综合练习：文件整理与撤销。"""

import shutil
from pathlib import Path

CATEGORIES = {
    "images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"},
    "documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".csv"},
    "code": {".py", ".js", ".ts", ".html", ".css", ".json"},
    "archives": {".zip", ".tar", ".gz", ".bz2", ".7z"},
}


def organize(directory: Path, dry_run: bool = False) -> list[dict]:
    """整理目录，返回 [{"src": 绝对路径, "dst": 绝对路径}]，按 dst 排序。"""
    raise NotImplementedError("删掉这一行，开始实现")


def undo(moves: list[dict]) -> int:
    """倒序恢复，返回成功恢复的数量。"""
    raise NotImplementedError("删掉这一行，开始实现")
