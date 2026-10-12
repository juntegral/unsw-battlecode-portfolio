#!/usr/bin/env python3
"""Walk 3 of sub-session C2: the pearl zone (candidate 3z). One pass over every study game, both sides.

My own counting code (occupancy mirror from y_w1.py, ping FORMAT as documented in e_belief.py; no key).

The turn counted ("pearl turn"), as sub-session B and the first red team defined it: a non-queen dragon of 2-4 gives
a move order, no enemy head is inside its 7x7 view, and a pearl lies on a free cell next to its head that has a
further free neighbour. "Taken" = its first step goes onto such a pearl.

Writes y_out/w3/<game_id>.json:
  pt     key "S|bin25|len|td|lc|bd|org" -> [turns, taken]
         td = cells from the pearl to the head of the side's longest dragon at round start, in bins
              0: 0-3, 1: 4-6, 2: 7-9, 3: 10-12, 4: 13-16, 5: 17+; "s" = the dragon is itself (one of) the longest
         lc = that longest dragon's length class (0: under 5, 1: 5-9, 2: 10+)
         bd = the same bins for the zone the dragon itself believes in (readable pings of team 1119 only):
              head of the id it named one turn before if that head is in its view, else the named position;
              "s" names itself, "n" sent no leader message, "-" not readable / other team
         org = n natural pearl, c corpse pearl
  pt10   key "S|bin10" -> [turns, taken]
  left   pearls declined inside a zone (true zone: 9 cells or fewer from the longest and the dragon is not the
         longest; believed zone likewise): [round first declined, side, in true zone, in believed zone (-1 unknown),
         org, rounds until eaten (or until the end), eaten (1/0), eater on the same side, eater id, eater length,
         eater is that side's longest at that round's start, eater is the longest of the round it was declined,
         eater is the id the decliner named, times declined, cx, cy]
  dr     per side, bin25: small non-queen dragons (2-4): dragon-rounds [inside true zone, outside, is the longest]
         and natural pearls they ate [inside, outside, as the longest]
  drb    readable only, bin25: the same by the believed zone [in, out, names itself, no message] x 2
  ni     per side, bin25: natural pearls eaten [by the longest, by others 2-4, 5-7, 8+] x [inside true zone, outside]
  box    per side, bin50: turns of the side's longest dragon (8+): [turns, with 0 free cells, with 1 free cell,
         blocked neighbour cells at 0-1 free: kelp, its own body, own dragon under 8, own dragon 8+, enemy,
         sum of own heads under 8 within 3 cells, turns with such a head within 1 cell of its head]
Usage: python3 y_w3.py [--test gid ...]
"""
import os
import sys
import time
from multiprocessing import Pool

import lib
import y_lib as Y
import y_w1
from y_w2 import decode


def dbin(d):
    if d <= 3:
        return "0"
    if d <= 6:
        return "1"
    if d <= 9:
        return "2"
    if d <= 12:
        return "3"
    if d <= 16:
        return "4"
    return "5"


