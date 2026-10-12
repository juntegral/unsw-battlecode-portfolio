#!/usr/bin/env python3
"""Red-team recount for candidate 2 ("our queen is never spent"). Own code; uses only lib.py. Version 2.

For every game and BOTH queens it records every queen turn that starts with an enemy head in her 7x7 view
(Chebyshev <= 3) or with an enemy head near enough to reach her, every turn with no legal one-step move ("boxed in"),
every queen split, and her death.

Reach model. An enemy of length L can move its head onto a cell this round if a path of free cells leads there whose
k-th step satisfies  k - (pearls eaten on the earlier steps) <= ceil(L/4) + (L - 2):  every pearl eaten on the way
pays for one more step (seen in the replays: 13% of all rams on a queen use it). "Free" = no dragon segment on the
cell at that moment; for the options of her turn her own tail cell counts as free. Two versions are stored:
  plain  pearls ignored (what the bot's existing spread_kill()/queen_margin() compute)
  pearl  pearl-paid steps included (what the engine allows)
Per queen turn (board at the start of her turn):
  opts      the four one-step moves: 'kelp', 'body', 'head' (a ram), or
            ['free', pearl?, thr_plain_seen, thr_plain_any, room, portal?, thr_pearl_seen, thr_pearl_any]
            thr > 0 means some enemy (in her view / anywhere) can reach the cell; the value is margin + 1.
  start_*   the same for the cell she stands on (path to her head).
  end_*     measured on the REAL board right after her action, for the enemies that were in her view at the start
            (end_seen, endp_seen) or any enemy (end_any, endp_any).
Deaths are attached to the turn of the same round (reason, killer, whether the killer was in her view at her turn).
Also stored: can she herself reach the ENEMY queen's head this turn (eq_reach), for candidate 1's "our own queen
as attacker" count.

Usage: python3 x_c2.py [--force] [--only gid,...]   -> x_out/c2/<gid>.json
"""
import json
import math
import os
import sys
from collections import deque
from multiprocessing import Pool

import lib

OUT = "x_out/c2"
CAP = 14
INF = 999


def reach(length):
    return min(CAP, math.ceil(length / 4) + max(0, length - 2))


def flood(board, src, R, blocked, pearls=None):
    """Net cost (steps minus pearls eaten) of standing on each cell reachable from src. pearls=None: plain steps."""
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
                if nc == cc:
                    dq.appendleft(n)
                else:
                    dq.append(n)
    return cost


def arrive(board, cost, cell):
    """Cheapest arrival on `cell` (which may itself be blocked: a head): 1 + the best neighbour, None if none."""
    best = None
    for n in board.nb(cell):
        if n is not None and n in cost:
            v = cost[n] + 1
            if best is None or v < best:
                best = v
    return best


def room(board, src, blocked, cap=40, limit=8):
    seen = {src}
    q = deque([(src, 0)])
    while q and len(seen) < cap:
        c, d = q.popleft()
        if d >= limit:
            continue
        for n in board.nb(c):
            if n is None or n in seen or n in blocked:
                continue
            seen.add(n)
            q.append((n, d + 1))
    return len(seen)


