#!/usr/bin/env python3
"""c_hdr.py <game_id>: summarise the map text in a replay header (line types, TILE field value counts, DRAGON lines).
Used to learn whether the header carries the pearl spawn interval of each tile."""
import csv
import sys
from collections import Counter

import lib
from lib import rp

GAMES = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
gid = sys.argv[1]
root = rp.load(GAMES[gid]["replay_path"]).root()
text = root.text(0)
kinds = Counter()
tile_f2, tile_f3 = Counter(), Counter()
shown = Counter()
for line in text.splitlines():
    p = line.split()
    if not p:
        continue
    kinds[p[0]] += 1
    if p[0] == "TILE":
        if len(p) > 3:
            tile_f2[p[3]] += 1
        if len(p) > 4:
            tile_f3[p[4]] += 1
        if len(p) > 3 and (p[3] != "0" or (len(p) > 4 and p[4] != "0")) and shown["TILE"] < 15:
            shown["TILE"] += 1
            print("  ", line)
    elif shown[p[0]] < 6:
        shown[p[0]] += 1
        print("  ", line[:160])
print("line kinds:", dict(kinds))
print("TILE field 3 values:", sorted(tile_f2.items(), key=lambda kv: -kv[1])[:30])
print("TILE field 4 values:", sorted(tile_f3.items(), key=lambda kv: -kv[1])[:30])
