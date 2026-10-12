#!/usr/bin/env python3
"""b_open.py <game_id> [upto=100]: opening economy per 10 rounds for both teams (sub-session A2, after a_open.py).

Per 10-round block and team: units and total length at the block start, natural pearls eaten, corpse pearls eaten,
splits, deaths by kind (K = noaction, S = moved into its own body, B = moved into another body, W = moved into kelp,
H = head-on, either side of a ram), move orders with paid steps (count / segments paid), mean wrapped manhattan
distance of non-queen heads from the team's queen spawn, number of different cells any own head has ever stood on
(coverage), natural pearls on the board within 10 cells of the queen spawn.
Then per team: split histogram (length before -> parent + child) for rounds 0-30, 31-60, 61-100; how many children
were born per block and how far (path steps, at most 40) the child's head was from the parent's head 5 rounds
after the split; the length of dragons at the moment they died by K/S/B/W and how many of the dropped pearls were
eaten by the own team within 10 rounds.
"""
import csv
import sys
from collections import Counter, defaultdict

import lib

GAMES = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
gid = sys.argv[1]
upto = int(sys.argv[2]) if len(sys.argv) > 2 else 100
info = GAMES[gid]
CODE = {"noaction": "K", "self": "S", "body": "B", "wall": "W", "headon": "H"}


class Stop(Exception):
    pass


