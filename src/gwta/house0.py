"""The House0 plant with a Siegenthaler loop: a split heat pump whose
leaving water a three-way valve keeps on the loop or sends on, a buffer, a
store of tanks in series behind a charge/discharge valve, a zoned
distribution loop and an oil boiler as backup. Its physics is the FMU
generated from modelica/Beech.mo, which is Beech's plant: two zones and
three store tanks. This module says which of the FMU's outputs each channel
of such a house reads and which of its inputs each relay drives.
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
from gwta.plant_layout import PlantLayout
from gwta.sema.enums import TelemetryName
from gwta.sema.property_format import SpaceheatName, UTCMilliseconds
from gwta.sema.types import BoilerBackup, Hydronic
from gwta.sensing import device_encodings

VARIABLE_BY_PLANT_CHANNEL: dict[SpaceheatName, str] = {
    "hp-lwt": "hpLwt",
    "hp-ewt": "hpEwt",
    "sieg-hot": "siegHot",
    "sieg-cold": "siegCold",
    "buffer-hot-pipe": "bufferHotPipe",
    "dist-swt": "distSwt",
    "dist-rwt": "distRwt",
    "store-hot-pipe": "storeHotPipe",
    "store-cold-pipe": "storeColdPipe",
    "hp-odu-pwr": "hpOduPower",
    "hp-idu-pwr": "hpIduPower",
    "primary-pump-pwr": "primaryPumpPower",
    "store-pump-pwr": "storePumpPower",
    "dist-pump-pwr": "distPumpPower",
    "oil-boiler-pwr": "oilBoilerPower",
}

VARIABLE_BY_FLOW_CHANNEL: dict[SpaceheatName, str] = {
    "primary-flow": "primaryFlow",
    "sieg-flow": "siegFlow",
    "dist-flow": "distFlow",
    "store-flow": "storeFlow",
}

BUFFER_DEPTHS = 3
DEPTH_SUFFIXES = ("", "-device", "-micro-v")

# What each of a relay's two states is to the plant input the relay drives,
# by the state's name in the relay's relay.control.config. Hand-kept: the
# names are the values of store.flow.relay, heat.pump.control,
# aquastat.control.state, primary.pump.control, hp.loop.keep.send and
# heatcall.source, and the snapshot holds aquastat.control.state alone; the
# other five in the snapshot retire these strings.
STORE_FLOW = {"ChargingStore": 1.0, "DischargingStore": 0.0}
HEAT_PUMP_CONTROL = {"Scada": 1.0, "BufferTankAquastat": 0.0}
AQUASTAT_CONTROL = {"Scada": 1.0, "Boiler": 0.0}
PRIMARY_PUMP_CONTROL = {"Scada": 1.0, "HeatPump": 0.0}
KEEP_SEND = {"SendLess": 1.0, "SendMore": 0.0}
HEATCALL_SOURCE = {"Scada": 1.0, "WallThermostat": 0.0}


def variable_by_channel(layout: PlantLayout) -> dict[SpaceheatName, str]:
    """The FMU output behind every channel a House0 house with a
    Siegenthaler loop can show. Tank 1 is the hot tank; depth 1 is the top
    of a tank or of the buffer. The zone at circuit position i is the
    model's zone i. A flow is also behind its meter's pulse rate (`-hz`),
    and a depth behind its module's temperature (`-device`) and thermistor
    voltage (`-micro-v`). A zone's thermostat wire is behind the wire's power
    when its channel is a power reading and behind the call itself, 1 or 0,
    when its channel is a pin."""
    hydronic = layout.hydronic
    variables = dict(VARIABLE_BY_PLANT_CHANNEL)
    for flow, variable in VARIABLE_BY_FLOW_CHANNEL.items():
        variables[flow] = variables[f"{flow}-hz"] = variable
    for depth in range(1, BUFFER_DEPTHS + 1):
        for suffix in DEPTH_SUFFIXES:
            variables[f"buffer-depth{depth}{suffix}"] = f"bufferDepth[{depth}]"
    store = hydronic.water_store
    if store is not None:
        for tank in range(1, store.total_store_tanks + 1):
            for depth in range(1, store.temp_sensors_per_tank + 1):
                for suffix in DEPTH_SUFFIXES:
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
    """What each relay of the house that switches something the model has
    does in each of its states. The relay that powers the picos and the one
    on the thermostats' common wire switch nothing the model has. Left to
    itself the boiler keeps the buffer warm and the heat pump is not
    called: its own aquastat makes no call in the model."""
    effects = {
        "hp-scada-ops-relay": StateEffect("hpEnable", CONTACT),
        "primary-pump-failsafe-relay": StateEffect(
            "primaryPumpScadaControl", PRIMARY_PUMP_CONTROL
        ),
        "primary-pump-scada-ops-relay": StateEffect("primaryPumpOn", CONTACT),
        "hp-loop-on-off-relay": StateEffect("siegMotorOn", CONTACT),
        "hp-loop-keep-send-relay": StateEffect("siegTowardKeep", KEEP_SEND),
        "charge-discharge-relay": StateEffect("chargeDischarge", STORE_FLOW),
        "store-pump-relay": StateEffect("storePumpOn", CONTACT),
    }
    backup = hydronic.backup
    if isinstance(backup, BoilerBackup):
        if backup.failsafe_relay_name is None:
            raise ValueError("the boiler backup names no heat pump failsafe relay")
        effects[backup.failsafe_relay_name] = StateEffect(
            "hpScadaControl", HEAT_PUMP_CONTROL
        )
        effects[backup.intercept_relay_name] = StateEffect(
            "boilerScadaControl", AQUASTAT_CONTROL
        )
    for circuit in hydronic.zone_call_circuits:
        zone = circuit.circuit_position
        effects[circuit.failsafe_relay_node] = StateEffect(
            f"zoneScadaControl[{zone}]", HEATCALL_SOURCE
        )
        effects[circuit.ops_relay_node] = StateEffect(f"zoneScadaCall[{zone}]", CONTACT)
    return effects


def effect_by_relay(layout: PlantLayout) -> dict[SpaceheatName, RelayEffect]:
    """What each relay of the house drives, in the states the layout gives
    it."""
    return relay_effects(layout, state_effects(layout.hydronic))


def house0_model(
    *,
    fmu_path: Path,
    layout: PlantLayout,
    overrides: Mapping[str, float],
    start_ms: UTCMilliseconds,
) -> FmuPlantModel:
    """A House0 plant for one house, refused if the house has more or fewer
    zones or store tanks than the FMU was generated with."""
    outputs = [v.name for v in read_model_description(str(fmu_path)).modelVariables]
    fmu_zones = sum(1 for name in outputs if name.startswith("zoneTemperature["))
    fmu_tanks = sum(
        1 for name in outputs if name.startswith("tankDepth[") and name.endswith(",1]")
    )
    zones = len(layout.hydronic.zone_call_circuits)
    store = layout.hydronic.water_store
    tanks = 0 if store is None else store.total_store_tanks
    if (zones, tanks) != (fmu_zones, fmu_tanks):
        raise ValueError(
            f"the layout has {zones} zone circuits and {tanks} store tanks, and "
            f"{fmu_path.name} models {fmu_zones} zones and {fmu_tanks} tanks"
        )
    return FmuPlantModel(
        fmu_path=fmu_path,
        telemetry_by_channel=layout.telemetry_by_channel,
        variable_by_channel=variable_by_channel(layout),
        encoding_by_channel=device_encodings(layout),
        effect_by_relay=effect_by_relay(layout),
        overrides=overrides,
        start_ms=start_ms,
    )
