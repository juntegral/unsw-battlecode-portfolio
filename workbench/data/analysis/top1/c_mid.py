#!/usr/bin/env python3
"""c_mid.py <game_id> <side A|B> [r1=140] [r2=220] [min_len=5] [--list]: the mid-game by length class, and dragon by dragon.

Part 1, both sides, per 50 rounds from r1 rounded down to r2: for the length classes 2, 3-4, 5-9, 10+:
  dragon-rounds; natural and corpse pearls eaten per 100 dragon-rounds; splits made (by parent length class);
  deaths: rammed / rammer / boxed / free-cell; mean path distance of heads from the own queen spawn;
  share of dragon-rounds with an enemy head in view (7x7); share of dragon-turns that moved 2+ steps.
Part 2 (--list), the chosen side: every dragon that was <min_len> or longer at some round in r1..r2: one line with
  its rounds in the window, length at start and end, natural / corpse pearls eaten, splits it made (before -> parent +
  child), different cells its head stood on, steps taken, rounds with an enemy head in view, how it ended (alive at r2,
  or death reason, round, cell, killer length), and its head position every 10 rounds.
"""
import sys
from collections import Counter, defaultdict

sys.dont_write_bytecode = True
import c_lib  # noqa: E402
from c_lib import GAMES, Hooks2, Stop, Walk2, tname  # noqa: E402

gid = sys.argv[1]
side = sys.argv[2]
nums = [a for a in sys.argv[3:] if a.lstrip("-").isdigit()]
r1 = int(nums[0]) if len(nums) > 0 else 140
r2 = int(nums[1]) if len(nums) > 1 else 220
min_len = int(nums[2]) if len(nums) > 2 else 5
do_list = "--list" in sys.argv
info = GAMES[gid]


def lc(n):
    return "2" if n <= 2 else "3-4" if n <= 4 else "5-9" if n <= 9 else "10+"


class M(Hooks2):
    def __init__(self):
        self.c = Counter()
        self.spawn = {}
        self.dspawn = {}
        self.dr = {}          # did -> record for the listed side
        self.cur = None

    def blk(self, r):
        return r // 50 * 50

    def rec(self, g, did):
        r = self.dr.get(did)
        if r is None:
            body = g.bodies[did]
            r = self.dr[did] = dict(first=g.round, len0=len(body), len1=len(body), nat=0, cor=0, splits=[], cells=set(), steps=0,
                                    ev=0, end=None, pos={}, maxlen=len(body), rounds=0, born=None, multi=0)
        return r

    def round_start(self, g, r):
        b = g.board
        if not self.spawn:
            for s in "AB":
                self.spawn[s] = b.starts[b.queen[s]]
                self.dspawn[s] = b.bfs(self.spawn[s], 10 ** 9)
        if r > r2:
            raise Stop
        if r < r1 // 50 * 50:
            return
        k = self.blk(r)
        heads = {s: [body[0] for d, body in g.bodies.items() if g.teams[d] == s] for s in "AB"}
        for d, body in g.bodies.items():
            s = g.teams[d]
            o = "B" if s == "A" else "A"
            cl = lc(len(body))
            self.c[(k, s, cl, "rounds")] += 1
            self.c[(k, s, cl, "dist")] += self.dspawn[s].get(body[0], 0)
            ev = any(b.cheb(body[0], c2) <= 3 for c2 in heads[o])
            if ev:
                self.c[(k, s, cl, "ev")] += 1
            if s == side and r >= r1:
                rec = self.rec(g, d)
                rec["rounds"] += 1
                rec["len1"] = len(body)
                rec["maxlen"] = max(rec["maxlen"], len(body))
                rec["cells"].add(body[0])
                rec["ev"] += ev
                if r % 10 == 0:
                    rec["pos"][r] = (body[0], len(body))

    def turn(self, g, did):
        self.cur = (did, len(g.bodies[did]))

    def action(self, g, did, kind, nsteps):
        if g.round < r1 // 50 * 50:
            return
        s = g.teams[did]
        cl = lc(len(g.bodies[did]))
        k = self.blk(g.round)
        self.c[(k, s, cl, "turns")] += 1
        if kind == 0 and nsteps >= 2:
            self.c[(k, s, cl, "multi")] += 1
            if s == side and did in self.dr:
                self.dr[did]["multi"] += 1

    def moved(self, g, did, head, step_index, ate):
        if g.teams[did] == side and did in self.dr and g.round >= r1:
            self.dr[did]["steps"] += 1

    def eat(self, g, did, cell, origin):
        if g.round < r1 // 50 * 50:
            return
        s = g.teams[did]
        L = self.cur[1] if self.cur and self.cur[0] == did else len(g.bodies[did])
        k = self.blk(g.round)
        self.c[(k, s, lc(L), "nat" if origin[0] == "natural" else "cor")] += 1
        if s == side and g.round >= r1 and did in self.dr:
            self.dr[did]["nat" if origin[0] == "natural" else "cor"] += 1

    def split(self, g, parent, child, before, plen, clen):
        if g.round < r1 // 50 * 50:
            return
        s = g.teams[parent]
        k = self.blk(g.round)
        self.c[(k, s, lc(before), "split")] += 1
        if s == side and g.round >= r1:
            if parent in self.dr:
                self.dr[parent]["splits"].append((g.round, before, plen, clen))
            if clen >= min_len or True:
                rec = self.rec(g, child)
                rec["born"] = (g.round, parent, clen)

    def death(self, g, did, reason, length, body, actor):
        if g.round < r1 // 50 * 50:
            return
        s = g.teams[did]
        k = self.blk(g.round)
        cl = lc(length)
        if reason == "headon":
            key = "rammer" if did == actor else "rammed"
        else:
            occ = c_lib.occupied(g)
            free = sum(1 for n in g.board.nb(body[0]) if n is not None and n not in occ)
            key = "boxed" if free == 0 else "freedeath"
        self.c[(k, s, cl, key)] += 1
        self.c[(k, s, cl, key + "_seg")] += length
        if s == side and did in self.dr and g.round >= r1:
            killer = None
            if reason == "headon" and did != actor and self.cur:
                killer = self.cur[1]
            self.dr[did]["end"] = (g.round, key, body[0], length, killer)


