"""1.1 参考答案：把字符串金额解析成 Decimal。"""

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation


def parse_amount(raw: str) -> Decimal:
    try:
        value = Decimal(raw)
    except (InvalidOperation, ValueError):
        raise ValueError(f"不是合法金额: {raw!r}") from None
    if not value.is_finite():
        raise ValueError("金额必须是有限数")
    if value <= 0:
        raise ValueError("金额必须大于 0")
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
