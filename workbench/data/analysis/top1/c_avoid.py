#!/usr/bin/env python3
"""c_avoid.py <team_id> <size> [max_games=60] [jobs=4] [upto=300]: what happens when an enemy head is on the next cell (all games).

A "meeting" = a dragon's turn begins with an enemy head on a neighbouring cell (kelp respected), both dragons 4 or
shorter (so either can ram the other with a free step when its turn comes). For the dragon whose turn it is:
  rammed it / stepped away / died otherwise (it had no other move, or moved into something)
and then, for the ones that stepped away, over the next 10 rounds:
  - was it rammed (by that enemy or another), did it die otherwise, is it alive
  - pearls eaten by it and by the enemy dragon it stepped away from (natural + corpse)
  - where the enemy dragon was 3 rounds later: on a cell our dragon had occupied (took the ground) or not
For the ones that rammed: who ate the pearls of the two corpses (own team / enemy / left 20 rounds).
Rows: the team's own dragons, and the opponents' dragons in the same games, by length pair (own <, =, > enemy).
"""
import csv
import sys
from collections import Counter
from multiprocessing import Pool

sys.dont_write_bytecode = True
import c_lib  # noqa: E402
from c_lib import Hooks2, Stop, Walk2  # noqa: E402

LOOK = 10


class V(Hooks2):
    def __init__(self, upto):
        self.upto = upto
        self.c = Counter()
        self.cur = None
        self.cellhead = {}
        self.watch = []           # dicts for stepped-away meetings
        self.ate = Counter()      # did -> pearls eaten (running)
        self.dead = {}            # did -> (round, reason, was_victim)
        self.ramcorpse = {}       # dead id -> key of the ram
        self.trail = {}

    def round_start(self, g, r):
        self.close(g)
        if r > self.upto + LOOK + 2:
            raise Stop
        self.cellhead = {body[0]: d for d, body in g.bodies.items()}
        keep = []
        for w in self.watch:
            if r - w["round"] == 3 and w["enemy"] in g.bodies:
                w["took"] = g.bodies[w["enemy"]][0] in w["cells"]
            if r - w["round"] >= LOOK:
                key = w["key"]
                d = self.dead.get(w["did"])
                if d is None:
                    fate = "alive"
                elif d[1] == "headon" and d[2]:
                    fate = "rammed"
                elif d[1] == "headon":
                    fate = "rammed someone"
                else:
                    fate = "died otherwise"
                self.c[key + ("then " + fate,)] += 1
                self.c[key + ("own ate",)] += self.ate[w["did"]] - w["ate0"]
                self.c[key + ("enemy ate",)] += self.ate[w["enemy"]] - w["eate0"]
                de = self.dead.get(w["enemy"])
                self.c[key + ("enemy alive" if de is None else "enemy dead",)] += 1
                if w.get("took"):
                    self.c[key + ("enemy took the ground",)] += 1
            else:
                keep.append(w)
        self.watch = keep

    def close(self, g):
        cur = self.cur
        self.cur = None
        if cur is None:
            return
        did, enemy, key, cells = cur
        d = self.dead.get(did)
        if d is not None and d[0] == g.round or (d is not None and did not in g.bodies):
            out = "rammed it" if d[1] == "headon" and not d[2] else "died otherwise"
            self.c[key + (out,)] += 1
            if out == "rammed it":
                self.ramcorpse[did] = key
                self.ramcorpse[enemy] = key
        else:
            self.c[key + ("stepped away",)] += 1
            self.watch.append(dict(round=g.round, did=did, enemy=enemy, key=key, ate0=self.ate[did], eate0=self.ate[enemy], cells=cells))
        self.c[key + ("n",)] += 1

    def turn(self, g, did):
        self.close(g)
        if g.round > self.upto:
            return
        body = g.bodies[did]
        L = len(body)
        if L > 4:
            return
        s = g.teams[did]
        b = g.board
        for n in b.nb(body[0]):
            if n is None:
                continue
            d2 = self.cellhead.get(n)
            if d2 is None or d2 not in g.bodies or g.teams[d2] == s or g.bodies[d2][0] != n:
                continue
            L2 = len(g.bodies[d2])
            if L2 > 4:
                continue
            rel = "own shorter" if L < L2 else "same length" if L == L2 else "own longer"
            self.cur = (did, d2, (s, rel), set(body))
            return

    def moved(self, g, did, head, step_index, ate):
        self.cellhead[head] = did

    def eat(self, g, did, cell, origin):
        self.ate[did] += 1
        if origin[0] == "corpse" and origin[3] == "headon":
            key = self.ramcorpse.get(origin[2])
            if key is not None:
                self.c[key + ("ram pearl eaten by own team" if g.teams[did] == key[0] else "ram pearl eaten by enemy",)] += 1

    def pearl_new(self, g, cell, origin):
        if origin[0] == "corpse" and origin[3] == "headon":
            key = self.ramcorpse.get(origin[2])
            if key is not None:
                self.c[key + ("ram pearls dropped",)] += 1

    def death(self, g, did, reason, length, body, actor):
        self.dead[did] = (g.round, reason, did != actor)
        cur = self.cur
        if cur is not None and reason == "headon" and did != actor and actor == cur[0]:
            # the victim of our rammer dies first: register so that its pearls are attributed
            self.ramcorpse[did] = cur[2]
            self.ramcorpse[actor] = cur[2]

    def end(self, g, rounds, winner, result):
        self.close(g)


