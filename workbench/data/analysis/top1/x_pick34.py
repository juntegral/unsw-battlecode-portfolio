#!/usr/bin/env python3
"""Pick turns to look at by eye for candidates 3 and 4 (own walk of a few of our games).

Candidate 3: our live bot on maps over 1,200 cells, rounds 150-299: a 2-3-long with no enemy head in view and a free
pearl on the next cell (with a way on) that does NOT take it. A few from maps of 1,200 cells or fewer after round 300.
Candidate 4: our live bot on maps over 1,200 cells: a dragon of 4 or shorter with a same-length or longer small enemy
head on the next cell, not outnumbered, that does NOT ram.
Output: x_out/c3_eye.json, x_out/c4_eye.json (lists of [game, round, dragon, note] for x_eye.py)."""
import json
import random
from collections import deque

import lib
import x_load as X

random.seed(11)


class H(lib.Hooks):
    def __init__(self, g, lo, hi):
        self.q = dict(g.board.queen)
        self.c3, self.c4 = [], []
        self.lo, self.hi = lo, hi
        self.side = None

    def action(self, g, did, kind, nsteps):
        side = g.teams.get(did)
        if side != self.side or did == self.q[side]:
            return
        b = g.board
        body = g.bodies[did]
        L = len(body)
        if L > 4:
            return
        h = body[0]
        own_h = en_h = 0
        targets = []
        for d2, bd in g.bodies.items():
            if d2 == did:
                continue
            if b.cheb(h, bd[0]) <= 3:
                if g.teams[d2] == side:
                    own_h += 1
                else:
                    en_h += 1
                    if d2 not in self.q.values() and len(bd) <= 4 and b.manhattan(h, bd[0]) == 1 and bd[0] in b.nb(h):
                        targets.append((d2, len(bd)))
        occ = set()
        for bd in g.bodies.values():
            occ.update(bd)
        if en_h == 0 and kind == 0 and L <= 3 and self.lo <= g.round < self.hi:
            good = []
            for d in range(4):
                c = b.nb(h)[d]
                if c is None or c not in g.pearls or c in occ:
                    continue
                if any(n is not None and n != h and n not in occ for n in b.nb(c)):
                    good.append((d, c))
            if good and not any(d == (g.act_dirs[0] if g.act_dirs else None) for d, c in good):
                best = None
                for d2, bd in g.bodies.items():
                    if d2 == did or g.teams[d2] != side or len(bd) <= L:
                        continue
                    dist = b.manhattan(good[0][1], bd[0])
                    if best is None or dist < best[0]:
                        best = (dist, len(bd), d2)
                self.c3.append([g.round, did, "declined pearl at %s; nearest longer own dragon: %s" % (
                    good[0][1], ("#%d, %d long, %d cells from the pearl" % (best[2], best[1], best[0])) if best else "none")])
        if targets and own_h >= en_h and g.round < 300:
            tg = [t for t in targets if t[1] >= L]
            if tg:
                self.c4.append([g.round, did, "enemy head #%d (%d long) on the next cell; own heads in view %d, enemy heads %d; own length %d" % (
                    tg[0][0], tg[0][1], own_h, en_h, L), tg[0][0]])
        self._pend = None

    def death(self, g, did, reason, length, body, actor):
        # drop candidate-4 picks in which it did ram that head
        if reason == "headon" and actor is not None and actor != did and self.c4 and self.c4[-1][0] == g.round and \
                self.c4[-1][1] == actor and self.c4[-1][3] == did:
            self.c4.pop()


gs = [g for g in X.games() if X.is_csv(g)]
mine = [(g, X.side_of(g, X.ME)) for g in gs if X.side_of(g, X.ME) and X.in_study(g, X.side_of(g, X.ME)) and X.build(g) == "live"]
bigm = [(g, s) for g, s in mine if g["cells"] > 1200]
small = [(g, s) for g, s in mine if g["cells"] <= 1200]
random.shuffle(bigm)
random.shuffle(small)
c3, c4 = [], []
seen_maps = {}
for g, side in bigm:
    if seen_maps.get(g["map"], 0) >= 2:
        continue
    seen_maps[g["map"]] = seen_maps.get(g["map"], 0) + 1
    w = lib.Walk(g["path"])
    h = H(w, 150, 300)
    h.side = side
    w.run(h)
    random.shuffle(h.c3)
    random.shuffle(h.c4)
    for r, did, note in h.c3[:2]:
        c3.append([g["gid"], r, did, "C3 big map: " + note])
    for r, did, note, _ in h.c4[:2]:
        c4.append([g["gid"], r, did, "C4 big map: " + note])
n = 0
for g, side in small:
    if n >= 3:
        break
    w = lib.Walk(g["path"])
    h = H(w, 300, 400)
    h.side = side
    w.run(h)
    if h.c3:
        random.shuffle(h.c3)
        r, did, note = h.c3[0]
        c3.append([g["gid"], r, did, "C3 small/medium map after round 300: " + note])
        n += 1
json.dump(c3, open("x_out/c3_eye.json", "w"))
json.dump(c4, open("x_out/c4_eye.json", "w"))
print(len(c3), "candidate-3 turns,", len(c4), "candidate-4 turns")
