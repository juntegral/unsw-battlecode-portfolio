#!/usr/bin/env python3
"""d_e.py: what the queen rules change that a replay can show (sub-session A4, question e).

Our queen rules are on only on maps of more than 600 cells.  For meow (live bot, rules on / rules off), the
opponent's queen and the top three, from d_out/life (head cell and length every round), q/*.json (splits) and
games.csv:
  portal steps   rounds in which her head jumped further than her reach allows (a portal step), per 100 queen-rounds,
                 on maps that have portals; and the share of queens that ever took one, and how many did so before
                 round 20
  late splits    her splits after round 200, per queen alive at round 200
  early splits   her splits in rounds 0-99 per 100 queen-rounds
  mean length    in rounds 100-199
"""
import csv
import json
import os
from collections import Counter, defaultdict

import lib

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = {"306": "Vibing++", "91": "SSS", "264": "forgot"}
LIVE = {"dl-20261003", "dl-20261004", "stride-old", "passage2-test-old", "qh31-test-old", "tc30-dev1-old"}
GROUPS = ["meow live rules on", "meow live rules off", "meow cand rules on", "meow cand rules off", "opp", "forgot", "SSS", "Vibing++"]


def main():
    t = defaultdict(Counter)
    for g in csv.DictReader(open(os.path.join(HERE, "games.csv"))):
        if g["map"] == "Schooltime":
            continue
        p = os.path.join(HERE, "d_out", "life", g["game_id"] + ".json")
        if not os.path.exists(p):
            continue
        life = q = None
        w, h = int(g["width"]), int(g["height"])
        for s in "AB":
            o = "B" if s == "A" else "A"
            team, opp = g[f"team{s}Id"], g[f"team{o}Id"]
            elo_o, elo_s = float(g[f"team{o}Elo"] or 0), float(g[f"team{s}Elo"] or 0)
            groups = []
            if team in TOP and elo_o >= 2000:
                groups.append(TOP[team])
            if team == "1119" and elo_o >= 2000:
                groups.append(("meow live" if g["battle_id"] in LIVE else "meow cand") + (" rules on" if int(g["cells"]) > 600 else " rules off"))
            if opp == "1119" and elo_s >= 2000:
                groups.append("opp")
            if not groups:
                continue
            if life is None:
                life = json.load(open(p))
                q = json.load(open(os.path.join(HERE, "q", g["game_id"] + ".json")))
            ls, qs = life["sides"][s], q["sides"][s]
            pos, qlen = ls["pos"], ls["qlen"]
            jumps = []
            for r in range(1, len(pos)):
                if pos[r] and pos[r - 1]:
                    dx, dy = abs(pos[r][0] - pos[r - 1][0]), abs(pos[r][1] - pos[r - 1][1])
                    d = min(dx, w - dx) + min(dy, h - dy)
                    if d > max(2, lib.reach(qlen[r - 1])):
                        jumps.append(r)
            alive = sum(1 for c in pos if c)
            for grp in groups:
                c = t[grp]
                c["games"] += 1
                c["rounds"] += alive
                if q["portals"]:
                    c["portal games"] += 1
                    c["portal rounds"] += alive
                    c["portal steps"] += len(jumps)
                    c["queens with a portal step"] += bool(jumps)
                    c["queens with a portal step before round 20"] += any(r < 20 for r in jumps)
                if len(pos) > 200 and pos[200]:
                    c["alive at 200"] += 1
                    c["splits after 200"] += sum(1 for sp in qs["qsplits"] if sp[0] > 200)
                    c["queens that split after 200"] += any(sp[0] > 200 for sp in qs["qsplits"])
                c["splits 0-99"] += sum(1 for sp in qs["qsplits"] if sp[0] < 100)
                c["rounds 0-99"] += sum(1 for c0 in pos[:100] if c0)
                c["len sum 100-199"] += sum(qlen[100:200])
                c["rounds 100-199"] += sum(1 for c0 in pos[100:200] if c0)
    print("group | games | games on maps with portals | portal steps per 100 queen-rounds there | queens that ever took one | ... before round 20 | queens alive at round 200 | of those split after round 200 | "
          "splits after 200 per such queen | splits per 100 rounds in rounds 0-99 | mean length rounds 100-199")
    for grp in GROUPS:
        c = t[grp]
        if not c["games"]:
            continue
        print(f"{grp} | {c['games']} | {c['portal games']} | {100 * c['portal steps'] / max(1, c['portal rounds']):.2f} | {c['queens with a portal step']} ({100 * c['queens with a portal step'] // max(1, c['portal games'])}%) | "
              f"{c['queens with a portal step before round 20']} | {c['alive at 200']} | {c['queens that split after 200']} | {c['splits after 200'] / max(1, c['alive at 200']):.2f} | "
              f"{100 * c['splits 0-99'] / max(1, c['rounds 0-99']):.2f} | {c['len sum 100-199'] / max(1, c['rounds 100-199']):.1f}")


if __name__ == "__main__":
    main()
