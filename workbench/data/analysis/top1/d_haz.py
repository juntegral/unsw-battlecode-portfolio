#!/usr/bin/env python3
"""d_haz.py: queen deaths per 1,000 queen-rounds, by kind, round band and group (sub-session A4).

Shares of games mislead when one queen lives 100 rounds and another 300: a longer life means more time to meet
every kind of death.  This table divides the deaths of each kind in a round band by the rounds queens of that group
were alive in that band.  Reads d_out/cls through d_tab.load().  Bands: 0-49, 50-99, 100-299, 300-499.
Also: the same-opponent comparison (games against test4 and WeHaveQuizzes only), and the share of queens still alive
at rounds 50 / 100 / 200 / 300 / the end.
"""
from collections import Counter, defaultdict

import d_tab

BANDS = [(0, 50), (50, 100), (100, 300), (300, 500)]
FAM = {"ram: unseen": "ram unseen", "ram: stepped in": "ram stepped/stayed in", "ram: stayed in": "ram stepped/stayed in",
       "ram: cornered": "ram cornered", "ram: model miss": "ram cornered", "boxed: terrain dead end": "boxed terrain",
       "boxed: ally body": "boxed bodies", "boxed: ally+enemy": "boxed bodies", "boxed: enemy body": "boxed bodies",
       "boxed: own body": "boxed bodies", "own ram": "own ram", "ally ram": "other", "crash: portal": "other",
       "crash: stride": "other", "crash: other": "other", "no action": "other"}
FAMS = ["ram stepped/stayed in", "ram cornered", "ram unseen", "boxed bodies", "boxed terrain", "own ram", "other"]
GROUPS = ["meow", "meow live", "meow live on", "meow live off", "meow vs test4/WHQ", "meow live vs test4/WHQ", "opp", "forgot", "SSS", "Vibing++",
          "top three", "top three vs test4/WHQ"]


def main():
    recs = d_tab.load()
    expo = defaultdict(Counter)
    dead = defaultdict(Counter)
    alive_at = defaultdict(Counter)
    n = Counter()
    for x in recs:
        gs = [g for g in x["groups"] if not g.startswith("run ")]
        if "meow live" in gs:
            gs.append("meow live on" if x["cells"] > 600 else "meow live off")
        life = x["det"]["r"] if x["kind"] != "alive" else x["rounds"]
        for grp in gs:
            n[grp] += 1
            for lo, hi in BANDS:
                expo[grp][(lo, hi)] += max(0, min(life, hi) - lo)
            for r in (50, 100, 200, 300):
                # alive at the start of round r, among games that reached round r
                if x["rounds"] > r:
                    alive_at[grp][(r, "n")] += 1
                    alive_at[grp][(r, "alive")] += life >= r if x["kind"] != "alive" else 1
            alive_at[grp][("end", "n")] += 1
            alive_at[grp][("end", "alive")] += x["kind"] == "alive"
            if x["kind"] != "alive":
                r = x["det"]["r"]
                for lo, hi in BANDS:
                    if lo <= r < hi:
                        dead[grp][(FAM[x["kind"]], (lo, hi))] += 1
                        dead[grp][("all", (lo, hi))] += 1
                dead[grp][(FAM[x["kind"]], "all")] += 1
                dead[grp][("all", "all")] += 1
    print("=== queens alive at the start of a round (of the games that reached it), and at the end")
    print("group | games | r50 | r100 | r200 | r300 | end | mean rounds alive")
    for g in GROUPS:
        a = alive_at[g]
        tot = sum(expo[g].values())
        print(f"{g} | {n[g]} | " + " | ".join(f"{100 * a[(r, 'alive')] / max(1, a[(r, 'n')]):.0f}% of {a[(r, 'n')]}" for r in (50, 100, 200, 300, "end")) + f" | {tot / max(1, n[g]):.0f}")
    print("\n=== deaths per 1,000 queen-rounds, whole game (deaths / queen-rounds in thousands)")
    print("group | queen-rounds | all | " + " | ".join(FAMS))
    for g in GROUPS:
        tot = sum(expo[g].values())
        print(f"{g} | {tot} | {1000 * dead[g][('all', 'all')] / max(1, tot):.2f} | " + " | ".join(f"{1000 * dead[g][(f, 'all')] / max(1, tot):.2f} ({dead[g][(f, 'all')]})" for f in FAMS))
    for lo, hi in BANDS:
        print(f"\n=== deaths per 1,000 queen-rounds, rounds {lo}-{hi - 1}")
        print("group | queen-rounds | all | " + " | ".join(FAMS))
        for g in GROUPS:
            e = expo[g][(lo, hi)]
            print(f"{g} | {e} | {1000 * dead[g][('all', (lo, hi))] / max(1, e):.2f} | " + " | ".join(f"{1000 * dead[g][(f, (lo, hi))] / max(1, e):.2f} ({dead[g][(f, (lo, hi))]})" for f in FAMS))


if __name__ == "__main__":
    main()
