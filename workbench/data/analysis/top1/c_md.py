#!/usr/bin/env python3
"""c_md.py <game_id> [step=10] [r1=0] [r2=149]: a compact markdown table for one game from the c_econ.py JSON files
(c_out/ec_<id>_0_150.json and, for rounds from 150, c_out/ec_<id>_150_350.json). One row per <step> rounds, each
cell "side A / side B". Columns: units and total length at the start of the row; natural pearls eaten; corpse pearls
eaten; new dragons (splits); dragons lost: rammed by the enemy, ramming, boxed (non-ram, no free cell), other non-ram;
squares of the 8x8 board grid with an own head; share of heads in the own half; natural pearls eaten on fountains of
the enemy half; own-half fountain tile-rounds with a pearl lying on them (%)."""
import json
import os
import sys

gid = sys.argv[1]
step = int(sys.argv[2]) if len(sys.argv) > 2 else 10
r1 = int(sys.argv[3]) if len(sys.argv) > 3 else 0
r2 = int(sys.argv[4]) if len(sys.argv) > 4 else 149
blocks = {}
names = mp = None
for path, lo, hi in ((f"c_out/ec_{gid}_0_150.json", 0, 149), (f"c_out/ec_{gid}_150_350.json", 150, 349)):
    if os.path.exists(path):
        d = json.load(open(path))
        names, mp = d["names"], d["map"]
        for r, row in d["blocks"].items():
            if lo <= int(r) <= hi:
                blocks[int(r)] = row
print(f"Game {gid}, {mp}: A = {names['A']}, B = {names['B']}. Each cell is A / B.")
print()
print("| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | boxed | other non-ram | squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for a in range(r1, r2 + 1, step):
    rs = [r for r in range(a, a + step, 10) if r in blocks]
    if not rs:
        continue
    cells = []

    def tot(s, k):
        return sum(blocks[r][s].get(k, 0) for r in rs)

    first = blocks[rs[0]]
    cells.append(f"{first['A']['units']} / {first['B']['units']}")
    cells.append(f"{first['A']['total']} / {first['B']['total']}")
    cells.append(f"{tot('A', 'nat')} / {tot('B', 'nat')}")
    cells.append(f"{tot('A', 'corpse_own') + tot('A', 'corpse_enemy')} / {tot('B', 'corpse_own') + tot('B', 'corpse_enemy')}")
    cells.append(f"{tot('A', 'split')} / {tot('B', 'split')}")
    cells.append(f"{tot('A', 'rammed')} / {tot('B', 'rammed')}")
    cells.append(f"{tot('A', 'rammer')} / {tot('B', 'rammer')}")
    cells.append(f"{tot('A', 'boxed')} / {tot('B', 'boxed')}")
    cells.append(f"{tot('A', 'freedeath')} / {tot('B', 'freedeath')}")
    cells.append(f"{first['A']['squares']} / {first['B']['squares']}")
    home = []
    lying = []
    for s in "AB":
        hr = max(1, tot(s, "heads_rounds"))
        home.append(f"{100 * tot(s, 'heads_own_half') / hr:.0f}")
        tr = max(1, tot(s, "hot_lying") + tot(s, "hot_body") + tot(s, "hot_empty"))
        lying.append(f"{100 * tot(s, 'hot_lying') / tr:.0f}")
    cells.append(" / ".join(home))
    cells.append(f"{tot('A', 'nat_hot_enemy')} / {tot('B', 'nat_hot_enemy')}")
    cells.append(" / ".join(lying))
    print(f"| {a}-{a + step - 1} | " + " | ".join(cells) + " |")
