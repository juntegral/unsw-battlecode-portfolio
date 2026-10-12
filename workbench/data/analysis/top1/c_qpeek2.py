#!/usr/bin/env python3
"""c_qpeek2.py <game_id>: top-level keys of q/<id>.json beyond the first 14, with a short sample of each."""
import json
import sys

d = json.load(open(f"q/{sys.argv[1]}.json"))
for k in list(d)[14:]:
    v = d[k]
    if isinstance(v, dict):
        print(k, "dict", list(v)[:10])
        for k2 in list(v)[:4]:
            print("   ", k2, json.dumps(v[k2])[:400])
    else:
        print(k, type(v).__name__, len(v) if hasattr(v, "__len__") else "", json.dumps(v)[:600])
print("sides keys:", list(d["sides"]["A"]))
