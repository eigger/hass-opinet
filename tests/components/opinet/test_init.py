"""Exercise entry setup, sensor loading and cleanup through Home Assistant."""

from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers import device_registry as dr, entity_registry as er

from custom_components.opinet.api import OpinetAuthError, OpinetConnectionError


async def test_setup_and_unload(hass, mock_config_entry, mock_client):
    """Real platforms expose state, station parentage, actions and unload."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.LOADED
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(
        "sensor", "opinet", f"{mock_config_entry.entry_id}_avg_B027"
    )
    assert hass.states.get(entity_id).state == "1700.5"
    station_entity = registry.async_get_entity_id("sensor", "opinet", "A0000001_B027")
    assert hass.states.get(station_entity).state == "1720.0"
    devices = dr.async_get(hass)
    hub = devices.async_get(registry.async_get(entity_id).device_id)
    station = devices.async_get(registry.async_get(station_entity).device_id)
    assert station.via_device_id == hub.id
    response = await hass.services.async_call(
        "opinet",
        "get_station_detail",
        {"device_id": station.id},
        blocking=True,
        return_response=True,
    )
    assert response["oil"][0]["UNI_ID"] == "A0000001"
    assert (
        mock_config_entry.runtime_data.station_coordinators[
            "station-subentry"
        ].hub_device_id
        == hub.id
    )
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED
    assert hass.states.get(entity_id).state == "unavailable"
    assert hass.states.get(station_entity).state == "unavailable"
    assert not hass.services.has_service("opinet", "get_station_detail")

    from datetime import timedelta
    from homeassistant.util import dt as dt_util
    from pytest_homeassistant_custom_component.common import async_fire_time_changed

    mock_client.reset_mock()
    scheduled = dt_util.now().replace(hour=9, minute=10, second=0, microsecond=0)
    async_fire_time_changed(hass, scheduled + timedelta(days=1))
    await hass.async_block_till_done()
    assert mock_client.mock_calls == []


async def test_setup_retry(hass, mock_config_entry, mock_client):
    """Temporary API failures retain the entry and recover on retry."""
    mock_config_entry.add_to_hass(hass)
    mock_client.async_get_avg_all_price.side_effect = OpinetConnectionError("offline")
    assert not await hass.config_entries.async_setup(mock_config_entry.entry_id)
    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY
    mock_client.async_get_avg_all_price.side_effect = None
    assert await hass.config_entries.async_reload(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)


async def test_setup_invalid_auth(hass, mock_config_entry, mock_client):
    """Invalid credentials trigger HA reauthentication."""
    mock_config_entry.add_to_hass(hass)
    mock_client.async_get_avg_all_price.side_effect = OpinetAuthError("invalid key")
    assert not await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.SETUP_ERROR
    assert any(
        flow["context"]["source"] == "reauth"
        for flow in hass.config_entries.flow.async_progress()
    )


async def test_partial_setup_failure(hass, mock_config_entry, mock_client):
    """A later initial refresh failure leaves no schedules or services."""
    from datetime import timedelta

    from homeassistant.util import dt as dt_util
    from pytest_homeassistant_custom_component.common import async_fire_time_changed

    mock_config_entry.add_to_hass(hass)
    mock_client.async_get_avg_recent_price.side_effect = OpinetConnectionError(
        "offline"
    )
    assert not await hass.config_entries.async_setup(mock_config_entry.entry_id)
    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY
    assert not hass.services.has_service("opinet", "get_station_detail")
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    mock_client.reset_mock()
    now = dt_util.now().replace(hour=9, minute=10, second=0, microsecond=0)
    async_fire_time_changed(hass, now + timedelta(days=1))
    await hass.async_block_till_done()
    assert mock_client.mock_calls == []


async def test_last_loaded_entry_removes_services(hass, mock_config_entry, mock_client):
    """Shared actions survive the first unload and disappear after the last."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    second_entry = MockConfigEntry(
        domain="opinet",
        title="Second",
        data={"api_key": "another-key"},
        unique_id="another-key",
    )
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    second_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(second_entry.entry_id)
    await hass.async_block_till_done()
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    assert hass.services.has_service("opinet", "get_avg_all_price")
    result = await hass.services.async_call(
        "opinet", "get_avg_all_price", blocking=True, return_response=True
    )
    assert result["oil"][0]["PRICE"] == "1700.5"
    assert await hass.config_entries.async_unload(second_entry.entry_id)
    assert not hass.services.has_service("opinet", "get_avg_all_price")
