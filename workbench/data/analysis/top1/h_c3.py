#!/usr/bin/env python3
"""Candidate 3 ("no clock"): what the leader rule does, counted on replays.

Our code (mybot2/main.cpp): after `grow_round` (150 on maps over 1,200 cells, 300 otherwise) every dragon treats
the LONGEST OWN DRAGON IT KNOWS OF as "the leader" (hear_exact / hear_sighting / sonar, forgotten after 25 rounds).
 - a dragon that knows a longer one: pearls within 9 cells (Manhattan, wrapped) of that leader's last known head are
   no targets, lose EAT_BONUS and cost ZONE_PEARL_PENALTY 600 (refresh_leader_zone, in_leader_pearl_zone, score_step);
 - a dragon that knows no longer one is "the leader" itself: is_leader() -> it never splits and never trades;
 - any dragon longer than 4 stops splitting (split_child_size).
A replay cannot show what a dragon knows, so the proxy here is geometry: is there an own dragon LONGER than this one
with its head within 9 cells of the pearl (then the zone probably applies), and is this dragon the longest own dragon
within 9 cells of itself (then it is probably "leader").

Counted per (group, map class, phase, ...):
 A. eat  : a non-queen dragon of 2-4 starts its turn with a pearl on a free cell next to its head, that cell has
           another free neighbour, no enemy head in its 7x7 view.  Did its first step take such a pearl?
           Split by: a longer own dragon's head within 9 cells of the pearl (its length class) / none.
 B. fate : pearls declined in A after the clock: eaten within 10 rounds by own team / by the enemy / still lying.
 C. split: a non-queen dragon of exactly 4 (and of 5-9) starts its turn with no enemy head in view: did it split?
           Split by: it is the longest own dragon within 9 cells of its head (ties count as longest) or not.
 D. per game: natural pearls eaten and units by 50-round block come from q/ (not here).
Phases use OUR clock for every team so that the columns compare: "before" = rounds < grow, "after" = grow..399
(feeding starts at 400 for us), "late" = 400+; grow = 150 on maps over 1,200 cells, else 300.
Usage: python3 h_c3.py run [jobs]  -> h_out/c3/<gid>.json ; python3 h_c3.py table -> stdout
"""
import csv
import json
import os
import random
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool

import lib

OUTD = "h_out/c3"
TEAMS = {"306": "Vibing++", "91": "SSS", "264": "forgot", "1119": "meow"}


def lcl(n):
    return "3-4" if n <= 4 else "5-9" if n <= 9 else "10+"


class H(lib.Hooks):
    def __init__(self, cells):
        self.grow = 150 if cells > 1200 else 300
        self.eat_tab = Counter()     # (side, phase, lenself, leaderclass, ate)
        self.split_tab = Counter()   # (side, phase, lenclass, locallongest, split)
        self.fate = Counter()        # (side, phase, fate)
        self.pend = None
        self.watch = {}              # cell -> (round, side, phase)
        self.heads = {}

    def phase(self, r):
        return "before" if r < self.grow else "after" if r < 400 else "late"

    def round_start(self, g, r):
        self.close(g)
        old = [c for c, v in self.watch.items() if r - v[0] > 10]
        for c in old:
            _, s, ph = self.watch.pop(c)
            self.fate[(s, ph, "still lying after 10 rounds" if c in g.pearls else "gone (covered or eaten unseen)")] += 1

    def close(self, g):
        p = self.pend
        self.pend = None
        if p is None:
            return
        side, ph, n, lead, cands, first = p
        ate = int(first in cands) if first is not None else 0
        self.eat_tab[(side, ph, n, lead, ate)] += 1
        if not ate and ph != "before":
            for c in cands:
                if c in g.pearls and c not in self.watch:
                    self.watch[c] = (g.round, side, ph)

    def action(self, g, did, kind, nsteps):
        self.close(g)
        b = g.board
        s = g.teams[did]
        if did == b.queen[s]:
            return
        body = g.bodies[did]
        n = len(body)
        if n > 9:
            return
        head = body[0]
        o = "B" if s == "A" else "A"
        # enemy head in view?
        own = []
        enemy_in_view = False
        occupied = set()
        for d2, other in g.bodies.items():
            occupied.update(other)
            if d2 == did:
                continue
            if g.teams[d2] == s:
                own.append((other[0], len(other)))
            elif b.cheb(other[0], head) <= 3:
                enemy_in_view = True
        if enemy_in_view:
            return
        ph = self.phase(g.round)
        # C. split behaviour of dragons of 4 and of 5-9
        if n >= 4:
            near = [L for (h2, L) in own if b.manhattan(h2, head) <= 9]
            local_longest = int(not near or max(near) <= n)
            self.split_tab[(s, ph, "4" if n == 4 else "5-9", local_longest, int(kind == 1))] += 1
        if n > 4 or kind != 0:
            return      # A counts move orders of dragons of 2-4 only (a split at 4 is not a declined pearl)
        # A. free pearl next to the head
        cands = []
        for c in b.nb(head):
            if c is None or c in occupied or c not in g.pearls:
                continue
            if any(m is not None and m != head and m not in occupied for m in b.nb(c)):
                cands.append(c)
        if not cands:
            return
        best = 0
        for c in cands:
            for (h2, L) in own:
                if L > n and b.manhattan(h2, c) <= 9:
                    best = max(best, L)
        lead = "none" if best == 0 else lcl(best)
        first = None
        if kind == 0 and g.act_dirs:
            first = b.step(head, g.act_dirs[0])
        self.pend = (s, ph, n, lead, cands, first)

    def eat(self, g, did, cell, origin):
        v = self.watch.pop(cell, None)
        if v is not None:
            r0, s, ph = v
            self.fate[(s, ph, "eaten by own team within 10 rounds" if g.teams[did] == s else "eaten by the enemy within 10 rounds")] += 1

    def end(self, g, rounds, winner, result):
        self.close(g)


