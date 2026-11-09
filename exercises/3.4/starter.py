"""3.4 综合练习：把 sleep 注入进来，让重试逻辑可测试。"""

import time


class RetryPolicy:
    def __init__(self, attempts: int = 3, delay: float = 1.0, sleep=time.sleep):
        self.attempts = attempts
        self.delay = delay
        self.sleep = sleep

    def run(self, operation):
        """按右侧课程正文的规则执行 operation。"""
        raise NotImplementedError("删掉这一行，开始实现")
