#!/usr/bin/env python3
"""a_pack.py <game_id> [team_id=306]: close-read pack for one game (sub-session A).

One pass over the replay with lib.Walk. Prints, from the protagonist's side:
  opening table (every 10 rounds to 60), split-length histogram 0-60, queen splits / eats,
  close approaches to the own queen (round by round), every queen kill with the killer's track,
  who could see her (7x7 square) and sonar rays that ended on the killer, deaths of dragons >= 15,
  the own long self-kills and who ate them, and ram chances on the enemy queen that were not taken.
"""
import csv
import json
import os
import sys
from collections import Counter, defaultdict

import lib

GAMES = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
gid = sys.argv[1]
team = int(sys.argv[2]) if len(sys.argv) > 2 else 306
q = json.load(open(f"q/{gid}.json"))
q3 = json.load(open(f"q3/{gid}.json")) if os.path.exists(f"q3/{gid}.json") else {"chances": []}
me = [s for s in "AB" if q["sides"][s]["team"] == team][0]
op = "B" if me == "A" else "A"
D = "NESW"

watch = {}  # killer id -> (round, victim side)
for s in "AB":
    qd = q["sides"][s].get("qdeath")
    if qd and qd.get("killer"):
        watch[qd["killer"]["id"]] = (qd["round"], s)


