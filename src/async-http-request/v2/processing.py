import asyncio
import base64
import hashlib
import json
from asyncio import Semaphore
from pathlib import Path

from aiofile import async_open
from aiohttp import ClientSession

MAX_RETRIES = 3
RETRY_DELAY = 5


async def process_single_url_with_retry(
    url: str, results_jsonl_path: Path, output_dir_path: Path, session: ClientSession, semaphore: Semaphore
):
    """Обрабатывает один URL с retry-логикой."""
    for attempt in range(MAX_RETRIES):
        try:
            async with semaphore:
                output_path = output_dir_path / f"{hashlib.sha256(url.encode()).hexdigest()}.json"
                await stream_url_to_file(session, url, output_path, results_jsonl_path)
                return
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                error_path = output_dir_path / f"error_{hashlib.sha256(url.encode()).hexdigest()}.json"
                await save_error_file(url, error_path, str(e))
                return
            retry_delay = RETRY_DELAY * (2**attempt)
            await asyncio.sleep(retry_delay)


async def stream_url_to_file(session: ClientSession, url: str, output_file_path: Path, results_jsonl_path: Path):
    """Определяет тип контента и записывает его в файл."""
    async with session.get(url) as resp:
        content_type = resp.headers.get("Content-Type", "").lower()
        content_disposition = resp.headers.get("Content-Disposition", "")
        async with async_open(output_file_path, "w") as file:

            await file.write(
                '{"url": '
                + json.dumps(url)
                + ', "status_code": '
                + str(resp.status)
                + ', "content_type": '
                + json.dumps(content_type)
                + ', "content_disposition": '
                + json.dumps(content_disposition)
                + ', "content": '
            )

            if "application/json" in content_type:
                async for chunk in resp.content.iter_chunked(10 * 1024 * 1024):
                    await file.write(chunk.decode("utf-8", errors="replace"))
                await file.write("}")

            elif "text/" in content_type:
                await file.write('"')
                async for chunk in resp.content.iter_chunked(10 * 1024 * 1024):
                    await file.write(chunk.decode("utf-8", errors="replace"))
                await file.write('"}')
            else:
                await file.write('"')
                await stream_binary_to_base64(resp, file)
                await file.write('"}')
    async with async_open(results_jsonl_path, "a+") as file:
        line_data = {"url": url, "output_file_path": str(output_file_path)}
        await file.write(f"{json.dumps(line_data)}\n")


async def stream_binary_to_base64(resp, file):
    """Кодирует бинарные данные в Base64 и пишет в файл."""
    b64_encoder = base64.b64encode
    async for chunk in resp.content.iter_chunked(10 * 1024 * 1024):
        await file.write(b64_encoder(chunk).decode("utf-8"))


async def save_error_file(url: str, error_path: Path, error: str):
    """Сохраняет ошибку в файл."""
    async with async_open(error_path, "w") as f:
        await f.write(
            json.dumps(
                {
                    "url": url,
                    "status_code": 0,
                    "error": error,
                }
            )
        )
