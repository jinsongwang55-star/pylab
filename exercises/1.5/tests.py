import inspect

import solution
from _harness import run


def test_is_generator():
    generator = solution.fib()
    assert inspect.isgenerator(generator), "fib() 必须返回生成器（函数体内使用 yield）"


def test_first_values():
    got = solution.take(solution.fib(), 8)
    assert got == [0, 1, 1, 2, 3, 5, 8, 13], f"前 8 项不对: {got}"


def test_take_zero():
    assert solution.take(solution.fib(), 0) == [], "n=0 应返回空列表"


def test_take_more_than_existing():
    assert solution.take([1, 2], 5) == [1, 2], "元素不足时应返回已有全部，而不是报错"


def test_laziness():
    values = solution.take(solution.fib(), 500)
    assert len(values) == 500
    a, b = 0, 1
    for _ in range(499):
        a, b = b, a + b
    assert values[-1] == a, "第 500 项数值不对，检查递推公式"


run([
    ("fib() 是生成器", test_is_generator),
    ("前 8 项数值正确", test_first_values),
    ("take 支持 n=0", test_take_zero),
    ("take 不足时返回全部", test_take_more_than_existing),
    ("惰性求值可连续取 500 项", test_laziness),
])
