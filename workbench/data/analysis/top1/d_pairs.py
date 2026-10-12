#!/usr/bin/env python3
"""d_pairs.py: the smoke-test pairs as natural experiments on our queen (sub-session A4, question e).

1. Old against new.  For each candidate that has a paired "-old" run (stride, passage2, qh31 against test4 and
   WeHaveQuizzes; tc30-dev1b-new against tc30-dev1-old on "dev test 1"), games are paired by (opponent, map).
   Printed: kinds of queen end in old and new, her death round (median, and in how many pairs new died earlier /
   later / same), wins.
2. The qn23 "queen no trap" candidate (45 games in ../../online/smoke/qn23-test-new, not in games.csv; walked by
   d_extra.py into d_out/cls_extra/).  Its queen ends by kind next to the live bot's games against the same three
   opponents (test4, WeHaveQuizzes, dev test 1) in the "-old" runs and ladder downloads.
Kinds: d_tab.classify().
"""
import glob
import json
import os
import statistics
from collections import Counter, defaultdict

import d_tab

HERE = os.path.dirname(os.path.abspath(__file__))
PAIRS = [("stride-old", "stride-new"), ("passage2-test-old", "passage2-test-new"), ("qh31-test-old", "qh31-test-new"),
         ("tc30-dev1-old", "tc30-dev1b-new")]
SHORT = {"ram: stepped in": "stepped in", "ram: stayed in": "stayed in", "ram: cornered": "cornered", "ram: unseen": "unseen",
         "ram: model miss": "cornered", "boxed: terrain dead end": "terrain", "boxed: ally body": "boxed by own", "boxed: ally+enemy": "boxed by enemy",
         "boxed: enemy body": "boxed by enemy", "boxed: own body": "boxed by own", "own ram": "own ram", "alive": "alive"}
ORDER = ["alive", "stepped in", "stayed in", "cornered", "unseen", "boxed by own", "boxed by enemy", "terrain", "own ram", "other"]


def main():
    recs = [x for x in d_tab.load() if "meow" in x["groups"]]
    by_run = defaultdict(dict)
    for x in recs:
        by_run[x["run"]][(x["opp"], x["map"])] = x
    print("=== 1. old against new, paired by opponent and map")
    for old, new in PAIRS:
        keys = sorted(set(by_run[old]) & set(by_run[new]))
        ko, kn = Counter(), Counter()
        earlier = later = same = 0
        ro, rn = [], []
        wo = wn = 0
        changes = Counter()
        for k in keys:
            a, b = by_run[old][k], by_run[new][k]
            ka, kb = SHORT.get(a["kind"], "other"), SHORT.get(b["kind"], "other")
            ko[ka] += 1
            kn[kb] += 1
            da = a["det"]["r"] if a["kind"] != "alive" else 999
            db = b["det"]["r"] if b["kind"] != "alive" else 999
            ro.append(da)
            rn.append(db)
            earlier += db < da
            later += db > da
            same += db == da
            wo += a["won"]
            wn += b["won"]
            if ka != kb:
                changes[(ka, kb)] += 1
        print(f"--- {old} against {new}: {len(keys)} pairs; wins old {wo}, new {wn}; queen death round median old {statistics.median(ro):.0f}, new {statistics.median(rn):.0f} "
              f"(alive counted as 999); new queen died earlier in {earlier} pairs, later in {later}, same round in {same}")
        print("    kind | old | new")
        for k in ORDER:
            if ko[k] or kn[k]:
                print(f"    {k} | {ko[k]} | {kn[k]}")
        print("    dead before round 100: old", sum(r < 100 for r in ro), "new", sum(r < 100 for r in rn), "| before round 300: old", sum(r < 300 for r in ro), "new", sum(r < 300 for r in rn))
    # ---- qn23
    print("\n=== 2. the qn23 'queen no trap' candidate (45 games, not in games.csv) against the live bot against the same opponents")
    live = [x for x in recs if "meow live" in x["groups"] and x["g"]["team" + ("B" if x["side"] == "A" else "A") + "Id"] in ("19", "87", "545")]
    new = []
    for f in sorted(glob.glob(os.path.join(HERE, "d_out", "cls_extra", "qn23-test-new", "*.json"))):
        d = json.load(open(f))
        for s in "AB":
            if d["sides"][s]["team"] == 1119:
                kind, det = d_tab.classify(d["sides"][s])
                o = "B" if s == "A" else "A"
                new.append(dict(kind=kind, det=det, map=d["map"], cells=d["cells"], won=d["winner"] == s, rounds=d["rounds"], opp=d["names"][o],
                                gid=d["game_id"], sd=d["sides"][s]))
    print(f"live bot: {len(live)} games; qn23: {len(new)} games")
    print("kind | live bot | qn23")
    cl = Counter(SHORT.get(x["kind"], "other") for x in live)
    cn = Counter(SHORT.get(x["kind"], "other") for x in new)
    for k in ORDER:
        print(f"{k} | {cl[k]} ({100 * cl[k] / len(live):.0f}%) | {cn[k]} ({100 * cn[k] / len(new):.0f}%)")
    for name, xs in (("live bot", live), ("qn23", new)):
        life = sum((x["det"]["r"] if x["kind"] != "alive" else x["rounds"]) for x in xs)
        dead = sum(x["kind"] != "alive" for x in xs)
        box = sum(x["kind"].startswith("boxed") for x in xs)
        print(f"{name}: wins {sum(x['won'] for x in xs)} of {len(xs)}; deaths per 1,000 queen-rounds {1000 * dead / life:.2f}; boxed-in deaths per 1,000 queen-rounds {1000 * box / life:.2f}; "
              f"dead before round 100: {sum(x['kind'] != 'alive' and x['det']['r'] < 100 for x in xs)}")
    print("qn23 boxed-in and early deaths (game, map, opponent, round, kind, sides):")
    for x in sorted(new, key=lambda x: (x["kind"], x["map"])):
        if x["kind"].startswith("boxed") or (x["kind"] != "alive" and x["det"]["r"] < 30):
            T = x["det"]["T"]
            print(f"   {x['gid']} {x['map']} vs {x['opp'][:8]} r{x['det']['r']} {x['kind']} L{x['det']['len']} sides {''.join(s[0] for s in T['sides'])} "
                  f"splits in her last turns {[t['split'] for t in x['sd']['turns'] if 'split' in t]}")


if __name__ == "__main__":
    main()
