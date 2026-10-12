#!/usr/bin/env python3
"""d_open.py: queen deaths before round 50, by map and kind, with the repeating patterns (sub-session A4, question d).

For meow (all runs and live bot), the opponent's queen in our games, and the top three: deaths before round 50 by
map and kind (d_tab.classify), and for meow every group of 3 or more deaths on one map with the same kind and
within 3 cells and 4 rounds of each other ("pattern"), with the queen's orders in her last turns for one of them.
"""
from collections import Counter, defaultdict

import d_tab

SHORT = {"ram: stepped in": "stepped in", "ram: stayed in": "stayed in", "ram: cornered": "cornered", "ram: unseen": "unseen",
         "ram: model miss": "cornered", "boxed: terrain dead end": "terrain", "boxed: ally body": "boxed by own", "boxed: ally+enemy": "boxed by enemy",
         "boxed: enemy body": "boxed by enemy", "boxed: own body": "boxed by own", "own ram": "own ram"}


def main():
    recs = d_tab.load()
    for grp in ("meow", "meow live", "opp", "top three"):
        xs = [x for x in recs if grp in x["groups"]]
        early = [x for x in xs if x["kind"] != "alive" and x["det"]["r"] < 50]
        print(f"\n=== {grp}: {len(early)} queen deaths before round 50 in {len(xs)} games ({100 * len(early) / len(xs):.0f}%)")
        maps = sorted({x["map"] for x in xs}, key=lambda m: min(y["cells"] for y in xs if y["map"] == m))
        kinds = ["stepped in", "stayed in", "cornered", "unseen", "boxed by own", "boxed by enemy", "terrain", "own ram", "other"]
        print("map (cells) | games | dead before r50 | " + " | ".join(kinds))
        tot = Counter()
        for m in maps:
            g = [x for x in xs if x["map"] == m]
            e = [x for x in early if x["map"] == m]
            c = Counter(SHORT.get(x["kind"], "other") for x in e)
            tot.update(c)
            print(f"{m} ({g[0]['cells']}) | {len(g)} | {len(e)} | " + " | ".join(str(c[k]) for k in kinds))
        print(f"all | {len(xs)} | {len(early)} | " + " | ".join(str(tot[k]) for k in kinds))
        if grp == "meow":
            print("\npatterns (3 or more deaths on one map, same kind, within 3 cells and 4 rounds):")
            used = set()
            for x in sorted(early, key=lambda x: (x["map"], x["kind"], x["det"]["r"])):
                if x["gid"] in used:
                    continue
                p = x["sd"]["death"]["pos"]
                grpx = [y for y in early if y["map"] == x["map"] and y["kind"] == x["kind"] and abs(y["det"]["r"] - x["det"]["r"]) <= 4
                        and abs(y["sd"]["death"]["pos"][0] - p[0]) <= 3 and abs(y["sd"]["death"]["pos"][1] - p[1]) <= 3 and y["gid"] not in used]
                if len(grpx) >= 3:
                    for y in grpx:
                        used.add(y["gid"])
                    runs = Counter("live" if "meow live" in y["groups"] else "candidate" for y in grpx)
                    lens = Counter(y["det"]["len"] for y in grpx)
                    res = Counter(d_tab.outcome(y) for y in grpx)
                    print(f"  {x['map']} {x['kind']}: {len(grpx)} games, rounds {min(y['det']['r'] for y in grpx)}-{max(y['det']['r'] for y in grpx)}, around {p}, her length {dict(lens)}, runs {dict(runs)}, results {dict(res)}")
                    print("     games:", " ".join(y["gid"] for y in grpx))
                    t = x["sd"]["turns"]
                    print("     last turns of", x["gid"], ":", " | ".join(f"r{tt['r']} L{tt['len']} {tuple(tt['head'])} {'move ' + tt['dirs'] if tt['kind'] == 0 else 'SPLIT'}{' +' + str(tt['ate']) if tt['ate'] else ''}" for tt in t[-8:]))
            rest = [x for x in early if x["gid"] not in used]
            print(f"  not in a pattern: {len(rest)} deaths: " + ", ".join(f"{k} {v}" for k, v in Counter(SHORT.get(x['kind'], 'other') for x in rest).most_common()))
            print("     by map:", dict(Counter(x["map"] for x in rest).most_common()))


if __name__ == "__main__":
    main()
