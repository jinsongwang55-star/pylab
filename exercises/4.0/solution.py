"""4.0 参考答案：并发抓取一组 URL。"""

import asyncio


async def fetch_all(urls, fetch):
    return list(await asyncio.gather(*(fetch(url) for url in urls)))