class H(lib.Hooks):
    def __init__(self, g):
        b = g.board
        self.q = dict(b.queen)
        self.turns = []
        self.splits = []
        self.qdeath = {}
        self.pending = None
        self.qrounds = {"A": 0, "B": 0}
        self.qrounds_small = {"A": 0, "B": 0}
        self.view_rounds = {"A": 0, "B": 0}
        self.last_view = {"A": set(), "B": set()}
        self.eaten = {"A": [0, 0, 0, 0, 0], "B": [0, 0, 0, 0, 0]}
        self.eaten_nat = {"A": [0, 0, 0, 0, 0], "B": [0, 0, 0, 0, 0]}
        self.len100 = {"A": {}, "B": {}}
        self.final = None

    def settle(self, g):
        p = self.pending
        if p is None:
            return
        self.pending = None
        side = p["side"]
        qid = self.q[side]
        body = g.bodies.get(qid)
        if body is not None:
            b = g.board
            h = body[0]
            occ = set()
            for bd in g.bodies.values():
                occ.update(bd)
            es = "B" if side == "A" else "A"
            res = dict(end_seen=None, end_any=None, endp_seen=None, endp_any=None)
            who = None
            for d2, bd in g.bodies.items():
                if g.teams[d2] != es:
                    continue
                R = reach(len(bd))
                seen = d2 in p["_seen"]
                if b.manhattan(bd[0], h) > R + 4 and not seen:
                    continue
                blocked = occ - {bd[0]}
                for tag, pearls in (("end", None), ("endp", g.pearls)):
                    cost = flood(b, bd[0], R, blocked, pearls)
                    a = arrive(b, cost, h)
                    if a is not None and a <= R:
                        m = R - a
                        if res[tag + "_any"] is None or m > res[tag + "_any"]:
                            res[tag + "_any"] = m
                        if seen and (res[tag + "_seen"] is None or m > res[tag + "_seen"]):
                            res[tag + "_seen"] = m
                            if tag == "endp":
                                who = [d2, len(bd), a]
            p.update(res)
            p["end_who"] = who
            p["endL"] = len(body)
            p["end"] = list(h)
        p.pop("_seen", None)
        self.turns.append(p)

    def round_start(self, g, r):
        self.settle(g)
        if r % 100 == 0:
            for s in "AB":
                bd = g.bodies.get(self.q[s])
                self.len100[s][r] = len(bd) if bd else 0

    def action(self, g, did, kind, nsteps):
        self.settle(g)
        side = g.teams.get(did)
        if side is None or did != self.q[side]:
            return
        b = g.board
        body = g.bodies[did]
        h, L = body[0], len(body)
        es = "B" if side == "A" else "A"
        self.qrounds[side] += 1
        if L <= 3:
            self.qrounds_small[side] += 1
        occ = set()
        heads = {}
        for d2, bd in g.bodies.items():
            occ.update(bd)
            heads[bd[0]] = d2
        seen, near = [], []
        for d2, bd in g.bodies.items():
            if g.teams[d2] != es:
                continue
            ch = b.cheb(h, bd[0])
            if ch <= 3:
                seen.append(d2)
            elif b.manhattan(h, bd[0]) <= reach(len(bd)) + 3:
                near.append(d2)
        own_h = sum(1 for d2, bd in g.bodies.items() if g.teams[d2] == side and d2 != did and b.cheb(h, bd[0]) <= 3)
        own6 = sum(1 for d2, bd in g.bodies.items() if g.teams[d2] == side and d2 != did and b.manhattan(h, bd[0]) <= 6)
        self.last_view[side] = set(seen)
        if seen:
            self.view_rounds[side] += 1
        opts = []
        n_legal = 0
        tail = body[-1]
        for d in range(4):
            c = b.nb(h)[d]
            if c is None:
                opts.append(["kelp"])
            elif c in occ:
                if c in heads and heads[c] != did:
                    opts.append(["head", heads[c], g.teams[heads[c]] == es, len(g.bodies[heads[c]])])
                else:
                    opts.append(["body"])
            else:
                n_legal += 1
                opts.append(["free", 1 if c in g.pearls else 0])
        # can she reach the enemy queen's head herself this turn (plain reach, strict path)?
        eq = g.bodies.get(self.q[es])
        eq_reach = None
        if eq is not None and b.cheb(h, eq[0]) <= 3:
            cost = flood(b, h, reach(L), occ - {h})
            a = arrive(b, cost, eq[0])
            if a is not None and a <= reach(L):
                eq_reach = a
        if not seen and not near and n_legal > 0 and kind != 1 and eq_reach is None:
            return
        blocked_all = occ - {tail}
        thr = [[0, 0, 0, 0] for _ in range(4)]  # plain seen, plain any, pearl seen, pearl any
        start = dict(start_seen=None, start_any=None, startp_seen=None, startp_any=None)
        ens = []
        for d2 in seen + near:
            bd = g.bodies[d2]
            R = reach(len(bd))
            is_seen = d2 in seen
            blocked = blocked_all - {bd[0]}
            row = [d2, len(bd), b.cheb(h, bd[0]), None, 1 if is_seen else 0, 1 if d2 == self.q[es] else 0, None]
            for vi, pearls in ((0, None), (2, g.pearls)):
                cost = flood(b, bd[0], R, blocked, pearls)
                a0 = arrive(b, cost, h)
                tag = "start" if vi == 0 else "startp"
                row[3 if vi == 0 else 6] = a0
                if a0 is not None and a0 <= R:
                    if start[tag + "_any"] is None or R - a0 > start[tag + "_any"]:
                        start[tag + "_any"] = R - a0
                    if is_seen and (start[tag + "_seen"] is None or R - a0 > start[tag + "_seen"]):
                        start[tag + "_seen"] = R - a0
                for d in range(4):
                    if opts[d][0] != "free":
                        continue
                    c = b.nb(h)[d]
                    a = arrive(b, cost, c)
                    if a is not None and a <= R:
                        thr[d][vi + 1] = max(thr[d][vi + 1], R - a + 1)
                        if is_seen:
                            thr[d][vi] = max(thr[d][vi], R - a + 1)
            ens.append(row)
        for d in range(4):
            if opts[d][0] == "free":
                c = b.nb(h)[d]
                opts[d] += [thr[d][0], thr[d][1], room(b, c, blocked_all | {h}), 1 if b.manhattan(h, c) != 1 else 0,
                            thr[d][2], thr[d][3]]
        dirs = list(g.act_dirs)
        self.pending = dict(r=g.round, side=side, L=L, kind=kind, n=nsteps, dirs=dirs[:6], opts=opts, n_legal=n_legal,
                            seen=len(seen), near=len(near), ens=ens, own_h=own_h, own6=own6, ate=0, death=None,
                            _seen=set(seen), head=list(h), eq_reach=eq_reach, **start)

    def moved(self, g, did, head, step_index, ate):
        pass

    def eat(self, g, did, cell, origin):
        side = g.teams.get(did)
        if side is not None and did == self.q[side]:
            k = min(4, g.round // 100)
            self.eaten[side][k] += 1
            if origin[0] == "natural":
                self.eaten_nat[side][k] += 1
            p = self.pending
            if p is not None and p["side"] == side:
                p["ate"] += 1

    def split(self, g, parent, child, before, plen, clen):
        side = g.teams.get(parent)
        if side is not None and parent == self.q[side]:
            p = self.pending
            mine = p is not None and p["side"] == side
            self.splits.append(dict(r=g.round, side=side, L=before, keep=plen, child=clen,
                                    n_legal=p["n_legal"] if mine else None, seen=p["seen"] if mine else None, cid=child))

    def death(self, g, did, reason, length, body, actor):
        side = g.teams[did]
        if did != self.q[side]:
            return
        info = dict(r=g.round, reason=reason, L=length, actor=actor)
        if actor is not None and actor != did:
            info["actor_team"] = g.teams.get(actor)
            info["actor_L"] = g.act_start[1] if g.act_start else None
            info["actor_steps"] = g.act_steps
            info["actor_seen"] = actor in self.last_view[side]
            if g.act_start:
                info["actor_cheb"] = g.board.cheb(g.act_start[0], body[0])
        else:
            info["own_move"] = True
        self.qdeath[side] = info
        p = self.pending
        if p is not None and p["side"] == side and p["r"] == g.round:
            p["death"] = info
        else:
            for t in reversed(self.turns):
                if t["side"] == side:
                    if t["r"] == g.round:
                        t["death"] = info
                    break

    def end(self, g, rounds, winner, result):
        self.settle(g)
        self.final = dict(rounds=rounds, winner=winner,
                          qlen={s: (len(g.bodies[self.q[s]]) if self.q[s] in g.bodies else 0) for s in "AB"})


def one(job):
    gid, path, force = job
    out = os.path.join(OUT, "%d.json" % gid)
    if os.path.exists(out) and not force:
        return gid, "skip"
    try:
        g = lib.Walk(path)
        h = H(g)
        g.run(h)
        b = g.board
        rec = dict(gid=gid, map=b.name, w=b.w, h=b.h, q=h.q, turns=h.turns, splits=h.splits, qdeath=h.qdeath,
                   qrounds=h.qrounds, qrounds_small=h.qrounds_small, view_rounds=h.view_rounds, eaten=h.eaten,
                   eaten_nat=h.eaten_nat, len100=h.len100, final=h.final, portals=len(b.portal_pair) // 2, v=2)
        tmp = out + ".tmp"
        json.dump(rec, open(tmp, "w"))
        os.replace(tmp, out)
        return gid, "ok"
    except Exception as e:  # noqa
        import traceback
        return gid, "ERR %r %s" % (e, traceback.format_exc()[-300:])


def main():
    os.nice(10)
    os.makedirs(OUT, exist_ok=True)
    force = "--force" in sys.argv
    only = None
    if "--only" in sys.argv:
        only = {int(x) for x in sys.argv[sys.argv.index("--only") + 1].split(",")}
    games = json.load(open("x_out/games.json"))
    jobs = [(g["gid"], g["path"], force) for g in games if only is None or g["gid"] in only]
    n = dict(ok=0, skip=0, err=0)
    with Pool(5) as pool:
        for i, (gid, status) in enumerate(pool.imap_unordered(one, jobs, chunksize=4)):
            if status.startswith("ERR"):
                n["err"] += 1
                print(gid, status, flush=True)
            else:
                n[status] += 1
            if (i + 1) % 200 == 0:
                print(i + 1, "/", len(jobs), n, flush=True)
    print("done", n)


if __name__ == "__main__":
    main()
