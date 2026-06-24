"""Device tracker platform for Opinet — shows each station on the map."""

from __future__ import annotations

from typing import Any

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.core import HomeAssistant, callback
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
    _attr_source_type = SourceType.GPS

    def __init__(self, coordinator: OpinetStationCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.station_id}_location"
        self._attr_device_info = coordinator.device_info
        self._sync_tracker_attrs()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Sync tracker attrs when station data is refreshed."""
        self._sync_tracker_attrs()
        super()._handle_coordinator_update()

    def _sync_tracker_attrs(self) -> None:
        """Update location attrs from coordinator data."""
        data = self.coordinator.data or {}
        self._attr_location_name = data.get("address") or data.get("name")
        self._attr_latitude = data.get("latitude")
        self._attr_longitude = data.get("longitude")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return {
            "station_id": self.coordinator.station_id,
            "station_name": data.get("name"),
            "brand": self.coordinator.brand_name,
            "address": data.get("address"),
            "katec_x": data.get("gis_x"),
            "katec_y": data.get("gis_y"),
        }
