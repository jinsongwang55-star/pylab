import asyncio
import time

import solution
from _harness import run
from _mock_service import MockService


def run_async(coroutine):
    return asyncio.run(coroutine)


def test_fast_request_returns_value():
    service = MockService(bodies={"a": "A"})
    assert run_async(solution.fetch_with_timeout("a", service.fetch, 0.5)) == "A"


def test_slow_request_returns_none_quickly():
    service = MockService(delay=0.3)
    started = time.perf_counter()
    got = run_async(solution.fetch_with_timeout("a", service.fetch, 0.05))
    elapsed = time.perf_counter() - started
    assert got is None, "超时应返回 None"
    assert elapsed < 0.5, f"超时后应立即返回，实际耗时 {elapsed:.2f}s"


def test_collect_mixed_results():
    service = MockService(delays={"slow": 0.3}, failures={"bad": 99})
    got = run_async(solution.collect(["ok", "slow", "bad"], service.fetch, 0.05))
    assert got == ["body:ok", None, None], f"混合结果不对: {got}"


def test_collect_preserves_order():
    service = MockService(bodies={"a": "A", "b": "B", "c": "C"})
    got = run_async(solution.collect(["c", "a", "b"], service.fetch, 0.5))
    assert got == ["C", "A", "B"], f"顺序不对: {got}"


def test_collect_empty():
    assert run_async(solution.collect([], MockService().fetch, 0.1)) == []


run([
    ("正常请求返回值", test_fast_request_returns_value),
    ("超时快速返回 None", test_slow_request_returns_none_quickly),
    ("失败被隔离为 None", test_collect_mixed_results),
    ("结果顺序不变", test_collect_preserves_order),
    ("空列表", test_collect_empty),
])
