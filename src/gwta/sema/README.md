# STAGING SNAPSHOT — PLEASE ONLY USE IN DEV

This snapshot contains STAGING vocabulary: mutable words that run on dev
brokers only. It MUST NOT be used against hybrid or production brokers.

Staging words in this snapshot:

- enum gpio.sense.mode:000
- enum gw.house0.primary.flow.source:000
- enum i2c.adc.channel
- enum i2c.adc.type:000
- enum i2c.dac.type:000
- enum thermistor.data.method:000
- type ads.channel.config:001
- type ads111x.based.component.gt:000
- type ads111x.based.device.type.gt:000
- type dfr.component.gt:000
- type dfr.config:001
- type egauge.register.config:000
- type electric.meter.channel.config:001
- type electric.meter.component.gt:002
- type electric.meter.device.type.gt:000
- type gw.house0.hydronic:000
- type gw.house0.layout:000
- type gw.native.gpio.pin:000
- type gw.nolan.layout:000
- type gw1.hvac.zone:000
- type gw1.scada.device.type.gt:000
- type gw1.simple.sim.layout:000
- type gw108.gpio.sensor.component.gt:002
- type gw108.vdc.relay.component.gt:002
- type hubitat.component.gt:000
- type hubitat.poller.component.gt:000
- type i2c.adc.capability:000
- type i2c.bus:000
- type i2c.dac.capability:000
- type i2c.expander:000
- type i2c.multichannel.dt.relay.component.gt:005
- type i2c.relay.capability:000
- type i2c.thermistor.channel.config:002
- type i2c.thermistor.interface.capability:000
- type i2c.thermistor.reader.component.gt:002
- type pico.btu.meter.component.gt:001
- type pico.flow.module.component.gt:001
- type pico.tank.module.component.gt:012
- type relay.actor.config:004
- type sim.pico.tank.module.component.gt:001
- type sim.relay.component.gt:000
- type sim.sensor.component.gt:000
- type web.server.component.gt:002

When these words promote to published, rebuild without `--allow-staged` to
get a publication-grade snapshot (and this file disappears).
