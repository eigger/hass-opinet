"""Scheduled refresh behavior with real HA coordinators."""

from datetime import datetime

from custom_components.opinet.coordinator import OpinetWeeklyAvgCoordinator


async def test_weekly_update_day(hass, mock_config_entry, mock_client):
    """Weekly data refreshes on Friday and ignores other weekdays."""
    mock_config_entry.add_to_hass(hass)
    coordinator = OpinetWeeklyAvgCoordinator(hass, mock_config_entry, mock_client)
    await coordinator._handle_scheduled_refresh(datetime(2026, 10, 22, 10, 10))
    mock_client.async_get_avg_last_week.assert_not_called()
    await coordinator._handle_scheduled_refresh(datetime(2026, 10, 23, 10, 10))
    mock_client.async_get_avg_last_week.assert_awaited_once()
    assert coordinator.data["B027"]["price"] == 1690.0
