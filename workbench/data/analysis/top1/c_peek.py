#!/usr/bin/env python3
"""c_peek.py <game_id> [max_round=3]: dump raw event kinds of a replay (counts per kind per round, and the first few
events of the kinds lib.py does not use: pearlCountdown (2), engineLog (5), dragonLog (6), dragonIndicator (7),
debugDraw (8)). Read-only; used once to learn whether the replay shows pearl timers.
"""
import csv
import sys
import time
from collections import Counter

import lib
from lib import rp

GAMES = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
gid = sys.argv[1]
maxr = int(sys.argv[2]) if len(sys.argv) > 2 else 3
t0 = time.time()
root = rp.load(GAMES[gid]["replay_path"]).root()
print("header text:")
print("\n".join(root.text(0).splitlines()[:6]))
cnt = Counter()
shown = Counter()
rnd = -1
for event in root.pointer(3):
    kind = event.u16(0)
    p = event.pointer(0)
    if kind == 0:
        rnd = p.i32(0)
    cnt[(rnd if rnd <= maxr else "later", rp.EVENT_NAMES[kind] if kind < len(rp.EVENT_NAMES) else kind)] += 1
    if kind in (2, 5, 6, 7, 8) and shown[kind] < 12:
        shown[kind] += 1
        fields = []
        if p is not None:
            fields.append(f"dwords={p.dwords} pwords={p.pwords}")
            for off in range(0, p.dwords * 8, 4):
                fields.append(f"i32@{off}={p.i32(off)}")
            for k in range(p.pwords):
                q = p.pointer(k)
                try:
                    fields.append(f"ptr{k}=point{rp.point(q)}")
                except Exception as e:  # noqa: BLE001
                    fields.append(f"ptr{k}=?({type(q).__name__})")
        print(f"round {rnd} kind {kind} {rp.EVENT_NAMES[kind]}: " + " ".join(fields))
    if kind == 3 and rnd <= 1 and shown[3] < 12:
        shown[3] += 1
        print(f"round {rnd} tileChange cell={rp.point(p.pointer(0))} bit0={p.bit(0)} dwords={p.dwords} raw i32@0={p.i32(0)}")
for k in sorted(cnt, key=str):
    print(k, cnt[k])
print("seconds to scan:", round(time.time() - t0, 2))
