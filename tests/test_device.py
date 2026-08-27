"""Opinet 디바이스 및 via_device_id 테스트."""
import asyncio
from unittest.mock import AsyncMock, MagicMock

from custom_components.opinet import _async_setup_devices, async_setup_entry
from custom_components.opinet.coordinator import OpinetStationCoordinator


def test_station_coordinator_device_info_via_device_id():
    """주유소 코디네이터의 DeviceInfo는 via_device 대신 via_device_id를 가져야 한다."""
    coordinator = OpinetStationCoordinator(
        hass=MagicMock(),
        entry=MagicMock(entry_id="test_entry_id"),
        api=MagicMock(),
        station_id="A0000001",
        hub_device_id="hub_device_123",
    )
    coordinator.data = {
        "name": "테스트 주유소",
        "brand": "SKE",
        "lpg_yn": "N",
    }

    dev_info = coordinator.device_info
    assert dev_info["identifiers"] == {("opinet", "A0000001")}
    assert dev_info["name"] == "테스트 주유소"
    assert dev_info["manufacturer"] == "SK에너지"
    assert dev_info.get("via_device_id") == "hub_device_123"
    assert "via_device" not in dev_info


def test_async_setup_devices_creates_hub_device():
    """_async_setup_devices가 허브 디바이스를 생성하고 DeviceEntry를 반환하는지 검증."""
    hass = MagicMock()
    entry = MagicMock(entry_id="entry_123")
    mock_dr = MagicMock()
    mock_device = MagicMock(id="hub_dev_456")
    mock_dr.async_get_or_create.return_value = mock_device

    from homeassistant.helpers import device_registry as dr
    dr.async_get.return_value = mock_dr

    result = _async_setup_devices(hass, entry)
    assert result == mock_device
    mock_dr.async_get_or_create.assert_called_once_with(
        config_entry_id="entry_123",
        identifiers={("opinet", "entry_123")},
        translation_key="nationwide_average",
        manufacturer="Korea National Oil Corporation (Opinet)",
        model="Nationwide average price",
    )


def test_async_setup_entry_passes_hub_device_id():
    """async_setup_entry에서 생성된 hub_device.id가 주유소 코디네이터 및 runtime_data에 전달되는지 검증."""
    async def _run():
        hass = MagicMock()
        hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)

        entry = MagicMock(
            entry_id="entry_abc",
            data={"api_key": "test_key"},
            options={},
            subentries={
                "sub1": MagicMock(data={"station_id": "A1234567"}),
            },
        )

        mock_dr = MagicMock()
        mock_hub_device = MagicMock(id="hub_dev_abc")
        mock_dr.async_get_or_create.return_value = mock_hub_device

        from homeassistant.helpers import device_registry as dr
        dr.async_get.return_value = mock_dr

        result = await async_setup_entry(hass, entry)

        assert result is True
        assert entry.runtime_data.hub_device_id == "hub_dev_abc"
        assert "sub1" in entry.runtime_data.station_coordinators
        station_coord = entry.runtime_data.station_coordinators["sub1"]
        assert station_coord.hub_device_id == "hub_dev_abc"

    asyncio.run(_run())
