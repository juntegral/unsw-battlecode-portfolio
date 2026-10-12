#!/usr/bin/env python3
"""c_contest.py <team_id> <size> [max_games=200] [jobs=4] [upto=500] [opp_ids]: who gets a pearl that both teams can reach (all games).

For every pearl that appears (natural, or dropped by a corpse) in the team's games against 2000+ opponents on maps of the
given size (Schooltime left out): the path distance (kelp, wrap and portals respected, bodies ignored, at most 8) from the
pearl to the nearest head of each team at that moment. Then: who eats it within 20 rounds, and what the nearest dragon
of each team did by the start of the next round but one (ended nearer to the pearl or ate it / not nearer / died).
Tables, one row per class of (own nearest distance minus enemy nearest distance):
  pearls | eaten by own team % / by the enemy % / left % | own nearest dragon ended nearer % | enemy nearest dragon ended nearer %
for all pearls and separately for natural pearls, pearls of ram corpses and pearls of other corpses.
"own only" = no enemy head within 8 steps; "enemy only" = no own head within 8 steps.
"""
import csv
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool

sys.dont_write_bytecode = True
import c_lib  # noqa: E402
from c_lib import Hooks2, Stop, Walk2  # noqa: E402

LOOK = 20
UPTO = 500


def other(s):
    return "B" if s == "A" else "A"


class C(Hooks2):
    def __init__(self, upto):
        self.upto = upto
        self.open = {}      # cell -> record
        self.watch = []     # (check_round, record)
        self.done = []

    def round_start(self, g, r):
        if r > self.upto + LOOK:
            raise Stop
        keep = []
        for rr, rec in self.watch:
            if rr > r:
                keep.append((rr, rec))
                continue
            for s in "AB":
                w = rec["near"][s]
                if w is None:
                    continue
                did, d0 = w
                if rec["eater"] is not None and rec["eater_id"] == did:
                    rec["move"][s] = "nearer"
                elif did not in g.bodies:
                    rec["move"][s] = "dead"
                else:
                    d1 = rec["dist"].get(g.bodies[did][0], 99)
                    rec["move"][s] = "nearer" if d1 < d0 else "not"
            rec["dist"] = None
        self.watch = keep
        for cell in [c for c, rec in self.open.items() if r - rec["round"] > LOOK]:
            self.done.append(self.open.pop(cell))

    def pearl_new(self, g, cell, origin):
        if g.round > self.upto:
            return
        b = g.board
        dist = b.bfs(cell, 8)
        near = {"A": None, "B": None}
        for did, body in g.bodies.items():
            d = dist.get(body[0])
            if d is None:
                continue
            s = g.teams[did]
            if near[s] is None or d < near[s][1]:
                near[s] = (did, d)
        kind = "natural" if origin[0] == "natural" else "ram" if origin[3] == "headon" else "corpse"
        rec = dict(round=g.round, kind=kind, cside=origin[1] if origin[0] == "corpse" else None, near=near, dist=dist,
                   eater=None, eater_id=None, wait=None, move={"A": None, "B": None})
        old = self.open.pop(cell, None)
        if old is not None:
            self.done.append(old)
        self.open[cell] = rec
        self.watch.append((g.round + (1 if kind == "natural" else 2), rec))

    def eat(self, g, did, cell, origin):
        rec = self.open.pop(cell, None)
        if rec is None:
            return
        rec["eater"] = g.teams[did]
        rec["eater_id"] = did
        rec["wait"] = g.round - rec["round"]
        self.done.append(rec)

    def end(self, g, rounds, winner, result):
        self.done.extend(self.open.values())
        self.open = {}


def cls(do, de):
    if do is None and de is None:
        return "nobody within 8"
    if de is None:
        return "own only"
    if do is None:
        return "enemy only"
    x = do - de
    return "own nearer by 3+" if x <= -3 else "own nearer by 2" if x == -2 else "own nearer by 1" if x == -1 else "same distance" if x == 0 else \
        "enemy nearer by 1" if x == 1 else "enemy nearer by 2" if x == 2 else "enemy nearer by 3+"


ORDER = ["own only", "own nearer by 3+", "own nearer by 2", "own nearer by 1", "same distance", "enemy nearer by 1", "enemy nearer by 2",
         "enemy nearer by 3+", "enemy only", "nobody within 8"]


