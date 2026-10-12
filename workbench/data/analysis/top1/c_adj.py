#!/usr/bin/env python3
"""c_adj.py <game_id|team_id> [size] [max_games=60] [jobs=4] [--examples N]: a pearl on the cell next to the head: is it eaten?

For every dragon-turn that begins with a pearl on a cell next to the head (kelp respected, the cell free of bodies):
did the dragon step onto a pearl cell next to it that turn (ate), and if not, what became of that pearl in the next
10 rounds (eaten by the own team, by the enemy, still lying)? Split by
  - phase: r0-49, r50-149, r150-299, r300+
  - length of the dragon: 2, 3, 4, 5+; and whether it is the team's longest dragon
  - exits: free cells next to the pearl cell other than the dragon's own head cell, at that moment (0 = stepping in
    leaves no way out next turn unless something moves; 1; 2+)
  - whether an enemy head is within 2 path steps of the pearl; whether another own head is also next to the pearl
With a game id: both sides of that game (side A = own). With a team id and a size: all games of the team against
2000+ opponents on maps of that size (Schooltime left out); own side and the opponents' side are pooled separately.
--examples N prints the first N declined turns (round, dragon, cells) of the own side for reading in story.py.
"""
import csv
import sys
from collections import Counter
from multiprocessing import Pool

sys.dont_write_bytecode = True
import c_lib  # noqa: E402
from c_lib import GAMES, Hooks2, Walk2  # noqa: E402

LOOK = 10
POCKET_CAP = 48      # our bot's rule: a kelp-enclosed region (portals not crossed) of fewer cells than this is a "pocket"


def region_sizes(b):
    """Size of the kelp-enclosed region of every cell (open edges only, portals not crossed), capped at POCKET_CAP."""
    w, h = b.w, b.h
    size = {}

    def open_nb(cell):
        x, y = cell
        out = []
        for d in range(4):
            if d == 0:
                key = (x, y, "N")
            elif d == 2:
                key = (x, (y + 1) % h, "N")
            elif d == 3:
                key = (x, y, "W")
            else:
                key = ((x + 1) % w, y, "W")
            if key in b.kelp or key in b.portal_pair:
                continue
            out.append(((x + lib_dx[d]) % w, (y + lib_dy[d]) % h))
        return out

    for y in range(h):
        for x in range(w):
            if (x, y) in size:
                continue
            seen = {(x, y)}
            stack = [(x, y)]
            while stack:
                c = stack.pop()
                for n in open_nb(c):
                    if n not in seen:
                        seen.add(n)
                        stack.append(n)
            for c in seen:
                size[c] = len(seen)
    return size


lib_dx = (0, 1, 0, -1)
lib_dy = (-1, 0, 1, 0)


def phase(r):
    return "r0-49" if r < 50 else "r50-149" if r < 150 else "r150-299" if r < 300 else "r300+"


class A(Hooks2):
    def __init__(self):
        self.c = Counter()
        self.cur = None
        self.longest = {"A": None, "B": None}
        self.watch = {}          # pearl cell -> list of (round, key)
        self.examples = []
        self.region = None

    def round_start(self, g, r):
        self.close(g)
        best = {"A": (0, None), "B": (0, None)}
        for d, body in g.bodies.items():
            s = g.teams[d]
            if len(body) > best[s][0]:
                best[s] = (len(body), d)
        self.longest = {s: best[s][1] for s in "AB"}
        for cell in list(self.watch):
            keep = []
            for rr, key in self.watch[cell]:
                if r - rr > LOOK:
                    self.c[key + ("then still lying",)] += 1
                else:
                    keep.append((rr, key))
            if keep:
                self.watch[cell] = keep
            else:
                del self.watch[cell]

    def close(self, g):
        cur = self.cur
        self.cur = None
        if cur is None:
            return
        key, ate, target, info = cur
        self.c[key + ("n",)] += 1
        if ate[0]:
            self.c[key + ("ate",)] += 1
        else:
            self.watch.setdefault(target, []).append((g.round, key))
            if len(self.examples) < 4000:
                self.examples.append(info + (key,))

    def turn(self, g, did):
        self.close(g)
        if not g.pearls:
            return
        body = g.bodies[did]
        s = g.teams[did]
        o = "B" if s == "A" else "A"
        b = g.board
        head = body[0]
        cands = [n for n in b.nb(head) if n is not None and n in g.pearls]
        if not cands:
            return
        occ = c_lib.occupied(g)
        cands = [n for n in cands if n not in occ]
        if not cands:
            return
        # the pearl with the most exits is the one that counts
        best = None
        for n in cands:
            ex = sum(1 for m in b.nb(n) if m is not None and m != head and m not in occ)
            if best is None or ex > best[0]:
                best = (ex, n)
        exits, target = best
        near = b.bfs(target, 2)
        enemy = mate = False
        for d2, body2 in g.bodies.items():
            if d2 == did:
                continue
            dd = near.get(body2[0])
            if dd is None:
                continue
            if g.teams[d2] == o:
                enemy = True
            elif dd <= 1:
                mate = True
        L = len(body)
        if self.region is None:
            self.region = region_sizes(b)
        P = self.region[target]
        pocket = "open region (48+ cells)" if P >= POCKET_CAP else "pocket, fits (length+1 <= cells/2)" if L + 1 <= P // 2 else "pocket, too long (length+1 > cells/2)"
        key = (s, phase(g.round), "longest" if did == self.longest[s] else "L%d" % L if L <= 4 else "L5+",
               "exits 0" if exits == 0 else "exits 1" if exits == 1 else "exits 2+",
               "enemy near" if enemy else "mate also next to it" if mate else "alone", pocket)
        self.cur = (key, [False], target, (g.round, did, L, head, target, g.pearls[target][0]))

    def eat(self, g, did, cell, origin):
        if self.cur is not None and g.current == did:
            self.cur[1][0] = True
        w = self.watch.pop(cell, None)
        if w:
            s = g.teams[did]
            for rr, key in w:
                self.c[key + ("then own team ate it" if key[0] == s else "then the enemy ate it",)] += 1

    def end(self, g, rounds, winner, result):
        self.close(g)


