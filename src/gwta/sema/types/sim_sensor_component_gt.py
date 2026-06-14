from typing import Literal
from gwta.sema.base import SemaType
from gwta.sema.property_format import PascalCase
from gwta.sema.property_format import UUID4Str
from gwta.sema.types.channel_config import ChannelConfig


class SimSensorComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/sim.sensor.component.gt/000"""

    component_id: UUID4Str
    device_type: PascalCase
    config_list: list[ChannelConfig]
    display_name: str | None = None
    hw_uid: str | None = None
    type_name: Literal["sim.sensor.component.gt"] = "sim.sensor.component.gt"
    version: Literal["000"] = "000"
