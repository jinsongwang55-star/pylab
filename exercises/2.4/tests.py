from pathlib import Path

import solution
from _harness import run


def _root(name):
    root = Path(name)
    root.mkdir(exist_ok=True)
    return root


def _touch(path, text=""):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_organize_moves():
    root = _root("s1")
    for name in ("a.py", "b.JPG", "c.txt", "d.zip", "e.unknown"):
        _touch(root / name)

    moves = solution.organize(root)

    assert len(moves) == 5, f"应返回 5 条移动记录，实际 {len(moves)}"
    for move in moves:
        assert Path(move["src"]).is_absolute(), "src 必须是绝对路径"
        assert Path(move["dst"]).is_absolute(), "dst 必须是绝对路径"
    assert (root / "code" / "a.py").exists()
    assert (root / "images" / "b.JPG").exists()
    assert (root / "documents" / "c.txt").exists()
    assert (root / "archives" / "d.zip").exists()
    assert (root / "others" / "e.unknown").exists()
    assert not (root / "a.py").exists(), "源文件应已被移走"


def test_dry_run():
    root = _root("s2")
    _touch(root / "a.py")
    before = sorted(child.name for child in root.iterdir())

    moves = solution.organize(root, dry_run=True)
    after = sorted(child.name for child in root.iterdir())

    assert len(moves) == 1
    assert before == after, "dry_run 不应改动文件系统"
    assert not (root / "code").exists(), "dry_run 不应创建分类目录"


def test_collision():
    root = _root("s3")
    _touch(root / "photo.jpg", "new")
    _touch(root / "images" / "photo.jpg", "old")

    solution.organize(root)

    assert (root / "images" / "photo.jpg").read_text(encoding="utf-8") == "old", "原文件不能被覆盖"
    assert (root / "images" / "photo(1).jpg").read_text(encoding="utf-8") == "new"


def test_undo_restores():
    root = _root("s4")
    names = ["a.py", "b.jpg", "c.md", "d.xyz"]
    for name in names:
        _touch(root / name, name)

    moves = solution.organize(root)
    restored = solution.undo(moves)

    assert restored == len(names), f"应恢复 {len(names)} 个文件，实际 {restored}"
    for name in names:
        assert (root / name).read_text(encoding="utf-8") == name, f"{name} 未恢复原位"


def test_undo_skips_occupied():
    root = _root("s5")
    _touch(root / "a.py", "original")
    _touch(root / "b.jpg", "image")

    moves = solution.organize(root)
    _touch(root / "a.py", "occupied")

    restored = solution.undo(moves)

    assert restored == 1, f"应只恢复 1 个，实际 {restored}"
    assert (root / "a.py").read_text(encoding="utf-8") == "occupied", "被占用的原位置不能覆盖"
    assert (root / "b.jpg").read_text(encoding="utf-8") == "image"


def test_skips_hidden_and_symlink():
    root = _root("s6")
    _touch(root / ".hidden.py")
    target = root / "real.py"
    _touch(target)
    link = root / "link.py"
    if not link.exists():
        link.symlink_to(target)

    moves = solution.organize(root)

    assert len(moves) == 1, f"只应移动 real.py，实际 {[m['src'] for m in moves]}"
    assert (root / ".hidden.py").exists(), "隐藏文件不应被移动"
    assert (root / "link.py").is_symlink(), "符号链接不应被移动（目标被移走后它会变成悬空链接）"


run([
    ("移动并分类正确", test_organize_moves),
    ("dry_run 零改动", test_dry_run),
    ("重名不覆盖", test_collision),
    ("undo 完整恢复", test_undo_restores),
    ("undo 跳过被占用位置", test_undo_skips_occupied),
    ("跳过隐藏文件与符号链接", test_skips_hidden_and_symlink),
])
