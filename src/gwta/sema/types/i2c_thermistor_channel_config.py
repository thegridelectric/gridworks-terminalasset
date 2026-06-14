from typing import Literal
from pydantic import StrictInt
from gwta.sema.base import SemaType
from gwta.sema.enums import I2cAdcChannel
from gwta.sema.enums import SpaceheatUnit
from gwta.sema.property_format import PositiveInt
from gwta.sema.property_format import SpaceheatName


class I2cThermistorChannelConfig(SemaType):
    """Sema: https://schemas.electricity.works/types/i2c.thermistor.channel.config/001"""

    channel_name: SpaceheatName
    poll_period_ms: PositiveInt | None = None
    capture_period_s: PositiveInt
    async_capture: bool
    async_capture_delta: PositiveInt | None = None
    exponent: StrictInt
    unit: SpaceheatUnit
    adc_channel: I2cAdcChannel
    send_to_derived: bool
    thermistor_beta: PositiveInt
    type_name: Literal["i2c.thermistor.channel.config"] = (
        "i2c.thermistor.channel.config"
    )
    version: Literal["001"] = "001"
