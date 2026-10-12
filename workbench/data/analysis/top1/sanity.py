#!/usr/bin/env python3
"""Hand check of timeline.csv against an independent recount, for a few replays.

Usage: python3 sanity.py <game_id> [<game_id> ...]
Also checks that lib.Board.step() predicts every real head move (walls, wrap, portals).
"""
import csv
import sys
from collections import Counter

import lib

BUCKETS = (25, 50, 100, 150, 200, 250, 300, 350, 400, 450)


class Check(lib.Hooks):
    def __init__(self):
        self.snap = {}
        self.cnt = {s: Counter() for s in "AB"}
        self.bucket_counts = {}
        self.bad_steps = 0
        self.steps = 0
        self.portal_steps = 0
        self.prev_head = {}
        self.hit = set()

    def round_start(self, g, r):
        if r in BUCKETS:
            self.take(g, r)

    def take(self, g, label):
        for s in "AB":
            mine = [b for d, b in g.bodies.items() if g.teams[d] == s]
            q = g.bodies.get(g.board.queen[s])
            self.snap[(label, s)] = dict(units=len(mine), total_length=sum(map(len, mine)),
                                         longest_length=max(map(len, mine), default=0),
                                         queen_alive=int(q is not None), queen_length=len(q) if q else 0)
            self.bucket_counts[(label, s)] = dict(self.cnt[s])
            self.cnt[s] = Counter()

    def action(self, g, did, kind, nsteps):
        self.prev_head[did] = g.bodies[did][0]
        self.hit.discard(did)
        if kind == 2:
            self.cnt[g.teams[did]]["suicides"] += 1

    def moved(self, g, did, head, step_index, ate):
        if did != g.current or not g.act_dirs:
            return
        d = g.act_dirs[step_index - 1]
        want = g.board.step(self.prev_head[did], d)
        self.steps += 1
        if want != head:
            self.bad_steps += 1
        x, y = self.prev_head[did]
        if abs(head[0] - x) + abs(head[1] - y) != 1 and want == head:
            self.portal_steps += 1  # wrap or portal
        self.prev_head[did] = head

    def eat(self, g, did, cell, origin):
        self.cnt[g.teams[did]]["pearls_" + origin[0]] += 1

    def death(self, g, did, reason, length, body, actor):
        s = g.teams[did]
        self.cnt[s]["deaths_" + ("other" if reason == "noaction" else reason)] += 1
        if reason == "headon" and actor is not None and actor != did and g.teams[actor] != s and actor not in self.hit:
            self.cnt[g.teams[actor]]["headon_initiated"] += 1
            self.hit.add(actor)

    def end(self, g, rounds, winner, result):
        self.rounds, self.winner = rounds, winner
        self.take(g, "end")


def main():
    rows = {}
    games = {}
    with open("games.csv") as f:
        for r in csv.DictReader(f):
            games[r["game_id"]] = r
    with open("timeline.csv") as f:
        for r in csv.DictReader(f):
            if r["game_id"] in sys.argv[1:]:
                rows[(r["game_id"], r["bucket"], r["side"])] = r
    for gid in sys.argv[1:]:
        gm = games[gid]
        c = Check()
        g = lib.Walk(gm["replay_path"])
        g.run(c)
        print(f"== game {gid} {gm['map']} {gm['width']}x{gm['height']} rounds {c.rounds} (csv {gm['rounds']}) "
              f"winner {c.winner} (csv {gm['winner']})")
        print(f"   move steps checked {c.steps}, mispredicted {c.bad_steps}, wrap/portal steps {c.portal_steps}, "
              f"portal edges {len(g.board.portal_pair)}, kelp edges {len(g.board.kelp)}")
        diffs = 0
        compared = 0
        for (label, s), mine in sorted(c.snap.items(), key=lambda kv: str(kv[0])):
            row = rows.get((gid, str(label), s))
            if row is None:
                continue
            counts = c.bucket_counts[(label, s)]
            mine = dict(mine)
            for k in ("suicides", "pearls_natural", "pearls_corpse", "deaths_wall", "deaths_self", "deaths_body",
                      "deaths_headon", "deaths_other"):
                mine[k] = counts.get(k, 0)
            mine["headon_initiated"] = counts.get("headon_initiated", 0)
            row = dict(row)
            row["headon_initiated"] = sum(int(row["headon_initiated_" + c2]) for c2 in ("le4", "5_9", "10plus"))
            for k, v in mine.items():
                compared += 1
                if int(float(row[k])) != v:
                    diffs += 1
                    print(f"   DIFF bucket {label} side {s} {k}: mine {v} csv {row[k]}")
        print(f"   compared {compared} values, {diffs} differ")
        for label in (100, 300, "end"):
            for s in "AB":
                if (label, s) in c.snap:
                    print(f"   r{label} {s}: {c.snap[(label, s)]} {c.bucket_counts[(label, s)]}")


if __name__ == "__main__":
    main()
