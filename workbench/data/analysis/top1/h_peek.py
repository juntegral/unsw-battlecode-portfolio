#!/usr/bin/env python3
"""Peek at the structure of the per-game JSON files (q, q3v2, r3, d_out/cls, d_out/life, c_out)."""
import json, sys, os, glob

def show(o, depth=0, maxd=3, key=""):
    pad = "  " * depth
    if isinstance(o, dict):
        print(f"{pad}{key} dict[{len(o)}]")
        if depth >= maxd:
            print(pad + "  keys:", list(o.keys())[:30])
            return
        for k, v in list(o.items())[:40]:
            show(v, depth + 1, maxd, str(k))
    elif isinstance(o, list):
        print(f"{pad}{key} list[{len(o)}] first={json.dumps(o[:2])[:300]}")
    else:
        print(f"{pad}{key} = {json.dumps(o)[:200]}")

gid = sys.argv[1] if len(sys.argv) > 1 else "1053784"
for d in ("q", "q3v2", "r3", "d_out/cls", "d_out/life"):
    p = f"{d}/{gid}.json"
    print("=====", p, os.path.exists(p))
    if os.path.exists(p):
        show(json.load(open(p)), maxd=int(sys.argv[2]) if len(sys.argv) > 2 else 3)
