#!/usr/bin/env python3
"""Candidate 1, the part the chance files skip: dragons LONGER than 12.

extract3.py (and my recount) skip attackers over 12 long.  With QUEEN_HUNT on and no length limit, hunt_path() lets
any non-queen dragon ram the enemy queen when her head is in its view and a path of free cells of at most
min(reach, 12) steps leads to it.  How often would one of our dragons of 13 or more have had such a turn, was it our
longest dragon, what was the state of the game, and did she die later anyway?
Walks our 401 games.  Usage: python3 h_c1long.py run -> h_out/c1long.json ; table -> stdout (h_out/c1long.txt)
"""
import csv
import json
import os
import sys
from collections import Counter, deque
from multiprocessing import Pool

import lib

OUT = "h_out/c1long.json"


class H(lib.Hooks):
    def __init__(self, me):
        self.me = me
        self.rows = []
        self.cur = None
        self.longest = None

    def round_start(self, g, r):
        best = None
        for d, body in g.bodies.items():
            if g.teams[d] == self.me and (best is None or len(body) > best[0]):
                best = (len(body), d)
        self.longest = best[1] if best else None

    def action(self, g, did, kind, nsteps):
        self.cur = None
        b = g.board
        s = g.teams[did]
        if s != self.me or did == b.queen[s]:
            return
        o = "B" if s == "A" else "A"
        q = g.bodies.get(b.queen[o])
        if q is None:
            return
        body = g.bodies[did]
        n = len(body)
        if n <= 12:
            return
        head, target = body[0], q[0]
        if b.cheb(head, target) > 3:
            return
        blocked = set()
        for other in g.bodies.values():
            blocked.update(other)
        rc = min(lib.reach(n), 12)
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
        free = -(-n // 4)
        rec = dict(round=g.round, id=did, len=n, steps=found, paid=max(0, found - free), qlen=len(q), taken=0,
                   longest=int(did == self.longest), ownq=int(b.queen[s] in g.bodies))
        self.rows.append(rec)
        self.cur = (did, rec)

    def death(self, g, did, reason, length, body, actor):
        s = g.teams[did]
        if did == g.board.queen[s] and s != self.me and reason == "headon" and self.cur is not None and actor == self.cur[0]:
            self.cur[1]["taken"] = 1


def work(job):
    gid, path, me = job
    h = H(me)
    lib.Walk(path).run(h)
    return gid, h.rows


def run():
    rows = [r for r in csv.DictReader(open("games.csv")) if r["map"] != "Schooltime"]
    jobs = []
    for r in rows:
        ea, eb = float(r["teamAElo"] or 0), float(r["teamBElo"] or 0)
        if r["teamAId"] == "1119" and eb >= 2000:
            jobs.append((r["game_id"], r["replay_path"], "A"))
        elif r["teamBId"] == "1119" and ea >= 2000:
            jobs.append((r["game_id"], r["replay_path"], "B"))
    out = {}
    with Pool(4) as pool:
        for i, (gid, res) in enumerate(pool.imap_unordered(work, jobs, chunksize=4)):
            out[gid] = res
            if (i + 1) % 100 == 0:
                print(i + 1, "/", len(jobs), flush=True)
    json.dump(out, open(OUT, "w"), separators=(",", ":"))


def table():
    data = json.load(open(OUT))
    base = {str(r["gid"]): r for r in json.load(open("h_out/base.json")) if "meow" in r["groups"]}
    turns = [(gid, p) for gid, rows in data.items() for p in rows]
    games = {gid for gid, rows in data.items() if rows}
    print(f"turns on which one of our dragons of 13 or more had her queen in view and within 12 free steps: {len(turns)} in {len(games)} of {len(data)} games")
    c = Counter()
    for gid, p in turns:
        c["taken (the live rules made it ram)"] += p["taken"]
        c["the dragon was our longest"] += p["longest"]
        c["our own queen alive at that moment"] += p["ownq"]
        c["free of charge (no paid step)"] += p["paid"] == 0
    for k, v in c.items():
        print(f"   {k}: {v}")
    print("games, by what the game was and whether a shorter dragon of ours also had a chance in it:")
    g2 = Counter()
    for gid in sorted(games):
        b = base[gid]
        first = min(data[gid], key=lambda p: p["round"])
        short_first = min((c_[0] for c_ in b["my_ch"] if c_[9]), default=None)
        qd = b["op_qd"]
        state = ("wipe-out " if b["end_type"] == "wipe-out" else "round 500 ") + ("W" if b["win"] else "L") + (", her queen alive at the end" if b["op_fin"]["queen"] else ", her queen dead at the end")
        g2[state] += 1
        print(f"   {gid} {b['map']:16s} {b['build']:4s} first such turn r{first['round']:3d}: our L{first['len']} ({'our longest' if first['longest'] else 'not our longest'}), {first['steps']} steps,"
              f" her queen L{first['qlen']}, our queen {'alive' if first['ownq'] else 'dead'}; a dragon of 12 or shorter had a chance from r{short_first};"
              f" her queen {'died r' + str(qd['round']) if qd else 'lived'}; {state}; final ours {b['my_fin']['longest']} (second {b['my_second_fin']}) hers {b['op_fin']['longest']}")
    print(dict(g2))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        try:
            os.nice(10)
        except OSError:
            pass
        run()
    else:
        table()
