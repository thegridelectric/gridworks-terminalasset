"""ta_link_roundtrip — gwta side of the scada<->terminalasset broker round-trip.

This is the COMMUNICATION harness, not the type validator. It binds a queue on the
dev rabbit (vhost d1__1) and decodes each body through gwta's codegen'd sema
snapshot (`gwta.sema.codec.default_codec`). Its job is to exercise the real
terminalasset<->scada comms path over the broker.

(Type validation — does a hand-written gwsproto type match the sema schema — is done
separately against the sema runtime directly via `sema validate`, since sema is the
source of truth and gwta's snapshot is only a codegen'd copy of it. That said, while
gwsproto is not yet codegen'd from sema, a clean decode here also confirms scada's
hand-written types survive the wire.)

    gridworks-terminalasset/.venv/bin/python ta_link_roundtrip_consumer.py
"""

import json

import pika

from gwta.sema.codec import default_codec

URL = "amqp://smqPublic:smqPublic@localhost:5672/d1__1"
EXCHANGE = "amq.topic"
RESULTS = "/tmp/ta_link_roundtrip_results.jsonl"


def on_message(ch, method, properties, body):
    rec = {"routing_key": method.routing_key}
    try:
        data = json.loads(body.decode())
        if isinstance(data, dict) and "Payload" in data and isinstance(data["Payload"], dict):
            data = data["Payload"]
        rec["type_name"] = data.get("TypeName")
        obj = default_codec.from_dict(data, mode="strict")
        rec["ok"] = True
        print(f"[gwta] ✓ {rec['type_name']} -> {type(obj).__name__}", flush=True)
    except Exception as e:
        rec["ok"] = False
        rec["error"] = f"{type(e).__name__}: {e}"
        print(f"[gwta] ✗ {rec.get('type_name')}: {rec['error']}", flush=True)
    with open(RESULTS, "a") as f:
        f.write(json.dumps(rec) + "\n")
    ch.basic_ack(method.delivery_tag)


def main() -> None:
    conn = pika.BlockingConnection(pika.URLParameters(URL))
    ch = conn.channel()
    q = ch.queue_declare(queue="", exclusive=True).method.queue
    ch.queue_bind(exchange=EXCHANGE, queue=q, routing_key="#")
    ch.basic_consume(queue=q, on_message_callback=on_message)
    print(f"[gwta] consuming {EXCHANGE} '#' on d1__1; results -> {RESULTS}", flush=True)
    ch.start_consuming()


if __name__ == "__main__":
    main()
