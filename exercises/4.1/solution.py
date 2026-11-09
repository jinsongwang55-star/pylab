"""4.1 参考答案：限制并发数的批量抓取。"""

import asyncio


async def fetch_limited(urls, fetch, limit):
    semaphore = asyncio.Semaphore(limit)

    async def one(url):
        async with semaphore:
            return await fetch(url)

    return list(await asyncio.gather(*(one(url) for url in urls)))
