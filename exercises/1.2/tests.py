from decimal import Decimal

import solution
from _harness import run

RECORDS = [
    {"amount": "35.5", "tag": "餐饮"},
    {"amount": "12", "tag": "交通"},
    {"amount": "64.5", "tag": "餐饮"},
    {"amount": "300", "tag": "居住"},
    {"amount": "20", "tag": "交通"},
]


def test_totals():
    got = solution.summarize_tags(RECORDS)
    expected = {
        "居住": Decimal("300"),
        "餐饮": Decimal("100"),
        "交通": Decimal("32"),
    }
    assert got == expected, f"汇总结果不对: {got}"


def test_value_type():
    got = solution.summarize_tags(RECORDS)
    assert got, "结果不应为空"
    assert all(isinstance(v, Decimal) for v in got.values()), "所有合计值必须是 Decimal，不能用 float"


def test_order_desc():
    got = solution.summarize_tags(RECORDS)
    assert list(got) == ["居住", "餐饮", "交通"], f"应按合计降序，实际顺序是 {list(got)}"


def test_tie_break_by_tag():
    records = [
        {"amount": "10", "tag": "b"},
        {"amount": "10", "tag": "a"},
        {"amount": "5", "tag": "c"},
    ]
    got = solution.summarize_tags(records)
    assert list(got) == ["a", "b", "c"], f"同额时应按 tag 升序，实际是 {list(got)}"


def test_empty():
    assert solution.summarize_tags([]) == {}, "空列表应返回空字典"


run([
    ("分类汇总金额正确", test_totals),
    ("合计值是 Decimal", test_value_type),
    ("按合计降序排列", test_order_desc),
    ("同额按标签升序", test_tie_break_by_tag),
    ("空输入返回空字典", test_empty),
])
