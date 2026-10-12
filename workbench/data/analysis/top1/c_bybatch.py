#!/usr/bin/env python3
"""c_bybatch.py [size_or_map=large] [team_id=1119]: the team's games split by the run (battle id) they came from.

The battle id in games.csv is the only trace of which build of our bot played a game. The smoke-test runs are pairs of
the live bot ("-old") and a candidate ("-new"); data/online/smoke/<name>-bot/main.cpp holds the candidate's source.
tc30 = TRADE_CONTACT (a small dragon may ram a target of at least its own length instead of max(5, length + 2)),
qh31 = QH_SCOUT (queen hunt), stride = free sprint steps, passage2 = a passage rule, dl-* = ladder downloads.

For every run, games against 2000+ opponents on the given map size (or one map), means per game unless stated:
  games, wins | units at round 50 / 100 / 150 / 200 / 300 own : opponent | total length at round 150 / 300 own : opponent |
  natural pearls eaten in rounds 0-149 own : opponent | of them on fountains of the other half own : opponent |
  meetings in rounds 0-149 (own small dragon's turn begins with an enemy small head on the next cell) and share rammed |
  the same for the opponent | rams made : suffered in rounds 0-149 | pearls of ram corpses eaten in rounds 0-149 own : opponent |
  own heads in the own half % | moves of two or more steps in rounds 0-149 own : opponent | boxed deaths own : opponent
Sources: c_out/ec_<id>_0_150.json (c_econ.py) and q/<id>.json.
"""
import csv
import json
import os
import sys
from collections import defaultdict

want = sys.argv[1] if len(sys.argv) > 1 else "large"
team = int(sys.argv[2]) if len(sys.argv) > 2 else 1119
only_opp = None
if "--opp" in sys.argv:
    only_opp = {int(x) for x in sys.argv[sys.argv.index("--opp") + 1].split(",")}

groups = defaultdict(list)
first_time = {}
for g in csv.DictReader(open("games.csv")):
    if g["map"] == "Schooltime":
        continue
    size = "small" if g["map_size"].startswith("small") else "medium" if g["map_size"].startswith("medium") else "large"
    if want not in (size, g["map"], "all"):
        continue
    for s in "AB":
        if int(g[f"team{s}Id"]) != team:
            continue
        o = "B" if s == "A" else "A"
        try:
            if float(g[f"team{o}Elo"]) < 2000:
                continue
        except ValueError:
            continue
        if only_opp and int(g[f"team{o}Id"]) not in only_opp:
            continue
        p = f"c_out/ec_{g['game_id']}_0_150.json"
        if not os.path.exists(p):
            continue
        bid = g["battle_id"]
        groups[bid].append((g, s, o))
        first_time[bid] = min(first_time.get(bid, g["completed_at"]), g["completed_at"])


def summarise(rows):
    n = len(rows)
    acc = defaultdict(float)
    cnt = defaultdict(int)
    for g, s, o in rows:
        d = json.load(open(f"c_out/ec_{g['game_id']}_0_150.json"))
        q = json.load(open(f"q/{g['game_id']}.json"))
        acc["won"] += g["winner"] == s
        for side, tag in ((s, "own"), (o, "opp")):
            per = q["sides"][side]["per"]
            for r in (50, 100, 150, 200, 300):
                if r < len(per["units"]):
                    acc[f"u{r}_{tag}"] += per["units"][r]
                    cnt[f"u{r}_{tag}"] += 1
                if r < len(per["total"]):
                    acc[f"t{r}_{tag}"] += per["total"][r]
                    cnt[f"t{r}_{tag}"] += 1
            for r, row in d["blocks"].items():
                if int(r) >= 150:        # the JSON also holds a block for round 150 itself; keep rounds 0-149
                    continue
                b = row[side]
                for k in ("nat", "nat_hot_enemy", "adj", "adj_ram", "rammer", "rammed", "ramcorpse_own", "ramcorpse_enemy",
                          "heads_own_half", "heads_rounds", "multi", "boxed", "split", "freedeath", "paidsegs"):
                    acc[f"{k}_{tag}"] += b.get(k, 0)
    return n, acc, cnt


print(f"=== BY BATCH team {team}, {want}" + (f", opponents {sorted(only_opp)}" if only_opp else "") + " (Schooltime left out; means per game)")
print("run | games, wins | units r50 / r100 / r150 / r200 / r300 own : opp | total length r150 / r300 own : opp | natural pearls r0-149 own : opp | "
      "on fountains of the other half own : opp | own meetings r0-149, rammed % | opp meetings, rammed % | rams made : suffered r0-149 | "
      "ram-corpse pearls eaten r0-149 own : opp | own heads in own half % | moves of 2+ steps r0-149 own : opp | boxed deaths own : opp | splits own : opp")


def line(name, rows):
    n, a, c = summarise(rows)
    if not n:
        return

    def m(k):
        return a[k] / max(1, c[k])

    u = " / ".join(f"{m(f'u{r}_own'):4.1f}:{m(f'u{r}_opp'):4.1f}" for r in (50, 100, 150, 200, 300))
    t = " / ".join(f"{m(f't{r}_own'):5.1f}:{m(f't{r}_opp'):5.1f}" for r in (150, 300))
    print(f"{name:22s} | {n:3d}, {int(a['won']):2d} | {u} | {t} | {a['nat_own'] / n:5.1f}:{a['nat_opp'] / n:5.1f} | "
          f"{a['nat_hot_enemy_own'] / n:5.1f}:{a['nat_hot_enemy_opp'] / n:5.1f} | {a['adj_own'] / n:5.1f}, {100 * a['adj_ram_own'] / max(1, a['adj_own']):3.0f}% | "
          f"{a['adj_opp'] / n:5.1f}, {100 * a['adj_ram_opp'] / max(1, a['adj_opp']):3.0f}% | {a['rammer_own'] / n:4.1f}:{a['rammed_own'] / n:4.1f} | "
          f"{(a['ramcorpse_own_own'] + a['ramcorpse_enemy_own']) / n:5.1f}:{(a['ramcorpse_own_opp'] + a['ramcorpse_enemy_opp']) / n:5.1f} | "
          f"{100 * a['heads_own_half_own'] / max(1, a['heads_rounds_own']):3.0f}% | {a['multi_own'] / n:5.1f}:{a['multi_opp'] / n:5.1f} | "
          f"{a['boxed_own'] / n:5.1f}:{a['boxed_opp'] / n:5.1f} | {a['split_own'] / n:5.1f}:{a['split_opp'] / n:5.1f}")


for bid in sorted(groups, key=lambda b: first_time[b]):
    line(bid, groups[bid])
tc = [r for b in groups for r in groups[b] if b.startswith("tc30") and b.endswith("new")]
rest = [r for b in groups for r in groups[b] if not (b.startswith("tc30") and b.endswith("new"))]
smoke_rest = [r for b in groups for r in groups[b] if not b.startswith("dl-") and not (b.startswith("tc30") and b.endswith("new"))]
print()
line("TRADE_CONTACT runs", tc)
line("all other runs", rest)
line("other smoke runs", smoke_rest)
