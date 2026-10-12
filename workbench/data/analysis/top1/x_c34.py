#!/usr/bin/env python3
"""Red-team recount for candidates 3 ("no leader before its time") and 4 ("do not give way at contact").
Own code; uses only lib.py. One pass per game, both sides. Version 2 (keeps its own occupancy and head index, so
that a 7x7 look-up costs 49 dictionary reads instead of a loop over every dragon).

Candidate 3, per (side, 10-round block):
  pearl turns  a non-queen dragon of 2-4 makes a MOVE, no enemy head is in its 7x7 view, and at least one pearl lies on
               a free neighbouring cell that has a further free neighbour (a way on). "taken" = its first step lands on
               such a pearl. Keyed also by its length, by the Manhattan distance from the pearl to the nearest LONGER
               own dragon's head (the possible "leader"), and by that dragon's length.
  turns/splits dragon-turns and splits by length class (2-3 / 4 / 5-9 / 10+), non-queens.
  eaten        natural and corpse pearls eaten, by eater class (2-4 / 5+ / queen).
Candidate 4, per (side, phase 0-149 / 150-299 / 300+):
  ram chances  a non-queen dragon of 4 or shorter starts its turn with the head of an enemy non-queen dragon of 4 or
               shorter in its view and a path of free cells to it within its reach. One record per (turn, target):
               next cell or 2-3 steps, enemy longer / same / shorter, not outnumbered (other own heads in view >= enemy
               heads in view) or not, and whether it rammed THAT head this turn.
  rams         every head-on between two non-queen dragons of 4 or shorter: who started it, the same classes, both
               lengths, and who ate the pearls of the two corpses afterwards.
Usage: python3 x_c34.py [--force] [--only gid,...] [--check]   -> x_out/c34/<gid>.json
"""
import json
import math
import os
import sys
from collections import deque, Counter
from multiprocessing import Pool

import lib

OUT = "x_out/c34"
CHECK = False


def reach(length):
    return math.ceil(length / 4) + max(0, length - 2)


def path_len(board, src, dst, limit, blocked):
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
            dist[n] = dc + 1
            q.append(n)
    return None


def lcls(L):
    return "2-3" if L <= 3 else "4" if L == 4 else "5-9" if L <= 9 else "10+"


def dbucket(d):
    return 0 if d <= 3 else 1 if d <= 6 else 2 if d <= 9 else 3 if d <= 12 else 4 if d <= 16 else 5


