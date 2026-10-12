#!/usr/bin/env python3
"""d_recount.py: an independent recount of the central number of deep-read-4.md (sub-session A4).

Claim to check: of our 251 queens rammed by an enemy, 106 had the killer in view at the start of their last own turn
and a one-step move that no visible enemy head could move into that round (104 of them ended in reach, 2 ended on a
"safe" cell and were rammed anyway).

This script shares no code with d_class.py / d_tab.py.  It walks each replay once, keeps the board at the start of
the queen's most recent own turn, and at her death by an enemy ram decides the same question with a different
method: for every enemy head within Chebyshev distance 3 of her head it ENUMERATES that dragon's possible moves
step by step (depth-first, no cell twice), following the engine rule exactly: the first ceil(L/4) steps are free
with L fixed at the start, each later step needs a length of 3 or more and removes one segment, a pearl on the
destination adds one.  A cell is blocked if any body stood on it at the start of her turn, except her own last
segment.  A one-step move of hers is "safe" if no such enumeration can end on its destination.

Usage: d_recount.py [jobs]      prints the counts and writes d_out/recount.txt lines per game
"""
import csv
import json
import math
import os
import sys
from multiprocessing import Pool

import lib

HERE = os.path.dirname(os.path.abspath(__file__))


def can_reach(b, blocked, pearls, src, length, targets):
    """Set of target cells the dragon (head src, length) can move its head into this round."""
    free = math.ceil(length / 4)
    hit = set()
    limit = 9

    def go(cell, step, cur, seen, eaten):
        if len(hit) == len(targets) or step > limit:
            return
        nxt = step + 1
        if nxt > free:
            if cur < 3:
                return
            cur2 = cur - 1
        else:
            cur2 = cur
        for d in range(4):
            n = b.step(cell, d)
            if n is None or n in seen:
                continue
            if n in targets:
                hit.add(n)
            if n in blocked:
                continue
            c3 = cur2
            if n in pearls and n not in eaten:
                c3 += 1
                go(n, nxt, c3, seen | {n}, eaten | {n})
            else:
                go(n, nxt, c3, seen | {n}, eaten)

    go(src, 0, length, {src}, frozenset())
    return hit


class H(lib.Hooks):
    def __init__(self, side, qid):
        self.side, self.qid = side, qid
        self.snap = None
        self.result = None

    def action(self, g, did, kind, nsteps):
        if did != self.qid:
            return
        b = g.board
        q = list(g.bodies[did])
        head = q[0]
        blocked = set()
        for d, body in g.bodies.items():
            blocked.update(body)
        vis = {d: (body[0], len(body)) for d, body in g.bodies.items() if g.teams[d] != self.side and b.cheb(body[0], head) <= 3}
        blocked_en = set(blocked)
        blocked_en.discard(q[-1])
        options = [n for n in b.nb(head) if n is not None and n not in blocked]
        self.snap = dict(r=g.round, head=head, vis=vis, options=options, blocked=blocked_en, pearls=set(g.pearls), end=None, kind=kind)

    def moved(self, g, did, head, step_index, ate):
        if did == self.qid and g.current == did and self.snap and self.snap["r"] == g.round:
            self.snap["end"] = head

    def death(self, g, did, reason, length, body, actor):
        if did != self.qid or self.result is not None:
            return
        if reason != "headon" or actor is None or actor == did or g.teams.get(actor) == self.side:
            self.result = dict(ram=False)
            return
        s = self.snap
        b = g.board
        danger = set()
        targets = set(s["options"]) | {s["head"]}
        for d, (h2, L2) in s["vis"].items():
            danger |= can_reach(b, s["blocked"], s["pearls"], h2, L2, targets)
        safe = [c for c in s["options"] if c not in danger]
        end = s["end"] if s["end"] is not None else s["head"]
        self.result = dict(ram=True, round=g.round, killer_in_view=actor in s["vis"], nfree=len(s["options"]), nsafe=len(safe),
                           began_in_reach=s["head"] in danger, ended_in_reach=end in danger)


def work(row):
    gid, path, side = row
    g = lib.Walk(path)
    h = H(side, g.board.queen[side])

    class Stop(Exception):
        pass

    orig = h.death

    def death(*a):
        orig(*a)
        if h.result is not None:
            raise Stop

    h.death = death
    try:
        g.run(h)
    except Stop:
        pass
    return gid, h.result


def main():
    jobs = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    rows = []
    for g in csv.DictReader(open(os.path.join(HERE, "games.csv"))):
        if g["map"] == "Schooltime":
            continue
        for s in "AB":
            o = "B" if s == "A" else "A"
            if g[f"team{s}Id"] == "1119" and g[f"team{o}Elo"] and float(g[f"team{o}Elo"]) >= 2000:
                q = json.load(open(os.path.join(HERE, "q", g["game_id"] + ".json")))
                qd = q["sides"][s]["qdeath"]
                if qd and qd["reason"] == "headon" and qd["killer"] and qd["killer"]["team"] != s:
                    rows.append((g["game_id"], g["replay_path"], s))
    print("our queens rammed by an enemy (from q/*.json):", len(rows), flush=True)
    os.nice(10)
    out = {}
    with Pool(jobs) as pool:
        for gid, res in pool.imap_unordered(work, rows, chunksize=4):
            out[gid] = res
    rams = [r for r in out.values() if r and r["ram"]]
    kv = [r for r in rams if r["killer_in_view"]]
    with_safe = [r for r in kv if r["nsafe"] > 0]
    print("rams found by this walk:", len(rams))
    print("killer's head in her view at the start of her last own turn:", len(kv))
    print("... and at least one safe one-step move:", len(with_safe))
    print("... ... she ended in reach:", sum(r["ended_in_reach"] for r in with_safe), " (began outside reach:", sum(r["ended_in_reach"] and not r["began_in_reach"] for r in with_safe),
          ", began in reach:", sum(r["ended_in_reach"] and r["began_in_reach"] for r in with_safe), ")")
    print("... ... she ended on a cell this script calls safe:", sum(not r["ended_in_reach"] for r in with_safe))
    print("... and no safe one-step move (cornered):", len(kv) - len(with_safe))
    print("killer not in view:", len(rams) - len(kv))
    with open(os.path.join(HERE, "d_out", "recount.txt"), "w") as f:
        for gid in sorted(out):
            f.write(f"{gid} {json.dumps(out[gid])}\n")
    # compare game by game with d_out/cls through d_tab
    import d_tab
    mine = {x["gid"]: x["kind"] for x in d_tab.load() if "meow" in x["groups"]}
    diff = []
    for gid, r in out.items():
        if not r or not r["ram"]:
            continue
        if not r["killer_in_view"]:
            k = "ram: unseen"
        elif r["nsafe"] == 0:
            k = "ram: cornered"
        elif not r["ended_in_reach"]:
            k = "ram: model miss"
        else:
            k = "ram: stayed in" if r["began_in_reach"] else "ram: stepped in"
        if mine.get(gid) != k:
            diff.append((gid, mine.get(gid), k))
    print("games in which the two scripts give a different kind:", len(diff))
    for d in diff[:30]:
        print("   ", d)


if __name__ == "__main__":
    main()
