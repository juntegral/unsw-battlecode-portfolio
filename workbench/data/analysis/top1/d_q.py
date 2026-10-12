#!/usr/bin/env python3
"""d_q.py <game_id> <A|B> [view=r1,r2,...] [rad=5] [from=R]: one queen's whole game on one page (sub-session A4).

  header      map, teams, result, both queens' start cells and the path distance between them
  life table  per 25 rounds: head cell at the block start, path distance from her start cell, length, pearls eaten
              in the block (natural / corpse), her splits, rounds with an enemy head in her 7x7 view, the nearest
              enemy head (path steps, bodies ignored) in the block, distinct cells used, own heads within 4 cells
              (mean), own / enemy units at the block start
  moves       every order from round `from` (default: 30 rounds before her death, or the last 30 rounds) with what
              she ate; '!' marks a turn that began with an enemy head in view, and the number after it is the path
              distance to the nearest one
  last turns  from d_out/cls/<id>.json when present: free / safe one-step moves, what each side of her head was
  views       the board at the START OF HER OWN TURN in the rounds given with view= (default: her last turn and
              three turns before it).  Legend: '@' queen of A, '&' queen of B, A/B heads, a/b bodies, '*' pearl,
              '|' '-' kelp, 'O' portal.  Rows are y (south is down), columns x.
"""
import csv
import json
import os
import sys
from collections import Counter, deque

import lib

HERE = os.path.dirname(os.path.abspath(__file__))
GAMES = {g["game_id"]: g for g in csv.DictReader(open(os.path.join(HERE, "games.csv")))}


def full_bfs(b, src):
    dist = {src: 0}
    q = deque([src])
    while q:
        c = q.popleft()
        for n in b.nb(c):
            if n is not None and n not in dist:
                dist[n] = dist[c] + 1
                q.append(n)
    return dist


def draw(g, centre, rad, mark=None):
    b = g.board
    w, h = b.w, b.h
    cx, cy = centre
    occ = {}
    for d, body in g.bodies.items():
        s = g.teams[d]
        for k, c in enumerate(body):
            if k == 0:
                occ[c] = ("@" if s == "A" else "&") if d == b.queen[s] else s
            else:
                occ.setdefault(c, s.lower())
    out = ["     " + "".join(f"{(cx + dx) % w:2d}" for dx in range(-rad, rad + 1))]
    for dy in range(-rad, rad + 1):
        y = (cy + dy) % h
        top, mid = "     ", f"{y:3d}  "
        for dx in range(-rad, rad + 1):
            x = (cx + dx) % w
            top += "+" + ("-" if (x, y, "N") in b.kelp else "O" if (x, y, "N") in b.portal_pair else " ")
            mid += ("|" if (x, y, "W") in b.kelp else "O" if (x, y, "W") in b.portal_pair else " ")
            mid += occ.get((x, y), "*" if (x, y) in g.pearls else ".")
        out.append(top)
        out.append(mid)
    heads = []
    for d, body in g.bodies.items():
        if b.cheb(body[0], centre) <= rad:
            heads.append(f"#{d}{g.teams[d]} L{len(body)} {body[0]}")
    out.append("heads: " + "; ".join(heads))
    return "\n".join(out)


class Q(lib.Hooks):
    def __init__(self, side, views, rad):
        self.side, self.views, self.rad = side, set(views), rad
        self.rows = []          # per round: (pos, len, nvis, mind, a4)
        self.eats = []          # (round, origin)
        self.splits = []
        self.orders = {}
        self.dead = None
        self.units = []
        self.pics = []
        self.dist = None
        self.auto = None

    def round_start(self, g, r):
        b = g.board
        s = self.side
        o = "B" if s == "A" else "A"
        if self.dist is None:
            self.dist = full_bfs(b, b.starts[b.queen[s]])
            self.gap = self.dist.get(b.starts[b.queen[o]], -1)
        own = sum(1 for d in g.bodies if g.teams[d] == s)
        self.units.append((own, len(g.bodies) - own))
        q = g.bodies.get(b.queen[s])
        if q is None:
            self.rows.append(None)
            return
        head = q[0]
        pd = b.bfs(head, 8)
        nvis = 0
        mind = 9
        a4 = 0
        for d, body in g.bodies.items():
            if d == b.queen[s]:
                continue
            if g.teams[d] != s:
                nvis += b.cheb(body[0], head) <= 3
                if body[0] in pd:
                    mind = min(mind, pd[body[0]])
            elif b.manhattan(body[0], head) <= 4:
                a4 += 1
        self.rows.append((head, len(q), nvis, mind, a4))

    def action(self, g, did, kind, nsteps):
        b = g.board
        if did != b.queen[self.side]:
            return
        r = g.round
        self.orders[r] = ("".join("NESW"[x] for x in g.act_dirs) if kind == 0 else "SPLIT" if kind == 1 else "none")
        if r in self.views:
            self.pics.append((r, draw(g, g.bodies[did][0], self.rad)))

    def eat(self, g, did, cell, origin):
        if did == g.board.queen[self.side]:
            self.eats.append((g.round, origin[0] if origin[0] != "corpse" else ("own" if origin[1] == self.side else "enemy") + " corpse"))

    def split(self, g, parent, child, before, plen, clen):
        if parent == g.board.queen[self.side]:
            self.splits.append((g.round, before, plen, clen, child))

    def death(self, g, did, reason, length, body, actor):
        if did == g.board.queen[self.side]:
            who = ""
            if reason == "headon" and actor is not None and actor != did:
                who = f" by #{actor}{g.teams[actor]} L{g.act_start[1]} from {g.act_start[0]} with {''.join('NESW'[x] for x in g.act_dirs)}"
            self.dead = (g.round, reason, length, body[0], who)

    def end(self, g, rounds, winner, result):
        self.rounds = rounds
        q = g.bodies.get(g.board.queen[self.side])
        self.final = len(q) if q else 0


