#!/usr/bin/env python3
"""b_tally.py <game_id> ...: recount, per team, of everything quoted in the answers of deep-read-2.md (sub-session A2).

For every game given and for both teams in it, one pass with lib.Walk. Totals are printed per team id (91 = SSS,
264 = forgot, others listed too), with the game ids behind each count where the count is small.

  A. own queen, rounds that began with an enemy head within 3 path steps: her order (move n / split), did her own
     move make the nearest enemy head further / same / nearer, own heads within 6 steps (0 / 1 / 2 / 3+), enemy
     heads rammed by an own dragon while within 6 steps of her; and how the queen ended
  B. every split or suicide order of the own queen by free neighbour cells (0 / 1+) and kind of split
     (4 -> 2+2 "mother", "shed 2" from a longer queen, other), and her deaths with reason
  C. followers: dragons that had the ENEMY queen's head inside their 7x7 view for 6+ rounds in a streak (gaps of up
     to 2 rounds): length at the start, rounds, whether they ate, how the streak ended
  D. kills of the enemy queen: attacker length, steps, paid steps, rounds the killer itself had her in view before
  E. dragons of 15+ that died: per victim team by reason; for rams the attacker length, steps, whether the attacker
     had split in the 5 rounds before or was a split child born in the last 3 rounds
  F. reverse splits (12+ long, parent keeps 3 or fewer): head had no free cell / had one
  G. non-ram deaths in rounds 0-100: with / without a free cell next to the head, and the order given
  H. feeding: deaths with a free cell within 6 cells of the own queen / of the own longest dragon, per 100 rounds
"""
import csv
import sys
from collections import Counter, defaultdict

import lib

GAMES = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
D = "NESW"
T = defaultdict(lambda: defaultdict(Counter))      # team -> section -> counter
L = defaultdict(lambda: defaultdict(list))         # team -> section -> list of notes


def lc(n):
    return "2" if n <= 2 else "3" if n == 3 else "4" if n == 4 else "5-9" if n <= 9 else "10+"