def work(job):
    gid, path, s = job
    z = A()
    try:
        Walk2(path).run(z)
    except Exception as e:  # noqa: BLE001
        return gid, None, repr(e), None
    out = Counter()
    for key, v in z.c.items():
        side = "own" if key[0] == s else "opp"
        out[(side,) + key[1:]] += v
    ex = [e for e in z.examples if e[-1][0] == s]
    return gid, out, None, ex


def show(total, title):
    print(title)
    print("  A turn counts when a pearl lies on a free cell next to the head. ate % = the dragon ate a pearl that turn. Of the turns it did not: what happened to the pearl within 10 rounds.")
    for side in ("own", "opp"):
        for block in ("by phase", "by length (all rounds)", "by exits of the pearl cell (all rounds)", "by company (all rounds)",
                      "by region of the pearl cell (all rounds)",
                      "by region, exits 1 or more, nobody else near, dragons 2-4 long, not the longest, rounds 0-149",
                      "by phase, exits 1 or more, nobody else near, dragons 2-4 long, not the longest",
                      "by phase, exits 1 or more, nobody else near, dragons 2-4 long, not the longest, open region only",
                      "by phase, exits 0, nobody else near, dragons 2-4 long, not the longest"):
            agg = Counter()
            for k, v in total.items():
                if k[0] != side:
                    continue
                _, ph, ln, ex, comp, pocket, what = k
                if block == "by phase":
                    lab = ph
                elif block.startswith("by length"):
                    lab = ln
                elif block.startswith("by exits"):
                    lab = ex
                elif block.startswith("by company"):
                    lab = comp
                elif block.startswith("by region of"):
                    lab = pocket
                elif block.startswith("by region, exits"):
                    if comp != "alone" or ln not in ("L2", "L3", "L4") or ex == "exits 0" or ph not in ("r0-49", "r50-149"):
                        continue
                    lab = pocket
                else:
                    if comp != "alone" or ln not in ("L2", "L3", "L4"):
                        continue
                    if ("exits 0" in block) != (ex == "exits 0"):
                        continue
                    if "open region only" in block and not pocket.startswith("open"):
                        continue
                    lab = ph
                agg[(lab, what)] += v
            labs = sorted({k[0] for k in agg})
            print(f"  {side} | {block}")
            for lab in labs:
                n, ate = agg[(lab, "n")], agg[(lab, "ate")]
                dec = max(1, n - ate)
                print(f"      {lab:38s} | {n:7d} turns | ate {100 * ate / max(1, n):3.0f}% | not eaten: {n - ate:6d} -> own team ate it later {100 * agg[(lab, 'then own team ate it')] / dec:3.0f}%, "
                      f"enemy ate it {100 * agg[(lab, 'then the enemy ate it')] / dec:3.0f}%, still lying after 10 rounds {100 * agg[(lab, 'then still lying')] / dec:3.0f}%")


if __name__ == "__main__":
    a = sys.argv[1]
    nex = int(sys.argv[sys.argv.index("--examples") + 1]) if "--examples" in sys.argv else 0
    if a in GAMES:
        info = GAMES[a]
        gid, out, err, ex = work((a, info["replay_path"], "A"))
        nm = {s: c_lib.tname(info, s) for s in "AB"}
        show(out, f"=== ADJ {a} {info['map']}: own = A = {nm['A']}, opp = B = {nm['B']}")
        for e in ex[:nex]:
            print("   declined:", e)
    else:
        team = int(a)
        size_want = sys.argv[2]
        nums = [x for x in sys.argv[3:] if x.isdigit()]
        maxg = int(nums[0]) if nums else 60
        jobs = int(nums[1]) if len(nums) > 1 else 4
        todo = []
        for g in csv.DictReader(open("games.csv")):
            if g["map"] == "Schooltime":
                continue
            size = "small" if g["map_size"].startswith("small") else "medium" if g["map_size"].startswith("medium") else "large"
            if size != size_want and size_want != g["map"]:
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
                todo.append((g["game_id"], g["replay_path"], s))
        todo = todo[:: max(1, len(todo) // maxg)][:maxg]
        total = Counter()
        with Pool(jobs) as pool:
            for gid, out, err, ex in pool.imap_unordered(work, todo):
                if err:
                    print("error", gid, err)
                    continue
                total.update(out)
        show(total, f"=== ADJ team {team}, {size_want}, {len(todo)} games{c_lib.battle_label()}: own = the team, opp = its opponents in the same games")
