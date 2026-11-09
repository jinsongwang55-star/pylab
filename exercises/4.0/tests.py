import asyncio
import time

import solution
from _harness import run
from _mock_service import MockService


def run_async(coroutine):
    return asyncio.run(coroutine)


def test_returns_in_order():
    service = MockService(bodies={"a": "A", "b": "B"})
    got = run_async(solution.fetch_all(["a", "b"], service.fetch))
    assert got == ["A", "B"], f"返回值或顺序不对: {got}"


def test_empty_list():
    service = MockService()
    assert run_async(solution.fetch_all([], service.fetch)) == []


def test_runs_concurrently():
    service = MockService(delay=0.05)
    urls = [f"u{i}" for i in range(8)]
    started = time.perf_counter()
    got = run_async(solution.fetch_all(urls, service.fetch))
    elapsed = time.perf_counter() - started
    assert len(got) == 8
    assert elapsed < 0.3, f"看起来是串行执行，8 个 0.05 秒请求耗时 {elapsed:.2f}s"


def test_calls_each_url_once():
    service = MockService()
    run_async(solution.fetch_all(["a", "b", "c"], service.fetch))
    assert service.calls == {"a": 1, "b": 1, "c": 1}, f"请求次数不对: {service.calls}"


def test_exception_propagates():
    service = MockService(failures={"bad": 99})
    try:
        run_async(solution.fetch_all(["ok", "bad"], service.fetch))
    except ConnectionError:
        return
    raise AssertionError("fetch 抛异常时应向上传播，不能被静默吞掉")


run([
    ("返回顺序与输入一致", test_returns_in_order),
    ("空列表返回空列表", test_empty_list),
    ("确实并发执行", test_runs_concurrently),
    ("每个 URL 只请求一次", test_calls_each_url_once),
    ("异常向上传播", test_exception_propagates),
])
