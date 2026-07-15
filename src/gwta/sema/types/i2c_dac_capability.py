from typing import Literal
from gwta.sema.base import SemaType
from gwta.sema.enums import I2cDacType
from gwta.sema.property_format import NonNegativeInt
from gwta.sema.property_format import PascalCase
from gwta.sema.property_format import PositiveInt


class I2cDacCapability(SemaType):
    """Sema: https://schemas.electricity.works/types/i2c.dac.capability/000"""

    dac_name: PascalCase
    i2c_bus: PascalCase
    i2c_address: NonNegativeInt
    dac_type: I2cDacType
    channels: PositiveInt
    type_name: Literal["i2c.dac.capability"] = "i2c.dac.capability"
    version: Literal["000"] = "000"
