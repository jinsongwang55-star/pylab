"""1.5 参考答案：无限斐波那契生成器与 take。"""


def fib():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def take(iterable, n: int) -> list:
    result = []
    iterator = iter(iterable)
    for _ in range(n):
        try:
            result.append(next(iterator))
        except StopIteration:
            break
    return result
