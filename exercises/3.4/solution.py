"""3.4 参考答案：把 sleep 注入进来，让重试逻辑可测试。"""

import time


class RetryPolicy:
    def __init__(self, attempts: int = 3, delay: float = 1.0, sleep=time.sleep):
        self.attempts = attempts
        self.delay = delay
        self.sleep = sleep

    def run(self, operation):
        last_error = None
        for attempt in range(self.attempts):
            try:
                return operation()
            except Exception as exc:  # noqa: BLE001 - 重试策略需要捕获所有失败
                last_error = exc
                if attempt == self.attempts - 1:
                    raise
                self.sleep(self.delay)
        raise last_error
