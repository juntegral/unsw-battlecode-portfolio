#!/usr/bin/env python3
"""d_conn.py: are the two queens' start cells connected on each map, with and without portals? (sub-session A4)

For one game per map: the size of the region reachable from queen A's start cell (kelp respected, portals used),
whether queen B's start cell is in it and at what path distance, and the same with portal edges treated as closed.
"""
import csv
from collections import deque

import lib

seen = set()
for g in csv.DictReader(open("games.csv")):
    if g["map"] in seen:
        continue
    seen.add(g["map"])
    w = lib.Walk(g["replay_path"])
    b = w.board
    sa, sb = b.starts[b.queen["A"]], b.starts[b.queen["B"]]

    def region(use_portals):
        dist = {sa: 0}
        q = deque([sa])
        while q:
            c = q.popleft()
            for d in range(4):
                n = b.step(c, d)
                if n is None or n in dist:
                    continue
                if not use_portals:
                    x, y = c
                    key = (x, y, "N") if d == 0 else (x, (y + 1) % b.h, "N") if d == 2 else (x, y, "W") if d == 3 else ((x + 1) % b.w, y, "W")
                    if key in b.portal_pair:
                        continue
                dist[n] = dist[c] + 1
                q.append(n)
        return dist

    with_p, without_p = region(True), region(False)
    print(f"{g['map']:18s} {b.w}x{b.h} cells {b.w * b.h:4d} portals {len(b.portal_pair) // 2:3d} | with portals: region {len(with_p):4d}, enemy start at {with_p.get(sb, 'not reachable')} | "
          f"without portals: region {len(without_p):4d}, enemy start at {without_p.get(sb, 'not reachable')}")
