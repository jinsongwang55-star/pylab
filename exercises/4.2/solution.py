"""4.2 参考答案：单请求超时与批量失败隔离。"""

import asyncio


async def fetch_with_timeout(url, fetch, seconds):
    try:
        return await asyncio.wait_for(fetch(url), timeout=seconds)
    except asyncio.TimeoutError:
        return None


async def collect(urls, fetch, seconds):
    async def one(url):
        try:
            return await asyncio.wait_for(fetch(url), timeout=seconds)
        except Exception:  # noqa: BLE001 - 批量边界故意把失败转成 None
            return None

    return list(await asyncio.gather(*(one(url) for url in urls)))
