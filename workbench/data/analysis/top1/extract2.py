#!/usr/bin/env python3
"""Second pass: assassin tracks, leader exposure, and how the queen's surroundings compare with her team's average.

Writes q2/<game_id>.json. Usage: python3 extract2.py   (4 workers, skips finished games)
  kills:   every enemy ram that killed a queen or a team's longest dragon (>= 15 long): the killer's path distance to the
           victim and its length at 1,2,3,5,8,12 rounds before, whether the victim could see it (Chebyshev <= 3) at the
           start of the fatal round, steps used.
  leader:  from round 250, per side, per round with a longest dragon >= 15: [round, len, n enemy heads (len <= 12) that
           have the leader's head inside their one-turn reach, nearest enemy head path distance (<= 12), is_queen]
  crowd:   every 10 rounds: [round, queen allies within manhattan 6, team mean of the same, queen enemies within manh 8,
           team mean of the same, units]
"""
import csv
import json
import os
import sys
from collections import deque
from multiprocessing import Pool
from pathlib import Path

import lib

OUT = Path(__file__).resolve().parent / "q2"
VERSION = 1
BACK = (1, 2, 3, 5, 8, 12)


class X(lib.Hooks):
    def __init__(self):
        self.hist = deque(maxlen=14)
        self.kills = []
        self.leader = {"A": [], "B": []}
        self.crowd = {"A": [], "B": []}
        self.longest = {}

    def round_start(self, g, r):
        b = g.board
        snap = {d: (body[0], len(body)) for d, body in g.bodies.items()}
        self.hist.append((r, snap))
        heads = {"A": [], "B": []}
        for d, body in g.bodies.items():
            heads[g.teams[d]].append((d, body[0], len(body)))
        for s in "AB":
            o = "B" if s == "A" else "A"
            mine = heads[s]
            if not mine:
                self.longest[s] = None
                continue
            lid, lhead, llen = max(mine, key=lambda t: (t[2], -t[0]))
            self.longest[s] = lid
            if r >= 250 and llen >= 15:
                dist = b.bfs(lhead, 12)
                n = 0
                near = 99
                for d, h, ln in heads[o]:
                    pd = dist.get(h)
                    if pd is None:
                        continue
                    near = min(near, pd)
                    if ln <= 12 and pd <= lib.reach(ln):
                        n += 1
                self.leader[s].append([r, llen, n, near if near < 99 else -1, int(lid == b.queen[s])])
            if r % 10 == 0 and len(mine) >= 2:
                qid = b.queen[s]
                tot_a = tot_e = 0
                qa = qe = None
                for d, h, ln in mine:
                    a = sum(1 for d2, h2, _ in mine if d2 != d and b.manhattan(h, h2) <= 6)
                    e = sum(1 for _, h2, _ in heads[o] if b.manhattan(h, h2) <= 8)
                    tot_a += a
                    tot_e += e
                    if d == qid:
                        qa, qe = a, e
                self.crowd[s].append([r, qa, round(tot_a / len(mine), 2), qe, round(tot_e / len(mine), 2), len(mine)])

    def death(self, g, did, reason, length, body, actor):
        if reason != "headon" or actor is None or actor == did:
            return
        s = g.teams[did]
        a = g.teams[actor]
        if a == s:
            return
        b = g.board
        is_q = did == b.queen[s]
        is_l = did == self.longest.get(s) and length >= 15
        if not (is_q or is_l):
            return
        r = g.round
        track = {}
        for rr, snap in self.hist:
            back = r - rr + 1          # 1 = start of the fatal round
            if back in BACK and actor in snap and did in snap:
                dd = b.bfs(snap[did][0], 20).get(snap[actor][0])
                track[back] = [dd if dd is not None else -1, snap[actor][1], b.cheb(snap[did][0], snap[actor][0])]
        self.kills.append(dict(round=r, victim_team=s, queen=int(is_q), longest=int(is_l), vlen=length,
                               klen=g.act_start[1], steps=g.step_index + 1, steps_req=g.act_steps,
                               track=track, born_same_round=int(1 not in track)))

    def end(self, g, rounds, winner, result):
        self.rounds = rounds


def work(row):
    out = OUT / (row["game_id"] + ".json")
    try:
        if out.exists():
            return row["game_id"], True, None
        x = X()
        g = lib.Walk(row["replay_path"])
        g.run(x)
        data = dict(version=VERSION, game_id=int(row["game_id"]), kills=x.kills, leader=x.leader, crowd=x.crowd)
        tmp = out.with_suffix(".tmp%d" % os.getpid())
        tmp.write_text(json.dumps(data, separators=(",", ":")))
        tmp.replace(out)
        return row["game_id"], False, None
    except Exception as exc:  # noqa: BLE001
        return row["game_id"], False, f"{type(exc).__name__}: {exc}"


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
        for gid, hit, err in pool.imap_unordered(work, rows, chunksize=4):
            done += 1
            if err:
                errors.append((gid, err))
            if done % 200 == 0:
                print(f"{done}/{len(rows)} errors {len(errors)}", flush=True)
    print(f"done {done} errors {len(errors)}", errors[:5])


if __name__ == "__main__":
    main()