class W3(y_w1.W1):
    def __init__(self, me_side):
        super().__init__(False)
        self.me = me_side
        self.tag = {"A": 2, "B": 1}.get(me_side)
        self.ping = [0, 0]
        self.belnow = {}
        self.belprev = {}
        self.pt = {}
        self.pt10 = {}
        self.left = []
        self.reg = {}
        self.dr = {"A": {}, "B": {}}
        self.drb = {}
        self.ni = {"A": {}, "B": {}}
        self.box = {"A": {}, "B": {}}
        self.maxlen = {"A": 0, "B": 0}

    # ---- belief ----------------------------------------------------------------
    def sonar(self, g, sender, value, raw):
        if self.me is None or g.teams.get(sender) != self.me:
            return
        m = decode(value)
        if m is None:
            return
        self.ping[0] += 1
        lid, ln, when, x, y, tag = m
        b = g.board
        if not (tag == self.tag and g.teams.get(lid) == self.me and 0 <= g.round - when <= 25 and 1 <= ln <= b.w * b.h
                and x < b.w and y < b.h):
            return
        self.ping[1] += 1
        self.belnow[sender] = (lid, ln, when, x, y)

    def _bzone(self, g, did, head):
        """Believed zone head of dragon did: (kind, cell) with kind 's', 'n' or 'z'."""
        bel = self.belprev.get(did)
        if bel is None:
            return "n", None
        lid = bel[0]
        if lid == did:
            return "s", None
        body = g.bodies.get(lid)
        if body is not None and g.board.cheb(body[0], head) <= 3:
            return "z", body[0]
        return "z", (bel[3], bel[4])

    # ---- per round -------------------------------------------------------------
    def round_start(self, g, r):
        super().round_start(g, r)
        self.belprev = self.belnow
        self.belnow = {}
        if r < 100:
            return
        b = g.board
        bodies = g.bodies
        teams = g.teams
        bn = r // 25
        q = b.queen
        readable = self.me is not None
        for s in "AB":
            lid, llen = self.lead[s]
            self.maxlen[s] = llen
            lh = bodies[lid][0] if lid in bodies else None
            row = self.dr[s].setdefault(bn, [0, 0, 0, 0, 0, 0])
            for d, bd in bodies.items():
                if teams[d] != s or d == q[s]:
                    continue
                L = len(bd)
                if L > 4:
                    continue
                if L >= llen:
                    row[2] += 1
                elif lh is not None and b.manhattan(bd[0], lh) <= 9:
                    row[0] += 1
                else:
                    row[1] += 1
                if readable and s == self.me:
                    rb = self.drb.setdefault(bn, [0, 0, 0, 0, 0, 0, 0, 0])
                    kind, zh = self._bzone(g, d, bd[0])
                    if kind == "n":
                        rb[3] += 1
                    elif kind == "s":
                        rb[2] += 1
                    elif b.manhattan(bd[0], zh) <= 9:
                        rb[0] += 1
                    else:
                        rb[1] += 1

    def action(self, g, did, kind, nsteps):
        super().action(g, did, kind, nsteps)
        r = g.round
        if r < 50:
            return
        body = g.bodies.get(did)
        if not body:
            return
        b = g.board
        side = g.teams[did]
        L = len(body)
        head = body[0]
        occ = self.occ
        lid, llen = self.lead[side]
        # ---- the leader's own situation
        if did == lid and L >= 8 and r >= 100:
            fr = self.act_free[2]
            row = self.box[side].setdefault(r // 50, [0] * 10)
            row[0] += 1
            crowd = 0
            touch = 0
            for d2, b2 in g.bodies.items():
                if d2 != did and g.teams[d2] == side and len(b2) < 8:
                    m = b.manhattan(b2[0], head)
                    if m <= 3:
                        crowd += 1
                        if m <= 1:
                            touch = 1
            row[8] += crowd
            row[9] += touch
            if fr <= 1:
                row[1 if fr == 0 else 2] += 1
                for n in b.nb(head):
                    if n is None:
                        row[3] += 1
                    elif n in occ:
                        who = None
                        for d2, b2 in g.bodies.items():
                            if n in b2:
                                who = d2
                                break
                        if who == did:
                            row[4] += 1
                        elif who is not None and g.teams[who] == side:
                            row[5 if len(g.bodies[who]) < 8 else 6] += 1
                        else:
                            row[7] += 1
        # ---- pearl turn
        if kind != 0 or L > 4 or L < 2 or did == b.queen[side]:
            return
        pearls = g.pearls
        cands = []
        for n in b.nb(head):
            if n is None or n in occ or n not in pearls:
                continue
            for n2 in b.nb(n):
                if n2 is not None and n2 != head and n2 not in occ:
                    cands.append(n)
                    break
        if not cands:
            return
        teams = g.teams
        for d2, b2 in g.bodies.items():
            if teams[d2] != side and b.cheb(b2[0], head) <= 3:
                return
        first = b.step(head, int(g.act_dirs[0])) if g.act_dirs else None
        taken = first in cands
        lh = g.bodies[lid][0] if lid in g.bodies else None
        is_self = (L >= llen)

        def tdist(c):
            return 99 if lh is None else b.manhattan(c, lh)

        if taken:
            pc = first
        else:
            pc = max(cands, key=tdist)
        td = "s" if is_self else dbin(tdist(pc))
        lc = "0" if llen < 5 else ("1" if llen < 10 else "2")
        bd = "-"
        zkind = None
        zh = None
        bel_id = -1
        if self.me is not None and side == self.me:
            zkind, zh = self._bzone(g, did, head)
            bel = self.belprev.get(did)
            bel_id = bel[0] if bel else -1
            if zkind == "z":
                bd = dbin(b.manhattan(pc, zh))
            else:
                bd = zkind
        org = "c" if pearls[pc][0] == "corpse" else "n"
        k = "%s|%d|%d|%s|%s|%s|%s" % (side, r // 25, L, td, lc, bd, org)
        v = self.pt.get(k)
        if v is None:
            v = self.pt[k] = [0, 0]
        v[0] += 1
        k10 = "%s|%d" % (side, r // 10)
        v10 = self.pt10.get(k10)
        if v10 is None:
            v10 = self.pt10[k10] = [0, 0]
        v10[0] += 1
        if taken:
            v[1] += 1
            v10[1] += 1
            return
        if r < 100:
            return
        for c in cands:
            tz = (not is_self) and tdist(c) <= 9
            bz = -1
            if zkind is not None:
                bz = 1 if (zkind == "z" and b.manhattan(c, zh) <= 9) else 0
            if not tz and bz != 1:
                continue
            reg = self.reg.get(c)
            if reg is None:
                self.reg[c] = [r, side, 1 if tz else 0, bz, "c" if pearls[c][0] == "corpse" else "n", lid, bel_id, 1]
            else:
                reg[7] += 1

    def eat(self, g, did, cell, origin):
        super().eat(g, did, cell, origin)
        r = g.round
        side = g.teams[did]
        b = g.board
        reg = self.reg.pop(cell, None)
        L = g.act_start[1] if (g.current == did and g.act_start) else len(g.bodies[did])
        if reg is not None:
            r0, s0, tz, bz, org, lid0, bel0, nd = reg
            self.left.append([r0, s0, tz, bz, org, r - r0, 1, 1 if side == s0 else 0, did, L,
                              1 if (side == s0 and L >= self.maxlen[s0]) else 0, 1 if did == lid0 else 0,
                              1 if did == bel0 else 0, nd, cell[0], cell[1]])
        if origin[0] != "natural" or r < 100:
            return
        bn = r // 25
        lid, llen = self.lead[side]
        lh = g.bodies[lid][0] if lid in g.bodies else None
        inz = 1 if (lh is not None and b.manhattan(cell, lh) <= 9) else 0
        row = self.ni[side].setdefault(bn, [0] * 8)
        if did == lid:
            cls = 0
        elif L <= 4:
            cls = 1
        elif L <= 7:
            cls = 2
        else:
            cls = 3
        row[cls * 2 + (0 if inz else 1)] += 1
        if L <= 4 and did != b.queen[side]:
            dr = self.dr[side].setdefault(bn, [0, 0, 0, 0, 0, 0])
            if L >= llen:
                dr[5] += 1
            elif inz:
                dr[3] += 1
            else:
                dr[4] += 1
            if self.me is not None and side == self.me:
                rb = self.drb.setdefault(bn, [0, 0, 0, 0, 0, 0, 0, 0])
                head0 = g.act_start[0] if (g.current == did and g.act_start) else cell
                kind, zh = self._bzone(g, did, head0)
                if kind == "n":
                    rb[7] += 1
                elif kind == "s":
                    rb[6] += 1
                elif b.manhattan(cell, zh) <= 9:
                    rb[4] += 1
                else:
                    rb[5] += 1

    def end(self, g, rounds, winner, result):
        super().end(g, rounds, winner, result)
        for cell, reg in self.reg.items():
            r0, s0, tz, bz, org, lid0, bel0, nd = reg
            self.left.append([r0, s0, tz, bz, org, rounds - r0, 0, 0, -1, 0, 0, 0, 0, nd, cell[0], cell[1]])
        self.reg = {}


def run_game(g):
    me = Y.side_of(g, Y.ME)
    if g["map"] == "Schooltime":
        me = None
    h = W3(me)
    lib.Walk(g["replay_path"]).run(h)
    return dict(gid=g["game_id"], me=me, ping=h.ping, pt=h.pt, pt10=h.pt10, left=h.left, dr=h.dr, drb=h.drb, ni=h.ni,
                box=h.box, rounds=h.rounds)


def work(g):
    try:
        p = Y.out_path("w3", g["game_id"] + ".json")
        if os.path.exists(p):
            return (g["game_id"], "skip")
        Y.dump(run_game(g), "w3", g["game_id"] + ".json")
        return (g["game_id"], "ok")
    except Exception as e:  # noqa: BLE001
        import traceback
        return (g["game_id"], "ERR %r %s" % (e, traceback.format_exc()[-400:]))


def main():
    games = Y.load_games()
    if len(sys.argv) > 2 and sys.argv[1] == "--test":
        G = {g["game_id"]: g for g in games}
        for gid in sys.argv[2:]:
            t = time.time()
            o = run_game(G[gid])
            me = o["me"]
            print(gid, "me", me, "ping", o["ping"], "pt keys", len(o["pt"]), "left", len(o["left"]), "time %.2f" % (time.time() - t))
            for lo, hi in ((8, 11), (12, 15)):
                n = t2 = 0
                for k, v in o["pt"].items():
                    p = k.split("|")
                    if p[0] == me and lo <= int(p[1]) <= hi:
                        n += v[0]
                        t2 += v[1]
                print("   our pearl turns in bins %d-%d: %d taken %d" % (lo, hi, n, t2))
            print("   left sample", o["left"][:5])
            print("   dr", {k: v for k, v in list(o["dr"][me].items())[8:12]})
            print("   drb", {k: v for k, v in list(o["drb"].items())[8:12]})
            print("   ni", {k: v for k, v in list(o["ni"][me].items())[8:12]})
            print("   box", o["box"][me])
        return
    todo = [g for g in games if Y.study_sides(g)]
    print("games to walk:", len(todo), flush=True)
    os.nice(10)
    t = time.time()
    n = errs = 0
    with Pool(5) as pool:
        for gid, st in pool.imap_unordered(work, todo, chunksize=4):
            n += 1
            if st.startswith("ERR"):
                errs += 1
                print(gid, st, flush=True)
            if n % 100 == 0:
                print("done %d of %d, %.0fs, errors %d" % (n, len(todo), time.time() - t, errs), flush=True)
    print("finished %d games in %.0fs, errors %d" % (n, time.time() - t, errs), flush=True)


if __name__ == "__main__":
    main()
