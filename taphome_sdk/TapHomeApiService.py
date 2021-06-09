import logging
from .Device import Device
from .Location import Location
from .TapHomeHttpClientFactory import TapHomeHttpClientFactory
from .ValueChangeResult import ValueChangeResult
from .ValueType import ValueType


_LOGGER = logging.getLogger(__name__)


class TapHomeApiService:
    def __init__(self, tapHomeHttpClient: TapHomeHttpClientFactory._TapHomeHttpClient):
        self.tapHomeHttpClient = tapHomeHttpClient

    async def async_discovery_devices(self):
        json = {}
        try:
            json = await self.tapHomeHttpClient.async_api_get("discovery")
            devices = []
            for device in json["devices"]:
                try:
                    devices.append(Device.create(device))
                except Exception:
                    _LOGGER.exception(f"Device.create fails \n {device} \n {json}")
            return devices
        except Exception:
            _LOGGER.exception(f"async_discovery_devices fails \n {json}")

    async def async_get_location(self):
        json = {}
        try:
            json = await self.tapHomeHttpClient.async_api_get("location")
            return Location.create(json)
        except Exception:
            _LOGGER.exception(f"async_get_location fails \n {json}")

    async def async_get_device_values(self, deviceId: int):
        deviceInfo = None
        try:
            deviceInfo = await self.tapHomeHttpClient.async_api_get(
                f"getDeviceValue/{deviceId}"
            )
            return deviceInfo["values"]
        except Exception:
            _LOGGER.exception(
                f"async_get_device_values for {deviceId} fails \n {deviceInfo}"
            )

    async def async_set_device_values(
        self, deviceId: int, values: list
    ) -> ValueChangeResult:
        json = None
        try:
            requestBody = {
                "deviceId": deviceId,
                "values": values,
            }
            json = await self.tapHomeHttpClient.async_api_post(
                "setDeviceValue", requestBody
            )
            results = json["valuesChanged"]

            return (
                ValueChangeResult.FAILED
                if any(
                    (
                        result
                        for result in results
                        if result["result"] == ValueChangeResult.FAILED
                    )
                )
                else ValueChangeResult.CHANGED
            )
        except Exception:
            _LOGGER.exception(f"async_get_device_values for {deviceId} fails \n {json}")
            return ValueChangeResult.FAILED

    def create_device_value(self, valueType: ValueType, value):
        return {
            "valueTypeId": valueType.value,
            "value": value,
        }
