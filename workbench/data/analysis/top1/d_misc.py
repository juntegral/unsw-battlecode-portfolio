#!/usr/bin/env python3
"""d_misc.py: three small counts for the report (sub-session A4).

1. Own rams (she moved her head into a head): did she have a free cell, what was the head she ran into (enemy or
   team-mate, its length), rules on or off.
2. Queens that died 6 or longer ("fed" or grown queens): by kind, with the length lost, the multi-step move of her
   last turn, and what the game became.  For meow, opp and the top three.
3. Queen splits with an enemy head in view (from the stored last turns only: splits in her last 13 turns before a
   death), and how many of the rammed queens had split within their last 3 turns.
Reads d_out/cls through d_tab.load().
"""
from collections import Counter, defaultdict

import d_tab


def main():
    recs = d_tab.load()
    print("=== 1. own rams")
    for grp in ("meow", "meow live", "opp", "forgot", "SSS", "Vibing++"):
        xs = [x for x in recs if grp in x["groups"] and x["kind"] == "own ram"]
        c = Counter()
        for x in xs:
            T = x["det"]["T"]
            hit = x["det"]["hit"]
            c["n"] += 1
            c["boxed (no free cell): the head was her only non-kelp side" if T["nfree"] == 0 else "had a free cell"] += 1
            c["had a free cell that was safe"] += T["nfree"] > 0 and T["nsafe"] > 0
            c["hit an enemy head" if hit[0] == "E" else "hit a team-mate's head"] += 1
            c["the other head was 2-3 long"] += hit[0] in "EA" and len(hit) > 2 and hit[2] <= 3
            c["rules off (600 cells or fewer)"] += x["cells"] <= 600
        print(f"  {grp}: {dict(c)}")
    print("\n=== 2. queens that died 6 or longer")
    for grp in ("meow", "meow live", "opp", "forgot", "SSS", "Vibing++"):
        xs = [x for x in recs if grp in x["groups"] and x["kind"] != "alive" and x["det"]["len"] >= 6]
        cut = [x for x in recs if grp in x["groups"] and x["kind"].startswith("boxed") and any("split" in t and t["split"][0] >= 6 and t["split"][1] <= 3 for t in x["sd"]["turns"])]
        c = Counter(x["kind"] for x in xs)
        oc = Counter(d_tab.outcome(x) for x in xs)
        stride = sum(1 for x in xs if x["kind"].startswith("ram") and len(x["det"]["T"]["dirs"]) >= 3)
        print(f"  {grp}: {len(xs)} deaths at 6+ ({dict(c)}); her last move had 3+ steps in {stride} of the rams; games became {dict(oc)}; "
              f"plus {len(cut)} queens that cut themselves from 6+ to 2-3 and died boxed in")
        if grp == "meow":
            for x in sorted(xs + cut, key=lambda x: x["det"]["r"]):
                T = x["det"]["T"]
                k = x["det"].get("k")
                cutinfo = [t["split"][:3] for t in x["sd"]["turns"] if "split" in t and t["split"][0] >= 6]
                print(f"     {x['gid']} {x['map'][:14]:14s} {x['run'][:16]:16s} r{x['det']['r']:3d} L{x['det']['len']:2d} {x['kind']:22s} last move {T['dirs'] or 'split'} "
                      + (f"killer L{k['len']} {k['steps']}st " if k else "") + f"cuts {cutinfo} | {d_tab.outcome(x)} | enemy queen final {x['g']['final_queen_length_' + ('B' if x['side'] == 'A' else 'A')]}")
    print("\n=== 3. splits just before a ram")
    for grp in ("meow", "meow live", "opp", "forgot", "SSS", "Vibing++"):
        xs = [x for x in recs if grp in x["groups"] and x["kind"].startswith("ram")]
        s3 = sum(1 for x in xs if any("split" in t for t in x["sd"]["turns"][-3:]))
        s3v = sum(1 for x in xs if any("split" in t and t["nvis"] > 0 for t in x["sd"]["turns"][-3:]))
        s1 = sum(1 for x in xs if "split" in x["sd"]["turns"][-1])
        print(f"  {grp}: rammed queens {len(xs)}; split within her last 3 turns {s3} ({100 * s3 // max(1, len(xs))}%), of those with an enemy head in view at the split {s3v}; split on her very last turn {s1}")


if __name__ == "__main__":
    main()
