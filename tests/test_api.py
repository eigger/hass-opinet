"""api.py 단위 테스트."""
import asyncio
import traceback
from unittest.mock import MagicMock

from aiohttp import ClientConnectionError, ClientResponseError, RequestInfo
import pytest
from yarl import URL

from custom_components.opinet.api import (
    OpinetApi,
    OpinetConnectionError,
    _strip_values,
)


def test_strip_values_string():
    assert _strip_values("  test_string\r\n ") == "test_string"


def test_strip_values_list():
    assert _strip_values(["  a\r\n", " b "]) == ["a", "b"]


def test_strip_values_dict():
    assert _strip_values({"key1": "  val1\n", "key2": ["  val2  "]}) == {
        "key1": "val1",
        "key2": ["val2"],
    }


def test_request_client_response_error_does_not_leak_api_key():
    """ClientResponseError 발생 시 URL/API 키가 에러 메시지에 노출되지 않는지 검증."""
    api_key = "SECRET_API_KEY_12345"
    session = MagicMock()
    url = URL(f"http://www.opinet.co.kr/api/avgAllPrice.do?out=json&code={api_key}")
    request_info = RequestInfo(url=url, method="GET", headers={}, real_url=url)
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = ClientResponseError(
        request_info=request_info,
        history=(),
        status=500,
        message="Internal Server Error",
    )
    session.get.return_value.__aenter__.return_value = mock_resp

    api = OpinetApi(session, api_key)
    with pytest.raises(OpinetConnectionError) as exc_info:
        asyncio.run(api.async_get_avg_all_price())

    assert exc_info.value.__cause__ is None
    assert api_key not in str(exc_info.value)
    assert "status 500" in str(exc_info.value)
    tb = "".join(traceback.format_exception(exc_info.value))
    assert api_key not in tb


def test_request_client_error_does_not_leak_api_key():
    """일반 ClientError 발생 시 URL/API 키가 에러 메시지 및 traceback에 노출되지 않고 클래스명이 표시되는지 검증."""
    api_key = "SECRET_API_KEY_12345"
    session = MagicMock()
    session.get.side_effect = ClientConnectionError(f"Connection failed: code={api_key}")

    api = OpinetApi(session, api_key)
    with pytest.raises(OpinetConnectionError) as exc_info:
        asyncio.run(api.async_get_avg_all_price())

    assert exc_info.value.__cause__ is None
    assert api_key not in str(exc_info.value)
    assert "ClientConnectionError" in str(exc_info.value)
    tb = "".join(traceback.format_exception(exc_info.value))
    assert api_key not in tb
