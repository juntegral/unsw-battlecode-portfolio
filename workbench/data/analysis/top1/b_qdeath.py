#!/usr/bin/env python3
"""b_qdeath.py <team_id> [list]: every death of the team's queen that was NOT a ram, over all games (sub-session A2).

Games against 2000+ teams, Schooltime left out; the games are picked from q/<id>.json (qdeath reason not 'headon',
or 'headon' where the queen herself moved into a head). Each replay is walked up to the death. At the start of the
queen's fatal turn it records: her length, the order (move with its steps / split / suicide), how many of the four
neighbour cells were free, what blocked the others (kelp / her own body / a team-mate's body / an enemy body),
whether an enemy head was within 3 path steps, the round, and her last split before that (rounds ago, kind).
Prints the cross-tables and, with "list", one line per death.
"""
import csv
import json
import os
import sys
from collections import Counter

import lib

HERE = os.path.dirname(os.path.abspath(__file__))
tid = sys.argv[1]
want = len(sys.argv) > 2 and sys.argv[2] == "list"
games = {g["game_id"]: g for g in csv.DictReader(open(os.path.join(HERE, "games.csv")))}
todo = []
for gid, g in games.items():
    if g["map"] == "Schooltime":
        continue
    side = "A" if g["teamAId"] == tid else "B" if g["teamBId"] == tid else None
    if side is None:
        continue
    op = "B" if side == "A" else "A"
    try:
        if float(g["team%sElo" % op]) < 2000:
            continue
    except ValueError:
        continue
    p = os.path.join(HERE, "q", gid + ".json")
    if not os.path.exists(p):
        continue
    q = json.load(open(p))
    qd = q["sides"][side].get("qdeath")
    if qd and (qd["reason"] != "headon" or not qd.get("killer")):
        todo.append((gid, side, qd["round"], qd["reason"]))


class Stop(Exception):
    pass


class H(lib.Hooks):
    def __init__(self, side, R):
        self.side, self.R = side, R
        self.rec = None
        self.lastsplit = None

    def round_start(self, g, r):
        if r > self.R:
            raise Stop

    def split(self, g, parent, child, before, plen, clen):
        if parent == g.board.queen[self.side]:
            self.lastsplit = (g.round, before, plen, clen)

    def action(self, g, did, kind, nsteps):
        b = g.board
        if g.round != self.R or did != b.queen[self.side]:
            return
        body = list(g.bodies[did])
        head = body[0]
        free = kelp = own = mate = foe = 0
        for d in range(4):
            c = b.step(head, d)
            if c is None:
                kelp += 1
            elif c in body:
                own += 1
            else:
                occ = [g.teams[i] for i, o in g.bodies.items() if i != did and c in o]
                if not occ:
                    free += 1
                elif occ[0] == self.side:
                    mate += 1
                else:
                    foe += 1
        dist = b.bfs(head, 3)
        near = any(g.teams[i] != self.side and o[0] in dist for i, o in g.bodies.items())
        self.rec = dict(len=len(body), kind=kind, dirs="".join("NESW"[x] for x in g.act_dirs), free=free, kelp=kelp, own=own, mate=mate, foe=foe,
                        near=near, ball=b.ball(head), head=head)


rows = []
for gid, side, R, reason in todo:
    h = H(side, R)
    try:
        lib.Walk(games[gid]["replay_path"]).run(h)
    except Stop:
        pass
    if h.rec:
        h.rec.update(gid=gid, map=games[gid]["map"], r=R, reason=reason, lastsplit=h.lastsplit)
        rows.append(h.rec)
print(f"team {tid}: {len(rows)} queen deaths that were not a ram by an enemy")


def tab(name, key):
    c = Counter(key(x) for x in rows)
    print(f"  by {name}: {dict(sorted(c.items(), key=lambda kv: str(kv[0])))}")


tab("reason", lambda x: x["reason"])
tab("free neighbour cells at the start of her fatal turn", lambda x: x["free"])
tab("her length", lambda x: "2" if x["len"] == 2 else "3" if x["len"] == 3 else "4-9" if x["len"] <= 9 else "10+")
tab("her order", lambda x: "split" if x["kind"] == 1 else "suicide" if x["kind"] == 2 else "move %d steps" % len(x["dirs"]))
tab("an enemy head within 3 steps", lambda x: x["near"])
tab("what blocked her (kelp, own body, team-mate, enemy body)", lambda x: f"kelp {x['kelp']} own {x['own']} mate {x['mate']} enemy {x['foe']} free {x['free']}")
tab("blocked by a team-mate's body on at least one side (boxed cases only)", lambda x: "n/a" if x["free"] else ("yes" if x["mate"] else "no"))
tab("she had split in the 20 rounds before", lambda x: bool(x["lastsplit"] and x["r"] - x["lastsplit"][0] <= 20))
tab("round", lambda x: "0-99" if x["r"] < 100 else "100-299" if x["r"] < 300 else "300+")
tab("map", lambda x: x["map"])
if want:
    for x in sorted(rows, key=lambda x: (x["gid"])):
        print(f"    {x['gid']} {x['map']} r{x['r']} {x['reason']} L{x['len']} at {x['head']} order {'split' if x['kind'] == 1 else 'suicide' if x['kind'] == 2 else 'move ' + x['dirs']}; free {x['free']} kelp {x['kelp']} own {x['own']} mate {x['mate']} enemy {x['foe']}; enemy head within 3: {x['near']}; last split {x['lastsplit']}")
