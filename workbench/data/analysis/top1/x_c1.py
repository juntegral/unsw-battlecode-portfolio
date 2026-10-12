#!/usr/bin/env python3
"""Red-team recount for candidate 1 ("take the queen"). Own code; uses only lib.py (the replay walker).

For every game in x_out/games.json and BOTH sides it records
  - every turn of a non-queen dragon that starts with the enemy queen's head inside its 7x7 view (Chebyshev <= 3)
    or within its reach by wrapped Manhattan distance, with three path tests, the local head counts, the
    economy at that moment, what the dragon did, and whether it rammed her on that turn;
  - every queen death (round, reason, killer, killer's length and distance at the start of its turn);
  - a timeline every 10 rounds (units, total length, longest dragon, longest non-queen, queen length);
  - the end state (queens alive, the three longest dragons of each side) and the fate of every dragon that had a chance.

Path tests (all respect kelp, portals and the wrap; the target is the queen's head cell):
  dW  walls only: bodies ignored.
  dS  strict: every cell occupied by any dragon segment at the start of the turn is blocked (the attacker's own
      body included). This is what the bot's own search does (enter_time != 0 blocks).
  dV  strict AND every cell stepped on is inside the attacker's own 7x7 view (nothing has to be guessed).
A value of None means no such path within the dragon's reach = ceil(L/4) + (L-2).

Usage: python3 x_c1.py [--force] [--only gid,gid,...]     -> x_out/c1/<gid>.json
"""
import json
import math
import os
import sys
from collections import deque
from multiprocessing import Pool

import lib

OUT = "x_out/c1"


def reach(length):
    return math.ceil(length / 4) + max(0, length - 2)


def path_len(board, src, dst, limit, blocked, view_of=None):
    """Steps of the shortest path src -> dst (dst may be occupied: it is the target head). None if > limit."""
    if src == dst:
        return 0
    dist = {src: 0}
    q = deque([src])
    while q:
        c = q.popleft()
        dc = dist[c]
        if dc >= limit:
            continue
        for n in board.nb(c):
            if n is None or n in dist:
                continue
            if n == dst:
                return dc + 1
            if n in blocked:
                continue
            if view_of is not None and board.cheb(view_of, n) > 3:
                continue
            dist[n] = dc + 1
            q.append(n)
    return None


