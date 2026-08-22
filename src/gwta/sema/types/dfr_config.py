from typing import Literal
from pydantic import StrictInt
from gwta.sema.base import SemaType
from gwta.sema.property_format import PositiveInt
from gwta.sema.property_format import SpaceheatName


class DfrConfig(SemaType):
    """Sema: https://schemas.electricity.works/types/dfr.config/000"""

    channel_name: SpaceheatName
    output_idx: PositiveInt
    initial_volts_times100: StrictInt
    type_name: Literal["dfr.config"] = "dfr.config"
    version: Literal["000"] = "000"
