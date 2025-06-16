import asyncio
import json
import os
from asyncio import Queue, Semaphore

from aiofile import async_open
from aiohttp import ClientError, ClientSession, ContentTypeError


async def fetch_urls(
    urls_file_path: str, output_file_path: str, max_concurrent: int = 5
):
    if os.path.exists(output_file_path):
        os.remove(output_file_path)
    queue = asyncio.Queue()
    semaphore = Semaphore(max_concurrent)
    async with ClientSession() as session:
        await asyncio.gather(
            _add_url_to_queue(queue, urls_file_path),
            _process_url(queue, output_file_path, session, semaphore),
        )


async def _add_url_to_queue(queue: Queue, urls_file_path: str):
    """Чтец urls из файла, добавляющий их в очередь"""
    async with async_open(urls_file_path, "r") as file:
        async for line in file:
            url = line.strip()
            await queue.put(url)
    await queue.put(None)


async def _process_url(
    queue: Queue, output_file_path: str, session: ClientSession, semaphore: Semaphore
):
    """Воркер, который выполняет запрос по url, забирая их из очереди."""
    while True:
        url = await queue.get()
        if url is None:
            break
        async with semaphore:
            result_dict = await _get_url(session, url)
            await _save_resp_to_file(output_file_path, result_dict)


async def _get_url(session, url):
    try:
        async with session.get(url) as resp:
            try:
                content = await resp.json()
            except ContentTypeError:
                content = await resp.text()
            result_dict = {
                "url": url,
                "status_code": resp.status,
                "content": content,
            }
    except ClientError:
        result_dict = {
            "url": url,
            "status_code": 0,
            "content": None,
        }
    return result_dict


async def _save_resp_to_file(file_path: str, result_dict: dict):
    async with async_open(file_path, "a") as result_file:
        await result_file.write(f"{json.dumps(result_dict)}\n")


if __name__ == "__main__":
    asyncio.run(fetch_urls("./urls.txt", "./results_v2.jsonl"))
