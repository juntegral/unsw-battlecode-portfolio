#!/usr/bin/env python3
"""b_cand.py <cand file> [...]: tabulate a candidate list (cand91.txt, cand264.txt, cand306.txt) (sub-session A2).

Each line: size | map | game_id | side | W/L | end type | opponent | opp elo | final own ... | opp ... | ownQ ... | oppQ ... | rounds
Prints per map: games, wins, own queen dead by round 60 / 100 / 200, own queen alive at the end, and the win rate
split by "own queen dead by round 100" and by which queen was dead at the end. Then the same summed by map size, and
the losses split by end type and queen state.
"""
import re
import sys
from collections import Counter, defaultdict


def parse(path):
    rows = []
    for line in open(path):
        p = [x.strip() for x in line.rstrip("\n").split("|")]
        if len(p) < 13:
            continue
        own = p[10]
        opp = p[11]

        def death(s):
            if "alive" in s:
                return None
            m = re.search(r" r(\d+) ", s + " ")
            return int(m.group(1)) if m else -1

        def how(s):
            if "alive" in s:
                return "alive"
            m = re.search(r"r\d+ (\w+)", s)
            return m.group(1) if m else "?"

        fo = re.search(r"own (\d+)u/(\d+)t/(\d+)L/q(\d+)", p[8])
        fp = re.search(r"opp (\d+)u/(\d+)t/(\d+)L/q(\d+)", p[9])
        rows.append(dict(size=p[0], map=p[1], gid=p[2], side=p[3], win=p[4] == "W", end=p[5], opp=p[6],
                         od=death(own), ed=death(opp), ohow=how(own), ehow=how(opp), rounds=int(p[12]),
                         own=tuple(map(int, fo.groups())) if fo else None, oppf=tuple(map(int, fp.groups())) if fp else None))
    return rows


def pct(a, b):
    return f"{a}/{b}" + (f" ({100 * a // b}%)" if b else "")


for path in sys.argv[1:]:
    rows = [r for r in parse(path) if r["map"] != "Schooltime"]
    print(f"=== {path}: {len(rows)} games without Schooltime, {sum(r['win'] for r in rows)} wins")
    bymap = defaultdict(list)
    for r in rows:
        bymap[(r["size"], r["map"])].append(r)
    print("  size | map | games | wins | own queen dead by r60 | by r100 | by r200 | alive at end | wins when own queen dead by r100 | wins otherwise | enemy queen dead by r100")
    for k in sorted(bymap):
        v = bymap[k]
        d60 = [r for r in v if r["od"] is not None and r["od"] <= 60]
        d100 = [r for r in v if r["od"] is not None and r["od"] <= 100]
        d200 = [r for r in v if r["od"] is not None and r["od"] <= 200]
        al = [r for r in v if r["od"] is None]
        rest = [r for r in v if r not in d100]
        e100 = [r for r in v if r["ed"] is not None and r["ed"] <= 100]
        print(f"  {k[0]:6s} | {k[1]:17s} | {len(v):3d} | {pct(sum(r['win'] for r in v), len(v)):13s} | {len(d60):3d} | {len(d100):3d} | {len(d200):3d} | {len(al):3d} | "
              f"{pct(sum(r['win'] for r in d100), len(d100)):13s} | {pct(sum(r['win'] for r in rest), len(rest)):13s} | {len(e100)}")
    for size in ("large", "medium", "small"):
        v = [r for r in rows if r["size"] == size]
        d100 = [r for r in v if r["od"] is not None and r["od"] <= 100]
        rest = [r for r in v if r not in d100]
        print(f"  {size}: {len(v)} games, wins {pct(sum(r['win'] for r in v), len(v))}; own queen dead by r100 in {len(d100)}: wins {pct(sum(r['win'] for r in d100), len(d100))}; otherwise wins {pct(sum(r['win'] for r in rest), len(rest))}")
    losses = [r for r in rows if not r["win"]]
    c = Counter()
    for r in losses:
        st = ("own queen " + ("alive" if r["od"] is None else "dead")) + ", enemy queen " + ("alive" if r["ed"] is None else "dead")
        c[(r["end"], st)] += 1
    print(f"  losses: {len(losses)}: " + "; ".join(f"{k[0]} with {k[1]}: {n}" for k, n in c.most_common()))
    # losses on 'longest' with more total length than the opponent
    lg = [r for r in losses if r["end"] == "longest" and r["own"] and r["oppf"]]
    more = [r for r in lg if r["own"][1] > r["oppf"][1]]
    print(f"  losses on the longest dragon: {len(lg)}; of those with the larger total length: {len(more)}; with more units: {sum(1 for r in lg if r['own'][0] > r['oppf'][0])}")
    wl = [r for r in rows if r["win"] and r["end"] == "longest" and r["own"] and r["oppf"]]
    print(f"  wins on the longest dragon: {len(wl)}; of those with the smaller total length: {sum(1 for r in wl if r['own'][1] < r['oppf'][1])}")
    oh = Counter(r["ohow"] for r in rows)
    print("  how the own queen ended:", dict(oh.most_common()))
    # queen-rule losses with both alive: by how much
    ba = [r for r in rows if r["end"] == "queen rule" and r["od"] is None and r["ed"] is None and r["own"] and r["oppf"]]
    print(f"  round-500 games with both queens alive: {len(ba)}, won {sum(r['win'] for r in ba)}; mean own queen {sum(r['own'][3] for r in ba) / max(1, len(ba)):.1f} vs enemy queen {sum(r['oppf'][3] for r in ba) / max(1, len(ba)):.1f}")
