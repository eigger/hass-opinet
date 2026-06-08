"""Binary sensors for gas-station amenities (from detailById)."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import OpinetConfigEntry
from .coordinator import OpinetStationCoordinator


@dataclass(frozen=True, kw_only=True)
class OpinetBinaryDescription(BinarySensorEntityDescription):
    """Binary sensor description tied to a coordinator data key (Y/N)."""

    data_key: str


DESCRIPTIONS: tuple[OpinetBinaryDescription, ...] = (
    OpinetBinaryDescription(
        key="car_wash",
        translation_key="car_wash",
        data_key="car_wash_yn",
        icon="mdi:car-wash",
    ),
    OpinetBinaryDescription(
        key="maintenance",
        translation_key="maintenance",
        data_key="maint_yn",
        icon="mdi:car-wrench",
    ),
    OpinetBinaryDescription(
        key="convenience_store",
        translation_key="convenience_store",
        data_key="cvs_yn",
        icon="mdi:store",
    ),
    OpinetBinaryDescription(
        key="quality_certified",
        translation_key="quality_certified",
        data_key="kpetro_yn",
        icon="mdi:certificate",
    ),
    OpinetBinaryDescription(
        key="good_station",
        translation_key="good_station",
        data_key="good_yn",
        icon="mdi:thumb-up",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: OpinetConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up amenity binary sensors per registered station."""
    data = entry.runtime_data
    for subentry_id, coordinator in data.station_coordinators.items():
        async_add_entities(
            (
                OpinetStationBinarySensor(coordinator, description)
                for description in DESCRIPTIONS
            ),
            config_subentry_id=subentry_id,
        )


class OpinetStationBinarySensor(
    CoordinatorEntity[OpinetStationCoordinator], BinarySensorEntity
):
    """Amenity flag (Y/N) of a gas station."""

    _attr_has_entity_name = True
    entity_description: OpinetBinaryDescription

    def __init__(
        self,
        coordinator: OpinetStationCoordinator,
        description: OpinetBinaryDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.station_id}_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool | None:
        value = (self.coordinator.data or {}).get(self.entity_description.data_key)
        if value is None:
            return None
        return str(value).upper() == "Y"
