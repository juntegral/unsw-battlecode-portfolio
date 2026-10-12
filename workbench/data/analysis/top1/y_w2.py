#!/usr/bin/env python3
"""Walk 2 of sub-session C2: what our dragons believe (readable pings only) and what happens after a leader cut.

My own counting code. It reuses the occupancy mirror of y_w1.py (also mine) and lib.py; it reads the ping FORMAT
as documented in e_belief.py (plain fields, no key). Sealed pings are simply counted as unreadable and left alone.

Writes y_out/w2/<game_id>.json with:
  ping     per side: [non-zero leader-type pings, of them plausible]        (only team 1119's side is decoded)
  bel      meow side, every round from 150: [round, senders (all own dragons but the longest), true longest id,
           true longest length, senders naming a longest dragon, naming a dead id, naming a living dragon under half
           the longest, naming themselves, most-named id, its count, its true length (0 dead), own units,
           dragons that could feed the longest by geometry (half its length or less, within 15 cells),
           of those the ones that name it]
  sup      both sides, every 5 rounds from 150: [units, longest, could-feed-by-geometry count, pearls they hold]
  cuts     every split from round 150 in which the side's longest dragon (8+) keeps 2-3 segments:
           r, side, stub, heir, before, keeps, gets, free cells at the order, longest other, room in front of the stub,
           own heads within 5 cells, cells to nearest enemy head, units,
           cohort: own dragons that could feed the heir (half its length or less) within 15 cells of the heir's or
                   the stub's head at the cut: [id, len, cells to heir head, cells to stub head, outcome, t, dh, ds]
           track:  per round t=1..30 after the cut: [heir length (0 dead), heir is the side's longest, stub alive,
                   cohort alive, sum cells to heir, sum cells to stub, (readable games) cohort naming heir / stub /
                   another living id / a dead id / nothing]
           end:    why tracking stopped (None, 'recut', 'heirdead', 'gameend') and at which t
Outcome codes of a cohort member within 25 rounds: H died by choice within 3 path steps of the heir's head;
S ... of the stub's head; B ... of another own dragon twice its length; N died by choice next to none of these;
R died in a ram; X died boxed in; h alive and 3+ cells nearer to the heir; s alive and 3+ cells nearer to the stub;
w alive, neither.
Usage: python3 y_w2.py [--test gid ...]
"""
import os
import sys
import time
from collections import deque
from multiprocessing import Pool

import lib
import y_lib as Y
import y_w1

HORIZON = 30
JUDGE = 25


def decode(v):
    """Leader message fields (format as in e_belief.py); None for zero or other message kinds."""
    if v == 0 or (v >> 63):
        return None
    return (v & 0x7FFF, (v >> 16) & 0xFFF, (v >> 28) & 0x1FF, (v >> 37) & 0x7F, (v >> 44) & 0x7F, (v >> 53) & 3)


