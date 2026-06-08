"""Config flow for the Opinet integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryFlow,
    OptionsFlow,
    SubentryFlowResult,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .api import OpinetApi, OpinetAuthError, OpinetConnectionError, OpinetError
from .const import (
    AREAS,
    BRANDS,
    CONF_API_KEY,
    CONF_AREA,
    CONF_OSNM,
    CONF_REFRESH_OFFSET,
    CONF_STATION_ID,
    DEFAULT_REFRESH_OFFSET_MINUTES,
    DOMAIN,
    MAX_REFRESH_OFFSET_MINUTES,
    MIN_REFRESH_OFFSET_MINUTES,
    SUBENTRY_TYPE_STATION,
)

_LOGGER = logging.getLogger(__name__)

AREA_OPTIONS = [
    SelectOptionDict(value=code, label=f"{name} ({code})")
    for code, name in AREAS.items()
]


class OpinetConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the initial setup (API key) for Opinet."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for the API key and validate it."""
        errors: dict[str, str] = {}
        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()
            await self.async_set_unique_id(api_key)
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            api = OpinetApi(session, api_key)
            try:
                await api.async_get_avg_all_price()
            except OpinetAuthError:
                errors["base"] = "invalid_auth"
            except OpinetConnectionError:
                errors["base"] = "cannot_connect"
            except OpinetError:
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title="오피넷 유가정보",
                    data={CONF_API_KEY: api_key},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> ConfigFlowResult:
        """Handle re-authentication when the API key becomes invalid."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for a new API key and update the entry."""
        errors: dict[str, str] = {}
        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()
            session = async_get_clientsession(self.hass)
            api = OpinetApi(session, api_key)
            try:
                await api.async_get_avg_all_price()
            except OpinetAuthError:
                errors["base"] = "invalid_auth"
            except OpinetConnectionError:
                errors["base"] = "cannot_connect"
            except OpinetError:
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    self._get_reauth_entry(),
                    data_updates={CONF_API_KEY: api_key},
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        """Return the subentry types supported by this integration."""
        return {SUBENTRY_TYPE_STATION: StationSubentryFlowHandler}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow handler."""
        return OpinetOptionsFlow()


class OpinetOptionsFlow(OptionsFlow):
    """Handle Opinet options (refresh offset)."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the refresh offset option."""
        if user_input is not None:
            return self.async_create_entry(
                data={
                    CONF_REFRESH_OFFSET: int(user_input[CONF_REFRESH_OFFSET])
                }
            )

        current = self.config_entry.options.get(
            CONF_REFRESH_OFFSET, DEFAULT_REFRESH_OFFSET_MINUTES
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_REFRESH_OFFSET, default=current
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=MIN_REFRESH_OFFSET_MINUTES,
                            max=MAX_REFRESH_OFFSET_MINUTES,
                            step=1,
                            unit_of_measurement="분",
                            mode=NumberSelectorMode.BOX,
                        )
                    )
                }
            ),
        )


class StationSubentryFlowHandler(ConfigSubentryFlow):
    """Add a gas station as a subentry (by name search or by id)."""

    def __init__(self) -> None:
        self._results: dict[str, str] = {}

    @property
    def _api(self) -> OpinetApi:
        entry = self._get_entry()
        session = async_get_clientsession(self.hass)
        return OpinetApi(session, entry.data[CONF_API_KEY])

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Let the user choose how to add a station."""
        return self.async_show_menu(
            step_id="user",
            menu_options=["search", "by_id"],
        )

    async def async_step_search(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Search stations by name (상호)."""
        errors: dict[str, str] = {}
        if user_input is not None:
            osnm = user_input[CONF_OSNM].strip()
            area = user_input.get(CONF_AREA) or None
            try:
                stations = await self._api.async_search_by_name(osnm, area)
            except OpinetAuthError:
                errors["base"] = "invalid_auth"
            except OpinetError:
                errors["base"] = "cannot_connect"
            else:
                if not stations:
                    errors["base"] = "no_results"
                else:
                    self._results = {
                        s["UNI_ID"]: self._format_station(s) for s in stations
                    }
                    return await self.async_step_select()

        return self.async_show_form(
            step_id="search",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_OSNM): str,
                    vol.Optional(CONF_AREA): SelectSelector(
                        SelectSelectorConfig(
                            options=AREA_OPTIONS,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_select(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Pick a station from the search results."""
        if user_input is not None:
            return await self._async_create_station(user_input[CONF_STATION_ID])

        options = [
            SelectOptionDict(value=uni_id, label=label)
            for uni_id, label in self._results.items()
        ]
        return self.async_show_form(
            step_id="select",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_STATION_ID): SelectSelector(
                        SelectSelectorConfig(
                            options=options,
                            mode=SelectSelectorMode.LIST,
                        )
                    )
                }
            ),
        )

    async def async_step_by_id(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Add a station directly by its Opinet ID."""
        errors: dict[str, str] = {}
        if user_input is not None:
            return await self._async_create_station(
                user_input[CONF_STATION_ID].strip(), errors
            )

        return self.async_show_form(
            step_id="by_id",
            data_schema=vol.Schema({vol.Required(CONF_STATION_ID): str}),
            errors=errors,
        )

    async def _async_create_station(
        self, station_id: str, errors: dict[str, str] | None = None
    ) -> SubentryFlowResult:
        """Validate the id and create the subentry."""
        if errors is None:
            errors = {}

        for subentry in self._get_entry().subentries.values():
            if subentry.data.get(CONF_STATION_ID) == station_id:
                return self.async_abort(reason="already_configured")

        try:
            detail = await self._api.async_detail_by_id(station_id)
        except OpinetAuthError:
            errors["base"] = "invalid_auth"
        except OpinetError:
            errors["base"] = "not_found"
        else:
            name = detail.get("OS_NM") or station_id
            return self.async_create_entry(
                title=name,
                data={CONF_STATION_ID: station_id},
                unique_id=station_id,
            )

        # Validation failed -> re-show the id form with the error.
        return self.async_show_form(
            step_id="by_id",
            data_schema=vol.Schema({vol.Required(CONF_STATION_ID): str}),
            errors=errors,
        )

    @staticmethod
    def _format_station(station: dict[str, Any]) -> str:
        """Human-readable label for a search result."""
        brand = BRANDS.get(station.get("POLL_DIV_CD", ""), "")
        name = station.get("OS_NM", "")
        addr = station.get("NEW_ADR") or station.get("VAN_ADR") or ""
        parts = [p for p in (name, brand, addr) if p]
        return " · ".join(parts)
