#!/usr/bin/env python3
"""b_chance3.py <team_id> [max_round=100] [min_round=0] [maxlen=3]: what else was true on the turns the team did /
did not ram a queen it had in view and within reach (sub-session A2).

Takes the in-view chances from q3v2 (2000+ opponents, no Schooltime) with min_round <= round < max_round and attacker
length <= maxlen, walks those replays (stopping at max_round) and records at the start of the attacker's turn:
  ate        did the attacker eat a pearl in the move it made instead
  pearl1/2   a pearl lay within 1 / 2 steps of its head
  allies4    own heads within 4 steps of the attacker (other than itself)
  foes4      enemy heads within 4 steps of the attacker, the queen not counted
  qallies2   own heads within 2 steps of her head (someone else who could do it)
  herfoes    enemy (her team) heads within 3 steps of her head: her escort
  order      what it did: 'closer' / 'same' / 'farther' (path distance to her head after its move), 'split', 'died'
  age        rounds since the attacker was born
  ownq       own queen alive
and whether she was rammed by another dragon of the team later in the same round.
Prints taken / not taken counts for each feature value, then every not-taken turn.
"""
import csv
import json
import os
import sys
from collections import Counter, defaultdict

import lib

HERE = os.path.dirname(os.path.abspath(__file__))
tid = sys.argv[1]
maxr = int(sys.argv[2]) if len(sys.argv) > 2 else 100
minr = int(sys.argv[3]) if len(sys.argv) > 3 else 0
maxlen = int(sys.argv[4]) if len(sys.argv) > 4 else 3
games = {g["game_id"]: g for g in csv.DictReader(open(os.path.join(HERE, "games.csv")))}
todo = {}
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
    p = os.path.join(HERE, "q3v2", gid + ".json")
    if not os.path.exists(p):
        continue
    ch = [c for c in json.load(open(p))["chances"] if c[1] == side and c[9] and minr <= c[0] < maxr and c[3] <= maxlen]
    if ch:
        todo[gid] = (side, {(c[0], c[2]): c for c in ch})


class Stop(Exception):
    pass


class H(lib.Hooks):
    def __init__(self, side, chances, lastr):
        self.side, self.chances, self.lastr = side, chances, lastr
        self.out = []
        self.born = {}
        self.pending = None
        self.qram = {}

    def round_start(self, g, r):
        if r > self.lastr + 1:
            raise Stop

    def split(self, g, parent, child, before, plen, clen):
        self.born[child] = g.round

    def action(self, g, did, kind, nsteps):
        self.finish(g)
        key = (g.round, did)
        c = self.chances.get(key)
        if c is None:
            return
        b = g.board
        s = self.side
        o = "B" if s == "A" else "A"
        q = g.bodies.get(b.queen[o])
        if q is None:
            return
        head = g.bodies[did][0]
        d4 = b.bfs(head, 4)
        dq = b.bfs(q[0], 12)
        pearls = [d4[c2] for c2 in g.pearls if c2 in d4]
        rec = dict(c=c, kind=kind,
                   pearl1=any(x <= 1 for x in pearls), pearl2=any(x <= 2 for x in pearls),
                   allies4=sum(1 for i, o2 in g.bodies.items() if g.teams[i] == s and i != did and o2[0] in d4),
                   foes4=sum(1 for i, o2 in g.bodies.items() if g.teams[i] == o and i != b.queen[o] and o2[0] in d4),
                   qallies2=sum(1 for i, o2 in g.bodies.items() if g.teams[i] == s and i != did and dq.get(o2[0], 99) <= 2),
                   herfoes=sum(1 for i, o2 in g.bodies.items() if g.teams[i] == o and i != b.queen[o] and dq.get(o2[0], 99) <= 3),
                   age=g.round - self.born.get(did, 0), ownq=int(b.queen[s] in g.bodies),
                   d0=dq.get(head), qcell=q[0], ate=False, did=did, r=g.round)
        self.pending = rec

    def eat(self, g, did, cell, origin):
        if self.pending and self.pending["did"] == did:
            self.pending["ate"] = True

    def finish(self, g):
        rec = self.pending
        if rec is None:
            return
        self.pending = None
        b = g.board
        did = rec["did"]
        body = g.bodies.get(did)
        if rec["kind"] == 1:
            rec["order"] = "split"
        elif body is None:
            rec["order"] = "died"
        else:
            d1 = b.bfs(rec["qcell"], 12).get(body[0])
            d0 = rec["d0"]
            rec["order"] = "?" if d1 is None or d0 is None else "closer" if d1 < d0 else "same" if d1 == d0 else "farther"
        self.out.append(rec)

    def death(self, g, did, reason, length, body, actor):
        b = g.board
        o = "B" if self.side == "A" else "A"
        if did == b.queen[o] and reason == "headon" and actor is not None and actor != did:
            self.qram[g.round] = actor

    def end(self, g, rounds, winner, result):
        self.finish(g)


