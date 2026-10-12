#!/usr/bin/env python3
"""d_life.py: where each queen lives, per 50 rounds, next to her own team (sub-session A4, questions c and f).

  python3 d_life.py run [jobs] [--only id,id]   walk the replays, write d_out/life/<game_id>.json (both sides)

Same games as d_class.py.  Per side and per 50-round block (index = round // 50), counted at the START of each round
while the queen is alive:
  qr        rounds the queen was alive
  home      sum of the path distance (kelp and portals respected, bodies ignored) from her head to her start cell
  thome     sum over the other own heads of the same distance, tn = number of those head-rounds
  half      rounds in which her head is nearer (path) to the enemy queen's start cell than to her own
  thalf     the same count over the other own heads
  seenr     rounds with at least one enemy head inside her 7x7 view; seers = sum of such heads
  m4, m8    sum of enemy heads within 4 / 8 cells (wrapped manhattan) of her head
  tm4, tm8  the same sums over the other own heads (so tm8 / tn = what an average own dragon has around it)
  a4        sum of own heads within 4 cells (manhattan) of her head
  lensum    sum of her length; cells25 = distinct head cells in each 25-round window (two numbers per block)
Also: seen = list of episodes [start, end, max heads, min path distance, her length at start, outcome], an episode
being consecutive rounds (gaps of one round allowed) with an enemy head in her view; outcome = 'rammed' (rammed during
the episode or within 2 rounds after it), 'died' (dead otherwise in that span), 'lived'.
first_seen = first round with an enemy head in her view; contact = first round any own head has an enemy head in view.
pos = her head cell every round (for loop detection); units = own living dragons every round.
"""
import csv
import json
import os
import sys
from collections import deque
from multiprocessing import Pool

import lib

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "d_out", "life")
TEAMS = {"1119", "306", "91", "264"}
VERSION = 2
KEYS = ("qr", "home", "thome", "tn", "half", "thalf", "seenr", "seers", "m4", "m8", "tm4", "tm8", "a4", "lensum")


def full_bfs(b, src):
    dist = {src: 0}
    q = deque([src])
    while q:
        c = q.popleft()
        for n in b.nb(c):
            if n is not None and n not in dist:
                dist[n] = dist[c] + 1
                q.append(n)
    return dist


