from typing import Literal
from gwta.sema.base import SemaType
from gwta.sema.enums import I2cAdcType
from gwta.sema.property_format import NonNegativeInt
from gwta.sema.property_format import PascalCase
from gwta.sema.property_format import PositiveFloat


class I2cThermistorInterfaceConfig(SemaType):
    """Sema: https://schemas.electricity.works/types/i2c.thermistor.interface.config/000"""

    name: PascalCase
    i2c_bus: PascalCase
    i2c_address: NonNegativeInt
    adc_type: I2cAdcType
    adc_reference_volts: PositiveFloat
    series_resistance_k_ohms: PositiveFloat
    type_name: Literal["i2c.thermistor.interface.config"] = (
        "i2c.thermistor.interface.config"
    )
    version: Literal["000"] = "000"
