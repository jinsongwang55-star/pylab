import json
from pathlib import Path

import solution
from _harness import run


def _clean(name):
    path = Path(name)
    if path.exists():
        path.unlink()
    return path


def test_creates_file():
    path = _clean("case_create.json")
    with solution.atomic_json(path, []) as data:
        data.append({"a": 1})
    assert path.exists(), "正常退出后应创建文件"
    assert json.loads(path.read_text(encoding="utf-8")) == [{"a": 1}]


def test_reads_existing():
    path = _clean("case_read.json")
    path.write_text('[{"x": 1}]', encoding="utf-8")
    with solution.atomic_json(path, []) as data:
        data.append({"x": 2})
    assert json.loads(path.read_text(encoding="utf-8")) == [{"x": 1}, {"x": 2}]


def test_no_file_on_error():
    path = _clean("case_never.json")
    try:
        with solution.atomic_json(path, []) as data:
            data.append(1)
            raise RuntimeError("模拟写盘前崩溃")
    except RuntimeError:
        pass
    else:
        raise AssertionError("异常必须向上抛出，不能被吞掉")
    assert not path.exists(), "块内抛异常时不应创建文件"


def test_preserves_existing_on_error():
    path = _clean("case_keep.json")
    path.write_text('[{"keep": true}]', encoding="utf-8")
    try:
        with solution.atomic_json(path, []) as data:
            data.append(999)
            raise RuntimeError("模拟写盘前崩溃")
    except RuntimeError:
        pass
    assert json.loads(path.read_text(encoding="utf-8")) == [{"keep": True}], "异常时原文件必须一字未变"


def test_default_not_mutated():
    path = _clean("case_default.json")
    default = []
    with solution.atomic_json(path, default) as data:
        data.append(1)
    assert default == [], "不能直接修改传入的 default，应使用深拷贝"


run([
    ("正常退出时写入文件", test_creates_file),
    ("能读取并追加已有数据", test_reads_existing),
    ("异常时不创建文件", test_no_file_on_error),
    ("异常时原文件不变", test_preserves_existing_on_error),
    ("不修改传入的 default", test_default_not_mutated),
])
