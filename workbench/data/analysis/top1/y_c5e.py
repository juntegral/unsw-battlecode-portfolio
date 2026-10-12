#!/usr/bin/env python3
"""Candidate 5: the naming curve after a cut on a larger sample, and fast against slow naming.
Reads y_out/w1, y_out/w2 (readable games of ours only). Output: y_out/c5e.txt

Uses every leader cut of ours from round 300 in a readable game, also those after which the heir cut again:
each cut is followed until the heir cuts again, dies, the game ends, or 30 rounds have passed.
"""
import json
import math
import os
from collections import defaultdict

import y_lib as Y
import y_r as R

OUTF = open(Y.out_path("c5e.txt"), "w")


def pr(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUTF.write(s + "\n")


w1 = R.load_w1()
recs = [r for r in R.sides(w1) if r["group"] == "meow"]
w2 = {}
for f in os.listdir(os.path.join(Y.OUT, "w2")):
    if f.endswith(".json"):
        d = json.load(open(os.path.join(Y.OUT, "w2", f)))
        w2[d["gid"]] = d


def readable(r):
    p = w2[r["gid"]]["ping"][r["side"]]
    return p[0] >= 500 and p[1] >= 0.95 * p[0]


rd = [r for r in recs if readable(r)]


def cuts(r, lo, hi=499, min_cohort=4):
    return [c for c in w2[r["gid"]]["cuts"] if c["side"] == r["side"] and lo <= c["r"] <= hi and len(c["cohort"]) >= min_cohort]


for lo, lab in ((300, "cuts from round 300"), (395, "cuts from round 395")):
    for cls, clab in ((None, "all maps"), (False, "small maps"), (True, "big maps")):
        cs = [c for r in rd if cls is None or r["big"] == cls for c in cuts(r, lo)]
        pr("\n== %s, readable games, %s: %d cuts (cohort of 4+)" % (lab, clab, len(cs)))
        pr("   round after the cut | cuts still followed | cohort alive a cut | naming the heir | the stub | another living id | a dead id | nothing")
        for t in (1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 18, 20, 22, 24, 25):
            a = [0] * 5
            n = alive = 0
            for c in cs:
                if len(c["track"]) < t:
                    continue
                tr = c["track"][t - 1]
                n += 1
                alive += tr[3]
                for i in range(5):
                    a[i] += tr[6 + i]
            tot = sum(a) or 1
            if n < 5:
                continue
            pr("   %2d | %3d | %4.1f | %3.0f%% | %3.0f%% | %3.0f%% | %3.0f%% | %3.0f%%" % (
                t, n, alive / n, 100 * a[0] / tot, 100 * a[1] / tot, 100 * a[2] / tot, 100 * a[3] / tot, 100 * a[4] / tot))

pr("\n== When half of the living cohort first names the heir (readable games, cuts from 300, cohort 4+; 'never' = not while the cut was followed)")
rows = []
for r in rd:
    for c in cuts(r, 300):
        t_half = None
        for t in range(1, len(c["track"]) + 1):
            tr = c["track"][t - 1]
            tot = sum(tr[6:11])
            if tot >= 3 and tr[6] * 2 >= tot:
                t_half = t
                break
        followed = len(c["track"])
        rows.append((t_half, followed, c, r))
n = len(rows)
pr("   cuts %d | half name the heir within 5 rounds: %d, 6-10: %d, 11-15: %d, 16-20: %d, 21-25: %d, 26-30: %d | never while followed: %d (of which followed under 10 rounds: %d, 10-24: %d, 25+: %d)" % (
    n, sum(1 for x in rows if x[0] and x[0] <= 5), sum(1 for x in rows if x[0] and 6 <= x[0] <= 10),
    sum(1 for x in rows if x[0] and 11 <= x[0] <= 15), sum(1 for x in rows if x[0] and 16 <= x[0] <= 20),
    sum(1 for x in rows if x[0] and 21 <= x[0] <= 25), sum(1 for x in rows if x[0] and x[0] >= 26),
    sum(1 for x in rows if not x[0]), sum(1 for x in rows if not x[0] and x[1] < 10),
    sum(1 for x in rows if not x[0] and 10 <= x[1] < 25), sum(1 for x in rows if not x[0] and x[1] >= 25)))

pr("\n== Fast against slow (cuts from round 395 followed for at least 15 rounds): heir's growth over the first 15 rounds by what the cohort named at rounds 5-10")
fast, slow = [], []
by = defaultdict(lambda: [[], []])
for r in rd:
    for c in cuts(r, 395):
        if len(c["track"]) < 15:
            continue
        h = tot = 0
        for t in range(5, 11):
            tr = c["track"][t - 1]
            h += tr[6]
            tot += sum(tr[6:11])
        if tot < 6:
            continue
        share = h / tot
        g15 = c["track"][14][0] - c["gets"]
        nH = sum(1 for m in c["cohort"] if m[4] == "H" and m[5] is not None and m[5] <= 15)
        (fast if share >= 0.25 else slow).append((g15, nH, len(c["cohort"]), share))
        by[r["gid"]][0 if share >= 0.25 else 1].append(g15)
for lab, grp in (("a quarter or more of the cohort names the heir at rounds 5-10", fast), ("fewer", slow)):
    if grp:
        pr("   %-62s cuts %3d | heir's growth in 15 rounds %+.1f | died next to the heir within 15 rounds %.2f a cut | cohort %.1f" % (
            lab, len(grp), Y.mean([x[0] for x in grp]), Y.mean([x[1] for x in grp]), Y.mean([x[2] for x in grp])))
d = [Y.mean(v[0]) - Y.mean(v[1]) for v in by.values() if v[0] and v[1]]
if d:
    m = Y.mean(d)
    sd = (sum((x - m) ** 2 for x in d) / max(1, len(d) - 1)) ** 0.5
    pr("   inside the same game: %+.1f segments in 15 rounds (se %.1f, %d games)" % (m, sd / math.sqrt(len(d)), len(d)))

pr("\n== The same question on ALL our games (no pings needed): after a leader cut from round 395 followed for 15+ rounds, the heir's growth in 15 rounds")
pr("   by how far the cohort stood from the heir's head at the cut (mean cells): the geometry any bot has to deal with")
allr = [r for r in recs]
buck = defaultdict(list)
for r in allr:
    if not r["race"]:
        continue
    for c in w2[r["gid"]]["cuts"]:
        if c["side"] != r["side"] or c["r"] < 395 or len(c["track"]) < 15 or len(c["cohort"]) < 4:
            continue
        dh = Y.mean([m[2] for m in c["cohort"]])
        g15 = c["track"][14][0] - c["gets"]
        k = 0 if dh < 8 else (1 if dh < 12 else (2 if dh < 16 else 3))
        buck[k].append((g15, c["gets"], dh))
for k, lab in ((0, "under 8 cells"), (1, "8-11"), (2, "12-15"), (3, "16 or more")):
    v = buck.get(k, [])
    if v:
        pr("   cohort %-14s cuts %3d | heir length at the cut %.1f | growth in 15 rounds %+.1f" % (lab, len(v), Y.mean([x[1] for x in v]), Y.mean([x[0] for x in v])))
OUTF.close()
