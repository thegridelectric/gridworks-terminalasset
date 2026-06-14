from typing import Literal
from gwta.sema.base import SemaType
from gwta.sema.property_format import PascalCase
from gwta.sema.property_format import PositiveInt
from gwta.sema.property_format import UUID4Str
from gwta.sema.types.dfr_config import DfrConfig


class DfrComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/dfr.component.gt/000"""

    component_id: UUID4Str
    device_type: PascalCase
    config_list: list[DfrConfig]
    i2c_address_list: list[PositiveInt]
    display_name: str | None = None
    hw_uid: str | None = None
    type_name: Literal["dfr.component.gt"] = "dfr.component.gt"
    version: Literal["000"] = "000"
