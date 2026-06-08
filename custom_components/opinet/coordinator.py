"""Data update coordinators for Opinet.

폴링 인터벌 대신, 오피넷 가이드의 가격 업데이트 시각(분/초 0)에 맞춰
지정된 시각에만 갱신한다.
"""

from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import OpinetApi, OpinetError
from .const import (
    DAILY_AVG_UPDATE_HOURS,
    DEFAULT_REFRESH_OFFSET_MINUTES,
    DOMAIN,
    PRICE_UPDATE_HOURS,
    WEEKLY_UPDATE_HOURS,
    WEEKLY_UPDATE_WEEKDAY,
)

_LOGGER = logging.getLogger(__name__)


def _to_float(value: Any) -> float | None:
    """Coerce an Opinet price/diff string into a float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class OpinetScheduledCoordinator(DataUpdateCoordinator[Any]):
    """Coordinator that refreshes at fixed clock times instead of an interval.

    ``update_hours`` 의 각 시각(분/초 0)에 갱신하며, ``update_weekday`` 가 지정되면
    해당 요일에만 갱신한다(주간 평균가격용, 월=0 … 금=4).
    """

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: OpinetApi,
        name: str,
        update_hours: tuple[int, ...],
        update_weekday: int | None = None,
        offset_minutes: int = DEFAULT_REFRESH_OFFSET_MINUTES,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=name,
            update_interval=None,  # 시각 기반 스케줄 사용
        )
        self._api = api
        self._update_hours = update_hours
        self._update_weekday = update_weekday
        self._offset_minutes = offset_minutes

    @callback
    def async_setup_schedule(self) -> None:
        """오피넷 업데이트 시각(+오프셋 분)마다 갱신을 예약한다.

        서버가 정시에 데이터를 갱신하므로, 곧바로 조회하면 갱신 전 값을 받을 수
        있어 ``REFRESH_OFFSET_MINUTES`` 만큼 지난 뒤 조회한다.
        """
        for hour in self._update_hours:
            unsub = async_track_time_change(
                self.hass,
                self._handle_scheduled_refresh,
                hour=hour,
                minute=self._offset_minutes,
                second=0,
            )
            if self.config_entry is not None:
                self.config_entry.async_on_unload(unsub)

    async def _handle_scheduled_refresh(self, now: datetime) -> None:
        """예약된 시각에 호출되어 갱신한다(요일 조건 확인)."""
        if self._update_weekday is not None and now.weekday() != self._update_weekday:
            return
        await self.async_request_refresh()


class OpinetAvgCoordinator(OpinetScheduledCoordinator):
    """전국 주유소 평균가격(현재) — 1, 2, 9, 12, 16, 19시 갱신."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: OpinetApi,
        offset_minutes: int = DEFAULT_REFRESH_OFFSET_MINUTES,
    ) -> None:
        super().__init__(
            hass,
            entry,
            api,
            name=f"{DOMAIN} 전국 평균가격",
            update_hours=PRICE_UPDATE_HOURS,
            offset_minutes=offset_minutes,
        )

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        try:
            rows = await self._api.async_get_avg_all_price()
        except OpinetError as err:
            raise UpdateFailed(str(err)) from err

        # Keyed by product code (PRODCD).
        return {
            row["PRODCD"]: {
                "name": row.get("PRODNM"),
                "price": _to_float(row.get("PRICE")),
                "diff": _to_float(row.get("DIFF")),
                "trade_dt": row.get("TRADE_DT"),
            }
            for row in rows
            if row.get("PRODCD")
        }


class OpinetRecentAvgCoordinator(OpinetScheduledCoordinator):
    """최근 7일간 전국 일일 평균가격 — 매일 0시 갱신, 최신일자 값 사용."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: OpinetApi,
        offset_minutes: int = DEFAULT_REFRESH_OFFSET_MINUTES,
    ) -> None:
        super().__init__(
            hass,
            entry,
            api,
            name=f"{DOMAIN} 전국 일일 평균가격",
            update_hours=DAILY_AVG_UPDATE_HOURS,
            offset_minutes=offset_minutes,
        )

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        try:
            rows = await self._api.async_get_avg_recent_price()
        except OpinetError as err:
            raise UpdateFailed(str(err)) from err

        # 제품별로 가장 최근 일자의 값만 남긴다.
        result: dict[str, dict[str, Any]] = {}
        for row in rows:
            prodcd = row.get("PRODCD")
            if not prodcd:
                continue
            date = row.get("DATE")
            current = result.get(prodcd)
            if current is None or (date and date > current.get("date", "")):
                result[prodcd] = {
                    "price": _to_float(row.get("PRICE")),
                    "date": date,
                }
        return result


class OpinetWeeklyAvgCoordinator(OpinetScheduledCoordinator):
    """최근 1주의 전국 주간 평균유가 — 금요일 10시 갱신."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: OpinetApi,
        offset_minutes: int = DEFAULT_REFRESH_OFFSET_MINUTES,
    ) -> None:
        super().__init__(
            hass,
            entry,
            api,
            name=f"{DOMAIN} 전국 주간 평균가격",
            update_hours=WEEKLY_UPDATE_HOURS,
            update_weekday=WEEKLY_UPDATE_WEEKDAY,
            offset_minutes=offset_minutes,
        )

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        try:
            rows = await self._api.async_get_avg_last_week()
        except OpinetError as err:
            raise UpdateFailed(str(err)) from err

        # AREA_CD 00 = 전국.
        result: dict[str, dict[str, Any]] = {}
        for row in rows:
            if row.get("AREA_CD") not in (None, "00", "0"):
                continue
            prodcd = row.get("PRODCD")
            if not prodcd:
                continue
            result[prodcd] = {
                "price": _to_float(row.get("PRICE")),
                "week": row.get("WEEK"),
                "sta_dt": row.get("STA_DT"),
                "end_dt": row.get("END_DT"),
            }
        return result


class OpinetStationCoordinator(OpinetScheduledCoordinator):
    """단일 주유소 상세/판매가격(현재) — 1, 2, 9, 12, 16, 19시 갱신."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: OpinetApi,
        station_id: str,
        offset_minutes: int = DEFAULT_REFRESH_OFFSET_MINUTES,
    ) -> None:
        super().__init__(
            hass,
            entry,
            api,
            name=f"{DOMAIN} 주유소 {station_id}",
            update_hours=PRICE_UPDATE_HOURS,
            offset_minutes=offset_minutes,
        )
        self.station_id = station_id

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            detail = await self._api.async_detail_by_id(self.station_id)
        except OpinetError as err:
            raise UpdateFailed(str(err)) from err

        prices: dict[str, dict[str, Any]] = {}
        for item in detail.get("OIL_PRICE", []) or []:
            prodcd = item.get("PRODCD")
            if not prodcd:
                continue
            prices[prodcd] = {
                "price": _to_float(item.get("PRICE")),
                "trade_dt": item.get("TRADE_DT"),
                "trade_tm": item.get("TRADE_TM"),
            }

        return {
            "uni_id": detail.get("UNI_ID", self.station_id),
            "name": detail.get("OS_NM"),
            "brand": detail.get("POLL_DIV_CD"),
            "tel": detail.get("TEL"),
            "address": detail.get("NEW_ADR") or detail.get("VAN_ADR"),
            "kpetro_yn": detail.get("KPETRO_YN"),
            "good_yn": detail.get("GOOD_YN"),
            "car_wash_yn": detail.get("CAR_WASH_YN"),
            "maint_yn": detail.get("MAINT_YN"),
            "cvs_yn": detail.get("CVS_YN"),
            "prices": prices,
        }