class H(lib.Hooks):
    def __init__(self, g):
        b = g.board
        self.q = dict(b.queen)
        self.pearl = Counter()
        self.turns = Counter()
        self.splits = Counter()
        self.eaten = Counter()
        self.chance = Counter()
        self.rams = []
        self.ram_of = {}
        self.cur = None
        self._pending_ram = None
        # own occupancy and head index
        self.occ = set()
        self.copy = {}
        self.head_at = {}
        for d, bd in g.bodies.items():
            t = tuple(bd)
            self.copy[d] = t
            self.occ.update(t)
            self.head_at[t[0]] = d
        self._view = {}
        self.w, self.h = b.w, b.h

    # ---- bookkeeping
    def view(self, cell):
        v = self._view.get(cell)
        if v is None:
            x, y = cell
            w, h = self.w, self.h
            v = self._view[cell] = tuple(((x + dx) % w, (y + dy) % h) for dx in range(-3, 4) for dy in range(-3, 4)
                                         if dx or dy)
        return v

    def sync(self, g, did):
        new = g.bodies.get(did)
        old = self.copy.get(did)
        if old is not None:
            if self.head_at.get(old[0]) == did:
                del self.head_at[old[0]]
            for c in old:
                self.occ.discard(c)
        if new is None:
            self.copy.pop(did, None)
            return
        t = tuple(new)
        self.copy[did] = t
        self.occ.update(t)
        self.head_at[t[0]] = did

    def moved(self, g, did, head, step_index, ate):
        old = self.copy.get(did)
        new = g.bodies.get(did)
        if old is None or new is None:
            self.sync(g, did)
            return
        n = len(new)
        if len(old) >= n - 1 and n >= 2 and new[1] == old[0]:
            # the usual shift: one new head, zero to two cells dropped from the tail
            if self.head_at.get(old[0]) == did:
                del self.head_at[old[0]]
            for c in old[n - 1:]:
                self.occ.discard(c)
            self.occ.add(head)
            self.head_at[head] = did
            self.copy[did] = (head,) + old[:n - 1]
        else:
            self.sync(g, did)

    # ---- hooks
    def action(self, g, did, kind, nsteps):
        self._flush()
        self.cur = None
        self._pending_ram = None
        side = g.teams.get(did)
        if side is None:
            return
        b = g.board
        body = g.bodies[did]
        L = len(body)
        rb = g.round // 10
        if did == self.q[side]:
            return
        self.turns[(side, rb, lcls(L))] += 1
        if L > 4:
            return
        h = body[0]
        if CHECK and g.round % 50 == 0:
            occ2 = set()
            for bd in g.bodies.values():
                occ2.update(bd)
            assert occ2 == self.occ, (g.round, did, len(occ2 ^ self.occ))
            assert {bd[0]: d for d, bd in g.bodies.items()} == self.head_at
        es = "B" if side == "A" else "A"
        own_h = en_h = 0
        targets = []
        head_at = self.head_at
        teams = g.teams
        for c in self.view(h):
            d2 = head_at.get(c)
            if d2 is None:
                continue
            if teams[d2] == side:
                own_h += 1
            else:
                en_h += 1
                if d2 != self.q[es] and len(g.bodies[d2]) <= 4:
                    targets.append(d2)
        occ = self.occ
        if en_h == 0:
            # ---- candidate 3: a free pearl on the next cell
            if kind != 0:
                return
            nbs = b.nb(h)
            pearls = g.pearls
            good = []
            for d in range(4):
                c = nbs[d]
                if c is None or c not in pearls or c in occ:
                    continue
                for n in b.nb(c):
                    if n is not None and n != h and n not in occ:
                        good.append((d, c))
                        break
            if not good:
                return
            first = g.act_dirs[0] if g.act_dirs else None
            taken = any(d == first for d, c in good)
            pc = next((c for d, c in good if d == first), good[0][1])
            best = None
            for d2, bd in g.bodies.items():
                if d2 == did or teams[d2] != side or len(bd) <= L:
                    continue
                dist = b.manhattan(pc, bd[0])
                if best is None or dist < best[0]:
                    best = (dist, len(bd))
            if best is None:
                key = (side, rb, L, 9, "none", int(taken))
            else:
                key = (side, rb, L, dbucket(best[0]), "3-4" if best[1] <= 4 else "5-9" if best[1] <= 9 else "10+", int(taken))
            self.pearl[key] += 1
            return
        if not targets:
            return
        # ---- candidate 4: reachable small enemy heads
        R = reach(L)
        notout = 1 if own_h >= en_h else 0
        phase = 0 if g.round < 150 else 1 if g.round < 300 else 2
        recs = {}
        for t in targets:
            tb = g.bodies[t]
            d = path_len(b, h, tb[0], R, occ)
            if d is None:
                continue
            TL = len(tb)
            rel = "longer" if TL > L else "same" if TL == L else "shorter"
            recs[t] = (side, phase, notout, rel, 1 if d == 1 else 2)
        self.cur = dict(did=did, recs=recs, L=L, notout=notout, own_h=own_h, en_h=en_h)

    def _flush(self, rammed=None):
        cur = self.cur
        if cur is None:
            return
        for t, key in cur["recs"].items():
            self.chance[key + (1 if t == rammed else 0,)] += 1
        cur["recs"] = {}

    def round_start(self, g, r):
        self._flush()
        self.cur = None

    def split(self, g, parent, child, before, plen, clen):
        self.sync(g, parent)
        self.sync(g, child)
        side = g.teams.get(parent)
        if side is not None and parent != self.q[side]:
            self.splits[(side, g.round // 10, lcls(before), min(clen, 9))] += 1

    def eat(self, g, did, cell, origin):
        side = g.teams.get(did)
        if side is None:
            return
        body = g.bodies.get(did)
        L = len(body) if body else 2
        cls = "queen" if did == self.q[side] else ("2-4" if L <= 5 else "5+")
        kind = "nat" if origin[0] == "natural" else "corpse"
        self.eaten[(side, g.round // 10, kind, cls)] += 1
        if origin[0] == "corpse" and origin[2] in self.ram_of:
            ram = self.rams[self.ram_of[origin[2]]]
            ram["eat_" + side] = ram.get("eat_" + side, 0) + 1

    def death(self, g, did, reason, length, body, actor):
        # occupancy first: the dead dragon leaves the board
        old = self.copy.pop(did, None)
        if old is not None:
            if self.head_at.get(old[0]) == did:
                del self.head_at[old[0]]
            for c in old:
                self.occ.discard(c)
        for c in body:
            self.occ.discard(c)
        if self.head_at.get(body[0]) == did:
            del self.head_at[body[0]]
        if reason != "headon" or actor is None:
            return
        side = g.teams[did]
        if actor != did:
            self._pending_ram = dict(r=g.round, victim=did, vL=length, vside=side, vq=(did == self.q[side]),
                                     side=g.teams.get(actor), sL0=g.act_start[1] if g.act_start else None,
                                     steps=g.act_steps)
            if self.cur is not None and self.cur["did"] == actor:
                self._flush(rammed=did)
            return
        ram = self._pending_ram
        self._pending_ram = None
        if ram is None:
            return
        ram["sL"] = length
        small = (ram["sL0"] or 99) <= 4 and ram["vL"] <= 4
        if small and not ram["vq"] and did != self.q[side] and ram["vside"] != side:
            cur = self.cur if (self.cur and self.cur["did"] == did) else None
            ram["notout"] = cur["notout"] if cur else None
            L0 = ram["sL0"]
            ram["rel"] = "longer" if ram["vL"] > L0 else "same" if ram["vL"] == L0 else "shorter"
            self.ram_of[did] = len(self.rams)
            self.ram_of[ram["victim"]] = len(self.rams)
            ram["attacker"] = did
            self.rams.append(ram)

    def end(self, g, rounds, winner, result):
        self._flush()


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

        def ser(c):
            return [[list(k), v] for k, v in c.items()]

        rec = dict(gid=gid, map=b.name, w=b.w, h=b.h, pearl=ser(h.pearl), turns=ser(h.turns), splits=ser(h.splits),
                   eaten=ser(h.eaten), chance=ser(h.chance), rams=h.rams, v=2)
        tmp = out + ".tmp"
        json.dump(rec, open(tmp, "w"))
        os.replace(tmp, out)
        return gid, "ok"
    except Exception as e:  # noqa
        import traceback
        return gid, "ERR %r %s" % (e, traceback.format_exc()[-500:])


def main():
    global CHECK
    os.nice(10)
    os.makedirs(OUT, exist_ok=True)
    force = "--force" in sys.argv
    CHECK = "--check" in sys.argv
    only = None
    if "--only" in sys.argv:
        only = {int(x) for x in sys.argv[sys.argv.index("--only") + 1].split(",")}
    games = json.load(open("x_out/games.json"))
    jobs = [(g["gid"], g["path"], force) for g in games if only is None or g["gid"] in only]
    n = dict(ok=0, skip=0, err=0)
    if CHECK:
        for j in jobs:
            print(one(j))
        return
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
