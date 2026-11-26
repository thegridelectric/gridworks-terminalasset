"""What a simulated plant reads from its house's hardware layout."""

import json
from pathlib import Path
from typing import NamedTuple

from gwbase.sema.enums import GwGNodeClass

from gwta.sema.codec import SemaCodec
from gwta.sema.enums import (
    ActorClass,
    HeatCallInterpretation,
    SimDeviceType,
    TelemetryName,
)
from gwta.sema.property_format import LeftRightDot, SpaceheatName
from gwta.sema.types import (
    ElectricMeterComponentGt,
    GNodeGt,
    GpioRelayComponentGt,
    GpioSensorComponentGt,
    House0Layout,
    House0NoSieg,
    Hydronic,
    I2cRelayComponentGt,
    I2cThermistorInterfaceCapability,
    I2cThermistorReaderComponentGt,
    KatahdinLayout,
    RelayControlConfig,
    ScadaBoardComponentGt,
    ScadaDeviceTypeGt,
    SimPicoBtuMeterComponentGt,
    SimPicoFlowModuleComponentGt,
    SimPicoTankModuleComponentGt,
    SimSensorComponentGt,
)

# The layout words a plant reads: one House0 house, with a Siegenthaler loop
# or without, or one Katahdin house.
Layout = House0Layout | House0NoSieg | KatahdinLayout
LAYOUT_WORDS = (House0Layout, House0NoSieg, KatahdinLayout)

# A board's own inputs: what the scada reads on the pins and the ADCs of its
# board, with no sensing device of another type between.
BoardInput = GpioSensorComponentGt | I2cThermistorReaderComponentGt
BOARD_INPUTS = (GpioSensorComponentGt, I2cThermistorReaderComponentGt)

SensingComponent = (
    BoardInput
    | ElectricMeterComponentGt
    | SimPicoBtuMeterComponentGt
    | SimPicoFlowModuleComponentGt
    | SimPicoTankModuleComponentGt
    | SimSensorComponentGt
)
SENSING_COMPONENTS = (
    *BOARD_INPUTS,
    ElectricMeterComponentGt,
    SimPicoBtuMeterComponentGt,
    SimPicoFlowModuleComponentGt,
    SimPicoTankModuleComponentGt,
    SimSensorComponentGt,
)


# The derived channel that makes a heat call from a raw input, and where it
# says how to read that input. Hand-kept: derived.channel.gt has Strategy
# and Parameters as free text, and a word for a heat call's derivation
# retires these.
HEAT_CALL_STRATEGY = "heat-call"
HEAT_CALL_INTERPRETATION = "Interpretation"


class PlantLayout(NamedTuple):
    """The plant's view of a layout: who it is, which scada it serves, the
    channels it shows that scada with the device that senses each, the
    relays it hears from it with what each one's two positions are, and the
    hydronic plant those belong to. A thermistor the board reads has the
    board's ADC for its channels, and a pin a heat call is read from has
    that heat call's interpretation. Interior to the plant; every field is
    read off the layout word."""

    g_node: GNodeGt
    scada_alias: LeftRightDot
    telemetry_by_channel: dict[SpaceheatName, TelemetryName]
    sensor_by_channel: dict[SpaceheatName, SensingComponent]
    thermistor_adc_by_channel: dict[SpaceheatName, I2cThermistorInterfaceCapability]
    heat_call_interpretation_by_channel: dict[SpaceheatName, HeatCallInterpretation]
    relay_names: frozenset[SpaceheatName]
    config_by_relay: dict[SpaceheatName, RelayControlConfig]
    hydronic: Hydronic


def g_node_of_class(layout: Layout, g_node_class: GwGNodeClass) -> GNodeGt:
    found = [g for g in layout.g_nodes if g.g_node_class == g_node_class.value]
    if len(found) != 1:
        raise ValueError(
            f"layout has {len(found)} {g_node_class.value} GNodes, expected one"
        )
    return found[0]


