#!/usr/bin/env python3
"""Lead's own recount of sub-session A3's main all-games claims (written without reading A3's scripts).

Per game (opp elo >= 2000, Schooltime excluded; teams 1119, 306, 91, 264 and the other side of our games):
  meetings  : a turn begins with an enemy head (<= 4 long) on a cell next to the own head, own dragon <= 4 long.
              Did the dragon ram it (both die head-on in this action)? By relative length and round block.
  charges   : rams made with a move of 2+ steps by a dragon that had no enemy head next to it at turn start.
  ram pearls: pearls dropped by enemy-on-enemy head-on deaths; who ate them; who started the ram.
  adjacent  : dragon of 2-4, no enemy head in its 7x7 view, a pearl on a free cell next to its head, and that cell
              has another free neighbour. Did it eat that pearl this turn? By round block; near own longest (5+).
  r300      : own total length below the opponent's at round 300, and the result (from q/*.json).
Usage: recount3.py run [jobs]   -> r3/<gid>.json
       recount3.py table        -> prints tables
"""
import csv
import json
import math
import os
import sys
from collections import defaultdict
from multiprocessing import Pool

from lib import Hooks, Walk

TEAMS = {"306": "Vibing++", "91": "SSS", "264": "forgot", "1119": "meow"}
TC = ("tc30-test-new", "tc30-dev1b-new")


