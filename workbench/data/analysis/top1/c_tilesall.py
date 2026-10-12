#!/usr/bin/env python3
"""c_tilesall.py <team_id> <size|map name> [max_games=120] [jobs=4] [upto=150]: use of the fountain tiles of the own half by
the shape of the tile, all games of a team (opponents 2000+, Schooltime left out).

Fountain tile = 10+ natural pearls per 500 rounds in the pooled supply map (c_supply.py). Own half = nearer (path) to
the own queen's spawn. Shape of the tile: "dead end" = one open side; "narrow" = two open sides and 20 or fewer cells
within 4 path steps; "open" = the rest. Per shape, for the team's own half and for the opponents' own half in the
same games, rounds 0..upto, means per game:
  tiles | share of them the home team ate from | natural pearls eaten there by the home team / by the visitors |
  share of tile-rounds with a pearl lying / with a body on the tile | home-team non-ram deaths on the tiles |
  mean round of the first home-team eat on a tile it ate from | mean rounds between first seeing a tile and first eating on it
"""
import csv
import json
import sys
from collections import Counter
from multiprocessing import Pool

sys.dont_write_bytecode = True
import c_lib  # noqa: E402
from c_lib import Hooks2, Stop, Walk2  # noqa: E402

HOT = {}


def hot_for(mapname):
    v = HOT.get(mapname)
    if v is None:
        try:
            sup = json.load(open("c_out/supply_%s.json" % mapname.lower().replace(" ", "_")))
        except FileNotFoundError:
            HOT[mapname] = set()
            return HOT[mapname]
        v = set()
        for key, n in sup["cells"].items():
            if n / sup["games"] >= 10:
                x, y = key.split(",")
                v.add((int(x), int(y)))
        HOT[mapname] = v
    return v


class T(Hooks2):
    def __init__(self, hot, upto):
        self.hot = hot
        self.upto = upto
        self.seen = {"A": {}, "B": {}}
        self.first = {"A": {}, "B": {}}
        self.eaten = {"A": Counter(), "B": Counter()}
        self.lying = Counter()
        self.body = Counter()
        self.deaths = {"A": Counter(), "B": Counter()}
        self._view = {}
        self.dspawn = {}

    def view(self, b, cell):
        v = self._view.get(cell)
        if v is None:
            v = self._view[cell] = tuple(c for c in self.hot if b.cheb(cell, c) <= 3)
        return v

    def round_start(self, g, r):
        b = g.board
        if not self.dspawn:
            for s in "AB":
                self.dspawn[s] = b.bfs(b.starts[b.queen[s]], 10 ** 9)
        if r > self.upto:
            raise Stop
        occ = c_lib.occupied(g)
        for c in self.hot:
            if c in g.pearls:
                self.lying[c] += 1
            elif c in occ:
                self.body[c] += 1
        for d, body in g.bodies.items():
            for c in self.view(b, body[0]):
                self.seen[g.teams[d]].setdefault(c, r)

    def moved(self, g, did, head, step_index, ate):
        for c in self.view(g.board, head):
            self.seen[g.teams[did]].setdefault(c, g.round)

    def eat(self, g, did, cell, origin):
        if origin[0] == "natural" and cell in self.hot:
            s = g.teams[did]
            self.eaten[s][cell] += 1
            self.first[s].setdefault(cell, g.round)

    def death(self, g, did, reason, length, body, actor):
        if reason != "headon" and body[0] in self.hot:
            self.deaths[g.teams[did]][body[0]] += 1