class H(lib.Hooks):
    def __init__(self, gid):
        self.gid = gid
        g = GAMES[gid]
        self.tid = {"A": g["teamAId"], "B": g["teamBId"]}
        self.close = {}
        self.afterq = {}
        self.inview = defaultdict(list)          # (hunter id) -> [(round, len)]
        self.eats = defaultdict(list)
        self.born = {}
        self.splits = defaultdict(list)
        self.longest = {}
        self.qhead = {}
        self.nearq_enemy = {}
        self.qdead = {}
        self.ended = {}
        self.viewhist = defaultdict(set)

    def other(self, s):
        return "B" if s == "A" else "A"

    def round_start(self, g, r):
        b = g.board
        self.close = {}
        self.nearq_enemy = {}
        for s in "AB":
            ls = sorted(((len(o), -d) for d, o in g.bodies.items() if g.teams[d] == s), reverse=True)
            self.longest[s] = -ls[0][1] if ls else None
            q = g.bodies.get(b.queen[s])
            self.qhead[s] = q[0] if q else None
            if q is None:
                continue
            t = self.tid[s]
            dist = b.bfs(q[0], 6)
            en = sorted((dist[o[0]], len(o), d) for d, o in g.bodies.items() if g.teams[d] != s and o[0] in dist)
            al = [d for d, o in g.bodies.items() if g.teams[d] == s and d != b.queen[s] and o[0] in dist]
            self.nearq_enemy[s] = {x[2] for x in en}
            if en and en[0][0] <= 3:
                self.close[s] = (en[0][0], len(al), en[0][1])
            o = self.other(s)
            for d, body in g.bodies.items():
                if g.teams[d] == o and b.cheb(body[0], q[0]) <= 3:
                    self.viewhist[d].add(r)
                    # a follower must be able to walk to her: path distance at most 6 (not just across a kelp wall)
                    if d != b.queen[o] and body[0] in dist:
                        self.inview[d].append((r, len(body), dist[body[0]]))

    def action(self, g, did, kind, nsteps):
        b = g.board
        s = g.teams[did]
        t = self.tid[s]
        body = g.bodies[did]
        if did == b.queen[s]:
            if s in self.close:
                T[t]["A orders"]["move %d" % nsteps if kind == 0 else "split" if kind == 1 else "suicide"] += 1
                T[t]["A own heads within 6"]["0" if self.close[s][1] == 0 else "1" if self.close[s][1] == 1 else "2" if self.close[s][1] == 2 else "3+"] += 1
                T[t]["A nearest intruder length"][lc(self.close[s][2])] += 1
                T[t]["A close rounds"]["n"] += 1
                T[t]["A close rounds by game"][self.gid] += 1
                if kind != 0:
                    L[t]["A close round with a split"].append(f"{self.gid} r{g.round} L{len(body)}")
                    self.afterq[s] = ("split", self.close[s][0])
            if kind != 0:
                occ = set()
                for o2 in g.bodies.values():
                    occ.update(o2)
                free = sum(1 for n in b.nb(body[0]) if n is not None and n not in occ)
                self.pending_qsplit = (s, free, len(body), kind)
        if kind == 1 and did != b.queen[s] and len(body) >= 12:
            occ = set()
            for o2 in g.bodies.values():
                occ.update(o2)
            self.bigfree = (did, sum(1 for n in b.nb(body[0]) if n is not None and n not in occ))

    def moved(self, g, did, head, step_index, ate):
        b = g.board
        s = g.teams.get(did)
        if s is None or did != b.queen[s] or step_index != g.act_steps or s not in self.close:
            return
        dist = b.bfs(head, 8)
        en = [dist[o[0]] for i, o in g.bodies.items() if g.teams[i] != s and o[0] in dist]
        after = min(en) if en else 99
        before = self.close[s][0]
        T[self.tid[s]]["A her move made the nearest enemy head"]["further" if after > before else "same" if after == before else "NEARER"] += 1
        if after < before:
            L[self.tid[s]]["A nearer"].append(f"{self.gid} r{g.round}")

    def split(self, g, parent, child, before, plen, clen):
        b = g.board
        s = g.teams[parent]
        t = self.tid[s]
        self.born[child] = (g.round, parent, clen)
        self.splits[parent].append(g.round)
        if parent == b.queen[s]:
            p = getattr(self, "pending_qsplit", None)
            free = p[1] if p and p[0] == s else -1
            kind = "4 -> 2+2" if before == 4 else "shed 2 (queen 5+)" if clen == 2 else "cut: keeps 2-3" if plen <= 3 else "other"
            T[t]["B queen splits"][("no free cell" if free == 0 else "1+ free cells") + ", " + kind] += 1
            if free == 0 or kind != "4 -> 2+2":
                L[t]["B queen splits not 4->2+2 with a free cell"].append(f"{self.gid} r{g.round} {before}->{plen}+{clen} free {free}")
        elif before >= 12 and plen <= 3:
            bf = getattr(self, "bigfree", None)
            free = bf[1] if bf and bf[0] == parent else -1
            T[t]["F reverse splits"]["head had no free cell" if free == 0 else "head had a free cell"] += 1

    def eat(self, g, did, cell, origin):
        self.eats[did].append(g.round)

    def death(self, g, did, reason, length, body, actor):
        b = g.board
        s = g.teams[did]
        t = self.tid[s]
        r = g.round
        self.ended[did] = (r, reason, actor)
        rammed = reason == "headon" and actor is not None and actor != did
        occ = set()
        for o2 in g.bodies.values():
            occ.update(o2)
        boxed = not any(n is not None and n not in occ for n in b.nb(body[0]))
        if did == b.queen[s]:
            self.qdead[s] = r
            if rammed:
                T[t]["A how the queen ended"]["rammed"] += 1
                kt = self.tid[g.teams[actor]]
                alen, steps = g.act_start[1], g.act_steps
                free = -(-alen // 4)
                seen_before = len([x for x in self.viewhist[actor] if r - 40 <= x < r])
                T[kt]["D queen kills by attacker length"][lc(alen)] += 1
                T[kt]["D queen kills by steps"]["next cell" if steps <= 1 else "%d steps" % steps] += 1
                nb = self.born.get(actor)
                L[kt]["D queen kills"].append(f"{self.gid} r{r}: #{actor} L{alen}, {steps} steps ({max(0, steps - free)} paid), had her in view in {seen_before} of the 40 rounds before, "
                                              f"{'born r%d as a %d-long' % (nb[0], nb[2]) if nb else 'a starting dragon'}, victim queen L{length}")
            else:
                T[t]["A how the queen ended"][reason + (" (no free cell)" if boxed else " (had a free cell)")] += 1
                L[t]["B queen deaths not by ram"].append(f"{self.gid} r{r} {reason} L{length} {'no free cell' if boxed else 'had a free cell'}")
        # intruder rammed by a defender near the other queen
        if rammed and g.teams[actor] != s:
            a = g.teams[actor]
            if did in self.nearq_enemy.get(a, ()):
                T[self.tid[a]]["A intruders rammed by an own dragon within 6 steps of the queen"]["n"] += 1
                L[self.tid[a]]["A intruders rammed"].append(f"{self.gid} r{r} L{g.act_start[1]} rams L{length}")
        if length >= 15 and did != b.queen[s]:
            if rammed and g.teams[actor] != s:
                kt = self.tid[g.teams[actor]]
                alen, steps = g.act_start[1], g.act_steps
                trick = "attacker split in the 5 rounds before" if any(r - 5 <= x <= r for x in self.splits.get(actor, [])) else \
                        "attacker is a split child born in the last 3 rounds" if actor in self.born and r - self.born[actor][0] <= 3 else "no split"
                T[t]["E own 15+ dragons lost"]["rammed by L" + lc(alen)] += 1
                T[kt]["E enemy 15+ dragons rammed, by attacker length"][lc(alen)] += 1
                T[kt]["E enemy 15+ dragons rammed, by steps"]["next cell" if steps <= 1 else "2-3 steps" if steps <= 3 else "4+ steps"] += 1
                T[kt]["E enemy 15+ dragons rammed, split trick"][trick] += 1
                if trick != "no split":
                    L[kt]["E split trick"].append(f"{self.gid} r{r} L{alen} rams L{length}: {trick}")
                if r >= 300:
                    T[kt]["E enemy 15+ rammed after r300"]["n"] += 1
            elif not rammed:
                T[t]["E own 15+ dragons lost"][reason + (", no free cell" if boxed else ", had a free cell")] += 1
        if reason != "headon":
            if r <= 100:
                order = {0: "move", 1: "split", 2: "suicide"}.get(g.act_kind, "none") if actor == did else "other"
                T[t]["G non-ram deaths r0-100"][("no free cell" if boxed else "HAD A FREE CELL") + ", order " + order + ", reason " + reason] += 1
            if not boxed:
                q = self.qhead.get(s)
                lid = self.longest.get(s)
                lh = g.bodies.get(lid)
                where = "near the queen" if q is not None and did != b.queen[s] and b.manhattan(body[0], q) <= 6 else \
                        "near the longest dragon" if lh is not None and lid != did and b.manhattan(body[0], lh[0]) <= 6 else "elsewhere"
                T[t]["H deaths by choice (a free cell was there)"][f"r{r // 100 * 100} {where}"] += 1
                T[t]["H segments in those deaths"][f"r{r // 100 * 100} {where}"] += length

    def end(self, g, rounds, winner, result):
        b = g.board
        for s in "AB":
            t = self.tid[s]
            T[t]["0 games"]["n"] += 1
            L[t]["0 games"].append(self.gid)
            if b.queen[s] in g.bodies:
                T[t]["A how the queen ended"]["alive"] += 1
        # followers
        for d, lst in self.inview.items():
            s = g.teams.get(d) or self.team_of.get(d)
        self.rounds = rounds


def followers(h, g):
    b = g.board
    out = []
    for d, lst in h.inview.items():
        streak = [lst[0]]
        for x in lst[1:] + [None]:
            if x is not None and x[0] - streak[-1][0] <= 3:
                streak.append(x)
                continue
            if len(streak) >= 6:
                r1, r2 = streak[0][0], streak[-1][0]
                ate = sum(1 for rr in h.eats.get(d, []) if r1 <= rr <= r2)
                e = h.ended.get(d)
                ds = sorted(v[2] for v in streak)
                out.append((d, r1, r2, len(streak), streak[0][1], ate, e, ds[len(ds) // 2], ds[0]))
            streak = [x] if x is not None else []
    return out


team_of = {}
for gid in sys.argv[1:]:
    h = H(gid)
    h.team_of = {}
    w = lib.Walk(GAMES[gid]["replay_path"])

    class Wrap(H):
        pass
    # remember each dragon's team (bodies are removed at death)
    orig_round = h.round_start

    def rs(g, r, orig=orig_round, hh=h):
        for d in g.bodies:
            hh.team_of[d] = g.teams[d]
        orig(g, r)
    h.round_start = rs
    w.run(h)
    b = w.board
    for (d, r1, r2, n, ln, ate, e, dmed, dmin) in followers(h, w):
        s = h.team_of.get(d)
        if s is None:
            continue
        t = h.tid[s]
        o = "B" if s == "A" else "A"
        T[t]["C followers (6+ rounds with the enemy queen's head in view)"]["n"] += 1
        T[t]["C follower length at the start"][lc(ln)] += 1
        T[t]["C follower streak length"]["6-9" if n < 10 else "10-19" if n < 20 else "20+"] += 1
        T[t]["C follower ate during the streak"]["nothing" if ate == 0 else "1" if ate == 1 else "2+"] += 1
        qd = h.qdead.get(o)
        if e and e[0] <= r2 + 2:
            if e[1] == "headon" and e[2] == d:
                endk = "it rammed the queen" if qd == e[0] else "it rammed another dragon"
            elif e[1] == "headon":
                endk = "it was rammed"
            else:
                endk = "it died (" + e[1] + ")"
        elif qd is not None and qd <= r2 + 2:
            endk = "the queen was rammed by someone else"
        else:
            endk = "lost her / game end"
        T[t]["C how the streak ended"][endk] += 1
        T[t]["C follower median path distance to her head"]["1-2" if dmed <= 2 else "3" if dmed == 3 else "4" if dmed == 4 else "5-6"] += 1
        if n >= 10:
            L[t]["C followers of 10+ rounds"].append(f"{gid} #{d} L{ln} r{r1}-{r2} ({n} rounds), median {dmed} steps away (min {dmin}), ate {ate}, {endk}")
    print("done", gid, file=sys.stderr)

NAMES = {"91": "SSS", "264": "forgot to mention", "306": "Vibing++"}
for t in sorted(T, key=lambda x: (x not in ("91", "264"), x)):
    print(f"\n===== team {t} {NAMES.get(t, '(opponent)')} =====")
    for sec in sorted(T[t]):
        print(f"  {sec}: {dict(sorted(T[t][sec].items()))}")
    for sec in sorted(L[t]):
        items = L[t][sec]
        print(f"  [{sec}] ({len(items)}): " + " | ".join(items[:40]))
