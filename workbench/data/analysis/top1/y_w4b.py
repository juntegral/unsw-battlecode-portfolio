#!/usr/bin/env python3
"""Walk 4b of sub-session C2: for every "no order" death of ours, how many segments of the dragon it died next to
were inside its own 7x7 view. Candidate 5 proposes "a feeder must count min(2 x its length, 6) segments of the
dragon it dies for"; this counts how many of today's deaths would pass that test.

Target = the longest own head inside the view and within 3 cells (the bot needs the head of the dragon in its
record in view within 3 cells; which id it holds is only known in readable games, see y_w4.py).
Writes y_out/w4b/<game_id>.json: rows [round, id, length, target id, target length, target segments in view,
target is the side's longest (1/0), path steps to the target's head (-1 over 12)]
"""
import os
import sys
from multiprocessing import Pool

import lib
import y_lib as Y


class W4b(lib.Hooks):
    def __init__(self, me):
        self.me = me
        self.rows = []

    def death(self, g, did, reason, length, body, actor):
        if reason != "noaction" or g.teams[did] != self.me or g.round < 150:
            return
        b = g.board
        head = body[0]
        best = None
        mx = 0
        for d2, b2 in g.bodies.items():
            if d2 == did or g.teams[d2] != self.me:
                continue
            L2 = len(b2)
            if L2 > mx:
                mx = L2
            h2 = b2[0]
            if b.cheb(h2, head) <= 3 and b.manhattan(h2, head) <= 3 and (best is None or L2 > best[1]):
                best = (d2, L2)
        if best is None:
            self.rows.append([g.round, did, length, -1, 0, 0, 0, -1])
            return
        tb = g.bodies[best[0]]
        vis = sum(1 for c in tb if b.cheb(c, head) <= 3)
        dist = b.bfs(head, 12)
        self.rows.append([g.round, did, length, best[0], best[1], vis, 1 if best[1] >= mx else 0, dist.get(tb[0], -1)])


def work(g):
    try:
        p = Y.out_path("w4b", g["game_id"] + ".json")
        if os.path.exists(p):
            return "skip"
        me = Y.side_of(g, Y.ME)
        h = W4b(me)
        lib.Walk(g["replay_path"]).run(h)
        Y.dump(dict(gid=g["game_id"], me=me, rows=h.rows), "w4b", g["game_id"] + ".json")
        return "ok"
    except Exception as e:  # noqa: BLE001
        return "ERR %r" % (e,)


if __name__ == "__main__":
    games = [g for g in Y.load_games() if any(t == Y.ME for t, s in Y.study_sides(g))]
    os.nice(10)
    with Pool(3) as pool:
        res = pool.map(work, games, chunksize=4)
    print("done", len(res), "errors", sum(1 for r in res if r.startswith("ERR")))