class O(lib.Hooks):
    def __init__(self):
        self.c = Counter()
        self.rows = {}
        self.spawn = {}
        self.cover = {"A": set(), "B": set()}
        self.splits = {"A": Counter(), "B": Counter()}
        self.pend = []           # (round+5, parent, child)
        self.sep = {"A": defaultdict(list), "B": defaultdict(list)}
        self.dl = {"A": Counter(), "B": Counter()}
        self.drop = {"A": Counter(), "B": Counter()}
        self.first_split_round = {"A": [], "B": []}
        self.eat_len = {"A": Counter(), "B": Counter()}
        self.how = {"A": Counter(), "B": Counter()}
        self.walls = {"A": Counter(), "B": Counter()}
        self.cells = {"A": Counter(), "B": Counter()}

    def round_start(self, g, r):
        b = g.board
        if r == 0:
            for s in "AB":
                self.spawn[s] = g.bodies[b.queen[s]][0]
        if r > upto:
            raise Stop
        for d, body in g.bodies.items():
            self.cover[g.teams[d]].add(body[0])
        keep = []
        for rr, parent, child in self.pend:
            if rr == r:
                if parent in g.bodies and child in g.bodies:
                    dist = b.bfs(g.bodies[parent][0], 40).get(g.bodies[child][0], 41)
                    self.sep[g.teams[parent]][(r - 5) // 10 * 10].append(dist)
            else:
                keep.append((rr, parent, child))
        self.pend = keep
        if r % 10 == 0:
            row = {}
            nat = [c for c, v in g.pearls.items() if v[0] == "natural"]
            for s in "AB":
                ls = [(d, body) for d, body in g.bodies.items() if g.teams[d] == s]
                others = [b.manhattan(body[0], self.spawn[s]) for d, body in ls if d != b.queen[s]]
                lens = Counter(min(len(x[1]), 6) for x in ls)
                row[s] = (len(ls), sum(len(x[1]) for x in ls), round(sum(others) / max(1, len(others)), 1),
                          sum(1 for c in nat if b.cheb(c, self.spawn[s]) <= 10), len(self.cover[s]), dict(sorted(lens.items())))
            row["nat"] = len(nat)
            self.rows[r] = row

    def action(self, g, did, kind, nsteps):
        if kind == 0:
            n = len(g.bodies[did])
            free = -(-n // 4)
            if nsteps > free:
                s = g.teams[did]
                self.c[(g.round // 10 * 10, s, "paidmoves")] += 1
                self.c[(g.round // 10 * 10, s, "paidsegs")] += nsteps - free

    def eat(self, g, did, cell, origin):
        s = g.teams[did]
        self.c[(g.round // 10 * 10, s, "nat" if origin[0] == "natural" else "corpse")] += 1
        if origin[0] == "corpse" and origin[1] == s and origin[3] != "headon":
            self.drop[s]["eaten by own"] += 1
        elif origin[0] == "corpse" and origin[1] != s and origin[3] != "headon":
            self.drop[origin[1]]["eaten by enemy"] += 1
        if origin[0] == "natural":
            self.eat_len[s][min(g.act_start[1] if g.act_start else 0, 6)] += 1

    def split(self, g, parent, child, before, plen, clen):
        s = g.teams[parent]
        self.c[(g.round // 10 * 10, s, "split")] += 1
        ph = "r0-30" if g.round <= 30 else "r31-60" if g.round <= 60 else "r61-%d" % upto
        self.splits[s][(ph, before, plen, clen)] += 1
        self.pend.append((g.round + 5, parent, child))

    def death(self, g, did, reason, length, body, actor):
        s = g.teams[did]
        self.c[(g.round // 10 * 10, s, CODE.get(reason, "?"))] += 1
        if reason != "headon":
            b = g.board
            occ = set()
            for o2 in g.bodies.values():
                occ.update(o2)
            free = sum(1 for n in b.nb(body[0]) if n is not None and n not in occ)
            nk = sum(1 for n in b.nb(body[0]) if n is None)
            mine = set(body)
            na = sum(1 for n in b.nb(body[0]) if n is not None and n in occ and n not in mine
                     and any(n in o2 for i2, o2 in g.bodies.items() if g.teams[i2] == s and i2 != did))
            ne = sum(1 for n in b.nb(body[0]) if n is not None and n in occ and n not in mine) - na
            self.walls[s][f"kelp {nk}, own body {4 - nk - na - ne - free}, team-mate {na}, enemy {ne}, free {free}"] += 1
            self.cells[s][body[0]] += 1
            order = {0: "move", 1: "split", 2: "suicide"}.get(g.act_kind, "none") if actor == did else "other"
            self.how[s][(CODE.get(reason, "?"), order, "boxed" if free == 0 else "had %d free" % free)] += 1
            self.dl[s][(CODE.get(reason, "?"), min(length, 6))] += 1
            self.drop[s]["pearls dropped"] += -(-length // 2)
            self.drop[s]["segments"] += length


o = O()
g = lib.Walk(info["replay_path"])
try:
    g.run(o)
except Stop:
    pass
print(f"=== OPEN2 {gid} {info.get('map')} | A = {info['teamAName']} ({info['teamAId']}) B = {info['teamBName']} ({info['teamBId']}) | queen spawns {o.spawn} | winner {info['winner']} by {info['end_type']}")
print("  block | side: units total | ate natural/corpse | splits | deaths K(noaction)/S(self)/B(body)/W(kelp)/H(head-on) | paid moves/segments paid | mean dist from spawn | coverage | nat pearls within 10 of spawn || same for B | natural pearls on board")
for r in sorted(o.rows):
    parts = []
    for s in "AB":
        u = o.rows[r][s]
        c = o.c
        parts.append(f"{s}: {u[0]:2d}u {u[1]:3d}t | ate {c[(r, s, 'nat')]:2d}/{c[(r, s, 'corpse')]:2d} | sp{c[(r, s, 'split')]:2d} | K{c[(r, s, 'K')]:2d} S{c[(r, s, 'S')]:2d} B{c[(r, s, 'B')]:2d} W{c[(r, s, 'W')]:2d} H{c[(r, s, 'H')]:2d} | paid {c[(r, s, 'paidmoves')]:2d}/{c[(r, s, 'paidsegs')]:2d} | dist{u[2]:5.1f} | cov{u[4]:4d} | near{u[3]:3d}")
    print(f"  r{r:3d} | " + " || ".join(parts) + f" | board {o.rows[r]['nat']}")
print("  length histogram of living dragons at each block start (6 = 6 or longer):")
for r in sorted(o.rows):
    print(f"    r{r:3d} A {o.rows[r]['A'][5]} | B {o.rows[r]['B'][5]}")
for s in "AB":
    name = info["team%sName" % s]
    print(f"  {s} ({name}) splits (phase, before -> parent + child): n")
    for ph in ("r0-30", "r31-60", "r61-%d" % upto):
        items = sorted(((k[1], k[2], k[3]), n) for k, n in o.splits[s].items() if k[0] == ph)
        print(f"     {ph}: " + ", ".join(f"{a}->{b_}+{c_}: {n}" for (a, b_, c_), n in items))
    print(f"  {s} parent-child path distance 5 rounds after the split, per block (n, mean):",
          {k: (len(v), round(sum(v) / len(v), 1)) for k, v in sorted(o.sep[s].items())})
    print(f"  {s} non-ram deaths by (kind, length; 6 = 6+): {dict(sorted(o.dl[s].items()))}; their pearls: {dict(o.drop[s])}")
    print(f"  {s} non-ram deaths by (kind, the order given, free neighbour cells of its head at that moment): {dict(sorted(o.how[s].items()))}")
    print(f"  {s} what blocked the four sides of the head in those deaths: {dict(o.walls[s].most_common(8))}")
    rep = sum(n for c, n in o.cells[s].items() if n >= 2)
    print(f"  {s} cells where such deaths happened: {len(o.cells[s])} different cells for {sum(o.cells[s].values())} deaths; {rep} deaths on cells used twice or more; most used {o.cells[s].most_common(5)}")
    print(f"  {s} natural pearls eaten by eater length at the start of its turn (6 = 6+): {dict(sorted(o.eat_len[s].items()))}")
