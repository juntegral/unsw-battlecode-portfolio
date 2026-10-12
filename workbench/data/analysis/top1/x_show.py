#!/usr/bin/env python3
"""Print one of my per-game JSON files in a compact way: python3 x_show.py <dir> <gid> [key]"""
import json, sys
d = json.load(open('x_out/%s/%s.json' % (sys.argv[1], sys.argv[2])))
if len(sys.argv) > 3:
    v = d[sys.argv[3]]
    if isinstance(v, list):
        for x in v[:int(sys.argv[4]) if len(sys.argv) > 4 else 40]: print(x)
    else:
        print(json.dumps(v, indent=1)[:4000])
else:
    for k, v in d.items():
        s = json.dumps(v)
        print(k, ':', s[:300], '...' if len(s) > 300 else '')
