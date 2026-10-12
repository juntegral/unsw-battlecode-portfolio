#!/usr/bin/env python3
"""Per run of ours: how many of our sonar pings read as a plain leader message (see e_belief.py).
A run whose pings do not read is a build that seals its sonar; for those games the belief columns are empty.
Reads e_out/w3. Output: stdout."""
import json
import os
from collections import defaultdict

import e_lib as E

W = os.path.join(E.HERE, "e_out", "w4")
agg = defaultdict(lambda: [0, 0, 0, 0])
for f in os.listdir(W):
    if not f.endswith(".json"):
        continue
    try:
        d = json.load(open(os.path.join(W, f)))
    except Exception:  # noqa: BLE001
        continue
    if not d["me"]:
        continue
    a = agg[d["set"]]
    a[0] += 1
    a[1] += d["nping"]
    a[2] += d["badping"]
    a[3] += 1 if d["nping"] and d["badping"] / d["nping"] < 0.05 else 0
for k, a in sorted(agg.items()):
    print("%-22s games %3d | pings read as leader messages %9d | of them implausible %9d (%.0f%%) | games with readable pings %d" % (
        k, a[0], a[1], a[2], 100.0 * a[2] / max(1, a[1]), a[3]))
