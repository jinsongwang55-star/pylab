import json
from decimal import Decimal
from pathlib import Path

import solution
from _harness import run


def _fresh(name):
    path = Path(name)
    if path.exists():
        path.unlink()
    return solution.Ledger(path), path


def test_add_returns_record():
    ledger, _ = _fresh("add_record.json")
    record = ledger.add("35.5", "午餐", "餐饮")
    assert isinstance(record, dict), "add 应返回记录字典"
    assert record["id"] == 1
    assert record["amount"] == "35.50", f"金额应存为两位小数字符串，实际 {record['amount']!r}"
    assert record["desc"] == "午餐"
    assert record["tag"] == "餐饮"


def test_ids_increment():
    ledger, _ = _fresh("ids.json")
    assert ledger.add("10", "a")["id"] == 1
    assert ledger.add("20", "b")["id"] == 2
    assert ledger.add("30", "c")["id"] == 3


def test_persistence():
    ledger, path = _fresh("persist.json")
    ledger.add("10", "a")
    ledger.add("20", "b")
    reopened = solution.Ledger(path)
    assert len(reopened.list()) == 2, "重新实例化后应读到全部记录"
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw[0]["amount"] == "10.00", "写盘的金额应是两位小数字符串"


def test_total():
    ledger, _ = _fresh("total.json")
    ledger.add("35.5", "a")
    ledger.add("64.5", "b")
    got = ledger.total()
    assert isinstance(got, Decimal), "total() 应返回 Decimal"
    assert got == Decimal("100.00"), f"合计应为 100.00，实际 {got}"


def test_filter_by_tag():
    ledger, _ = _fresh("filter.json")
    ledger.add("1", "餐饮一", "餐饮")
    ledger.add("2", "交通一", "交通")
    rows = ledger.list("餐饮")
    assert len(rows) == 1, "按标签过滤结果数量不对"
    assert rows[0]["desc"] == "餐饮一"


def test_list_returns_copies():
    ledger, _ = _fresh("copy.json")
    ledger.add("1", "原始")
    rows = ledger.list()
    rows[0]["desc"] = "被外部改掉了"
    assert ledger.list()[0]["desc"] == "原始", "list() 必须返回副本，不能暴露内部对象"


def test_invalid_amount_has_no_side_effect():
    ledger, _ = _fresh("invalid.json")
    ledger.add("1", "a")
    for bad in ("abc", "0", "-5", "NaN"):
        try:
            ledger.add(bad, "bad")
        except ValueError:
            continue
        raise AssertionError(f"非法金额 {bad!r} 应抛 ValueError")
    assert ledger.add("2", "c")["id"] == 2, "失败的操作不应占用 ID"


run([
    ("add 返回完整记录", test_add_returns_record),
    ("ID 从 1 递增", test_ids_increment),
    ("重新打开后数据仍在", test_persistence),
    ("total 返回 Decimal 合计", test_total),
    ("按标签过滤", test_filter_by_tag),
    ("list 返回副本", test_list_returns_copies),
    ("非法金额无副作用", test_invalid_amount_has_no_side_effect),
])
