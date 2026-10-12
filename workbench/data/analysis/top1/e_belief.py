#!/usr/bin/env python3
"""Which dragon does each of OUR dragons believe is the leader? Decoded from our own sonar pings in a replay.

Our bot sends its "known leader" (id, length, round heard, position, facing) on four sonar rays after every turn
(`broadcast_leader()` / `pack_leader()` in mybot2/main.cpp). In the ladder replays the fields are in the clear in the
low 53 bits of the ping value (bits 0-15 id with 0x8000 = "queen game" flag, 16-27 length, 28-36 round, 37-43 x,
44-50 y, 51-52 facing, 53-54 team tag, 55-62 a check byte, bit 63 = other message kinds).
No key is used or needed: this only reads fields our own bot wrote into the replay.

Usage: python3 e_belief.py <game_id> [rounds comma list]
Prints, per chosen round: the true top-4 own dragons, and how many of our dragons broadcast which leader id.
"""
import csv
import sys
from collections import Counter

import lib

GAMES = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
ME = "1119"


def decode(v):
    """Leader message fields, or None for other message kinds / zero."""
    if v == 0 or (v >> 63):
        return None
    return dict(id=v & 0x7FFF, qgame=bool(v & 0x8000), len=(v >> 16) & 0xFFF, when=(v >> 28) & 0x1FF,
                x=(v >> 37) & 0x7F, y=(v >> 44) & 0x7F, face=(v >> 51) & 3, tag=(v >> 53) & 3)


class B(lib.Hooks):
    def __init__(self, side, rounds):
        self.side, self.rounds = side, set(rounds)
        self.last = {}

    def round_start(self, g, r):
        if (r - 1) in self.rounds:
            self.report(g, r - 1)
        self.last = {}

    def sonar(self, g, sender, value, raw):
        if g.teams.get(sender) != self.side:
            return
        m = decode(value)
        if m is not None:
            self.last[sender] = m

    def end(self, g, rounds, winner, result):
        if (rounds - 1) in self.rounds:
            self.report(g, rounds - 1)

    def report(self, g, r):
        own = sorted(((len(b), d) for d, b in g.bodies.items() if g.teams[d] == self.side), reverse=True)
        en = sorted(((len(b), d) for d, b in g.bodies.items() if g.teams[d] != self.side), reverse=True)
        c = Counter()
        lens = {}
        stale = Counter()
        qg = 0
        for d, m in self.last.items():
            c[m["id"]] += 1
            lens.setdefault(m["id"], []).append(m["len"])
            stale[m["id"]] += r - m["when"]
            qg += m["qgame"]
        true_id = own[0][1] if own else None
        n = sum(c.values())
        print("r%d own units %d total %d top %s | enemy top %s | senders %d, believing the true longest #%s: %d; queen-game flag on %d" % (
            r, len(own), sum(x[0] for x in own), ["#%d L%d" % (d, L) for L, d in own[:4]],
            ["#%d L%d" % (d, L) for L, d in en[:3]], n, true_id, c.get(true_id, 0), qg))
        for lid, k in c.most_common(8):
            alive = lid in g.bodies
            print("      believed leader #%d: %d dragons, believed length %d-%d, true length %s, mean age of news %.1f rounds" % (
                lid, k, min(lens[lid]), max(lens[lid]), len(g.bodies[lid]) if alive else "dead", stale[lid] / k))


if __name__ == "__main__":
    gid = sys.argv[1]
    rounds = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [150, 200, 250, 300, 350, 400, 425, 450, 475, 499]
    g = GAMES[gid]
    side = "A" if g["teamAId"] == ME else "B"
    print("game", gid, g["map"], g["cells"], "cells |", g["battle_id"], "| meow is", side, "| vs", g["teamBName"] if side == "A" else g["teamAName"],
          "| winner", g["winner"], g["end_type"])
    lib.Walk(g["replay_path"]).run(B(side, rounds))