def block(r):
    return min(r // 50, 9)


class H(Hooks):
    def __init__(self):
        self.meet = defaultdict(lambda: [0, 0])      # (side, rel, block) -> [n, rammed]
        self.charge = defaultdict(int)               # (side, block) -> charges
        self.rams = defaultdict(int)                 # (starter side, block) -> enemy rams
        self.dropped = defaultdict(int)              # (starter side) -> pearls dropped by enemy rams
        self.eaten = defaultdict(int)                # (starter side, eater side) -> pearls eaten
        self.adj = defaultdict(lambda: [0, 0])       # (side, block, nearleader) -> [n, eaten]
        self.pend = None
        self.ram_ids = {}
        self.dead_now = []

    def flush(self, g):
        p = self.pend
        self.pend = None
        if p is None:
            return
        did, side, length, adj_en, pearl_cells, near, nsteps, ate, rnd = p
        heads_dead = [d for d, t, r in self.dead_now if r == "headon"]
        teams_dead = {t for d, t, r in self.dead_now if r == "headon"}
        rammed = did in heads_dead and len(teams_dead) == 2
        b = block(rnd)
        if rammed:
            self.rams[(side, b)] += 1
            for d, t, r in self.dead_now:
                if r == "headon":
                    self.ram_ids[d] = side
            self.dropped[side] += sum(math.ceil(L / 2) for d, t, r, L in self.dead_full if r == "headon")
        if adj_en and length <= 4:
            for rel in adj_en.values():
                k = (side, rel, b)
                self.meet[k][0] += 1
            hit = [d for d in heads_dead if d in adj_en]
            if rammed and hit:
                self.meet[(side, adj_en[hit[0]], b)][1] += 1
        if rammed and not adj_en and nsteps >= 2:
            self.charge[(side, b)] += 1
        if pearl_cells:
            k = (side, b, near)
            self.adj[k][0] += 1
            self.adj[k][1] += ate[0]

    def round_start(self, g, r):
        self.flush(g)

    def action(self, g, did, kind, nsteps):
        self.flush(g)
        self.dead_now = []
        self.dead_full = []
        head, length = g.act_start
        side = g.teams[did]
        b = g.board
        nbs = [c for c in b.nb(head) if c is not None]
        nbset = set(nbs)
        adj_en = {}
        enemy_in_view = False
        own_long = None
        for d2, body in g.bodies.items():
            if d2 == did:
                continue
            h2 = body[0]
            if g.teams[d2] != side:
                if h2 in nbset and len(body) <= 4:
                    L2 = len(body)
                    adj_en[d2] = "shorter" if length < L2 else "same" if length == L2 else "longer"
                if not enemy_in_view and b.cheb(head, h2) <= 3:
                    enemy_in_view = True
            elif len(body) >= 5 and (own_long is None or len(body) > own_long[1]):
                own_long = (h2, len(body))
        pearl_cells = None
        near = "none5"
        if 2 <= length <= 4 and not enemy_in_view:
            cand = [c for c in nbs if c in g.pearls]
            if cand:
                occ = set()
                for body in g.bodies.values():
                    occ.update(body)
                ok = []
                for c in cand:
                    if c in occ:
                        continue
                    if any(n is not None and n != head and n not in occ for n in b.nb(c)):
                        ok.append(c)
                if ok:
                    pearl_cells = set(ok)
                    if own_long is not None:
                        near = "near" if b.manhattan(head, own_long[0]) <= 9 else "far"
        self.pend = (did, side, length, adj_en, pearl_cells, near, nsteps if kind == 0 else 0, [0], g.round)

    def eat(self, g, did, cell, origin):
        p = self.pend
        if p is not None and p[0] == did and p[4] and cell in p[4]:
            p[7][0] = 1
        if origin[0] == "corpse" and origin[3] == "headon" and origin[2] in self.ram_ids:
            self.eaten[(self.ram_ids[origin[2]], g.teams[did])] += 1

    def death(self, g, did, reason, length, body, actor):
        self.dead_now.append((did, g.teams[did], reason))
        self.dead_full.append((did, g.teams[did], reason, length))

    def end(self, g, rounds, winner, result):
        self.flush(g)


def g_round(p):
    return p[8]


def one(row):
    gid = row["game_id"]
    out = f"r3/{gid}.json"
    if os.path.exists(out):
        return
    h = H()
    # the ram bookkeeping needs the starter marked before pearls are eaten: deaths are flushed at the next action,
    # and nothing can be eaten between the two deaths of a ram and that flush except by the acting dragon (dead).
    Walk(row["replay_path"]).run(h)
    res = {
        "game_id": gid,
        "meet": [[*k, *v] for k, v in h.meet.items()],
        "charge": [[*k, v] for k, v in h.charge.items()],
        "rams": [[*k, v] for k, v in h.rams.items()],
        "dropped": dict(h.dropped),
        "eaten": [[*k, v] for k, v in h.eaten.items()],
        "adj": [[*k, *v] for k, v in h.adj.items()],
    }
    json.dump(res, open(out + ".tmp", "w"))
    os.rename(out + ".tmp", out)


def wanted():
    rows = []
    for g in csv.DictReader(open("games.csv")):
        if g["map"] == "Schooltime":
            continue
        for s in "AB":
            o = "B" if s == "A" else "A"
            if g[f"team{s}Id"] in TEAMS and g[f"team{o}Elo"] and float(g[f"team{o}Elo"]) >= 2000:
                # all sizes for us; large maps only for the top three
                if g[f"team{s}Id"] == "1119" or int(g["cells"]) > 1500:
                    rows.append(g)
                    break
    return rows


def size(c):
    return "small" if c <= 700 else "medium" if c <= 1500 else "large"


def table():
    meet = defaultdict(lambda: [0, 0])
    charge = defaultdict(float)
    rams = defaultdict(float)
    games = defaultdict(int)
    drop = defaultdict(float)
    eat = defaultdict(float)
    adj = defaultdict(lambda: [0, 0])
    r300 = defaultdict(lambda: [0, 0, 0, 0])
    missing = 0
    for g in csv.DictReader(open("games.csv")):
        if g["map"] == "Schooltime":
            continue
        sz = size(int(g["cells"]))
        path = f"r3/{g['game_id']}.json"
        d = None
        for s in "AB":
            o = "B" if s == "A" else "A"
            if g[f"team{s}Id"] not in TEAMS or not g[f"team{o}Elo"] or float(g[f"team{o}Elo"]) < 2000:
                continue
            name = TEAMS[g[f"team{s}Id"]]
            if name != "meow" and sz != "large":
                continue
            if d is None:
                if not os.path.exists(path):
                    missing += 1
                    break
                d = json.load(open(path))
            groups = [(name, s)]
            if name == "meow":
                groups = [("meow all", s), ("meow test build" if g["battle_id"] in TC else "meow live", s),
                          ("run " + g["battle_id"], s), ("opponents of meow", o)]
            for grp, side in groups:
                other = "B" if side == "A" else "A"
                games[(grp, sz)] += 1
                for sd, rel, b, n, k in d["meet"]:
                    if sd == side:
                        for key in ((grp, sz, "all", "all"), (grp, sz, rel, "all"), (grp, sz, "all", "r0-149" if b < 3 else "r150+")):
                            meet[key][0] += n
                            meet[key][1] += k
                for sd, b, n in d["charge"]:
                    if sd == side and b < 3:
                        charge[(grp, sz)] += n
                for sd, b, n in d["rams"]:
                    rams[(grp, sz, "own" if sd == side else "enemy")] += n
                    if b < 3:
                        rams[(grp, sz, "own149" if sd == side else "enemy149")] += n
                for st, n in d["dropped"].items():
                    drop[(grp, sz, "all")] += n
                    drop[(grp, sz, "own start" if st == side else "enemy start")] += n
                for st, eater, n in d["eaten"]:
                    who = "own" if eater == side else "enemy"
                    eat[(grp, sz, "all", who)] += n
                    eat[(grp, sz, "own start" if st == side else "enemy start", who)] += n
                for sd, b, near, n, k in d["adj"]:
                    if sd == side:
                        per = "r0-149" if b < 3 else "r150-299" if b < 6 else "r300+"
                        for key in ((grp, sz, per, "all"), (grp, sz, per, near)):
                            adj[key][0] += n
                            adj[key][1] += k
                q = json.load(open(f"q/{g['game_id']}.json"))
                mine, theirs = q["sides"][side]["per"]["total"], q["sides"][other]["per"]["total"]
                if len(mine) > 300 and len(theirs) > 300 and mine[300] and theirs[300]:
                    x = r300[(grp, sz)]
                    x[0] += 1
                    behind = mine[300] < theirs[300]
                    x[1] += behind
                    x[2] += behind and g["winner"] == side
                    x[3] += (not behind) and g["winner"] == side
    print("games without r3 output:", missing)

    def pct(v):
        return f"{100 * v[1] / v[0]:.0f}% of {v[0]}" if v[0] else "-"

    for sz in ("large", "medium", "small"):
        print(f"\n===== {sz} maps =====")
        grps = sorted({g for g, z in games if z == sz}, key=lambda x: (x.startswith("run "), x))
        print("group | games | meetings rammed: all | shorter | same | longer | r0-149 | r150+ | charges r0-149 /game | rams started /game (r0-149) | share of rams started")
        for grp in grps:
            n = games[(grp, sz)]
            own, en = rams[(grp, sz, "own")], rams[(grp, sz, "enemy")]
            print(f"{grp:28s} | {n:3d} | {pct(meet[(grp, sz, 'all', 'all')])} | {pct(meet[(grp, sz, 'shorter', 'all')])} | {pct(meet[(grp, sz, 'same', 'all')])} | "
                  f"{pct(meet[(grp, sz, 'longer', 'all')])} | {pct(meet[(grp, sz, 'all', 'r0-149')])} | {pct(meet[(grp, sz, 'all', 'r150+')])} | {charge[(grp, sz)] / n:.1f} | "
                  f"{own / n:.1f} ({rams[(grp, sz, 'own149')] / n:.1f}) | {100 * own / max(1, own + en):.0f}%")
        print("\ngroup | ram pearls dropped /game | eaten by own / enemy (of dropped) | of rams own side started: own share | of rams the enemy started: own share")
        for grp in grps:
            n = games[(grp, sz)]
            dall = drop[(grp, sz, "all")]
            if not dall:
                continue
            a = eat[(grp, sz, "all", "own")], eat[(grp, sz, "all", "enemy")]
            o1, o2 = drop[(grp, sz, "own start")], drop[(grp, sz, "enemy start")]
            print(f"{grp:28s} | {dall / n:.0f} | {100 * a[0] / dall:.0f}% / {100 * a[1] / dall:.0f}% | "
                  f"{100 * eat[(grp, sz, 'own start', 'own')] / max(1, o1):.0f}% of {o1:.0f} | {100 * eat[(grp, sz, 'enemy start', 'own')] / max(1, o2):.0f}% of {o2:.0f}")
        print("\ngroup | free pearl next to head eaten: r0-149 | r150-299 | r300+ | r150-299 near own longest (<=9) | far from it | no own 5+ | r300+ near | far | none")
        for grp in grps:
            print(f"{grp:28s} | " + " | ".join(pct(adj[(grp, sz, per, 'all')]) for per in ("r0-149", "r150-299", "r300+")) + " | "
                  + " | ".join(pct(adj[(grp, sz, 'r150-299', nr)]) for nr in ("near", "far", "none5")) + " | "
                  + " | ".join(pct(adj[(grp, sz, 'r300+', nr)]) for nr in ("near", "far", "none5")))
        print("\ngroup | games reaching r300 | behind in total length at r300 | wins among those | wins when level or ahead")
        for grp in grps:
            x = r300[(grp, sz)]
            if x[0]:
                print(f"{grp:28s} | {x[0]} | {x[1]} | {x[2]} | {x[3]} of {x[0] - x[1]}")


if __name__ == "__main__":
    if sys.argv[1] == "run":
        os.makedirs("r3", exist_ok=True)
        rows = wanted()
        print("games:", len(rows), flush=True)
        os.nice(10)
        with Pool(int(sys.argv[2]) if len(sys.argv) > 2 else 5) as p:
            for i, _ in enumerate(p.imap_unordered(one, rows, chunksize=4)):
                if i % 50 == 0:
                    print(i, flush=True)
        print("done", flush=True)
    else:
        table()
