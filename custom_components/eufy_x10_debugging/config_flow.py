"""Config flow for Eufy X10 Pro Omni Debugging integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_DEVICE_ID, CONF_DEBUG_MODE

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_DEVICE_ID): str,
        vol.Optional(CONF_DEBUG_MODE, default=True): bool,
    }
)


class EufyX10DebugConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Eufy X10 Debugging."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Basic validation
            if not user_input[CONF_USERNAME]:
                errors["base"] = "invalid_username"
            elif not user_input[CONF_PASSWORD]:
                errors["base"] = "invalid_password"
            elif not user_input[CONF_DEVICE_ID]:
                errors["base"] = "invalid_device_id"
            else:
                # Check if already configured
                await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
                self._abort_if_unique_id_configured()
                
                # Create the entry
                _LOGGER.info("Creating Eufy X10 Debug entry for device: %s", user_input[CONF_DEVICE_ID])
                return self.async_create_entry(
                    title=f"Eufy X10 Debug ({user_input[CONF_DEVICE_ID]})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_import(self, import_config: dict) -> FlowResult:
        """Import a config entry from configuration.yaml."""
        return await self.async_step_user(import_config)


class EufyX10DebugOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Eufy X10 Debugging."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_DEBUG_MODE,
                        default=self.config_entry.options.get(CONF_DEBUG_MODE, True),
                    ): bool,
                }
            ),
        )