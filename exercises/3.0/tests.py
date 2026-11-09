import typing

import solution
from _harness import run


def test_user_definition():
    user = getattr(solution, "User", None)
    assert user is not None, "需要定义 User(TypedDict)"
    assert user.__annotations__ == {"name": str, "age": int}, f"User 字段不对: {user.__annotations__}"
    assert user.__required_keys__ == frozenset({"name", "age"}), "name 与 age 都应是必填字段"


def test_function_annotations():
    hints = typing.get_type_hints(solution.adult_names)
    users_type = hints.get("users")
    assert typing.get_origin(users_type) is list, f"users 应标注为 list[User]，实际 {users_type}"
    assert typing.get_args(users_type) == (solution.User,), "users 的元素类型应是 User"

    return_type = hints.get("return")
    assert typing.get_origin(return_type) is list, f"返回值应标注为 list[str]，实际 {return_type}"
    assert typing.get_args(return_type) == (str,), "返回值元素类型应是 str"


def test_filters_adults():
    users = [
        {"name": "A", "age": 17},
        {"name": "B", "age": 18},
        {"name": "C", "age": 30},
    ]
    assert solution.adult_names(users) == ["B", "C"]


def test_boundary_18():
    assert solution.adult_names([{"name": "X", "age": 18}]) == ["X"], "18 岁应当算成年"


def test_preserves_order():
    users = [{"name": name, "age": 20} for name in ("z", "a", "m")]
    assert solution.adult_names(users) == ["z", "a", "m"]


def test_empty():
    assert solution.adult_names([]) == []


run([
    ("User 的 TypedDict 定义", test_user_definition),
    ("函数标注完整正确", test_function_annotations),
    ("筛选成年用户", test_filters_adults),
    ("18 岁边界", test_boundary_18),
    ("保持原顺序", test_preserves_order),
    ("空列表", test_empty),
])
