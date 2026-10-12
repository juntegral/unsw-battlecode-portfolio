#!/usr/bin/env python3
"""d_expo.py: how often a queen ends a turn inside the reach of a visible enemy head, per 1,000 rounds alive, and
how often that turn is punished by a ram (sub-session A4, questions b and f).

Three situations at the start of a queen turn with an enemy head in view (reach model: d_class.py):
  A  she is outside every visible reach and a safe one-step move exists
  B  she is inside a visible reach and a safe one-step move exists
  C  no safe one-step move exists (cornered)
For each group: queen-rounds alive, turns with an enemy head in view, turns of each situation that END inside reach
(for C: all of them), the same per 1,000 queen-rounds, and the share of those turns on which she was rammed.
Reads d_out/cls through d_tab.load().
"""
from collections import Counter, defaultdict

import d_tab

GROUPS = ["meow", "meow live", "meow live rules on", "meow live rules off", "meow vs test4/WHQ", "meow live vs test4/WHQ", "opp", "forgot", "SSS",
          "Vibing++", "top three", "top three vs test4/WHQ"]


def main():
    recs = d_tab.load()
    t = defaultdict(Counter)
    for x in recs:
        gs = [g for g in x["groups"] if not g.startswith("run ")]
        if "meow live" in gs:
            gs.append("meow live rules on" if x["cells"] > 600 else "meow live rules off")
        life = x["det"]["r"] if x["kind"] != "alive" else x["rounds"]
        sd = x["sd"]
        rows = sd["enc"] + [tt for tt in sd["turns"] if tt["nvis"]]
        for g in gs:
            c = t[g]
            c["games"] += 1
            c["rounds"] += life
            c["turns"] += len(rows)
            for tt in rows:
                e = tt.get("end_reach", 0) > 0
                ram = tt["fate"] == "rammed"
                if tt["nfree"] == 0:
                    c["boxed"] += 1
                    c["boxed ram"] += ram
                    continue
                if tt["nsafe"] == 0:
                    c["C"] += 1
                    c["C ram"] += ram
                elif tt["reach0"] == 0:
                    c["A"] += 1
                    c["A in"] += e
                    c["A in ram"] += e and ram
                    c["A in adjacent"] += tt.get("end_reach", 0) == 1
                else:
                    c["B"] += 1
                    c["B in"] += e
                    c["B in ram"] += e and ram
                    c["B in ate"] += e and tt["ate"] > 0
    print("group | games | queen-rounds | turns with an enemy head in view (share of her rounds) | A turns | A ended in reach | per 1,000 rounds | rammed | "
          "B turns | per 1,000 rounds | B ended in reach again | per 1,000 rounds | of those she ate on the move | rammed | C turns (cornered) | per 1,000 rounds | rammed | "
          "all turns ending in reach per 1,000 rounds | ... by choice (A + B) | rammed on a turn that ended in reach")
    for g in GROUPS:
        c = t[g]
        k = c["rounds"] / 1000
        allin = c["A in"] + c["B in"] + c["C"]
        allram = c["A in ram"] + c["B in ram"] + c["C ram"]
        print(f"{g} | {c['games']} | {c['rounds']} | {c['turns']} ({100 * c['turns'] / c['rounds']:.1f}%) | {c['A']} | {c['A in']} ({100 * c['A in'] / max(1, c['A']):.2f}%) | {c['A in'] / k:.2f} | "
              f"{c['A in ram']} ({100 * c['A in ram'] / max(1, c['A in']):.0f}%) | {c['B']} | {c['B'] / k:.2f} | {c['B in']} ({100 * c['B in'] / max(1, c['B']):.0f}%) | {c['B in'] / k:.2f} | "
              f"{c['B in ate']} | {c['B in ram']} ({100 * c['B in ram'] / max(1, c['B in']):.0f}%) | {c['C']} | {c['C'] / k:.2f} | {c['C ram']} ({100 * c['C ram'] / max(1, c['C']):.0f}%) | "
              f"{allin / k:.2f} | {(c['A in'] + c['B in']) / k:.2f} | {allram} of {allin} ({100 * allram / max(1, allin):.0f}%)")


if __name__ == "__main__":
    main()
