"""Async client for the Opinet (한국석유공사 오피넷) free API.

문서: "오피넷 일반 API 이용 가이드" 의 19종 API를 모두 제공한다.
"""

from __future__ import annotations

import logging
from typing import Any

from aiohttp import ClientError, ClientSession

from .const import API_BASE

_LOGGER = logging.getLogger(__name__)


class OpinetError(Exception):
    """Base error for the Opinet API."""


class OpinetAuthError(OpinetError):
    """Raised when the API key is rejected."""


class OpinetConnectionError(OpinetError):
    """Raised when the API cannot be reached or returns garbage."""


class OpinetApi:
    """Thin wrapper around the Opinet HTTP endpoints."""

    def __init__(self, session: ClientSession, api_key: str) -> None:
        """Initialize the client."""
        self._session = session
        self._api_key = api_key

    async def _request(self, endpoint: str, **params: Any) -> list[dict[str, Any]]:
        """Call an Opinet endpoint and return the ``RESULT.OIL`` list.

        Opinet always wraps successful responses as
        ``{"RESULT": {"OIL": [...]}}``. An invalid key (or any server side
        problem) yields HTML / an error string instead, which we surface as the
        appropriate :class:`OpinetError`.
        """
        url = f"{API_BASE}/{endpoint}"
        query: dict[str, str] = {"out": "json", "code": self._api_key}
        # Drop unset optional params; stringify everything else.
        query.update(
            {key: str(value) for key, value in params.items() if value is not None}
        )
        try:
            async with self._session.get(url, params=query) as resp:
                resp.raise_for_status()
                # Opinet serves JSON with a text/html content type.
                data = await resp.json(content_type=None)
        except ClientError as err:
            raise OpinetConnectionError(f"Opinet request failed: {err}") from err
        except ValueError as err:
            # Body was not JSON -> almost always an invalid/expired key page.
            raise OpinetAuthError("Opinet returned a non-JSON response") from err

        if not isinstance(data, dict) or "RESULT" not in data:
            raise OpinetAuthError("Unexpected Opinet response (check the API key)")

        result = data["RESULT"]
        if not isinstance(result, dict):
            raise OpinetConnectionError("Malformed Opinet RESULT block")

        oil = result.get("OIL", [])
        if not isinstance(oil, list):
            raise OpinetConnectionError("Malformed Opinet OIL block")
        return oil

    # ── ① 전국 주유소 평균가격(현재) ──────────────────────────────
    async def async_get_avg_all_price(self) -> list[dict[str, Any]]:
        """① avgAllPrice.do — 전국 주유소 평균가격(현재)."""
        return await self._request("avgAllPrice.do")

    # ── ② 시도별 주유소 평균가격(현재) ────────────────────────────
    async def async_get_avg_sido_price(
        self, sido: str | None = None, prodcd: str | None = None
    ) -> list[dict[str, Any]]:
        """② avgSidoPrice.do — 시도별 주유소 평균가격(현재)."""
        return await self._request("avgSidoPrice.do", sido=sido, prodcd=prodcd)

    # ── ③ 시군구별 주유소 평균가격(현재) ──────────────────────────
    async def async_get_avg_sigun_price(
        self, sido: str, sigun: str | None = None, prodcd: str | None = None
    ) -> list[dict[str, Any]]:
        """③ avgSigunPrice.do — 시군구별 주유소 평균가격(현재)."""
        return await self._request(
            "avgSigunPrice.do", sido=sido, sigun=sigun, prodcd=prodcd
        )

    # ── ④ 최근 7일간 전국 일일 평균가격 ───────────────────────────
    async def async_get_avg_recent_price(
        self, date: str | None = None, prodcd: str | None = None
    ) -> list[dict[str, Any]]:
        """④ avgRecentPrice.do — 최근 7일간 전국 일일 평균가격."""
        return await self._request("avgRecentPrice.do", date=date, prodcd=prodcd)

    # ── ⑤ 최근 7일간 전국 일일 상표별 평균가격 ────────────────────
    async def async_get_poll_avg_recent_price(
        self, prodcd: str | None = None, pollcd: str | None = None
    ) -> list[dict[str, Any]]:
        """⑤ pollAvgRecentPrice.do — 최근 7일간 전국 일일 상표별 평균가격."""
        return await self._request(
            "pollAvgRecentPrice.do", prodcd=prodcd, pollcd=pollcd
        )

    # ── ⑥ 최근 7일간 전국 일일 지역별 평균가격 ────────────────────
    async def async_get_area_avg_recent_price(
        self, area: str, date: str | None = None, prodcd: str | None = None
    ) -> list[dict[str, Any]]:
        """⑥ areaAvgRecentPrice.do — 최근 7일간 전국 일일 지역별 평균가격."""
        return await self._request(
            "areaAvgRecentPrice.do", area=area, date=date, prodcd=prodcd
        )

    # ── ⑦ 최근 1주의 주간 평균유가(전국/시도별) ───────────────────
    async def async_get_avg_last_week(
        self, prodcd: str | None = None, sido: str | None = None
    ) -> list[dict[str, Any]]:
        """⑦ avgLastWeek.do — 최근 1주의 주간 평균유가(전국/시도별)."""
        return await self._request("avgLastWeek.do", prodcd=prodcd, sido=sido)

    # ── ⑧ 전국/지역별 최저가 주유소(TOP20) ────────────────────────
    async def async_get_low_top(
        self, prodcd: str, area: str | None = None, cnt: int | None = None
    ) -> list[dict[str, Any]]:
        """⑧ lowTop10.do — 전국/지역별 최저가 주유소(TOP20)."""
        return await self._request(
            "lowTop10.do", prodcd=prodcd, area=area, cnt=cnt
        )

    # ── ⑨ 반경 내 주유소 검색 ─────────────────────────────────────
    async def async_get_around_all(
        self,
        x: float | str,
        y: float | str,
        radius: int,
        prodcd: str,
        sort: int = 1,
    ) -> list[dict[str, Any]]:
        """⑨ aroundAll.do — 반경 내 주유소 검색 (좌표: KATEC, sort 1:가격 2:거리)."""
        return await self._request(
            "aroundAll.do", x=x, y=y, radius=radius, prodcd=prodcd, sort=sort
        )

    # ── ⑩ 주유소 상세정보(ID) ─────────────────────────────────────
    async def async_detail_by_id(self, station_id: str) -> dict[str, Any]:
        """⑩ detailById.do — 주유소 상세정보(ID)."""
        oil = await self._request("detailById.do", id=station_id)
        if not oil:
            raise OpinetConnectionError(f"No station found for id {station_id}")
        return oil[0]

    # ── ⑪ 상호로 주유소 검색 ──────────────────────────────────────
    async def async_search_by_name(
        self, osnm: str, area: str | None = None
    ) -> list[dict[str, Any]]:
        """⑪ searchByName.do — 상호로 주유소 검색 (검색어 2글자 이상)."""
        return await self._request("searchByName.do", osnm=osnm, area=area)

    # ── ⑫ 최근 7일간 전국 일일 면세유 평균가격 ────────────────────
    async def async_get_taxfree_avg_recent_price(
        self, prodcd: str | None = None
    ) -> list[dict[str, Any]]:
        """⑫ taxfreeAvgRecentPrice.do — 최근 7일간 전국 일일 면세유 평균가격."""
        return await self._request("taxfreeAvgRecentPrice.do", prodcd=prodcd)

    # ── ⑬ 최근 7일간 전국 일일 상표별 면세유 평균가격 ─────────────
    async def async_get_tax_poll_avg_recent_price(
        self, prodcd: str | None = None, pollcd: str | None = None
    ) -> list[dict[str, Any]]:
        """⑬ taxPollAvgRecentPrice.do — 최근 7일간 전국 일일 상표별 면세유 평균가격."""
        return await self._request(
            "taxPollAvgRecentPrice.do", prodcd=prodcd, pollcd=pollcd
        )

    # ── ⑭ 전국/지역별 최저가 면세유 주유소(TOP20) ─────────────────
    async def async_get_taxfree_low_top(
        self, prodcd: str, area: str | None = None, cnt: int | None = None
    ) -> list[dict[str, Any]]:
        """⑭ taxfreeLowTop20.do — 전국/지역별 최저가 면세유 주유소(TOP20)."""
        return await self._request(
            "taxfreeLowTop20.do", prodcd=prodcd, area=area, cnt=cnt
        )

    # ── ⑮ 주유소의 요소수 판매가격(지역별) ────────────────────────
    async def async_get_urea_price(self, area: str) -> list[dict[str, Any]]:
        """⑮ ureaPrice.do — 주유소의 요소수 판매가격(지역별, 시도코드 2자리)."""
        return await self._request("ureaPrice.do", area=area)

    # ── ⑯ 지역코드 조회 ───────────────────────────────────────────
    async def async_get_area_code(
        self, area: str | None = None
    ) -> list[dict[str, Any]]:
        """⑯ areaCode.do — 지역코드 조회(미입력:시도, 시도코드 입력:시군구)."""
        return await self._request("areaCode.do", area=area)

    # ── ⑰ 특정 7일간 전국 일일 평균가격 ───────────────────────────
    async def async_get_date_avg_recent_price(
        self, date: str, prodcd: str | None = None
    ) -> list[dict[str, Any]]:
        """⑰ dateAvgRecentPrice.do — 특정 7일간 전국 일일 평균가격."""
        return await self._request(
            "dateAvgRecentPrice.do", date=date, prodcd=prodcd
        )

    # ── ⑱ 특정 7일간 전국 일일 상표별 평균가격 ────────────────────
    async def async_get_date_poll_avg_recent_price(
        self, date: str, prodcd: str | None = None, pollcd: str | None = None
    ) -> list[dict[str, Any]]:
        """⑱ datePollAvgRecentPrice.do — 특정 7일간 전국 일일 상표별 평균가격."""
        return await self._request(
            "datePollAvgRecentPrice.do", date=date, prodcd=prodcd, pollcd=pollcd
        )

    # ── ⑲ 특정 7일간 전국 일일 지역별 평균가격 ────────────────────
    async def async_get_date_area_avg_recent_price(
        self, area: str, date: str, prodcd: str | None = None
    ) -> list[dict[str, Any]]:
        """⑲ dateAreaAvgRecentPrice.do — 특정 7일간 전국 일일 지역별 평균가격."""
        return await self._request(
            "dateAreaAvgRecentPrice.do", area=area, date=date, prodcd=prodcd
        )
