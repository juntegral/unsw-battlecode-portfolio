#!/usr/bin/env python3
"""c_zone.py <game_id|team_id> [size] [max_games=60] [jobs=4]: is a pearl next to the head eaten? (test of a "pearls near
the leader are reserved" rule)

For every dragon-turn that begins with a pearl on a cell next to the head (kelp respected, the cell free of bodies):
did the dragon eat a pearl that turn? Split by
  - phase: rounds 0-149 / 150-299 / 300+
  - who the dragon is: the team's longest dragon ("leader") or another dragon
  - where the pearl is: within 9 cells (wrapped manhattan) of the head of the team's longest dragon ("in zone") or not
  - whether an enemy head is within 2 path steps of the pearl
With a game id: both sides of that game. With a team id and a size: all games of the team against 2000+ opponents on
maps of that size (Schooltime left out), own side and the opponents' side pooled separately.
"""
import csv
import sys
from collections import Counter
from multiprocessing import Pool

sys.dont_write_bytecode = True
import c_lib  # noqa: E402
from c_lib import GAMES, Hooks2, Walk2  # noqa: E402

ZONE = 9


class Z(Hooks2):
    def __init__(self):
        self.c = Counter()
        self.cur = None
        self.longest = {"A": None, "B": None}
        self.heads = {}

    def round_start(self, g, r):
        self.close(g)
        best = {"A": (0, None), "B": (0, None)}
        for d, body in g.bodies.items():
            s = g.teams[d]
            if len(body) > best[s][0]:
                best[s] = (len(body), d)
        self.longest = {s: best[s][1] for s in "AB"}

    def close(self, g):
        cur = self.cur
        self.cur = None
        if cur is None:
            return
        key, ate = cur
        self.c[key + ("n",)] += 1
        if ate[0]:
            self.c[key + ("ate",)] += 1

    def turn(self, g, did):
        self.close(g)
        body = g.bodies[did]
        s = g.teams[did]
        o = "B" if s == "A" else "A"
        b = g.board
        head = body[0]
        if not g.pearls:
            return
        occ = None
        target = None
        for n in b.nb(head):
            if n is not None and n in g.pearls:
                if occ is None:
                    occ = c_lib.occupied(g)
                if n not in occ:
                    target = n
                    break
        if target is None:
            return
        lid = self.longest[s]
        who = "leader" if did == lid else "other"
        zone = "no leader"
        if lid is not None and lid in g.bodies:
            zone = "in zone" if b.manhattan(target, g.bodies[lid][0]) <= ZONE else "outside"
        near = b.bfs(target, 2)
        enemy = any(g.teams[d2] == o and body2[0] in near for d2, body2 in g.bodies.items())
        ph = "r0-149" if g.round < 150 else "r150-299" if g.round < 300 else "r300+"
        L = len(body)
        cl = "L2-4" if L <= 4 else "L5+"
        self.cur = ((s, ph, who, cl, zone, "enemy near" if enemy else "no enemy"), [False])

    def eat(self, g, did, cell, origin):
        if self.cur is not None:
            self.cur[1][0] = True

    def end(self, g, rounds, winner, result):
        self.close(g)


def work(job):
    gid, path, s = job
    z = Z()
    try:
        Walk2(path).run(z)
    except Exception as e:  # noqa: BLE001
        return gid, None, repr(e)
    out = Counter()
    for key, v in z.c.items():
        side = "own" if key[0] == s else "opp"
        out[(side,) + key[1:]] += v
    return gid, out, None


def show(total, sides, title):
    print(title)
    print("  side phase dragon length pearl place | enemy head within 2 steps of the pearl: no -> turns, ate % | yes -> turns, ate %")
    keys = sorted({k[:5] for k in total})
    for k in keys:
        if k[0] not in sides:
            continue
        n0, a0 = total[k + ("no enemy", "n")], total[k + ("no enemy", "ate")]
        n1, a1 = total[k + ("enemy near", "n")], total[k + ("enemy near", "ate")]
        if n0 + n1 < 5:
            continue
        print(f"  {k[0]:4s} {k[1]:9s} {k[2]:6s} {k[3]:4s} {k[4]:9s} | {n0:6d} turns, ate {100 * a0 / max(1, n0):3.0f}% | {n1:6d} turns, ate {100 * a1 / max(1, n1):3.0f}%")


if __name__ == "__main__":
    a = sys.argv[1]
    if a in GAMES:
        info = GAMES[a]
        gid, out, err = work((a, info["replay_path"], "A"))
        nm = {s: c_lib.tname(info, s) for s in "AB"}
        show(out, ("own", "opp"), f"=== ZONE {a} {info['map']}: own = A = {nm['A']}, opp = B = {nm['B']}")
    else:
        team = int(a)
        size_want = sys.argv[2]
        maxg = int(sys.argv[3]) if len(sys.argv) > 3 else 60
        jobs = int(sys.argv[4]) if len(sys.argv) > 4 else 4
        todo = []
        for g in csv.DictReader(open("games.csv")):
            if g["map"] == "Schooltime":
                continue
            size = "small" if g["map_size"].startswith("small") else "medium" if g["map_size"].startswith("medium") else "large"
            if size != size_want:
                continue
            for s in "AB":
                if int(g[f"team{s}Id"]) != team:
                    continue
                o = "B" if s == "A" else "A"
                try:
                    if float(g[f"team{o}Elo"]) < 2000:
                        continue
                except ValueError:
                    continue
                todo.append((g["game_id"], g["replay_path"], s))
        todo = todo[:: max(1, len(todo) // maxg)][:maxg]
        total = Counter()
        with Pool(jobs) as pool:
            for gid, out, err in pool.imap_unordered(work, todo):
                if err:
                    print("error", gid, err)
                    continue
                total.update(out)
        show(total, ("own", "opp"), f"=== ZONE team {team}, {size_want} maps, {len(todo)} games: own = the team, opp = its opponents in the same games")
