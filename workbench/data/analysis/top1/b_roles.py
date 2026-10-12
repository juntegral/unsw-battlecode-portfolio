#!/usr/bin/env python3
"""b_roles.py <game_id> [min_life=60]: dragons that live long without eating (sub-session A2).

A forager eats and splits. A dragon that lives min_life rounds or more and never eats in that time is doing something
else (scouting, following, guarding). For each team: how many dragons lived that long at all, how many of them ate
nothing / one pearl, and for each non-eater: id, born (round, length), length, rounds alive, how far its head
travelled (cells between its position every 10 rounds), in how many rounds it had the enemy queen's head inside its
7x7 view, how many rounds it spent within 6 cells (manhattan) of its own queen, and how it ended.
Queens are left out.
"""
import csv
import sys
from collections import Counter, defaultdict

import lib

GAMES = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
gid = sys.argv[1]
minlife = int(sys.argv[2]) if len(sys.argv) > 2 else 60
info = GAMES[gid]


class R(lib.Hooks):
    def __init__(self):
        self.born = {}
        self.blen = {}
        self.team = {}
        self.eats = Counter()
        self.last = {}
        self.ended = {}
        self.sawq = Counter()
        self.nearq = Counter()
        self.pos = defaultdict(list)
        self.len_now = {}
        self.rounds = 0
        self.split_n = Counter()

    def round_start(self, g, r):
        b = g.board
        self.rounds = r
        qh = {s: (g.bodies[b.queen[s]][0] if b.queen[s] in g.bodies else None) for s in "AB"}
        for d, body in g.bodies.items():
            s = g.teams[d]
            if d not in self.born:
                self.born[d] = r
                self.blen[d] = len(body)
                self.team[d] = s
            self.last[d] = r
            self.len_now[d] = len(body)
            o = "B" if s == "A" else "A"
            if qh[o] is not None and b.cheb(body[0], qh[o]) <= 3:
                self.sawq[d] += 1
            if qh[s] is not None and b.manhattan(body[0], qh[s]) <= 6:
                self.nearq[d] += 1
            if r % 10 == 0:
                self.pos[d].append(body[0])

    def eat(self, g, did, cell, origin):
        self.eats[did] += 1

    def split(self, g, parent, child, before, plen, clen):
        self.split_n[parent] += 1

    def death(self, g, did, reason, length, body, actor):
        s = g.teams[did]
        how = reason
        if reason == "headon":
            if actor == did:
                how = "rammed an enemy" if True else how
            else:
                how = "was rammed"
        self.ended[did] = (g.round, how, length)


x = R()
g = lib.Walk(info["replay_path"])
g.run(x)
b = g.board
print(f"=== ROLES {gid} {info['map']} | A = {info['teamAName']} B = {info['teamBName']} | dragons that lived {minlife}+ rounds")
for s in "AB":
    name = info["team%sName" % s]
    ids = [d for d in x.born if x.team[d] == s and d != b.queen[s] and x.last[d] - x.born[d] + 1 >= minlife]
    non = [d for d in ids if x.eats[d] == 0]
    one = [d for d in ids if x.eats[d] == 1]
    alln = sum(1 for d in x.born if x.team[d] == s)
    print(f"  {s} ({name}): {alln} dragons in the game, {len(ids)} lived {minlife}+ rounds; of those {len(non)} never ate, {len(one)} ate once; eats per 100 rounds of life among the long-lived: "
          f"{100 * sum(x.eats[d] for d in ids) / max(1, sum(x.last[d] - x.born[d] + 1 for d in ids)):.1f}")
    for d in sorted(non, key=lambda d: x.born[d])[:25]:
        pos = x.pos[d]
        trav = sum(b.manhattan(pos[i], pos[i + 1]) for i in range(len(pos) - 1))
        e = x.ended.get(d)
        life = x.last[d] - x.born[d] + 1
        print(f"    #{d} born r{x.born[d]} L{x.blen[d]}, alive {life} rounds, final L{x.len_now[d]}, splits {x.split_n[d]}, moved about {trav} cells (10-round hops), "
              f"enemy queen in view {x.sawq[d]} rounds, within 6 of own queen {x.nearq[d]} rounds, end: {('r%d %s' % (e[0], e[1])) if e else 'alive at the end'}")
