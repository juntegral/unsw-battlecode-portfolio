#!/usr/bin/env python3
"""Independent recount of the key numbers of candidate 1, written without the lead's extract3.py code.

For every meow game (opp elo >= 2000, Schooltime out), both sides:
  a chance = a non-queen dragon of 2-12 starts its own action with the enemy queen's head inside its 7x7 view and a
  path to it over cells that hold no dragon segment at that moment (every body counts as blocked, the mover's own
  body too: stricter than extract3.py, which lets the mover pass cells its own tail has left), no longer than
  ceil(L/4) + L - 2 steps.  Taken = the enemy queen dies head-on during that action with this dragon as the actor.
Prints, for meow and for its opponents: chances, taken, by attacker length; games with a chance; games in which the
side rammed the queen; games with a chance and no ram at all.
Usage: python3 h_c1recount.py run -> h_out/c1recount.json ; python3 h_c1recount.py table
"""
import csv
import json
import os
import sys
from collections import Counter, deque
from multiprocessing import Pool

import lib

OUT = "h_out/c1recount.json"


class H(lib.Hooks):
    def __init__(self):
        self.ch = []            # [round, side, id, length, steps, taken]
        self.cur = None
        self.qkill = {"A": None, "B": None}    # side whose queen was rammed -> (round, actor)

    def action(self, g, did, kind, nsteps):
        self.cur = None
        b = g.board
        s = g.teams[did]
        if did == b.queen[s]:
            return
        o = "B" if s == "A" else "A"
        q = g.bodies.get(b.queen[o])
        if q is None:
            return
        body = g.bodies[did]
        n = len(body)
        if n > 12:
            return
        head, target = body[0], q[0]
        if b.cheb(head, target) > 3:
            return
        blocked = set()
        for other in g.bodies.values():
            blocked.update(other)
        rc = lib.reach(n)
        dist = {head: 0}
        dq = deque([head])
        found = None
        while dq and found is None:
            c = dq.popleft()
            if dist[c] >= rc:
                continue
            for nb in b.nb(c):
                if nb is None or nb in dist:
                    continue
                if nb == target:
                    found = dist[c] + 1
                    break
                if nb in blocked:
                    continue
                dist[nb] = dist[c] + 1
                dq.append(nb)
        if found is None:
            return
        rec = [g.round, s, did, n, found, 0]
        self.ch.append(rec)
        self.cur = (did, rec)

    def death(self, g, did, reason, length, body, actor):
        s = g.teams[did]
        if did == g.board.queen[s] and reason == "headon" and actor is not None and actor != did and g.teams.get(actor) != s:
            self.qkill[s] = (g.round, actor)
            if self.cur is not None and self.cur[0] == actor:
                self.cur[1][5] = 1


def work(job):
    gid, path = job
    h = H()
    lib.Walk(path).run(h)
    return gid, dict(ch=h.ch, qkill=h.qkill)


def run():
    rows = [r for r in csv.DictReader(open("games.csv")) if r["map"] != "Schooltime"]
    jobs = []
    for r in rows:
        ea, eb = float(r["teamAElo"] or 0), float(r["teamBElo"] or 0)
        if (r["teamAId"] == "1119" and eb >= 2000) or (r["teamBId"] == "1119" and ea >= 2000):
            jobs.append((r["game_id"], r["replay_path"]))
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

    def lc(n):
        return "2-3" if n <= 3 else "4" if n == 4 else "5-9" if n <= 9 else "10-12"

    for who in ("meow", "opponents of meow"):
        c = Counter()
        g_ch = g_kill = g_miss = 0
        for gid, v in data.items():
            r = rows[gid]
            me = "A" if r["teamAId"] == "1119" else "B"
            side = me if who == "meow" else ("B" if me == "A" else "A")
            other = "B" if side == "A" else "A"
            ch = [x for x in v["ch"] if x[1] == side]
            for x in ch:
                c[(lc(x[3]), "n")] += 1
                c[(lc(x[3]), "taken")] += x[5]
            killed = v["qkill"][other] is not None
            g_ch += bool(ch)
            g_kill += killed
            g_miss += bool(ch) and not killed
        tot = sum(v for k, v in c.items() if k[1] == "n")
        tk = sum(v for k, v in c.items() if k[1] == "taken")
        print(f"{who}: games {len(data)}; in-view chances {tot}, taken {tk} = {100 * tk / max(1, tot):.0f}%; "
              + "; ".join(f"{k}: {c[(k, 'taken')]} of {c[(k, 'n')]}" for k in ("2-3", "4", "5-9", "10-12"))
              + f"; games with a chance {g_ch}; games in which this side rammed the queen {g_kill}; chance and never a ram {g_miss}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        try:
            os.nice(10)
        except OSError:
            pass
        run()
    else:
        table()
