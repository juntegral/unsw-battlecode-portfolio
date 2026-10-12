#!/usr/bin/env python3
"""c_pairs.py: the trade-on-contact test on the ladder, game by game on the large maps (markdown table).

Run tc30-test-new (candidate with TRADE_CONTACT) and run qh31-test-old (the live bot, 80 minutes earlier) each played
test4 and WeHaveQuizzes once per large map from side A. For every such game: units at round 100 / 150 / 300 own : opponent,
total length at round 150 / 300 own : opponent (q/<id>.json), natural pearls eaten in rounds 0-149 own : opponent,
rams made : suffered in rounds 0-149, how many of the meetings in rounds 0-149 (own small dragon's turn begins with an
enemy small head on the next cell) ended in a ram (c_out/ec_<id>_0_150.json), and the result.
Output: c_out/pairs_large.md.
"""
import csv
import json

RUNS = {"qh31-test-old": "live", "tc30-test-new": "test build"}
OPP = {19: "test4", 87: "WHQ"}
rows = []
for g in csv.DictReader(open("games.csv")):
    if g["battle_id"] not in RUNS or int(g["cells"]) <= 1200 or g["map"] == "Schooltime":
        continue
    if int(g["teamAId"]) != 1119 or int(g["teamBId"]) not in OPP:
        continue
    q = json.load(open(f"q/{g['game_id']}.json"))
    d = json.load(open(f"c_out/ec_{g['game_id']}_0_150.json"))
    ua, ub = q["sides"]["A"]["per"]["units"], q["sides"]["B"]["per"]["units"]
    ta, tb = q["sides"]["A"]["per"]["total"], q["sides"]["B"]["per"]["total"]

    def at(v, r):
        return str(v[r]) if r < len(v) else "-"

    def tot(side, k):
        # the JSON also holds a block for round 150 itself; keep rounds 0-149
        return sum(row[side].get(k, 0) for r, row in d["blocks"].items() if int(r) < 150)

    rows.append((g["map"], OPP[int(g["teamBId"])], RUNS[g["battle_id"]] != "live", g["game_id"], RUNS[g["battle_id"]],
                 " / ".join(f"{at(ua, r)}:{at(ub, r)}" for r in (100, 150, 300)),
                 " / ".join(f"{at(ta, r)}:{at(tb, r)}" for r in (150, 300)),
                 f"{tot('A', 'nat')}:{tot('B', 'nat')}", f"{tot('A', 'rammer')}:{tot('A', 'rammed')}",
                 f"{tot('A', 'adj_ram')} of {tot('A', 'adj')}",
                 ("win" if g["winner"] == "A" else "loss") + ", " + g["end_type"] + (f" r{g['rounds']}" if g["rounds"] != "500" else "")))
out = ["| map | opponent | game | bot | units r100 / r150 / r300, own:opp | total length r150 / r300, own:opp | natural pearls r0-149, own:opp | rams made:suffered r0-149 | meetings rammed r0-149 | result |",
       "|---|---|---|---|---|---|---|---|---|---|"]
for r in sorted(rows):
    out.append(f"| {r[0]} | {r[1]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]} | {r[8]} | {r[9]} | {r[10]} |")
open("c_out/pairs_large.md", "w").write("\n".join(out) + "\n")
print("\n".join(out))
