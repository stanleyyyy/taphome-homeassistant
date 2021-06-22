"""TapHome light integration."""
import typing

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_SWITCHES
from homeassistant.core import HomeAssistant

from .add_entry_request import AddEntryRequest
from .const import DOMAIN
from .coordinator import TapHomeDataUpdateCoordinator
from .taphome_sdk import *
from .taphome_entity import *


class SwitchConfigEntry(TapHomeConfigEntry):
    def __init__(self, device_config: dict):
        super(SwitchConfigEntry, self).__init__(device_config)
        self._device_class = self.get_optional(device_config, "device_class", None)

    @property
    def device_class(self):
        return self._device_class


class TapHomeSwitch(TapHomeEntity, SwitchEntity):
    """Representation of an switch"""

    def __init__(
        self,
        config_entry: SwitchConfigEntry,
        coordinator: TapHomeDataUpdateCoordinator,
        switch_service: SwitchService,
    ):
        super(TapHomeSwitch, self).__init__(config_entry.id, coordinator, SwitchState)
        self.switch_service = switch_service
        self._device_class = config_entry.device_class

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return self._device_class

    @property
    def is_on(self):
        """Returns if the switch entity is on or not."""
        if not self.taphome_state is None:
            return self.taphome_state.switch_state == SwitchStates.ON

    async def async_turn_on(self, **kwargs):
        """Turn device on."""
        await self.async_turn(SwitchStates.ON)

    async def async_turn_off(self):
        """Turn device off."""
        await self.async_turn(SwitchStates.OFF)

    async def async_turn(self, switch_state: SwitchStates):
        async with UpdateTapHomeState(self) as state:
            await self.switch_service.async_turn_switch(
                switch_state, self.taphome_device
            )
            state.switch_state = switch_state


def setup_platform(
    hass: HomeAssistant,
    config,
    add_entities,
    discovery_info=None,
) -> None:
    """Set up the switch platform."""
    add_entry_requests: typing.List[AddEntryRequest] = hass.data[DOMAIN][CONF_SWITCHES]
    switches = []
    for add_entry_request in add_entry_requests:
        switch_service = SwitchService(add_entry_request.tapHome_api_service)
        switch = TapHomeSwitch(
            add_entry_request.config_entry,
            add_entry_request.coordinator,
            switch_service,
        )
        switches.append(switch)

    add_entities(switches)