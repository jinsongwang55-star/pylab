"""本地异步模拟服务，供阶段 4 的测试注入使用。

不依赖网络与第三方库，延迟、失败次数、挂起行为都可精确控制，
因此可以对并发、超时、重试做确定性断言。
"""

from __future__ import annotations

import asyncio
from collections import Counter


class MockService:
    """模拟一个远端服务。

    参数:
        delay: 所有请求的基础延迟（秒）
        delays: 按 URL 覆盖延迟，例如 {"slow": 0.3}
        failures: 按 URL 指定前 N 次失败，例如 {"flaky": 2}
        timeout_urls: 这些 URL 会一直挂起，直到调用方取消
        bodies: 按 URL 指定返回内容，默认 "body:<url>"
    """

    def __init__(self, delay=0.0, delays=None, failures=None, timeout_urls=None, bodies=None):
        self.delay = delay
        self.delays = dict(delays or {})
        self.failures = dict(failures or {})
        self.timeout_urls = set(timeout_urls or ())
        self.bodies = dict(bodies or {})
        self.active = 0
        self.max_active = 0
        self.calls: Counter[str] = Counter()

    async def fetch(self, url: str) -> str:
        self.calls[url] += 1
        self.active += 1
        self.max_active = max(self.max_active, self.active)
        try:
            if url in self.timeout_urls:
                await asyncio.sleep(3600)

            delay = self.delays.get(url, self.delay)
            if delay:
                await asyncio.sleep(delay)

            remaining = self.failures.get(url, 0)
            if remaining > 0:
                self.failures[url] = remaining - 1
                raise ConnectionError(f"模拟失败: {url}")

            return self.bodies.get(url, f"body:{url}")
        finally:
            self.active -= 1
