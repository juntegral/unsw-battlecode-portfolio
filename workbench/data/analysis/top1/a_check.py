#!/usr/bin/env python3
"""a_check.py <game_id>...: recount of the numbers quoted in deep-read.md (sub-session A).

Per game, for the protagonist (team 306):
  - q3 chances on the enemy queen: total / taken / not taken
  - rounds in which an enemy head started within 3 path steps of the own queen, and what the queen ordered in those
    rounds (move with n steps / split / suicide), and how many such rounds had an own-team head within 6 steps
  - number of separate episodes (gap of more than 3 rounds starts a new one)
"""
import csv
import json
import os
import sys
from collections import Counter

import lib

GAMES = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
tot = Counter()


class C(lib.Hooks):
    def __init__(self, me):
        self.me = me
        self.flag = None
        self.kinds = Counter()
        self.rounds = []
        self.allies = Counter()

    def round_start(self, g, r):
        b = g.board
        qid = b.queen[self.me]
        self.flag = None
        body = g.bodies.get(qid)
        if not body:
            return
        dist = b.bfs(body[0], 6)
        en = [dist[o[0]] for i, o in g.bodies.items() if g.teams[i] != self.me and o[0] in dist]
        al = [dist[o[0]] for i, o in g.bodies.items() if g.teams[i] == self.me and i != qid and o[0] in dist]
        if en and min(en) <= 3:
            self.flag = (min(en), len(al))
            self.rounds.append(r)
            self.allies["0 allies" if not al else "1 ally" if len(al) == 1 else "2+ allies"] += 1

    def action(self, g, did, kind, nsteps):
        if self.flag is not None and did == g.board.queen[self.me]:
            self.kinds["move %d" % nsteps if kind == 0 else "split" if kind == 1 else "suicide"] += 1


for gid in sys.argv[1:]:
    q = json.load(open(f"q/{gid}.json"))
    me = [s for s in "AB" if q["sides"][s]["team"] == 306][0]
    q3 = json.load(open(f"q3/{gid}.json")) if os.path.exists(f"q3/{gid}.json") else {"chances": []}
    ch = [c for c in q3["chances"] if c[1] == me]
    taken = sum(1 for c in ch if c[5])
    small_missed = sum(1 for c in ch if not c[5] and c[3] <= 3)
    c = C(me)
    lib.Walk(GAMES[gid]["replay_path"]).run(c)
    eps = 0
    last = None
    for r in c.rounds:
        if last is None or r - last > 3:
            eps += 1
        last = r
    print(f"{gid} {q['map']:15s} chances {len(ch):2d} taken {taken} missed {len(ch) - taken} (missed by 2-3-long: {small_missed}) | close rounds {len(c.rounds):3d} episodes {eps} | queen orders {dict(c.kinds)} | {dict(c.allies)}")
    tot["chances"] += len(ch)
    tot["taken"] += taken
    tot["missed"] += len(ch) - taken
    tot["close rounds"] += len(c.rounds)
    tot["episodes"] += eps
    for k, v in c.kinds.items():
        tot["order " + k] += v
    for k, v in c.allies.items():
        tot[k] += v
print("TOTAL", dict(tot))
