#!/usr/bin/env python3
"""e_walk.py: one pass over each replay for sub-session A5 (the longest-dragon race), both sides of every game.

Usage:  python3 e_walk.py run [jobs] [--all]     walk the study games (meow or a top-three team against a 2000+
                                                 opponent, Schooltime left out; --all = every game of games.csv)
        python3 e_walk.py one <game_id>          walk one game and print the size of what was collected
Output: e_out/w/<game_id>.json  (skips games already done; delete the file to redo)

Words used in the output
  leader / "long"   : the team's longest dragon at the start of the round (ties: the previous one stays, else lowest id).
  lineage / "lin"   : the dragon that is the team's longest at the END of the game, followed back in time; when it was
                      born in a split, the lineage continues with its parent before that moment.
  death classes     : 0 rammed by an enemy head, 1 it rammed a head itself, 2 "by choice" = any other death of a dragon
                      that had at least one free cell next to its head at the start of its own turn, 3 "boxed" = any other
                      death with no free cell, 4 rammed by a team-mate.
  free cell         : a cell next to the head (kelp and portals respected) with no body segment on it.
  pearl codes       : 0 natural, 1/2/3 pearl of an own dragon that died by choice / boxed / in a ram, 4/5/6 the same for
                      an enemy dragon, 7 unknown.
  path distance     : steps along the shortest way that respects kelp, wrap and portals and ignores bodies.

Per side the file holds
  tl      every 5 rounds: [round, units, total, longest, leader id, 2nd, 3rd, queen length (0 = dead), dragons of 8+,
          of 15+, dragons of 4 or shorter, their summed length, "pot" = the pearls all own dragons but the longest
          would drop if they died now (sum of ceil(length / 2))]
  lead    every 25 rounds from 100, for the leader: [round, id, length, x, y, cells within 4 steps (41 = open),
          Manhattan distance to the nearest enemy head, that enemy's length, path distance to the nearest enemy head
          (-1 = more than 12), enemy heads within 8 path steps, own heads within 6 path steps, Manhattan distance to
          the own queen's start, in the same region as the ENEMY queen's start when portals count as walls (1/0),
          the same for the OWN start, steps taken so far, segments paid so far, natural pearls eaten so far, corpse
          pearls eaten so far, is the queen (1/0), own heads within 8 cells (Manhattan), their summed length, own heads
          within 15 cells, their summed length, of those at most half as long as the leader: number, summed length,
          own dragons MORE than half as long as the leader (anywhere): number, summed length, path distance from the
          leader's head to the other own heads: median, 80th percentile, largest]
  deaths  one row for every death by choice, every death of a dragon of 8+, every queen death, every head-on death of
          a dragon of 5+, every boxed-in death within 3 path steps of an own dragon at least twice as long, and (meow's
          side) every `noaction` death (columns: DCOL; "rem" = 1 when the dragon was the head part left with 2-3
          segments by a split of a dragon of 5+ in the last 5 rounds)
  dagg    all deaths: "bin50|class|length class" -> [number, summed length]   (length classes 2, 3-4, 5-9, 10-19, 20+)
  drops   pearls dropped by this side's corpses: "bin50|corpse class 0 choice/1 boxed/2 ram" -> number
  eats    "role|bin50|code" -> pearls eaten, role T = whole team, L = the leader of that round, N = the lineage
  paid    "role|bin50" -> segments paid for extra steps (dragons of 5+ only), roles L and N
  splits  every split of a dragon of 5+: [round, parent, child, length before, parent keeps, child gets, free cells at
          the parent's head at its turn start, parent was the leader, parent is the queen]
  nsplit  bin50 -> splits (all lengths)
  lin     the lineage: final id and length, the chain of ids with birth rounds, its length every 5 rounds, the first
          round it reached 8 / 15 / 25 / 40, the handovers (a split in which the lineage went to the child)
  longfirst  first round the team's leader was 8 / 15 / 25 / 40 long
  adj     "bin10|near" -> [turns, pearl taken]: turns of a non-queen dragon of 2-4 that moves, with no enemy head in
          its 7x7 view and a pearl on a free next cell that has a further free neighbour. near: 0 = the pearl is within
          9 cells of the own leader (5+ long, another dragon), 1 = farther, 2 = no own leader of 5+
  zone    one row per pearl declined on such a turn, followed until eaten (columns: ZCOL)
For meow's side only (decoded from our own sonar pings, see e_belief.py; nothing here needs a key)
  bel     every 5 rounds from 100: [round, senders (all own dragons but the leader that have pinged), of them believing
          the true leader, believing a dead dragon, believing themselves, distinct believed ids, the most believed id,
          how many believe it, its believed length (max), its true length (0 = dead), the true leader's length, the true
          leader's id, mean age of the news in rounds, senders whose believed leader is dead or less than half as long
          as the true leader, senders that could feed the true leader by our rules (believe it, within 15 cells of its
          head, at most half its length): number and summed length, the same without the belief test: number, length]
  adjz    "bin10|flag" -> [turns, pearl taken] for the turns of `adj`; flag 1 = every such pearl lies within 9 cells of
          the position the dragon believes its leader is at, 0 = not, 2 = it believes it is the leader itself, -1 = unknown
"""
import json
import os
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool

