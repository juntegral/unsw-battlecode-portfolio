#!/usr/bin/env python3
"""d_after.py: what happens after the SAFE choice in the same situations (sub-session A4, questions g and h).

The reach veto of section 7 would turn "ended in reach although a safe step existed" into "took the safe step".
What is a safe step worth?  For every queen turn in one of two close situations in which she DID end outside reach:
  B  she began the turn inside a visible enemy's reach and a safe one-step move existed
  A4 she began outside reach with a visible small enemy head (4 or shorter) within 4 path steps, a safe step existed
this prints how often she was rammed in that same round, within the next 3 rounds and within the next 10 rounds,
and how often she died another way within 10 rounds; next to the same figures for the turns on which she ended
in reach.  Reads d_out/cls through d_tab.load().
"""
from collections import Counter, defaultdict

import d_tab

GROUPS = ["meow", "meow live", "meow vs test4/WHQ", "opp", "forgot", "SSS", "Vibing++", "top three", "top three vs test4/WHQ"]


def main():
    recs = d_tab.load()
    t = defaultdict(Counter)
    for x in recs:
        gs = [g for g in x["groups"] if not g.startswith("run ")]
        sd = x["sd"]
        rows = sd["enc"] + [tt for tt in sd["turns"] if tt["nvis"]]
        dr = x["det"]["r"] if x["kind"] != "alive" else None
        ram = x["kind"].startswith("ram")
        for tt in rows:
            if tt["nfree"] == 0 or tt["nsafe"] == 0:
                continue
            if tt["reach0"] > 0:
                sit = "B"
            elif tt["nvis_small"] > 0 and 0 < tt["d0_small"] <= 4:
                sit = "A4"
            else:
                continue
            took = "in" if tt.get("end_reach", 0) > 0 else "safe"
            r = tt["r"]
            for g in gs:
                c = t[(g, sit, took)]
                c["n"] += 1
                if dr is not None:
                    gap = dr - r
                    if ram:
                        c["ram0"] += gap <= 0 or (gap == 1 and tt["fate"] == "rammed")
                        c["ram3"] += gap <= 3
                        c["ram10"] += gap <= 10
                    else:
                        c["other10"] += gap <= 10
    print("group | situation | she ended | turns | rammed that round | rammed within 3 rounds | rammed within 10 rounds | dead another way within 10 rounds")
    for g in GROUPS:
        for sit in ("B", "A4"):
            for took in ("safe", "in"):
                c = t[(g, sit, took)]
                if not c["n"]:
                    continue
                n = c["n"]
                print(f"{g} | {sit} | {'outside reach' if took == 'safe' else 'in reach'} | {n} | {c['ram0']} ({100 * c['ram0'] / n:.1f}%) | {c['ram3']} ({100 * c['ram3'] / n:.1f}%) | "
                      f"{c['ram10']} ({100 * c['ram10'] / n:.1f}%) | {c['other10']} ({100 * c['other10'] / n:.1f}%)")


if __name__ == "__main__":
    main()
