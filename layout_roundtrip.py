"""Hack: bidirectional layout round-trip between terminalasset and scada.

terminalasset (this script) SENDS a layout — built and canonicalized through the
gwta Sema snapshot — to scada, which RETURNS it (decoded + re-encoded through
gwsproto). We then decode the returned bytes through the gwta snapshot again and
confirm they match. A green run proves scada and gwta agree on the layout type's
wire contract — the focused, layout-only round-trip.

The loop this serves: edit the layout type in Sema -> snapshot to gwta ->
hand-port to gwsproto -> run this script.

    uv run python layout_roundtrip.py [gw.house0.layout]
"""

import json
import subprocess
import sys
from pathlib import Path

from gwta.sema.codec import default_codec

SHARED = Path("/tmp/gw_layout_roundtrip")
SCADA = Path(__file__).resolve().parent.parent / "gridworks-scada"
SCADA_PY = SCADA / "gw_spaceheat" / "venv" / "bin" / "python"
SCADA_RETURN = SCADA / "gw_spaceheat" / "layout_roundtrip_return.py"


def main() -> int:
    type_name = sys.argv[1] if len(sys.argv) > 1 else "gw.house0.layout"
    SHARED.mkdir(parents=True, exist_ok=True)
    outbound_path = SHARED / "outbound.json"
    returned_path = SHARED / "returned.json"

    # SEND: build a minimal instance and canonicalize it through the gwta snapshot.
    cls = default_codec.registry.get(type_name)
    if cls is None:
        print(f"gwta snapshot has no type {type_name!r}")
        return 2
    instance = {"TypeName": type_name, "Version": cls.version_value()}
    outbound = default_codec.from_dict(instance).to_dict()
    outbound_path.write_text(json.dumps(outbound, indent=2))
    print(f"gwta: sent {type_name} -> {outbound_path}")

    # scada RETURNS it (decode + re-encode through gwsproto), in scada's venv.
    subprocess.run(
        [str(SCADA_PY), str(SCADA_RETURN), str(outbound_path), str(returned_path)],
        check=True,
    )

    # VERIFY: decode the returned bytes through the gwta snapshot and compare.
    returned = json.loads(returned_path.read_text())
    decoded = default_codec.from_dict(returned).to_dict()
    if decoded == outbound:
        print(f"ROUND-TRIP OK: {type_name} survived gwta -> scada -> gwta unchanged.")
        return 0
    print(
        f"ROUND-TRIP MISMATCH for {type_name}:\n"
        f"  outbound={outbound}\n  returned={returned}"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
