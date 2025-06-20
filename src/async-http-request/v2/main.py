import asyncio
from asyncio import Queue, Semaphore
from pathlib import Path

from aiohttp import ClientSession, ClientTimeout

from queue_management import add_url_to_queue, process_urls

TIMEOUT = ClientTimeout(total=3600)


async def fetch_urls(
    urls_file_path: Path,
    output_file_path: Path,
    max_concurrent: int = 5,
    clear_output_file: bool = False,
):
    """Запускает обработку URL с потоковой записью в файлы."""
    if clear_output_file and output_file_path.exists():
        output_file_path.unlink(missing_ok=True)

    queue = Queue()
    semaphore = Semaphore(max_concurrent)

    async with ClientSession(timeout=TIMEOUT) as session:
        await asyncio.gather(
            add_url_to_queue(queue, urls_file_path),
            process_urls(queue, output_file_path, session, semaphore),
        )


def start():
    asyncio.run(
        fetch_urls(
            urls_file_path=Path(__file__).parent / "urls.txt",
            output_file_path=Path(__file__).parent / "results.jsonl",
            max_concurrent=5,
            clear_output_file=True,
        )
    )


if __name__ == "__main__":
    start()
