from typing import Literal
from pydantic import StrictInt
from gwta.sema.base import SemaType
from gwta.sema.enums import SpaceheatUnit
from gwta.sema.property_format import PositiveInt
from gwta.sema.property_format import SpaceheatName
from gwta.sema.types.egauge_register_config import EgaugeRegisterConfig


class ElectricMeterChannelConfig(SemaType):
    """Sema: https://schemas.electricity.works/types/electric.meter.channel.config/000"""

    channel_name: SpaceheatName
    poll_period_ms: PositiveInt | None = None
    capture_period_s: PositiveInt
    async_capture: bool
    async_capture_delta: PositiveInt | None = None
    exponent: StrictInt
    unit: SpaceheatUnit
    egauge_register_config: EgaugeRegisterConfig | None = None
    type_name: Literal["electric.meter.channel.config"] = (
        "electric.meter.channel.config"
    )
    version: Literal["000"] = "000"
