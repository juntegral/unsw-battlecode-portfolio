#!/usr/bin/env python3
"""c_ledger.py game_id ...: length ledger per 50 rounds for both sides, from the c_econ.py JSON files
(c_out/ec_<id>_0_150.json for rounds 0-149 and c_out/ec_<id>_150_350.json for rounds 150-349 if present).

Total length changes only by: + natural pearls eaten, + corpse pearls eaten (own corpses, enemy corpses),
- segments of dragons that die (rammed by an enemy, ramming an enemy, ram between team-mates, non-ram with no free
cell = boxed, non-ram with a free cell), - segments paid for extra steps. The 'check' column is the change in total
length that these add up to, next to the real change, so the ledger can be trusted.
"""
import json
import os
import sys

PERIODS = [(0, 49), (50, 99), (100, 149), (150, 199), (200, 249), (250, 299), (300, 349)]
KEYS = ("nat", "corpse_own", "corpse_enemy", "rammed_seg", "rammer_seg", "ram_friend_seg", "boxed_seg", "freedeath_seg", "paidsegs",
        "split", "rammed", "rammer", "ram_friend", "boxed", "freedeath", "turns", "nat_hot_own", "nat_hot_enemy")


def load(gid):
    blocks = {}
    names = None
    mp = None
    p1 = f"c_out/ec_{gid}_0_150.json"
    p2 = f"c_out/ec_{gid}_150_350.json"
    if os.path.exists(p1):
        d = json.load(open(p1))
        names, mp = d["names"], d["map"]
        for r, row in d["blocks"].items():
            if int(r) < 150:
                blocks[int(r)] = row
    if os.path.exists(p2):
        d = json.load(open(p2))
        names, mp = d["names"], d["map"]
        for r, row in d["blocks"].items():
            if 150 <= int(r):
                blocks[int(r)] = row
    return names, mp, blocks


print("game map side team period | units start>end | total start>end (real change / ledger) | + natural (of which on fountains in own half / enemy half) "
      "+ own corpses + enemy corpses | - rammed - rammer - team-mate ram - boxed - free-cell deaths - paid steps (segments) | "
      "dragons: +splits -rammed -rammer -boxed -free | natural pearls per 100 dragon-turns")
for gid in sys.argv[1:]:
    names, mp, blocks = load(gid)
    if not blocks:
        print(gid, "missing")
        continue
    for s in "AB":
        for a, b in PERIODS:
            rs = [r for r in range(a // 10 * 10, b + 1, 10)]
            if a not in blocks or (b + 1) not in blocks:
                continue
            t = {k: 0 for k in KEYS}
            for r in rs:
                for k in KEYS:
                    t[k] += blocks[r][s].get(k, 0)
            u0, u1 = blocks[a][s]["units"], blocks[b + 1][s]["units"]
            l0, l1 = blocks[a][s]["total"], blocks[b + 1][s]["total"]
            led = (t["nat"] + t["corpse_own"] + t["corpse_enemy"] - t["rammed_seg"] - t["rammer_seg"] - t["ram_friend_seg"]
                   - t["boxed_seg"] - t["freedeath_seg"] - t["paidsegs"])
            print(f"{gid} {mp[:9]:9s} {s} {names[s][:9]:9s} r{a:3d}-{b:3d} | u {u0:2d}>{u1:2d} | t {l0:3d}>{l1:3d} ({l1 - l0:+4d} / {led:+4d}) | "
                  f"+{t['nat']:3d} ({t['nat_hot_own']:3d}/{t['nat_hot_enemy']:3d}) +{t['corpse_own']:3d} +{t['corpse_enemy']:3d} | "
                  f"-{t['rammed_seg']:3d} -{t['rammer_seg']:3d} -{t['ram_friend_seg']:2d} -{t['boxed_seg']:3d} -{t['freedeath_seg']:3d} -{t['paidsegs']:3d} | "
                  f"+{t['split']:3d} -{t['rammed']:2d} -{t['rammer']:2d} -{t['boxed']:3d} -{t['freedeath']:2d} | {100 * t['nat'] / max(1, t['turns']):4.2f}")
        print()
