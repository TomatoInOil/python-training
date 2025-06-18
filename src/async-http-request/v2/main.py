import asyncio
import os
from asyncio import Queue, Semaphore
from pathlib import Path

from aiohttp import ClientSession, ClientTimeout

from queue_management import add_url_to_queue, process_urls

TIMEOUT = ClientTimeout(total=3600)


async def fetch_urls(
    urls_file_path: Path, results_dir_path: Path, max_concurrent: int = 5
):
    """Запускает обработку URL с потоковой записью в файлы."""
    os.makedirs(results_dir_path, exist_ok=True)
    queue = Queue()
    semaphore = Semaphore(max_concurrent)

    async with ClientSession(timeout=TIMEOUT) as session:
        await asyncio.gather(
            add_url_to_queue(queue, urls_file_path),
            process_urls(queue, results_dir_path, session, semaphore),
        )


def start():
    asyncio.run(
        fetch_urls(
            urls_file_path=Path(__file__).parent / "urls.txt",
            results_dir_path=Path(__file__).parent / "results",
            max_concurrent=5,
        )
    )

if __name__ == "__main__":
    start()
