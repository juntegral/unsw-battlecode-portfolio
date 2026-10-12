#!/usr/bin/env python3
"""b_qsplit.py: what kind of splits do the three top teams' queens make, over all games? (sub-session A2)

Uses q/<id>.json (qsplits = [round, length before, parent keeps, child gets] for every split of each queen; qdeath).
Games against 2000+ teams, Schooltime left out. Per team (306 Vibing++, 91 SSS, 264 forgot):
  - splits by kind: "4 -> 2+2" (mother), "shed 2" (queen 5+ long, child = 2), "cut" (queen 6+ long keeps 2 or 3),
    other
  - "shed runs": runs of shed-2 splits in consecutive rounds after round 20 (a queen that stands still for several
    rounds): number of runs of 3+ rounds, games with one, total segments shed, the longest, and how the game ended
  - "cuts" after round 20 from 8+ long: number, games, mean length before and after
  - queen deaths by reason
"""
import csv
import json
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
games = {g["game_id"]: g for g in csv.DictReader(open(os.path.join(HERE, "games.csv")))}
TEAMS = {"306": "Vibing++", "91": "SSS", "264": "forgot"}
for tid, name in TEAMS.items():
    kinds = Counter()
    runs = []
    cuts = []
    deaths = Counter()
    n = 0
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
        p = os.path.join(HERE, "q", gid + ".json")
        if not os.path.exists(p):
            continue
        q = json.load(open(p))
        n += 1
        sp = q["sides"][side].get("qsplits", [])
        qd = q["sides"][side].get("qdeath")
        deaths[qd["reason"] if qd else "alive"] += 1
        run = []
        for (r, before, keep, child) in sp:
            if before == 4:
                k = "4 -> 2+2"
            elif child == 2 and before >= 5:
                k = "shed 2"
            elif keep <= 3 and before >= 6:
                k = "cut (keeps 2-3)"
            else:
                k = "other"
            kinds[k + (" in rounds 0-20" if r <= 20 else "")] += 1
            if k == "cut (keeps 2-3)" and r > 20 and before >= 8:
                cuts.append((gid, r, before, keep, g["winner"] == side))
            if k == "shed 2" and r > 20:
                if run and r == run[-1][0] + 1:
                    run.append((r, before))
                else:
                    if len(run) >= 3:
                        runs.append((gid, run[0][0], len(run), run[0][1], g["winner"] == side, g["end_type"]))
                    run = [(r, before)]
            else:
                if len(run) >= 3:
                    runs.append((gid, run[0][0], len(run), run[0][1], g["winner"] == side, g["end_type"]))
                run = []
        if len(run) >= 3:
            runs.append((gid, run[0][0], len(run), run[0][1], g["winner"] == side, g["end_type"]))
    print(f"=== {name} ({tid}): {n} games")
    print("  queen splits by kind:", dict(sorted(kinds.items())))
    print(f"  shed runs of 3+ rounds in a row after round 20: {len(runs)} in {len({x[0] for x in runs})} games; segments shed {sum(2 * x[2] for x in runs)}; "
          f"longest {max((x[2] for x in runs), default=0)} rounds; started at queen length {sorted(x[3] for x in runs)[len(runs) // 2] if runs else '-'} (median); "
          f"games won {sum(1 for gid in {x[0] for x in runs} if any(y[0] == gid and y[4] for y in runs))}")
    late = [x for x in runs if x[1] + x[2] >= 499]
    print(f"     of those, runs still going at round 499: {len(late)}; examples (game, start round, rounds, length at start, won): {[(x[0], x[1], x[2], x[3], x[4]) for x in sorted(runs, key=lambda x: -x[2])[:8]]}")
    print(f"  cuts after round 20 of a queen 8+ long that keep 2-3: {len(cuts)} in {len({x[0] for x in cuts})} games; mean length before {sum(x[2] for x in cuts) / max(1, len(cuts)):.1f}; "
          f"games won {sum(1 for gid in {x[0] for x in cuts} if any(y[0] == gid and y[4] for y in cuts))}; biggest: {[(x[0], x[1], x[2], x[3]) for x in sorted(cuts, key=lambda x: -x[2])[:6]]}")
    print("  how the queen ended:", dict(deaths.most_common()))
    # did the shedding cost games? round-500 games lost on the queen rule with both queens alive
    shed_by_game = defaultdict(int)
    for x in runs:
        shed_by_game[x[0]] += 2 * x[2]
    flip, lostq = [], 0
    for gid, shed in shed_by_game.items():
        g = games[gid]
        side = "A" if g["teamAId"] == tid else "B"
        op = "B" if side == "A" else "A"
        q = json.load(open(os.path.join(HERE, "q", gid + ".json")))
        mine, theirs = q["sides"][side]["final"]["queen"], q["sides"][op]["final"]["queen"]
        if g["winner"] != side and g["end_type"] == "queen rule" and mine > 0 and theirs > 0:
            lostq += 1
            if mine + shed > theirs:
                flip.append((gid, g["map"], mine, shed, theirs))
    print(f"  games with a shed run that were lost on the queen rule with both queens alive: {lostq}; of those the queen would have been the longer one without the shedding: {len(flip)} {flip}")
