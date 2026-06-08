"""Device tracker platform for Opinet — shows each station on the map."""

from __future__ import annotations

from typing import Any

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import OpinetConfigEntry
from .coordinator import OpinetStationCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: OpinetConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up a tracker per registered station."""
    data = entry.runtime_data
    for subentry_id, coordinator in data.station_coordinators.items():
        async_add_entities(
            [OpinetStationTracker(coordinator)],
            config_subentry_id=subentry_id,
        )


class OpinetStationTracker(
    CoordinatorEntity[OpinetStationCoordinator], TrackerEntity
):
    """주유소 위치(GPS) — 지도에 표시된다."""

    _attr_has_entity_name = True
    _attr_translation_key = "station_location"
    _attr_icon = "mdi:gas-station"

    def __init__(self, coordinator: OpinetStationCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.station_id}_location"
        self._attr_device_info = coordinator.device_info

    @property
    def source_type(self) -> SourceType:
        return SourceType.GPS

    @property
    def latitude(self) -> float | None:
        return (self.coordinator.data or {}).get("latitude")

    @property
    def longitude(self) -> float | None:
        return (self.coordinator.data or {}).get("longitude")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return {
            "station_id": self.coordinator.station_id,
            "station_name": data.get("name"),
            "address": data.get("address"),
            "katec_x": data.get("gis_x"),
            "katec_y": data.get("gis_y"),
        }
