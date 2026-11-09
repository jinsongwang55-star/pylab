import asyncio

import solution
from _harness import run
from _mock_service import MockService


def run_async(coroutine):
    return asyncio.run(coroutine)


def test_limit_respected():
    service = MockService(delay=0.03)
    urls = [f"u{i}" for i in range(10)]
    got = run_async(solution.fetch_limited(urls, service.fetch, 3))
    assert len(got) == 10
    assert service.max_active <= 3, f"并发峰值 {service.max_active} 超过了 limit=3"


def test_order_preserved():
    service = MockService(bodies={"a": "A", "b": "B", "c": "C"})
    got = run_async(solution.fetch_limited(["a", "b", "c"], service.fetch, 2))
    assert got == ["A", "B", "C"], f"顺序不对: {got}"


def test_limit_larger_than_urls():
    service = MockService(delay=0.02)
    got = run_async(solution.fetch_limited(["a", "b"], service.fetch, 10))
    assert got == ["body:a", "body:b"]
    assert service.max_active <= 2, "并发不应超过实际任务数"


def test_limit_one_is_serial():
    service = MockService(delay=0.02)
    run_async(solution.fetch_limited(["a", "b", "c"], service.fetch, 1))
    assert service.max_active == 1, f"limit=1 时应串行，实际峰值 {service.max_active}"


def test_empty_list():
    service = MockService()
    assert run_async(solution.fetch_limited([], service.fetch, 3)) == []


run([
    ("并发峰值不超过 limit", test_limit_respected),
    ("返回顺序不变", test_order_preserved),
    ("limit 大于任务数时正常工作", test_limit_larger_than_urls),
    ("limit=1 退化为串行", test_limit_one_is_serial),
    ("空列表", test_empty_list),
])
