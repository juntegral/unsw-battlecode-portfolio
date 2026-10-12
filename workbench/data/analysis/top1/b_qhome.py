#!/usr/bin/env python3
"""b_qhome.py <game_id> ...: where does each queen live relative to her team? (sub-session A2)

One pass per game. Every 10 rounds from round 20, while the queen is alive: her wrapped manhattan distance from her
own spawn, the mean such distance of the other own heads, the number of own heads and of enemy heads within 8 cells
(manhattan) of her head, and the same two numbers for the average own non-queen dragon (own heads / enemy heads
within 8 cells of it). Also: natural pearls eaten by the queen per 100 rounds of life against the team's average
per dragon, and the share of her moves that end further from the nearest enemy head when one is within 6 cells.
Prints one line per (game, team) and totals per team id.
"""
import csv
import sys
from collections import defaultdict

import lib

GAMES = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
NAMES = {"91": "SSS", "264": "forgot", "306": "Vibing++"}
tot = defaultdict(lambda: defaultdict(float))


class H(lib.Hooks):
    def __init__(self):
        self.rows = {"A": [], "B": []}
        self.qeat = {"A": 0, "B": 0}
        self.teat = {"A": 0, "B": 0}
        self.unit_rounds = {"A": 0, "B": 0}
        self.qrounds = {"A": 0, "B": 0}

    def round_start(self, g, r):
        b = g.board
        for s in "AB":
            q = g.bodies.get(b.queen[s])
            own = [o[0] for d, o in g.bodies.items() if g.teams[d] == s and d != b.queen[s]]
            self.unit_rounds[s] += len(own)
            if q is None:
                continue
            self.qrounds[s] += 1
            if r < 20 or r % 10 or len(q) > 5:
                continue
            en = [o[0] for d, o in g.bodies.items() if g.teams[d] != s]
            sp = b.starts[b.queen[s]]
            home = b.manhattan(q[0], sp)
            oth = sum(b.manhattan(c, sp) for c in own) / len(own) if own else None
            qa = sum(1 for c in own if b.manhattan(c, q[0]) <= 8)
            qe = sum(1 for c in en if b.manhattan(c, q[0]) <= 8)
            # the average own dragon (sample at most 30 to keep it cheap)
            sample = own[:30]
            if sample:
                da = sum(sum(1 for c2 in own if c2 is not c and b.manhattan(c, c2) <= 8) for c in sample) / len(sample)
                de = sum(sum(1 for c2 in en if b.manhattan(c, c2) <= 8) for c in sample) / len(sample)
            else:
                da = de = None
            self.rows[s].append((home, oth, qa, qe, da, de))

    def eat(self, g, did, cell, origin):
        s = g.teams[did]
        if origin[0] != "natural":
            return
        if did == g.board.queen[s]:
            self.qeat[s] += 1
        else:
            self.teat[s] += 1


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else float("nan")


print("game | map | team | checkpoints (queen 5 or shorter) | queen dist from spawn | other heads dist from spawn | own heads within 8 of queen | of the average dragon | enemy heads within 8 of queen | of the average dragon | natural pearls per 100 rounds: queen / average dragon")
for gid in sys.argv[1:]:
    g = GAMES[gid]
    h = H()
    lib.Walk(g["replay_path"]).run(h)
    for s in "AB":
        t = g["team%sId" % s]
        rows = h.rows[s]
        if not rows:
            continue
        v = [mean([x[i] for x in rows]) for i in range(6)]
        qrate = 100 * h.qeat[s] / max(1, h.qrounds[s])
        trate = 100 * h.teat[s] / max(1, h.unit_rounds[s])
        print(f"{gid} | {g['map']:15s} | {NAMES.get(t, g['team%sName' % s][:10]):8s} | {len(rows):3d} | {v[0]:5.1f} | {v[1]:5.1f} | {v[2]:4.1f} | {v[4]:4.1f} | {v[3]:4.1f} | {v[5]:4.1f} | {qrate:4.1f} / {trate:4.1f}")
        for k, val in zip(("home", "oth", "qa", "qe", "da", "de"), v):
            if val == val:
                tot[t][k] += val
        tot[t]["n"] += 1
        tot[t]["qrate"] += qrate
        tot[t]["trate"] += trate
print("\nmeans over the games of each team (each game counts once):")
for t, d in tot.items():
    n = d["n"]
    print(f"  {NAMES.get(t, t):8s} games {int(n):2d} | queen dist from spawn {d['home'] / n:5.1f} | other heads {d['oth'] / n:5.1f} | own heads within 8: queen {d['qa'] / n:4.1f}, average dragon {d['da'] / n:4.1f} | "
          f"enemy heads within 8: queen {d['qe'] / n:4.1f}, average dragon {d['de'] / n:4.1f} | natural pearls per 100 rounds: queen {d['qrate'] / n:4.1f}, average dragon {d['trate'] / n:4.1f}")
