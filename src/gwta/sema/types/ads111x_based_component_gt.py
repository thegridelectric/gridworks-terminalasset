from typing import Literal
from pydantic import StrictFloat
from gwta.sema.base import SemaType
from gwta.sema.property_format import PascalCase
from gwta.sema.property_format import UUID4Str
from gwta.sema.types.ads_channel_config import AdsChannelConfig


class Ads111xBasedComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/ads111x.based.component.gt/000"""

    component_id: UUID4Str
    device_type: PascalCase
    config_list: list[AdsChannelConfig]
    open_voltage_by_ads: list[StrictFloat]
    display_name: str | None = None
    hw_uid: str | None = None
    type_name: Literal["ads111x.based.component.gt"] = "ads111x.based.component.gt"
    version: Literal["000"] = "000"
