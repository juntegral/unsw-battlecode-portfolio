#!/usr/bin/env python3
"""Walk 1 of sub-session C2: one pass over every study game, both sides. My own counting code (uses lib.py only).

Writes y_out/w1/<game_id>.json with:
  meta      game id, map, cells, rounds, winner side, team ids
  snap      every 5 rounds from round 100 (and 50, and "end"): per side
            [units, total length, longest id, longest len, second len, potential, potential within 15 cells of
             the longest's head, own units within 15 cells, queen alive, queen length]
  qdeath    round each queen died (or None)
  born      child id -> [round, parent, length before, parent keeps, child gets]   (every split)
  team      dragon id -> side
  lsplit    splits of a dragon of 6+: [round, parent, child, before, parent keeps, child gets, side,
            free cells next to the parent's head when it gave the order, longest OTHER own dragon then, seq in round]
  deaths    from round 100: [round, id, side, reason, length, hx, hy, actor, free cells next to its head when it gave
            its order (-1: died on another dragon's turn), longest other own dragon: id, len, path steps to its head
            (-1: over 8), own heads within 8 path steps [[id, len, steps], ...], cells to nearest enemy head]
  ceat      corpse pearls eaten: [round, eater id, dead id]
  nat       natural pearls eaten: "id:bin25" -> n ; natlead[side][bin25] by the side's longest of that round;
            natcls[side][bin25] = [by 2-4, by 5-7, by 8+]
  final     per side: list of [length, id] at the end, longest first (top 6)

Usage: python3 y_w1.py [--test gid ...] | (no args: all study games, 5 workers)
"""
import math
import os
import sys
import time
from collections import deque
from multiprocessing import Pool

import lib
import y_lib as Y

SNAP_FROM = 100


def half(n):
    return (n + 1) // 2


