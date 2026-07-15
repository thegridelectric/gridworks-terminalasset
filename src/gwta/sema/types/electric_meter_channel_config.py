from typing import Literal
from gwta.sema.base import SemaType
from gwta.sema.property_format import SpaceheatName
from gwta.sema.types.egauge_register_config import EgaugeRegisterConfig


class ElectricMeterChannelConfig(SemaType):
    """Sema: https://schemas.electricity.works/types/electric.meter.channel.config/001"""

    channel_name: SpaceheatName
    egauge_register_config: EgaugeRegisterConfig | None = None
    type_name: Literal["electric.meter.channel.config"] = (
        "electric.meter.channel.config"
    )
    version: Literal["001"] = "001"
