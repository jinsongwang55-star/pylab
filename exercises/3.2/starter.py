"""3.2 练习：把「今天」作为参数传入，让业务逻辑可测试。"""

from datetime import date


def is_expired(due: date, today: date) -> bool:
    """due 早于 today 视为过期，相等不算。"""
    raise NotImplementedError("删掉这一行，开始实现")


def overdue_days(due: date, today: date) -> int:
    """已过期返回相差天数，未过期返回 0。"""
    raise NotImplementedError("删掉这一行，开始实现")


def build_summary(tasks: list[dict], today: date) -> dict:
    """返回 {"total", "overdue", "overdue_titles"}，标题保持输入顺序。"""
    raise NotImplementedError("删掉这一行，开始实现")