import e_lib as E

OUT = os.path.join(E.HERE, "e_out", "w4")
VERSION = 4
REASON_IDX = {"wall": 0, "self": 1, "body": 2, "headon": 3, "noaction": 4, "other": 5}
DCOL = ("r", "id", "len", "reason", "cls", "akind", "sdone", "sord", "free", "rank",
        "tid", "tlen", "tdist", "tq", "tlong", "lid", "llen", "lmanh", "lpath", "qlen", "qmanh",
        "emanh", "elen", "epath", "kid", "klen", "ksteps", "kenemy",
        "bid", "blen", "bage", "balive", "btrue", "blong", "bmanh",
        "drop", "e_t", "e_l", "e_q", "e_o", "e_e", "dsum", "e_big", "e_lin", "x", "y", "tle", "nlid", "nllen", "nldist", "rem")
DI = {k: i for i, k in enumerate(DCOL)}
ZCOL = ("r", "x", "y", "did", "dlen", "dlong", "llen", "lid", "dnl", "nllen", "zflag", "ndecl", "fate", "delay", "elen", "eid", "elong")
THRESH = (8, 15, 25, 40)


def lclass(n):
    return 0 if n <= 2 else 1 if n <= 4 else 2 if n <= 9 else 3 if n <= 19 else 4


