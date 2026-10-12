#!/usr/bin/env python3
"""Close-reading tools for one replay (read-only).

  python3 story.py summary <game_id>                      phase table, queen fate, biggest dragons, feeding, rams
  python3 story.py track <game_id> <id,id,...> [every]     position/length/nearby heads of chosen dragons
  python3 story.py view <game_id> <round> <x> <y> [rad]    ASCII board around a cell at the START of that round
  python3 story.py events <game_id> <r1> <r2> [x y rad]    every action/death/split in rounds r1..r2 (optionally near a cell)
  python3 story.py queen <game_id> <A|B> [every]           the queen's round-by-round line (pos, len, threats, escorts)

Coordinates: x east, y south (y grows downward), the board wraps. Team A / B as in the replay; the queen is the
lowest id of each team (0 or 1). Dragons act in id order within a round. "path" distances respect kelp and portals.
View legend: A/B = heads (Q/q... see below), a/b = bodies, * pearl, | and - kelp, O portal, digits/@ = heads of
the two queens: '@' queen of A, '&' queen of B.
"""
import csv
import sys
from collections import Counter, defaultdict

import lib

GAMES = {g["game_id"]: g for g in csv.DictReader(open(__file__.rsplit("/", 1)[0] + "/games.csv"))}


def info(gid):
    g = GAMES[gid]
    return g


def header(gid, b):
    g = info(gid)
    print(f"game {gid} | {g['map']} {b.w}x{b.h} | A = {g['teamAName']} ({g['teamAId']}, elo {g['teamAElo']}) "
          f"B = {g['teamBName']} ({g['teamBId']}, elo {g['teamBElo']}) | winner {g['winner']} by {g['end_type']} "
          f"| rounds {g['rounds']} | queens: A=#{b.queen['A']} B=#{b.queen['B']}")