class W1(lib.Hooks):
    def __init__(self, check=False):
        self.check = check
        self.occ = {}
        self.my = {}
        self.ready = False
        self.snap = {}
        self.qdeath = {"A": None, "B": None}
        self.born = {}
        self.lsplit = []
        self.deaths = []
        self.ceat = []
        self.nat = {}
        self.natlead = {"A": {}, "B": {}}
        self.natcls = {"A": {}, "B": {}}
        self.act_free = (-1, -1, -1)
        self.lead = {"A": (-1, 0), "B": (-1, 0)}
        self.seq = 0
        self.rounds = 0
        self.winner = None

    # ---- occupancy mirror -------------------------------------------------
    def _add(self, cells):
        occ = self.occ
        for c in cells:
            occ[c] = occ.get(c, 0) + 1

    def _rem(self, cells):
        occ = self.occ
        for c in cells:
            v = occ.get(c, 0) - 1
            if v <= 0:
                occ.pop(c, None)
            else:
                occ[c] = v

    def _init(self, g):
        self.occ = {}
        self.my = {}
        for d, b in g.bodies.items():
            self.my[d] = deque(b)
            self._add(b)
        self.ready = True

    def _verify(self, g):
        ref = {}
        for b in g.bodies.values():
            for c in b:
                ref[c] = ref.get(c, 0) + 1
        if ref != self.occ:
            diff = [(c, ref.get(c), self.occ.get(c)) for c in set(ref) | set(self.occ) if ref.get(c) != self.occ.get(c)]
            owners = {}
            for d, b in g.bodies.items():
                for c in b:
                    owners.setdefault(c, []).append(d)
            raise RuntimeError("occupancy mirror differs at round %d: %s owners %s" % (
                g.round, diff[:8], [(c, owners.get(c)) for c, _, _ in diff[:8]]))

    # ---- helpers -----------------------------------------------------------
    def _sides(self, g):
        """Per side: sorted list of (len, id) desc."""
        out = {"A": [], "B": []}
        teams = g.teams
        for d, b in g.bodies.items():
            out[teams[d]].append((len(b), d))
        for s in out:
            out[s].sort(key=lambda t: (-t[0], t[1]))
        return out

    def _snapshot(self, g, key, sides=None):
        if sides is None:
            sides = self._sides(g)
        b = g.board
        row = {}
        for s in "AB":
            lst = sides[s]
            if not lst:
                row[s] = [0, 0, -1, 0, 0, 0, 0, 0, 0, 0]
                continue
            L, lid = lst[0]
            second = lst[1][0] if len(lst) > 1 else 0
            total = sum(x[0] for x in lst)
            pot = L + sum(half(x[0]) for x in lst[1:])
            lh = g.bodies[lid][0]
            ploc = L
            nloc = 0
            for x in lst[1:]:
                if b.manhattan(g.bodies[x[1]][0], lh) <= 15:
                    ploc += half(x[0])
                    nloc += 1
            q = b.queen[s]
            qa = 1 if q in g.bodies else 0
            row[s] = [len(lst), total, lid, L, second, pot, ploc, nloc, qa, len(g.bodies[q]) if qa else 0]
        self.snap[key] = row

    # ---- hooks -------------------------------------------------------------
    def round_start(self, g, r):
        if not self.ready:
            self._init(g)
        self.seq = 0
        sides = self._sides(g)
        for s in "AB":
            self.lead[s] = (sides[s][0][1], sides[s][0][0]) if sides[s] else (-1, 0)
        if r == 50 or (r >= SNAP_FROM and r % 5 == 0):
            self._snapshot(g, str(r), sides)
            if self.check and r % 50 == 0:
                self._verify(g)

    def action(self, g, did, kind, nsteps):
        if not self.ready:
            self._init(g)
        body = g.bodies.get(did)
        if not body:
            return
        occ = self.occ
        n = 0
        for c in g.board.nb(body[0]):
            if c is not None and c not in occ:
                n += 1
        self.act_free = (g.round, did, n)

    def moved(self, g, did, head, step_index, ate):
        if not self.ready:
            return  # placement events before round 0
        m = self.my.get(did)
        body = g.bodies[did]
        if m is None:
            self.my[did] = deque(body)
            self._add(body)
            return
        if m[0] != head:
            m.appendleft(head)
            self.occ[head] = self.occ.get(head, 0) + 1
        n = len(body)
        while len(m) > n:
            c = m.pop()
            v = self.occ.get(c, 0) - 1
            if v <= 0:
                self.occ.pop(c, None)
            else:
                self.occ[c] = v

    def split(self, g, parent, child, before, plen, clen):
        old = self.my.get(parent)
        if old is not None:
            self._rem(old)
        pb, cb = g.bodies[parent], g.bodies[child]
        self.my[parent] = deque(pb)
        self.my[child] = deque(cb)
        self._add(pb)
        self._add(cb)
        r = g.round
        self.born[child] = [r, parent, before, plen, clen]
        if before >= 6:
            side = g.teams[parent]
            mx = 0
            for d, b in g.bodies.items():
                if d != parent and d != child and g.teams[d] == side and len(b) > mx:
                    mx = len(b)
            fr = self.act_free[2] if (self.act_free[0] == r and self.act_free[1] == parent) else -1
            self.lsplit.append([r, parent, child, before, plen, clen, side, fr, mx, self.seq])
            self.seq += 1

    def death(self, g, did, reason, length, body, actor):
        r = g.round
        side = g.teams[did]
        q = g.board.queen
        if did == q[side] and self.qdeath[side] is None:
            self.qdeath[side] = r
        if r >= SNAP_FROM:
            head = body[0]
            own_turn = (g.current == did)
            fr = self.act_free[2] if (own_turn and self.act_free[0] == r and self.act_free[1] == did) else -1
            lid, llen, dl = -1, 0, -1
            near = []
            en = 99
            b = g.board
            dist = b.bfs(head, 8) if reason != "headon" else None
            for d2, b2 in g.bodies.items():
                if d2 == did:
                    continue
                h2 = b2[0]
                if g.teams[d2] == side:
                    L2 = len(b2)
                    if L2 > llen or (L2 == llen and d2 < lid):
                        lid, llen = d2, L2
                    if dist is not None:
                        st = dist.get(h2)
                        if st is not None:
                            near.append([d2, L2, st])
                else:
                    m = b.manhattan(h2, head)
                    if m < en:
                        en = m
            if dist is not None and lid >= 0:
                st = dist.get(g.bodies[lid][0])
                dl = st if st is not None else -1
            near.sort(key=lambda t: (t[2], -t[1]))
            self.deaths.append([r, did, side, reason, length, head[0], head[1], actor if actor is not None else -1,
                                fr, lid, llen, dl, near[:12], en])
        old = self.my.pop(did, None)
        if old is not None:
            self._rem(old)

    def eat(self, g, did, cell, origin):
        r = g.round
        if origin[0] == "corpse":
            self.ceat.append([r, did, origin[2]])
        elif origin[0] == "natural":
            side = g.teams[did]
            bn = r // 25
            k = "%d:%d" % (did, bn)
            self.nat[k] = self.nat.get(k, 0) + 1
            if did == self.lead[side][0]:
                self.natlead[side][bn] = self.natlead[side].get(bn, 0) + 1
            L = g.act_start[1] if (g.current == did and g.act_start) else len(g.bodies[did])
            c = 0 if L <= 4 else (1 if L <= 7 else 2)
            row = self.natcls[side].setdefault(bn, [0, 0, 0])
            row[c] += 1

    def end(self, g, rounds, winner, result):
        self.rounds = rounds
        self.winner = winner
        self._snapshot(g, "end")
        sides = self._sides(g)
        self.final = {s: [[x[0], x[1]] for x in sides[s][:6]] for s in "AB"}
        if self.check:
            self._verify(g)


