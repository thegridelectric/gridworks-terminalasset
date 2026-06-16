from typing import Any, Literal
from gwta.sema.base import SemaType
from gwta.sema.types.ads111x_based_device_type_gt import Ads111xBasedDeviceTypeGt
from gwta.sema.types.data_channel_gt import DataChannelGt
from gwta.sema.types.derived_channel_gt import DerivedChannelGt
from gwta.sema.types.electric_meter_component_gt import ElectricMeterComponentGt
from gwta.sema.types.electric_meter_device_type_gt import ElectricMeterDeviceTypeGt
from gwta.sema.types.g_node_gt import GNodeGt
from gwta.sema.types.gw108_gpio_sensor_component_gt import Gw108GpioSensorComponentGt
from gwta.sema.types.gw108_vdc_relay_component_gt import Gw108VdcRelayComponentGt
from gwta.sema.types.i2c_multichannel_dt_relay_component_gt import (
    I2cMultichannelDtRelayComponentGt,
)
from gwta.sema.types.i2c_thermistor_reader_component_gt import (
    I2cThermistorReaderComponentGt,
)
from gwta.sema.types.pico_btu_meter_component_gt import PicoBtuMeterComponentGt
from gwta.sema.types.pico_tank_module_component_gt import PicoTankModuleComponentGt
from gwta.sema.types.scada_device_type_gt import ScadaDeviceTypeGt
from gwta.sema.types.sim_pico_tank_module_component_gt import (
    SimPicoTankModuleComponentGt,
)
from gwta.sema.types.spaceheat_node_gt import SpaceheatNodeGt
from gwta.sema.types.web_server_component_gt import WebServerComponentGt


class NolanLayout(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.nolan.layout/000"""

    g_nodes: list[GNodeGt]
    sh_nodes: list[SpaceheatNodeGt]
    data_channels: list[DataChannelGt]
    derived_channels: list[DerivedChannelGt]
    components: list[
        ElectricMeterComponentGt
        | Gw108GpioSensorComponentGt
        | Gw108VdcRelayComponentGt
        | I2cMultichannelDtRelayComponentGt
        | I2cThermistorReaderComponentGt
        | PicoBtuMeterComponentGt
        | PicoTankModuleComponentGt
        | SimPicoTankModuleComponentGt
        | WebServerComponentGt
    ]
    device_types: list[
        ElectricMeterDeviceTypeGt | Ads111xBasedDeviceTypeGt | ScadaDeviceTypeGt
    ]
    hydronic: dict[str, Any]
    type_name: Literal["gw.nolan.layout"] = "gw.nolan.layout"
    version: Literal["000"] = "000"
