#!/usr/bin/env python3
"""b_pack.py <game_id> <team_id>: close-read pack for one game from one team's side (sub-session A2).

Adapted from a_pack.py (sub-session A). One pass over the replay with lib.Walk. Sections:
  [1] opening: units every 10 rounds, split histogram, the first 40 queen actions of both queens
  [2] own queen: every split/suicide order with what lay on the four neighbour cells (a_box logic), what she ate,
      a line every 20 rounds, ALL rounds with an enemy head within 3 path steps (her order, did the distance to the
      nearest intruder grow, what allies within 6 steps did, deaths near her)
  [3] queen deaths of both sides with the killer's track, what it ate, who had her in view, sonar rays onto the killer
  [4] followers: dragons that kept the other side's queen head inside their 7x7 square for a streak of rounds
  [5] turn-level ram chances on the enemy queen from q3v2 (with the in-view flag), taken and not taken
  [6] deaths of dragons 15+ with the killer's track and whether the killer had just split or was just born
  [7] feeding: queen and leader every 25 rounds, what queen and leader ate per 50 rounds, own deaths that are not
      rams by reason and length, and what happened to the pearls of own dragons that died near the queen / leader
"""
import csv
import json
import os
import sys
from collections import Counter, defaultdict

import lib

GAMES = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
gid = sys.argv[1]
team = int(sys.argv[2])
q = json.load(open(f"q/{gid}.json"))
q3 = json.load(open(f"q3v2/{gid}.json")) if os.path.exists(f"q3v2/{gid}.json") else {"chances": []}
me = [s for s in "AB" if q["sides"][s]["team"] == team][0]
op = "B" if me == "A" else "A"
D = "NESW"
OTHER = {"A": "B", "B": "A"}

watch = {}  # killer id -> (round, victim side)
for s in "AB":
    qd = q["sides"][s].get("qdeath")
    if qd and qd.get("killer"):
        watch[qd["killer"]["id"]] = (qd["round"], s)


def lc(n):
    return "2" if n <= 2 else "3-4" if n <= 4 else "5-9" if n <= 9 else "10-19" if n <= 19 else "20+"


def src(origin, s):
    if origin[0] != "corpse":
        return origin[0]
    return f"{'own' if origin[1] == s else 'enemy'}_{origin[3]}"


