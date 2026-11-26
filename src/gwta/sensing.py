"""What a simulated sensing device reports where its channel has the
device's own electrical reading and not the quantity it measures: a
thermistor's voltage, a flow meter's pulse rate, the level of a pin a heat
call is read from.
"""

import math
from collections.abc import Callable

from gwta.fmu_model import KELVIN_AT_0_C, M3_PER_S_PER_GPM, DeviceEncoding
from gwta.plant_layout import PlantLayout
from gwta.sema.enums import (
    GpmFromHzMethod,
    HeatCallInterpretation,
    TelemetryName,
    TempCalcMethod,
)
from gwta.sema.property_format import SpaceheatName
from gwta.sema.types import (
    GpioSensorComponentGt,
    I2cThermistorReaderComponentGt,
    SimPicoBtuMeterComponentGt,
    SimPicoFlowModuleComponentGt,
    SimPicoTankModuleComponentGt,
    SimSensorComponentGt,
)

# A thermistor: 10 kOhm at 298 K, read by a device that takes 0 C as 273 K.
# Hand-kept: the component words have the thermistor's beta and nothing
# else of it, and a word for the thermistor retires these.
THERMISTOR_R0_KOHMS = 10.0
THERMISTOR_T0_K = 298.0
READER_KELVIN_AT_0_C = 273.0

# A tank module's divider: 5.65 kOhm across the pico's 3.3 V. Hand-kept:
# pico.tank.module.component.gt has nothing of its divider, and a word for
# it retires these. A board's divider is its i2c.thermistor.interface.capability.
PICO_DIVIDER_KOHMS = 5.65
PICO_VOLTS = 3.3

# The level of a pin while its zone calls, for the interpretations that
# read a pin.
CALLING_LEVEL_BY_INTERPRETATION = {
    HeatCallInterpretation.DigitalZeroIsActive: 0,
    HeatCallInterpretation.DigitalOneIsActive: 1,
}

# The meter behind a flow that a sim.sensor.component.gt reads. Hand-kept:
# that word names no meter, and a flow read by a
# sim.pico.flow.module.component.gt, which does, retires this.
SIM_SENSOR_GALLONS_PER_PULSE = 0.0009


def thermistor_microvolts(
    beta: int, *, divider_kohms: float, volts: float
) -> Callable[[float], int]:
    """The voltage across a thermistor in a divider at a temperature in
    kelvin, in microvolts."""

    def encode(kelvin: float) -> int:
        reader_kelvin = kelvin - KELVIN_AT_0_C + READER_KELVIN_AT_0_C
        kohms = THERMISTOR_R0_KOHMS * math.exp(
            beta * (1 / reader_kelvin - 1 / THERMISTOR_T0_K)
        )
        return round(volts * kohms / (divider_kohms + kohms) * 1e6)

    return encode


def pin_level(calling_level: int) -> Callable[[float], int]:
    """The level of a pin on a thermostat wire from the model's call, 1
    while the thermostat circuit is closed and 0 while it is open."""

    def encode(call: float) -> int:
        return calling_level if round(call) == 1 else 1 - calling_level

    return encode


def pulse_microhertz(gallons_per_pulse: float) -> Callable[[float], int]:
    """The pulse rate of a flow meter at a flow in m3/s, in microhertz."""

    def encode(m3_per_s: float) -> int:
        gallons_per_s = m3_per_s / M3_PER_S_PER_GPM / 60
        return round(gallons_per_s / gallons_per_pulse * 1e6)

    return encode


def device_encoding(
    layout: PlantLayout, channel: SpaceheatName
) -> DeviceEncoding | None:
    """The encoding a channel's sensor gives it, or None where the
    telemetry alone decides it or the sensor has no reading of that kind."""
    telemetry = layout.telemetry_by_channel[channel]
    sensor = layout.sensor_by_channel[channel]
    if telemetry == TelemetryName.MicroVolts:
        if (
            isinstance(sensor, SimPicoTankModuleComponentGt)
            and sensor.temp_calc_method == TempCalcMethod.SimpleBeta
        ):
            return DeviceEncoding(
                "K",
                thermistor_microvolts(
                    sensor.thermistor_beta,
                    divider_kohms=PICO_DIVIDER_KOHMS,
                    volts=PICO_VOLTS,
                ),
            )
        if (
            isinstance(sensor, I2cThermistorReaderComponentGt)
            and sensor.temp_calc_method == TempCalcMethod.SimpleBeta
        ):
            adc = layout.thermistor_adc_by_channel[channel]
            [config] = [c for c in sensor.config_list if c.channel_name == channel]
            return DeviceEncoding(
                "K",
                thermistor_microvolts(
                    config.thermistor_beta,
                    divider_kohms=adc.series_resistance_k_ohms,
                    volts=adc.adc_reference_volts,
                ),
            )
    elif telemetry == TelemetryName.BinaryState:
        interpretation = layout.heat_call_interpretation_by_channel.get(channel)
        calling_level = (
            None
            if interpretation is None
            else CALLING_LEVEL_BY_INTERPRETATION.get(interpretation)
        )
        if isinstance(sensor, GpioSensorComponentGt) and calling_level is not None:
            return DeviceEncoding("1", pin_level(calling_level))
    elif telemetry == TelemetryName.MicroHz:
        if isinstance(sensor, SimSensorComponentGt):
            return DeviceEncoding(
                "m3/s", pulse_microhertz(SIM_SENSOR_GALLONS_PER_PULSE)
            )
        if (
            isinstance(sensor, SimPicoFlowModuleComponentGt)
            and sensor.gpm_from_hz_method == GpmFromHzMethod.Constant
        ):
            return DeviceEncoding(
                "m3/s", pulse_microhertz(sensor.constant_gallons_per_tick)
            )
        if (
            isinstance(sensor, SimPicoBtuMeterComponentGt)
            and sensor.gpm_from_hz_method == GpmFromHzMethod.Constant
        ):
            return DeviceEncoding("m3/s", pulse_microhertz(sensor.gallons_per_pulse))
    return None


def with_shared_thermistors(
    layout: PlantLayout, variable_by_channel: dict[SpaceheatName, str]
) -> dict[SpaceheatName, str]:
    """`variable_by_channel` with every channel a board reads from a
    thermistor given the variable of the channel on the same ADC input that
    has one: a thermistor's voltage reads what its temperature reads."""
    variables = dict(variable_by_channel)
    for channel, sensor in layout.sensor_by_channel.items():
        if not isinstance(sensor, I2cThermistorReaderComponentGt):
            continue
        adc_input = {c.channel_name: c.adc_channel for c in sensor.config_list}
        for other, variable in variable_by_channel.items():
            if adc_input.get(other) == adc_input[channel]:
                variables[channel] = variable
    return variables


def device_encodings(layout: PlantLayout) -> dict[SpaceheatName, DeviceEncoding]:
    """The channels of a layout that are encoded as their sensing device
    does."""
    encodings: dict[SpaceheatName, DeviceEncoding] = {}
    for channel in layout.telemetry_by_channel:
        encoding = device_encoding(layout, channel)
        if encoding is not None:
            encodings[channel] = encoding
    return encodings
