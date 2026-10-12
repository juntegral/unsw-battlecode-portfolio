#!/usr/bin/env python3
"""c_build.py: assemble deep-read-3.md from the part files c_p_*.md (in the order listed below).

A line of the form  <<TABLE game_id step r1 r2>>  in a part file is replaced by a compact markdown table for that game
built from the c_econ.py JSON files (same numbers as c_md.py prints). A line  <<FILE path first last>>  is replaced by
the lines first..last of a text file (1-based), indented as a code block.
"""
import json
import os

PARTS = ["c_p_head.md", "c_p_games.md", "c_p_maps.md", "c_p_maps2.md", "c_p_answers.md", "c_p_table.md", "c_p_change.md", "c_p_wrong.md", "c_p_unknown.md"]


def table(gid, step, r1, r2):
    blocks = {}
    names = mp = None
    for path, lo, hi in ((f"c_out/ec_{gid}_0_150.json", 0, 149), (f"c_out/ec_{gid}_150_350.json", 150, 349)):
        if os.path.exists(path):
            d = json.load(open(path))
            names, mp = d["names"], d["map"]
            for r, row in d["blocks"].items():
                if lo <= int(r) <= hi:
                    blocks[int(r)] = row
    out = [f"Game {gid}, {mp}: A = {names['A']}, B = {names['B']}. Every cell is A / B.", "",
           "| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for a in range(r1, r2 + 1, step):
        rs = [r for r in range(a, a + step, 10) if r in blocks]
        if not rs:
            continue

        def tot(s, k):
            return sum(blocks[r][s].get(k, 0) for r in rs)

        first = blocks[rs[0]]
        cells = [f"{first['A']['units']} / {first['B']['units']}", f"{first['A']['total']} / {first['B']['total']}",
                 f"{tot('A', 'nat')} / {tot('B', 'nat')}",
                 f"{tot('A', 'corpse_own') + tot('A', 'corpse_enemy')} / {tot('B', 'corpse_own') + tot('B', 'corpse_enemy')}",
                 f"{tot('A', 'split')} / {tot('B', 'split')}", f"{tot('A', 'rammed')} / {tot('B', 'rammed')}",
                 f"{tot('A', 'rammer')} / {tot('B', 'rammer')}", f"{tot('A', 'ram_friend')} / {tot('B', 'ram_friend')}",
                 f"{tot('A', 'boxed')} / {tot('B', 'boxed')}",
                 f"{tot('A', 'freedeath')} / {tot('B', 'freedeath')}", f"{first['A']['squares']} / {first['B']['squares']}"]
        home, lying = [], []
        for s in "AB":
            hr = max(1, tot(s, "heads_rounds"))
            home.append(f"{100 * tot(s, 'heads_own_half') / hr:.0f}")
            tr = max(1, tot(s, "hot_lying") + tot(s, "hot_body") + tot(s, "hot_empty"))
            lying.append(f"{100 * tot(s, 'hot_lying') / tr:.0f}")
        cells.append(" / ".join(home))
        cells.append(f"{tot('A', 'nat_hot_enemy')} / {tot('B', 'nat_hot_enemy')}")
        cells.append(" / ".join(lying))
        out.append(f"| {a}-{a + step - 1} | " + " | ".join(cells) + " |")
    return out


def build():
    lines = []
    for part in PARTS:
        if not os.path.exists(part):
            continue
        for line in open(part).read().splitlines():
            if line.startswith("<<TABLE "):
                p = line.strip("<>").split()
                lines.extend(table(p[1], int(p[2]), int(p[3]), int(p[4])))
            elif line.startswith("<<RAW "):
                p = line.strip("<>").split()
                path, a, b = " ".join(p[1:-2]), int(p[-2]), int(p[-1])
                lines.extend(open(path).read().splitlines()[a - 1:b])
            elif line.startswith("<<FILE "):
                p = line.strip("<>").split()
                path, a, b = " ".join(p[1:-2]), int(p[-2]), int(p[-1])
                src = open(path).read().splitlines()
                lines.append("```")
                lines.extend(src[a - 1:b])
                lines.append("```")
            else:
                lines.append(line)
        lines.append("")
    open("deep-read-3.md", "w").write("\n".join(lines) + "\n")
    print("deep-read-3.md written:", len(lines), "lines from", sum(1 for p in PARTS if os.path.exists(p)), "parts")


if __name__ == "__main__":
    build()