def work(job):
    gid, path, s, upto = job
    c = C(upto)
    try:
        Walk2(path).run(c)
    except Stop:
        c.done.extend(c.open.values())
    except Exception as e:  # noqa: BLE001
        return gid, None, repr(e)
    o = other(s)
    agg = Counter()
    for rec in c.done:
        do = rec["near"][s][1] if rec["near"][s] else None
        de = rec["near"][o][1] if rec["near"][o] else None
        k = cls(do, de)
        kind = rec["kind"]
        if kind == "ram":
            kind2 = "ram corpse"
        elif kind == "corpse":
            kind2 = "own non-ram corpse" if rec["cside"] == s else "enemy non-ram corpse"
        else:
            kind2 = "natural"
        ph = "r0-99" if rec["round"] < 100 else "r100-199" if rec["round"] < 200 else "r200+"
        if rec["eater"] is None or rec["wait"] > LOOK:
            res = "left"
        else:
            res = "own" if rec["eater"] == s else "enemy"
        for key in (("all", k), (kind2, k), (kind2 + " " + ph, k)):
            agg[key + ("n",)] += 1
            agg[key + (res,)] += 1
            if res != "left":
                agg[key + (res + "_wait",)] += rec["wait"]
            if rec["move"][s] is not None:
                agg[key + ("own_" + rec["move"][s],)] += 1
            if rec["move"][o] is not None:
                agg[key + ("en_" + rec["move"][o],)] += 1
    return gid, agg, None


if __name__ == "__main__":
    team = int(sys.argv[1])
    size_want = sys.argv[2]
    maxg = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    jobs = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    upto = int(sys.argv[5]) if len(sys.argv) > 5 else UPTO
    opps = {int(x) for x in sys.argv[6].split(",")} if len(sys.argv) > 6 else None
    todo = []
    for g in csv.DictReader(open("games.csv")):
        if g["map"] == "Schooltime":
            continue
        size = "small" if g["map_size"].startswith("small") else "medium" if g["map_size"].startswith("medium") else "large"
        if size != size_want and size_want != "any":
            continue
        for s in "AB":
            if int(g[f"team{s}Id"]) != team:
                continue
            o = other(s)
            try:
                if float(g[f"team{o}Elo"]) < 2000:
                    continue
            except ValueError:
                continue
            if opps and int(g[f"team{o}Id"]) not in opps:
                continue
            todo.append((g["game_id"], g["replay_path"], s, upto))
    todo = todo[:: max(1, len(todo) // maxg)][:maxg]
    total = Counter()
    with Pool(jobs) as pool:
        for gid, agg, err in pool.imap_unordered(work, todo):
            if err:
                print("error", gid, err)
                continue
            total.update(agg)
    print(f"=== CONTEST team {team}, {size_want} maps, {len(todo)} games, pearls appearing in rounds 0-{upto}" + (f", opponents {sorted(opps)}" if opps else ""))
    print("kind | class | pearls | eaten within 20 rounds by own team % (mean wait) / by the enemy % (mean wait) / left % | own nearest dragon: ended nearer % / not nearer % / died % | enemy nearest dragon: nearer % / not % / died %")
    kinds = ["all", "natural", "ram corpse", "own non-ram corpse", "enemy non-ram corpse"]
    kinds += [k + " " + ph for k in ("natural", "ram corpse") for ph in ("r0-99", "r100-199", "r200+")]
    for kind in kinds:
        for k in ORDER:
            n = total[(kind, k, "n")]
            if not n:
                continue
            own, en, left = total[(kind, k, "own")], total[(kind, k, "enemy")], total[(kind, k, "left")]
            on, onot, od = total[(kind, k, "own_nearer")], total[(kind, k, "own_not")], total[(kind, k, "own_dead")]
            en_n, en_not, en_d = total[(kind, k, "en_nearer")], total[(kind, k, "en_not")], total[(kind, k, "en_dead")]
            ot, et = max(1, on + onot + od), max(1, en_n + en_not + en_d)
            print(f"{kind:28s} | {k:18s} | {n:6d} | own {100 * own / n:3.0f}% ({total[(kind, k, 'own_wait')] / max(1, own):4.1f}) / enemy {100 * en / n:3.0f}% ({total[(kind, k, 'enemy_wait')] / max(1, en):4.1f}) / left {100 * left / n:3.0f}% | "
                  f"own {100 * on / ot:3.0f} / {100 * onot / ot:3.0f} / {100 * od / ot:3.0f} | enemy {100 * en_n / et:3.0f} / {100 * en_not / et:3.0f} / {100 * en_d / et:3.0f}")
        print()
