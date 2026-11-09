"""4.4 综合练习：带并发上限、超时与重试的批量抓取器。"""


async def crawl(urls, fetch, *, limit=5, timeout=1.0, retries=2):
    """返回 [{"url", "ok", "body", "error", "attempts"}]，顺序与 urls 一致，永不抛异常。"""
    raise NotImplementedError("删掉这一行，开始实现")
