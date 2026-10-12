#!/usr/bin/env python3
"""b_turn.py <game_id> <round> <dragon_id> [radius=5]: the board at the START OF ONE DRAGON'S TURN (sub-session A2).

story.py view draws the board at the start of a round. A ram chance is judged at the start of the attacker's own
turn, after both queens and every lower id have moved. This prints the same ASCII board at that moment, centred
between the dragon and the enemy queen, then the dragon's order and what happened to it.
Legend as in story.py: '@' queen of A, '&' queen of B, 'A'/'B' heads, 'a'/'b' bodies, '*' pearl, '|' '-' kelp,
'O' portal; the acting dragon's head is shown as 'X' and its body as 'x'.
"""
import csv
import sys

import lib

GAMES = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
gid, rnd, did = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
rad = int(sys.argv[4]) if len(sys.argv) > 4 else 5


class Stop(Exception):
    pass


class T(lib.Hooks):
    def __init__(self):
        self.done = False

    def round_start(self, g, r):
        if r > rnd + 1:
            raise Stop

    def action(self, g, d, kind, nsteps):
        if g.round != rnd or d != did or self.done:
            return
        self.done = True
        b = g.board
        s = g.teams[d]
        o = "B" if s == "A" else "A"
        me = g.bodies[d]
        q = g.bodies.get(b.queen[o])
        cx, cy = me[0]
        w, h = b.w, b.h
        occ = {}
        for i, body in g.bodies.items():
            t = g.teams[i]
            for k, c in enumerate(body):
                if i == d:
                    occ[c] = "X" if k == 0 else "x"
                elif k == 0:
                    occ[c] = ("@" if t == "A" else "&") if i == b.queen[t] else t
                else:
                    occ.setdefault(c, t.lower())
        print(f"game {gid} {GAMES[gid]['map']} round {rnd}, turn of #{d} (team {s}, L{len(me)}) at {me[0]}; enemy queen #{b.queen[o]} "
              f"{'L%d at %s' % (len(q), q[0]) if q else 'dead'}; path distance (bodies ignored) {b.bfs(me[0], 20).get(q[0]) if q else '-'}; cheb {b.cheb(me[0], q[0]) if q else '-'}")
        print("     " + "".join(f"{(cx + dx) % w:2d}" for dx in range(-rad, rad + 1)))
        for dy in range(-rad, rad + 1):
            y = (cy + dy) % h
            top, mid = "     ", f"{y:3d}  "
            for dx in range(-rad, rad + 1):
                x = (cx + dx) % w
                top += "+" + ("-" if (x, y, "N") in b.kelp else "O" if (x, y, "N") in b.portal_pair else " ")
                mid += ("|" if (x, y, "W") in b.kelp else "O" if (x, y, "W") in b.portal_pair else " ")
                mid += occ.get((x, y), "*" if (x, y) in g.pearls else ".")
            print(top)
            print(mid)
        what = ("move " + "".join("NESW"[k] for k in g.act_dirs)) if kind == 0 else "SPLIT" if kind == 1 else "SUICIDE"
        print(f"its order: {what}")

    def death(self, g, d, reason, length, body, actor):
        if g.round == rnd and (d == did or actor == did):
            print(f"  r{g.round}: #{d} (team {g.teams[d]}, L{length}) dies ({reason}) at {body[0]}" + (f", actor #{actor}" if actor is not None else ""))


try:
    lib.Walk(GAMES[gid]["replay_path"]).run(T())
except Stop:
    pass
