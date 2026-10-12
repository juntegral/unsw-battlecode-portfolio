#!/usr/bin/env python3
"""b_map.py <game_id> <round> [block=8]: coarse map of one round (sub-session A2).

The board is cut into block x block squares. For each square: natural pearls lying there / heads of team A / heads
of team B at the start of the round (a dot = nothing). 'a' or 'b' after a cell marks the queen's square, 'S'/'s' the
spawn square of A / B. Also prints, for each team, how many of the squares hold at least one own head.
"""
import csv
import sys

import lib

GAMES = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
gid, rnd = sys.argv[1], int(sys.argv[2])
blk = int(sys.argv[3]) if len(sys.argv) > 3 else 8
info = GAMES[gid]


class Stop(Exception):
    pass


class M(lib.Hooks):
    def round_start(self, g, r):
        if r != rnd:
            return
        b = g.board
        nx, ny = -(-b.w // blk), -(-b.h // blk)
        pe = [[0] * nx for _ in range(ny)]
        ha = [[0] * nx for _ in range(ny)]
        hb = [[0] * nx for _ in range(ny)]
        for c, v in g.pearls.items():
            if v[0] == "natural":
                pe[c[1] // blk][c[0] // blk] += 1
        q = {}
        for d, body in g.bodies.items():
            h = body[0]
            (ha if g.teams[d] == "A" else hb)[h[1] // blk][h[0] // blk] += 1
            if d == b.queen[g.teams[d]]:
                q[g.teams[d]] = (h[0] // blk, h[1] // blk)
        sp = {s: (b.starts[b.queen[s]][0] // blk, b.starts[b.queen[s]][1] // blk) for s in "AB"}
        print(f"game {gid} {info['map']} round {r}: A = {info['teamAName']} B = {info['teamBName']}; squares of {blk}x{blk}; each cell = natural pearls / A heads / B heads")
        print("      " + "".join(f"x{x * blk:<9d}" for x in range(nx)))
        for y in range(ny):
            row = f"y{y * blk:<4d} "
            for x in range(nx):
                mark = ("a" if q.get("A") == (x, y) else "") + ("b" if q.get("B") == (x, y) else "") + ("S" if sp["A"] == (x, y) else "") + ("s" if sp["B"] == (x, y) else "")
                cell = f"{pe[y][x] or '.'}/{ha[y][x] or '.'}/{hb[y][x] or '.'}{mark}"
                row += f"{cell:<10s}"
            print(row)
        for s, hh in (("A", ha), ("B", hb)):
            occ = sum(1 for y in range(ny) for x in range(nx) if hh[y][x])
            alone = sum(pe[y][x] for y in range(ny) for x in range(nx) if hh[y][x] and not (hb if s == "A" else ha)[y][x])
            print(f"  team {s}: heads in {occ} of {nx * ny} squares; natural pearls lying in squares where only this team has a head: {alone}")
        print(f"  natural pearls on the board: {sum(map(sum, pe))}; in squares with no head at all: {sum(pe[y][x] for y in range(ny) for x in range(nx) if not ha[y][x] and not hb[y][x])}")
        raise Stop


try:
    lib.Walk(info["replay_path"]).run(M())
except Stop:
    pass
