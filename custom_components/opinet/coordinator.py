"""Data update coordinators for Opinet.

폴링 인터벌 대신, 오피넷 가이드의 가격 업데이트 시각(분/초 0)에 맞춰
지정된 시각에만 갱신한다.
"""

from __future__ import annotations

from datetime import datetime
import logging
from typing import Any, NoReturn

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import OpinetApi, OpinetAuthError, OpinetError
from .const import (
    DAILY_AVG_UPDATE_HOURS,
    DEFAULT_REFRESH_OFFSET_MINUTES,
    DOMAIN,
    PRICE_UPDATE_HOURS,
    UREA_UPDATE_HOURS,
    WEEKLY_UPDATE_HOURS,
    WEEKLY_UPDATE_WEEKDAY,
    brand_label,
    poll_div_code,
    station_type_label,
)
from .geo import katec_to_wgs84

_LOGGER = logging.getLogger(__name__)


def _to_float(value: Any) -> float | None:
    """Coerce an Opinet price/diff string into a float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _raise_update_error(err: OpinetError) -> NoReturn:
    """인증 오류는 reauth 를 트리거하고, 그 외는 일반 갱신 실패로 처리한다."""
    if isinstance(err, OpinetAuthError):
        raise ConfigEntryAuthFailed(str(err)) from err
    raise UpdateFailed(str(err)) from err


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
            name=f"{DOMAIN} nationwide average price",
            update_hours=PRICE_UPDATE_HOURS,
            offset_minutes=offset_minutes,
        )

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        try:
            rows = await self._api.async_get_avg_all_price()
        except OpinetError as err:
            _raise_update_error(err)

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
            name=f"{DOMAIN} nationwide daily average price",
            update_hours=DAILY_AVG_UPDATE_HOURS,
            offset_minutes=offset_minutes,
        )

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        try:
            rows = await self._api.async_get_avg_recent_price()
        except OpinetError as err:
            _raise_update_error(err)

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
            name=f"{DOMAIN} nationwide weekly average price",
            update_hours=WEEKLY_UPDATE_HOURS,
            update_weekday=WEEKLY_UPDATE_WEEKDAY,
            offset_minutes=offset_minutes,
        )

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        try:
            rows = await self._api.async_get_avg_last_week()
        except OpinetError as err:
            _raise_update_error(err)

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
            name=f"{DOMAIN} station {station_id}",
            update_hours=PRICE_UPDATE_HOURS,
            offset_minutes=offset_minutes,
        )
        self.station_id = station_id

    @property
    def brand_name(self) -> str | None:
        """Human-readable oil company / brand label."""
        return brand_label((self.data or {}).get("brand"))

    @property
    def station_type(self) -> str:
        """Device model label from LPG_YN (gas / LPG / both)."""
        return station_type_label((self.data or {}).get("lpg_yn"))

    @property
    def device_info(self) -> DeviceInfo:
        """주유소 기기 정보. 제조사=정유사(상표), 모델=업종, 허브 기기의 하위로 연결된다."""
        data = self.data or {}
        refiner = self.brand_name
        entry_id = self.config_entry.entry_id if self.config_entry else ""
        return DeviceInfo(
            identifiers={(DOMAIN, self.station_id)},
            # 기기 이름은 실제 주유소 상호(데이터) — 라벨이 아니므로 그대로 사용.
            name=data.get("name") or self.station_id,
            manufacturer=refiner or None,
            model=self.station_type,
            via_device=(DOMAIN, entry_id),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            detail = await self._api.async_detail_by_id(self.station_id)
        except OpinetError as err:
            _raise_update_error(err)

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

        # KATEC 좌표 → 위경도(WGS84) 변환 (pyproj는 블로킹이라 executor 에서).
        gis_x = _to_float(detail.get("GIS_X_COOR"))
        gis_y = _to_float(detail.get("GIS_Y_COOR"))
        latitude: float | None = None
        longitude: float | None = None
        if gis_x is not None and gis_y is not None:
            latitude, longitude = await self.hass.async_add_executor_job(
                katec_to_wgs84, gis_x, gis_y
            )

        return {
            "uni_id": detail.get("UNI_ID", self.station_id),
            "name": detail.get("OS_NM"),
            "brand": poll_div_code(detail),
            "sigun": detail.get("SIGUNCD"),
            "lpg_yn": detail.get("LPG_YN"),
            "tel": detail.get("TEL"),
            "address": detail.get("NEW_ADR") or detail.get("VAN_ADR"),
            "kpetro_yn": detail.get("KPETRO_YN"),
            "good_yn": detail.get("GOOD_YN"),
            "car_wash_yn": detail.get("CAR_WASH_YN"),
            "maint_yn": detail.get("MAINT_YN"),
            "cvs_yn": detail.get("CVS_YN"),
            "gis_x": gis_x,
            "gis_y": gis_y,
            "latitude": latitude,
            "longitude": longitude,
            "prices": prices,
        }


class OpinetUreaCoordinator(OpinetScheduledCoordinator):
    """등록 주유소의 요소수 판매가격/재고 — 7, 13, 18, 24(0)시 갱신.

    요소수 API(``ureaPrice.do``)는 시도(2자리) 단위 벌크 조회만 제공하므로,
    등록된 주유소들의 시도코드 집합을 한 번씩 조회한 뒤 ``UNI_ID`` 로 키잉한다.
    같은 시도에 주유소가 여러 개여도 호출은 시도당 1회다.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: OpinetApi,
        areas: set[str],
        offset_minutes: int = DEFAULT_REFRESH_OFFSET_MINUTES,
    ) -> None:
        super().__init__(
            hass,
            entry,
            api,
            name=f"{DOMAIN} urea price",
            update_hours=UREA_UPDATE_HOURS,
            offset_minutes=offset_minutes,
        )
        self._areas = set(areas)

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}
        for area in self._areas:
            try:
                rows = await self._api.async_get_urea_price(area)
            except OpinetError as err:
                _raise_update_error(err)
            for row in rows:
                uni_id = row.get("UNI_ID")
                if not uni_id:
                    continue
                result[uni_id] = {
                    "stock": row.get("STOCK_YN"),
                    "price": _to_float(row.get("PRICE")),
                    "trade_dt": row.get("TRADE_DT"),
                    "trade_tm": row.get("TRADE_TM"),
                }
        return result
