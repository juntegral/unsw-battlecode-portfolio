#!/usr/bin/env python3
"""c_agg.py <size|map name> [r1=0] [r2=149]: all-games table of the c_econ.py numbers (c_out/ec_<id>_0_150.json),
means per game over the blocks r1..r2, one column per group:
  meow | test4 v meow | WHQ v meow | test4 v top3 | WHQ v top3 | forgot | SSS | Vibing++
(the four named teams: all their games against 2000+ opponents, Schooltime left out; test4 = team 19, WHQ =
WeHaveQuizzes = team 87, counted in their games against us and in their games against the top three).
The first argument is a map size (large, medium, small) or a map name (e.g. "Around UNSW").

Rounds: the c_econ.py rows are snapshots at the start of each 10-round block. Rows labelled "at round N (last snapshot)"
or "by round N" are therefore the state at round r2 - 9 (140 for rounds 0-149). Units and total length at round r2 + 1
(50, 100, 150) come from q/<id>.json and are means over the games that reached that round.
"""
import csv
import json
import os
import sys
from collections import defaultdict

want = sys.argv[1]
r1 = int(sys.argv[2]) if len(sys.argv) > 2 else 0
r2 = int(sys.argv[3]) if len(sys.argv) > 3 else 149
SNAP = r2 // 10 * 10          # round of the last 10-round snapshot inside r1..r2
END = SNAP + 10               # first round after the range
TOP = {306: "Vibing++", 91: "SSS", 264: "forgot", 1119: "meow"}
COLS = ["meow", "test4 v meow", "WHQ v meow", "test4 v top3", "WHQ v top3", "forgot", "SSS", "Vibing++"]
acc = defaultdict(lambda: defaultdict(list))
ng = defaultdict(int)


def add(col, row):
    for k, v in row.items():
        acc[col][k].append(v)
    ng[col] += 1