def run_game(g, check=False):
    h = W1(check)
    w = lib.Walk(g["replay_path"])
    w.run(h)
    out = dict(
        gid=g["game_id"], map=g["map"], cells=int(g["cells"]), w=w.board.w, h=w.board.h, rounds=h.rounds,
        winner=h.winner, A=g["teamAId"], B=g["teamBId"], battle=g["battle_id"],
        queen=w.board.queen, snap=h.snap, qdeath=h.qdeath, born=h.born,
        team={str(d): t for d, t in w.teams.items()}, lsplit=h.lsplit, deaths=h.deaths, ceat=h.ceat,
        nat=h.nat, natlead=h.natlead, natcls=h.natcls, final=h.final)
    return out


def work(g):
    try:
        os.nice(0)
        p = Y.out_path("w1", g["game_id"] + ".json")
        if os.path.exists(p):
            return (g["game_id"], "skip")
        Y.dump(run_game(g), "w1", g["game_id"] + ".json")
        return (g["game_id"], "ok")
    except Exception as e:  # noqa: BLE001
        return (g["game_id"], "ERR %r" % (e,))


def main():
    games = Y.load_games()
    if len(sys.argv) > 2 and sys.argv[1] == "--test":
        G = {g["game_id"]: g for g in games}
        for gid in sys.argv[2:]:
            t = time.time()
            o = run_game(G[gid], check=True)
            print(gid, o["map"], "rounds", o["rounds"], "winner", o["winner"], "time %.2f" % (time.time() - t))
            print(" snap300", o["snap"].get("300"), "snap400", o["snap"].get("400"), "end", o["snap"]["end"])
            print(" qdeath", o["qdeath"], "final", o["final"])
            print(" lsplit", len(o["lsplit"]), o["lsplit"][-5:])
            print(" deaths", len(o["deaths"]), o["deaths"][-4:])
            print(" ceat", len(o["ceat"]), "nat keys", len(o["nat"]), "natlead", o["natlead"]["A"])
        return
    todo = [g for g in games if Y.study_sides(g)]
    print("games to walk:", len(todo), flush=True)
    os.nice(10)
    t = time.time()
    n = 0
    errs = 0
    with Pool(5) as pool:
        for gid, st in pool.imap_unordered(work, todo, chunksize=4):
            n += 1
            if st.startswith("ERR"):
                errs += 1
                print(gid, st, flush=True)
            if n % 100 == 0:
                print("done %d of %d, %.0fs, errors %d" % (n, len(todo), time.time() - t, errs), flush=True)
    print("finished %d games in %.0fs, errors %d" % (n, time.time() - t, errs), flush=True)


if __name__ == "__main__":
    main()
