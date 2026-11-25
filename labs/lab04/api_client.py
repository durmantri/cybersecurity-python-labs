import os
from typing import Any

import requests

API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"


class JSONResponseError(ValueError):
    """Помилка, бо NVD повернув некоректний JSON"""


class HTTPStatusError(RuntimeError):
    """Помилка, бо отримано неочікуваний HTTP-статус"""

    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        super().__init__(f"Unexpected HTTP status: {status_code}")


def build_headers() -> dict[str, str]:
    """Формує заголовки запиту до NVD API."""

    headers = {"Accept": "application/json"}

    # API-ключ зі змінної середовища
    api_key = os.getenv("NVD_API_KEY")

    # Додаємо ключ лише тоді, коли він непорожній
    if api_key and api_key.strip():
        headers["apiKey"] = api_key.strip()

    return headers


def fetch_response(cve_id: str) -> Any:
    """Виконує GET-запит до NVD та повертає JSON-відповідь."""

    response = requests.get(
        API_URL,
        params={"cveId": cve_id},
        headers=build_headers(),
        timeout=(3.05, 10),
        allow_redirects=False,
    )

    # Перевіряємо HTTP-помилки
    response.raise_for_status()

    # Дозволений лише статус 200
    if response.status_code != 200:
        raise HTTPStatusError(response.status_code)

    # Декодуємо JSON
    try:
        return response.json()
    except ValueError as exc:
        raise JSONResponseError("NVD повернув некоректний JSON.") from exc
