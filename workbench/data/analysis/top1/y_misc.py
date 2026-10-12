#!/usr/bin/env python3
"""Small leftovers for the text. Reads y_out/w1, y_out/w2. Output: y_out/misc.txt
1. Rounds until half of our dragons name the true longest after a leader cut, with and without the cuts after
   which that never happens before the game ends (readable games).
2. Margins of our lost and won races by map class.
3. Growth of our longest from round 400 to the end, by run (medians), and the same for the other groups.
"""
import json
import os

import y_lib as Y
import y_r as R

OUTF = open(Y.out_path("misc.txt"), "w")


def pr(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUTF.write(s + "\n")


w1 = R.load_w1()
recs = R.sides(w1)
w2 = {}
for f in os.listdir(os.path.join(Y.OUT, "w2")):
    if f.endswith(".json"):
        d = json.load(open(os.path.join(Y.OUT, "w2", f)))
        w2[d["gid"]] = d
me = [r for r in recs if r["group"] == "meow"]


def readable(r):
    p = w2[r["gid"]]["ping"][r["side"]]
    return p[0] >= 500 and p[1] >= 0.95 * p[0]


waits = []
for r in me:
    if not readable(r):
        continue
    bel = {row[0]: row for row in w2[r["gid"]]["bel"]}
    for c in w2[r["gid"]]["cuts"]:
        if c["side"] != r["side"]:
            continue
        t = None
        for rr in range(c["r"] + 1, r["rounds"] + 1):
            row = bel.get(rr)
            if row is None or row[1] < 4:
                continue
            if row[4] * 2 >= row[1]:
                t = rr - c["r"]
                break
        waits.append(t)
done = sorted(x for x in waits if x is not None)
pr("1. leader cuts in readable games: %d; half name the true longest again before the end in %d: quartiles %d / %d / %d rounds; never before the end: %d" % (
    len(waits), len(done), done[len(done) // 4], done[len(done) // 2], done[(3 * len(done)) // 4], len(waits) - len(done)))

pr("2. margins (final longest, winner minus loser)")
for cls, lab in ((False, "small maps"), (True, "big maps")):
    lost = sorted(R.snap(r, "end", "L", False) - R.snap(r, "end", "L") for r in me if r["race"] and not r["won"] and r["big"] == cls)
    won = sorted(R.snap(r, "end", "L") - R.snap(r, "end", "L", False) for r in me if r["race"] and r["won"] and r["big"] == cls)
    pr("   %s: lost races %d, median margin %s, margins of 5 or less %d, 10 or less %d: %s" % (
        lab, len(lost), Y.med(lost), sum(1 for x in lost if x <= 5), sum(1 for x in lost if x <= 10), lost[:14]))
    pr("   %s: won races %d, median margin %s, margins of 3 or less %d, 5 or less %d: %s" % (
        lab, len(won), Y.med(won), sum(1 for x in won if x <= 3), sum(1 for x in won if x <= 5), won[:14]))

pr("3. growth of the longest from round 400 to the end in races (median), small / big maps")
GROUPS = [("meow live", lambda r: r["group"] == "meow" and r["build"] == "live"),
          ("meow test", lambda r: r["group"] == "meow" and r["build"] == "test"),
          ("meow earlier bot", lambda r: r["group"] == "meow" and readable(r)),
          ("opponents", lambda r: r["group"] == "opp"),
          ("forgot", lambda r: r["group"] == "forgot"), ("SSS", lambda r: r["group"] == "SSS"),
          ("Vibing++", lambda r: r["group"] == "Vibing++")]
for r in recs:
    if r["group"] != "meow":
        r["_rd"] = False
for name, pred in GROUPS:
    cells = []
    for cls in (False, True):
        rs = [r for r in recs if r["race"] and r["big"] == cls and (pred(r) if r["group"] == "meow" or "meow" not in name else False)]
        v = [R.snap(r, "end", "L") - R.snap(r, 400, "L") for r in rs]
        cells.append("%s (%d races)" % (Y.med(v), len(v)) if v else "-")
    pr("   %-18s %s" % (name, " / ".join(cells)))
for b in sorted(set(r["battle"] for r in me)):
    cells = []
    for cls in (False, True):
        v = [R.snap(r, "end", "L") - R.snap(r, 400, "L") for r in me if r["race"] and r["big"] == cls and r["battle"] == b]
        cells.append("%s (%d)" % (Y.med(v), len(v)) if v else "-")
    pr("     run %-20s %s" % (b, " / ".join(cells)))
OUTF.close()
