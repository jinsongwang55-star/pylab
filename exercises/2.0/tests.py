from pathlib import Path

import solution
from _harness import run


def _dir(name):
    root = Path(name)
    root.mkdir(exist_ok=True)
    return root


def test_basic_classification():
    root = _dir("d_basic")
    for name in ("photo.JPG", "notes.md", "app.py", "data.csv", "archive.zip", "README", "weird.xyz"):
        (root / name).write_text("", encoding="utf-8")

    got = solution.classify_files(root)
    expected = {
        "images": ["photo.JPG"],
        "documents": ["data.csv", "notes.md"],
        "code": ["app.py"],
        "archives": ["archive.zip"],
        "others": ["README", "weird.xyz"],
    }
    assert got == expected, f"分类结果不对: {got}"
    assert list(got) == ["images", "documents", "code", "archives", "others"], f"键顺序不对: {list(got)}"


def test_hidden_skipped():
    root = _dir("d_hidden")
    (root / ".secret.py").write_text("", encoding="utf-8")
    (root / "visible.py").write_text("", encoding="utf-8")
    got = solution.classify_files(root)
    assert got == {"code": ["visible.py"]}, f"隐藏文件应被跳过: {got}"


def test_not_recursive():
    root = _dir("d_sub")
    sub = root / "sub"
    sub.mkdir(exist_ok=True)
    (sub / "nested.py").write_text("", encoding="utf-8")
    assert solution.classify_files(root) == {}, "不应递归进入子目录"


def test_symlink_skipped():
    root = _dir("d_link")
    target = root / "real.py"
    target.write_text("", encoding="utf-8")
    link = root / "link.py"
    if not link.exists():
        link.symlink_to(target)
    got = solution.classify_files(root)
    assert got == {"code": ["real.py"]}, f"符号链接应被跳过: {got}"


def test_empty_directory():
    assert solution.classify_files(_dir("d_empty")) == {}, "空目录应返回空字典"


def test_uppercase_suffix():
    root = _dir("d_upper")
    (root / "A.PNG").write_text("", encoding="utf-8")
    (root / "B.Mp4").write_text("", encoding="utf-8")
    got = solution.classify_files(root)
    assert got == {"images": ["A.PNG"], "others": ["B.Mp4"]}, f"扩展名应不区分大小写: {got}"


run([
    ("分类与排序正确", test_basic_classification),
    ("跳过隐藏文件", test_hidden_skipped),
    ("不递归子目录", test_not_recursive),
    ("跳过符号链接", test_symlink_skipped),
    ("空目录返回空字典", test_empty_directory),
    ("扩展名不区分大小写", test_uppercase_suffix),
])
