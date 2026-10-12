#!/usr/bin/env python3
"""Per-game queen / role / feeding extraction for the top-team study.

Reads games.csv (made by tools/top_metrics.py), walks every replay once and writes q/<game_id>.json.
Usage: python3 extract.py [--limit N] [--only id,id]   (4 worker processes, skips games already done)
All distances called "path" respect kelp, wrap and portals but ignore dragon bodies.

History: the first run (run1/REPORT.md, 1,754 games) skipped two games (1021191, 1054802) because the
`victim_queen` expression in death() could evaluate to None. Fixed with bool() before the 04:05 refresh, so the
refreshed q/ holds every game in games.csv.
"""
import csv
import json
import os
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import lib

OUT = Path(__file__).resolve().parent / "q"
VERSION = 3
BFS_LIMIT = 12
NEAR = 6      # an enemy head this close (path) to the queen opens an "intruder" episode
GONE = 9      # ... and it closes once the enemy is further than this


def lclass(n):
    return "2" if n <= 2 else "3_4" if n <= 4 else "5_9" if n <= 9 else "10_19" if n <= 19 else "20p"


class X(lib.Hooks):
    def __init__(self):
        self.per = {s: defaultdict(list) for s in "AB"}
        self.headons = []
        self.suicides = []
        self.big_deaths = []
        self.splits = {s: Counter() for s in "AB"}
        self.sprints = {s: Counter() for s in "AB"}
        self.flow = {s: Counter() for s in "AB"}
        self.qeats = {s: Counter() for s in "AB"}
        self.qsplits = {s: [] for s in "AB"}
        self.qdeath = {s: None for s in "AB"}
        self.qsteps = {s: Counter() for s in "AB"}
        self.episodes = {s: [] for s in "AB"}
        self.active = {s: {} for s in "AB"}
        self.round_heads = {}
        self.qdist = {s: None for s in "AB"}
        self.longest_id = {s: None for s in "AB"}
        self.qmoved = {s: 0 for s in "AB"}
        self.qround = {s: None for s in "AB"}

    # ---- helpers
    def other(self, s):
        return "B" if s == "A" else "A"

    def round_start(self, g, r):
        b = g.board
        self.round_heads = {d: (body[0], len(body)) for d, body in g.bodies.items()}
        occupied = None
        for s in "AB":
            per = self.per[s]
            mine = [(len(body), -d) for d, body in g.bodies.items() if g.teams[d] == s]
            mine.sort(reverse=True)
            per["units"].append(len(mine))
            per["total"].append(sum(m[0] for m in mine))
            per["longest"].append(mine[0][0] if mine else 0)
            per["second"].append(mine[1][0] if len(mine) > 1 else 0)
            self.longest_id[s] = -mine[0][1] if mine else None
            hist = Counter(lclass(m[0]) for m in mine)
            if r % 25 == 0:
                per["lenhist"].append([r] + [hist.get(k, 0) for k in ("2", "3_4", "5_9", "10_19", "20p")])
            qid = b.queen[s]
            q = g.bodies.get(qid)
            self.qround[s] = (q[0], len(q)) if q else None
            self.qmoved[s] = 0
            if not q:
                per["q"].append(None)
                self.qdist[s] = None
                for ep in self.active[s].values():
                    ep["outcome"] = ep.get("outcome") or "queen_dead"
                    ep["end"] = r
                    self.episodes[s].append(ep)
                self.active[s] = {}
                continue
            head = q[0]
            dist = b.bfs(head, BFS_LIMIT)
            self.qdist[s] = dist
            if occupied is None:
                occupied = set()
                for body in g.bodies.values():
                    occupied.update(body)
            free = sum(1 for n in b.nb(head) if n is not None and n not in occupied)
            e8m = e8p = e4p = a6p = a3p = seen = 0
            margin = 99
            near_small = 99
            qcells = list(q)
            for d, body in g.bodies.items():
                if d == qid:
                    continue
                h2 = body[0]
                pd = dist.get(h2)
                if g.teams[d] == s:
                    if pd is not None:
                        a6p += pd <= 6
                        a3p += pd <= 3
                    continue
                if b.manhattan(head, h2) <= 8:
                    e8m += 1
                if any(b.cheb(h2, c) <= 3 for c in qcells):
                    seen += 1
                if pd is not None:
                    e8p += pd <= 8
                    e4p += pd <= 4
                    margin = min(margin, pd - lib.reach(len(body)))
                    if len(body) <= 4:
                        near_small = min(near_small, pd)
                    # intruder episodes
                    if pd <= NEAR and d not in self.active[s]:
                        self.active[s][d] = dict(id=d, start=r, len=len(body), min=pd, qpos=list(head),
                                                 a6=None, qlen=len(q))
                    if d in self.active[s]:
                        ep = self.active[s][d]
                        ep["min"] = min(ep["min"], pd)
            for d in list(self.active[s]):
                ep = self.active[s][d]
                if ep["a6"] is None:
                    ep["a6"] = a6p
                body = g.bodies.get(d)
                if body is None:
                    continue  # closed in death()
                pd = dist.get(body[0])
                if pd is None or pd > GONE:
                    ep["outcome"], ep["end"] = "left", r
                    ep["qmove"] = b.manhattan(tuple(ep["qpos"]), head)
                    self.episodes[s].append(ep)
                    del self.active[s][d]
            pd_portal = min((dist[c] for c in b.portal_cells if c in dist), default=-1)
            per["q"].append([head[0], head[1], len(q), e8m, e8p, e4p, a6p, a3p, seen,
                             margin if margin < 99 else None, near_small if near_small < 99 else None,
                             free, b.ball(head, 4), b.degree(head), pd_portal,
                             b.manhattan(head, b.starts[qid]), int(self.longest_id[s] == qid)])

    def action(self, g, did, kind, nsteps):
        s = g.teams[did]
        n = len(g.bodies[did])
        bucket = g.round // 50
        if kind == 0 and nsteps >= 2:
            free = -(-n // 4)
            self.sprints[s][f"{bucket}:{lclass(n)}:n"] += 1
            self.sprints[s][f"{bucket}:{lclass(n)}:paid"] += max(0, nsteps - free)
        if kind == 0:
            self.sprints[s][f"{bucket}:{lclass(n)}:moves"] += 1
        if kind == 2:
            b = g.board
            head = g.bodies[did][0]
            lid = self.longest_id[s]
            qid = b.queen[s]
            lbody = g.bodies.get(lid)
            qbody = g.bodies.get(qid)
            dl = b.manhattan(head, lbody[0]) if lbody is not None and lid != did else -1
            dq = b.manhattan(head, qbody[0]) if qbody is not None and qid != did else -1
            self.suicides.append([g.round, s, did, n, head[0], head[1], dl, len(lbody) if lbody else 0,
                                  dq, len(qbody) if qbody else 0, int(lid == qid)])

    def moved(self, g, did, head, step_index, ate):
        s = g.teams[did]
        if did == g.board.queen[s] and did == g.current:
            self.qsteps[s][g.round // 50] += 1
            self.qmoved[s] += 1

    def split(self, g, parent, child, before, plen, clen):
        s = g.teams[parent]
        self.splits[s][f"{g.round // 50}:{lclass(before)}"] += 1
        if parent == g.board.queen[s]:
            self.qsplits[s].append([g.round, before, plen, clen])

    def eat(self, g, did, cell, origin):
        s = g.teams[did]
        b = g.board
        bucket = g.round // 50
        role = "queen" if did == b.queen[s] else "longest" if did == self.longest_id[s] else "other"
        if origin[0] == "corpse":
            src = "own" if origin[1] == s else "enemy"
            kind = "suicide" if origin[3] == "noaction" else "ram" if origin[3] == "headon" else "crash"
            self.flow[s][f"{bucket}:{src}:{kind}:{role}"] += 1
        else:
            self.flow[s][f"{bucket}:natural::{role}"] += 1
        if role == "queen":
            self.qeats[s][f"{bucket}:{origin[0]}"] += 1

    def death(self, g, did, reason, length, body, actor):
        s = g.teams[did]
        b = g.board
        r = g.round
        killer = None
        if reason == "headon" and actor is not None and actor != did:
            a_head, a_len = g.act_start
            start = self.round_heads.get(actor)
            vq = did == b.queen[s]
            killer = dict(id=actor, team=g.teams[actor], len=a_len, steps_used=g.step_index + 1,
                          steps_req=g.act_steps, born_this_round=start is None)
            self.headons.append([r, g.teams[actor], actor, a_len, g.step_index + 1, g.act_steps,
                                 s, did, length, int(vq), int(did == self.longest_id[s]),
                                 int(actor == b.queen[g.teams[actor]]), b.manhattan(a_head, body[0])])
            if vq:
                dist = self.qdist[s]
                qstart = self.qround[s]
                if start is not None:
                    killer["start_len"] = start[1]
                    killer["start_path_to_qstart"] = dist.get(start[0]) if dist else None
                    killer["start_manh_to_qstart"] = b.manhattan(start[0], qstart[0]) if qstart else None
                    killer["start_manh_to_qdeath"] = b.manhattan(start[0], body[0])
                    dd = b.bfs(body[0], BFS_LIMIT)
                    killer["start_path_to_qdeath"] = dd.get(start[0])
        if length >= 8:
            self.big_deaths.append([r, s, did, length, reason, killer["len"] if killer else -1,
                                    int(did == self.longest_id[s]), int(did == b.queen[s])])
        if did == b.queen[s]:
            qstart = self.qround[s]
            last = self.per[s]["q"][-1] if self.per[s]["q"] else None
            self.qdeath[s] = dict(round=r, reason=reason, len=length, pos=list(body[0]),
                                  own_action=int(actor == did), qsteps_this_round=self.qmoved[s],
                                  killer=killer, last=last,
                                  actor_team=g.teams.get(actor) if actor is not None else None,
                                  round_start_pos=list(qstart[0]) if qstart else None)
        # intruder episodes of the other side's queen
        o = self.other(s)
        ep = self.active[o].pop(did, None)
        if ep is not None:
            if reason == "headon" and actor is not None and actor != did:
                ep["outcome"] = "rammed_by_queen" if actor == b.queen[o] else "rammed_by_defender"
                ep["by_len"] = g.act_start[1]
            elif reason == "headon":
                ep["outcome"] = "it_rammed"   # refined below through the victim's own record
                ep["victim_queen"] = int(bool(self.qdeath[o] is not None and self.qdeath[o]["round"] == r
                                              and self.qdeath[o].get("killer") and self.qdeath[o]["killer"]["id"] == did))
            else:
                ep["outcome"] = "died_" + reason
            ep["end"] = r
            self.episodes[o].append(ep)

    def end(self, g, rounds, winner, result):
        self.rounds, self.winner = rounds, winner
        for s in "AB":
            for ep in self.active[s].values():
                ep["outcome"], ep["end"] = "game_end", rounds
                self.episodes[s].append(ep)
        self.final = {}
        for s in "AB":
            mine = [len(body) for d, body in g.bodies.items() if g.teams[d] == s]
            q = g.bodies.get(g.board.queen[s])
            self.final[s] = dict(units=len(mine), total=sum(mine), longest=max(mine, default=0),
                                 queen=len(q) if q else 0)


def work(row):
    out = OUT / (row["game_id"] + ".json")
    try:
        if out.exists():
            try:
                if json.loads(out.read_text()).get("version") == VERSION:
                    return row["game_id"], True, None
            except ValueError:
                pass
        x = X()
        g = lib.Walk(row["replay_path"])
        g.run(x)
        b = g.board
        data = dict(version=VERSION, game_id=int(row["game_id"]), map=row["map"], w=b.w, h=b.h, rounds=x.rounds,
                    winner=x.winner, end_type=row["end_type"], ranked=row["ranked"], sources=row["sources"],
                    completed_at=row["completed_at"],
                    sides={s: dict(team=int(row[f"team{s}Id"]), name=row[f"team{s}Name"],
                                   elo=float(row[f"team{s}Elo"]) if row[f"team{s}Elo"] else None,
                                   queen_id=b.queen[s], start=list(b.starts[b.queen[s]]),
                                   start_len=None, final=x.final[s], qdeath=x.qdeath[s], qsplits=x.qsplits[s],
                                   qsteps=dict(x.qsteps[s]), qeats=dict(x.qeats[s]), episodes=x.episodes[s],
                                   splits=dict(x.splits[s]), sprints=dict(x.sprints[s]), flow=dict(x.flow[s]),
                                   per={k: v for k, v in x.per[s].items()}) for s in "AB"},
                    n_start=len(b.starts), portals=len(b.portal_pair) // 2, kelp=len(b.kelp),
                    headons=x.headons, suicides=x.suicides, big_deaths=x.big_deaths)
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
    if "--limit" in sys.argv:
        rows = rows[: int(sys.argv[sys.argv.index("--limit") + 1])]
    errors, done, cached = [], 0, 0
    with Pool(4) as pool:
        for gid, hit, err in pool.imap_unordered(work, rows, chunksize=4):
            done += 1
            cached += hit
            if err:
                errors.append((gid, err))
            if done % 100 == 0:
                print(f"{done}/{len(rows)} cached {cached} errors {len(errors)}", flush=True)
    print(f"done {done} cached {cached} errors {len(errors)}")
    for e in errors[:20]:
        print("ERR", e)


if __name__ == "__main__":
    main()