def main():
    gid, side = sys.argv[1], sys.argv[2]
    views, rad, frm = None, 5, None
    for a in sys.argv[3:]:
        if a.startswith("view="):
            views = [int(x) for x in a[5:].split(",") if x]
        elif a.startswith("rad="):
            rad = int(a[4:])
        elif a.startswith("from="):
            frm = int(a[5:])
    info = GAMES[gid]
    qj = json.load(open(os.path.join(HERE, "q", gid + ".json")))
    qd = qj["sides"][side]["qdeath"]
    if views is None:
        if qd:
            last = qd["round"] if qd["own_action"] or (qd["killer"] and qd["killer"]["id"] > qj["sides"][side]["queen_id"]) else qd["round"] - 1
            views = [max(0, last - 3), last]
        else:
            views = []
    x = Q(side, views, rad)
    g = lib.Walk(info["replay_path"])
    g.run(x)
    b = g.board
    o = "B" if side == "A" else "A"
    print(f"=== {gid} {info['map']} {b.w}x{b.h} ({info['cells']} cells) run {info['battle_id']} | {side} = {info['team' + side + 'Name']} ({info['team' + side + 'Elo']}) "
          f"vs {info['team' + o + 'Name']} ({info['team' + o + 'Elo']}) | winner {info['winner']} by {info['end_type']} after {info['rounds']} rounds")
    print(f"queen #{b.queen[side]} start {b.starts[b.queen[side]]}; enemy queen #{b.queen[o]} start {b.starts[b.queen[o]]}; path between the starts {x.gap}")
    if x.dead:
        print(f"DEATH r{x.dead[0]} {x.dead[1]} L{x.dead[2]} at {x.dead[3]}{x.dead[4]}")
    else:
        print(f"ALIVE at the end, length {x.final}")
    print("splits (round, before -> keeps + child, child id):", " ".join(f"r{r}:{a}->{p}+{c}(#{ch})" for r, a, p, c, ch in x.splits) or "none")
    print("block | head | from start | len | ate nat/corpse | splits | rounds enemy in view | nearest enemy | cells used | own heads<=4 | units own/enemy")
    for k in range(0, x.rounds, 25):
        rows = [r for r in x.rows[k:k + 25] if r]
        if not rows:
            break
        h0 = rows[0][0]
        nat = sum(1 for r, og in x.eats if k <= r < k + 25 and og == "natural")
        cor = sum(1 for r, og in x.eats if k <= r < k + 25 and og != "natural")
        sp = sum(1 for s in x.splits if k <= s[0] < k + 25)
        print(f"r{k:3d} | {str(h0):9s} | {x.dist.get(h0, -1):3d} | {rows[0][1]:2d} | {nat}/{cor} | {sp} | {sum(1 for r in rows if r[2]):2d} | "
              f"{min(r[3] for r in rows)} | {len({r[0] for r in rows}):2d} | {sum(r[4] for r in rows) / len(rows):.1f} | {x.units[k][0]}/{x.units[k][1]}")
    end = x.dead[0] if x.dead else x.rounds - 1
    if frm is None:
        frm = max(0, end - 30)
    print(f"moves from round {frm}:")
    line = []
    eat_at = Counter(r for r, _ in x.eats)
    for r in range(frm, end + 1):
        row = x.rows[r] if r < len(x.rows) else None
        od = x.orders.get(r, "?")
        mark = f"!{row[3]}" if row and row[2] else ""
        line.append(f"{r}:{od}{'+' * eat_at[r]}{mark}")
        if len(line) == 12:
            print("   " + "  ".join(line))
            line = []
    if line:
        print("   " + "  ".join(line))
    p = os.path.join(HERE, "d_out", "cls", gid + ".json")
    if os.path.exists(p):
        sd = json.load(open(p))["sides"][side]
        if sd["death"]:
            print("death record:", json.dumps(sd["death"]))
        for t in sd["turns"][-8:]:
            sides = " ".join(f"{'NESW'[i]}={s[0]}" + (f"({s[1]},{s[2]}){'p' if s[3] else ''}" + (f" reach{s[4]} room{s[8]}" if s[0] in 'FP' and len(s) > 8 else f" #{s[4]}L{s[5]}s{s[6]}" if s[0] not in 'FP' else "") if s[0] != 'K' else "") for i, s in enumerate(t.get("sides", [])))
            en = " ".join(f"#{e[0]}L{e[1]}@({e[2]},{e[3]})c{e[4]}p{e[5]}{'V' if e[6] else ''}" for e in t["en"] if e[6] or e[5] <= 6)
            print(f"  r{t['r']} L{t['len']} at {tuple(t['head'])} {('move ' + t['dirs']) if t['kind'] == 0 else 'SPLIT' if t['kind'] == 1 else 'none'} -> {t['end']} ate {t['ate']} | free {t['nfree']} safe {t['nsafe']} | "
                  f"in reach at start {t['reach0']}, at end {t.get('end_reach')} | froom {t.get('froom')} tree {t.get('tree')} | {sides} | enemies {en}")
    for r, pic in x.pics:
        print(f"--- board at the start of her turn, round {r}")
        print(pic)


if __name__ == "__main__":
    main()
