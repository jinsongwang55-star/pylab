"""3.0 参考答案：用 TypedDict 与函数标注描述数据契约。"""

from typing import TypedDict


class User(TypedDict):
    name: str
    age: int


def adult_names(users: list[User]) -> list[str]:
    return [user["name"] for user in users if user["age"] >= 18]