def work(row):
    out = f"{OUTD}/{row['game_id']}.json"
    if os.path.exists(out):
        return row["game_id"], None
    try:
        h = H(int(row["cells"]))
        lib.Walk(row["replay_path"]).run(h)
        data = dict(game_id=row["game_id"], grow=h.grow,
                    eat=[list(k) + [v] for k, v in h.eat_tab.items()],
                    split=[list(k) + [v] for k, v in h.split_tab.items()],
                    fate=[list(k) + [v] for k, v in h.fate.items()])
        tmp = out + ".tmp%d" % os.getpid()
        json.dump(data, open(tmp, "w"), separators=(",", ":"))
        os.replace(tmp, out)
        return row["game_id"], None
    except Exception as exc:  # noqa: BLE001
        return row["game_id"], f"{type(exc).__name__}: {exc}"


def pick_rows():
    rows = [r for r in csv.DictReader(open("games.csv")) if r["map"] != "Schooltime"]
    random.seed(7)
    ours, top = [], defaultdict(list)
    for r in rows:
        a, b_ = r["teamAId"], r["teamBId"]
        ea, eb = float(r["teamAElo"] or 0), float(r["teamBElo"] or 0)
        if (a == "1119" and eb >= 2000) or (b_ == "1119" and ea >= 2000):
            ours.append(r)
            continue
        for t, e_opp in ((a, eb), (b_, ea)):
            if t in ("306", "91", "264") and e_opp >= 2000:
                top[t].append(r)
    sel = list(ours)
    seen = {r["game_id"] for r in sel}
    for t, lst in top.items():
        random.shuffle(lst)
        k = 0
        for r in lst:
            if r["game_id"] in seen:
                continue
            sel.append(r)
            seen.add(r["game_id"])
            k += 1
            if k >= 130:
                break
    return sel


def run(jobs):
    os.makedirs(OUTD, exist_ok=True)
    rows = pick_rows()
    errs = []
    with Pool(jobs) as pool:
        for i, (gid, err) in enumerate(pool.imap_unordered(work, rows, chunksize=4)):
            if err:
                errs.append((gid, err))
            if (i + 1) % 100 == 0:
                print(i + 1, "/", len(rows), "errors", len(errs), flush=True)
    print("done", len(rows), "errors", errs[:5])


