#!/usr/bin/env python3
"""b_chance5.py <team_id>: what became of the long dragons that did not ram a queen in view? (sub-session A2)

Takes the team's in-view chances from q3v2 (2000+ opponents, no Schooltime) with attacker length 5-12 that were
NOT taken, one record per (game, dragon) (its first such turn), walks the replay for 40 more rounds and reports:
  - was it the team's longest dragon at that turn; its length then and 20 rounds later
  - what it ate in the 20 rounds before and after (natural / corpse of own team / corpse of the enemy)
  - how it ended within 40 rounds: died by its own order with a free cell next to its head, within 6 cells of its
    own queen or of its team's longest dragon (= it fed them); died boxed in; rammed someone; was rammed; split;
    still alive
Prints the counts and one line per dragon.
"""
import csv
import json
import os
import sys
from collections import Counter, defaultdict

import lib

HERE = os.path.dirname(os.path.abspath(__file__))
tid = sys.argv[1]
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
    first = {}
    for c in json.load(open(p))["chances"]:
        if c[1] == side and c[9] and not c[5] and c[3] >= 5 and c[2] not in first:
            first[c[2]] = c
    if first:
        todo[gid] = (side, first)


class Stop(Exception):
    pass


class H(lib.Hooks):
    def __init__(self, side, first):
        self.side, self.first = side, first
        self.last = max(c[0] for c in first.values()) + 41
        self.eats = defaultdict(list)
        self.len_at = {}
        self.ended = {}
        self.longest = None
        self.splits = defaultdict(list)

    def round_start(self, g, r):
        if r > self.last:
            raise Stop
        b = g.board
        best = None
        for d, o in g.bodies.items():
            if g.teams[d] == self.side and (best is None or len(o) > best[0]):
                best = (len(o), d)
        self.longest = best[1] if best else None
        for d, c in self.first.items():
            if d in g.bodies:
                if r == c[0]:
                    self.len_at[(d, 0)] = (len(g.bodies[d]), d == self.longest)
                if r == c[0] + 20:
                    self.len_at[(d, 20)] = (len(g.bodies[d]), d == self.longest)

    def eat(self, g, did, cell, origin):
        if did in self.first:
            k = "natural" if origin[0] != "corpse" else ("own corpse" if origin[1] == self.side else "enemy corpse")
            self.eats[did].append((g.round, k))

    def split(self, g, parent, child, before, plen, clen):
        if parent in self.first:
            self.splits[parent].append((g.round, before, plen, clen))

    def death(self, g, did, reason, length, body, actor):
        b = g.board
        if did in self.first and did not in self.ended:
            c = self.first[did]
            if not (c[0] <= g.round <= c[0] + 40):
                return
            if reason == "headon":
                self.ended[did] = (g.round, "rammed someone" if actor == did else "was rammed", length)
                return
            occ = set()
            for o2 in g.bodies.values():
                occ.update(o2)
            boxed = not any(n is not None and n not in occ for n in b.nb(body[0]))
            q = g.bodies.get(b.queen[self.side])
            lh = g.bodies.get(self.longest) if self.longest != did else None
            near = "near own queen" if q is not None and b.manhattan(body[0], q[0]) <= 6 else "near own longest" if lh is not None and b.manhattan(body[0], lh[0]) <= 6 else "elsewhere"
            self.ended[did] = (g.round, ("died boxed in" if boxed else "died by choice") + ", " + near, length)


res = Counter()
lines = []
n = 0
for gid, (side, first) in sorted(todo.items()):
    h = H(side, first)
    try:
        lib.Walk(games[gid]["replay_path"]).run(h)
    except Stop:
        pass
    for d, c in first.items():
        n += 1
        l0 = h.len_at.get((d, 0), (c[3], False))
        l20 = h.len_at.get((d, 20))
        e = h.ended.get(d)
        before = Counter(k for r, k in h.eats[d] if c[0] - 20 <= r < c[0])
        after = Counter(k for r, k in h.eats[d] if c[0] <= r <= c[0] + 20)
        sp = [s for s in h.splits[d] if c[0] <= s[0] <= c[0] + 40]
        if e:
            kind = e[1]
        elif sp:
            kind = "split (%d -> %d+%d)" % sp[0][1:]
        else:
            kind = "alive 40 rounds later"
        res[kind.split(" (")[0]] += 1
        res["was the team's longest at that turn"] += int(l0[1])
        res["ate own-team corpse pearls in the 20 rounds before"] += int(before["own corpse"] > 0)
        res["ate own-team corpse pearls in the 20 rounds after"] += int(after["own corpse"] > 0)
        res["longer 20 rounds later"] += int(bool(l20 and l20[0] > l0[0]))
        lines.append(f"    {gid} {games[gid]['map']} r{c[0]} #{d} L{c[3]} (her L{c[6]}, steps {c[4]}); longest {l0[1]}; ate before {dict(before)} after {dict(after)}; "
                     f"L after 20 rounds {l20[0] if l20 else '-'}; end: {kind}{' r%d L%d' % (e[0], e[2]) if e else ''}")
print(f"team {tid}: {n} dragons of 5-12 that did not ram a queen in view (first such turn each)")
for k, v in res.most_common():
    print(f"  {k}: {v}")
for line in lines[:80]:
    print(line)
