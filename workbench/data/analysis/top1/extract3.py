#!/usr/bin/env python3
"""Third pass: turn-level ram chances on the enemy queen.

At the start of every non-queen dragon's own turn (so after both queens have moved this round), if the enemy queen is
alive and close: is there a path of FREE cells from this dragon's head to her head, no longer than this dragon's
one-turn reach (ceil(L/4) + L - 2)? If yes, that turn is a "chance". It is "taken" if the dragon rams her that turn.
Free = no dragon segment on the cell at that moment (the mover's own body counts as blocked, which is slightly
conservative). Kelp, wrap and portals are respected. Dragons longer than 12 are skipped.

Writes q3v2/<game_id>.json: {"chances": [[round, side, id, length, steps, taken, her_length, is_longest, own_queen_alive, in_view]],
(q3/ holds the first version without the in_view flag; sub-session A used it.)
                           "kills_without_chance": n}
"""
import csv
import json
import os
import sys
from collections import deque
from multiprocessing import Pool
from pathlib import Path

import lib

OUT = Path(__file__).resolve().parent / "q3v2"


class X(lib.Hooks):
    def __init__(self):
        self.chances = []
        self.pending = {}
        self.unflagged = 0
        self.longest = {"A": None, "B": None}
        self.qbfs = {}

    def round_start(self, g, r):
        for s in "AB":
            best = None
            for d, body in g.bodies.items():
                if g.teams[d] == s and (best is None or len(body) > best[0]):
                    best = (len(body), d)
            self.longest[s] = best[1] if best else None

    def action(self, g, did, kind, nsteps):
        b = g.board
        s = g.teams[did]
        o = "B" if s == "A" else "A"
        self.pending.pop(did, None)
        if did == b.queen[s]:
            return
        q = g.bodies.get(b.queen[o])
        if q is None:
            return
        body = g.bodies[did]
        n = len(body)
        if n > 12:
            return
        rc = lib.reach(n)
        head, target = body[0], q[0]
        # exact prefilter: path distance ignoring bodies is a lower bound; cached per queen position
        cached = self.qbfs.get(o)
        if cached is None or cached[0] != target:
            cached = (target, b.bfs(target, 14))
            self.qbfs[o] = cached
        d0 = cached[1].get(head)
        if d0 is None or d0 > rc:
            return
        occupied = set()
        for d2, other in g.bodies.items():
            if d2 != did:
                occupied.update(other)
        own = {c: i for i, c in enumerate(body)}   # own segment index, 0 = head
        free = -(-n // 4)
        # BFS over free cells; reaching her head costs one more step. An own-body cell with segment index i has
        # been vacated by the tail once (steps done + paid steps done) >= n - i (the tail's cell is still blocked
        # for the step in which it would leave). Pearls eaten on the way are ignored.
        dist = {head: 0}
        dq = deque([head])
        found = None
        while dq and found is None:
            c = dq.popleft()
            dc = dist[c]
            if dc >= rc:
                continue
            for nb in b.nb(c):
                if nb is None:
                    continue
                if nb == target:
                    found = dc + 1
                    break
                if nb in dist or nb in occupied:
                    continue
                i = own.get(nb)
                if i is not None and dc + max(0, dc - free) < n - i:
                    continue
                dist[nb] = dc + 1
                dq.append(nb)
        if found is None:
            return
        own_q = b.queen[s] in g.bodies
        # in view = her head inside the 7x7 square around this dragon's head at its own turn
        inview = int(b.cheb(head, target) <= 3)
        rec = [g.round, s, did, n, found, 0, len(q), int(did == self.longest[s]), int(own_q), inview]
        self.chances.append(rec)
        self.pending[did] = rec

    def death(self, g, did, reason, length, body, actor):
        s = g.teams[did]
        if did == g.board.queen[s] and reason == "headon" and actor is not None and actor != did and g.teams[actor] != s:
            rec = self.pending.get(actor)
            if rec is not None:
                rec[5] = 1
            else:
                self.unflagged += 1


def work(row):
    out = OUT / (row["game_id"] + ".json")
    try:
        if out.exists():
            return row["game_id"], None
        x = X()
        lib.Walk(row["replay_path"]).run(x)
        tmp = out.with_suffix(".tmp%d" % os.getpid())
        tmp.write_text(json.dumps(dict(game_id=int(row["game_id"]), chances=x.chances, kills_without_chance=x.unflagged),
                                  separators=(",", ":")))
        tmp.replace(out)
        return row["game_id"], None
    except Exception as exc:  # noqa: BLE001
        return row["game_id"], f"{type(exc).__name__}: {exc}"


def main():
    OUT.mkdir(exist_ok=True)
    try:
        os.nice(10)
    except OSError:
        pass
    rows = list(csv.DictReader(open(Path(__file__).resolve().parent / "games.csv")))
    if "--only" in sys.argv:
        ids = set(sys.argv[sys.argv.index("--only") + 1].split(","))
        rows = [r for r in rows if r["game_id"] in ids]
    done = 0
    errors = []
    with Pool(4) as pool:
        for gid, err in pool.imap_unordered(work, rows, chunksize=4):
            done += 1
            if err:
                errors.append((gid, err))
            if done % 200 == 0:
                print(f"{done}/{len(rows)} errors {len(errors)}", flush=True)
    print(f"done {done} errors {len(errors)}", errors[:5])


if __name__ == "__main__":
    main()
