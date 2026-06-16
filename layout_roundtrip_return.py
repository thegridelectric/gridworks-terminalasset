"""gwta side of the scada-originated layout round-trip.

Reads a Sema layout instance that scada SENT (built from a real dc layout via the
house0 bijection), decodes it through the gwta snapshot, re-encodes it, and writes
it back. Invoked by gridworks-scada/gw_spaceheat/layout_roundtrip.py using the
gwta (terminalasset) venv.

    python layout_roundtrip_return.py <infile.json> <outfile.json>
"""

import json
import sys

from gwta.sema.codec import default_codec


def main() -> int:
    infile, outfile = sys.argv[1], sys.argv[2]
    data = json.loads(open(infile).read())

    returned = default_codec.from_dict(data).to_dict()

    with open(outfile, "w") as f:
        json.dump(returned, f, indent=2)

    print(f"gwta: decoded + re-encoded {data['TypeName']} through the snapshot")
    return 0


if __name__ == "__main__":
    sys.exit(main())