class W2(y_w1.W1):
    def __init__(self, me_side):
        super().__init__(False)
        self.me = me_side          # side of team 1119 or None
        self.tag = {"A": 2, "B": 1}.get(me_side)
        self.ping = {"A": [0, 0], "B": [0, 0]}
        self.belnow = {}
        self.belprev = {}
        self.bel = []
        self.sup = {"A": {}, "B": {}}
        self.cuts = []
        self.active = []
        self.sides_now = None

    # ---- belief ----------------------------------------------------------------
    def sonar(self, g, sender, value, raw):
        if self.me is None or g.teams.get(sender) != self.me:
            return
        m = decode(value)
        if m is None:
            return
        p = self.ping[self.me]
        p[0] += 1
        lid, ln, when, x, y, tag = m
        r = g.round
        b = g.board
        ok = (tag == self.tag and g.teams.get(lid) == self.me and 0 <= r - when <= 25 and 1 <= ln <= b.w * b.h
              and x < b.w and y < b.h)
        if not ok:
            return
        p[1] += 1
        self.belnow[sender] = (lid, ln, when, x, y)

    # ---- per round -------------------------------------------------------------
    def round_start(self, g, r):
        super().round_start(g, r)
        self.belprev = self.belnow
        self.belnow = {}
        sides = self._sides(g)
        self.sides_now = sides
        bodies = g.bodies
        b = g.board
        geo = {}
        for s in "AB":
            lst = sides[s]
            if not lst:
                geo[s] = (0, 0, [], -1, 0)
                continue
            L, lid = lst[0]
            lh = bodies[lid][0]
            ids = [x[1] for x in lst[1:] if x[0] * 2 <= L and b.manhattan(bodies[x[1]][0], lh) <= 15]
            geo[s] = (len(ids), sum((len(bodies[i]) + 1) // 2 for i in ids), ids, lid, L)
            if r >= 150 and r % 5 == 0:
                self.sup[s][str(r)] = [len(lst), L, geo[s][0], geo[s][1]]
        if self.me is not None and r >= 150:
            s = self.me
            lst = sides[s]
            if lst:
                L = lst[0][0]
                longest = set(x[1] for x in lst if x[0] == L)
                n = ntrue = ndead = nsmall = nself = 0
                cnt = {}
                for d, (lid, ln, when, x, y) in self.belprev.items():
                    if d not in bodies or d in longest:
                        continue
                    n += 1
                    cnt[lid] = cnt.get(lid, 0) + 1
                    if lid in longest:
                        ntrue += 1
                    elif lid not in bodies:
                        ndead += 1
                    elif len(bodies[lid]) * 2 < L:
                        nsmall += 1
                    if lid == d:
                        nself += 1
                top, topn = (-1, 0)
                for k, v in cnt.items():
                    if v > topn:
                        top, topn = k, v
                gb = sum(1 for i in geo[s][2] if i in self.belprev and self.belprev[i][0] in longest)
                self.bel.append([r, n, lst[0][1], L, ntrue, ndead, nsmall, nself, top, topn,
                                 len(bodies[top]) if top in bodies else 0, len(lst), geo[s][0], gb])
        # ---- follow-ups of cuts
        if self.active:
            still = []
            for c in self.active:
                t = r - c["r"]
                if t < 1:
                    still.append(c)
                    continue
                if t > HORIZON:
                    self._close(g, c, None, HORIZON)
                    continue
                heir, stub = c["heir"], c["stub"]
                if heir not in bodies:
                    self._close(g, c, "heirdead", t)
                    continue
                side = c["side"]
                hl = len(bodies[heir])
                hh = bodies[heir][0]
                is_long = 1 if hl >= sides[side][0][0] else 0
                sa = 1 if stub in bodies else 0
                sh = bodies[stub][0] if sa else None
                na = sdh = sds = 0
                nb_h = nb_s = nb_o = nb_d = nb_n = 0
                readable = (side == self.me)
                for m in c["cohort"]:
                    if m[4] is not None:
                        continue
                    d = m[0]
                    if d not in bodies:
                        continue
                    na += 1
                    h = bodies[d][0]
                    dh = b.manhattan(h, hh)
                    ds = b.manhattan(h, sh) if sa else -1
                    sdh += dh
                    sds += max(ds, 0)
                    m[6], m[7] = dh, ds
                    if readable:
                        bl = self.belprev.get(d)
                        if bl is None:
                            nb_n += 1
                        elif bl[0] == heir:
                            nb_h += 1
                        elif bl[0] == stub:
                            nb_s += 1
                        elif bl[0] in bodies:
                            nb_o += 1
                        else:
                            nb_d += 1
                c["track"].append([hl, is_long, sa, na, sdh, sds, nb_h, nb_s, nb_o, nb_d, nb_n])
                if t == JUDGE:
                    self._judge(c)
                still.append(c)
            self.active = still

    def _judge(self, c):
        for m in c["cohort"]:
            if m[4] is None:
                dh0, ds0, dh, ds = m[2], m[3], m[6], m[7]
                gh = dh0 - dh
                gs = (ds0 - ds) if ds >= 0 else -99
                if gh >= 3 and gh >= gs:
                    m[4] = "h"
                elif gs >= 3:
                    m[4] = "s"
                else:
                    m[4] = "w"
                m[5] = JUDGE

    def _close(self, g, c, why, t):
        if c.get("end") is None:
            c["end"] = [why, t]
        if why is not None and t < JUDGE:
            for m in c["cohort"]:
                if m[4] is None:
                    m[4] = "c"   # censored: the heir died or cut again before round 25
                    m[5] = t

    def split(self, g, parent, child, before, plen, clen):
        super().split(g, parent, child, before, plen, clen)
        r = g.round
        if r < 150 or before < 8 or plen > 3:
            return
        row = self.lsplit[-1] if self.lsplit and self.lsplit[-1][1] == parent and self.lsplit[-1][2] == child else None
        if row is None:
            return
        fr, mx = row[7], row[8]
        if before < mx:
            return  # not the side's longest
        side = g.teams[parent]
        b = g.board
        bodies = g.bodies
        # a running follow-up of the parent as heir ends here
        for c in self.active:
            if c["heir"] == parent and c.get("end") is None:
                self._close(g, c, "recut", r - c["r"])
        self.active = [c for c in self.active if c.get("end") is None]
        sh = bodies[parent][0]
        hh = bodies[child][0]
        # room in front of the stub: free cells reachable from its head (cap 40)
        occ = self.occ
        seen = set()
        q = deque()
        for n in b.nb(sh):
            if n is not None and n not in occ and n not in seen:
                seen.add(n)
                q.append(n)
        while q and len(seen) < 40:
            c0 = q.popleft()
            for n in b.nb(c0):
                if n is not None and n not in occ and n not in seen:
                    seen.add(n)
                    q.append(n)
        crowd = 0
        en = 99
        cohort = []
        units = 0
        for d, bd in bodies.items():
            if g.teams[d] == side:
                units += 1
                if d == parent or d == child:
                    continue
                h = bd[0]
                dsb = b.manhattan(h, sh)
                dhh = b.manhattan(h, hh)
                if dsb <= 5:
                    crowd += 1
                if len(bd) * 2 <= clen and (dsb <= 15 or dhh <= 15):
                    cohort.append([d, len(bd), dhh, dsb, None, None, dhh, dsb])
            else:
                m = b.manhattan(bd[0], sh)
                if m < en:
                    en = m
        c = dict(r=r, side=side, stub=parent, heir=child, before=before, keeps=plen, gets=clen, fr=fr, mx=mx,
                 room=len(seen), crowd=crowd, en=en, units=units, cohort=cohort, track=[], end=None,
                 seq=row[9])
        self.cuts.append(c)
        self.active.append(c)

    def death(self, g, did, reason, length, body, actor):
        r = g.round
        if self.active:
            head = body[0]
            dist = None
            for c in self.active:
                t = r - c["r"]
                if t > JUDGE:
                    continue
                for m in c["cohort"]:
                    if m[0] != did or m[4] is not None:
                        continue
                    own_turn = (g.current == did)
                    fr = self.act_free[2] if (own_turn and self.act_free[0] == r and self.act_free[1] == did) else -1
                    if reason == "headon":
                        m[4] = "R"
                    elif fr == 0:
                        m[4] = "X"
                    else:
                        if dist is None:
                            dist = g.board.bfs(head, 3)
                        heir, stub = c["heir"], c["stub"]
                        bodies = g.bodies
                        if heir in bodies and bodies[heir][0] in dist:
                            m[4] = "H"
                        elif stub in bodies and bodies[stub][0] in dist:
                            m[4] = "S"
                        else:
                            side = c["side"]
                            code = "N"
                            for d2, b2 in bodies.items():
                                if d2 != did and g.teams[d2] == side and len(b2) >= 2 * length and b2[0] in dist:
                                    code = "B"
                                    break
                            m[4] = code
                    m[5] = t
        super().death(g, did, reason, length, body, actor)

    def end(self, g, rounds, winner, result):
        super().end(g, rounds, winner, result)
        for c in self.active:
            t = rounds - c["r"]
            if t >= JUDGE:
                self._judge(c)
                self._close(g, c, None, min(t, HORIZON))
            else:
                self._close(g, c, "gameend", t)
        self.active = []


def run_game(g):
    me = Y.side_of(g, Y.ME)
    if g["map"] == "Schooltime":
        me = None
    h = W2(me)
    w = lib.Walk(g["replay_path"])
    w.run(h)
    for c in h.cuts:
        c["cohort"] = [m for m in c["cohort"]]
    return dict(gid=g["game_id"], me=me, ping=h.ping, bel=h.bel, sup=h.sup, cuts=h.cuts, rounds=h.rounds,
                winner=h.winner)


def work(g):
    try:
        p = Y.out_path("w2", g["game_id"] + ".json")
        if os.path.exists(p):
            return (g["game_id"], "skip")
        Y.dump(run_game(g), "w2", g["game_id"] + ".json")
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
            print(gid, "me", o["me"], "ping", o["ping"], "bel rows", len(o["bel"]), "cuts", len(o["cuts"]),
                  "time %.2f" % (time.time() - t))
            for row in o["bel"][250:262]:
                print("   bel", row)
            for c in o["cuts"][-6:]:
                print("   cut r%d %s stub #%d heir #%d %d->%d+%d fr %s room %d crowd %d en %d units %d end %s" % (
                    c["r"], c["side"], c["stub"], c["heir"], c["before"], c["keeps"], c["gets"], c["fr"], c["room"],
                    c["crowd"], c["en"], c["units"], c["end"]))
                print("       cohort", [(m[0], m[1], m[2], m[3], m[4], m[5]) for m in c["cohort"]][:12])
                print("       track ", c["track"][:3], "...", c["track"][-1:] if c["track"] else "")
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
