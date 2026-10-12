#!/usr/bin/env python3
"""Dump raw sonarPing fields for a game: python3 sonarpeek.py <game_id> [team A|B] [max]"""
import csv
import sys
from collections import Counter

import lib

GAMES = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}


class S(lib.Hooks):
    def __init__(self, side, limit):
        self.side, self.limit, self.n = side, limit, 0
        self.values = Counter()
        self.per_round = Counter()
        self.shown = 0

    def sonar(self, g, sender, value, raw):
        s = g.teams.get(sender)
        if self.side and s != self.side:
            return
        self.n += 1
        self.values[(s, value != 0)] += 1
        self.per_round[(s, g.round // 100)] += 1
        if self.shown < self.limit and value != 0:
            self.shown += 1
            fields = [raw.i32(0), raw.i32(4), raw.u32(8), raw.u32(12), raw.u64(16), raw.dwords, raw.pwords]
            pts = [lib.rp.point(raw.pointer(k)) if raw.pwords > k and raw.pointer(k) is not None and hasattr(raw.pointer(k), "i32") else None for k in range(raw.pwords)]
            body = g.bodies.get(sender)
            print(f"r{g.round} sender #{sender}{s} len {len(body) if body else '?'} head {body[0] if body else None} "
                  f"raw i32@0={fields[0]} i32@4={fields[1]} u32@8={fields[2]} u32@12={fields[3]} u64@16={fields[4]:#018x} "
                  f"dwords={fields[5]} pwords={fields[6]} points={pts}")


gid = sys.argv[1]
side = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] in "AB" else None
x = S(side, int(sys.argv[3]) if len(sys.argv) > 3 else 12)
lib.Walk(GAMES[gid]["replay_path"]).run(x)
print("pings (team, nonzero):", dict(x.values))
print("pings per 100 rounds:", dict(sorted(x.per_round.items())))
