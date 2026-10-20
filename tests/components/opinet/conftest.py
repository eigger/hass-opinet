"""Fixtures for the Opinet integration."""

# <!-- hass-standards:domain-fixtures:start -->
# Use pytest_homeassistant_custom_component.common.MockConfigEntry for
# mock_config_entry when the integration uses config entries.
# Define mock_client only when an external communication client is present.
# Mock external communication boundaries, never Home Assistant core modules.
# Keep integration-specific fixtures below this managed block.
# <!-- hass-standards:domain-fixtures:end -->

from unittest.mock import AsyncMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry


@pytest.fixture
def mock_config_entry():
    """Provide an entry with a registered station subentry."""
    return MockConfigEntry(
        domain="opinet",
        title="Opinet",
        data={"api_key": "test-api-key"},
        unique_id="test-api-key",
        subentries_data=[
            {
                "data": {"station_id": "A0000001"},
                "subentry_id": "station-subentry",
                "subentry_type": "station",
                "title": "Test station",
                "unique_id": "A0000001",
            }
        ],
    )


@pytest.fixture
def mock_client():
    """Replace only the external Opinet API client."""
    with patch("custom_components.opinet.OpinetApi", autospec=True) as factory:
        client = factory.return_value
        client.async_get_avg_all_price = AsyncMock(
            return_value=[{"PRODCD": "B027", "PRICE": "1700.5", "DIFF": "1.2"}]
        )
        client.async_get_avg_recent_price = AsyncMock(
            return_value=[{"PRODCD": "B027", "PRICE": "1699", "DATE": "20261019"}]
        )
        client.async_get_avg_last_week = AsyncMock(
            return_value=[{"PRODCD": "B027", "PRICE": "1690", "AREA_CD": "00"}]
        )
        client.async_detail_by_id = AsyncMock(
            return_value={
                "UNI_ID": "A0000001",
                "OS_NM": "Test station",
                "POLL_DIV_CO": "SKE",
                "LPG_YN": "N",
                "SIGUNCD": "0101",
                "NEW_ADR": "Test address",
                "CAR_WASH_YN": "Y",
                "OIL_PRICE": [{"PRODCD": "B027", "PRICE": "1720"}],
            }
        )
        client.async_get_urea_price = AsyncMock(
            return_value=[
                {
                    "UNI_ID": "A0000001",
                    "PRICE": "1000",
                    "STOCK_YN": "Y",
                }
            ]
        )
        yield client
