import solution
from _harness import run


def test_counter_basic():
    counter = solution.make_counter()
    assert counter() == 0, "第一次调用应返回 0"
    assert counter() == 1, "第二次调用应返回 1"
    assert counter() == 2, "第三次调用应返回 2"


def test_counter_start():
    counter = solution.make_counter(10)
    assert counter() == 10
    assert counter() == 11


def test_counters_independent():
    first = solution.make_counter()
    second = solution.make_counter(10)
    assert first() == 0
    assert second() == 10
    assert first() == 1, "第一个计数器不应受第二个影响"
    assert second() == 11, "第二个计数器不应受第一个影响"


def test_append_fresh_list():
    assert solution.append_item(1) == [1]
    assert solution.append_item(2) == [2], "上一次调用不应影响这一次（可变默认参数泄漏）"


def test_append_to_given_list():
    target = []
    result = solution.append_item("x", target)
    assert result is target, "传入 target 时应返回同一个列表对象"
    assert target == ["x"]


run([
    ("计数器从 0 开始递增", test_counter_basic),
    ("计数器支持起始值", test_counter_start),
    ("两个计数器互不影响", test_counters_independent),
    ("不传 target 时无状态泄漏", test_append_fresh_list),
    ("传入 target 时原地追加", test_append_to_given_list),
])