class H(lib.Hooks):
    def __init__(self):
        self.blk = {s: [dict.fromkeys(KEYS, 0) for _ in range(10)] for s in "AB"}
        self.cells = {s: [set() for _ in range(20)] for s in "AB"}
        self.seenlog = {s: [] for s in "AB"}      # (round, heads, min path)
        self.first_seen = {s: None for s in "AB"}
        self.contact = {s: None for s in "AB"}
        self.pos = {s: [] for s in "AB"}
        self.units = {s: [] for s in "AB"}
        self.qlen = {s: [] for s in "AB"}
        self.dist = None
        self.qdeath = {s: None for s in "AB"}

    def round_start(self, g, r):
        b = g.board
        if self.dist is None:
            self.dist = {s: full_bfs(b, b.starts[b.queen[s]]) for s in "AB"}
        heads = {"A": [], "B": []}
        for d, body in g.bodies.items():
            heads[g.teams[d]].append((d, body[0]))
        k = min(r // 50, 9)
        w, h = b.w, b.h
        for s in "AB":
            o = "B" if s == "A" else "A"
            self.units[s].append(len(heads[s]))
            qid = b.queen[s]
            q = g.bodies.get(qid)
            if self.contact[s] is None:
                for _, c in heads[s]:
                    if any(b.cheb(c, e) <= 3 for _, e in heads[o]):
                        self.contact[s] = r
                        break
            if q is None:
                self.pos[s].append(None)
                self.qlen[s].append(0)
                continue
            head = q[0]
            self.pos[s].append([head[0], head[1]])
            self.qlen[s].append(len(q))
            blk = self.blk[s][k]
            own, far = self.dist[s], self.dist[o]
            big = w + h
            blk["qr"] += 1
            dq = own.get(head, big)
            blk["home"] += dq
            blk["half"] += far.get(head, big) < dq
            blk["lensum"] += len(q)
            self.cells[s][min(r // 25, 19)].add(head)
            seers = 0
            for _, e in heads[o]:
                dx, dy = abs(e[0] - head[0]), abs(e[1] - head[1])
                dx, dy = min(dx, w - dx), min(dy, h - dy)
                m = dx + dy
                if m <= 8:
                    blk["m8"] += 1
                    blk["m4"] += m <= 4
                if dx <= 3 and dy <= 3:
                    seers += 1
            if seers:
                blk["seenr"] += 1
                blk["seers"] += seers
                pd = b.bfs(head, 8)
                mind = min((pd[e] for _, e in heads[o] if e in pd), default=9)
                self.seenlog[s].append((r, seers, mind, len(q)))
                if self.first_seen[s] is None:
                    self.first_seen[s] = r
            eh = [e for _, e in heads[o]]
            for d, c in heads[s]:
                if d == qid:
                    continue
                blk["tn"] += 1
                dc = own.get(c, big)
                blk["thome"] += dc
                blk["thalf"] += far.get(c, big) < dc
                x, y = c
                for e in eh:
                    dx = abs(e[0] - x)
                    if dx > 8 and w - dx > 8:
                        continue
                    dy = abs(e[1] - y)
                    m = min(dx, w - dx) + min(dy, h - dy)
                    if m <= 8:
                        blk["tm8"] += 1
                        blk["tm4"] += m <= 4
                dx, dy = abs(x - head[0]), abs(y - head[1])
                if min(dx, w - dx) + min(dy, h - dy) <= 4:
                    blk["a4"] += 1

    def death(self, g, did, reason, length, body, actor):
        s = g.teams[did]
        if did == g.board.queen[s]:
            self.qdeath[s] = (g.round, "rammed" if reason == "headon" and actor != did and g.teams.get(actor) != s else "died")

    def end(self, g, rounds, winner, result):
        self.rounds, self.winner = rounds, winner


def episodes(log, qdeath):
    out, cur = [], None
    for r, n, mind, L in log:
        if cur and r - cur[1] <= 2:
            cur[1], cur[2], cur[3] = r, max(cur[2], n), min(cur[3], mind)
        else:
            cur = [r, r, n, mind, L]
            out.append(cur)
    for ep in out:
        oc = "lived"
        if qdeath and ep[0] <= qdeath[0] <= ep[1] + 2:
            oc = qdeath[1]
        ep.append(oc)
    return out


def work(row):
    gid = row["game_id"]
    out = os.path.join(OUT, gid + ".json")
    try:
        if os.path.exists(out):
            try:
                if json.load(open(out)).get("version") == VERSION:
                    return gid, None
            except ValueError:
                pass
        h = H()
        g = lib.Walk(row["replay_path"])
        g.run(h)
        b = g.board
        data = dict(version=VERSION, game_id=int(gid), map=row["map"], w=b.w, h=b.h, rounds=h.rounds, winner=h.winner,
                    battle_id=row["battle_id"], end_type=row["end_type"],
                    sides={s: dict(team=int(row[f"team{s}Id"]), queen=b.queen[s], start=list(b.starts[b.queen[s]]),
                                   blk=h.blk[s], cells25=[len(c) for c in h.cells[s]], seen=episodes(h.seenlog[s], h.qdeath[s]),
                                   first_seen=h.first_seen[s], contact=h.contact[s], pos=h.pos[s], units=h.units[s],
                                   qlen=h.qlen[s], qdeath=h.qdeath[s],
                                   start_gap=h.dist[s].get(b.starts[b.queen["B" if s == "A" else "A"]], -1)) for s in "AB"})
        tmp = out + ".tmp%d" % os.getpid()
        json.dump(data, open(tmp, "w"), separators=(",", ":"))
        os.replace(tmp, out)
        return gid, None
    except Exception:  # noqa: BLE001
        import traceback
        return gid, traceback.format_exc()[-600:]


def wanted():
    rows = []
    for g in csv.DictReader(open(os.path.join(HERE, "games.csv"))):
        if g["map"] == "Schooltime":
            continue
        for s in "AB":
            o = "B" if s == "A" else "A"
            if g[f"team{s}Id"] in TEAMS and g[f"team{o}Elo"] and float(g[f"team{o}Elo"]) >= 2000:
                rows.append(g)
                break
    return rows


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = wanted()
    if "--only" in sys.argv:
        ids = set(sys.argv[sys.argv.index("--only") + 1].split(","))
        rows = [r for r in rows if r["game_id"] in ids]
    jobs = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 4
    try:
        os.nice(10)
    except OSError:
        pass
    print("games:", len(rows), flush=True)
    errs = []
    with Pool(jobs) as pool:
        for i, (gid, err) in enumerate(pool.imap_unordered(work, rows, chunksize=4)):
            if err:
                errs.append((gid, err))
            if i % 200 == 0:
                print(i, flush=True)
    print("done; errors", len(errs))
    for e in errs[:10]:
        print(e[0], e[1])


if __name__ == "__main__":
    main()
