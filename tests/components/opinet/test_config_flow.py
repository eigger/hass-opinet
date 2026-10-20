"""Configuration flows run through Home Assistant's flow manager."""

from unittest.mock import patch

import pytest
from homeassistant.data_entry_flow import FlowResultType

from custom_components.opinet.api import OpinetAuthError, OpinetConnectionError


async def test_user_flow(hass, mock_client):
    """Valid API credentials create and load the integration."""
    with patch(
        "custom_components.opinet.config_flow.OpinetApi", return_value=mock_client
    ):
        result = await hass.config_entries.flow.async_init(
            "opinet", context={"source": "user"}
        )
        assert result["type"] is FlowResultType.FORM
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"api_key": "test-api-key"}
        )
        assert result["type"] is FlowResultType.CREATE_ENTRY
        assert result["data"] == {"api_key": "test-api-key"}
        await hass.async_block_till_done()
        assert await hass.config_entries.async_unload(result["result"].entry_id)


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (OpinetAuthError("invalid"), "invalid_auth"),
        (OpinetConnectionError("offline"), "cannot_connect"),
    ],
)
async def test_user_flow_errors(hass, mock_client, error, expected):
    """Authentication and communication failures keep the form open."""
    mock_client.async_get_avg_all_price.side_effect = error
    with patch(
        "custom_components.opinet.config_flow.OpinetApi", return_value=mock_client
    ):
        result = await hass.config_entries.flow.async_init(
            "opinet", context={"source": "user"}, data={"api_key": "test-api-key"}
        )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": expected}


async def test_duplicate_entry(hass, mock_config_entry):
    """The same API key cannot create a second entry."""
    mock_config_entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        "opinet", context={"source": "user"}, data={"api_key": "test-api-key"}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_reauthentication(hass, mock_config_entry, mock_client):
    """Reauthentication validates and replaces the API key then reloads."""
    mock_config_entry.add_to_hass(hass)
    with patch(
        "custom_components.opinet.config_flow.OpinetApi", return_value=mock_client
    ):
        result = await hass.config_entries.flow.async_init(
            "opinet",
            context={"source": "reauth", "entry_id": mock_config_entry.entry_id},
            data=mock_config_entry.data,
        )
        assert result["step_id"] == "reauth_confirm"
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"api_key": "replacement-key"}
        )
        assert result["reason"] == "reauth_successful"
        await hass.async_block_till_done()
    assert mock_config_entry.data["api_key"] == "replacement-key"
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)


async def test_station_add_and_duplicate(hass, mock_config_entry, mock_client):
    """Station subentry flows validate IDs and reject an existing station."""
    mock_config_entry.add_to_hass(hass)
    with patch(
        "custom_components.opinet.config_flow.OpinetApi", return_value=mock_client
    ):
        result = await hass.config_entries.subentries.async_init(
            (mock_config_entry.entry_id, "station"), context={"source": "user"}
        )
        assert result["type"] is FlowResultType.MENU
        result = await hass.config_entries.subentries.async_configure(
            result["flow_id"], {"next_step_id": "by_id"}
        )
        assert result["step_id"] == "by_id"
        result = await hass.config_entries.subentries.async_configure(
            result["flow_id"], {"station_id": "A0000001"}
        )
        assert result["reason"] == "already_configured"
        result = await hass.config_entries.subentries.async_init(
            (mock_config_entry.entry_id, "station"),
            context={"source": "user"},
        )
        result = await hass.config_entries.subentries.async_configure(
            result["flow_id"], {"next_step_id": "by_id"}
        )
        result = await hass.config_entries.subentries.async_configure(
            result["flow_id"], {"station_id": "A0000002"}
        )
        assert result["type"] is FlowResultType.CREATE_ENTRY
        assert result["data"] == {"station_id": "A0000002"}


async def test_options(hass, mock_config_entry, mock_client):
    """Options updates save the refresh offset and reload real platforms."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"refresh_offset": 15}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert mock_config_entry.options["refresh_offset"] == 15
    assert mock_config_entry.runtime_data.avg_coordinator._offset_minutes == 15
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)


async def test_station_search(hass, mock_config_entry, mock_client):
    """Name search offers actual results before registering a chosen station."""
    mock_config_entry.add_to_hass(hass)
    mock_client.async_search_by_name.return_value = [
        {"UNI_ID": "A0000002", "OS_NM": "Test station"}
    ]
    with patch(
        "custom_components.opinet.config_flow.OpinetApi", return_value=mock_client
    ):
        result = await hass.config_entries.subentries.async_init(
            (mock_config_entry.entry_id, "station"), context={"source": "user"}
        )
        result = await hass.config_entries.subentries.async_configure(
            result["flow_id"], {"next_step_id": "search"}
        )
        result = await hass.config_entries.subentries.async_configure(
            result["flow_id"], {"osnm": "Test", "area": "01"}
        )
        assert result["step_id"] == "select"
        mock_client.async_search_by_name.assert_awaited_once_with("Test", "01")
        result = await hass.config_entries.subentries.async_configure(
            result["flow_id"], {"station_id": "A0000002"}
        )
        assert result["type"] is FlowResultType.CREATE_ENTRY
