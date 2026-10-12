#!/usr/bin/env python3
"""Candidate 2, attack H: what would the rule see if it is built from the bot's existing pieces?

B proposes to mark "every cell that an enemy head visible this round can move into" with stride_reach_map() /
spread_kill() / queen_margin(). Those compute an enemy's reach from the parts of it that are INSIDE THE QUEEN'S VIEW
(visible_parts), without pearl-paid steps, over cells not blocked by a part she sees. The study's "safe step" uses
the enemy's true length, pearl-paid steps and the true board. This script walks OUR games and, for every turn of our
queen with an enemy head in view, records for each free one-step move whether it is "in reach" under four models:
  bot    visible parts, no pearls, only parts in her view block (the existing code)
  bot+1  the same with one unseen segment assumed (A4's suggestion)
  true   true length, no pearls, true board
  pearl  true length, pearl-paid steps, true board
and which move she made and whether she was rammed that round by an enemy that was in view.
Output: x_out/c2vis.json (one list of turns), summary x_out/c2vis.txt"""
import json
import math
import os
import sys
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
    def __init__(self, g, side):
        self.q = dict(g.board.queen)
        self.side = side
        self.turns = []
        self.pending = None
        self.seen = set()

    def action(self, g, did, kind, nsteps):
        self.pending = None
        side = g.teams.get(did)
        if side != self.side or did != self.q[side]:
            return
        b = g.board
        body = g.bodies[did]
        h, L = body[0], len(body)
        es = "B" if side == "A" else "A"
        occ = set()
        inview = set()
        for d2, bd in g.bodies.items():
            occ.update(bd)
            if d2 != did:
                for c in bd:
                    if b.cheb(h, c) <= 3:
                        inview.add(c)
        ens = []
        for d2, bd in g.bodies.items():
            if g.teams[d2] == es and b.cheb(h, bd[0]) <= 3:
                v = sum(1 for c in bd if b.cheb(h, c) <= 3)
                ens.append((d2, bd[0], len(bd), v))
        self.seen = {e[0] for e in ens}
        if not ens:
            return
        tail = body[-1]
        opts = []
        for d in range(4):
            c = b.nb(h)[d]
            if c is None or c in occ:
                opts.append(None)
            else:
                opts.append(c)
        thr = [[False] * 4 for _ in range(4)]  # per option: bot, bot+1, true, pearl
        st = [False] * 4
        for d2, eh, EL, v in ens:
            models = (
                (reach(max(v, 2)), inview - {eh}, None),
                (reach(max(v + 1, 2)), inview - {eh}, None),
                (reach(EL), occ - {tail, eh}, None),
                (reach(EL), occ - {tail, eh}, g.pearls),
            )
            for mi, (R, blocked, pearls) in enumerate(models):
                R = min(R, 14)
                cost = flood(b, eh, R, blocked, pearls)
                a0 = arrive(b, cost, h)
                if a0 is not None and a0 <= R:
                    st[mi] = True
                for d in range(4):
                    if opts[d] is None:
                        continue
                    a = arrive(b, cost, opts[d])
                    if a is not None and a <= R:
                        thr[d][mi] = True
        first = g.act_dirs[0] if (kind == 0 and g.act_dirs) else None
        self.pending = dict(r=g.round, L=L, kind=kind, n=nsteps, first=first, free=[o is not None for o in opts], thr=thr,
                            start=st, ens=[[e[0], e[2], e[3]] for e in ens], rammed=False, pearl=[bool(o is not None and o in g.pearls) for o in opts],
                            killer_vis=None, killer_L=None)
        self.turns.append(self.pending)

    def death(self, g, did, reason, length, body, actor):
        side = g.teams[did]
        if side == self.side and did == self.q[side] and reason == "headon" and actor is not None and actor != did \
                and g.teams.get(actor) != side:
            p = self.turns[-1] if self.turns and self.turns[-1]["r"] == g.round else None
            if p is not None:
                p["rammed"] = True
                p["killer_seen"] = actor in self.seen
                for e in p["ens"]:
                    if e[0] == actor:
                        p["killer_L"], p["killer_vis"] = e[1], e[2]


def one(job):
    gid, path, side, meta = job
    g = lib.Walk(path)
    h = H(g, side)
    g.run(h)
    for t in h.turns:
        t["gid"] = gid
        t.update(meta)
    return h.turns


def main():
    os.nice(10)
    gs = [g for g in X.games() if X.is_csv(g)]
    jobs = []
    for g in gs:
        side = X.side_of(g, X.ME)
        if side and X.in_study(g, side):
            jobs.append((g["gid"], g["path"], side, dict(cells=g["cells"], live=X.build(g) == "live")))
    allt = []
    with Pool(5) as pool:
        for res in pool.imap_unordered(one, jobs, chunksize=4):
            allt += res
    json.dump(allt, open("x_out/c2vis.json", "w"))
    print("games", len(jobs), "queen turns with an enemy head in view", len(allt))


if __name__ == "__main__":
    main()
