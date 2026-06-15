# Samples

Canonical JSON instances, one per seeded **type** version that carries
an `examples:` block. Generated from the authored examples (never edited
by hand) and consumed by `roundtrip.py`. A type version without a sample
is silently untested by the round-trip, so its absence is recorded here.

Coverage: **33 of 38** seeded type versions have a sample.

Seeded type versions lacking a sample (no `examples:`):

- `ads111x.based.device.type.gt.000`
- `electric.meter.device.type.gt.000`
- `gw.nolan.layout.000`
- `gw1.scada.device.type.gt.000`
- `spaceheat.telemetry.quantity.projection.000`
