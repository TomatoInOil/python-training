import asyncio
import hashlib
import json
from asyncio import Semaphore
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

from aiofile import async_open
from aiohttp import ClientSession

MAX_RETRIES = 3
RETRY_DELAY = 5
CHUNK_SIZE = 1024 * 1024 * 100

process_pool = ProcessPoolExecutor(max_workers=2)


async def process_single_url_with_retry(
    url: str,
    output_file_path: Path,
    session: ClientSession,
    semaphore: Semaphore,
):
    """Обрабатывает один URL с retry-логикой."""
    for attempt in range(MAX_RETRIES):
        try:
            async with semaphore:
                await stream_url_to_file(session, url, output_file_path)
                return
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                await save_error_file(url, output_file_path, str(e))
                return
            retry_delay = RETRY_DELAY * (2**attempt)
            await asyncio.sleep(retry_delay)


async def stream_url_to_file(session: ClientSession, url: str, output_file_path: Path):
    """Определяет тип контента и записывает его в файл."""
    async with session.get(url) as resp:
        text = None
        temp_file_path = (
            output_file_path.parent
            / f"temp_{hashlib.sha256(url.encode()).hexdigest()}.bin"
        )
        if int(resp.headers.get("content-length", 0)) > CHUNK_SIZE:
            async with async_open(
                temp_file_path,
                "ab",
            ) as file:
                async for chunk in resp.content.iter_chunked(CHUNK_SIZE):
                    await file.write(chunk)
        else:
            text = await resp.text()

        loop = asyncio.get_running_loop()
        if text is None:
            parsed_content = await loop.run_in_executor(
                process_pool, parse_large_json, temp_file_path
            )
            temp_file_path.unlink()
        else:
            parsed_content = await loop.run_in_executor(process_pool, json.loads, text)
        async with async_open(output_file_path, "a") as file:
            await file.write(
                f"{
                    json.dumps(
                        {
                            'url': url,
                            'status_code': resp.status,
                            'content': parsed_content,
                        }
                    )
                }\n"
            )


def parse_large_json(file_path: Path) -> dict:
    with open(file_path, "r") as f:
        return json.loads(f.read())


async def save_error_file(url: str, output_file_path: Path, error: str):
    """Сохраняет ошибку в файл."""
    async with async_open(output_file_path, "a") as f:
        await f.write(
            f"{
                json.dumps(
                    {
                        'url': url,
                        'status_code': 0,
                        'error': error,
                    }
                )
            }\n"
        )
