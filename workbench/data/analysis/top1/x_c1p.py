#!/usr/bin/env python3
"""Candidate 1, attack A: chances that exist only through a pearl-paid step.

In our 401 games, both sides: turns of a non-queen dragon (12 or shorter) with the enemy queen's head in its 7x7
view where NO path within the plain reach exists but one does when every pearl eaten on the way pays for one more
step (the engine's real rule). Taken or not. The bot's hunt_path() plans within the plain reach only.
Output: x_out/c1p.txt"""
import math
import os
from collections import deque, Counter
from multiprocessing import Pool

import lib
import x_load as X

INF = 999


def reach(length):
    return math.ceil(length / 4) + max(0, length - 2)


def flood(board, src, R, blocked, pearls=None):
    cost = {src: 0}
    dq = deque([src])
    while dq:
        c = dq.popleft()
        cc = cost[c]
        if cc + 1 > R:
            continue
        for n in board.nb(c):
            if n is None or n in blocked:
                continue
            nc = cc if (pearls is not None and n in pearls) else cc + 1
            if nc < cost.get(n, INF):
                cost[n] = nc
                (dq.appendleft if nc == cc else dq.append)(n)
    return cost


def arrive(board, cost, cell):
    best = None
    for n in board.nb(cell):
        if n is not None and n in cost:
            v = cost[n] + 1
            if best is None or v < best:
                best = v
    return best


class H(lib.Hooks):
    def __init__(self, g):
        self.q = dict(g.board.queen)
        self.c = Counter()
        self.pend = None

    def action(self, g, did, kind, nsteps):
        self.pend = None
        side = g.teams.get(did)
        if side is None or did == self.q[side]:
            return
        es = "B" if side == "A" else "A"
        qb = g.bodies.get(self.q[es])
        if not qb:
            return
        body = g.bodies[did]
        L = len(body)
        if L > 12:
            return
        b = g.board
        h, qh = body[0], qb[0]
        if b.cheb(h, qh) > 3:
            return
        R = reach(L)
        occ = set()
        for bd in g.bodies.values():
            occ.update(bd)
        blocked = occ - {h}
        a_plain = arrive(b, flood(b, h, R, blocked), qh)
        plain = a_plain is not None and a_plain <= R
        kind_ = None
        if plain:
            kind_ = "plain"
        else:
            a_p = arrive(b, flood(b, h, R, blocked, g.pearls), qh)
            if a_p is not None and a_p <= R:
                kind_ = "pearl"
        if kind_:
            cls = "2-3" if L <= 3 else "4" if L == 4 else "5-12"
            self.pend = (side, kind_, cls, did)
            self.c[(side, kind_, cls, "n")] += 1

    def death(self, g, did, reason, length, body, actor):
        p = self.pend
        if p is None or reason != "headon" or actor != p[3] or actor == did:
            return
        side = g.teams[did]
        if did == self.q[side] and side != p[0]:
            self.c[(p[0], p[1], p[2], "t")] += 1


def one(job):
    gid, path, side = job
    g = lib.Walk(path)
    h = H(g)
    g.run(h)
    return side, {"|".join(k): v for k, v in h.c.items()}


def main():
    os.nice(10)
    gs = [g for g in X.games() if X.is_csv(g)]
    jobs = []
    for g in gs:
        side = X.side_of(g, X.ME)
        if side and X.in_study(g, side):
            jobs.append((g["gid"], g["path"], side))
    tot = {"meow": Counter(), "our opponents": Counter()}
    with Pool(5) as pool:
        for side, c in pool.imap_unordered(one, jobs, chunksize=4):
            for k, v in c.items():
                s, kind, cls, what = k.split("|")
                tot["meow" if s == side else "our opponents"][(kind, cls, what)] += v
    out = open("x_out/c1p.txt", "w")
    for who in ("meow", "our opponents"):
        c = tot[who]
        line = "%-14s" % who
        for kind in ("plain", "pearl"):
            for cls in ("2-3", "4", "5-12"):
                line += " | %s reach, attacker %s: %d of %d" % (kind, cls, c[(kind, cls, "t")], c[(kind, cls, "n")])
            line += " | %s reach, all: %d of %d" % (kind, sum(c[(kind, x, "t")] for x in ("2-3", "4", "5-12")), sum(c[(kind, x, "n")] for x in ("2-3", "4", "5-12")))
        print(line)
        out.write(line + "\n")


if __name__ == "__main__":
    main()
