"""2.0 参考答案：用 pathlib 扫描并分类直接子文件。"""

from pathlib import Path

CATEGORIES = {
    "images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"},
    "documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".csv"},
    "code": {".py", ".js", ".ts", ".html", ".css", ".json"},
    "archives": {".zip", ".tar", ".gz", ".bz2", ".7z"},
}
CATEGORY_ORDER = ["images", "documents", "code", "archives", "others"]


def classify_files(directory: Path) -> dict[str, list[str]]:
    buckets: dict[str, list[str]] = {name: [] for name in CATEGORY_ORDER}
    for child in Path(directory).iterdir():
        if child.is_symlink() or not child.is_file() or child.name.startswith("."):
            continue
        suffix = child.suffix.lower()
        category = "others"
        for name in ("images", "documents", "code", "archives"):
            if suffix in CATEGORIES[name]:
                category = name
                break
        buckets[category].append(child.name)
    return {name: sorted(buckets[name]) for name in CATEGORY_ORDER if buckets[name]}
