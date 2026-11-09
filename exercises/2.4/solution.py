"""2.4 参考答案：文件整理与撤销。"""

import shutil
from pathlib import Path

CATEGORIES = {
    "images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"},
    "documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".csv"},
    "code": {".py", ".js", ".ts", ".html", ".css", ".json"},
    "archives": {".zip", ".tar", ".gz", ".bz2", ".7z"},
}


def _category(path: Path) -> str:
    suffix = path.suffix.lower()
    for name in ("images", "documents", "code", "archives"):
        if suffix in CATEGORIES[name]:
            return name
    return "others"


def _unique_path(target: Path) -> Path:
    if not target.exists():
        return target
    counter = 1
    while True:
        candidate = target.with_name(f"{target.stem}({counter}){target.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def organize(directory: Path, dry_run: bool = False) -> list[dict]:
    root = Path(directory).resolve()
    moves: list[dict] = []
    for child in sorted(root.iterdir()):
        if child.is_symlink() or not child.is_file() or child.name.startswith("."):
            continue
        target_dir = root / _category(child)
        destination = _unique_path(target_dir / child.name)
        moves.append({"src": str(child), "dst": str(destination)})
        if not dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(child), str(destination))
    return sorted(moves, key=lambda item: item["dst"])


def undo(moves: list[dict]) -> int:
    restored = 0
    for move in reversed(moves):
        source = Path(move["src"])
        destination = Path(move["dst"])
        if not destination.exists() or source.exists():
            continue
        shutil.move(str(destination), str(source))
        restored += 1
    return restored
