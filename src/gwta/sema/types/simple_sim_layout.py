from typing import Literal
from gwta.sema.base import SemaType


class SimpleSimLayout(SemaType):
    """Sema: https://schemas.electricity.works/types/gw1.simple.sim.layout/000"""

    type_name: Literal["gw1.simple.sim.layout"] = "gw1.simple.sim.layout"
    version: Literal["000"] = "000"
