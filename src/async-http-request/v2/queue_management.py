import asyncio
from asyncio import Queue, Semaphore
from pathlib import Path

from aiofile import async_open
from aiohttp import ClientSession

from processing import process_single_url_with_retry


async def add_url_to_queue(queue: Queue, urls_file_path: Path):
    """Читает URL из файла и добавляет их в очередь."""
    async with async_open(urls_file_path, "r") as file:
        async for line in file:
            url = line.strip()
            if url:
                await queue.put(url)
    await queue.put(None)


async def process_urls(
    queue: Queue, output_file_path: Path, session: ClientSession, semaphore: Semaphore
):
    """Запускает обработку URL-ов."""
    tasks = []
    while True:
        url = await queue.get()
        if url is None:
            break
        task = asyncio.create_task(
            process_single_url_with_retry(url, output_file_path, session, semaphore)
        )
        tasks.append(task)
    await asyncio.gather(*tasks)
