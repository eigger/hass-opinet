"""Sensor platform for Opinet."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import OpinetConfigEntry
from .const import BRANDS, DOMAIN, PRICE_UNIT, PRODUCTS
from .coordinator import (
    OpinetAvgCoordinator,
    OpinetRecentAvgCoordinator,
    OpinetStationCoordinator,
    OpinetWeeklyAvgCoordinator,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: OpinetConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Opinet sensors for the entry and each station subentry."""
    data = entry.runtime_data
    entry_id = entry.entry_id

    # 전국 평균 — 현재/일일/주간 (하나의 공통 기기에 묶음).
    async_add_entities(
        OpinetAvgSensor(data.avg_coordinator, entry_id, prodcd)
        for prodcd in PRODUCTS
    )
    async_add_entities(
        OpinetRecentAvgSensor(data.recent_coordinator, entry_id, prodcd)
        for prodcd in (data.recent_coordinator.data or {})
        if prodcd in PRODUCTS
    )
    async_add_entities(
        OpinetWeeklyAvgSensor(data.weekly_coordinator, entry_id, prodcd)
        for prodcd in (data.weekly_coordinator.data or {})
        if prodcd in PRODUCTS
    )

    # Per-station sensors, attached to their subentry/device.
    for subentry_id, coordinator in data.station_coordinators.items():
        prices: dict[str, Any] = (coordinator.data or {}).get("prices", {})
        async_add_entities(
            (
                OpinetStationSensor(coordinator, prodcd)
                for prodcd in prices
                if prodcd in PRODUCTS
            ),
            config_subentry_id=subentry_id,
        )


def _avg_device_info(entry_id: str) -> DeviceInfo:
    """현재/일일/주간 전국 평균 센서가 공유하는 기기 (이름은 번역됨)."""
    return DeviceInfo(
        identifiers={(DOMAIN, f"{entry_id}_avg")},
        translation_key="nationwide_average",
        manufacturer="Korea National Oil Corporation (Opinet)",
    )


class OpinetAvgSensor(CoordinatorEntity[OpinetAvgCoordinator], SensorEntity):
    """전국 평균가격(현재) — 제품별."""

    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = PRICE_UNIT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:gas-station"

    def __init__(
        self,
        coordinator: OpinetAvgCoordinator,
        entry_id: str,
        prodcd: str,
    ) -> None:
        super().__init__(coordinator)
        self._prodcd = prodcd
        self._attr_unique_id = f"{entry_id}_avg_{prodcd}"
        self._attr_translation_key = f"avg_current_{prodcd.lower()}"
        self._attr_device_info = _avg_device_info(entry_id)

    @property
    def _row(self) -> dict[str, Any]:
        return (self.coordinator.data or {}).get(self._prodcd, {})

    @property
    def native_value(self) -> float | None:
        return self._row.get("price")

    @property
    def available(self) -> bool:
        return super().available and bool(self._row)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        row = self._row
        return {
            "product_code": self._prodcd,
            "diff": row.get("diff"),
            "trade_date": row.get("trade_dt"),
        }


class OpinetRecentAvgSensor(
    CoordinatorEntity[OpinetRecentAvgCoordinator], SensorEntity
):
    """전국 일일 평균가격(최근 확정 일자) — 제품별."""

    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = PRICE_UNIT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:gas-station-outline"

    def __init__(
        self,
        coordinator: OpinetRecentAvgCoordinator,
        entry_id: str,
        prodcd: str,
    ) -> None:
        super().__init__(coordinator)
        self._prodcd = prodcd
        self._attr_unique_id = f"{entry_id}_recent_{prodcd}"
        self._attr_translation_key = f"avg_daily_{prodcd.lower()}"
        self._attr_device_info = _avg_device_info(entry_id)

    @property
    def _row(self) -> dict[str, Any]:
        return (self.coordinator.data or {}).get(self._prodcd, {})

    @property
    def native_value(self) -> float | None:
        return self._row.get("price")

    @property
    def available(self) -> bool:
        return super().available and bool(self._row)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "product_code": self._prodcd,
            "date": self._row.get("date"),
        }


class OpinetWeeklyAvgSensor(
    CoordinatorEntity[OpinetWeeklyAvgCoordinator], SensorEntity
):
    """전국 주간 평균가격 — 제품별."""

    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = PRICE_UNIT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:calendar-week"

    def __init__(
        self,
        coordinator: OpinetWeeklyAvgCoordinator,
        entry_id: str,
        prodcd: str,
    ) -> None:
        super().__init__(coordinator)
        self._prodcd = prodcd
        self._attr_unique_id = f"{entry_id}_weekly_{prodcd}"
        self._attr_translation_key = f"avg_weekly_{prodcd.lower()}"
        self._attr_device_info = _avg_device_info(entry_id)

    @property
    def _row(self) -> dict[str, Any]:
        return (self.coordinator.data or {}).get(self._prodcd, {})

    @property
    def native_value(self) -> float | None:
        return self._row.get("price")

    @property
    def available(self) -> bool:
        return super().available and bool(self._row)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        row = self._row
        return {
            "product_code": self._prodcd,
            "week": row.get("week"),
            "start_date": row.get("sta_dt"),
            "end_date": row.get("end_dt"),
        }


class OpinetStationSensor(
    CoordinatorEntity[OpinetStationCoordinator], SensorEntity
):
    """Selling price of a single product at a specific gas station."""

    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = PRICE_UNIT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:gas-station"

    def __init__(
        self, coordinator: OpinetStationCoordinator, prodcd: str
    ) -> None:
        super().__init__(coordinator)
        self._prodcd = prodcd
        station_id = coordinator.station_id
        self._attr_unique_id = f"{station_id}_{prodcd}"
        self._attr_translation_key = f"station_{prodcd.lower()}"

        data = coordinator.data or {}
        brand = BRANDS.get(data.get("brand", ""), data.get("brand"))
        # 기기 이름은 실제 주유소 상호(데이터) — 라벨이 아니므로 그대로 사용.
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, station_id)},
            name=data.get("name") or station_id,
            manufacturer=brand or None,
            model="Gas station",
        )

    @property
    def _price(self) -> dict[str, Any]:
        return (self.coordinator.data or {}).get("prices", {}).get(
            self._prodcd, {}
        )

    @property
    def native_value(self) -> float | None:
        return self._price.get("price")

    @property
    def available(self) -> bool:
        return super().available and bool(self._price)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        price = self._price
        return {
            "product_code": self._prodcd,
            "station_id": self.coordinator.station_id,
            "station_name": data.get("name"),
            "brand": BRANDS.get(data.get("brand", ""), data.get("brand")),
            "address": data.get("address"),
            "tel": data.get("tel"),
            "trade_date": price.get("trade_dt"),
            "trade_time": price.get("trade_tm"),
        }
