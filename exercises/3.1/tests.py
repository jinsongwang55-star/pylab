from dataclasses import FrozenInstanceError
from decimal import Decimal

import solution
from _harness import run


def test_construct():
    item = solution.Item("咖啡", Decimal("18.5"))
    assert item.name == "咖啡"
    assert item.price == Decimal("18.5")
    assert item.tags == (), "tags 默认值应为空元组"


def test_frozen():
    item = solution.Item("咖啡", Decimal("18.5"))
    try:
        item.price = Decimal("1")
    except FrozenInstanceError:
        return
    raise AssertionError("frozen=True 时赋值应抛 FrozenInstanceError")


def test_equality():
    first = solution.Item("咖啡", Decimal("18.5"), ("饮品",))
    second = solution.Item("咖啡", Decimal("18.5"), ("饮品",))
    third = solution.Item("咖啡", Decimal("18.5"), ("早餐",))
    assert first == second, "相同值的 Item 应相等"
    assert first != third


def test_invalid_price():
    for price in (Decimal("0"), Decimal("-1")):
        try:
            solution.Item("x", price)
        except ValueError:
            continue
        raise AssertionError(f"price={price} 应抛 ValueError")


def test_blank_name():
    for name in ("", "   "):
        try:
            solution.Item(name, Decimal("1"))
        except ValueError:
            continue
        raise AssertionError(f"name={name!r} 应抛 ValueError")


def test_empty_tags_default():
    assert solution.Item("x", Decimal("1")).tags == ()


run([
    ("正常构造与默认 tags", test_construct),
    ("冻结后不可赋值", test_frozen),
    ("值相等语义", test_equality),
    ("非法价格被拒绝", test_invalid_price),
    ("空名称被拒绝", test_blank_name),
    ("默认 tags 为空元组", test_empty_tags_default),
])