class H(lib.Hooks):
    def __init__(self, g):
        b = g.board
        self.q = dict(b.queen)
        self.qalive = {"A": True, "B": True}
        self.qdeath = {}
        self.chances = []
        self.pending = None
        self.timeline = []
        self.died = {}
        self.born = {}
        self.end_info = None
        self.near = {"A": 0, "B": 0}

    # ---- helpers
    def team_stats(self, g):
        st = {s: [0, 0, 0, 0, 0] for s in "AB"}  # units, total, longest, longest non-queen, queen length
        for d, body in g.bodies.items():
            s = g.teams[d]
            L = len(body)
            a = st[s]
            a[0] += 1
            a[1] += L
            if L > a[2]:
                a[2] = L
            if d == self.q[s]:
                a[4] = L
            elif L > a[3]:
                a[3] = L
        return st

    def finalize(self, g):
        p = self.pending
        if p is None:
            return
        self.pending = None
        if p.get("_full"):
            body = g.bodies.get(p["a"])
            if body is not None:
                p["endL"] = len(body)
                p["end_cheb"] = g.board.cheb(body[0], tuple(p["_qh"]))
                p["end_manh"] = g.board.manhattan(body[0], tuple(p["_qh"]))
        p.pop("_qh", None)
        p.pop("_full", None)
        self.chances.append(p)

    # ---- hooks
    def round_start(self, g, r):
        self.finalize(g)
        if r % 10 == 0:
            st = self.team_stats(g)
            self.timeline.append([r] + st["A"] + st["B"])

    def action(self, g, did, kind, nsteps):
        self.finalize(g)
        side = g.teams.get(did)
        if side is None or did == self.q[side]:
            return
        es = "B" if side == "A" else "A"
        if not self.qalive[es]:
            return
        qbody = g.bodies.get(self.q[es])
        if not qbody:
            return
        body = g.bodies[did]
        b = g.board
        h, qh = body[0], qbody[0]
        L = len(body)
        R = reach(L)
        ch = b.cheb(h, qh)
        mh = b.manhattan(h, qh)
        if ch > 3 and mh > R:
            return
        occ = set()
        for bd in g.bodies.values():
            occ.update(bd)
        dS = path_len(b, h, qh, R, occ)
        dV = path_len(b, h, qh, R, occ, view_of=h) if ch <= 3 else None
        dW = path_len(b, h, qh, R, ())
        if dS is None and dW is None:
            self.near[side] += 1  # in view (or in Manhattan reach) but no path within reach: only counted
            return
        # own-body-aware variant: the attacker's own segments free up as the tail advances (ignored: pearls, paid steps)
        own_h = en_h = 0
        en_small = 0
        for d2, bd in g.bodies.items():
            if d2 == did:
                continue
            if b.cheb(h, bd[0]) <= 3:
                if g.teams[d2] == side:
                    own_h += 1
                else:
                    en_h += 1
                    if len(bd) <= 4:
                        en_small += 1
        st = self.team_stats(g)
        own, en = st[side], st[es]
        longer = sum(1 for d2, bd in g.bodies.items() if g.teams[d2] == side and len(bd) > L)
        oq = g.bodies.get(self.q[side])
        self.pending = dict(
            r=g.round, side=side, a=did, L=L, R=R, cheb=ch, manh=mh, dS=dS, dV=dV, dW=dW,
            kind=kind, n=nsteps, own_h=own_h, en_h=en_h, en_small=en_small, qL=len(qbody),
            oq=len(oq) if oq else 0, longer=longer, own=own, en=en, taken=False, died=None, ate=0,
            _qh=list(qh), _full=True)

    def moved(self, g, did, head, step_index, ate):
        p = self.pending
        if p is not None and p["a"] == did and ate:
            p["ate"] += 1

    def split(self, g, parent, child, before, plen, clen):
        self.born[child] = [g.round, parent, clen]

    def death(self, g, did, reason, length, body, actor):
        self.died[did] = [g.round, reason, length, actor]
        side = g.teams[did]
        p = self.pending
        if p is not None and p["a"] == did:
            p["died"] = reason
        if did == self.q[side]:
            self.qalive[side] = False
            info = dict(r=g.round, reason=reason, L=length, actor=actor)
            if actor is not None and actor != did:
                info["actor_team"] = g.teams.get(actor)
                if g.act_start:
                    info["actor_L"] = g.act_start[1]
                    info["actor_cheb"] = g.board.cheb(g.act_start[0], body[0])
                    info["actor_manh"] = g.board.manhattan(g.act_start[0], body[0])
                info["actor_steps"] = g.act_steps
            elif actor == did:
                info["own_move"] = True
            self.qdeath[side] = info
            if reason == "headon" and actor is not None and actor != did:
                if p is not None and p["a"] == actor and p["side"] != side:
                    p["taken"] = True
                elif g.teams.get(actor) != side:
                    # a ram from outside view and outside Manhattan reach (portal) - keep a minimal record
                    self.chances.append(dict(r=g.round, side=g.teams.get(actor), a=actor,
                                             L=g.act_start[1] if g.act_start else None, far=True, taken=True,
                                             cheb=info.get("actor_cheb"), manh=info.get("actor_manh")))

    def end(self, g, rounds, winner, result):
        self.finalize(g)
        st = self.team_stats(g)
        tops = {s: [] for s in "AB"}
        for d, body in g.bodies.items():
            tops[g.teams[d]].append([len(body), d])
        for s in "AB":
            tops[s].sort(reverse=True)
            tops[s] = tops[s][:4]
        self.end_info = dict(rounds=rounds, winner=winner, st=st, tops=tops,
                             qalive={s: self.q[s] in g.bodies for s in "AB"})
        for c in self.chances:
            a = c["a"]
            if a in self.died:
                c["a_death"] = self.died[a][:3]
            elif a in g.bodies:
                c["a_final"] = len(g.bodies[a])
            if a in self.born:
                c["a_born"] = self.born[a]


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
        rec = dict(gid=gid, map=b.name, w=b.w, h=b.h, q=h.q, chances=h.chances, qdeath=h.qdeath,
                   timeline=h.timeline, end=h.end_info, portals=len(b.portal_pair) // 2, near=h.near)
        tmp = out + ".tmp"
        json.dump(rec, open(tmp, "w"))
        os.replace(tmp, out)
        return gid, "ok"
    except Exception as e:  # noqa
        return gid, "ERR %r" % (e,)


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
