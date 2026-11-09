"""1.2 参考答案：按标签汇总金额。"""

from decimal import Decimal


def summarize_tags(records: list[dict]) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = {}
    for record in records:
        tag = record["tag"]
        totals[tag] = totals.get(tag, Decimal("0")) + Decimal(record["amount"])
    return dict(sorted(totals.items(), key=lambda item: (-item[1], item[0])))
