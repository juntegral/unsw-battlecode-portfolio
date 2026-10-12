#!/usr/bin/env python3
"""Walk 4 of sub-session C2: every death of one of OUR dragons by the "no order" rule (that is how our feeders die),
with what stood next to it and, where the pings are readable, which leader it named one turn before.

My own counting code (occupancy mirror from y_w1.py, ping FORMAT as documented in e_belief.py; no key).
Writes y_out/w4/<game_id>.json: rows
 [round, id, length, free cells next to its head,
  named id, named length, named round (or -1 x3 when the pings are sealed or it sent none),
  named dragon: true length now (0 dead), cells to its head, path steps (-1 over 12), in the 7x7 view (0/1),
  true longest other own dragon: id, length, cells, path steps,
  the longest own head inside the view AND within 3 cells: id, length, cells, path steps (-1s if none),
  own heads in view, cells to the nearest enemy head]
Usage: python3 y_w4.py [--test gid ...]
"""
import os
import sys
import time
from multiprocessing import Pool

import lib
import y_lib as Y
import y_w1
from y_w2 import decode


class W4(y_w1.W1):
    def __init__(self, me_side):
        super().__init__(False)
        self.me = me_side
        self.tag = {"A": 2, "B": 1}[me_side]
        self.ping = [0, 0]
        self.belnow = {}
        self.belprev = {}
        self.rows = []

    def sonar(self, g, sender, value, raw):
        if g.teams.get(sender) != self.me:
            return
        m = decode(value)
        if m is None:
            return
        self.ping[0] += 1
        lid, ln, when, x, y, tag = m
        b = g.board
        if not (tag == self.tag and g.teams.get(lid) == self.me and 0 <= g.round - when <= 25 and 1 <= ln <= b.w * b.h
                and x < b.w and y < b.h):
            return
        self.ping[1] += 1
        self.belnow[sender] = (lid, ln, when, x, y)

    def round_start(self, g, r):
        super().round_start(g, r)
        self.belprev = self.belnow
        self.belnow = {}

    def death(self, g, did, reason, length, body, actor):
        if reason == "noaction" and g.teams[did] == self.me and g.round >= 150:
            r = g.round
            b = g.board
            head = body[0]
            fr = self.act_free[2] if (self.act_free[0] == r and self.act_free[1] == did) else -1
            dist = b.bfs(head, 12)
            bodies = g.bodies
            bel = self.belprev.get(did)
            if bel is None:
                bel = self.belnow.get(did)
            row = [r, did, length, fr]
            if bel is None:
                row += [-1, -1, -1, -1, -1, -1, -1]
            else:
                lid = bel[0]
                if lid in bodies and lid != did:
                    h2 = bodies[lid][0]
                    row += [lid, bel[1], bel[2], len(bodies[lid]), b.manhattan(h2, head), dist.get(h2, -1),
                            1 if b.cheb(h2, head) <= 3 else 0]
                else:
                    row += [lid, bel[1], bel[2], 0 if lid != did else length, -1, -1, 0]
            tl, tll = -1, 0
            best = None
            nview = 0
            en = 99
            for d2, b2 in bodies.items():
                if d2 == did:
                    continue
                h2 = b2[0]
                if g.teams[d2] == self.me:
                    L2 = len(b2)
                    if L2 > tll:
                        tl, tll = d2, L2
                    if b.cheb(h2, head) <= 3:
                        nview += 1
                        m = b.manhattan(h2, head)
                        if m <= 3 and (best is None or L2 > best[1]):
                            best = (d2, L2, m, dist.get(h2, -1))
                else:
                    m = b.manhattan(h2, head)
                    if m < en:
                        en = m
            if tl >= 0:
                h2 = bodies[tl][0]
                row += [tl, tll, b.manhattan(h2, head), dist.get(h2, -1)]
            else:
                row += [-1, 0, -1, -1]
            row += list(best) if best else [-1, 0, -1, -1]
            row += [nview, en]
            self.rows.append(row)
        super().death(g, did, reason, length, body, actor)


def run_game(g):
    me = Y.side_of(g, Y.ME)
    h = W4(me)
    lib.Walk(g["replay_path"]).run(h)
    return dict(gid=g["game_id"], me=me, ping=h.ping, rows=h.rows)


def work(g):
    try:
        p = Y.out_path("w4", g["game_id"] + ".json")
        if os.path.exists(p):
            return (g["game_id"], "skip")
        Y.dump(run_game(g), "w4", g["game_id"] + ".json")
        return (g["game_id"], "ok")
    except Exception as e:  # noqa: BLE001
        import traceback
        return (g["game_id"], "ERR %r %s" % (e, traceback.format_exc()[-300:]))


def main():
    games = Y.load_games()
    if len(sys.argv) > 2 and sys.argv[1] == "--test":
        G = {g["game_id"]: g for g in games}
        for gid in sys.argv[2:]:
            t = time.time()
            o = run_game(G[gid])
            print(gid, "ping", o["ping"], "rows", len(o["rows"]), "time %.2f" % (time.time() - t))
            for row in o["rows"][:12]:
                print("  ", row)
        return
    todo = [g for g in games if any(t == Y.ME for t, s in Y.study_sides(g))]
    print("games to walk:", len(todo), flush=True)
    os.nice(10)
    t = time.time()
    n = errs = 0
    with Pool(5) as pool:
        for gid, st in pool.imap_unordered(work, todo, chunksize=4):
            n += 1
            if st.startswith("ERR"):
                errs += 1
                print(gid, st, flush=True)
    print("finished %d games in %.0fs, errors %d" % (n, time.time() - t, errs), flush=True)


if __name__ == "__main__":
    main()
