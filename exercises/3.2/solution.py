"""3.2 参考答案：把「今天」作为参数传入，让业务逻辑可测试。"""

from datetime import date


def is_expired(due: date, today: date) -> bool:
    return due < today


def overdue_days(due: date, today: date) -> int:
    if due >= today:
        return 0
    return (today - due).days


def build_summary(tasks: list[dict], today: date) -> dict:
    overdue_titles = []
    for task in tasks:
        if is_expired(date.fromisoformat(task["due"]), today):
            overdue_titles.append(task["title"])
    return {
        "total": len(tasks),
        "overdue": len(overdue_titles),
        "overdue_titles": overdue_titles,
    }
