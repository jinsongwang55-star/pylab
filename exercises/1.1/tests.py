from decimal import Decimal

import solution
from _harness import run


def test_basic():
    got = solution.parse_amount("35.5")
    assert isinstance(got, Decimal), f"返回值应为 Decimal，实际是 {type(got).__name__}"
    assert got == Decimal("35.50"), f"'35.5' 应得到 35.50，实际是 {got}"


def test_integer_string():
    got = solution.parse_amount("100")
    assert got == Decimal("100.00"), f"'100' 应得到 100.00，实际是 {got}"


def test_round_half_up():
    got = solution.parse_amount("2.675")
    assert got == Decimal("2.68"), f"'2.675' 按 ROUND_HALF_UP 应为 2.68，实际是 {got}"


def test_trailing_zeros():
    got = solution.parse_amount("1")
    assert str(got) == "1.00", f"字符串形式应为 '1.00'，实际是 {str(got)!r}"


def test_reject_text():
    try:
        solution.parse_amount("abc")
    except ValueError:
        return
    raise AssertionError("'abc' 应抛 ValueError")


def test_reject_empty():
    try:
        solution.parse_amount("")
    except ValueError:
        return
    raise AssertionError("空字符串应抛 ValueError")


def test_reject_non_positive():
    for raw in ("0", "-1", "-0.01"):
        try:
            solution.parse_amount(raw)
        except ValueError:
            continue
        raise AssertionError(f"{raw!r} 应抛 ValueError")


def test_reject_non_finite():
    for raw in ("NaN", "Infinity", "-Infinity"):
        try:
            solution.parse_amount(raw)
        except ValueError:
            continue
        raise AssertionError(f"{raw!r} 应抛 ValueError")


run([
    ("基础转换 35.5 → 35.50", test_basic),
    ("整数串 100 → 100.00", test_integer_string),
    ("四舍五入 2.675 → 2.68", test_round_half_up),
    ("保留两位 1 → '1.00'", test_trailing_zeros),
    ("拒绝非数字", test_reject_text),
    ("拒绝空串", test_reject_empty),
    ("拒绝零与负数", test_reject_non_positive),
    ("拒绝 NaN / Infinity", test_reject_non_finite),
])