recs = []
n = 0
for gid, (side, chances) in sorted(todo.items()):
    h = H(side, chances, max(k[0] for k in chances))
    w = lib.Walk(games[gid]["replay_path"])
    try:
        w.run(h)
    except Stop:
        h.finish(w)
    for rec in h.out:
        rec["gid"] = gid
        rec["map"] = games[gid]["map"]
        rec["rammed_by_other"] = h.qram.get(rec["r"]) not in (None, rec["did"])
        recs.append(rec)
    n += 1
print(f"team {tid}: rounds {minr}-{maxr - 1}, attackers up to {maxlen} long: {len(recs)} in-view chances in {n} games; taken {sum(r['c'][5] for r in recs)}")


def show(name, key):
    c = defaultdict(lambda: [0, 0])
    for r in recs:
        k = key(r)
        c[k][0] += r["c"][5]
        c[k][1] += 1
    print(f"  {name}: " + " | ".join(f"{k}: {v[0]}/{v[1]}" for k, v in sorted(c.items(), key=lambda kv: str(kv[0]))))


show("a pearl within 1 step of the attacker", lambda r: r["pearl1"])
show("a pearl within 2 steps", lambda r: r["pearl2"])
show("own heads within 4 steps of the attacker", lambda r: min(r["allies4"], 3))
show("enemy heads (not the queen) within 4 steps of the attacker", lambda r: min(r["foes4"], 3))
show("own heads within 2 steps of her", lambda r: min(r["qallies2"], 2))
show("her own heads within 3 steps of her", lambda r: min(r["herfoes"], 3))
show("own queen alive", lambda r: r["ownq"])
show("age of the attacker (rounds since born)", lambda r: "0-4" if r["age"] < 5 else "5-19" if r["age"] < 20 else "20+")
show("attacker length, her length", lambda r: "L%d vs her %d" % (r["c"][3], min(r["c"][6], 4)))
show("map", lambda r: r["map"])
show("allies4 minus foes4 (incl. the queen as one foe)", lambda r: max(-2, min(2, r["allies4"] - r["foes4"] - 1)))
nt = [r for r in recs if not r["c"][5]]
print(f"  not taken: {len(nt)}; what it did instead: {dict(Counter(r['order'] for r in nt))}; ate that turn: {sum(r['ate'] for r in nt)}; she was rammed by another dragon of the team that round: {sum(r['rammed_by_other'] for r in nt)}")
bylen = defaultdict(Counter)
for r in nt:
    ln = r["c"][3]
    bylen["2-3" if ln <= 3 else "4" if ln == 4 else "5-9" if ln <= 9 else "10-12"][r["order"]] += 1
print("  not taken, what it did instead, by attacker length: " + "; ".join(f"{k}: {dict(v)}" for k, v in sorted(bylen.items())))
big = [r for r in recs if r["c"][3] >= 5]
c2 = defaultdict(lambda: [0, 0])
for r in big:
    k = "her length >= attacker" if r["c"][6] >= r["c"][3] else "her length = attacker - 1 or - 2" if r["c"][6] >= r["c"][3] - 2 else "her length <= attacker - 3"
    c2[k][0] += r["c"][5]
    c2[k][1] += 1
print("  attackers 5-12 long, taken by her length relative to the attacker: " + "; ".join(f"{k}: {v[0]}/{v[1]}" for k, v in sorted(c2.items())))
for r in nt[:70]:
    c = r["c"]
    print(f"    {r['gid']} {r['map']} r{c[0]} #{c[2]} L{c[3]} needs {c[4]} her L{c[6]}; did: {r['order']}{' and ate' if r['ate'] else ''}; pearl within 1: {r['pearl1']}; own heads near me {r['allies4']}, enemy heads near me {r['foes4']}, her escort {r['herfoes']}; own queen alive {r['ownq']}; age {r['age']}"
          + ("; another dragon rammed her this round" if r["rammed_by_other"] else ""))
