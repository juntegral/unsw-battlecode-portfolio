#!/usr/bin/env python3
"""c_tab.py [r1=0] [r2=149] game_id ...: one line per game and side from the c_out/ec_<id>_0_150.json files made by
c_econ.py, summed over the blocks r1..r2. Columns are explained in the header line that is printed."""
import glob
import json
import sys

args = sys.argv[1:]
r1, r2 = int(args[0]), int(args[1])
gids = args[2:]
if not gids:
    gids = sorted(p.split("ec_")[1].split("_")[0] for p in glob.glob("c_out/ec_*_0_150.json"))

print(f"rounds {r1}-{r2} | game map side team | units at r50 r100 r150 | nat = natural pearls eaten (hot = on fountain tiles in own half / in enemy half) | "
      "per100 = natural pearls per 100 dragon-turns | turns %: eat split die appr pass new old | pearl in view % | enemy head in view % | "
      "near6 = natural pearls that appeared within 6 steps of an own head: n -> own / enemy / left 20 rounds; unc = the uncontested ones: n -> own (mean wait) | dup = two own heads within 2 of an eaten pearl | "
      "rammed / rammer | boxed / free-cell non-ram deaths | splits | crowd = share of heads with an own head within 6 | adj = enemy head on next cell: n -> ram / away | "
      "sep = parent-child distance after 5 / 10 rounds | newshare = child / parent steps onto unvisited cells in 10 rounds after a split %")
for gid in gids:
    try:
        d = json.load(open(f"c_out/ec_{gid}_0_150.json"))
    except FileNotFoundError:
        print(gid, "missing")
        continue
    for s in "AB":
        t = {}
        crowd = []
        for r, row in d["blocks"].items():
            if r1 <= int(r) <= r2:
                for k, v in row[s].items():
                    if isinstance(v, (int, float)):
                        t[k] = t.get(k, 0) + v
                crowd.append(row[s]["crowd"])
        u = [d["blocks"].get(str(r), {}).get(s, {}).get("units", 0) for r in (50, 100, 150)]
        g = lambda k: t.get(k, 0)  # noqa: E731
        turns = max(1, g("turns"))
        tot = d["totals"][s]
        print(f"{gid} {d['map'][:9]:9s} {s} {d['names'][s][:9]:9s} | u {u[0]:2d} {u[1]:2d} {u[2]:2d} | nat {g('nat'):3d} (hot {g('nat_hot_own'):3d}/{g('nat_hot_enemy'):3d}) | "
              f"per100 {100 * g('nat') / turns:4.2f} | {100 * g('t_eat') / turns:2.0f} {100 * g('t_split') / turns:2.0f} {100 * g('t_die') / turns:2.0f} "
              f"{100 * g('t_approach') / turns:2.0f} {100 * g('t_pass') / turns:2.0f} {100 * g('t_new') / turns:2.0f} {100 * g('t_old') / turns:2.0f} | "
              f"pv {100 * g('turns_pearl_in_view') / turns:2.0f} ev {100 * g('t_enemy_in_view') / turns:2.0f} | "
              f"near6 {g('p_n'):3d} -> {g('p_own'):3d}/{g('p_enemy'):3d}/{g('p_left'):3d} unc {g('pu_n'):3d} -> {g('pu_own'):3d} ({g('pu_wait') / max(1, g('pu_own')):3.1f}) | dup {g('dup'):2d} | "
              f"ram {g('rammed'):2d}/{g('rammer'):2d} | box {g('boxed'):3d}/{g('freedeath'):2d} | sp {g('split'):3d} | crowd {sum(crowd) / max(1, len(crowd)):.2f} | "
              f"adj {g('adj'):2d} -> {g('adj_ram'):2d}/{g('adj_away'):2d} | sep {tot.get('sep5', 0):4.1f}/{tot.get('sep10', 0):4.1f} | newshare {100 * tot.get('child_new_share', 0):2.0f}/{100 * tot.get('parent_new_share', 0):2.0f}")