class P(lib.Hooks):
    def __init__(self):
        self.snap, self.qbody, self.units, self.qline = {}, {}, {}, {"A": {}, "B": {}}
        self.acts = defaultdict(dict)
        self.deaths, self.splits = [], []
        self.born = {}
        self.qeat = Counter()
        self.pings = defaultdict(list)
        self.seers = defaultdict(dict)
        self.corpse = defaultdict(Counter)
        self.weats = defaultdict(list)
        self.rounds = 0

    def round_start(self, g, r):
        b = g.board
        self.rounds = r
        self.snap[r] = {d: (body[0], len(body)) for d, body in g.bodies.items()}
        qb = {}
        u = {}
        for s in "AB":
            qid = b.queen[s]
            if qid in g.bodies:
                qb[s] = tuple(g.bodies[qid])
            ls = [len(body) for d, body in g.bodies.items() if g.teams[d] == s]
            u[s] = (len(ls), sum(ls), max(ls) if ls else 0)
        self.qbody[r], self.units[r] = qb, u
        for s in qb:
            head = qb[s][0]
            dist = b.bfs(head, 6)
            en = sorted((dist[o[0]], len(o), i) for i, o in g.bodies.items() if g.teams[i] != s and o[0] in dist)
            al = sorted((dist[o[0]], len(o), i) for i, o in g.bodies.items() if g.teams[i] == s and i != b.queen[s] and o[0] in dist)
            self.qline[s][r] = (head, len(qb[s]), en, al, b.ball(head))
        for k, (R, vs) in watch.items():
            if R - 40 <= r <= R and vs in qb:
                kt = "A" if vs == "B" else "B"
                cells = qb[vs]
                self.seers[k][r] = [d for d, body in g.bodies.items() if g.teams[d] == kt and any(b.cheb(body[0], c) <= 3 for c in cells)]

    def action(self, g, did, kind, nsteps):
        self.acts[g.round][did] = (kind, "".join(D[d] for d in g.act_dirs) if kind == 0 else "")

    def split(self, g, parent, child, before, plen, clen):
        self.splits.append((g.round, parent, child, before, plen, clen, g.teams[parent], g.bodies[parent][0]))
        self.born[child] = (g.round, parent, clen)

    def death(self, g, did, reason, length, body, actor):
        self.deaths.append(dict(r=g.round, id=did, team=g.teams[did], reason=reason, len=length, head=body[0], actor=actor,
                                astart=g.act_start if actor is not None and actor != did else None,
                                asteps=(g.step_index, len(g.act_dirs)) if actor is not None and actor != did else None))

    def eat(self, g, did, cell, origin):
        b = g.board
        s = g.teams[did]
        if did == b.queen[s]:
            self.qeat[(s, g.round // 50, origin[0] if origin[0] != "corpse" else f"{'own' if origin[1] == s else 'enemy'}_{origin[3]}")] += 1
        if origin[0] == "corpse":
            self.corpse[origin[2]][did] += 1
        if did in watch:
            self.weats[did].append((g.round, origin[0] if origin[0] != "corpse" else f"{'own' if origin[1] == s else 'enemy'}_{origin[3]}"))

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
meta = GAMES[gid]
print(f"=== PACK {gid} {q['map']} {q['w']}x{q['h']} | protagonist side {me} (team {team}) vs {q['sides'][op]['name']} ({q['sides'][op]['elo']}) | winner {q['winner']} by {q['end_type']} | rounds {q['rounds']}")
print("final:", {s: q["sides"][s]["final"] for s in "AB"}, "| queens:", qid)


def act(r, d):
    a = p.acts.get(r, {}).get(d)
    if a is None:
        return "-"
    return ("mv " + a[1]) if a[0] == 0 else "SPLIT" if a[0] == 1 else "SUICIDE"


print("\n-- opening: units/total/longest every 10 rounds (own | opp)")
for r in list(range(0, 61, 10)) + [80, 100]:
    if r in p.units:
        print(f"  r{r:3d} own {p.units[r][me]} | opp {p.units[r][op]} | ownQ {p.qline[me].get(r, ('dead', 0))[:2]} oppQ {p.qline[op].get(r, ('dead', 0))[:2]}")
for s in (me, op):
    h = Counter((x[3], x[4], x[5]) for x in p.splits if x[6] == s and x[0] <= 60)
    su = sum(1 for d in p.deaths if d["team"] == s and d["reason"] == "noaction" and d["r"] <= 60)
    ram = sum(1 for d in p.deaths if d["team"] != s and d["reason"] == "headon" and d["actor"] != d["id"] and d["r"] <= 60)
    print(f"  {'own' if s == me else 'opp'} splits r0-60 (before,parent,child):n {sorted(h.items())} | self-kills {su} | rams made {ram}")
    print(f"  {'own' if s == me else 'opp'} queen first 30 actions:", " ".join(f"{r}:{act(r, qid[s])}" for r in range(0, 30)))

for s in (me, op):
    tag = "own" if s == me else "opp"
    print(f"\n-- {tag} queen splits:", [(x[0], f"{x[3]}->{x[4]}+{x[5]}", x[7]) for x in p.splits if x[1] == qid[s]])
    e = defaultdict(dict)
    for (ss, k, o), n in p.qeat.items():
        if ss == s:
            e[k * 50][o] = n
    print(f"   {tag} queen eats per 50 rounds:", dict(sorted(e.items())))
    ql = p.qline[s]
    print(f"   {tag} queen every 20 rounds (round: head, len, ball, nearest enemy d/L, allies<=6):",
          " | ".join(f"{r}:{ql[r][0]} L{ql[r][1]} b{ql[r][4]} e{(ql[r][2][0][0], ql[r][2][0][1]) if ql[r][2] else '-'} a{len(ql[r][3])}" for r in range(0, p.rounds + 1, 20) if r in ql))


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
        print(f"    r{r:3d} Q{head} L{ln} ball{ball} {act(r, qid[s])} | en: {es or '-'} | al: {als or '-'}" + (f" | deaths: {'; '.join(nd)}" if nd else ""))


def episodes(s, thr=3, maxn=5):
    ql = p.qline[s]
    rs = [r for r in sorted(ql) if ql[r][2] and ql[r][2][0][0] <= thr]
    eps = []
    for r in rs:
        if eps and r - eps[-1][1] <= 3:
            eps[-1][1] = r
        else:
            eps.append([r, r])
    scored = sorted(eps, key=lambda e: (min(ql[r][2][0][0] for r in range(e[0], e[1] + 1) if r in ql and ql[r][2]), e[0]))
    return eps, sorted(scored[:maxn])


eps, pick = episodes(me)
print(f"\n-- own queen: {len(eps)} episodes with an enemy head within 3 steps; rounds {[(a, c) for a, c in eps][:30]}")
for a, c in pick:
    print(f"  episode r{a}-{c}:")
    qrows(me, a - 2, min(c + 2, a + 11))

print("\n-- queen deaths")
for s in (me, op):
    tag = "OWN" if s == me else "ENEMY"
    qd = q["sides"][s].get("qdeath")
    if not qd:
        print(f"  {tag} queen alive at the end, len {q['sides'][s]['final']['queen']}")
        continue
    R = qd["round"]
    print(f"  {tag} queen died r{R} {qd['reason']} len {qd['len']} at {qd['pos']}")
    print("   her last 10 rounds:")
    qrows(s, R - 9, R)
    k = qd.get("killer")
    if not k:
        nd = [d for d in p.deaths if d["r"] == R and d["id"] == qid[s]]
        print("   no killer; death record:", nd)
        continue
    kid = k["id"]
    kt = "A" if s == "B" else "B"
    print(f"   killer #{kid} team {kt} born {p.born.get(kid, 'start')} (round, parent, length at birth)")
    row = []
    for rr in [R - 30, R - 20, R - 15, R - 10, R - 8, R - 6, R - 5, R - 4, R - 3, R - 2, R - 1, R]:
        if rr in p.snap and kid in p.snap[rr] and s in p.qbody.get(rr, {}):
            kh, kl = p.snap[rr][kid]
            dist = b.bfs(p.qbody[rr][s][0], 45)
            row.append(f"r{rr}:{kh} L{kl} d{dist.get(kh, '>45')} [{act(rr, kid)}]")
    print("   killer track (round: head, len, path distance to her head, its action):", " ".join(row))
    print("   killer ate (round:source), last 30 rounds:", [(r, o) for r, o in p.weats.get(kid, []) if r >= R - 30])
    see = p.seers.get(kid, {})
    first_self = [r for r in sorted(see) if kid in see[r]]
    print(f"   rounds (of the 40 before) in which the killer's head had her inside its 7x7 square: {first_self}")
    print("   number of the killer's team-mates with her inside their 7x7 square, per round:", " ".join(f"{r}:{len(see[r])}" for r in sorted(see)))
    pg = p.pings.get(kid, [])
    byr = defaultdict(list)
    for r, snd, nz in pg:
        byr[r].append((snd, nz, snd in see.get(r, []) or snd in see.get(r - 1, []) or snd in see.get(r - 2, [])))
    print("   sonar rays that ended on the killer, per round: (n rays, n from a dragon that had her in view in the last 3 rounds):",
          " ".join(f"{r}:{len(v)}/{sum(1 for x in v if x[2])}" for r, v in sorted(byr.items())))

print("\n-- deaths of dragons >= 15 long (both teams)")
for d in p.deaths:
    if d["len"] < 15:
        continue
    R = d["r"]
    tag = "own" if d["team"] == me else "opp"
    longest = p.units.get(R, {}).get(d["team"], (0, 0, 0))[2]
    line = f"  r{R} {tag} #{d['id']} L{d['len']} {d['reason']} at {d['head']} (team longest then {longest}) born {p.born.get(d['id'], 'start')}"
    if d["astart"]:
        a = d["actor"]
        row = []
        for rr in [R - 10, R - 5, R - 3, R - 2, R - 1, R]:
            if rr in p.snap and a in p.snap[rr] and d["id"] in p.snap[rr]:
                dist = b.bfs(p.snap[rr][d["id"]][0], 30)
                row.append(f"r{rr}:L{p.snap[rr][a][1]} d{dist.get(p.snap[rr][a][0], '>30')}")
        line += f"\n      killer #{a} L{d['astart'][1]} from {d['astart'][0]} step {d['asteps'][0]}/{d['asteps'][1]} born {p.born.get(a, 'start')}; its length / path distance before: {' '.join(row)}"
    else:
        qh = p.qbody.get(R, {}).get(d["team"])
        line += f" | own queen then: {'dead' if not qh else 'at %s L%d, manh %d' % (qh[0], len(qh), b.manhattan(qh[0], d['head']))}"
    eaters = p.corpse.get(d["id"])
    if eaters:
        line += "\n      pearls eaten by: " + ", ".join(f"#{e}{g.teams.get(e, '?')}x{n}{'(Q)' if e in qid.values() else ''}" for e, n in eaters.most_common(4))
    print(line)

print("\n-- own self-kills (noaction) by length class per 100 rounds, and top eaters of own self-kill pearls")
sk = Counter()
for d in p.deaths:
    if d["team"] == me and d["reason"] == "noaction":
        sk[(d["r"] // 100 * 100, "2" if d["len"] <= 2 else "3-4" if d["len"] <= 4 else "5-9" if d["len"] <= 9 else "10+")] += 1
print("  ", dict(sorted(sk.items())))

print("\n-- reverse splits (before >= 12, parent keeps <= 3) own:", sum(1 for x in p.splits if x[6] == me and x[3] >= 12 and x[4] <= 3),
      "opp:", sum(1 for x in p.splits if x[6] == op and x[3] >= 12 and x[4] <= 3))
big = [x for x in p.splits if x[6] == me and x[3] >= 20 and x[4] <= 3]
print("   own reverse splits of 20+ (round, id, before->p+c, at):", [(x[0], x[1], f"{x[3]}->{x[4]}+{x[5]}", x[7]) for x in big][:40])

print("\n-- ram chances on the enemy queen (q3): own side")
ch = [c for c in q3.get("chances", []) if c[1] == me]
print(f"   total {len(ch)}, taken {sum(1 for c in ch if c[5])}, not taken {sum(1 for c in ch if not c[5])}")
for c in [c for c in ch if not c[5]][:30]:
    r, _, did, ln, st, tk, hl, lg, oqa = c
    h = p.snap.get(r, {}).get(did)
    oq = p.qline[op].get(r)
    oq2 = p.qline[op].get(r + 1)
    later = [d for d in p.deaths if d["id"] == did and r <= d["r"] <= r + 3]
    free = -(-ln // 4)
    vis = f"view-dist(cheb) to her head at round start {b.cheb(h[0], oq[0]) if h and oq else '?'}, after her move {b.cheb(h[0], oq2[0]) if h and oq2 else '?'}"
    print(f"   r{r} #{did} L{ln} at {h[0] if h else '?'} needs {st} steps (free {free}, cost {max(0, st - free)}); {vis}; her L{hl} at {oq[0] if oq else '?'}; longest {lg}; own queen alive {oqa}; it did: {act(r, did)}"
          + (f"; then died r{later[0]['r']} {later[0]['reason']}" if later else ""))
ch2 = [c for c in q3.get("chances", []) if c[1] == op]
print(f"   (opponent's chances on the own queen: total {len(ch2)}, taken {sum(1 for c in ch2 if c[5])})")
for c in [c for c in ch2 if not c[5]][:6]:
    r, _, did, ln, st, tk, hl, lg, oqa = c
    print(f"     opp not taken: r{r} #{did} L{ln} needs {st}; it did: {act(r, did)}")
