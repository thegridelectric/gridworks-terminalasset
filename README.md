# gridworks-terminalasset

A GridWorks **terminal asset** actor: the avatar for a real-world transactive
device — a heating system, a thermal store, an EV charger — represented as a
GNode that communicates over a RabbitMQ broker.

In the GridWorks fleet, a SCADA reports on behalf of a terminal asset and an
aggregator or leaf transactive node trades on its behalf. This repo holds the
terminal asset itself as a service built on
[gridworks-base](https://github.com/thegridelectric/gridworks-base).

## First use: simulated terminal assets

The first inhabitants of this repo are **simulated** terminal assets: actors
that model a (deliberately simple) heating system and publish synthetic sensor
telemetry over a broker, so that a whole house — terminal asset, sensors,
SCADA control — can be stood up in software and exercised end to end. The
simulated assets double as traffic generators for communications experiments:
tunable emission cadence, scriptable silence, and burst modes are first-class
features.

The longer arc is a hybrid fleet where simulated houses run alongside real
ones on the same brokers, indistinguishable in their communication patterns.

## Status

Early. The project scaffold (uv, gridworks-base dependency, a hello-world
actor that connects to a dev RabbitMQ broker and emits a heartbeat) is the
current work. Physics modeling beyond synthetic constant/sawtooth channels is
deliberately out of scope for now.

## Development

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```shell
uv sync
uv run pytest
```
