#!/usr/bin/env python3
"""Debug view of our own leader broadcasts in one round: raw ping values and the decoded fields per sender.
Usage: python3 e_belief2.py <game_id> <round> [max senders]
(see e_belief.py for the field layout; no key is used)"""
import csv
import sys

import lib
from e_belief import decode, GAMES, ME


class D(lib.Hooks):
    def __init__(self, side, rnd, limit):
        self.side, self.rnd, self.limit = side, rnd, limit
        self.rows = {}

    def sonar(self, g, sender, value, raw):
        if g.round != self.rnd or g.teams.get(sender) != self.side:
            return
        body = g.bodies.get(sender)
        self.rows.setdefault(sender, []).append((value, raw.i32(4) & 0xFFFF, (raw.i32(4) >> 16) & 0xFFFF, raw.u32(12),
                                                 len(body) if body else None, body[0] if body else None))

    def round_start(self, g, r):
        if r == self.rnd + 1:
            n = 0
            for d, rows in sorted(self.rows.items()):
                if n >= self.limit:
                    break
                n += 1
                for v, direction, hit, hid, L, head in rows:
                    m = decode(v)
                    print("#%d L%s head %s dir %d hit %d target #%d  value %#018x -> %s" % (d, L, head, direction, hit, hid, v, m))
            raise SystemExit


if __name__ == "__main__":
    gid, rnd = sys.argv[1], int(sys.argv[2])
    g = GAMES[gid]
    side = "A" if g["teamAId"] == ME else "B"
    lib.Walk(g["replay_path"]).run(D(side, rnd, int(sys.argv[3]) if len(sys.argv) > 3 else 12))
