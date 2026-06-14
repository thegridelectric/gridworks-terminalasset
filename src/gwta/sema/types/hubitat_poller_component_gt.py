from typing import Literal
from gwta.sema.base import SemaType
from gwta.sema.property_format import PascalCase
from gwta.sema.property_format import UUID4Str
from gwta.sema.types.channel_config import ChannelConfig
from gwta.sema.types.hubitat_poller_gt import HubitatPollerGt


class HubitatPollerComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/hubitat.poller.component.gt/000"""

    component_id: UUID4Str
    device_type: PascalCase
    poller: HubitatPollerGt
    config_list: list[ChannelConfig]
    display_name: str | None = None
    hw_uid: str | None = None
    type_name: Literal["hubitat.poller.component.gt"] = "hubitat.poller.component.gt"
    version: Literal["000"] = "000"
