"""The Opinet (오피넷 유가정보) integration."""

from __future__ import annotations

from dataclasses import dataclass, field
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OpinetApi
from .const import (
    CONF_API_KEY,
    CONF_REFRESH_OFFSET,
    CONF_STATION_ID,
    DEFAULT_REFRESH_OFFSET_MINUTES,
    DOMAIN,
)
from .coordinator import (
    OpinetAvgCoordinator,
    OpinetRecentAvgCoordinator,
    OpinetStationCoordinator,
    OpinetWeeklyAvgCoordinator,
)
from .services import async_setup_services, async_unload_services

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.DEVICE_TRACKER,
    Platform.SENSOR,
]


@dataclass
class OpinetRuntimeData:
    """Objects shared across the entry's platforms."""

    api: OpinetApi
    avg_coordinator: OpinetAvgCoordinator
    recent_coordinator: OpinetRecentAvgCoordinator
    weekly_coordinator: OpinetWeeklyAvgCoordinator
    station_coordinators: dict[str, OpinetStationCoordinator] = field(
        default_factory=dict
    )


type OpinetConfigEntry = ConfigEntry[OpinetRuntimeData]


async def async_setup_entry(hass: HomeAssistant, entry: OpinetConfigEntry) -> bool:
    """Set up Opinet from a config entry."""
    session = async_get_clientsession(hass)
    api = OpinetApi(session, entry.data[CONF_API_KEY])

    offset = entry.options.get(
        CONF_REFRESH_OFFSET, DEFAULT_REFRESH_OFFSET_MINUTES
    )

    avg_coordinator = OpinetAvgCoordinator(hass, entry, api, offset)
    await avg_coordinator.async_config_entry_first_refresh()
    avg_coordinator.async_setup_schedule()

    recent_coordinator = OpinetRecentAvgCoordinator(hass, entry, api, offset)
    await recent_coordinator.async_config_entry_first_refresh()
    recent_coordinator.async_setup_schedule()

    weekly_coordinator = OpinetWeeklyAvgCoordinator(hass, entry, api, offset)
    await weekly_coordinator.async_config_entry_first_refresh()
    weekly_coordinator.async_setup_schedule()

    station_coordinators: dict[str, OpinetStationCoordinator] = {}
    for subentry_id, subentry in entry.subentries.items():
        station_id = subentry.data[CONF_STATION_ID]
        coordinator = OpinetStationCoordinator(
            hass, entry, api, station_id, offset
        )
        await coordinator.async_config_entry_first_refresh()
        coordinator.async_setup_schedule()
        station_coordinators[subentry_id] = coordinator

    entry.runtime_data = OpinetRuntimeData(
        api=api,
        avg_coordinator=avg_coordinator,
        recent_coordinator=recent_coordinator,
        weekly_coordinator=weekly_coordinator,
        station_coordinators=station_coordinators,
    )

    _async_setup_devices(hass, entry, bool(station_coordinators))

    # 데이터 조회용 서비스(전 API)를 1회만 등록한다.
    async_setup_services(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


def _async_setup_devices(
    hass: HomeAssistant, entry: OpinetConfigEntry, has_stations: bool
) -> None:
    """기기 계층을 만든다.

    오피넷 전국 평균 유가 정보(허브) ─ 주유소(서브 기기) ─ 각 주유소.
    via_device 가 참조하는 부모가 먼저 존재해야 하므로 여기서 미리 생성한다.
    """
    device_reg = dr.async_get(hass)
    # 허브: 전국 평균 센서가 올라가는 기기이자 주유소들의 부모.
    device_reg.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        translation_key="nationwide_average",
        manufacturer="Korea National Oil Corporation (Opinet)",
        model="Nationwide average price",
    )
    # 주유소 그룹(서브 기기): 추가된 주유소 기기들이 이 밑으로 묶인다.
    if has_stations:
        device_reg.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, f"{entry.entry_id}_stations")},
            translation_key="stations",
            via_device=(DOMAIN, entry.entry_id),
        )


async def _async_update_listener(
    hass: HomeAssistant, entry: OpinetConfigEntry
) -> None:
    """Reload the entry when subentries (stations) are added/removed."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: OpinetConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    # 마지막 엔트리가 내려가면 서비스도 제거한다.
    if unloaded and len(hass.config_entries.async_entries(DOMAIN)) <= 1:
        async_unload_services(hass)
    return unloaded
