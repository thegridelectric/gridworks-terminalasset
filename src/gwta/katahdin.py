"""The Katahdin plant: a monobloc heat pump on a glycol loop, a plate
exchanger, a three-tank store and a zoned distribution loop, with an oil
boiler or immersion elements as backup. Its physics is the FMU generated
from modelica/Katahdin.mo; this module says which of the FMU's outputs each
channel of a Katahdin house reads and which of its inputs each relay
drives.
"""

from collections.abc import Mapping
from pathlib import Path

from fmpy import read_model_description

from gwta.fmu_model import (
    CONTACT,
    FmuPlantModel,
    RelayEffect,
    StateEffect,
    relay_effects,
)
from gwta.sensing import device_encodings, with_shared_thermistors
from gwta.plant_layout import PlantLayout
from gwta.sema.enums import TelemetryName, ValveOpenOrClosed
from gwta.sema.property_format import SpaceheatName, UTCMilliseconds
from gwta.sema.types import BoilerBackup, Hydronic

VARIABLE_BY_PLANT_CHANNEL: dict[SpaceheatName, str] = {
    "hp-lwt": "hpLwt",
    "hp-ewt": "hpEwt",
    "secondary-lwt": "secondaryLwt",
    "secondary-ewt": "secondaryEwt",
    "dist-swt": "distSwt",
    "dist-rwt": "distRwt",
    "store-hot-pipe": "storeHotPipe",
    "store-cold-pipe": "storeColdPipe",
    "hp-odu-pwr": "hpOduPower",
    "hp-ctrl-box-pwr": "hpCtrlBoxPower",
    "dist-pump-pwr": "distPumpPower",
    "secondary-pump-pwr": "secondaryPumpPower",
}

VARIABLE_BY_FLOW_CHANNEL: dict[SpaceheatName, str] = {
    "primary-flow": "primaryFlow",
    "secondary-flow": "secondaryFlow",
    "dist-flow": "distFlow",
    "store-flow": "storeFlow",
}


VALVE = {
    ValveOpenOrClosed.ValveOpen.value: 1.0,
    ValveOpenOrClosed.ValveClosed.value: 0.0,
}


def variable_by_channel(layout: PlantLayout) -> dict[SpaceheatName, str]:
    """The FMU output behind every channel a Katahdin house can show. Tank 1
    is the hot tank and tank 3 the cold one; depth 1 is the top of a tank.
    The zone at circuit position i is the model's zone i. A flow is also
    behind its meter's pulse rate (`-hz`), and a tank depth behind its
    module's temperature (`-device`) and thermistor voltage (`-micro-v`). A
    zone's thermostat wire is behind the wire's power when its channel is a
    power reading and behind the call itself, 1 or 0, when its channel is a
    pin."""
    hydronic = layout.hydronic
    variables = dict(VARIABLE_BY_PLANT_CHANNEL)
    for flow, variable in VARIABLE_BY_FLOW_CHANNEL.items():
        variables[flow] = variables[f"{flow}-hz"] = variable
    store = hydronic.water_store
    if store is not None:
        for tank in range(1, store.total_store_tanks + 1):
            for depth in range(1, store.temp_sensors_per_tank + 1):
                for suffix in ("", "-device", "-micro-v"):
                    variables[f"tank{tank}-depth{depth}{suffix}"] = (
                        f"tankDepth[{tank},{depth}]"
                    )
    for circuit in hydronic.zone_call_circuits:
        zone = circuit.circuit_position
        wire = circuit.whitewire_channel_name
        variables[wire] = (
            f"zoneCall[{zone}]"
            if layout.telemetry_by_channel.get(wire) == TelemetryName.BinaryState
            else f"zoneCallPower[{zone}]"
        )
        if circuit.temp_channel_name is not None:
            variables[circuit.temp_channel_name] = f"zoneTemperature[{zone}]"
    return variables


def state_effects(hydronic: Hydronic) -> dict[SpaceheatName, StateEffect]:
    """What each relay of a Katahdin house that switches something the
    model has does in each of its states. The boiler's valve is in a house
    with a boiler. The boiler's intercept relay switches nothing the model
    has: the model's boiler fires on its own aquastat."""
    effects = {
        "v1-hx-house-relay": StateEffect("v1Position", VALVE),
        "v2-store-hot-relay": StateEffect("v2Position", VALVE),
        "v3-store-cold-relay": StateEffect("v3Position", VALVE),
        "v4-house-return-relay": StateEffect("v4Position", VALVE),
        "secondary-pump-relay": StateEffect("secondaryPumpOn", CONTACT),
        "hp-scada-ops-relay": StateEffect("hpEnable", CONTACT),
    }
    if isinstance(hydronic.backup, BoilerBackup):
        effects["v5-boiler-relay"] = StateEffect("v5Position", VALVE)
    return effects


def effect_by_relay(layout: PlantLayout) -> dict[SpaceheatName, RelayEffect]:
    """What each relay of a Katahdin house drives, in the states the layout
    gives it."""
    return relay_effects(layout, state_effects(layout.hydronic))


def katahdin_model(
    *,
    fmu_path: Path,
    layout: PlantLayout,
    overrides: Mapping[str, float],
    start_ms: UTCMilliseconds,
) -> FmuPlantModel:
    """A Katahdin plant for one house, refused if the house has more or
    fewer zones than the FMU was generated with."""
    zones = len(layout.hydronic.zone_call_circuits)
    fmu_zones = sum(
        1
        for variable in read_model_description(str(fmu_path)).modelVariables
        if variable.name.startswith("zoneTemperature[")
    )
    if zones != fmu_zones:
        raise ValueError(
            f"the layout has {zones} zone circuits and {fmu_path.name} models "
            f"{fmu_zones} zones"
        )
    return FmuPlantModel(
        fmu_path=fmu_path,
        telemetry_by_channel=layout.telemetry_by_channel,
        variable_by_channel=with_shared_thermistors(
            layout, variable_by_channel(layout)
        ),
        encoding_by_channel=device_encodings(layout),
        effect_by_relay=effect_by_relay(layout),
        overrides=overrides,
        start_ms=start_ms,
    )
