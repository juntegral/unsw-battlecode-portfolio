#!/usr/bin/env python3
"""Candidate 3, a test of the mechanism: does the eating rate step at 9 cells from a longer own dragon?

Our code's leader zone is "within 9 cells (wrapped Manhattan distance) of the leader's last known head".  If that
zone is what stops our small dragons from eating, the share of free pearls taken should be low up to 9 cells from
the nearest LONGER own dragon and jump beyond it; teams without such a rule should show no step.

Turn counted as in h_c3.py part A (a non-queen dragon of 2-3 moves, no enemy head in its view, a pearl on a free cell
next to its head with a way on behind it), after our switch round only (150 on maps over 1,200 cells, else 300), up to
round 399.  Bucket = distance from the pearl to the head of the nearest own dragon that is longer than the mover:
0-3, 4-6, 7-9, 10-12, 13-16, 17+ or none on the board.
Walks our 401 games (both sides).  Usage: python3 h_c3dist.py run -> h_out/c3dist.json ; table -> stdout
"""
import csv
import json
import os
import sys
from collections import Counter
from multiprocessing import Pool

import lib

OUT = "h_out/c3dist.json"
BUCKETS = [(0, 3), (4, 6), (7, 9), (10, 12), (13, 16), (17, 999)]


def bucket(d):
    if d is None:
        return "none"
    for lo, hi in BUCKETS:
        if lo <= d <= hi:
            return f"{lo}-{hi}" if hi < 999 else f"{lo}+"


class H(lib.Hooks):
    def __init__(self, cells):
        self.grow = 150 if cells > 1200 else 300
        self.tab = Counter()
        self.pend = None

    def close(self):
        p = self.pend
        self.pend = None
        if p:
            side, bk, cands, first = p
            self.tab[(side, bk, int(first in cands))] += 1

    def round_start(self, g, r):
        self.close()

    def action(self, g, did, kind, nsteps):
        self.close()
        if not (self.grow <= g.round < 400) or kind != 0:
            return
        b = g.board
        s = g.teams[did]
        if did == b.queen[s]:
            return
        body = g.bodies[did]
        n = len(body)
        if n > 3:
            return
        head = body[0]
        occupied = set()
        longer = []
        for d2, other in g.bodies.items():
            occupied.update(other)
            if d2 == did:
                continue
            if g.teams[d2] != s:
                if b.cheb(other[0], head) <= 3:
                    return
            elif len(other) > n:
                longer.append(other[0])
        cands = [c for c in b.nb(head) if c is not None and c not in occupied and c in g.pearls
                 and any(m is not None and m != head and m not in occupied for m in b.nb(c))]
        if not cands:
            return
        dmin = None
        for c in cands:
            for h2 in longer:
                d = b.manhattan(h2, c)
                if dmin is None or d < dmin:
                    dmin = d
        self.pend = (s, bucket(dmin), cands, b.step(head, g.act_dirs[0]) if g.act_dirs else None)

    def end(self, g, rounds, winner, result):
        self.close()


def work(job):
    gid, path, cells = job
    h = H(cells)
    lib.Walk(path).run(h)
    return gid, [list(k) + [v] for k, v in h.tab.items()]


def run():
    rows = [r for r in csv.DictReader(open("games.csv")) if r["map"] != "Schooltime"]
    jobs = []
    for r in rows:
        ea, eb = float(r["teamAElo"] or 0), float(r["teamBElo"] or 0)
        if (r["teamAId"] == "1119" and eb >= 2000) or (r["teamBId"] == "1119" and ea >= 2000):
            jobs.append((r["game_id"], r["replay_path"], int(r["cells"])))
    out = {}
    with Pool(4) as pool:
        for i, (gid, res) in enumerate(pool.imap_unordered(work, jobs, chunksize=4)):
            out[gid] = res
            if (i + 1) % 100 == 0:
                print(i + 1, "/", len(jobs), flush=True)
    json.dump(out, open(OUT, "w"), separators=(",", ":"))


def table():
    rows = {r["game_id"]: r for r in csv.DictReader(open("games.csv"))}
    data = json.load(open(OUT))
    T = Counter()
    for gid, tab in data.items():
        r = rows[gid]
        me = "A" if r["teamAId"] == "1119" else "B"
        cls = "over 1,200 cells" if int(r["cells"]) > 1200 else "1,200 cells or fewer"
        live = r["battle_id"].startswith("dl-") or r["battle_id"].endswith("-old")
        for side, bk, ate, v in tab:
            who = ("meow live" if live else "meow candidates") if side == me else "opponents"
            T[(cls, who, bk, "n")] += v
            T[(cls, who, bk, "ate")] += v * ate
    order = [f"{lo}-{hi}" if hi < 999 else f"{lo}+" for lo, hi in BUCKETS] + ["none"]
    for cls in ("over 1,200 cells", "1,200 cells or fewer"):
        print(f"\n== maps of {cls}: a 2-3-long takes the free pearl next to it, after our switch round, by the distance from the pearl to the nearest LONGER own dragon's head ==")
        print("   " + " | ".join(f"{o:>14s}" for o in ["group"] + order))
        for who in ("meow live", "meow candidates", "opponents"):
            cells_ = []
            for bk in order:
                n, a = T[(cls, who, bk, "n")], T[(cls, who, bk, "ate")]
                cells_.append(f"{100 * a / n:3.0f}% of {n:5d}" if n else "      -      ")
            print(f"   {who:>14s} | " + " | ".join(cells_))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        try:
            os.nice(10)
        except OSError:
            pass
        run()
    else:
        table()