def thermistor_adc(
    layout: Layout, reader: I2cThermistorReaderComponentGt, board_type: str
) -> I2cThermistorInterfaceCapability:
    """The ADC of the reader's board that the reader is on."""
    found = [
        adc
        for device_type in layout.device_types
        if isinstance(device_type, ScadaDeviceTypeGt)
        and device_type.device_type == board_type
        for adc in device_type.thermistor_adcs or []
        if adc.name == reader.adc_name
    ]
    if len(found) != 1:
        raise ValueError(
            f"{board_type} has {len(found)} thermistor ADCs named "
            f"{reader.adc_name}, expected one"
        )
    return found[0]


def plant_layout(layout: Layout) -> PlantLayout:
    """A channel is the plant's to show when the component of the node that
    captures it is a sensing device of a simulated type, or an input of a
    board of a simulated type. A relay's state and an output's level are
    the scada's own and stay out. The layout word holds every channel of a
    disabled node in DisabledChannelNames, so the channel list alone
    decides what is left out."""
    simulated = set(SimDeviceType.values())
    board_type_by_component_id = {
        c.component_id: c.device_type
        for c in layout.components
        if isinstance(c, ScadaBoardComponentGt)
    }

    def device_type(component: SensingComponent) -> str | None:
        if isinstance(component, BOARD_INPUTS):
            return board_type_by_component_id.get(component.board_component_id)
        return component.device_type

    sensor_by_component_id: dict[str, SensingComponent] = {
        c.component_id: c
        for c in layout.components
        if isinstance(c, SENSING_COMPONENTS) and device_type(c) in simulated
    }
    sensor_by_node = {
        n.name: sensor_by_component_id[n.component_id]
        for n in layout.sh_nodes
        if n.component_id in sensor_by_component_id
    }
    disabled_channels = set(layout.disabled_channel_names)
    shown = [
        ch
        for ch in layout.data_channels
        if ch.captured_by_node_name in sensor_by_node
        and ch.name not in disabled_channels
    ]
    return PlantLayout(
        g_node=g_node_of_class(layout, GwGNodeClass.TerminalAsset),
        scada_alias=g_node_of_class(layout, GwGNodeClass.Scada).alias,
        telemetry_by_channel={ch.name: ch.telemetry_name for ch in shown},
        sensor_by_channel={
            ch.name: sensor_by_node[ch.captured_by_node_name] for ch in shown
        },
        thermistor_adc_by_channel={
            ch.name: thermistor_adc(layout, reader, str(device_type(reader)))
            for ch in shown
            if isinstance(
                reader := sensor_by_node[ch.captured_by_node_name],
                I2cThermistorReaderComponentGt,
            )
        },
        heat_call_interpretation_by_channel={
            name: HeatCallInterpretation(derived.parameters[HEAT_CALL_INTERPRETATION])
            for derived in layout.derived_channels
            if derived.strategy == HEAT_CALL_STRATEGY
            and derived.parameters is not None
            and HEAT_CALL_INTERPRETATION in derived.parameters
            for name in derived.input_channel_names
        },
        relay_names=frozenset(
            n.name for n in layout.sh_nodes if n.actor_class == ActorClass.Relay
        ),
        config_by_relay={
            config.actor_name: config
            for c in layout.components
            if isinstance(c, (I2cRelayComponentGt, GpioRelayComponentGt))
            for config in c.config_list
        },
        hydronic=layout.hydronic,
    )


def load_layout(path: Path) -> Layout:
    decoded = SemaCodec().from_dict(json.loads(path.read_text()))
    if not isinstance(decoded, LAYOUT_WORDS):
        raise ValueError(
            f"{path} holds a {type(decoded).__name__}, and a plant reads a "
            f"{' or a '.join(word.__name__ for word in LAYOUT_WORDS)}"
        )
    return decoded


def load_plant_layout(path: Path) -> PlantLayout:
    return plant_layout(load_layout(path))
