#!/usr/bin/env python3
"""Candidate 5: the stall after a cut, heir by heir, for every team. Reads y_out/w1, y_out/w2. Output: y_out/c5g.txt

For every leader cut from round 395 in a race (10+ other own dragons): the heir's length t rounds later minus its
length at birth, over the cuts that are still followed at t (the heir alive and not cut again).
"""
import json
import os

import y_lib as Y
import y_r as R

OUTF = open(Y.out_path("c5g.txt"), "w")


def pr(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUTF.write(s + "\n")


w1 = R.load_w1()
recs = [r for r in R.sides(w1) if r["race"]]
w2 = {}
for f in os.listdir(os.path.join(Y.OUT, "w2")):
    if f.endswith(".json"):
        d = json.load(open(os.path.join(Y.OUT, "w2", f)))
        w2[d["gid"]] = d


def readable(r):
    p = w2[r["gid"]]["ping"][r["side"]]
    return p[0] >= 500 and p[1] >= 0.95 * p[0]


SETS = [("meow, earlier bot (readable)", lambda r: r["group"] == "meow" and readable(r)),
        ("meow, live bot (sealed)", lambda r: r["group"] == "meow" and not readable(r) and r["build"] == "live"),
        ("meow, test builds", lambda r: r["group"] == "meow" and r["build"] == "test"),
        ("opponents", lambda r: r["group"] == "opp"),
        ("test4 (vs us)", lambda r: r["group"] == "opp" and r["team"] == Y.T4),
        ("WHQ (vs us)", lambda r: r["group"] == "opp" and r["team"] == Y.WHQ),
        ("forgot", lambda r: r["group"] == "forgot"),
        ("SSS", lambda r: r["group"] == "SSS"),
        ("Vibing++", lambda r: r["group"] == "Vibing++")]
TS = (3, 5, 8, 10, 15, 20, 25)
for cls, lab in ((None, "all maps"), (False, "small maps"), (True, "big maps")):
    pr("\n== %s: heir's growth t rounds after a leader cut made from round 395 (cuts still followed at t)" % lab)
    pr("   group | cuts | " + " | ".join("t=%d" % t for t in TS) + " | heir length at the cut | free cells at the cut: none / some")
    for name, pred in SETS:
        cs = []
        for r in recs:
            if not pred(r) or (cls is not None and r["big"] != cls):
                continue
            for c in w2[r["gid"]]["cuts"]:
                if c["side"] == r["side"] and c["r"] >= 395 and c["units"] >= 11:
                    cs.append(c)
        if len(cs) < 8:
            continue
        cells = []
        for t in TS:
            v = [c["track"][t - 1][0] - c["gets"] for c in cs if len(c["track"]) >= t]
            cells.append("%+.1f (%d)" % (Y.mean(v), len(v)) if len(v) >= 5 else "-")
        pr("   %-28s %4d | %s | %.1f | %d / %d" % (name, len(cs), " | ".join(cells), Y.mean([c["gets"] for c in cs]),
                                                 sum(1 for c in cs if c["fr"] == 0), sum(1 for c in cs if c["fr"] >= 1)))

pr("\n== The same by whether the cut was forced (no free cell) or early (a free cell left), our sealed games against the others")
for name, pred in SETS:
    for fr_lab, fr_pred in (("no free cell", lambda c: c["fr"] == 0), ("a free cell", lambda c: c["fr"] >= 1)):
        cs = [c for r in recs if pred(r) for c in w2[r["gid"]]["cuts"]
              if c["side"] == r["side"] and c["r"] >= 395 and c["units"] >= 11 and fr_pred(c)]
        if len(cs) < 8:
            continue
        cells = []
        for t in (5, 10, 15, 25):
            v = [c["track"][t - 1][0] - c["gets"] for c in cs if len(c["track"]) >= t]
            cells.append("%+.1f (%d)" % (Y.mean(v), len(v)) if len(v) >= 5 else "-")
        rc = [c["end"][1] for c in cs if c["end"] and c["end"][0] == "recut"]
        pr("   %-28s %-13s cuts %4d | t=5/10/15/25: %s | heir cuts again within 10 rounds %.0f%% | room in front of the stub (median) %s | own heads within 5 cells %.1f" % (
            name, fr_lab, len(cs), " | ".join(cells), 100.0 * sum(1 for x in rc if x <= 10) / len(cs),
            Y.med([c["room"] for c in cs]), Y.mean([c["crowd"] for c in cs])))
OUTF.close()
