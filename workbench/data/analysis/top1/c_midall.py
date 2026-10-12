#!/usr/bin/env python3
"""c_midall.py <team_id> <size> [max_games=120] [jobs=4] [upto=349]: the game by length class, all games of a team.

For the team and for its opponents in the same games (2000+ opponents, Schooltime left out), per 50 rounds and length
class (2, 3-4, 5-9, 10+), means per game:
  dragons (mean number alive in the class) | natural / corpse pearls per 100 dragon-rounds | splits by parents of the
  class: ordinary (parent keeps 3 or more, or 4 -> 2+2) and "shed" (parent of 5+ keeps only 2: the front part is left
  behind) | deaths: rammed / rammer / boxed / free-cell | segments lost in them | share of dragon-rounds with an enemy
  head in view | share of turns of two or more steps | deaths in head-ons between two dragons of the same team
  ("friend"; they are not rams and are kept out of rammed / rammer).
"""
import csv
import sys
from collections import Counter
from multiprocessing import Pool

sys.dont_write_bytecode = True
import c_lib  # noqa: E402
from c_lib import Hooks2, Stop, Walk2  # noqa: E402


def lc(n):
    return "2" if n <= 2 else "3-4" if n <= 4 else "5-9" if n <= 9 else "10+"


class M(Hooks2):
    def __init__(self, upto):
        self.upto = upto
        self.c = Counter()
        self.cur = None
        self.last_victim_team = None

    def round_start(self, g, r):
        if r > self.upto:
            raise Stop
        b = g.board
        k = r // 50 * 50
        heads = {"A": [], "B": []}
        for d, body in g.bodies.items():
            heads[g.teams[d]].append(body[0])
        for d, body in g.bodies.items():
            s = g.teams[d]
            o = "B" if s == "A" else "A"
            cl = lc(len(body))
            self.c[(k, s, cl, "rounds")] += 1
            h = body[0]
            for c2 in heads[o]:
                if b.cheb(h, c2) <= 3:
                    self.c[(k, s, cl, "ev")] += 1
                    break

    def turn(self, g, did):
        self.cur = (did, len(g.bodies[did]))

    def action(self, g, did, kind, nsteps):
        s = g.teams[did]
        cl = lc(len(g.bodies[did]))
        k = g.round // 50 * 50
        self.c[(k, s, cl, "turns")] += 1
        if kind == 0 and nsteps >= 2:
            self.c[(k, s, cl, "multi")] += 1

    def eat(self, g, did, cell, origin):
        s = g.teams[did]
        L = self.cur[1] if self.cur and self.cur[0] == did else len(g.bodies[did])
        self.c[(g.round // 50 * 50, s, lc(L), "nat" if origin[0] == "natural" else "cor")] += 1

    def split(self, g, parent, child, before, plen, clen):
        s = g.teams[parent]
        k = g.round // 50 * 50
        shed = before >= 5 and plen == 2
        self.c[(k, s, lc(before), "shed" if shed else "split")] += 1

    def death(self, g, did, reason, length, body, actor):
        s = g.teams[did]
        k = g.round // 50 * 50
        cl = lc(length)
        if reason == "headon":
            # the victim of a head-on dies first, the mover second; a head-on inside one team is not a ram
            if did == actor:
                key = "friend" if self.last_victim_team == s else "rammer"
            else:
                self.last_victim_team = s
                key = "friend" if (actor is not None and g.teams.get(actor) == s) else "rammed"
        else:
            occ = c_lib.occupied(g)
            free = sum(1 for n in g.board.nb(body[0]) if n is not None and n not in occ)
            key = "boxed" if free == 0 else "freedeath"
        self.c[(k, s, cl, key)] += 1
        self.c[(k, s, cl, key + "_seg")] += length


def work(job):
    gid, path, s, upto = job
    m = M(upto)
    try:
        Walk2(path).run(m)
    except Stop:
        pass
    except Exception as e:  # noqa: BLE001
        return gid, None, repr(e)
    out = Counter()
    for (k, side, cl, what), v in m.c.items():
        out[(k, "own" if side == s else "opp", cl, what)] += v
    for k in {key[0] for key in m.c}:
        out[(k, "games")] += 1
    return gid, out, None


if __name__ == "__main__":
    team = int(sys.argv[1])
    size_want = sys.argv[2]
    nums = [x for x in sys.argv[3:] if x.isdigit()]
    maxg = int(nums[0]) if nums else 120
    jobs = int(nums[1]) if len(nums) > 1 else 4
    upto = int(nums[2]) if len(nums) > 2 else 349
    opps = None
    if "--opp" in sys.argv:
        opps = {int(x) for x in sys.argv[sys.argv.index("--opp") + 1].split(",")}
    todo = []
    for g in csv.DictReader(open("games.csv")):
        if g["map"] == "Schooltime":
            continue
        size = "small" if g["map_size"].startswith("small") else "medium" if g["map_size"].startswith("medium") else "large"
        if size != size_want and size_want != g["map"]:
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
            if opps and int(g[f"team{o}Id"]) not in opps:
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
    print(f"=== LENGTH CLASSES team {team}, {size_want}, {len(todo)} games" + (f", opponents {sorted(opps)}" if opps else "") + ": means per game (a game counts in a block while it lasts)")
    print("block side class | dragons alive (mean) | natural / corpse pearls per 100 dragon-rounds | ordinary splits / sheds (5+ parent keeps 2) per game | "
          "deaths per game: rammed / rammer / boxed / free-cell | segments lost per game in those four | enemy head in view % of dragon-rounds | turns of 2+ steps % | "
          "deaths per game in head-ons inside the own team (not counted as rams)")
    for k in sorted({key[0] for key in total if len(key) == 4}):
        n = max(1, total[(k, "games")])
        for side in ("own", "opp"):
            for cl in ("2", "3-4", "5-9", "10+"):
                r = total[(k, side, cl, "rounds")]
                if not r:
                    continue
                t = max(1, total[(k, side, cl, "turns")])
                g = lambda what: total[(k, side, cl, what)]  # noqa: E731
                who = f"team {team}" if side == "own" else "opponents"
                print(f"r{k:3d} {who:10s} L{cl:4s} | {r / n / 50:5.1f} | nat {100 * g('nat') / r:5.2f} cor {100 * g('cor') / r:5.2f} | {g('split') / n:5.1f} / {g('shed') / n:4.1f} | "
                      f"{g('rammed') / n:4.1f} / {g('rammer') / n:4.1f} / {g('boxed') / n:4.1f} / {g('freedeath') / n:4.1f} | "
                      f"{g('rammed_seg') / n:5.1f} / {g('rammer_seg') / n:5.1f} / {g('boxed_seg') / n:5.1f} / {g('freedeath_seg') / n:5.1f} | "
                      f"ev {100 * g('ev') / r:3.0f}% | multi {100 * g('multi') / t:3.0f}% | friend {g('friend') / n:4.1f}")
            print()
