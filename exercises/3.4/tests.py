import solution
from _harness import run


class Boom(Exception):
    pass


def test_success_first_try():
    delays = []
    calls = []

    def operation():
        calls.append(1)
        return "ok"

    policy = solution.RetryPolicy(attempts=3, delay=0.5, sleep=delays.append)
    assert policy.run(operation) == "ok"
    assert len(calls) == 1, f"成功时只应调用一次，实际 {len(calls)}"
    assert delays == [], "成功时不应 sleep"


def test_retry_then_success():
    delays = []
    calls = []

    def operation():
        calls.append(1)
        if len(calls) < 3:
            raise Boom(f"fail-{len(calls)}")
        return "done"

    policy = solution.RetryPolicy(attempts=3, delay=0.5, sleep=delays.append)
    assert policy.run(operation) == "done"
    assert len(calls) == 3, f"应调用 3 次，实际 {len(calls)}"
    assert delays == [0.5, 0.5], f"延迟序列不对: {delays}"


def test_all_fail_raises_last():
    delays = []
    calls = []

    def operation():
        calls.append(1)
        raise Boom(f"fail-{len(calls)}")

    policy = solution.RetryPolicy(attempts=3, delay=0.2, sleep=delays.append)
    try:
        policy.run(operation)
    except Boom as exc:
        assert str(exc) == "fail-3", f"应抛最后一次异常，实际 {exc}"
    else:
        raise AssertionError("全部失败时应抛出异常")
    assert len(calls) == 3
    assert delays == [0.2, 0.2]


def test_single_attempt():
    delays = []
    calls = []

    def operation():
        calls.append(1)
        raise Boom("once")

    policy = solution.RetryPolicy(attempts=1, delay=1.0, sleep=delays.append)
    try:
        policy.run(operation)
    except Boom:
        pass
    else:
        raise AssertionError("应抛出异常")
    assert len(calls) == 1, "attempts=1 时只应调用一次"
    assert delays == [], "attempts=1 时不应 sleep"


def test_returns_value():
    policy = solution.RetryPolicy(attempts=2, delay=0, sleep=lambda _: None)
    assert policy.run(lambda: 42) == 42


run([
    ("首次成功不重试", test_success_first_try),
    ("失败后重试并成功", test_retry_then_success),
    ("全部失败抛最后一次异常", test_all_fail_raises_last),
    ("attempts=1 只调用一次", test_single_attempt),
    ("返回 operation 的结果", test_returns_value),
])
