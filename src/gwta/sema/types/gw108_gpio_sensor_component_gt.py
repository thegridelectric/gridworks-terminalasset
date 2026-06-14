from typing import Literal
from gwta.sema.base import SemaType
from gwta.sema.enums import GpioSenseMode
from gwta.sema.property_format import PascalCase
from gwta.sema.property_format import PositiveInt
from gwta.sema.property_format import UUID4Str
from gwta.sema.types.channel_config import ChannelConfig


class Gw108GpioSensorComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/gw108.gpio.sensor.component.gt/002"""

    component_id: UUID4Str
    device_type: PascalCase
    config_list: list[ChannelConfig]
    gpio_pin: PositiveInt
    sense_mode: GpioSenseMode
    send_to_derived: bool
    display_name: str | None = None
    hw_uid: str | None = None
    type_name: Literal["gw108.gpio.sensor.component.gt"] = (
        "gw108.gpio.sensor.component.gt"
    )
    version: Literal["002"] = "002"