def table():
    games = {r["game_id"]: r for r in csv.DictReader(open("games.csv"))}
    eat = defaultdict(lambda: [0, 0])
    split = defaultdict(lambda: [0, 0])
    fate = Counter()
    ngames = Counter()
    for f in os.listdir(OUTD):
        if not f.endswith(".json"):
            continue
        d = json.load(open(f"{OUTD}/{f}"))
        g = games[d["game_id"]]
        cls = "large" if int(g["cells"]) > 1200 else "other"
        for s in "AB":
            o = "B" if s == "A" else "A"
            tid, oid = g[f"team{s}Id"], g[f"team{o}Id"]
            grp = []
            if tid == "1119":
                grp.append("meow")
                grp.append("meow live" if (g["battle_id"].startswith("dl-") or g["battle_id"].endswith("-old")) else "meow cand")
            elif oid == "1119":
                grp.append("opp of meow")
            if tid in ("306", "91", "264") and float(g[f"team{o}Elo"] or 0) >= 2000:
                grp.append(TEAMS[tid])
                grp.append("top3")
            for gname in grp:
                ngames[(gname, cls)] += 1
            for side, ph, n, lead, ate, v in d["eat"]:
                if side != s:
                    continue
                for gname in grp:
                    keys = [(gname, cls, ph, "all", lead), (gname, cls, ph, "all", "any"), (gname, cls, ph, str(n), lead)]
                    if lead != "none":
                        keys.append((gname, cls, ph, "all", "longer"))
                    for key in keys:
                        eat[key][0] += v
                        eat[key][1] += v * ate
            for side, ph, lc, loc, sp, v in d["split"]:
                if side != s:
                    continue
                for gname in grp:
                    for key in ((gname, cls, ph, lc, loc), (gname, cls, ph, lc, "any")):
                        split[key][0] += v
                        split[key][1] += v * sp
            for side, ph, what, v in d["fate"]:
                if side != s:
                    continue
                for gname in grp:
                    fate[(gname, cls, ph, what)] += v
    G = ["meow live", "meow cand", "meow", "opp of meow", "Vibing++", "SSS", "forgot", "top3"]

    def pc(v):
        return f"{100 * v[1] / v[0]:3.0f}% of {v[0]:6d}" if v[0] else "      -       "

    print("games walked:", {f"{k[0]} {k[1]}": v for k, v in sorted(ngames.items())})
    for cls, grow in (("large", 150), ("other", 300)):
        print(f"\n===== maps {'over 1,200 cells' if cls == 'large' else 'of 1,200 cells or fewer'}: our clock is round {grow}")
        print("A. a free pearl next to the head is eaten (dragon 2-4, no enemy head in view), by whether a LONGER own dragon's head is within 9 cells of the pearl")
        for ph, label in (("before", f"rounds 0-{grow - 1}"), ("after", f"rounds {grow}-399"), ("late", "rounds 400+")):
            print(f"  {label}:   any | no longer own dragon near | a longer one near | ... of 3-4 | ... of 5-9 | ... of 10+")
            for g in G:
                cells_ = [pc(eat[(g, cls, ph, "all", k)]) for k in ("any", "none", "longer", "3-4", "5-9", "10+")]
                print(f"     {g:12s} " + " | ".join(cells_))
        print("A2. the same for a 2-long only / 3-long only / 4-long only, after the clock (any | none near | longer near)")
        for n in ("2", "3", "4"):
            for g in ("meow live", "opp of meow", "top3"):
                def col(k):
                    if k == "any":
                        tot = [0, 0]
                        for kk in ("none", "3-4", "5-9", "10+"):
                            v = eat[(g, cls, "after", n, kk)]
                            tot[0] += v[0]
                            tot[1] += v[1]
                        return pc(tot)
                    if k == "longer":
                        tot = [0, 0]
                        for kk in ("3-4", "5-9", "10+"):
                            v = eat[(g, cls, "after", n, kk)]
                            tot[0] += v[0]
                            tot[1] += v[1]
                        return pc(tot)
                    return pc(eat[(g, cls, "after", n, k)])
                print(f"     L{n} {g:12s} " + " | ".join(col(k) for k in ("any", "none", "longer")))
        print("B. pearls declined after the clock (first decline of each pearl): what became of them, per game")
        for ph in ("after", "late"):
            for g in ("meow live", "meow cand", "opp of meow", "top3"):
                n = ngames[(g, cls)]
                tot = sum(v for k, v in fate.items() if k[:3] == (g, cls, ph))
                if not n or not tot:
                    continue
                parts = "; ".join(f"{k[3]} {v / n:.1f} ({100 * v / tot:.0f}%)" for k, v in sorted(fate.items()) if k[:3] == (g, cls, ph))
                print(f"     {ph:6s} {g:12s} {tot / n:5.1f} per game: {parts}")
        print("C. a dragon of exactly 4 / of 5-9 splits (no enemy head in view): share of such turns;  any | it is the longest own dragon within 9 cells | it is not")
        for ph, label in (("before", f"rounds 0-{grow - 1}"), ("after", f"rounds {grow}-399"), ("late", "rounds 400+")):
            for lc in ("4", "5-9"):
                print(f"  {label}, length {lc}:")
                for g in G:
                    print(f"     {g:12s} " + " | ".join(pc(split[(g, cls, ph, lc, k)]) for k in ("any", 1, 0)))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        try:
            os.nice(10)
        except OSError:
            pass
        run(int(sys.argv[2]) if len(sys.argv) > 2 else 4)
    else:
        table()