m = M()
g = Walk2(info["replay_path"])
try:
    g.run(m)
except Stop:
    pass
nm = {s: tname(info, s) for s in "AB"}
print(f"=== MID {gid} {info['map']} | A = {nm['A']} B = {nm['B']} | winner {info['winner']} by {info['end_type']} | rounds {r1 // 50 * 50}-{r2}")
print("  block side class | dragon-rounds | natural / corpse pearls per 100 dragon-rounds | splits by parents of this class | deaths rammed / rammer / boxed / free-cell (segments) | "
      "mean distance from own spawn | enemy head in view % | turns of 2+ steps %")
c = m.c
for k in sorted({key[0] for key in c}):
    for s in "AB":
        for cl in ("2", "3-4", "5-9", "10+"):
            n = c[(k, s, cl, "rounds")]
            if not n:
                continue
            t = max(1, c[(k, s, cl, "turns")])
            print(f"  r{k:3d} {s} {nm[s][:9]:9s} L{cl:4s} | {n:5d} | nat {100 * c[(k, s, cl, 'nat')] / n:5.2f} cor {100 * c[(k, s, cl, 'cor')] / n:5.2f} | sp {c[(k, s, cl, 'split')]:3d} | "
                  f"rammed {c[(k, s, cl, 'rammed')]:2d} ({c[(k, s, cl, 'rammed_seg')]:3d}) rammer {c[(k, s, cl, 'rammer')]:2d} ({c[(k, s, cl, 'rammer_seg')]:3d}) "
                  f"boxed {c[(k, s, cl, 'boxed')]:2d} ({c[(k, s, cl, 'boxed_seg')]:3d}) free {c[(k, s, cl, 'freedeath')]:2d} ({c[(k, s, cl, 'freedeath_seg')]:3d}) | "
                  f"dist {c[(k, s, cl, 'dist')] / n:5.1f} | ev {100 * c[(k, s, cl, 'ev')] / n:3.0f}% | multi {100 * c[(k, s, cl, 'multi')] / t:3.0f}%")
        print()
if do_list:
    print(f"  dragons of side {side} ({nm[side]}) that were {min_len}+ long at some round in r{r1}-{r2}:")
    rows = [(d, r) for d, r in m.dr.items() if r["maxlen"] >= min_len]
    for d, r in sorted(rows, key=lambda x: x[1]["first"]):
        end = r["end"]
        if end is None:
            fate = f"alive at r{r2}"
        else:
            fate = f"{end[1]} r{end[0]} at {end[2]} L{end[3]}" + (f" by L{end[4]}" if end[4] else "")
        born = f" born r{r['born'][0]} from #{r['born'][1]} as L{r['born'][2]}" if r["born"] else ""
        sp = " ".join(f"r{a}:{b_}->{p}+{ch}" for a, b_, p, ch in r["splits"])
        pos = " ".join(f"r{rr}:{p[0][0]},{p[0][1]}/L{p[1]}" for rr, p in sorted(r["pos"].items()))
        print(f"    #{d:<4d} rounds {r['rounds']:3d} L{r['len0']:2d}->{r['len1']:2d} (max {r['maxlen']:2d}) | nat {r['nat']:2d} cor {r['cor']:2d} | cells {len(r['cells']):3d} steps {r['steps']:3d} multi {r['multi']:2d} | "
              f"enemy in view {r['ev']:3d} | {fate}{born} | splits: {sp or '-'} | {pos}")
