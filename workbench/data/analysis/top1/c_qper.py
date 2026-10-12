#!/usr/bin/env python3
"""c_qper.py <game_id> [step=25]: units / total length / longest per side every <step> rounds from q/<id>.json,
plus the structure of the 'per' and 'flow' entries (first call only prints a sample)."""
import json
import sys

gid = sys.argv[1]
step = int(sys.argv[2]) if len(sys.argv) > 2 else 25
d = json.load(open(f"q/{gid}.json"))
A, B = d["sides"]["A"], d["sides"]["B"]
per = A["per"]
if isinstance(per, dict):
    print("per keys:", list(per)[:12])
    for k in list(per)[:6]:
        print("  ", k, json.dumps(per[k])[:200])
else:
    print("per list", len(per), json.dumps(per[:2])[:300])
print("flow:", json.dumps(A["flow"])[:300])
