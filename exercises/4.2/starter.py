"""4.2 练习：单请求超时与批量失败隔离。"""


async def fetch_with_timeout(url, fetch, seconds):
    """在 seconds 秒内返回结果，超时返回 None。"""
    raise NotImplementedError("删掉这一行，开始实现")


async def collect(urls, fetch, seconds):
    """并发抓取；超时或异常的位置返回 None，顺序与输入一致。"""
    raise NotImplementedError("删掉这一行，开始实现")
