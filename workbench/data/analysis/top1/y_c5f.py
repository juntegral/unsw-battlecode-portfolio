#!/usr/bin/env python3
"""Candidate 5: does the earlier bot (the 82 games with readable pings) behave like today's builds after a cut?
The belief numbers come from the earlier bot only. Here the two position-only measures (the clock after a cut and
the 25-round windows) are split into readable games / sealed live-bot games / test builds.
Reads y_out/w1, y_out/w2. Output: y_out/c5f.txt
"""
import json
import os
from collections import defaultdict

import y_lib as Y
import y_r as R

OUTF = open(Y.out_path("c5f.txt"), "w")


def pr(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUTF.write(s + "\n")


w1 = R.load_w1()
recs = [r for r in R.sides(w1) if r["group"] == "meow" and r["race"]]
ping = {}
for f in os.listdir(os.path.join(Y.OUT, "w2")):
    if f.endswith(".json"):
        d = json.load(open(os.path.join(Y.OUT, "w2", f)))
        ping[d["gid"]] = d["ping"]


def readable(r):
    p = ping[r["gid"]][r["side"]]
    return p[0] >= 500 and p[1] >= 0.95 * p[0]


def leader_cuts(rec, lo=0, hi=999):
    out = []
    for row in rec["w"]["lsplit"]:
        r, parent, child, before, plen, clen, side, fr, mx, seq = row
        if side == rec["side"] and before >= 8 and plen <= 3 and before >= mx and lo <= r <= hi:
            out.append(row)
    return out


def choice_deaths(rec, lo, hi):
    out = []
    for d in rec["w"]["deaths"]:
        if d[2] == rec["side"] and lo <= d[0] <= hi and d[3] != "headon" and d[8] >= 1:
            out.append(d)
    return out


TB = [(0, 4), (5, 9), (10, 14), (15, 19), (20, 24), (25, 29), (30, 39), (40, 59), (60, 999)]


def clock(rs, lo=400, hi=499):
    expo = defaultdict(int)
    hit = defaultdict(int)
    stub = defaultdict(int)
    for r in rs:
        cuts = sorted(c[0] for c in leader_cuts(r, 250, 499))
        stubs = defaultdict(list)
        for row in r["w"]["lsplit"]:
            if row[6] == r["side"] and row[4] <= 3:
                stubs[row[1]].append(row[0])

        def since(t):
            last = None
            for c in cuts:
                if c <= t:
                    last = c
                else:
                    break
            return None if last is None else t - last
        for t in range(lo, hi + 1):
            u = R.snap(r, t - t % 25, "units")
            if u is None or u < 11:
                continue
            s = since(t)
            expo["none" if s is None else s] += 1
        for d in choice_deaths(r, lo, hi):
            u = R.snap(r, d[0] - d[0] % 25, "units")
            if u is None or u < 11:
                continue
            s = since(d[0])
            k = "none" if s is None else s
            if 0 <= d[11] <= 3 and d[10] >= 2 * d[4]:
                hit[k] += 1
            elif any(n[2] <= 3 and any(0 <= d[0] - x <= 26 for x in stubs.get(n[0], [])) for n in d[12]):
                stub[k] += 1
    return expo, hit, stub


def row(name, rs):
    expo, hit, stub = clock(rs)
    cells = []
    for lo, hi in TB:
        e = sum(v for k, v in expo.items() if k != "none" and lo <= k <= hi)
        h = sum(v for k, v in hit.items() if k != "none" and lo <= k <= hi)
        s = sum(v for k, v in stub.items() if k != "none" and lo <= k <= hi)
        cells.append("%5.1f/%4.1f" % (100.0 * h / e, 100.0 * s / e) if e >= 40 else "    -     ")
    e = expo.get("none", 0)
    cells.append("%5.1f" % (100.0 * hit.get("none", 0) / e) if e >= 40 else "  -")
    pr("   %-34s %3d races | %s" % (name, len(rs), " ".join(cells)))


pr("== 1. The clock after a cut, rounds 400-499 of our races: deaths by choice within 3 steps of the side's longest / of a fresh stub, per 100 side-rounds")
pr("   %-34s           | %s | no cut yet" % ("rounds since the last leader cut", " ".join("%10s" % ("%d-%d" % b if b[1] < 999 else "60+") for b in TB)))
SETS = [("readable (earlier bot)", lambda r: readable(r)),
        ("sealed, live bot", lambda r: not readable(r) and r["build"] == "live"),
        ("sealed, test builds", lambda r: not readable(r) and r["build"] == "test"),
        ("readable, small maps", lambda r: readable(r) and not r["big"]),
        ("sealed live, small maps", lambda r: not readable(r) and r["build"] == "live" and not r["big"]),
        ("sealed test, small maps", lambda r: not readable(r) and r["build"] == "test" and not r["big"]),
        ("readable, big maps", lambda r: readable(r) and r["big"]),
        ("sealed live, big maps", lambda r: not readable(r) and r["build"] == "live" and r["big"]),
        ("sealed test, big maps", lambda r: not readable(r) and r["build"] == "test" and r["big"])]
for name, pred in SETS:
    row(name, [r for r in recs if pred(r)])

pr("\n== 2. Growth of the longest per 25-round window from round 400 (10+ other own dragons): cut inside / cut only in the 25 rounds before / none in 50 rounds")
WIN = (400, 425, 450, 475)
for name, pred in SETS:
    a, b, c = [], [], []
    for r in recs:
        if not pred(r):
            continue
        cuts = leader_cuts(r, 300, 499)
        for t in WIN:
            u = R.snap(r, t, "units")
            if u is None or u < 11:
                continue
            L0 = R.snap(r, t, "L")
            L1 = R.snap(r, t + 25 if t + 25 < 500 else "end", "L")
            n_in = sum(1 for x in cuts if t <= x[0] < t + 25)
            n_bef = sum(1 for x in cuts if t - 25 <= x[0] < t)
            (a if n_in else (b if n_bef else c)).append(L1 - L0)

    def f(x):
        return "%.1f (%d)" % (Y.mean(x), len(x)) if x else "-"
    pr("   %-34s inside %-11s before-only %-11s none %-11s" % (name, f(a), f(b), f(c)))

pr("\n== 3. Races and results of the three sets; leader cuts per race from round 395; share of feeder deaths (no order) per race")
for name, pred in SETS[:3]:
    rs = [r for r in recs if pred(r)]
    pr("   %-34s races %3d won %2d | leader cuts from 395 per race %.1f | potential ratio at 300 (median) %.2f" % (
        name, len(rs), sum(r["won"] for r in rs), Y.mean([len(leader_cuts(r, 395, 499)) for r in rs]),
        Y.med([R.ratio(r, 300, "P") for r in rs])))
OUTF.close()
