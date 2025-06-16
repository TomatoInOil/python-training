import re
from typing import Callable, Optional

import requests

EXTERNAL_API_URL = "https://api.exchangerate-api.com/v4/latest/{currency}"
REGEX_PATH_INFO = r"^/(?P<currency>[A-Z]+)$"


def app(
    environ: dict[str, str],
    start_response: Callable[[str, list[tuple[str, str]]], None],
) -> list[bytes]:
    path_info = _validate_path(environ)
    if path_info is None:
        return _handle_not_found(start_response)
    allowed_methods = ("GET",)
    if _validate_method(allowed_methods, environ):
        return _handle_not_allowed(start_response, allowed_methods)

    return _process_request(start_response, path_info.group("currency"))


def _process_request(
    start_response: Callable[[str, list[tuple[str, str]]], None], currency: str
) -> list[bytes]:
    response = _fetch_external_api_data(currency)
    data = response.content
    response_headers = _build_response_headers(data)
    status = str(response.status_code)
    start_response(status, response_headers)
    return [data]


def _build_response_headers(data: bytes) -> list[tuple[str, str]]:
    response_headers = [
        ("Content-type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(data))),
    ]
    return response_headers


def _fetch_external_api_data(currency: str) -> requests.Response:
    response = requests.get(EXTERNAL_API_URL.format(currency=currency))
    return response


def _validate_method(allowed_methods: tuple[str, ...], environ) -> bool:
    return environ["REQUEST_METHOD"] not in allowed_methods


def _validate_path(environ: dict[str, str]) -> Optional[re.Match]:
    path_info = re.fullmatch(REGEX_PATH_INFO, environ["PATH_INFO"])
    return path_info


def _handle_not_allowed(
    start_response: Callable[[str, list[tuple[str, str]]], None],
    allowed_methods: tuple[str],
) -> list[bytes]:
    start_response(
        "405 METHOD NOT ALLOWED",
        [("Content-Length", "0"), ("Allow", ", ".join(allowed_methods))],
    )
    return []


def _handle_not_found(
    start_response: Callable[[str, list[tuple[str, str]]], None],
) -> list[bytes]:
    start_response("404 NOT FOUND", [("Content-Length", "0")])
    return []


if __name__ == "__main__":
    from waitress import serve

    serve(app)