class W(E.Hooks):
    def __init__(self, g, meta):
        b = g.board
        self.meta = meta
        self.me_side = "A" if meta["A"] == E.ME else ("B" if meta["B"] == E.ME else None)
        self.me_tag = 2 if self.me_side == "A" else 1
        self.queen = dict(b.queen)
        self.queens = set(b.queen.values())
        self.comp = E.noportal_components(b)
        self.born = {d: (0, 0, None, len(body), len(body)) for d, body in g.bodies.items()}
        self.hist = {}
        self.members = {"A": set(), "B": set()}
        for d in g.bodies:
            self.members[g.teams[d]].add(d)
        self.long_id = {"A": None, "B": None}
        self.long_len = {"A": 0, "B": 0}
        self.long_first = {"A": {}, "B": {}}
        self.cnt = {d: [0, 0, 0, 0] for d in g.bodies}
        self.dead = {}
        self.ccls = {}
        self.eats = []
        self.paidev = []
        self.tl = {"A": [], "B": []}
        self.lead = {"A": [], "B": []}
        self.deaths = {"A": [], "B": []}
        self.dagg = {"A": defaultdict(lambda: [0, 0]), "B": defaultdict(lambda: [0, 0])}
        self.drops = {"A": Counter(), "B": Counter()}
        self.eat_t = {"A": Counter(), "B": Counter()}
        self.eat_l = {"A": Counter(), "B": Counter()}
        self.paid_l = {"A": Counter(), "B": Counter()}
        self.splits = {"A": [], "B": []}
        self.nsplit = {"A": Counter(), "B": Counter()}
        self.adj = {"A": defaultdict(lambda: [0, 0]), "B": defaultdict(lambda: [0, 0])}
        self.adjz = defaultdict(lambda: [0, 0])
        self.zp = {"A": {}, "B": {}}
        self.zdone = {"A": [], "B": []}
        self.belief = {}
        self.bel = []
        self.pend = {}
        self.nping = self.badping = 0
        self.qdeath = {"A": None, "B": None}
        self.round_seq = []
        self.t_did = None
        self.t_kind = None
        self.t_len = self.t_free = self.t_eats = self.t_seq = self.t_round = 0
        self.t_head = None
        self.t_adj = None
        self.t_islong = False
        self.ram_pending = None
        self.cut_round = {}

    # ---------------------------------------------------------------- rounds
    def round_start(self, g, r):
        self.finish_action(g)
        self.round_seq.append(g.seq)
        bodies, teams, hist = g.bodies, g.teams, self.hist
        per = {"A": [], "B": []}
        for d, body in bodies.items():
            L = len(body)
            h = hist.get(d)
            if h is None:
                hist[d] = [r, [L]]
            else:
                h[1].append(L)
            per[teams[d]].append((L, d))
        for S in "AB":
            v = per[S]
            if not v:
                self.long_id[S], self.long_len[S] = None, 0
                continue
            mx = max(v)[0]
            cur = self.long_id[S]
            if not (cur in bodies and teams[cur] == S and len(bodies[cur]) == mx):
                self.long_id[S] = min(d for L, d in v if L == mx)
            self.long_len[S] = mx
            lf = self.long_first[S]
            for T in THRESH:
                if mx >= T and T not in lf:
                    lf[T] = r
            if r % 5 == 0:
                ls = sorted((L for L, d in v), reverse=True)
                q = bodies.get(self.queen[S])
                small = [L for L in ls if L <= 4]
                self.tl[S].append([r, len(v), sum(ls), ls[0], self.long_id[S], ls[1] if len(ls) > 1 else 0,
                                   ls[2] if len(ls) > 2 else 0, len(q) if q else 0, sum(1 for L in ls if L >= 8),
                                   sum(1 for L in ls if L >= 15), len(small), sum(small), sum((L + 1) // 2 for L in ls[1:])])
            if r % 25 == 0 and r >= 100:
                self.sample_leader(g, S, r)
        if self.me_side and r % 5 == 0 and r >= 100:
            self.sample_belief(g, r)

    def sample_leader(self, g, S, r):
        b = g.board
        lid = self.long_id[S]
        body = g.bodies[lid]
        head, L = body[0], len(body)
        dist = b.bfs(head, 12)
        es = E.other(S)
        dm, dml, dp, ne8 = 999, 0, -1, 0
        for d in self.members[es]:
            eb = g.bodies[d]
            eh = eb[0]
            m = b.manhattan(head, eh)
            if m < dm:
                dm, dml = m, len(eb)
            pd = dist.get(eh)
            if pd is not None:
                if dp < 0 or pd < dp:
                    dp = pd
                if pd <= 8:
                    ne8 += 1
        n6 = n8 = n15 = f15 = l8 = l15 = lf15 = nbig = lbig = 0
        far = b.bfs(head, 1 << 20)
        pds = []
        for d in self.members[S]:
            if d == lid:
                continue
            ob = g.bodies[d]
            oh, ol = ob[0], len(ob)
            pds.append(far.get(oh, 999))
            if 2 * ol > L:
                nbig += 1
                lbig += ol
            pd = dist.get(oh)
            if pd is not None and pd <= 6:
                n6 += 1
            m = b.manhattan(head, oh)
            if m <= 15:
                n15 += 1
                l15 += ol
                if 2 * ol <= L:
                    f15 += 1
                    lf15 += ol
                if m <= 8:
                    n8 += 1
                    l8 += ol
        pds.sort()
        c = self.cnt.get(lid, [0, 0, 0, 0])
        st, est = b.starts[b.queen[S]], b.starts[b.queen[es]]
        comp = self.comp
        self.lead[S].append([r, lid, L, head[0], head[1], b.ball(head), dm, dml, dp, ne8, n6, b.manhattan(head, st),
                             int(comp[head] == comp[est]), int(comp[head] == comp[st]), c[0], c[1], c[2], c[3],
                             int(lid == b.queen[S]), n8, l8, n15, l15, f15, lf15, nbig, lbig,
                             pds[len(pds) // 2] if pds else -1, pds[(4 * len(pds)) // 5] if pds else -1, pds[-1] if pds else -1])

    def sample_belief(self, g, r):
        S = self.me_side
        lid = self.long_id[S]
        if lid is None:
            return
        bodies = g.bodies
        b = g.board
        L = len(bodies[lid])
        lhead = bodies[lid][0]
        n = nt = nd = ns = nsmall = nelig = lelig = ngeo = lgeo = 0
        ages = 0
        ids = Counter()
        blen = {}
        for d in self.members[S]:
            if d == lid:
                continue
            ob = bodies[d]
            ol = len(ob)
            geo = 2 * ol <= L and b.manhattan(ob[0], lhead) <= 15
            if geo:
                ngeo += 1
                lgeo += ol
            bel = self.belief.get(d)
            if bel is None:
                continue
            n += 1
            bid = bel[0]
            ids[bid] += 1
            if bid == lid:
                nt += 1
                if geo:
                    nelig += 1
                    lelig += ol
            else:
                if bid == d:
                    ns += 1
                elif bid not in bodies:
                    nd += 1
                if L >= 2 * (len(bodies[bid]) if bid in bodies else 0):
                    nsmall += 1
            ages += max(0, r - 1 - bel[2])
            if bel[1] > blen.get(bid, 0):
                blen[bid] = bel[1]
        if not n:
            self.bel.append([r, 0, 0, 0, 0, 0, -1, 0, 0, 0, L, lid, 0, 0, 0, 0, ngeo, lgeo])
            return
        top, k = ids.most_common(1)[0]
        self.bel.append([r, n, nt, nd, ns, len(ids), top, k, blen.get(top, 0), len(bodies[top]) if top in bodies else 0,
                         L, lid, round(ages / n, 1), nsmall, nelig, lelig, ngeo, lgeo])

    # ---------------------------------------------------------------- turns
    def finish_action(self, g):
        did = self.t_did
        if did is None:
            return
        self.t_did = None
        self.ram_pending = None
        body = g.bodies.get(did)
        if body is None or self.t_kind != 0:
            return
        paid = self.t_len + self.t_eats - len(body)
        if paid > 0:
            self.cnt[did][1] += paid
            if self.t_len >= 5:
                self.paidev.append((self.t_seq, self.t_round, did, self.t_len, paid))
                if self.t_islong:
                    self.paid_l[g.teams[did]][self.t_round // 50] += paid

    def turn(self, g, did):
        self.finish_action(g)
        body = g.bodies[did]
        head = body[0]
        L = len(body)
        occ = g.occ
        b = g.board
        nb = b.nb(head)
        free = 0
        for n in nb:
            if n is not None and n not in occ:
                free += 1
        self.t_did, self.t_len, self.t_free, self.t_eats, self.t_head = did, L, free, 0, head
        self.t_kind = None
        self.t_seq, self.t_round = g.seq, g.round
        self.t_adj = None
        S = g.teams[did]
        self.t_islong = did == self.long_id[S]
        if S == self.me_side:
            p = self.pend.pop(did, None)
            if p is not None:
                a = self.adjz[(p[0], -1)]
                a[0] += 1
                a[1] += p[1]
        if 2 <= L <= 4 and free and did not in self.queens:
            pearls = g.pearls
            cand = None
            for n in nb:
                if n is not None and n in pearls and n not in occ and (cand is None or n not in cand):
                    for m in b.nb(n):
                        if m is not None and m != head and m not in occ:
                            if cand is None:
                                cand = []
                            cand.append(n)
                            break
            if cand:
                bodies = g.bodies
                for d in self.members[E.other(S)]:
                    if b.cheb(head, bodies[d][0]) <= 3:
                        cand = None
                        break
                self.t_adj = cand

    def action(self, g, did, kind, nsteps):
        self.t_kind = kind
        self.t_seq = g.seq
        adj = self.t_adj
        if not adj or did != self.t_did or kind != 0 or not g.act_dirs:
            return
        S = g.teams[did]
        r = g.round
        b = g.board
        dest = b.nb(self.t_head)[g.act_dirs[0]]
        taken = dest in adj
        lid = self.long_id[S]
        if lid not in g.bodies:
            lid = None
        if lid is None or lid == did or self.long_len[S] < 5:
            near, dl = 2, -1
        else:
            dl = b.manhattan(adj[0], g.bodies[lid][0])
            near = 0 if dl <= 9 else 1
        a = self.adj[S][(r // 10, near)]
        a[0] += 1
        a[1] += taken
        new = []
        if not taken:
            zp = self.zp[S]
            L = self.t_len
            for cell in adj:
                rec = zp.get(cell)
                if rec is not None:
                    rec[11] += 1
                    continue
                dnl, nll = 999, 0
                bodies = g.bodies
                for d in self.members[S]:
                    ob = bodies[d]
                    if len(ob) > L and d != did:
                        m = b.manhattan(cell, ob[0])
                        if m < dnl:
                            dnl, nll = m, len(ob)
                if lid is None or lid == did:
                    dlong, llen, lidv = -1, 0, -1
                else:
                    dlong, llen, lidv = b.manhattan(cell, bodies[lid][0]), self.long_len[S], lid
                rec = [r, cell[0], cell[1], did, L, dlong, llen, lidv, dnl if dnl < 999 else -1, nll, -1, 1, -1, -1, 0, -1, 0]
                zp[cell] = rec
                new.append(rec)
        if S == self.me_side:
            self.pend[did] = (r // 10, int(taken), list(adj), new)

    def moved(self, g, did, head, step_index, ate):
        if did == g.current:
            c = self.cnt.get(did)
            if c is not None:
                c[0] += 1

    def split(self, g, parent, child, before, plen, clen):
        S = g.teams[parent]
        r = g.round
        self.members[S].add(child)
        self.born[child] = (r, g.seq, parent, clen, before)
        self.cnt[child] = [0, 0, 0, 0]
        self.nsplit[S][r // 50] += 1
        if before >= 5 and plen <= 3:
            self.cut_round[parent] = r
        if before >= 5:
            self.splits[S].append([r, parent, child, before, plen, clen, self.t_free if self.t_did == parent else -1,
                                   int(parent == self.long_id[S]), int(parent == self.queen[S])])

    # ---------------------------------------------------------------- pearls
    def drop(self, g, cell, origin):
        if origin[0] != "corpse":
            return
        cid = origin[2]
        info = self.ccls.get(cid)
        if info is None:
            return
        self.drops[info[0]][(g.round // 50, info[1])] += 1
        rec = self.dead.get(cid)
        if rec is not None:
            rec[DI["drop"]] += 1

    def eat(self, g, did, cell, origin):
        if did == self.t_did:
            self.t_eats += 1
        S = g.teams[did]
        r = g.round
        cid = -1
        if origin[0] == "natural":
            code = 0
            self.cnt[did][2] += 1
        elif origin[0] == "corpse":
            cid = origin[2]
            info = self.ccls.get(cid)
            if info is None:
                code = 7
            else:
                code = (1 if info[0] == S else 4) + info[1]
            self.cnt[did][3] += 1
            rec = self.dead.get(cid)
            if rec is not None:
                if info[0] == S:
                    if did == rec[DI["tid"]]:
                        rec[DI["e_t"]] += 1
                    elif did == rec[DI["lid"]]:
                        rec[DI["e_l"]] += 1
                    elif did == self.queen[S]:
                        rec[DI["e_q"]] += 1
                    else:
                        rec[DI["e_o"]] += 1
                    if len(g.bodies[did]) >= 8:
                        rec[DI["e_big"]] += 1
                else:
                    rec[DI["e_e"]] += 1
                rec[DI["dsum"]] += r - rec[0]
        else:
            code = 7
        self.eats.append((g.seq, r, did, code, cid))
        self.eat_t[S][(r // 50, code)] += 1
        if did == self.long_id[S]:
            self.eat_l[S][(r // 50, code)] += 1
        for T in "AB":
            rec = self.zp[T].pop(cell, None)
            if rec is not None:
                if S == T:
                    rec[12] = 0 if did == rec[7] else 1
                else:
                    rec[12] = 2
                rec[13] = r - rec[0]
                rec[14] = len(g.bodies[did])
                rec[15] = did
                rec[16] = int(did == self.long_id[S])
                self.zdone[T].append(rec)

    # ---------------------------------------------------------------- deaths
    def death(self, g, did, reason, length, body, actor):
        S = g.teams[did]
        r = g.round
        b = g.board
        self.members[S].discard(did)
        cur = g.current
        kid = klen = ksteps = -1
        kenemy = 0
        if reason == "headon":
            if cur is not None and cur != did:
                kenemy = int(g.teams[cur] != S)
                cls = 0 if kenemy else 4
                kid, klen, ksteps = cur, (g.act_start[1] if g.act_start else -1), g.step_index + 1
            else:
                cls = 1
        else:
            if self.t_did == did:
                free = self.t_free
            else:
                free = len(E.free_neighbours(g, body[0]))
            cls = 2 if free > 0 else 3
        ccode = 0 if cls == 2 else 1 if cls == 3 else 2
        self.ccls[did] = (S, ccode, r)
        a = self.dagg[S][(r // 50, cls, lclass(length))]
        a[0] += 1
        a[1] += length
        isq = did == self.queen[S]
        head = body[0]
        bodies = g.bodies
        full = (cls == 2 or length >= 8 or isq or (reason == "headon" and length >= 5)
                or (S == self.me_side and reason == "noaction"))
        if not full and reason != "headon":
            # a boxed-in death is kept as a row when it happens within 3 path steps of a much longer own dragon
            near = b.bfs(head, 3)
            for d in self.members[S]:
                ob = bodies[d]
                if len(ob) >= 2 * length and ob[0] in near:
                    full = True
                    break
        if not full:
            if reason == "headon":
                self.pair_ram(did, S, length, None)
            return
        dist = b.bfs(head, 8)
        rank = 1
        tid = tlen = tq = tlong = -1
        tdist = 99
        nlid = nllen = -1
        nldist = 99
        lid = self.long_id[S]
        for d in self.members[S]:
            ob = bodies[d]
            ol = len(ob)
            if ol > length:
                rank += 1
            pd = dist.get(ob[0])
            if pd is None:
                continue
            if ol >= 2 * length and pd < tdist:
                tid, tlen, tdist = d, ol, pd
            if ol > length and pd < nldist:
                nlid, nllen, nldist = d, ol, pd
        if tid >= 0:
            tq, tlong = int(tid == self.queen[S]), int(tid == lid)
        else:
            tdist = -1
        if nlid < 0:
            nldist = -1
        if lid is None or lid == did or lid not in bodies:
            lidv, llen, lmanh, lpath = -1, 0, -1, -1
        else:
            lh = bodies[lid][0]
            lidv, llen, lmanh, lpath = lid, len(bodies[lid]), b.manhattan(head, lh), dist.get(lh, -1)
        q = bodies.get(self.queen[S])
        if q is not None and not isq:
            qlen, qmanh = len(q), b.manhattan(head, q[0])
        else:
            qlen, qmanh = 0, -1
        emanh, elen, epath = 999, 0, -1
        for d in self.members[E.other(S)]:
            if d == cur and reason == "headon":
                continue
            eb = bodies.get(d)
            if eb is None:
                continue
            m = b.manhattan(head, eb[0])
            if m < emanh:
                emanh, elen = m, len(eb)
            pd = dist.get(eb[0])
            if pd is not None and (epath < 0 or pd < epath):
                epath = pd
        bid = blen = bage = balive = btrue = blong = bmanh = -1
        if S == self.me_side:
            bel = self.belief.get(did)
            if bel is not None:
                bid, blen, bage = bel[0], bel[1], max(0, r - 1 - bel[2])
                balive = int(bid in bodies and bid != did)
                btrue = len(bodies[bid]) if balive else 0
                blong = int(bid == lid)
                bmanh = b.manhattan(head, bodies[bid][0]) if balive else b.manhattan(head, (bel[3], bel[4]))
        rec = [r, did, length, REASON_IDX.get(reason, 5), cls, g.act_kind if g.act_kind is not None else -1,
               g.step_index if cur == did else -1, g.act_steps if cur == did else -1,
               self.t_free if self.t_did == did else -1, rank,
               tid, tlen, tdist, tq, tlong, lidv, llen, lmanh, lpath, qlen, qmanh,
               emanh, elen, epath, kid, klen, ksteps, kenemy,
               bid, blen, bage, balive, btrue, blong, bmanh,
               0, 0, 0, 0, 0, 0, 0, 0, 0, head[0], head[1], int(bool(g.act_tle)) if cur == did else 0, nlid, nllen, nldist,
               int(did in self.cut_round and r - self.cut_round[did] <= 5)]
        self.dead[did] = rec
        self.deaths[S].append(rec)
        if isq:
            self.qdeath[S] = [r, reason, cls, length, klen, ksteps]
        if reason == "headon":
            self.pair_ram(did, S, length, rec)

    def pair_ram(self, did, S, length, rec):
        """The two deaths of one head-on arrive as two events; give the attacker's row its victim (kid, klen, kenemy)."""
        p = self.ram_pending
        if p is None:
            self.ram_pending = (did, S, length, rec)
            return
        self.ram_pending = None
        for (a, sa, la, ra), (v, sv, lv, rv) in ((p, (did, S, length, rec)), ((did, S, length, rec), p)):
            if ra is not None and ra[DI["cls"]] == 1:
                ra[DI["kid"]], ra[DI["klen"]], ra[DI["kenemy"]] = v, lv, int(sv != sa)

    # ---------------------------------------------------------------- sonar (our own pings only)
    def sonar(self, g, sender, value, raw):
        if self.me_side is None or g.teams.get(sender) != self.me_side:
            return
        m = E.decode(value)
        if m is None:
            return
        self.nping += 1
        b = g.board
        if m[5] != self.me_tag or m[3] >= b.w or m[4] >= b.h or m[2] > g.round:
            self.badping += 1
            return
        self.belief[sender] = m
        p = self.pend.pop(sender, None)
        if p is not None:
            if m[0] == sender:
                flag = 2
            else:
                pos = (m[3], m[4])
                flag = int(all(b.manhattan(c, pos) <= 9 for c in p[2]))
                for rec in p[3]:
                    rec[10] = int(b.manhattan((rec[1], rec[2]), pos) <= 9)
            if flag == 2:
                for rec in p[3]:
                    rec[10] = 2
            a = self.adjz[(p[0], flag)]
            a[0] += 1
            a[1] += p[1]

    # ---------------------------------------------------------------- end
    def end(self, g, rounds, winner, result):
        self.finish_action(g)
        self.rounds = rounds
        self.winner = winner
        for S in "AB":
            for cell, rec in self.zp[S].items():
                rec[12], rec[13] = 3, rounds - rec[0]
                self.zdone[S].append(rec)
        self.final = {}
        self.lin = {}
        for S in "AB":
            v = sorted(((len(body), -d) for d, body in g.bodies.items() if g.teams[d] == S), reverse=True)
            q = g.bodies.get(self.queen[S])
            self.final[S] = dict(units=len(v), total=sum(x[0] for x in v), top=[[x[0], -x[1]] for x in v[:5]],
                                 queen=len(q) if q else 0, pot=sum((x[0] + 1) // 2 for x in v[1:]))
            self.lin[S] = self.lineage(g, S, rounds, v)

    def lineage(self, g, S, rounds, v):
        if not v:
            return None
        mx = v[0][0]
        cur = self.long_id[S]
        F = cur if (cur in g.bodies and g.teams[cur] == S and len(g.bodies[cur]) == mx) else -v[0][1]
        chain = []
        d = F
        while d is not None:
            chain.append(d)
            d = self.born[d][2]
        chain.reverse()
        bseq = [self.born[d][1] for d in chain]
        pos = {d: i for i, d in enumerate(chain)}
        hist = self.hist

        def holder_at_round(r):
            for d in reversed(chain):
                h = hist.get(d)
                if h is not None and h[0] <= r < h[0] + len(h[1]):
                    return d, h[1][r - h[0]]
            return None, 0

        curve, ids = [], []
        first = {}
        for r in range(rounds):
            d, L = holder_at_round(r)
            if r % 5 == 0:
                curve.append(L)
                ids.append(d if d is not None else -1)
            for T in THRESH:
                if L >= T and T not in first:
                    first[T] = r
        hand = [[self.born[d][0], self.born[d][2], d, self.born[d][4], self.born[d][3]] for d in chain if self.born[d][2] is not None]

        def is_holder(did, seq):
            i = pos.get(did)
            if i is None or bseq[i] > seq:
                return False
            return i + 1 >= len(chain) or bseq[i + 1] > seq

        eat_n = Counter()
        for seq, r, did, code, cid in self.eats:
            if g.teams[did] == S and is_holder(did, seq):
                eat_n[(r // 50, code)] += 1
                if cid >= 0:
                    rec = self.dead.get(cid)
                    if rec is not None:
                        rec[DI["e_lin"]] += 1
        paid_n = Counter()
        for seq, r, did, L0, paid in self.paidev:
            if is_holder(did, seq):
                paid_n[r // 50] += paid
        shed = Counter()
        for row in self.splits[S]:
            r, parent, child = row[0], row[1], row[2]
            if parent in pos and child not in pos and is_holder(parent, self.born[child][1] - 1):
                shed[r // 50] += row[5]
        return dict(id=F, len=mx, chain=[[d, self.born[d][0]] for d in chain[-12:]], curve=curve, ids=ids,
                    first={str(k): x for k, x in first.items()}, hand=[h for h in hand if h[0] >= 200], nhand=len(hand),
                    eat={"%d|%d" % k: x for k, x in eat_n.items()}, paid={str(k): x for k, x in paid_n.items()},
                    shed={str(k): x for k, x in shed.items()})

    def result(self, g):
        meta = self.meta
        out = dict(v=VERSION, gid=meta["gid"], map=meta["map"], cells=meta["cells"], w=g.board.w, h=g.board.h,
                   set=meta["set"], rounds=self.rounds, winner=self.winner, end_type=meta["end_type"],
                   A=meta["A"], B=meta["B"], An=meta["An"], Bn=meta["Bn"], Ae=meta["Ae"], Be=meta["Be"],
                   me=self.me_side, nping=self.nping, badping=self.badping, dcol=list(DCOL), zcol=list(ZCOL), sides={})
        for S in "AB":
            eats = {}
            for k, x in self.eat_t[S].items():
                eats["T|%d|%d" % k] = x
            for k, x in self.eat_l[S].items():
                eats["L|%d|%d" % k] = x
            lin = self.lin[S]
            if lin:
                for k, x in lin.pop("eat").items():
                    eats["N|" + k] = x
            paid = {"L|%d" % k: x for k, x in self.paid_l[S].items()}
            if lin:
                for k, x in lin.pop("paid").items():
                    paid["N|" + k] = x
            side = dict(queen=self.queen[S], start=list(g.board.starts[self.queen[S]]), qdeath=self.qdeath[S],
                        final=self.final[S], tl=self.tl[S], lead=self.lead[S], deaths=self.deaths[S],
                        dagg={"%d|%d|%d" % k: x for k, x in self.dagg[S].items()},
                        drops={"%d|%d" % k: x for k, x in self.drops[S].items()},
                        eats=eats, paid=paid, splits=self.splits[S], nsplit={str(k): x for k, x in self.nsplit[S].items()},
                        lin=lin, longfirst={str(k): x for k, x in self.long_first[S].items()},
                        adj={"%d|%d" % k: x for k, x in self.adj[S].items()}, zone=self.zdone[S])
            if S == self.me_side:
                side["bel"] = self.bel
                side["adjz"] = {"%d|%d" % k: x for k, x in self.adjz.items()}
            out["sides"][S] = side
        return out


def walk(meta):
    g = E.Walk(meta["path"])
    w = W(g, meta)
    g.run(w)
    return w.result(g)


def one(meta):
    path = os.path.join(OUT, "%d.json" % meta["gid"])
    if os.path.exists(path):
        return meta["gid"], "skip"
    try:
        out = walk(meta)
    except Exception as e:  # noqa: BLE001
        return meta["gid"], "ERROR %r" % (e,)
    tmp = path + ".tmp%d" % os.getpid()
    with open(tmp, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    os.replace(tmp, path)
    return meta["gid"], "ok"


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    if sys.argv[1] == "one":
        gid = int(sys.argv[2])
        meta = next(g for g in E.load_games() if g["gid"] == gid)
        out = walk(meta)
        s = json.dumps(out, separators=(",", ":"))
        print("bytes", len(s), "pings", out["nping"], "bad", out["badping"])
        for S in "AB":
            d = out["sides"][S]
            print(S, out[S + "n"], "final", d["final"], "| lin", {k: d["lin"][k] for k in ("id", "len", "first", "nhand")} if d["lin"] else None)
            print("   tl rows", len(d["tl"]), "lead", len(d["lead"]), "deaths", len(d["deaths"]), "splits5+", len(d["splits"]),
                  "zone", len(d["zone"]), "bel", len(d.get("bel", [])))
        with open(os.path.join(OUT, "%d.json" % gid), "w") as f:
            f.write(s)
    else:
        jobs = 5
        allg = "--all" in sys.argv
        for a in sys.argv[2:]:
            if a.isdigit():
                jobs = int(a)
        rows = E.load_games() if allg else E.study_games()
        rows = [m for m in rows if not os.path.exists(os.path.join(OUT, "%d.json" % m["gid"]))]
        print("games to walk:", len(rows), flush=True)
        os.nice(10)
        bad = 0
        with Pool(min(jobs, 5)) as p:
            for i, (gid, st) in enumerate(p.imap_unordered(one, rows, chunksize=2)):
                if st.startswith("ERROR"):
                    bad += 1
                    print(gid, st, flush=True)
                if i % 100 == 0:
                    print(i, flush=True)
        print("done, errors:", bad, flush=True)
