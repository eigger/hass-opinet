"""Registered Opinet actions use the active API and actual coordinate conversion."""

import pytest
from homeassistant.exceptions import HomeAssistantError

from custom_components.opinet.api import OpinetConnectionError
from custom_components.opinet.geo import wgs84_to_katec


async def test_get_around(hass, mock_config_entry, mock_client):
    """Entity coordinates take priority over explicit coordinates and home."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    hass.states.async_set(
        "device_tracker.test_location",
        "home",
        {"latitude": 37.5665, "longitude": 126.978},
    )
    mock_client.async_get_around_all.return_value = [{"UNI_ID": "A0000001"}]
    data = {
        "entity_id": "device_tracker.test_location",
        "latitude": 35,
        "longitude": 128,
        "radius": 1000,
        "prodcd": "B027",
    }
    response = await hass.services.async_call(
        "opinet", "get_around", data, blocking=True, return_response=True
    )
    x, y = wgs84_to_katec(37.5665, 126.978)
    mock_client.async_get_around_all.assert_awaited_once_with(x, y, 1000, "B027", 1)
    assert response["latitude"] == 37.5665
    assert response["oil"] == [{"UNI_ID": "A0000001"}]
    mock_client.async_get_around_all.side_effect = OpinetConnectionError("offline")
    with pytest.raises(HomeAssistantError, match="offline"):
        await hass.services.async_call(
            "opinet", "get_around", data, blocking=True, return_response=True
        )
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
