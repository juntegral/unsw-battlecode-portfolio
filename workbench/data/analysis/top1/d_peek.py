#!/usr/bin/env python3
"""d_peek.py <path to a json under d_out> [key.path ...]: print a stored record compactly (sub-session A4, helper)."""
import json
import sys

d = json.load(open(sys.argv[1]))
for path in sys.argv[2:] or [""]:
    x = d
    for k in [p for p in path.split(".") if p]:
        x = x[int(k)] if isinstance(x, list) else x[k]
    s = json.dumps(x)
    print(path or "(all)", ":", s[:3000])
