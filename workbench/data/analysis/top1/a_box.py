#!/usr/bin/env python3
"""a_box.py <game_id> [team=306]: was the protagonist's queen boxed in when she split or died by `noaction`?

For every split of the protagonist's queen and for her death, prints what lies on each of the four neighbouring
cells of her head at the moment she acts: kelp (no step possible), her own body (segment number), another own-team
body, an enemy body, or free. Sub-session A.
"""
import csv
import json
import sys

import lib

GAMES = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
gid = sys.argv[1]
team = int(sys.argv[2]) if len(sys.argv) > 2 else 306
q = json.load(open(f"q/{gid}.json"))
me = [s for s in "AB" if q["sides"][s]["team"] == team][0]


class B(lib.Hooks):
    def action(self, g, did, kind, nsteps):
        b = g.board
        if did != b.queen[me] or kind == 0:
            return
        body = list(g.bodies[did])
        head = body[0]
        out = []
        free = 0
        for d in range(4):
            c = b.step(head, d)
            if c is None:
                out.append("NESW"[d] + ":kelp")
                continue
            if c in body:
                out.append(f"{'NESW'[d]}:own segment {body.index(c) + 1}")
                continue
            occ = [(i, g.teams[i]) for i, o in g.bodies.items() if i != did and c in o]
            if occ:
                i, t = occ[0]
                part = "head" if g.bodies[i][0] == c else "tail" if g.bodies[i][-1] == c else "body"
                out.append(f"{'NESW'[d]}:{'ally' if t == me else 'ENEMY'} #{i} L{len(g.bodies[i])} {part}")
            else:
                out.append("NESW"[d] + ":FREE")
                free += 1
        ball = b.ball(head)
        print(f"  {gid} {q['map']} r{g.round} queen L{len(body)} at {head} orders {'SPLIT' if kind == 1 else 'SUICIDE'}; free neighbours {free}; cells within 4 steps {ball}; " + ", ".join(out))

    def split(self, g, parent, child, before, plen, clen):
        if parent == g.board.queen[me]:
            print(f"      -> split {before} -> {plen}+{clen}")

    def death(self, g, did, reason, length, body, actor):
        if did == g.board.queen[me]:
            print(f"      -> queen dies r{g.round} ({reason}) L{length}")


lib.Walk(GAMES[gid]["replay_path"]).run(B())