class Summary(lib.Hooks):
    def __init__(self):
        self.rows = []
        self.maxlen = Counter()
        self.born = {}
        self.dead = {}
        self.team = {}
        self.sui = defaultdict(Counter)
        self.rams = defaultdict(Counter)
        self.splits = defaultdict(Counter)
        self.qlog = {"A": [], "B": []}
        self.bigdeaths = []
        self.eats = defaultdict(Counter)
        self.longest_id = {}

    def round_start(self, g, r):
        b = g.board
        for d, body in g.bodies.items():
            if len(body) > self.maxlen[d]:
                self.maxlen[d] = len(body)
            self.team[d] = g.teams[d]
            self.born.setdefault(d, r)
        for s in "AB":
            mine = sorted(((len(body), -d) for d, body in g.bodies.items() if g.teams[d] == s), reverse=True)
            self.longest_id[s] = -mine[0][1] if mine else None
        if r % 25 == 0:
            row = [r]
            for s in "AB":
                mine = sorted((len(body) for d, body in g.bodies.items() if g.teams[d] == s), reverse=True)
                q = g.bodies.get(b.queen[s])
                row.append((len(mine), sum(mine), mine[:3], len(q) if q else 0, q[0] if q else None))
            self.rows.append(row)

    def action(self, g, did, kind, nsteps):
        if kind == 2:
            s = g.teams[did]
            b = g.board
            head = g.bodies[did][0]
            lid = self.longest_id.get(s)
            near_l = lid in g.bodies and lid != did and b.manhattan(head, g.bodies[lid][0]) <= 6
            q = g.bodies.get(b.queen[s])
            near_q = q is not None and b.queen[s] != did and b.manhattan(head, q[0]) <= 6
            self.sui[(s, g.round // 50)]["n"] += 1
            self.sui[(s, g.round // 50)]["nearQ"] += near_q
            self.sui[(s, g.round // 50)]["nearLongest"] += near_l

    def split(self, g, parent, child, before, plen, clen):
        s = g.teams[parent]
        self.splits[(s, g.round // 50)]["n"] += 1
        if parent == g.board.queen[s]:
            self.qlog[s].append(f"r{g.round} queen split {before}->{plen}+{clen} at {g.bodies[parent][0]}")

    def eat(self, g, did, cell, origin):
        s = g.teams[did]
        b = g.board
        role = "queen" if did == b.queen[s] else "longest" if did == self.longest_id.get(s) else "other"
        src = origin[0] if origin[0] != "corpse" else ("own_" if origin[1] == s else "enemy_") + origin[3]
        self.eats[(s, g.round // 100)][f"{role}:{src}"] += 1

    def death(self, g, did, reason, length, body, actor):
        s = g.teams[did]
        b = g.board
        self.dead[did] = g.round
        if reason == "headon" and actor is not None and actor != did:
            a = g.teams[actor]
            self.rams[(a, g.round // 50)]["n" if a != s else "own_team"] += 1
        if did == b.queen[s]:
            who = ""
            if reason == "headon" and actor is not None and actor != did:
                who = f" by #{actor} (team {g.teams[actor]}, len {g.act_start[1]}, started its move at {g.act_start[0]}, step {g.step_index + 1} of {g.act_steps})"
            elif reason == "headon":
                who = " (the queen moved into a head herself)"
            self.qlog[s].append(f"r{g.round} QUEEN DIED: {reason}{who}, len {length}, at {body[0]}")
        if length >= 10:
            klen = g.act_start[1] if (reason == "headon" and actor is not None and actor != did) else None
            self.bigdeaths.append((g.round, s, did, length, reason, klen, body[0]))

    def end(self, g, rounds, winner, result):
        self.rounds = rounds
        self.final = {d: len(body) for d, body in g.bodies.items()}


def cmd_summary(gid):
    g = lib.Walk(info(gid)["replay_path"])
    x = Summary()
    g.run(x)
    b = g.board
    header(gid, b)
    print("\nround |  A: units total top3 queen(len@pos)            |  B: units total top3 queen(len@pos)")
    for row in x.rows:
        cells = []
        for u, t, top, ql, qp in row[1:]:
            cells.append(f"{u:3d} {t:4d} {str(top):14s} q={ql}@{qp}")
        print(f"{row[0]:5d} |  {cells[0]:44s} |  {cells[1]}")
    print("\nqueen logs:")
    for s in "AB":
        for line in x.qlog[s][:40]:
            print(f"  {s}: {line}")
        if not any("DIED" in line for line in x.qlog[s]):
            print(f"  {s}: queen alive at the end (len {x.final.get(b.queen[s], 0)})")
    print("\nper 50 rounds: splits / suicides (near own queen, near own longest) / enemy heads rammed by us")
    for s in "AB":
        print(f"  {s}: " + " | ".join(
            f"r{k * 50}: sp{x.splits[(s, k)]['n']} su{x.sui[(s, k)]['n']}(Q{x.sui[(s, k)]['nearQ']},L{x.sui[(s, k)]['nearLongest']}) ram{x.rams[(s, k)]['n']}"
            for k in range((x.rounds + 49) // 50)))
    print("\nwho ate what, per 100 rounds (role:source):")
    for s in "AB":
        for k in range((x.rounds + 99) // 100):
            print(f"  {s} r{k * 100}: {dict(x.eats[(s, k)].most_common(10))}")
    print("\nbiggest dragons ever (id, team, born, died, max len, final len):")
    for d, m in x.maxlen.most_common(10):
        print(f"  #{d} team {x.team[d]} born r{x.born[d]} died {('r%d' % x.dead[d]) if d in x.dead else '-'} max {m} final {x.final.get(d, 0)}")
    print("\ndeaths of dragons >= 10 long (round, team, id, len, reason, killer len, at):")
    for row in x.bigdeaths[:40]:
        print("  ", row)


class Track(lib.Hooks):
    def __init__(self, ids, every):
        self.ids, self.every = ids, every

    def round_start(self, g, r):
        if r % self.every:
            return
        b = g.board
        for d in self.ids:
            body = g.bodies.get(d)
            if body is None:
                continue
            s = g.teams[d]
            dist = b.bfs(body[0], 8)
            en = sorted((dist[o[0]], len(o), i) for i, o in g.bodies.items() if g.teams[i] != s and o[0] in dist)
            al = sorted((dist[o[0]], len(o), i) for i, o in g.bodies.items() if g.teams[i] == s and i != d and o[0] in dist)
            print(f"r{r:3d} #{d} {s} len {len(body):3d} head {body[0]} ball4 {b.ball(body[0])} "
                  f"enemies<=8 {[(x[0], 'L%d' % x[1], '#%d' % x[2]) for x in en[:5]]} allies<=8 {[(x[0], 'L%d' % x[1]) for x in al[:5]]}")

    def split(self, g, parent, child, before, plen, clen):
        if parent in self.ids:
            print(f"r{g.round:3d} #{parent} SPLIT {before}->{plen}+{clen} child #{child}")

    def death(self, g, did, reason, length, body, actor):
        if did in self.ids:
            print(f"r{g.round:3d} #{did} DIED {reason} len {length} at {body[0]} actor #{actor} "
                  f"{'(len %d from %s)' % (g.act_start[1], g.act_start[0]) if actor is not None and actor != did else ''}")
        elif actor in self.ids and reason == "headon":
            print(f"r{g.round:3d} #{actor} RAMMED #{did} (team {g.teams[did]}, len {length}) at {body[0]}")

    def eat(self, g, did, cell, origin):
        if did in self.ids and origin[0] == "corpse" and self.every <= 2:
            print(f"r{g.round:3d} #{did} ate corpse pearl of team {origin[1]} ({origin[3]}) at {cell}")


def cmd_track(gid, ids, every=10):
    g = lib.Walk(info(gid)["replay_path"])
    header(gid, g.board)
    g.run(Track([int(i) for i in ids.split(",")], int(every)))


def cmd_queen(gid, side, every=5):
    g = lib.Walk(info(gid)["replay_path"])
    header(gid, g.board)
    g.run(Track([g.board.queen[side]], int(every)))


class Stop(Exception):
    pass


class View(lib.Hooks):
    def __init__(self, rnd, cx, cy, rad):
        self.rnd, self.cx, self.cy, self.rad = rnd, cx, cy, rad

    def round_start(self, g, r):
        if r != self.rnd:
            return
        b = g.board
        w, h = b.w, b.h
        occ = {}
        for d, body in g.bodies.items():
            s = g.teams[d]
            for k, c in enumerate(body):
                if k == 0:
                    occ[c] = ("@" if s == "A" else "&") if d == b.queen[s] else s
                else:
                    occ.setdefault(c, s.lower())
        rad = self.rad
        print(f"round {r} start, centre ({self.cx},{self.cy}), radius {rad}; rows are y, columns x")
        print("     " + "".join(f"{(self.cx + dx) % w:2d}" for dx in range(-rad, rad + 1)))
        for dy in range(-rad, rad + 1):
            y = (self.cy + dy) % h
            top, mid = "     ", f"{y:3d}  "
            for dx in range(-rad, rad + 1):
                x = (self.cx + dx) % w
                ek = (x, y, "N")
                top += "+" + ("-" if ek in b.kelp else "O" if ek in b.portal_pair else " ")
                wk = (x, y, "W")
                mid += ("|" if wk in b.kelp else "O" if wk in b.portal_pair else " ")
                mid += occ.get((x, y), "*" if (x, y) in g.pearls else ".")
            print(top)
            print(mid)
        heads = []
        for d, body in g.bodies.items():
            if b.cheb(body[0], (self.cx, self.cy)) <= rad:
                heads.append(f"#{d}{g.teams[d]} L{len(body)} head{body[0]}")
        print("heads in view:", "; ".join(heads))
        raise Stop


def cmd_view(gid, rnd, x, y, rad=8):
    g = lib.Walk(info(gid)["replay_path"])
    header(gid, g.board)
    try:
        g.run(View(int(rnd), int(x), int(y), int(rad)))
    except Stop:
        pass


class Events(lib.Hooks):
    def __init__(self, r1, r2, near):
        self.r1, self.r2, self.near = r1, r2, near

    def ok(self, g, cell):
        if not (self.r1 <= g.round <= self.r2):
            return False
        if self.near is None:
            return True
        x, y, rad = self.near
        return g.board.cheb(cell, (x, y)) <= rad

    def round_start(self, g, r):
        if r > self.r2:
            raise Stop

    def action(self, g, did, kind, nsteps):
        body = g.bodies[did]
        if self.ok(g, body[0]):
            what = ("move " + "".join("NESW"[d] for d in g.act_dirs)) if kind == 0 else "SPLIT" if kind == 1 else "SUICIDE"
            print(f"r{g.round:3d} #{did}{g.teams[did]} L{len(body)} at {body[0]} {what}")

    def death(self, g, did, reason, length, body, actor):
        if self.ok(g, body[0]):
            print(f"r{g.round:3d}    -> #{did}{g.teams[did]} L{length} DIES ({reason}) at {body[0]}"
                  + (f" rammed by #{actor}{g.teams[actor]}" if reason == "headon" and actor is not None and actor != did else ""))

    def eat(self, g, did, cell, origin):
        if self.ok(g, cell):
            print(f"r{g.round:3d}    -> #{did}{g.teams[did]} eats {origin[0]} pearl at {cell}"
                  + (f" (from team {origin[1]} #{origin[2]} {origin[3]})" if origin[0] == "corpse" else ""))

    def split(self, g, parent, child, before, plen, clen):
        if self.ok(g, g.bodies[parent][0]):
            print(f"r{g.round:3d}    -> #{parent} split {before}->{plen}+{clen}, child #{child} head {g.bodies[child][0]}")


def cmd_events(gid, r1, r2, x=None, y=None, rad=None):
    g = lib.Walk(info(gid)["replay_path"])
    header(gid, g.board)
    near = (int(x), int(y), int(rad)) if rad is not None else None
    try:
        g.run(Events(int(r1), int(r2), near))
    except Stop:
        pass


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    globals()["cmd_" + sys.argv[1]](*sys.argv[2:])
