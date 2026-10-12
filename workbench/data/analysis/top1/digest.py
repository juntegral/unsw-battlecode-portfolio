#!/usr/bin/env python3
"""One-page digest of a game from one team's point of view, for the close read.

  python3 digest.py <game_id> [team_id=306]

Sections: phase table, opening, queen routine, queen deaths with the killer's approach track, contact style,
late game (leader chain, feeding), roles, sonar. Distances are path steps (kelp/portals respected) unless marked manh.
"""
import csv
import sys
from collections import Counter, defaultdict, deque

import lib

GAMES = {g["game_id"]: g for g in csv.DictReader(open(__file__.rsplit("/", 1)[0] + "/games.csv"))}
HIST = 16


def lc(n):
    return "2" if n <= 2 else "3-4" if n <= 4 else "5-9" if n <= 9 else "10-19" if n <= 19 else "20+"


class D(lib.Hooks):
    def __init__(self, me):
        self.me = me
        self.op = "B" if me == "A" else "A"
        self.table = []
        self.hist = deque(maxlen=HIST)   # per round: {did: (head, len)}
        self.qhist = {"A": deque(maxlen=HIST), "B": deque(maxlen=HIST)}
        self.first_split = {}
        self.first_contact = None
        self.first_ram = None
        self.qline = []
        self.qcells = set()
        self.qdeaths = []
        self.rams = defaultdict(Counter)
        self.ramvic = defaultdict(Counter)
        self.sui = defaultdict(list)
        self.leader = []
        self.lenhist = []
        self.bigdeaths = []
        self.sonar_n = defaultdict(Counter)
        self.longest_id = {}
        self.eaten = defaultdict(Counter)
        self.intr = {}
        self.intr_done = []
        self.qsplits = defaultdict(list)
        self.births = {}
        self.parent = {}
        self.leader_moves = Counter()
        self.revsplits = []

    def round_start(self, g, r):
        b = g.board
        snap = {d: (body[0], len(body)) for d, body in g.bodies.items()}
        self.hist.append((r, snap))
        for s in "AB":
            mine = sorted(((len(body), -d) for d, body in g.bodies.items() if g.teams[d] == s), reverse=True)
            self.longest_id[s] = -mine[0][1] if mine else None
            q = g.bodies.get(b.queen[s])
            self.qhist[s].append((r, q[0] if q else None, len(q) if q else 0))
        if r % 50 == 0:
            row = [r]
            for s in (self.me, self.op):
                mine = sorted((len(body) for d, body in g.bodies.items() if g.teams[d] == s), reverse=True)
                q = g.bodies.get(b.queen[s])
                row.append(f"{len(mine):2d}u {sum(mine):3d}t top{mine[:3]} q{len(q) if q else 0}")
            self.table.append(row)
        if r % 100 == 0:
            h = Counter(lc(len(body)) for d, body in g.bodies.items() if g.teams[d] == self.me)
            self.lenhist.append((r, dict(sorted(h.items()))))
        # first contact
        if self.first_contact is None:
            mine = [body[0] for d, body in g.bodies.items() if g.teams[d] == self.me]
            theirs = [body[0] for d, body in g.bodies.items() if g.teams[d] == self.op]
            if any(b.manhattan(a, c) <= 4 for a in mine for c in theirs):
                self.first_contact = r
        q = g.bodies.get(b.queen[self.me])
        if q:
            self.qcells.add(q[0])
            dist = b.bfs(q[0], 9)
            near = sorted((dist[body[0]], len(body), d) for d, body in g.bodies.items()
                          if g.teams[d] == self.op and body[0] in dist)
            allies = sum(1 for d, body in g.bodies.items() if g.teams[d] == self.me and d != b.queen[self.me]
                         and dist.get(body[0], 99) <= 6)
            for dd, ln, d in near:
                if dd <= 6 and d not in self.intr:
                    self.intr[d] = dict(id=d, start=r, len=ln, min=dd, allies=allies)
                if d in self.intr:
                    self.intr[d]["min"] = min(self.intr[d]["min"], dd)
            for d in list(self.intr):
                body = g.bodies.get(d)
                if body is not None and dist.get(body[0], 99) > 9:
                    ep = self.intr.pop(d)
                    ep["out"], ep["end"] = "left", r
                    self.intr_done.append(ep)
            if r % 25 == 0:
                self.qline.append(f"r{r:3d} {q[0]} L{len(q)} ball{b.ball(q[0])} home{b.manhattan(q[0], b.starts[b.queen[self.me]])} "
                                  f"enemies<=8:{[(x[0], 'L%d' % x[1]) for x in near if x[0] <= 8][:4]} allies<=6:{allies} cells/25r:{len(self.qcells)}")
                self.qcells = set()
        if r % 25 == 0 and r >= 200:
            lid = self.longest_id[self.me]
            if lid is not None:
                body = g.bodies[lid]
                self.leader.append(f"r{r} #{lid} L{len(body)} at {body[0]} ball{b.ball(body[0])}"
                                   + (" (queen)" if lid == b.queen[self.me] else ""))

    def action(self, g, did, kind, nsteps):
        s = g.teams[did]
        pass

    def split(self, g, parent, child, before, plen, clen):
        s = g.teams[parent]
        self.births[child] = g.round
        self.parent[child] = parent
        if s == self.me and parent not in self.first_split and g.round < 60 and parent < 40:
            self.first_split[parent] = (g.round, before, plen, clen)
        if parent == g.board.queen[s]:
            self.qsplits[s].append(f"r{g.round} {before}->{plen}+{clen}")
        if s == self.me and before >= 12 and clen > plen:
            self.revsplits.append(f"r{g.round} #{parent} L{before} -> keeps {plen}, child #{child} gets {clen}")

    def eat(self, g, did, cell, origin):
        s = g.teams[did]
        if s != self.me:
            return
        role = "queen" if did == g.board.queen[s] else "longest" if did == self.longest_id[s] else "other"
        src = "natural" if origin[0] != "corpse" else ("own" if origin[1] == s else "enemy") + "_" + (
            "suicide" if origin[3] == "noaction" else "ram" if origin[3] == "headon" else "crash")
        self.eaten[g.round // 100][f"{role}<-{src}"] += 1

    def sonar(self, g, sender, value, raw):
        s = g.teams.get(sender)
        if s:
            self.sonar_n[s][g.round // 100] += 1

    def death(self, g, did, reason, length, body, actor):
        s = g.teams[did]
        b = g.board
        r = g.round
        rammed = reason == "headon" and actor is not None and actor != did
        if rammed:
            a = g.teams[actor]
            alen = g.act_start[1]
            if a != s:
                self.rams[a][(r // 100, lc(alen), "adjacent" if g.act_steps <= 1 else f"sprint{min(g.act_steps, 5)}")] += 1
                self.ramvic[a][(lc(alen), lc(length))] += 1
                if self.first_ram is None:
                    self.first_ram = (r, a, alen, length)
        if did == b.queen[s]:
            line = f"{'OWN' if s == self.me else 'ENEMY'} queen #{did} died r{r}: {reason}, L{length}, at {body[0]}"
            if rammed:
                k = actor
                track = []
                for rr, snap in self.hist:
                    if k in snap:
                        qpos = next((p for r2, p, _ in self.qhist[s] if r2 == rr), None)
                        if qpos is not None:
                            dd = b.bfs(qpos, 14).get(snap[k][0])
                            track.append(f"r{rr}:d{dd if dd is not None else '>14'}/L{snap[k][1]}")
                line += (f"\n      killer #{actor} team {g.teams[actor]} L{g.act_start[1]} from {g.act_start[0]}, {g.step_index + 1} of {g.act_steps} steps, "
                         f"born r{self.births.get(actor, 0)}"
                         f"\n      killer distance to the queen / its length, last rounds: {' '.join(track[-12:])}")
                qtrack = [f"r{rr}:{p}L{ln}" for rr, p, ln in list(self.qhist[s])[-6:]]
                line += f"\n      queen track: {' '.join(qtrack)}"
                others = []
                for d2, body2 in g.bodies.items():
                    if d2 in (did, actor):
                        continue
                    dd = b.manhattan(body2[0], body[0])
                    if dd <= 6:
                        others.append((dd, g.teams[d2], len(body2)))
                line += f"\n      other heads within manh 6 of the death cell: {sorted(others)[:10]}"
            self.qdeaths.append(line)
        if reason == "noaction" and s == self.me:
            lid = self.longest_id[s]
            dl = b.manhattan(body[0], g.bodies[lid][0]) if lid in g.bodies and lid != did else None
            dq = b.manhattan(body[0], g.bodies[b.queen[s]][0]) if b.queen[s] in g.bodies and b.queen[s] != did else None
            self.sui[r // 50].append((length, dl, dq))
        if length >= 15:
            self.bigdeaths.append(f"r{r} team {s} #{did} L{length} {reason}"
                                  + (f" by L{g.act_start[1]} in {g.step_index + 1}/{g.act_steps} steps" if rammed else "")
                                  + (" [team longest]" if did == self.longest_id[s] else "") + f" at {body[0]}")
        if s == self.op and did in self.intr:
            ep = self.intr.pop(did)
            if rammed and g.teams[actor] == self.me:
                ep["out"] = f"RAMMED by own L{g.act_start[1]}" + (" (the queen)" if actor == b.queen[self.me] else "")
            elif reason == "headon" and actor == did:
                ep["out"] = "it rammed someone"
            else:
                ep["out"] = "died " + reason
            ep["end"] = r
            self.intr_done.append(ep)

    def end(self, g, rounds, winner, result):
        self.rounds, self.winner = rounds, winner
        for ep in self.intr.values():
            ep["out"], ep["end"] = "still near at end/queen death", rounds
            self.intr_done.append(ep)


def main():
    gid = sys.argv[1]
    team = sys.argv[2] if len(sys.argv) > 2 else "306"
    gm = GAMES[gid]
    me = "A" if gm["teamAId"] == team else "B"
    op = "B" if me == "A" else "A"
    g = lib.Walk(gm["replay_path"])
    x = D(me)
    g.run(x)
    b = g.board
    print(f"=== {gid} {gm['map']} {b.w}x{b.h} | {gm['team' + me + 'Name']} (side {me}) vs {gm['team' + op + 'Name']} ({gm['team' + op + 'Elo']}) | "
          f"{'WIN' if x.winner == me else 'LOSS'} by {gm['end_type']} | rounds {x.rounds} | start dragons {len(b.starts)} | portals {len(b.portal_pair) // 2}")
    print("phase table (own | opp): units, total, top3, queen length")
    for row in x.table:
        print(f"  r{row[0]:3d} | {row[1]:38s} | {row[2]}")
    print(f"opening: first contact (heads within manh 4) r{x.first_contact}; first ram {x.first_ram} (round, attacker team, attacker len, victim len)")
    print("  first splits of starting dragons (id: round, len -> parent+child):", dict(list(x.first_split.items())[:8]))
    print(f"  queen splits own: {x.qsplits[me][:12]} | opp: {x.qsplits[op][:12]}")
    print("queen routine (own):")
    for line in x.qline:
        print("  " + line)
    eps = x.intr_done
    out = Counter(e["out"].split(" by ")[0] for e in eps)
    print(f"  enemy heads that came within 6 steps of the own queen: {len(eps)} episodes; outcomes {dict(out)}")
    close = [e for e in eps if e["min"] <= 3][:10]
    for e in close:
        print(f"    r{e['start']}-{e['end']} #{e['id']} L{e['len']} min dist {e['min']} allies<=6 at start {e['allies']} -> {e['out']}")
    print("queen deaths:")
    for line in x.qdeaths:
        print("  " + line)
    if not x.qdeaths:
        print("  none (both queens alive)")
    for s, label in ((me, "own"), (op, "opp")):
        tot = Counter()
        for (bucket, cls, how), n in x.rams[s].items():
            tot[(cls, how)] += n
        per = Counter()
        for (bucket, cls, how), n in x.rams[s].items():
            per[bucket] += n
        print(f"rams on enemy heads by {label}: per 100 rounds {dict(sorted(per.items()))}; by attacker length/steps {dict(sorted(tot.items()))}")
        print(f"   attacker len -> victim len: {dict(sorted(x.ramvic[s].items()))}")
    print("late game (own): leader every 25 rounds from r200:")
    for line in x.leader:
        print("  " + line)
    print("  self-kills ('noaction' deaths) per 50 rounds: n, mean len, share within manh 6 of own longest, share within 6 of own queen:")
    print("   ", {k * 50: (len(v), round(sum(a for a, _, _ in v) / len(v), 1),
                       round(sum(1 for _, d, _ in v if d is not None and d <= 6) / len(v), 2),
                       round(sum(1 for _, _, d in v if d is not None and d <= 6) / len(v), 2))
                  for k, v in sorted(x.sui.items())})
    print("  what own dragons ate per 100 rounds:", {k * 100: dict(v.most_common(5)) for k, v in sorted(x.eaten.items())})
    print("  'reverse' splits (child bigger than parent, len >= 12):", len(x.revsplits), "total; first:", x.revsplits[:2])
    print("  deaths of dragons >= 15:")
    for line in x.bigdeaths[:14]:
        print("    " + line)
    print("roles (own): length histogram every 100 rounds:", x.lenhist)
    print("sonar pings per 100 rounds: own", dict(sorted(x.sonar_n[me].items())), "| opp", dict(sorted(x.sonar_n[op].items())))


if __name__ == "__main__":
    main()
