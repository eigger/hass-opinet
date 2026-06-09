"""Sensor platform for Opinet."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import OpinetConfigEntry
from .const import AMENITY_NO, AMENITY_OPTIONS, AMENITY_YES, DOMAIN, PRICE_UNIT, PRODUCTS
from .coordinator import (
    OpinetAvgCoordinator,
    OpinetRecentAvgCoordinator,
    OpinetStationCoordinator,
    OpinetUreaCoordinator,
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
    urea_coordinator = data.urea_coordinator
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
        async_add_entities(
            (
                OpinetStationAmenitySensor(coordinator, description)
                for description in AMENITY_DESCRIPTIONS
            ),
            config_subentry_id=subentry_id,
        )

        # 요소수 가격/재고 — 해당 주유소가 요소수 판매 목록에 있을 때만 생성.
        uni_id = (coordinator.data or {}).get("uni_id")
        if (
            urea_coordinator is not None
            and uni_id
            and uni_id in (urea_coordinator.data or {})
        ):
            async_add_entities(
                (
                    OpinetStationUreaSensor(urea_coordinator, coordinator, uni_id),
                    OpinetStationUreaStockSensor(
                        urea_coordinator, coordinator, uni_id
                    ),
                ),
                config_subentry_id=subentry_id,
            )


def _avg_device_info(entry_id: str) -> DeviceInfo:
    """현재/일일/주간 전국 평균 센서가 공유하는 허브 기기 (이름은 번역됨)."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry_id)},
        translation_key="nationwide_average",
        manufacturer="Korea National Oil Corporation (Opinet)",
        model="Nationwide average price",
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
        self._attr_device_info = coordinator.device_info

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
            "brand": self.coordinator.brand_name,
            "address": data.get("address"),
            "tel": data.get("tel"),
            "trade_date": price.get("trade_dt"),
            "trade_time": price.get("trade_tm"),
        }


@dataclass(frozen=True, kw_only=True)
class OpinetAmenityDescription:
    """Amenity sensor tied to a coordinator data key (Y/N)."""

    key: str
    translation_key: str
    data_key: str
    icon: str


AMENITY_DESCRIPTIONS: tuple[OpinetAmenityDescription, ...] = (
    OpinetAmenityDescription(
        key="car_wash",
        translation_key="car_wash",
        data_key="car_wash_yn",
        icon="mdi:car-wash",
    ),
    OpinetAmenityDescription(
        key="maintenance",
        translation_key="maintenance",
        data_key="maint_yn",
        icon="mdi:car-wrench",
    ),
    OpinetAmenityDescription(
        key="convenience_store",
        translation_key="convenience_store",
        data_key="cvs_yn",
        icon="mdi:store",
    ),
    OpinetAmenityDescription(
        key="quality_certified",
        translation_key="quality_certified",
        data_key="kpetro_yn",
        icon="mdi:certificate",
    ),
    OpinetAmenityDescription(
        key="good_station",
        translation_key="good_station",
        data_key="good_yn",
        icon="mdi:thumb-up",
    ),
)


class OpinetStationAmenitySensor(
    CoordinatorEntity[OpinetStationCoordinator], SensorEntity
):
    """Amenity availability (있음/없음) of a gas station."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = list(AMENITY_OPTIONS)

    def __init__(
        self,
        coordinator: OpinetStationCoordinator,
        description: OpinetAmenityDescription,
    ) -> None:
        super().__init__(coordinator)
        self._description = description
        self._attr_unique_id = f"{coordinator.station_id}_{description.key}"
        self._attr_translation_key = description.translation_key
        self._attr_icon = description.icon
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> str | None:
        value = (self.coordinator.data or {}).get(self._description.data_key)
        if value is None:
            return None
        return AMENITY_YES if str(value).upper() == "Y" else AMENITY_NO


class OpinetStationUreaSensor(
    CoordinatorEntity[OpinetUreaCoordinator], SensorEntity
):
    """요소수(DEF) 판매가격 — 주유소별."""

    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = PRICE_UNIT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 0
    _attr_icon = "mdi:car-coolant-level"
    _attr_translation_key = "station_urea"

    def __init__(
        self,
        coordinator: OpinetUreaCoordinator,
        station: OpinetStationCoordinator,
        uni_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._uni_id = uni_id
        self._attr_unique_id = f"{station.station_id}_urea"
        self._attr_device_info = station.device_info

    @property
    def _row(self) -> dict[str, Any]:
        return (self.coordinator.data or {}).get(self._uni_id, {})

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
            "station_id": self._uni_id,
            "in_stock": str(row.get("stock", "")).upper() == "Y",
            "trade_date": row.get("trade_dt"),
            "trade_time": row.get("trade_tm"),
        }


class OpinetStationUreaStockSensor(
    CoordinatorEntity[OpinetUreaCoordinator], SensorEntity
):
    """요소수 재고 유/무 (있음/없음) — 주유소별."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = list(AMENITY_OPTIONS)
    _attr_icon = "mdi:storefront-outline"
    _attr_translation_key = "urea_stock"

    def __init__(
        self,
        coordinator: OpinetUreaCoordinator,
        station: OpinetStationCoordinator,
        uni_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._uni_id = uni_id
        self._attr_unique_id = f"{station.station_id}_urea_stock"
        self._attr_device_info = station.device_info

    @property
    def native_value(self) -> str | None:
        row = (self.coordinator.data or {}).get(self._uni_id)
        if not row:
            return None
        return AMENITY_YES if str(row.get("stock", "")).upper() == "Y" else AMENITY_NO
