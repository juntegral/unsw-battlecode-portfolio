#!/usr/bin/env python3
"""Independent recount of the headline numbers (approaches to the enemy queen and how they end), written separately
from extract.py and run straight from the replays, for: every large-map game of ours (not Schooltime) and every
large-map game between two of the top three. Prints the recount next to the numbers stored in q/*.json.

Definition (same as the report): an approach starts when an enemy head is within 6 path-steps of a living queen at a
round start; it ends when that dragon dies, is more than 9 steps away at a round start, or the queen dies. It "ends
with her rammed" if that dragon's head-on is what killed the queen.
"""
import csv
import json
import os
from collections import defaultdict
from multiprocessing import Pool

import lib

TOP3 = {"306", "91", "264"}
HERE = os.path.dirname(os.path.abspath(__file__))


def lc(n):
    return "L2-3" if n <= 3 else "L4" if n == 4 else "L5-9" if n <= 9 else "L10+"


class R(lib.Hooks):
    def __init__(self):
        self.open = {"A": {}, "B": {}}       # victim side -> attacker id -> start length
        self.done = {"A": [], "B": []}       # victim side -> (start length, killed queen?)
        self.qkill = {"A": None, "B": None}  # victim side -> killer id

    def round_start(self, g, r):
        b = g.board
        for s in "AB":
            q = g.bodies.get(b.queen[s])
            if q is None:
                for a, ln in self.open[s].items():
                    self.done[s].append((ln, self.qkill[s] == a))
                self.open[s] = {}
                continue
            dist = b.bfs(q[0], 9)
            for d, body in g.bodies.items():
                if g.teams[d] == s:
                    continue
                pd = dist.get(body[0])
                if pd is not None and pd <= 6 and d not in self.open[s]:
                    self.open[s][d] = len(body)
            for d in list(self.open[s]):
                body = g.bodies.get(d)
                if body is None:
                    self.done[s].append((self.open[s].pop(d), self.qkill[s] == d))
                elif body[0] not in dist:
                    self.done[s].append((self.open[s].pop(d), False))

    def death(self, g, did, reason, length, body, actor):
        s = g.teams[did]
        if did == g.board.queen[s] and reason == "headon" and actor is not None and actor != did and g.teams[actor] != s:
            self.qkill[s] = actor

    def end(self, g, rounds, winner, result):
        for s in "AB":
            for a, ln in self.open[s].items():
                self.done[s].append((ln, self.qkill[s] == a))


def work(row):
    x = R()
    lib.Walk(row["replay_path"]).run(x)
    out = {}
    for s in "AB":
        out[s] = dict(done=x.done[s], killed=x.qkill[s] is not None)
    return row["game_id"], out


def main():
    rows = []
    for g in csv.DictReader(open(os.path.join(HERE, "games.csv"))):
        if not g["map_size"].startswith("large") or g["map"] == "Schooltime":
            continue
        a, b = g["teamAId"], g["teamBId"]
        ours = "1119" in (a, b)
        top = a in TOP3 and b in TOP3
        if not (ours or top):
            continue
        o_elo = g["teamBElo"] if a == "1119" else g["teamAElo"]
        if ours and (not o_elo or float(o_elo) < 2000):
            continue
        rows.append(g)
    print("games to recount:", len(rows))
    res = {}
    with Pool(4) as pool:
        for gid, out in pool.imap_unordered(work, rows, chunksize=2):
            res[gid] = out
    new = defaultdict(lambda: [0, 0])
    old = defaultdict(lambda: [0, 0])
    kills_new = defaultdict(int)
    kills_old = defaultdict(int)
    ngames = defaultdict(int)
    for g in rows:
        gid = g["game_id"]
        qpath = os.path.join(HERE, "q", gid + ".json")
        if not os.path.exists(qpath):
            continue
        q = json.load(open(qpath))
        for s in "AB":              # s = victim side; attacker = other side
            o = "B" if s == "A" else "A"
            att = g[f"team{o}Id"]
            grp = "meow" if att == "1119" else "top three (vs top three)" if att in TOP3 and g[f"team{s}Id"] in TOP3 else None
            if grp is None:
                continue
            ngames[grp] += 1
            for ln, k in res[gid][s]["done"]:
                new[(grp, lc(ln))][0] += 1
                new[(grp, lc(ln))][1] += k
            kills_new[grp] += res[gid][s]["killed"]
            for ep in q["sides"][s]["episodes"]:
                old[(grp, lc(ep["len"]))][0] += 1
                old[(grp, lc(ep["len"]))][1] += ep["outcome"] == "it_rammed" and bool(ep.get("victim_queen"))
            qd = q["sides"][s]["qdeath"]
            kills_old[grp] += bool(qd and qd["reason"] == "headon" and qd["killer"] and qd["killer"]["team"] == o)
    for grp in ("meow", "top three (vs top three)"):
        print(f"\n{grp}: games {ngames[grp]}; rams on the enemy queen: recount {kills_new[grp]}, stored {kills_old[grp]}")
        for c in ("L2-3", "L4", "L5-9", "L10+"):
            a, b = new[(grp, c)], old[(grp, c)]
            print(f"  {c:5s} recount {a[1]:3d}/{a[0]:4d} = {a[1] / max(1, a[0]):.3f}   stored {b[1]:3d}/{b[0]:4d} = {b[1] / max(1, b[0]):.3f}")


if __name__ == "__main__":
    main()