class P(lib.Hooks):
    def __init__(self):
        self.snap, self.qbody, self.units, self.qline = {}, {}, {}, {"A": {}, "B": {}}
        self.acts = defaultdict(dict)
        self.deaths, self.splits = [], []
        self.born = {}
        self.lastsplit = defaultdict(list)      # parent id -> [(round, before, plen, clen)]
        self.qeat = Counter()
        self.leat = Counter()
        self.pings = defaultdict(list)
        self.seers = defaultdict(dict)
        self.corpse = defaultdict(Counter)
        self.weats = defaultdict(list)
        self.eats = defaultdict(list)            # did -> [(round, source)]
        self.inview = {"A": {}, "B": {}}         # victim side -> round -> {hunter id: (path dist or None, len)}
        self.boxes = {"A": [], "B": []}
        self.longest = {}
        self.leadline = {}
        self.qcells = {"A": set(), "B": set()}
        self.qcell_n = {"A": {}, "B": {}}
        self.qsteps = {"A": Counter(), "B": Counter()}
        self.afterq = {}                         # round -> side -> nearest intruder dist after the queen's own move
        self.rounds = 0
        self.dead_info = {}                      # corpse id -> (round, team, len, reason, near queen, near leader)
        self.bigsplit_free = {}                  # (round, id) -> free neighbour cells of the head when a 12+ dragon orders a split
        self.qctx = {"A": {}, "B": {}}
        self.react_pending = []
        self.react = {"A": Counter(), "B": Counter()}

    def round_start(self, g, r):
        b = g.board
        self.rounds = r
        self.snap[r] = {d: (body[0], len(body)) for d, body in g.bodies.items()}
        qb, u, lg = {}, {}, {}
        for s in "AB":
            qid = b.queen[s]
            if qid in g.bodies:
                qb[s] = tuple(g.bodies[qid])
            ls = sorted(((len(body), -d) for d, body in g.bodies.items() if g.teams[d] == s), reverse=True)
            u[s] = (len(ls), sum(x[0] for x in ls), ls[0][0] if ls else 0)
            lg[s] = -ls[0][1] if ls else None
        self.qbody[r], self.units[r], self.longest[r] = qb, u, lg
        # how did the allies of last round's close episodes move: towards the intruder's old cell, towards the queen's old cell?
        for (r0, s0, allies, icell, iid, qcell) in self.react_pending:
            di = b.bfs(icell, 14)
            dq = b.bfs(qcell, 14)
            for aid, acell in allies:
                nb_ = g.bodies.get(aid)
                if nb_ is None:
                    self.react[s0]["ally died that round"] += 1
                    continue
                a0, a1 = di.get(acell), di.get(nb_[0])
                q0, q1 = dq.get(acell), dq.get(nb_[0])
                if a0 is not None and a1 is not None:
                    self.react[s0]["to intruder: closer" if a1 < a0 else "to intruder: same" if a1 == a0 else "to intruder: farther"] += 1
                if q0 is not None and q1 is not None:
                    self.react[s0]["to queen: closer" if q1 < q0 else "to queen: same" if q1 == q0 else "to queen: farther"] += 1
        self.react_pending = []
        for s in qb:
            head = qb[s][0]
            dist = b.bfs(head, 12)
            en = sorted((dist[o[0]], len(o), i) for i, o in g.bodies.items() if g.teams[i] != s and o[0] in dist)
            al = sorted((dist[o[0]], len(o), i) for i, o in g.bodies.items() if g.teams[i] == s and i != b.queen[s] and o[0] in dist and dist[o[0]] <= 6)
            self.qline[s][r] = (head, len(qb[s]), [x for x in en if x[0] <= 6], al, b.ball(head))
            self.qcells[s].add(head)
            if r % 20 == 0:
                self.qcell_n[s][r] = len(self.qcells[s])
                self.qcells[s] = set()
                sp = b.starts[b.queen[s]]
                oth = [b.manhattan(o[0], sp) for i, o in g.bodies.items() if g.teams[i] == s and i != b.queen[s]]
                enh = [b.manhattan(o[0], head) for i, o in g.bodies.items() if g.teams[i] != s]
                self.qctx[s][r] = (round(sum(oth) / len(oth), 1) if oth else None, min(enh) if enh else None,
                                   sum(1 for x in enh if x <= 8), sum(1 for i, o in g.bodies.items() if g.teams[i] == s and i != b.queen[s] and b.manhattan(o[0], head) <= 8))
            # allies within 6 steps and intruders within 3: remember positions to see next round who moved towards whom
            if en and en[0][0] <= 3 and al:
                self.react_pending.append((r, s, [(x[2], g.bodies[x[2]][0]) for x in al], g.bodies[en[0][2]][0], en[0][2], head))
            iv = {}
            for i, o in g.bodies.items():
                if g.teams[i] != s and b.cheb(o[0], head) <= 3:
                    iv[i] = (dist.get(o[0]), len(o))
            self.inview[s][r] = iv
        for k, (R, vs) in watch.items():
            if R - 40 <= r <= R and vs in qb:
                kt = OTHER[vs]
                cells = qb[vs]
                self.seers[k][r] = [d for d, body in g.bodies.items() if g.teams[d] == kt and any(b.cheb(body[0], c) <= 3 for c in cells)]
        if r % 25 == 0:
            for s in "AB":
                lid = lg[s]
                if lid is not None:
                    body = g.bodies[lid]
                    self.leadline.setdefault(s, {})[r] = (lid, len(body), body[0], u[s][1], u[s][0], len(qb[s]) if s in qb else 0)

    def action(self, g, did, kind, nsteps):
        b = g.board
        self.acts[g.round][did] = (kind, "".join(D[d] for d in g.act_dirs) if kind == 0 else "")
        s = g.teams[did]
        if kind == 1 and did != b.queen[s] and len(g.bodies[did]) >= 12:
            occ = set()
            for o2 in g.bodies.values():
                occ.update(o2)
            head = g.bodies[did][0]
            self.bigsplit_free[(g.round, did)] = sum(1 for n in b.nb(head) if n is not None and n not in occ)
        if did == b.queen[s]:
            if kind == 0:
                self.qsteps[s][nsteps] += 1
            else:
                body = list(g.bodies[did])
                head = body[0]
                out, free = [], 0
                for d in range(4):
                    c = b.step(head, d)
                    if c is None:
                        out.append(D[d] + ":kelp")
                        continue
                    if c in body:
                        out.append(f"{D[d]}:own segment {body.index(c) + 1}")
                        continue
                    occ = [(i, g.teams[i]) for i, o in g.bodies.items() if i != did and c in o]
                    if occ:
                        i, t = occ[0]
                        part = "head" if g.bodies[i][0] == c else "tail" if g.bodies[i][-1] == c else "body"
                        out.append(f"{D[d]}:{'ally' if t == s else 'ENEMY'} #{i} L{len(g.bodies[i])} {part}")
                    else:
                        out.append(D[d] + ":FREE")
                        free += 1
                dist = b.bfs(head, 6)
                en = sorted((dist[o[0]], len(o), i) for i, o in g.bodies.items() if g.teams[i] != s and o[0] in dist)
                self.boxes[s].append(f"r{g.round} L{len(body)} at {head} orders {'SPLIT' if kind == 1 else 'SUICIDE'}; free neighbours {free}; ball4 {b.ball(head)}; "
                                     + ", ".join(out) + f"; nearest enemy head {('d%d L%d' % en[0][:2]) if en else 'none within 6'}")

    def moved(self, g, did, head, step_index, ate):
        b = g.board
        s = g.teams.get(did)
        if s is None:
            return
        # after the queen's last step: distance from her head to the nearest enemy head
        if did == b.queen[s] and step_index == g.act_steps:
            dist = b.bfs(head, 8)
            en = [dist[o[0]] for i, o in g.bodies.items() if g.teams[i] != s and o[0] in dist]
            self.afterq.setdefault(g.round, {})[s] = min(en) if en else None

    def split(self, g, parent, child, before, plen, clen):
        self.splits.append((g.round, parent, child, before, plen, clen, g.teams[parent], g.bodies[parent][0]))
        self.born[child] = (g.round, parent, clen)
        self.lastsplit[parent].append((g.round, before, plen, clen))
        s = g.teams[parent]
        if parent == g.board.queen[s] and self.boxes[s]:
            self.boxes[s][-1] += f" -> split {before} -> {plen}+{clen}"

    def death(self, g, did, reason, length, body, actor):
        b = g.board
        s = g.teams[did]
        r = g.round
        qh = g.bodies.get(b.queen[s])
        lid = self.longest.get(r, {}).get(s)
        lh = g.bodies.get(lid) if lid is not None else None
        nq = qh is not None and did != b.queen[s] and b.manhattan(body[0], qh[0]) <= 6
        nl = lh is not None and did != lid and b.manhattan(body[0], lh[0]) <= 6
        boxed = None
        if reason != "headon":
            occ = set()
            for o2 in g.bodies.values():
                occ.update(o2)
            boxed = not any(n is not None and n not in occ for n in b.nb(body[0]))
        self.dead_info[did] = (r, s, length, reason, nq, nl, boxed)
        self.deaths.append(dict(r=r, id=did, team=s, reason=reason, len=length, head=body[0], actor=actor,
                                astart=g.act_start if actor is not None and actor != did else None,
                                asteps=(g.step_index, len(g.act_dirs)) if actor is not None and actor != did else None,
                                nq=nq, nl=nl))
        if did == b.queen[s] and self.boxes[s] and reason == "noaction":
            self.boxes[s][-1] += f" -> queen dies ({reason})"

    def eat(self, g, did, cell, origin):
        b = g.board
        s = g.teams[did]
        o = src(origin, s)
        if did == b.queen[s]:
            self.qeat[(s, g.round // 50, o)] += 1
        elif did == self.longest.get(g.round, {}).get(s):
            self.leat[(s, g.round // 50, o)] += 1
        if origin[0] == "corpse":
            role = "Q" if did == b.queen[s] else "L" if did == self.longest.get(g.round, {}).get(s) else "o"
            self.corpse[origin[2]][(did, s, role)] += 1
        if did in watch:
            self.weats[did].append((g.round, o))
        self.eats[did].append((g.round, o))

    def sonar(self, g, sender, value, raw):
        r = g.round
        for k, (R, vs) in watch.items():
            if R - 40 <= r <= R and k in g.bodies and sender != k:
                try:
                    end = lib.rp.point(raw.pointer(1))
                except Exception:
                    return
                if end in g.bodies[k]:
                    self.pings[k].append((r, sender, value != 0))


p = P()
g = lib.Walk(GAMES[gid]["replay_path"])
g.run(p)
b = g.board
qid = {s: b.queen[s] for s in "AB"}
print(f"=== PACK2 {gid} {q['map']} {q['w']}x{q['h']} | protagonist side {me} (team {team} {q['sides'][me]['name']}) vs {q['sides'][op]['name']} ({q['sides'][op]['elo']}) | winner {q['winner']} by {q['end_type']} | rounds {q['rounds']}")
print("final:", {s: q["sides"][s]["final"] for s in "AB"}, "| queens:", qid, "| spawns:", {s: b.starts[qid[s]] for s in "AB"})


def act(r, d):
    a = p.acts.get(r, {}).get(d)
    if a is None:
        return "-"
    return ("mv " + a[1]) if a[0] == 0 else "SPLIT" if a[0] == 1 else "SUICIDE"


def tag(s):
    return "own" if s == me else "opp"


print("\n[1] OPENING: units/total/longest every 10 rounds (own | opp)")
for r in list(range(0, 101, 10)) + [120, 150]:
    if r in p.units:
        print(f"  r{r:3d} own {p.units[r][me]} | opp {p.units[r][op]} | ownQ {p.qline[me].get(r, ('dead', 0))[:2]} oppQ {p.qline[op].get(r, ('dead', 0))[:2]}")
for s in (me, op):
    for lo, hi in ((0, 60), (61, 120)):
        h = Counter((x[3], x[4], x[5]) for x in p.splits if x[6] == s and lo <= x[0] <= hi)
        dr = Counter(d["reason"] for d in p.deaths if d["team"] == s and lo <= d["r"] <= hi)
        ram = sum(1 for d in p.deaths if d["team"] != s and d["reason"] == "headon" and d["actor"] != d["id"] and lo <= d["r"] <= hi)
        print(f"  {tag(s)} r{lo}-{hi} splits (before,parent,child):n {sorted(h.items())} | own deaths by reason {dict(dr)} | rams made {ram}")
    print(f"  {tag(s)} queen first 40 actions:", " ".join(f"{r}:{act(r, qid[s])}" for r in range(0, 40)))

for s in (me, op):
    print(f"\n[2] {tag(s).upper()} QUEEN #{qid[s]}")
    print("   every split / suicide order and the four neighbour cells:")
    for line in p.boxes[s]:
        print("     " + line)
    e = defaultdict(dict)
    for (ss, k, o), n in p.qeat.items():
        if ss == s:
            e[k * 50][o] = n
    print("   eats per 50 rounds:", dict(sorted(e.items())))
    print("   steps per move order:", dict(sorted(p.qsteps[s].items())))
    ql = p.qline[s]
    print("   every 20 rounds (head, len, ball4, manh from spawn, nearest enemy d/L within 6, allies<=6, different cells in the last 20 rounds):")
    for r in range(0, p.rounds + 1, 20):
        if r in ql:
            v = ql[r]
            cx = p.qctx[s].get(r, (None, None, 0, 0))
            print(f"     r{r:3d} {v[0]} L{v[1]} ball{v[4]} home{b.manhattan(v[0], b.starts[qid[s]])} (other own heads: mean {cx[0]} from her spawn) e{(v[2][0][0], v[2][0][1]) if v[2] else '-'} a{len(v[3])} cells{p.qcell_n[s].get(r, '-')}"
                  f" | nearest enemy head manh {cx[1]}, enemy heads within manh 8: {cx[2]}, own heads within manh 8: {cx[3]}")
    first = {}
    for r in sorted(ql):
        for thr in (6, 10, 20, 40):
            if ql[r][1] >= thr and thr not in first and r > 30:
                oq = p.qline[OTHER[s]].get(r)
                first[thr] = f"r{r} (other queen then: {'L%d' % oq[1] if oq else 'dead'})"
    print("   first round (after r30) at which she was at least 6 / 10 / 20 / 40 long:", first)


def near_deaths(r, cell, rad=6):
    out = []
    for d in p.deaths:
        if d["r"] == r and b.cheb(d["head"], cell) <= rad:
            s = f"#{d['id']}{d['team']} L{d['len']} {d['reason']}"
            if d["astart"]:
                s += f" by #{d['actor']}{g.teams.get(d['actor'], '?')} L{d['astart'][1]} from {d['astart'][0]} step {d['asteps'][0]}/{d['asteps'][1]}"
            out.append(s)
    return out


def qrows(s, r1, r2):
    ql = p.qline[s]
    for r in range(max(0, r1), r2 + 1):
        if r not in ql:
            continue
        head, ln, en, al, ball = ql[r]
        es = ", ".join(f"d{x[0]} L{x[1]} #{x[2]}({act(r, x[2])})" for x in en[:4])
        als = ", ".join(f"d{x[0]} L{x[1]} #{x[2]}({act(r, x[2])})" for x in al[:4])
        nd = near_deaths(r, head)
        aq = p.afterq.get(r, {}).get(s)
        print(f"    r{r:3d} Q{head} L{ln} ball{ball} {act(r, qid[s])} (after her move nearest enemy d{aq}) | en: {es or '-'} | al: {als or '-'}" + (f" | deaths: {'; '.join(nd)}" if nd else ""))


def episodes(s, thr=3):
    ql = p.qline[s]
    rs = [r for r in sorted(ql) if ql[r][2] and ql[r][2][0][0] <= thr]
    eps = []
    for r in rs:
        if eps and r - eps[-1][1] <= 3:
            eps[-1][1] = r
        else:
            eps.append([r, r])
    return rs, eps


for s in (me, op):
    rs, eps = episodes(s)
    ql = p.qline[s]
    orders, away, allies, small = Counter(), Counter(), Counter(), Counter()
    for r in rs:
        a = p.acts.get(r, {}).get(qid[s])
        if a is None:
            continue
        orders["move %d" % len(a[1]) if a[0] == 0 else "split" if a[0] == 1 else "suicide"] += 1
        before = ql[r][2][0][0]
        after = p.afterq.get(r, {}).get(s)
        away["grew" if after is None or after > before else "same" if after == before else "shrank"] += 1
        allies["0 allies" if not ql[r][3] else "1 ally" if len(ql[r][3]) == 1 else "2 allies" if len(ql[r][3]) == 2 else "3+ allies"] += 1
        small[lc(ql[r][2][0][1])] += 1
    print(f"\n[2b] {tag(s).upper()} queen: {len(rs)} rounds / {len(eps)} episodes with an enemy head within 3 steps at round start; her orders {dict(orders)}; "
          f"distance to the nearest enemy head after her own move {dict(away)}; {dict(allies)}; nearest intruder length {dict(small)}")
    print(f"     in those rounds, own dragons within 6 steps of her moved (relative to the intruder's cell / to her cell at round start): {dict(sorted(p.react[s].items()))}")
    ramdef = [d for d in p.deaths if d["team"] != s and d["reason"] == "headon" and d["actor"] is not None and d["actor"] != d["id"]
              and g.teams.get(d["actor"]) == s and d["r"] in ql and any(x[2] == d["id"] for x in ql[d["r"]][2])]
    print(f"     enemy heads rammed by an own dragon while within 6 steps of her: {len(ramdef)} {[(d['r'], '#%d L%d by #%d L%d' % (d['id'], d['len'], d['actor'], d['astart'][1])) for d in ramdef][:12]}")
    print("     episodes:", [(a, c) for a, c in eps])
    if s == me or len(rs) <= 60:
        for a, c in eps:
            print(f"  episode r{a}-{c}:")
            qrows(s, a - 2, min(c + 1, a + 40))

print("\n[3] QUEEN DEATHS")
for s in (me, op):
    t = "OWN" if s == me else "ENEMY"
    qd = q["sides"][s].get("qdeath")
    if not qd:
        print(f"  {t} queen alive at the end, len {q['sides'][s]['final']['queen']}")
        continue
    R = qd["round"]
    print(f"  {t} queen died r{R} {qd['reason']} len {qd['len']} at {qd['pos']}")
    print("   her last 12 rounds:")
    qrows(s, R - 11, R)
    k = qd.get("killer")
    if not k:
        nd = [d for d in p.deaths if d["r"] == R and d["id"] == qid[s]]
        print("   no killer; death record:", nd)
        continue
    kid = k["id"]
    kt = OTHER[s]
    print(f"   killer #{kid} team {kt} born {p.born.get(kid, 'start')} (round, parent, length at birth); its own splits: {p.lastsplit.get(kid, [])[-4:]}")
    row = []
    for rr in [R - 40, R - 30, R - 25, R - 20, R - 15, R - 12, R - 10, R - 8, R - 6, R - 5, R - 4, R - 3, R - 2, R - 1, R]:
        if rr in p.snap and kid in p.snap[rr] and s in p.qbody.get(rr, {}):
            kh, kl = p.snap[rr][kid]
            dist = b.bfs(p.qbody[rr][s][0], 60)
            row.append(f"r{rr}:{kh} L{kl} d{dist.get(kh, '>60')} [{act(rr, kid)}]")
    print("   killer track (round: head, len, path distance to her head, its action):", " ".join(row))
    print("   killer ate (round:source), last 40 rounds:", [(r, o) for r, o in p.weats.get(kid, []) if r >= R - 40])
    see = p.seers.get(kid, {})
    first_self = [r for r in sorted(see) if kid in see[r]]
    print(f"   rounds (of the 40 before) in which the killer's head had her (any segment) inside its 7x7 square: {first_self}")
    print("   number of the killer's team-mates with her inside their 7x7 square, per round:", " ".join(f"{r}:{len(see[r])}" for r in sorted(see)))
    pg = p.pings.get(kid, [])
    byr = defaultdict(list)
    for r, snd, nz in pg:
        byr[r].append((snd, nz, snd in see.get(r, []) or snd in see.get(r - 1, []) or snd in see.get(r - 2, [])))
    print("   sonar rays that ended on the killer, per round: (n rays, n from a dragon that had her in view in the last 3 rounds):",
          " ".join(f"{r}:{len(v)}/{sum(1 for x in v if x[2])}" for r, v in sorted(byr.items())))

print("\n[4] FOLLOWERS: dragons that had the other queen's HEAD inside their 7x7 square (streaks of >= 6 rounds, gaps of <= 2 rounds allowed)")
for s in (op, me):
    hunters = "own dragons on the ENEMY queen" if s == op else "enemy dragons on the OWN queen"
    iv = p.inview[s]
    per = defaultdict(list)
    for r in sorted(iv):
        for d, (dd, ln) in iv[r].items():
            per[d].append((r, dd, ln))
    nseers = [len(iv[r]) for r in sorted(iv)]
    alive_rounds = len(nseers)
    print(f"  {hunters}: queen alive {alive_rounds} rounds; rounds with at least one seer {sum(1 for n in nseers if n)}; with 2+ seers {sum(1 for n in nseers if n >= 2)}")
    rows = []
    for d, lst in per.items():
        streak = [lst[0]]
        for x in lst[1:] + [None]:
            if x is not None and x[0] - streak[-1][0] <= 3:
                streak.append(x)
                continue
            if len(streak) >= 6:
                r1, r2 = streak[0][0], streak[-1][0]
                ds = sorted(v[1] for v in streak if v[1] is not None)
                eats = Counter(o for rr, o in p.eats.get(d, []) if r1 <= rr <= r2)
                adj = sum(1 for v in streak if v[1] == 1)
                di = p.dead_info.get(d)
                if di and di[0] <= r2 + 2:
                    endr = f"died r{di[0]} {di[3]}"
                    kd = [x for x in p.deaths if x["r"] == di[0] and x["actor"] == d and x["id"] != d]
                    if kd:
                        endr += f" ramming #{kd[0]['id']} L{kd[0]['len']}" + (" (THE QUEEN)" if kd[0]["id"] == qid[s] else "")
                else:
                    endr = "lost sight / queen died" if r2 < p.rounds - 1 else "game end"
                rows.append((r1, f"    #{d} r{r1}-{r2} ({len(streak)} rounds in view) L{streak[0][2]}->{streak[-1][2]} path dist min {ds[0] if ds else '?'} median {ds[len(ds) // 2] if ds else '?'} max {ds[-1] if ds else '?'}; "
                                 f"next to her head at round start {adj}x; ate {dict(eats) or 'nothing'}; born {p.born.get(d, 'start')}; end: {endr}"))
            streak = [x] if x is not None else []
    for _, line in sorted(rows)[:60]:
        print(line)

print("\n[5] RAM CHANCES on the enemy queen (q3v2): [round, side, id, len, steps, taken, her len, is longest, own queen alive, in view]")
for s in (me, op):
    ch = [c for c in q3.get("chances", []) if c[1] == s]
    iv1 = [c for c in ch if c[9]]
    print(f"  {tag(s)} side: total {len(ch)}; in view {len(iv1)} (taken {sum(1 for c in iv1 if c[5])}); not in view {len(ch) - len(iv1)} (taken {sum(1 for c in ch if not c[9] and c[5])})")
    lst = ch if s == me else [c for c in ch if c[9] or c[5]]
    for c in lst[:80]:
        r, _, did, ln, st, tk, hl, lg, oqa, inv = c
        h = p.snap.get(r, {}).get(did)
        o = OTHER[s]
        oq = p.qline[o].get(r)
        later = [d for d in p.deaths if d["id"] == did and r <= d["r"] <= r + 3]
        free = -(-ln // 4)
        qdead = [d for d in p.deaths if d["id"] == qid[o] and d["r"] == r]
        ate = [x[1] for x in p.eats.get(did, []) if x[0] == r]
        seers = len(p.inview[o].get(r, {}))
        streak = sum(1 for rr in range(r - 10, r) if did in p.inview[o].get(rr, {}))
        print(f"    r{r} #{did} L{ln} at {h[0] if h else '?'} {'IN VIEW' if inv else 'not in view'} needs {st} (free {free}, cost {max(0, st - free)}) her L{hl} at {oq[0] if oq else '?'}(round start); longest {lg}; own queen alive {oqa}; "
              f"{'TAKEN' if tk else 'NOT TAKEN: ' + act(r, did)}"
              + (f"; ate {ate}" if ate and not tk else "")
              + f"; in view {streak} of the last 10 rounds; team-mates with her in view {seers - (1 if did in p.inview[o].get(r, {}) else 0)}"
              + (f"; born {p.born[did]}" if did in p.born else "")
              + (f"; she was rammed this round by #{qdead[0]['actor']}" if qdead and not tk and qdead[0]["actor"] != qid[o] else "")
              + (f"; then died r{later[0]['r']} {later[0]['reason']}" if later and not tk else ""))

print("\n[6] DEATHS OF DRAGONS >= 15 (both teams)")
for d in p.deaths:
    if d["len"] < 15:
        continue
    R = d["r"]
    t = tag(d["team"])
    longest = p.units.get(R, {}).get(d["team"], (0, 0, 0))[2]
    line = f"  r{R} {t} #{d['id']} L{d['len']} {d['reason']} at {d['head']} (team longest then {longest}{', QUEEN' if d['id'] in qid.values() else ''}) born {p.born.get(d['id'], 'start')}"
    if d["astart"]:
        a = d["actor"]
        row = []
        for rr in [R - 20, R - 10, R - 5, R - 3, R - 2, R - 1, R]:
            if rr in p.snap and a in p.snap[rr] and d["id"] in p.snap[rr]:
                dist = b.bfs(p.snap[rr][d["id"]][0], 40)
                row.append(f"r{rr}:L{p.snap[rr][a][1]} d{dist.get(p.snap[rr][a][0], '>40')}")
        ls = [x for x in p.lastsplit.get(a, []) if R - 5 <= x[0] <= R]
        line += (f"\n      killer #{a} L{d['astart'][1]} from {d['astart'][0]} step {d['asteps'][0] + 1}/{d['asteps'][1]} born {p.born.get(a, 'start')}"
                 f"{'; KILLER SPLIT just before: ' + str(ls) if ls else ''}{'; KILLER IS A NEW SPLIT CHILD' if a in p.born and R - p.born[a][0] <= 3 else ''}; its length / path distance before: {' '.join(row)}")
    else:
        qh = p.qbody.get(R, {}).get(d["team"])
        line += f" | own queen then: {'dead' if not qh else 'at %s L%d, manh %d' % (qh[0], len(qh), b.manhattan(qh[0], d['head']))}"
    eaters = p.corpse.get(d["id"])
    if eaters:
        line += "\n      pearls eaten by: " + ", ".join(f"#{e[0]}{e[1]}x{n}{'(Q)' if e[2] == 'Q' else '(leader)' if e[2] == 'L' else ''}" for e, n in eaters.most_common(5))
    print(line)

print("\n[7] FEEDING")
for s in (me, op):
    print(f"  {tag(s)}: every 25 rounds: leader id, leader len, share of team total, units, queen len")
    ll = p.leadline.get(s, {})
    print("    " + " | ".join(f"r{r}:#{v[0]}{'(Q)' if v[0] == qid[s] else ''} L{v[1]} {100 * v[1] // max(1, v[3])}% u{v[4]} q{v[5]}" for r, v in sorted(ll.items()) if r >= 100))
    e = defaultdict(dict)
    for (ss, k, o), n in p.leat.items():
        if ss == s:
            e[k * 50][o] = n
    print("    leader (longest non-queen at that moment) eats per 50 rounds:", dict(sorted(e.items())))
    dr = Counter()
    for d in p.deaths:
        if d["team"] == s and not (d["reason"] == "headon"):
            dr[(d["r"] // 100 * 100, d["reason"], lc(d["len"]))] += 1
    print("    own non-ram deaths (per 100 rounds, reason, length class):", dict(sorted(dr.items())))
    # pearls of own dragons that died without a ram: where did they go
    agg = defaultdict(Counter)
    for did, (r, ss, ln, reason, nq, nl, boxed) in p.dead_info.items():
        if ss != s or reason == "headon":
            continue
        k = (r // 100 * 100, "nearQ" if nq else "nearLeader" if nl else "elsewhere", "no free cell" if boxed else "HAD A FREE CELL")
        agg[k]["n"] += 1
        agg[k]["segments"] += ln
        agg[k]["pearls"] += -(-ln // 2)
        for (eid, es, role), n in p.corpse.get(did, {}).items():
            agg[k]["eaten by " + ("enemy" if es != s else "queen" if role == "Q" else "leader" if role == "L" else "other own")] += n
    print("    own dragons that died without a ram (per 100 rounds; where; did the head have a free neighbour cell): count, segments, pearls dropped, who ate them")
    for k in sorted(agg):
        print(f"    r{k[0]} {k[1]}, {k[2]}: {dict(agg[k])}")
    rev = [x for x in p.splits if x[6] == s and x[3] >= 12 and x[4] <= 3]
    print(f"    reverse splits (before >= 12, parent keeps <= 3): {len(rev)}; of 20+: {[(x[0], x[1], '%d->%d+%d' % (x[3], x[4], x[5])) for x in rev if x[3] >= 20][:30]}")
    fr = Counter()
    for x in rev:
        f = p.bigsplit_free.get((x[0], x[1]))
        fr["head had no free cell" if f == 0 else "head had a free cell" if f else "unknown"] += 1
    child_dead = sum(1 for x in rev if x[2] in p.dead_info and p.dead_info[x[2]][0] <= x[0] + 1)
    front_dead = sum(1 for x in rev if x[1] in p.dead_info and p.dead_info[x[1]][0] <= x[0] + 3 and p.dead_info[x[1]][3] != "headon")
    front_ram = sum(1 for x in rev if x[1] in p.dead_info and p.dead_info[x[1]][0] <= x[0] + 5 and p.dead_info[x[1]][3] == "headon")
    print(f"    at those reverse splits: {dict(fr)}; the 2-3-long front part died without a ram within 3 rounds in {front_dead}, died in a ram within 5 rounds in {front_ram}; the big child died within 1 round in {child_dead}")
    big = [x for x in p.splits if x[6] == s and x[3] >= 12 and x[4] > 3]
    print(f"    other splits of 12+ (parent keeps > 3): {[(x[0], x[1], '%d->%d+%d' % (x[3], x[4], x[5])) for x in big][:30]}")
