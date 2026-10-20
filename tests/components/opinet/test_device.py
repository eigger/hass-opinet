"""Device metadata regressions using Home Assistant fixtures."""

from homeassistant.helpers.device_registry import DeviceInfo

from custom_components.opinet import _async_setup_devices
from custom_components.opinet.coordinator import OpinetStationCoordinator


def test_device_info_supports_via_device_id():
    """The supported HA runtime exposes the station parent device API."""
    assert "via_device_id" in DeviceInfo.__annotations__


async def test_station_coordinator_device_info_via_device_id(
    hass, mock_config_entry, mock_client
):
    """Keep station branding and parent IDs stable."""
    mock_config_entry.add_to_hass(hass)
    coordinator = OpinetStationCoordinator(
        hass, mock_config_entry, mock_client, "A0000001", "hub_device_123"
    )
    coordinator.data = {"name": "테스트 주유소", "brand": "SKE", "lpg_yn": "N"}
    info = coordinator.device_info
    assert info["identifiers"] == {("opinet", "A0000001")}
    assert info["name"] == "테스트 주유소"
    assert info["manufacturer"] == "SK에너지"
    assert info["via_device_id"] == "hub_device_123"
    assert "via_device" not in info


async def test_async_setup_devices_creates_hub_device(hass, mock_config_entry):
    """Hub registration uses the real device registry and remains idempotent."""
    mock_config_entry.add_to_hass(hass)
    device = _async_setup_devices(hass, mock_config_entry)
    assert device.identifiers == {("opinet", mock_config_entry.entry_id)}
    assert device.manufacturer == "Korea National Oil Corporation (Opinet)"
    assert device.model == "Nationwide average price"
    assert _async_setup_devices(hass, mock_config_entry).id == device.id
