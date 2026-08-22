from typing import Literal
from pydantic import model_validator
from gwta.sema.base import SemaType
from gwta.sema.enums import ZoneActuatorKind
from gwta.sema.enums import ZoneCircuitRole
from gwta.sema.enums import ZoneSetpointSource
from gwta.sema.property_format import PositiveInt
from gwta.sema.property_format import SpaceheatName
from gwta.sema.types.zone_thermostat import ZoneThermostat


class ZoneCallCircuit(SemaType):
    """Sema: https://schemas.electricity.works/types/gw1.zone.call.circuit/000"""

    circuit_position: PositiveInt
    serves_zone: SpaceheatName
    actuator_kind: ZoneActuatorKind
    role: ZoneCircuitRole
    can_cool: bool
    setpoint_source: ZoneSetpointSource
    thermostat: ZoneThermostat
    whitewire_channel_name: SpaceheatName
    failsafe_relay_node: SpaceheatName
    ops_relay_node: SpaceheatName
    type_name: Literal["gw1.zone.call.circuit"] = "gw1.zone.call.circuit"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "ZoneCallCircuit":
        """
        Axiom 1: FloorLoopsCannotCool
        If ActuatorKind is FloorLoop, CanCool SHALL be false.
        """
        if self.actuator_kind == ZoneActuatorKind.FloorLoop and self.can_cool:
            raise ValueError(
                "Axiom 1 (FloorLoopsCannotCool) failed: ActuatorKind is "
                "FloorLoop, so CanCool SHALL be false."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "ZoneCallCircuit":
        """
        Axiom 2: ReadSetpointNeedsCommsStat
        If SetpointSource is FromThermostat, Thermostat.Kind SHALL NOT be MechanicalDial.
        """
        # String comparison, not an enum import: ThermostatKind is not a field
        # enum of this type, and an absolute sema.runtime import would break
        # inside a restricted snapshot package.
        if (
            self.setpoint_source == ZoneSetpointSource.FromThermostat
            and self.thermostat.kind == "MechanicalDial"
        ):
            raise ValueError(
                "Axiom 2 (ReadSetpointNeedsCommsStat) failed: SetpointSource is "
                "FromThermostat, so Thermostat.Kind SHALL NOT be MechanicalDial."
            )
        return self
