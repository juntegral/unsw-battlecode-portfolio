#!/usr/bin/env python3
"""b_feed.py: when does each top team start feeding its queen, over all games? (sub-session A2)

Uses timeline.csv (25-round buckets with queen_length and longest_length per team) and q/<id>.json (queen death
rounds). Games against teams rated 2000+, Schooltime left out, as in findings.md.
For each of Vibing++ (306), SSS (91), forgot (264):
  - games in which the own queen was alive at round 300
  - in those: the first bucket in which her length is 8 or more ("feeding has started"), split by whether the ENEMY
    queen was alive or dead at the start of that bucket; and how many were never fed although she lived to the end
  - the queen's mean length at rounds 300, 400, 450 and the end, by enemy-queen state at round 300
  - who is the longest dragon at round 400 when the own queen is alive: the queen or another dragon
"""
import csv
import json
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
games = {g["game_id"]: g for g in csv.DictReader(open(os.path.join(HERE, "games.csv")))}
tl = defaultdict(dict)
for row in csv.DictReader(open(os.path.join(HERE, "timeline.csv"))):
    tl[(row["game_id"], row["team_id"])][int(row["round_end"])] = row
TEAMS = {"306": "Vibing++", "91": "SSS", "264": "forgot"}

for tid, name in TEAMS.items():
    start = Counter()
    by300 = Counter()
    start_state = Counter()
    never = Counter()
    n300 = 0
    lens = defaultdict(list)
    lead400 = Counter()
    ex = defaultdict(list)
    for gid, g in games.items():
        if g["map"] == "Schooltime":
            continue
        side = "A" if g["teamAId"] == tid else "B" if g["teamBId"] == tid else None
        if side is None:
            continue
        op = "B" if side == "A" else "A"
        try:
            if float(g["team%sElo" % op]) < 2000:
                continue
        except ValueError:
            continue
        qp = os.path.join(HERE, "q", gid + ".json")
        if not os.path.exists(qp):
            continue
        q = json.load(open(qp))
        od = q["sides"][side].get("qdeath")
        ed = q["sides"][op].get("qdeath")
        own_death = od["round"] if od else 10 ** 6
        en_death = ed["round"] if ed else 10 ** 6
        rows = tl.get((gid, tid))
        if not rows or own_death < 300 or int(g["rounds"]) < 500:
            continue
        n300 += 1
        first = None
        for rend in sorted(rows):
            if rend <= 100:
                continue
            row = rows[rend]
            if row["queen_alive"] in ("1", "True", "true") and float(row["queen_length"] or 0) >= 8:
                first = rend
                break
        state300 = "enemy queen alive at r300" if en_death > 300 else "enemy queen dead by r300"
        for rend in (300, 400, 450, 500):
            row = rows.get(rend)
            if row and row["queen_alive"] in ("1", "True", "true"):
                lens[(state300, rend)].append(float(row["queen_length"]))
        row400 = rows.get(400)
        if row400 and row400["queen_alive"] in ("1", "True", "true"):
            lead400[(state300, "queen is the longest" if float(row400["queen_length"]) >= float(row400["longest_length"]) else "another dragon is longer")] += 1
        by300[(state300, "never" if first is None else "by r250" if first <= 250 else "r251-300" if first <= 300 else "r301-350" if first <= 350
               else "r351-425" if first <= 425 else "r426-500")] += 1
        if first is None:
            never[(state300, "alive at the end" if own_death > 10 ** 5 else "died after r300")] += 1
        else:
            st = "enemy queen alive" if en_death > first - 25 else "enemy queen dead"
            start[(st, first)] += 1
            start_state[st] += 1
            if len(ex[(st, first)]) < 4:
                ex[(st, first)].append(gid)
    print(f"=== {name} ({tid}): round-500 games with the own queen alive at r300: {n300}")
    for st in ("enemy queen alive", "enemy queen dead"):
        tot = start_state[st]
        print(f"  queen first 8+ long (bucket end round), {st} at that time: n={tot}: " + " ".join(f"r{r}:{start[(st, r)]}" for r in sorted(r for s2, r in start if s2 == st)))
    print("  never 8+ long:", dict(never))
    for st in ("enemy queen alive at r300", "enemy queen dead by r300"):
        print(f"  {st}: mean queen length (n) at r300 / r400 / r450 / r500: " + " / ".join(
            f"{sum(lens[(st, r)]) / len(lens[(st, r)]):.1f} ({len(lens[(st, r)])})" if lens[(st, r)] else "-" for r in (300, 400, 450, 500)))
    print("  at r400 with the own queen alive:", dict(lead400))
    for st in ("enemy queen alive at r300", "enemy queen dead by r300"):
        keys = ("by r250", "r251-300", "r301-350", "r351-425", "r426-500", "never")
        tot = sum(by300[(st, k)] for k in keys)
        print(f"  {st} ({tot} games): own queen first 8+ long: " + ", ".join(f"{k} {by300[(st, k)]}" for k in keys))
