#!/usr/bin/env python3
"""c_qpeek.py <game_id>: show the structure of q/<id>.json (keys, types, first items)."""
import json
import sys

d = json.load(open(f"q/{sys.argv[1]}.json"))


def show(x, ind=0, key=""):
    pad = "  " * ind
    if isinstance(x, dict):
        print(f"{pad}{key}: dict({len(x)}) keys={list(x)[:14]}")
        for k in list(x)[:14]:
            show(x[k], ind + 1, str(k))
    elif isinstance(x, list):
        print(f"{pad}{key}: list({len(x)}) first={json.dumps(x[:3])[:220]}")
    else:
        print(f"{pad}{key}: {json.dumps(x)[:120]}")


show(d)