def work(job):
    gid, path, s, upto = job
    v = V(upto)
    try:
        Walk2(path).run(v)
    except Stop:
        pass
    except Exception as e:  # noqa: BLE001
        return gid, None, repr(e)
    out = Counter()
    for key, n in v.c.items():
        out[("own" if key[0] == s else "opp",) + key[1:]] += n
    return gid, out, None


if __name__ == "__main__":
    team = int(sys.argv[1])
    size_want = sys.argv[2]
    nums = [x for x in sys.argv[3:] if x.isdigit()]
    maxg = int(nums[0]) if nums else 60
    jobs = int(nums[1]) if len(nums) > 1 else 4
    upto = int(nums[2]) if len(nums) > 2 else 300
    todo = []
    for g in csv.DictReader(open("games.csv")):
        if g["map"] == "Schooltime":
            continue
        size = "small" if g["map_size"].startswith("small") else "medium" if g["map_size"].startswith("medium") else "large"
        if size != size_want and size_want != "any":
            continue
        if not c_lib.battle_ok(g):
            continue
        for s in "AB":
            if int(g[f"team{s}Id"]) != team:
                continue
            o = "B" if s == "A" else "A"
            try:
                if float(g[f"team{o}Elo"]) < 2000:
                    continue
            except ValueError:
                continue
            todo.append((g["game_id"], g["replay_path"], s, upto))
    todo = todo[:: max(1, len(todo) // maxg)][:maxg]
    total = Counter()
    with Pool(jobs) as pool:
        for gid, out, err in pool.imap_unordered(work, todo):
            if err:
                print("error", gid, err)
                continue
            total.update(out)
    n_games = len(todo)
    print(f"=== MEETINGS team {team}, {size_want} maps, {n_games} games{c_lib.battle_label()}, rounds 0-{upto}: a turn that begins with an enemy head on a neighbouring cell, both dragons 4 or shorter")
    print("side, lengths | meetings (per game) | rammed it % / stepped away % / died otherwise % | of those that stepped away, 10 rounds later: rammed % / died otherwise % / alive % | "
          "pearls eaten in those 10 rounds per meeting: by the dragon that stepped away / by the enemy it left | enemy stood on the dragon's cells 3 rounds later % | "
          "of the rams: pearls dropped, eaten by the rammer's team % / by the other team %")
    for side in ("own", "opp"):
        for rel in ("own shorter", "same length", "own longer", "all"):
            def get(what):
                if rel == "all":
                    return sum(v for k, v in total.items() if k[0] == side and k[2] == what)
                return total[(side, rel, what)]
            n = get("n")
            if not n:
                continue
            away = max(1, get("stepped away"))
            dropped = max(1, get("ram pearls dropped"))
            label = {"own shorter": "shorter than the enemy", "same length": "same length", "own longer": "longer than the enemy", "all": "all"}[rel]
            who = f"team {team}" if side == "own" else "its opponents"
            print(f"{who:13s} {label:22s} | {n:6d} ({n / n_games:5.1f}) | ram {100 * get('rammed it') / n:3.0f}% away {100 * get('stepped away') / n:3.0f}% died {100 * get('died otherwise') / n:3.0f}% | "
                  f"rammed {100 * get('then rammed') / away:3.0f}% died {100 * get('then died otherwise') / away:3.0f}% alive {100 * get('then alive') / away:3.0f}% | "
                  f"ate {get('own ate') / away:4.2f} vs enemy {get('enemy ate') / away:4.2f} | took {100 * get('enemy took the ground') / away:3.0f}% | "
                  f"{get('ram pearls dropped')} dropped: rammer's team {100 * get('ram pearl eaten by own team') / dropped:3.0f}%, other team {100 * get('ram pearl eaten by enemy') / dropped:3.0f}%")