def work(job):
    gid, path, s, mapname, upto = job
    hot = hot_for(mapname)
    t = T(hot, upto)
    g = Walk2(path)
    try:
        g.run(t)
    except Stop:
        pass
    except Exception as e:  # noqa: BLE001
        return gid, None, repr(e)
    b = g.board
    out = Counter()
    for c in hot:
        da, db = t.dspawn["A"].get(c, 10 ** 6), t.dspawn["B"].get(c, 10 ** 6)
        if da == db:
            continue
        home = "A" if da < db else "B"
        away = "B" if home == "A" else "A"
        deg, ball = b.degree(c), b.ball(c, 4)
        shape = "dead end" if deg == 1 else "narrow" if deg == 2 and ball <= 20 else "open"
        side = "own" if home == s else "opp"
        for sh in (shape, "all"):
            k = (side, sh)
            out[k + ("tiles",)] += 1
            out[k + ("ate_from",)] += t.eaten[home][c] > 0
            out[k + ("home_n",)] += t.eaten[home][c]
            out[k + ("away_n",)] += t.eaten[away][c]
            out[k + ("lying",)] += t.lying[c]
            out[k + ("body",)] += t.body[c]
            out[k + ("deaths",)] += t.deaths[home][c]
            if c in t.first[home]:
                out[k + ("first_sum",)] += t.first[home][c]
                out[k + ("first_cnt",)] += 1
                if c in t.seen[home]:
                    out[k + ("lag_sum",)] += t.first[home][c] - t.seen[home][c]
                    out[k + ("lag_cnt",)] += 1
            if c in t.seen[home]:
                out[k + ("seen",)] += 1
    out[("games",)] = 1
    out[("rounds",)] = min(upto, t.upto) + 1
    return gid, out, None


if __name__ == "__main__":
    team = int(sys.argv[1])
    want = sys.argv[2]
    nums = [x for x in sys.argv[3:] if x.isdigit()]
    maxg = int(nums[0]) if nums else 120
    jobs = int(nums[1]) if len(nums) > 1 else 4
    upto = int(nums[2]) if len(nums) > 2 else 150
    todo = []
    for g in csv.DictReader(open("games.csv")):
        if g["map"] == "Schooltime":
            continue
        size = "small" if g["map_size"].startswith("small") else "medium" if g["map_size"].startswith("medium") else "large"
        if want not in (size, g["map"]):
            continue
        if int(g["rounds"]) <= upto:
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
            todo.append((g["game_id"], g["replay_path"], s, g["map"], upto))
    todo = todo[:: max(1, len(todo) // maxg)][:maxg]
    total = Counter()
    with Pool(jobs) as pool:
        for gid, out, err in pool.imap_unordered(work, todo):
            if err:
                print("error", gid, err)
                continue
            total.update(out)
    n = max(1, total[("games",)])
    print(f"=== FOUNTAIN TILES BY SHAPE team {team}, {want}, {n} games that lasted past round {upto}, rounds 0-{upto}, means per game")
    print("whose half, shape | tiles | seen by the home team % | eaten from by the home team % | natural pearls eaten there: home team / visitors | "
          "tile-rounds with a pearl lying % / with a body % | home-team non-ram deaths on the tiles | first eat (mean round) | rounds from first sight to first eat")
    for side in ("own", "opp"):
        for sh in ("dead end", "narrow", "open", "all"):
            k = (side, sh)
            tiles = total[k + ("tiles",)]
            if not tiles:
                continue
            tr = tiles * (upto + 1)
            who = f"team {team}'s half" if side == "own" else "opponents' half"
            print(f"{who:18s} {sh:8s} | {tiles / n:5.1f} | {100 * total[k + ('seen',)] / tiles:3.0f}% | {100 * total[k + ('ate_from',)] / tiles:3.0f}% | "
                  f"{total[k + ('home_n',)] / n:6.1f} / {total[k + ('away_n',)] / n:5.1f} | {100 * total[k + ('lying',)] / tr:3.0f}% / {100 * total[k + ('body',)] / tr:3.0f}% | "
                  f"{total[k + ('deaths',)] / n:5.1f} | {total[k + ('first_sum',)] / max(1, total[k + ('first_cnt',)]):5.1f} | {total[k + ('lag_sum',)] / max(1, total[k + ('lag_cnt',)]):5.1f}")
