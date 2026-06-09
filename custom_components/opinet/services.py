"""Service calls exposing every Opinet API endpoint.

센서로 노출하기 애매한(좌표/날짜/검색어/TOP-N/목록 반환) API는 모두
``response`` 를 돌려주는 서비스로 제공한다. 호출 시 ``return_response`` 로 결과를
받는다.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

import voluptuous as vol

from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
    callback,
)
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.service import (
    ALL_SERVICE_DESCRIPTIONS_CACHE,
    SERVICE_DESCRIPTION_CACHE,
)

from .api import OpinetApi, OpinetError
from .const import DOMAIN
from .geo import wgs84_to_katec

SERVICE_GET_AROUND = "get_around"
SERVICE_GET_STATION_DETAIL = "get_station_detail"

_GET_AROUND_SCHEMA = vol.Schema(
    {
        vol.Optional("entity_id"): cv.entity_id,
        vol.Optional("latitude"): vol.Coerce(float),
        vol.Optional("longitude"): vol.Coerce(float),
        vol.Required("radius"): vol.All(vol.Coerce(int), vol.Range(1, 5000)),
        vol.Required("prodcd"): cv.string,
        vol.Optional("sort", default=1): vol.All(vol.Coerce(int), vol.In([1, 2])),
    }
)

_GET_STATION_DETAIL_SCHEMA = vol.Schema(
    {
        vol.Optional("device_id"): cv.string,
        vol.Optional("station_id"): cv.string,
    }
)

# 각 서비스: (이름, 스키마, api 호출 콜백)
type _Handler = Callable[[OpinetApi, dict[str, Any]], Awaitable[list[dict[str, Any]]]]

_SERVICES: list[tuple[str, vol.Schema, _Handler]] = [
    # ① 전국 평균가격(현재)
    (
        "get_avg_all_price",
        vol.Schema({}),
        lambda api, d: api.async_get_avg_all_price(),
    ),
    # ② 시도별 평균가격(현재)
    (
        "get_avg_sido_price",
        vol.Schema(
            {vol.Optional("sido"): cv.string, vol.Optional("prodcd"): cv.string}
        ),
        lambda api, d: api.async_get_avg_sido_price(d.get("sido"), d.get("prodcd")),
    ),
    # ③ 시군구별 평균가격(현재)
    (
        "get_avg_sigun_price",
        vol.Schema(
            {
                vol.Required("sido"): cv.string,
                vol.Optional("sigun"): cv.string,
                vol.Optional("prodcd"): cv.string,
            }
        ),
        lambda api, d: api.async_get_avg_sigun_price(
            d["sido"], d.get("sigun"), d.get("prodcd")
        ),
    ),
    # ④ 최근 7일 전국 일일 평균가격
    (
        "get_avg_recent_price",
        vol.Schema(
            {vol.Optional("date"): cv.string, vol.Optional("prodcd"): cv.string}
        ),
        lambda api, d: api.async_get_avg_recent_price(d.get("date"), d.get("prodcd")),
    ),
    # ⑤ 최근 7일 전국 일일 상표별 평균가격
    (
        "get_poll_avg_recent_price",
        vol.Schema(
            {vol.Optional("prodcd"): cv.string, vol.Optional("pollcd"): cv.string}
        ),
        lambda api, d: api.async_get_poll_avg_recent_price(
            d.get("prodcd"), d.get("pollcd")
        ),
    ),
    # ⑥ 최근 7일 전국 일일 지역별 평균가격
    (
        "get_area_avg_recent_price",
        vol.Schema(
            {
                vol.Required("area"): cv.string,
                vol.Optional("date"): cv.string,
                vol.Optional("prodcd"): cv.string,
            }
        ),
        lambda api, d: api.async_get_area_avg_recent_price(
            d["area"], d.get("date"), d.get("prodcd")
        ),
    ),
    # ⑦ 최근 1주 주간 평균유가(전국/시도별)
    (
        "get_avg_last_week",
        vol.Schema(
            {vol.Optional("prodcd"): cv.string, vol.Optional("sido"): cv.string}
        ),
        lambda api, d: api.async_get_avg_last_week(d.get("prodcd"), d.get("sido")),
    ),
    # ⑧ 전국/지역별 최저가 주유소(TOP20)
    (
        "get_low_top",
        vol.Schema(
            {
                vol.Required("prodcd"): cv.string,
                vol.Optional("area"): cv.string,
                vol.Optional("cnt"): vol.All(vol.Coerce(int), vol.Range(1, 20)),
            }
        ),
        lambda api, d: api.async_get_low_top(d["prodcd"], d.get("area"), d.get("cnt")),
    ),
    # ⑨ 반경 내 주유소 검색 → get_around 로 별도 등록(위경도→KATEC 변환 필요)
    # ⑩ 주유소 상세정보 → get_station_detail 로 별도 등록(등록 주유소 선택 지원)
    # ⑪ 상호로 주유소 검색
    (
        "search_station",
        vol.Schema(
            {vol.Required("osnm"): cv.string, vol.Optional("area"): cv.string}
        ),
        lambda api, d: api.async_search_by_name(d["osnm"], d.get("area")),
    ),
    # ⑫ 최근 7일 전국 일일 면세유 평균가격
    (
        "get_taxfree_avg_recent_price",
        vol.Schema({vol.Optional("prodcd"): cv.string}),
        lambda api, d: api.async_get_taxfree_avg_recent_price(d.get("prodcd")),
    ),
    # ⑬ 최근 7일 전국 일일 상표별 면세유 평균가격
    (
        "get_taxfree_poll_avg_recent_price",
        vol.Schema(
            {vol.Optional("prodcd"): cv.string, vol.Optional("pollcd"): cv.string}
        ),
        lambda api, d: api.async_get_tax_poll_avg_recent_price(
            d.get("prodcd"), d.get("pollcd")
        ),
    ),
    # ⑭ 전국/지역별 최저가 면세유 주유소(TOP20)
    (
        "get_taxfree_low_top",
        vol.Schema(
            {
                vol.Required("prodcd"): cv.string,
                vol.Optional("area"): cv.string,
                vol.Optional("cnt"): vol.All(vol.Coerce(int), vol.Range(1, 20)),
            }
        ),
        lambda api, d: api.async_get_taxfree_low_top(
            d["prodcd"], d.get("area"), d.get("cnt")
        ),
    ),
    # ⑮ 요소수 판매가격(지역별)
    (
        "get_urea_price",
        vol.Schema({vol.Required("area"): cv.string}),
        lambda api, d: api.async_get_urea_price(d["area"]),
    ),
    # ⑯ 지역코드 조회
    (
        "get_area_code",
        vol.Schema({vol.Optional("area"): cv.string}),
        lambda api, d: api.async_get_area_code(d.get("area")),
    ),
    # ⑰ 특정 7일 전국 일일 평균가격
    (
        "get_date_avg_recent_price",
        vol.Schema(
            {vol.Required("date"): cv.string, vol.Optional("prodcd"): cv.string}
        ),
        lambda api, d: api.async_get_date_avg_recent_price(d["date"], d.get("prodcd")),
    ),
    # ⑱ 특정 7일 전국 일일 상표별 평균가격
    (
        "get_date_poll_avg_recent_price",
        vol.Schema(
            {
                vol.Required("date"): cv.string,
                vol.Optional("prodcd"): cv.string,
                vol.Optional("pollcd"): cv.string,
            }
        ),
        lambda api, d: api.async_get_date_poll_avg_recent_price(
            d["date"], d.get("prodcd"), d.get("pollcd")
        ),
    ),
    # ⑲ 특정 7일 전국 일일 지역별 평균가격
    (
        "get_date_area_avg_recent_price",
        vol.Schema(
            {
                vol.Required("area"): cv.string,
                vol.Required("date"): cv.string,
                vol.Optional("prodcd"): cv.string,
            }
        ),
        lambda api, d: api.async_get_date_area_avg_recent_price(
            d["area"], d["date"], d.get("prodcd")
        ),
    ),
]


def _station_id_from_device(hass: HomeAssistant, device_id: str) -> str:
    """선택한 기기(등록된 주유소)에서 주유소 ID를 추출한다."""
    device = dr.async_get(hass).async_get(device_id)
    if device is None:
        raise HomeAssistantError(f"기기 {device_id} 를 찾을 수 없습니다.")
    # 허브(entry_id) 식별자는 제외하고, 주유소 식별자 (DOMAIN, 주유소ID) 만 추출.
    excluded = set(device.config_entries)
    for domain, identifier in device.identifiers:
        if domain == DOMAIN and identifier not in excluded:
            return identifier
    raise HomeAssistantError("선택한 기기에서 주유소 ID를 찾을 수 없습니다.")


def _get_api(hass: HomeAssistant) -> OpinetApi:
    """로드된 Opinet 엔트리에서 API 클라이언트를 얻는다."""
    for entry in hass.config_entries.async_entries(DOMAIN):
        runtime = getattr(entry, "runtime_data", None)
        if runtime is not None:
            return runtime.api
    raise HomeAssistantError("Opinet 통합이 아직 로드되지 않았습니다.")


def _resolve_location(
    hass: HomeAssistant, data: dict[str, Any]
) -> tuple[float, float]:
    """엔티티 → 위경도 → 홈 좌표 순으로 위치를 결정한다."""
    entity_id = data.get("entity_id")
    if entity_id:
        state = hass.states.get(entity_id)
        if state is None:
            raise HomeAssistantError(f"엔티티 {entity_id} 를 찾을 수 없습니다.")
        lat = state.attributes.get("latitude")
        lon = state.attributes.get("longitude")
        if lat is None or lon is None:
            raise HomeAssistantError(
                f"{entity_id} 에 위치(위경도) 정보가 없습니다."
            )
        return float(lat), float(lon)

    if data.get("latitude") is not None and data.get("longitude") is not None:
        return float(data["latitude"]), float(data["longitude"])

    if hass.config.latitude is None or hass.config.longitude is None:
        raise HomeAssistantError(
            "위치가 지정되지 않았고 홈(Home) 좌표도 설정되어 있지 않습니다."
        )
    return hass.config.latitude, hass.config.longitude


@callback
def _invalidate_service_descriptions(hass: HomeAssistant) -> None:
    """services.yaml 기반 UI 필드 정의를 다시 읽도록 캐시를 비운다."""
    service_names = [name for name, _schema, _handler in _SERVICES] + [
        SERVICE_GET_AROUND,
        SERVICE_GET_STATION_DETAIL,
    ]
    if descriptions_cache := hass.data.get(SERVICE_DESCRIPTION_CACHE):
        for name in service_names:
            descriptions_cache.pop((DOMAIN, name), None)
    hass.data.pop(ALL_SERVICE_DESCRIPTIONS_CACHE, None)


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """모든 Opinet 데이터 조회 서비스를 등록한다(중복 등록 방지)."""

    def _make(handler: _Handler):
        async def _service(call: ServiceCall) -> ServiceResponse:
            api = _get_api(hass)
            try:
                rows = await handler(api, dict(call.data))
            except OpinetError as err:
                raise HomeAssistantError(f"Opinet 요청 실패: {err}") from err
            return {"oil": rows}

        return _service

    for name, schema, handler in _SERVICES:
        if hass.services.has_service(DOMAIN, name):
            continue
        hass.services.async_register(
            DOMAIN,
            name,
            _make(handler),
            schema=schema,
            supports_response=SupportsResponse.ONLY,
        )

    # ⑨ 반경 내 주유소: 위경도→KATEC 변환이 필요해 전용 핸들러로 등록.
    async def _around(call: ServiceCall) -> ServiceResponse:
        api = _get_api(hass)
        lat, lon = _resolve_location(hass, dict(call.data))
        x, y = await hass.async_add_executor_job(wgs84_to_katec, lat, lon)
        try:
            rows = await api.async_get_around_all(
                x, y, call.data["radius"], call.data["prodcd"], call.data["sort"]
            )
        except OpinetError as err:
            raise HomeAssistantError(f"Opinet 요청 실패: {err}") from err
        return {
            "oil": rows,
            "latitude": lat,
            "longitude": lon,
            "katec_x": round(x, 1),
            "katec_y": round(y, 1),
        }

    if not hass.services.has_service(DOMAIN, SERVICE_GET_AROUND):
        hass.services.async_register(
            DOMAIN,
            SERVICE_GET_AROUND,
            _around,
            schema=_GET_AROUND_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )

    # ⑩ 주유소 상세정보: 등록된 주유소(기기)를 선택하거나 ID 직접 입력.
    async def _station_detail(call: ServiceCall) -> ServiceResponse:
        api = _get_api(hass)
        station_id = call.data.get("station_id")
        device_id = call.data.get("device_id")
        if not station_id and device_id:
            station_id = _station_id_from_device(hass, device_id)
        if not station_id:
            raise HomeAssistantError("주유소를 선택하거나 주유소 ID를 입력하세요.")
        try:
            detail = await api.async_detail_by_id(station_id)
        except OpinetError as err:
            raise HomeAssistantError(f"Opinet 요청 실패: {err}") from err
        return {"oil": [detail]}

    if not hass.services.has_service(DOMAIN, SERVICE_GET_STATION_DETAIL):
        hass.services.async_register(
            DOMAIN,
            SERVICE_GET_STATION_DETAIL,
            _station_detail,
            schema=_GET_STATION_DETAIL_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )

    _invalidate_service_descriptions(hass)


@callback
def async_unload_services(hass: HomeAssistant) -> None:
    """등록한 서비스를 제거한다."""
    names = [name for name, _s, _h in _SERVICES] + [
        SERVICE_GET_AROUND,
        SERVICE_GET_STATION_DETAIL,
    ]
    for name in names:
        if hass.services.has_service(DOMAIN, name):
            hass.services.async_remove(DOMAIN, name)
    _invalidate_service_descriptions(hass)
