import asyncio

import solution
from _harness import run
from _mock_service import MockService


def run_async(coroutine):
    return asyncio.run(coroutine)


def test_all_success():
    service = MockService(bodies={"a": "A", "b": "B"})
    got = run_async(solution.crawl(["a", "b"], service.fetch, limit=2, timeout=0.5, retries=2))
    assert [item["ok"] for item in got] == [True, True]
    assert [item["body"] for item in got] == ["A", "B"]
    assert [item["attempts"] for item in got] == [1, 1]
    assert [item["error"] for item in got] == ["", ""]


def test_retry_then_success():
    service = MockService(failures={"flaky": 2})
    got = run_async(solution.crawl(["flaky"], service.fetch, retries=2))
    assert got[0]["ok"] is True, f"应最终成功: {got[0]}"
    assert got[0]["attempts"] == 3, f"应尝试 3 次，实际 {got[0]['attempts']}"
    assert got[0]["body"] == "body:flaky"


def test_all_attempts_fail():
    service = MockService(failures={"bad": 99})
    got = run_async(solution.crawl(["bad"], service.fetch, retries=2))
    assert got[0]["ok"] is False
    assert got[0]["attempts"] == 3, f"应尝试 3 次，实际 {got[0]['attempts']}"
    assert got[0]["error"], "失败时 error 必须有内容"
    assert got[0]["body"] == ""


def test_timeout_is_recorded():
    service = MockService(timeout_urls={"slow"})
    got = run_async(solution.crawl(["slow"], service.fetch, timeout=0.05, retries=0))
    assert got[0]["ok"] is False
    assert got[0]["attempts"] == 1
    assert "timeout" in got[0]["error"].lower(), f"error 应说明超时，实际 {got[0]['error']!r}"


def test_limit_and_order():
    service = MockService(delay=0.03)
    urls = [f"u{i}" for i in range(9)]
    got = run_async(solution.crawl(urls, service.fetch, limit=3))
    assert [item["url"] for item in got] == urls, "结果顺序应与输入一致"
    assert service.max_active <= 3, f"并发峰值 {service.max_active} 超过 limit=3"


def test_empty():
    assert run_async(solution.crawl([], MockService().fetch)) == []


run([
    ("全部成功", test_all_success),
    ("失败两次后成功", test_retry_then_success),
    ("始终失败记录次数与错误", test_all_attempts_fail),
    ("超时被记录", test_timeout_is_recorded),
    ("并发上限与顺序", test_limit_and_order),
    ("空列表", test_empty),
])
