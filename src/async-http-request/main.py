import asyncio
import json
import os
from asyncio import Semaphore

import aiohttp
from aiofile import async_open

urls = [
    "https://example.com",
    "https://httpbin.org/status/404",
    "https://nonexistent.url",
]


async def fetch_urls(urls: list[str], file_path: str, max_concurrent: int = 5):
    if os.path.exists(file_path):
        os.remove(file_path)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(
                asyncio.create_task(
                    process_url(file_path, max_concurrent, session, url)
                )
            )
        await asyncio.gather(*tasks)


async def process_url(file_path, max_concurrent, session, url):
    async with Semaphore(max_concurrent):
        result_dict = await get_url(session, url)
        await save_resp_to_file(file_path, result_dict)


async def get_url(session, url):
    try:
        async with session.get(url) as resp:
            result_dict = {"url": url, "status_code": resp.status}
    except aiohttp.ClientError:
        result_dict = {"url": url, "status_code": 0}
    return result_dict


async def save_resp_to_file(file_path: str, result_dict: dict):
    async with async_open(file_path, "a") as result_file:
        await result_file.write(json.dumps(result_dict))
        await result_file.write("\n")


if __name__ == "__main__":
    asyncio.run(fetch_urls(urls, "./results.jsonl"))
