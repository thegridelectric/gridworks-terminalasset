from typing import Literal
from gwta.sema.base import SemaType
from gwta.sema.property_format import PascalCase
from gwta.sema.property_format import PositiveInt
from gwta.sema.property_format import UUID4Str
from gwta.sema.types.electric_meter_channel_config import ElectricMeterChannelConfig


class ElectricMeterComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/electric.meter.component.gt/002"""

    component_id: UUID4Str
    device_type: PascalCase
    config_list: list[ElectricMeterChannelConfig]
    modbus_host: str | None = None
    modbus_port: PositiveInt | None = None
    display_name: str | None = None
    hw_uid: str | None = None
    type_name: Literal["electric.meter.component.gt"] = "electric.meter.component.gt"
    version: Literal["002"] = "002"
