from typing import Literal
from gwta.sema.base import SemaType
from gwta.sema.enums import RelayWiringConfig
from gwta.sema.property_format import PascalCase
from gwta.sema.types.i2c_bit_address import I2cBitAddress


class I2cRelayConfig(SemaType):
    """Sema: https://schemas.electricity.works/types/i2c.relay.config/000"""

    relay_name: PascalCase
    i2c_bus: PascalCase
    address: I2cBitAddress
    supported_wiring_configs: list[RelayWiringConfig]
    notes: str | None = None
    type_name: Literal["i2c.relay.config"] = "i2c.relay.config"
    version: Literal["000"] = "000"
