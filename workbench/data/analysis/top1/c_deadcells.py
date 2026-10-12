#!/usr/bin/env python3
"""c_deadcells.py [per_map=12] [jobs=4] [upto=150]: early non-ram deaths with no free cell, by map and team, and whether a
team keeps dying on the same cells (all four teams; opponents rated 2000+; up to <per_map> games per team and map).

For each game and side, rounds 0..upto: every non-ram death; whether the head had a free neighbour cell; the cell.
Per map and team (the team's own side), and for "opponents of meow" (test4, WeHaveQuizzes in our games):
  games | non-ram deaths per game: boxed (no free cell) / with a free cell | segments lost per game in boxed deaths |
  different cells per game | share of boxed deaths on a cell where a team-mate had already died that way in this game |
  deaths per game on the most used cell | share of boxed deaths on a cell with 1 open side (dead-end cell) |
  share of boxed deaths where the cell held a pearl just before (the dragon ate there that turn or the turn before).
"""
import csv
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool

sys.dont_write_bytecode = True
import c_lib  # noqa: E402
from c_lib import Hooks2, Stop, Walk2  # noqa: E402

TOP = {306: "Vibing++", 91: "SSS", 264: "forgot", 1119: "meow"}
MAPS = ["Australia", "Islands", "Around UNSW", "Slithery Fight", "Trauma", "Maze", "weakhold", "Tower Defense", "Stripes", "Portals"]


class D(Hooks2):
    def __init__(self, upto):
        self.upto = upto
        self.d = {"A": [], "B": []}
        self.lasteat = {}

    def round_start(self, g, r):
        if r > self.upto:
            raise Stop

    def eat(self, g, did, cell, origin):
        self.lasteat[did] = (g.round, cell)

    def death(self, g, did, reason, length, body, actor):
        if reason == "headon":
            return
        b = g.board
        occ = c_lib.occupied(g)
        head = body[0]
        free = sum(1 for n in b.nb(head) if n is not None and n not in occ)
        le = self.lasteat.get(did)
        ate_here = le is not None and g.round - le[0] <= 1 and le[1] == head
        self.d[g.teams[did]].append((g.round, head, length, free, b.degree(head), ate_here))


def work(job):
    gid, path, upto = job
    d = D(upto)
    try:
        Walk2(path).run(d)
    except Stop:
        pass
    except Exception as e:  # noqa: BLE001
        return gid, None, repr(e)
    return gid, d.d, None


if __name__ == "__main__":
    nums = [a for a in sys.argv[1:] if a.isdigit()]
    per_map = int(nums[0]) if nums else 12
    jobs = int(nums[1]) if len(nums) > 1 else 4
    upto = int(nums[2]) if len(nums) > 2 else 150
    picked = defaultdict(list)
    meta = {}
    for g in csv.DictReader(open("games.csv")):
        if g["map"] not in MAPS:
            continue
        for s in "AB":
            o = "B" if s == "A" else "A"
            t = int(g[f"team{s}Id"])
            try:
                oelo = float(g[f"team{o}Elo"])
            except ValueError:
                oelo = 0
            if t in TOP and oelo >= 2000:
                picked[(g["map"], t)].append(g["game_id"])
        meta[g["game_id"]] = g
    todo = {}
    for (mp, t), ids in picked.items():
        ids = ids[:: max(1, len(ids) // per_map)][:per_map]
        for gid in ids:
            todo[gid] = (gid, meta[gid]["replay_path"], upto)
    res = {}
    with Pool(jobs) as pool:
        for gid, d, err in pool.imap_unordered(work, list(todo.values())):
            if err:
                print("error", gid, err)
                continue
            res[gid] = d
    agg = defaultdict(Counter)
    for gid, d in res.items():
        g = meta[gid]
        for s in "AB":
            o = "B" if s == "A" else "A"
            t, ot = int(g[f"team{s}Id"]), int(g[f"team{o}Id"])
            try:
                oelo = float(g[f"team{o}Elo"])
            except ValueError:
                oelo = 0
            cols = []
            if t in TOP and oelo >= 2000:
                cols.append(TOP[t])
            if ot == 1119 and t in (19, 87):
                cols.append("opponents of meow (test4, WHQ)")
            if not cols:
                continue
            boxed = [x for x in d[s] if x[3] == 0]
            free = [x for x in d[s] if x[3] > 0]
            cells = Counter(x[1] for x in boxed)
            seen = set()
            rep = 0
            for x in sorted(boxed):
                if x[1] in seen:
                    rep += 1
                seen.add(x[1])
            for c in cols:
                a = agg[(g["map"], c)]
                a["games"] += 1
                a["boxed"] += len(boxed)
                a["free"] += len(free)
                a["seg"] += sum(x[2] for x in boxed)
                a["cells"] += len(cells)
                a["rep"] += rep
                a["top"] += cells.most_common(1)[0][1] if cells else 0
                a["deadend"] += sum(1 for x in boxed if x[4] == 1)
                a["ate"] += sum(1 for x in boxed if x[5])
                a["len2"] += sum(1 for x in boxed if x[2] == 2)
    print(f"=== DEAD CELLS rounds 0-{upto}: non-ram deaths by map and team (up to {per_map} games per team and map; opponents 2000+)")
    print("map | team | games | boxed deaths per game / free-cell deaths per game | segments lost in boxed deaths per game | different cells per game | "
          "share of boxed deaths on a cell where a team-mate already died this game | deaths per game on the most used cell | on a cell with one open side | "
          "the dragon ate on that cell within a round before | 2-long")
    for mp in MAPS:
        for c in ("meow", "opponents of meow (test4, WHQ)", "forgot", "SSS", "Vibing++"):
            a = agg.get((mp, c))
            if not a:
                continue
            n, b = a["games"], max(1, a["boxed"])
            print(f"{mp:15s} | {c:30s} | {n:3d} | {a['boxed'] / n:5.1f} / {a['free'] / n:4.1f} | {a['seg'] / n:5.1f} | {a['cells'] / n:5.1f} | "
                  f"{100 * a['rep'] / b:3.0f}% | {a['top'] / n:4.1f} | {100 * a['deadend'] / b:3.0f}% | {100 * a['ate'] / b:3.0f}% | {100 * a['len2'] / b:3.0f}%")
        print()
