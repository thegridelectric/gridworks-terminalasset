from typing import Literal
from gwta.sema.base import SemaType
from gwta.sema.property_format import PascalCase
from gwta.sema.property_format import UUID4Str
from gwta.sema.types.relay_actor_config import RelayActorConfig


class SimRelayComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/sim.relay.component.gt/000"""

    component_id: UUID4Str
    device_type: PascalCase
    config_list: list[RelayActorConfig]
    display_name: str | None = None
    hw_uid: str | None = None
    type_name: Literal["sim.relay.component.gt"] = "sim.relay.component.gt"
    version: Literal["000"] = "000"
