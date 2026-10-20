"""Real sensor availability regressions."""

from homeassistant.helpers import entity_registry as er

from custom_components.opinet.api import OpinetConnectionError


async def test_sensor_failure_and_recovery(hass, mock_config_entry, mock_client):
    """A failed refresh makes real sensors unavailable and later recovers."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    entity_id = er.async_get(hass).async_get_entity_id(
        "sensor", "opinet", f"{mock_config_entry.entry_id}_avg_B027"
    )
    coordinator = mock_config_entry.runtime_data.avg_coordinator
    mock_client.async_get_avg_all_price.side_effect = OpinetConnectionError("offline")
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == "unavailable"
    mock_client.async_get_avg_all_price.side_effect = None
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == "1700.5"
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
