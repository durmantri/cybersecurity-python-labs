from unittest.mock import Mock

import pytest
import requests

from labs.lab04 import api_client

API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"


def test_without_api_key():
    """Тест без api ключа"""
    assert api_client.build_headers() == {"Accept": "application/json"}


def test_with_api_key(monkeypatch):
    """Тест з api ключем"""
    monkeypatch.setenv("NVD_API_KEY", "fake-test-key-123")
    assert api_client.build_headers() == {
        "Accept": "application/json",
        "apiKey": "fake-test-key-123",
    }


def test_get_success(monkeypatch):
    """Тест успішного get запиту"""
    payload = {"startIndex": 0, "totalResults": 0, "vulnerabilities": []}
    response = Mock(spec=requests.Response)
    response.status_code = 200
    response.headers = {"Content-Type": "application/json; charset=utf-8"}
    response.json.return_value = payload
    fake_get = Mock(return_value=response)
    monkeypatch.setattr(api_client.requests, "get", fake_get)

    assert api_client.fetch_response("CVE-2099-10001") == payload
    fake_get.assert_called_once_with(
        API_URL,
        params={"cveId": "CVE-2099-10001"},
        headers={"Accept": "application/json"},
        timeout=(3.05, 10),
        allow_redirects=False,
    )
    response.raise_for_status.assert_called_once_with()


@pytest.mark.parametrize(
    "network_error",
    [
        requests.exceptions.Timeout("timeout"),
        requests.exceptions.ConnectionError("network unreachable"),
    ],
    ids=["timeout", "network unreachable"],
)
def test_fetch_response_network_error(monkeypatch, network_error):
    """Мережеві помилки"""
    fake_get = Mock(side_effect=network_error)
    monkeypatch.setattr(api_client.requests, "get", fake_get)

    with pytest.raises(requests.exceptions.RequestException):
        api_client.fetch_response("CVE-2099-10001")


def test_fetch_response_http_error(monkeypatch):
    """HTTP-помилка"""
    response = Mock(spec=requests.Response)
    response.status_code = 404
    response.raise_for_status.side_effect = requests.HTTPError(response=response)

    monkeypatch.setattr(api_client.requests, "get", Mock(return_value=response))

    with pytest.raises(requests.HTTPError):
        api_client.fetch_response("CVE-2099-10001")
