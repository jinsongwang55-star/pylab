from datetime import date

import solution
from _harness import run

TODAY = date(2026, 11, 9)


def test_is_expired_boundaries():
    assert solution.is_expired(date(2026, 11, 8), TODAY) is True, "昨天应算过期"
    assert solution.is_expired(date(2026, 11, 9), TODAY) is False, "当天不算过期"
    assert solution.is_expired(date(2026, 11, 10), TODAY) is False, "未来不算过期"


def test_overdue_days():
    assert solution.overdue_days(date(2026, 11, 1), TODAY) == 8
    assert solution.overdue_days(date(2026, 11, 9), TODAY) == 0
    assert solution.overdue_days(date(2026, 12, 1), TODAY) == 0


def test_build_summary():
    tasks = [
        {"title": "写报告", "due": "2026-11-01"},
        {"title": "交房租", "due": "2026-11-09"},
        {"title": "订机票", "due": "2026-11-20"},
        {"title": "年检", "due": "2026-10-15"},
    ]
    got = solution.build_summary(tasks, TODAY)
    expected = {"total": 4, "overdue": 2, "overdue_titles": ["写报告", "年检"]}
    assert got == expected, f"汇总结果不对: {got}"


def test_build_summary_empty():
    assert solution.build_summary([], TODAY) == {"total": 0, "overdue": 0, "overdue_titles": []}


def test_due_today_not_overdue():
    got = solution.build_summary([{"title": "今天到期", "due": "2026-11-09"}], TODAY)
    assert got["overdue"] == 0, "当天到期不应算逾期"


run([
    ("过期边界判断", test_is_expired_boundaries),
    ("逾期天数计算", test_overdue_days),
    ("汇总数量与顺序", test_build_summary),
    ("空任务列表", test_build_summary_empty),
    ("当天到期不算逾期", test_due_today_not_overdue),
])