for g in csv.DictReader(open("games.csv")):
    if g["map"] == "Schooltime":
        continue
    size = "small" if g["map_size"].startswith("small") else "medium" if g["map_size"].startswith("medium") else "large"
    if want not in (size, g["map"]):
        continue
    path = f"c_out/ec_{g['game_id']}_0_150.json"
    if not os.path.exists(path):
        continue
    d = None
    q = None
    for s in "AB":
        o = "B" if s == "A" else "A"
        t, ot = int(g[f"team{s}Id"]), int(g[f"team{o}Id"])
        try:
            oelo = float(g[f"team{o}Elo"])
        except ValueError:
            oelo = 0
        cols = []
        if t in TOP and oelo >= 2000:
            cols.append(TOP[t])
        if t in (19, 87):
            nm = "test4" if t == 19 else "WHQ"
            if ot == 1119:
                cols.append(nm + " v meow")
            elif ot in (306, 91, 264):
                cols.append(nm + " v top3")
        if not cols:
            continue
        if d is None:
            d = json.load(open(path))
        tsum = defaultdict(float)
        first = last = None
        nb = 0
        for r, row in d["blocks"].items():
            r = int(r)
            if r1 <= r <= r2:
                nb += 1
                for k, v in row[s].items():
                    if isinstance(v, (int, float)):
                        tsum[k] += v
                if first is None or r < first[0]:
                    first = (r, row[s])
                if last is None or r > last[0]:
                    last = (r, row[s])
        if not nb:
            continue
        x = lambda k: tsum.get(k, 0)  # noqa: E731
        turns = max(1.0, x("turns"))
        view = max(1.0, x("turns_pearl_in_view"))
        # The c_econ.py rows are snapshots at the START of each 10-round block, so the last row of rounds r1..r2 is the
        # state at round SNAP = r2 - 9 (140 for 0-149), not at round r2 + 1. Units and total length at round END = r2 + 1
        # are taken from q/<id>.json (per-round values) for the games that reached that round.
        if q is None:
            q = json.load(open(f"q/{g['game_id']}.json"))
        per = q["sides"][s]["per"]
        row = {
            "units at start": first[1]["units"], f"units at round {SNAP} (last snapshot)": last[1]["units"],
            f"total length at round {SNAP} (last snapshot)": last[1]["total"],
            "natural pearls eaten": x("nat"),
            "  on own-half fountains": x("nat_hot_own"), "  on enemy-half fountains": x("nat_hot_enemy"),
            "  on other tiles": x("nat") - x("nat_hot"),
            "corpse pearls eaten, own corpses": x("corpse_own"), "corpse pearls eaten, enemy corpses": x("corpse_enemy"),
            "dragon-turns": x("turns"),
            "natural pearls per 100 dragon-turns": 100 * x("nat") / turns,
            "turns %: eat": 100 * x("t_eat") / turns, "turns %: split": 100 * x("t_split") / turns, "turns %: die": 100 * x("t_die") / turns,
            "turns %: approach (pearl in view, ended nearer)": 100 * x("t_approach") / turns,
            "turns %: pass (pearl in view, not nearer)": 100 * x("t_pass") / turns,
            "turns %: no pearl in view, new cell": 100 * x("t_new") / turns,
            "turns %: no pearl in view, visited cell": 100 * x("t_old") / turns,
            "turns with a pearl in view %": 100 * x("turns_pearl_in_view") / turns,
            "turns with an enemy head in view %": 100 * x("t_enemy_in_view") / turns,
            "new dragons (splits)": x("split"),
            "dragons rammed by the enemy": x("rammed"), "dragons that rammed an enemy": x("rammer"),
            "non-ram deaths, no free cell (boxed)": x("boxed"), "non-ram deaths with a free cell": x("freedeath"),
            "segments lost: rammed": x("rammed_seg"), "segments lost: rammer": x("rammer_seg"),
            "segments lost: boxed": x("boxed_seg"), "segments lost: free-cell deaths": x("freedeath_seg"),
            "segments paid for steps": x("paidsegs"), "moves of 2+ steps": x("multi"),
            "pearls appearing within 6 steps of an own head": x("p_n"),
            "  eaten by own team within 20 rounds %": 100 * x("p_own") / max(1, x("p_n")),
            "  eaten by the enemy %": 100 * x("p_enemy") / max(1, x("p_n")),
            "  left for 20 rounds %": 100 * x("p_left") / max(1, x("p_n")),
            "  uncontested ones: mean rounds until eaten": x("pu_wait") / max(1, x("pu_own")),
            "eats with a second own head within 2 steps": x("dup"),
            f"squares (of 64) with an own head, at round {SNAP}": last[1]["squares"],
            f"cells visited by round {SNAP}": last[1]["visited"],
            f"mean distance of heads from own spawn, at round {SNAP}": last[1]["dmean"],
            "share of heads with an own head within 6 steps": tsum.get("crowd", 0) / nb,
            "own heads on tight cells (mean)": tsum.get("tight", 0) / nb,
            f"dragons not eaten for 20 rounds, at round {SNAP}": last[1]["hungry"],
            "own heads in own half %": 100 * x("heads_own_half") / max(1, x("heads_rounds")),
            "own heads within 3 steps of a fountain %": 100 * x("heads_at_hot") / max(1, x("heads_rounds")),
            "own-half fountains: pearl lying %": 100 * x("hot_lying") / max(1, x("hot_lying") + x("hot_body") + x("hot_empty")),
            "own-half fountains: body on it %": 100 * x("hot_body") / max(1, x("hot_lying") + x("hot_body") + x("hot_empty")),
            f"own-half fountains eaten from by round {SNAP} (of n)": last[1].get("hot_eaten", 0),
            "own-half fountains (n)": last[1].get("hot_own", 0),
            f"own-half fountains the enemy has seen by round {SNAP}": last[1].get("hot_seen_by_enemy", 0),
        }
        if END < len(per["units"]):
            row[f"units at round {END} (games that reached it)"] = per["units"][END]
            row[f"total length at round {END} (games that reached it)"] = per["total"][END]
        for rv in ("free", "mate", "enemy"):
            a, p = x(f"t_approach_{rv}"), x(f"t_pass_{rv}")
            e, sp, di = x(f"t_eat_view_{rv}"), x(f"t_split_view_{rv}"), x(f"t_die_view_{rv}")
            n = a + p + e + sp + di
            label = {"free": "nobody else as near", "mate": "an own head is nearer", "enemy": "an enemy head is as near or nearer"}[rv]
            row[f"pearl in view, {label}: turns"] = n
            row[f"  ate or ended nearer %"] = 0  # placeholder to keep order (overwritten below)
            row[f"  [{rv}] ate or ended nearer %"] = 100 * (a + e) / max(1, n)
            row[f"  [{rv}] did not get nearer %"] = 100 * p / max(1, n)
            row[f"  [{rv}] split or died %"] = 100 * (sp + di) / max(1, n)
        del row["  ate or ended nearer %"]
        ev = x("ev_farther") + x("ev_nearer") + x("ev_same") + x("ev_rammed_it") + x("ev_died")
        row["enemy head in view at turn start: turns"] = ev
        row["  ended farther from it %"] = 100 * x("ev_farther") / max(1, ev)
        row["  ended nearer to it %"] = 100 * x("ev_nearer") / max(1, ev)
        row["  rammed an enemy that turn %"] = 100 * x("ev_rammed_it") / max(1, ev)
        row["enemy head on a neighbouring cell at turn start"] = x("adj")
        row["  rammed it %"] = 100 * x("adj_ram") / max(1, x("adj"))
        row["  stepped away %"] = 100 * x("adj_away") / max(1, x("adj"))
        row["  stepped away, rammed within 2 rounds (n)"] = x("adj_then_rammed")
        tot = d["totals"][s]
        if r1 == 0 and r2 >= 140:
            row["parent-child distance 5 rounds after a split"] = tot.get("sep5", 0)
            row["parent-child distance 10 rounds after a split"] = tot.get("sep10", 0)
            row["child's steps onto unvisited cells in 10 rounds %"] = 100 * tot.get("child_new_share", 0)
            row["parent's steps onto unvisited cells in 10 rounds %"] = 100 * tot.get("parent_new_share", 0)
        for c in cols:
            add(c, row)

print(f"=== AGG {want}, rounds {r1}-{r2 + 9 if r2 % 10 == 0 else r2}: means per game. Games: " + ", ".join(f"{c} {ng[c]}" for c in COLS))
print(f"{'':62s} | " + " | ".join(f"{c:>12s}" for c in COLS))
keys = []
for c in COLS:
    for k in acc[c]:
        if k not in keys:
            keys.append(k)
for k in keys:
    cells = []
    for c in COLS:
        v = acc[c].get(k)
        if not v:
            cells.append(f"{'-':>12s}")
        else:
            m = sum(v) / len(v)
            cells.append(f"{m:12.1f}" if abs(m) >= 10 else f"{m:12.2f}")
    print(f"{k:62s} | " + " | ".join(cells))
