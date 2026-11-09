"""4.4 参考答案：带并发上限、超时与重试的批量抓取器。"""

import asyncio


async def crawl(urls, fetch, *, limit=5, timeout=1.0, retries=2):
    semaphore = asyncio.Semaphore(limit)

    async def one(url):
        attempts = 0
        last_error = ""
        for _ in range(retries + 1):
            attempts += 1
            try:
                async with semaphore:
                    body = await asyncio.wait_for(fetch(url), timeout=timeout)
                return {"url": url, "ok": True, "body": body, "error": "", "attempts": attempts}
            except asyncio.TimeoutError:
                last_error = "TimeoutError"
            except Exception as exc:  # noqa: BLE001 - 批量边界把失败转成数据
                last_error = type(exc).__name__
        return {"url": url, "ok": False, "body": "", "error": last_error, "attempts": attempts}

    return list(await asyncio.gather(*(one(url) for url in urls)))
