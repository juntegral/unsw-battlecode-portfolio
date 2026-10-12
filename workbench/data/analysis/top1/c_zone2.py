#!/usr/bin/env python3
"""c_zone2.py <team_id> <size> [max_games=120] [jobs=4]: is a free pearl next to the head eaten, by distance to long own dragons?

Test of our bot's "leader zone" (after round 150 on large maps a non-leader gets no reward, and a penalty, for a pearl
within 9 cells of the leader it knows). Turns counted: a dragon 2-4 long that is not its team's longest; a pearl on a
free cell next to its head; that cell has at least one other free neighbour; no enemy head within 2 steps of the
pearl and no other own head next to it. Split by phase and by where the pearl is:
  - within 9 cells (wrapped manhattan) of the head of the team's longest dragon, if that dragon is 5 or longer
  - else within 9 cells of the head of another own dragon of 5 or longer
  - else no own dragon of 5+ within 9 cells
and, separately, by the length of the team's longest dragon at that moment (under 5, 5-9, 10+).
Own side and the opponents' side of the same games are pooled separately.
"""
import csv
import sys
from collections import Counter
from multiprocessing import Pool

sys.dont_write_bytecode = True
import c_lib  # noqa: E402
from c_lib import Hooks2, Walk2  # noqa: E402

ZONE = 9


def phase(r):
    return "r0-99" if r < 100 else "r100-149" if r < 150 else "r150-199" if r < 200 else "r200-299" if r < 300 else "r300-399" if r < 400 else "r400+"


class Z(Hooks2):
    def __init__(self):
        self.c = Counter()
        self.cur = None
        self.longest = {"A": None, "B": None}
        self.big = {"A": [], "B": []}

    def round_start(self, g, r):
        self.close()
        best = {"A": (0, None), "B": (0, None)}
        self.big = {"A": [], "B": []}
        for d, body in g.bodies.items():
            s = g.teams[d]
            if len(body) > best[s][0]:
                best[s] = (len(body), d)
            if len(body) >= 5:
                self.big[s].append(d)
        self.longest = {s: best[s] for s in "AB"}

    def close(self):
        cur = self.cur
        self.cur = None
        if cur is None:
            return
        for key in cur[0]:
            self.c[key + ("n",)] += 1
            if cur[1][0]:
                self.c[key + ("ate",)] += 1

    def turn(self, g, did):
        self.close()
        if not g.pearls:
            return
        body = g.bodies[did]
        L = len(body)
        s = g.teams[did]
        if L > 4 or self.longest[s][1] == did:
            return
        o = "B" if s == "A" else "A"
        b = g.board
        head = body[0]
        cands = [n for n in b.nb(head) if n is not None and n in g.pearls]
        if not cands:
            return
        occ = c_lib.occupied(g)
        target = None
        for n in cands:
            if n in occ:
                continue
            ex = sum(1 for m in b.nb(n) if m is not None and m != head and m not in occ)
            if ex >= 1:
                target = n
                break
        if target is None:
            return
        near = b.bfs(target, 2)
        for d2, body2 in g.bodies.items():
            if d2 == did:
                continue
            dd = near.get(body2[0])
            if dd is None:
                continue
            if g.teams[d2] == o or dd <= 1:
                return
        llen, lid = self.longest[s]
        zone = "no own dragon of 5+ within 9 cells"
        if lid is not None and lid in g.bodies and llen >= 5 and b.manhattan(target, g.bodies[lid][0]) <= ZONE:
            zone = "within 9 cells of the longest own dragon"
        else:
            for d2 in self.big[s]:
                if d2 != did and d2 in g.bodies and b.manhattan(target, g.bodies[d2][0]) <= ZONE:
                    zone = "within 9 cells of another own dragon of 5+"
                    break
        lcl = "longest own dragon under 5" if llen < 5 else "longest own dragon 5-9" if llen < 10 else "longest own dragon 10+"
        ph = phase(g.round)
        self.cur = ([(s, ph, "zone", zone), (s, ph, "leader", lcl), (s, ph, "all", "all")], [False])

    def eat(self, g, did, cell, origin):
        if self.cur is not None and g.current == did:
            self.cur[1][0] = True

    def end(self, g, rounds, winner, result):
        self.close()


def work(job):
    gid, path, s = job
    z = Z()
    try:
        Walk2(path).run(z)
    except Exception as e:  # noqa: BLE001
        return gid, None, repr(e)
    out = Counter()
    for key, v in z.c.items():
        out[("own" if key[0] == s else "opp",) + key[1:]] += v
    return gid, out, None


if __name__ == "__main__":
    team = int(sys.argv[1])
    size_want = sys.argv[2]
    nums = [x for x in sys.argv[3:] if x.isdigit()]
    maxg = int(nums[0]) if nums else 120
    jobs = int(nums[1]) if len(nums) > 1 else 4
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
    print(f"=== ZONE2 team {team}, {size_want} maps, {len(todo)} games: a 2-4-long dragon (not the longest) with a free pearl next to its head, an exit behind the pearl and nobody else near: ate % (turns)")
    PH = ("r0-99", "r100-149", "r150-199", "r200-299", "r300-399", "r400+")
    for side in ("own", "opp"):
        who = f"team {team}" if side == "own" else "its opponents"
        print(f"  {who}")
        for kind in ("all", "zone", "leader"):
            labs = sorted({k[3] for k in total if k[0] == side and k[2] == kind})
            for lab in labs:
                cells = []
                for ph in PH:
                    n, a = total[(side, ph, kind, lab, "n")], total[(side, ph, kind, lab, "ate")]
                    cells.append(f"{ph} {100 * a / n:3.0f}% ({n:5d})" if n else f"{ph}   -  (    0)")
                print(f"    {lab:44s} | " + " | ".join(cells))
