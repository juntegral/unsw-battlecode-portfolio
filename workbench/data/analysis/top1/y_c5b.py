#!/usr/bin/env python3
"""Candidate 5, counts from walk 2: beliefs (readable pings only) and what feeders do after a leader cut.
Reads y_out/w1 and y_out/w2. Output: y_out/c5b.txt
"""
import json
import math
import os
from collections import Counter, defaultdict

import y_lib as Y
import y_r as R

OUTF = open(Y.out_path("c5b.txt"), "w")


def pr(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUTF.write(s + "\n")


w1 = R.load_w1()
w2 = {}
for f in os.listdir(os.path.join(Y.OUT, "w2")):
    if f.endswith(".json"):
        d = json.load(open(os.path.join(Y.OUT, "w2", f)))
        w2[d["gid"]] = d
recs = R.sides(w1)
me = [r for r in recs if r["group"] == "meow"]
for r in recs:
    r["w2"] = w2[r["gid"]]


def readable(r):
    p = r["w2"]["ping"][r["side"]]
    return p[0] >= 500 and p[1] >= 0.95 * p[0]


pr("== 1. Which of our games have readable pings (theirs: 83 games, 78 in the study; ladder 3 Oct, first 31 of 4 Oct, stride-old)")
c = Counter()
cr = Counter()
for r in me:
    c[r["battle"]] += 1
    if readable(r):
        cr[r["battle"]] += 1
for b in sorted(c):
    pr("   %-20s games %3d readable %3d" % (b, c[b], cr[b]))
rd = [r for r in me if readable(r)]
pr("   readable: %d games (%d small maps, %d big); races among them %d (won %d)" % (
    len(rd), sum(1 for r in rd if not r["big"]), sum(1 for r in rd if r["big"]), sum(1 for r in rd if r["race"]),
    sum(1 for r in rd if r["race"] and r["won"])))
unread_frac = [r["w2"]["ping"][r["side"]][1] / max(1, r["w2"]["ping"][r["side"]][0]) for r in me if not readable(r)]
pr("   in the other games the share of pings that happen to pass the plausibility test: median %.4f, max %.4f" % (
    Y.med(unread_frac), max(unread_frac)))

# bel row: [r, n, true_id, L, ntrue, ndead, nsmall, nself, top, topn, toplen, units, ngeo, ngeo_bel]
pr("\n== 2. What our dragons name as leader, per 25-round block (all own dragons but the longest; a look every 5 rounds)")
pr("   theirs (small maps, blocks 300-324 ... 475-499): true 16 / 32 / 28 / 34 / 37 / 34 / 31 / 28%; dead 49 / 26 / 37 / 27 / 19 / 36 / 36 / 34%;")
pr("   samples with half or more naming it 26 / 35 / 32 / 39 / 48 / 50 / 46 / 39%; could feed by our rules 2.0 / 4.6 / 3.9 / 4.6 / 5.2 / 3.0 / 1.5 / 1.2, without the belief test 7.5 / 9.2 / 9.5 / 10.2 / 9.3 / 5.2 / 4.1 / 3.7")
for cls, lab in ((False, "small maps"), (True, "big maps")):
    rs = [r for r in rd if r["big"] == cls]
    acc = defaultdict(lambda: [0] * 9)
    for r in rs:
        for row in r["w2"]["bel"]:
            if row[0] % 5 or row[1] == 0:
                continue
            a = acc[row[0] // 25 * 25]
            a[0] += row[1]
            a[1] += row[4]
            a[2] += row[5]
            a[3] += row[5] + row[6]
            a[4] += 1
            a[5] += 1 if row[4] * 2 >= row[1] else 0
            a[6] += row[12]
            a[7] += row[13]
            a[8] += row[7]
    pr(" %s (%d games): block | naming a longest | naming a dead id | dead or under half the longest | naming itself | samples with half or more naming it | could feed it: by geometry / also naming it" % (lab, len(rs)))
    for b in sorted(acc):
        a = acc[b]
        if b < 150 or a[4] < 5:
            continue
        pr("   %3d-%3d | %3.0f%% | %3.0f%% | %3.0f%% | %3.0f%% | %3.0f%% (%d) | %.1f / %.1f" % (
            b, b + 24, 100 * a[1] / a[0], 100 * a[2] / a[0], 100 * a[3] / a[0], 100 * a[8] / a[0], 100 * a[5] / a[4], a[4],
            a[6] / a[4], a[7] / a[4]))

# -----------------------------------------------------------------------------------------------------------------
pr("\n== 3. After a leader cut (longest 8+, from round 150): rounds until half of our dragons name the true longest again")
pr("   theirs: median 27 and 27.5 rounds (quartiles 17 and 36-41); 161 cuts on small maps, 227 on big; in between the most-named id is dead in 36-44%, alive but under half in 28-34%")


def quart(xs):
    xs = sorted(xs)
    n = len(xs)
    if not n:
        return (None, None, None)
    return (xs[n // 4], xs[n // 2], xs[(3 * n) // 4])


for cls, lab in ((False, "small maps"), (True, "big maps"), (None, "all")):
    waits = []
    cens = 0
    top_dead = top_small = top_true = top_n = 0
    first_true = []
    for r in rd:
        if cls is not None and r["big"] != cls:
            continue
        bel = {row[0]: row for row in r["w2"]["bel"]}
        for cdat in r["w2"]["cuts"]:
            if cdat["side"] != r["side"]:
                continue
            r0 = cdat["r"]
            t = None
            for rr in range(r0 + 1, r["rounds"] + 1):
                row = bel.get(rr)
                if row is None or row[1] < 4:
                    continue
                if row[4] * 2 >= row[1]:
                    t = rr - r0
                    break
                # what is the most-named id meanwhile
                top_n += 1
                if row[10] == 0:
                    top_dead += 1
                elif row[10] * 2 < row[3]:
                    top_small += 1
                elif row[10] == row[3]:
                    top_true += 1
            if t is None:
                cens += 1
                waits.append(999)
            else:
                waits.append(t)
    q = quart(waits)
    pr("   %-10s cuts %d | rounds until half name the true longest: quartile %s, median %s, quartile %s | never before the end %d | within 5 rounds %d, within 10 %d, within 20 %d" % (
        lab, len(waits), q[0], q[1], q[2], cens, sum(1 for x in waits if x <= 5), sum(1 for x in waits if x <= 10),
        sum(1 for x in waits if x <= 20)))
    if top_n:
        pr("              meanwhile the most-named id is: dead %.0f%%, alive but under half the longest %.0f%%, a longest %.0f%%" % (
            100 * top_dead / top_n, 100 * top_small / top_n, 100 * top_true / top_n))

# -----------------------------------------------------------------------------------------------------------------
pr("\n== 4. Rounds 400-494, a look every 5 rounds, 10+ senders: growth of the longest over the next 5 rounds by the share naming it")
pr("   theirs: under a quarter +0.42 (187 samples), a quarter to a half +1.85 (40), a half to three quarters +1.51 (41), more +2.00 (79)")


def leader_cut_rounds(r):
    return sorted(c["r"] for c in r["w2"]["cuts"] if c["side"] == r["side"])


def samples(rs):
    out = []
    for r in rs:
        bel = {row[0]: row for row in r["w2"]["bel"]}
        cuts = leader_cut_rounds(r)
        for t in range(400, 495, 5):
            row = bel.get(t)
            if row is None or row[1] < 10:
                continue
            L0 = R.snap(r, t, "L")
            L1 = R.snap(r, t + 5 if t + 5 < 500 else "end", "L")
            if L0 is None or L1 is None:
                continue
            share = row[4] / row[1]
            ncut = sum(1 for c in cuts if t <= c < t + 5)
            last = max([c for c in cuts if c < t], default=None)
            out.append(dict(t=t, share=share, g=L1 - L0, ncut=ncut, since=None if last is None else t - last, rec=r,
                            geo=row[12], geob=row[13], L=L0))
    return out


S = samples(rd)
SB = [(0, 0.25, "under a quarter"), (0.25, 0.5, "a quarter to a half"), (0.5, 0.75, "a half to three quarters"), (0.75, 1.01, "more")]


def srow(sub):
    if not sub:
        return "-"
    return "%+.2f (%d)" % (Y.mean([s["g"] for s in sub]), len(sub))


def srow_adj(sub):
    if not sub:
        return "-"
    return "%+.2f" % Y.mean([s["g"] + 2 * s["ncut"] for s in sub])


pr("   share naming the longest | growth (samples) | with 2 per cut in those 5 rounds given back | samples with a cut in those 5 rounds | mean could-feed-by-geometry | mean longest")
for lo, hi, lab in SB:
    sub = [s for s in S if lo <= s["share"] < hi]
    pr("   %-26s | %s | %s | %s | %.1f | %.1f" % (lab, srow(sub), srow_adj(sub), Y.pct(sum(1 for s in sub if s["ncut"]), len(sub)),
                                              Y.mean([s["geo"] for s in sub]) if sub else 0, Y.mean([s["L"] for s in sub]) if sub else 0))
pr("   The same, only samples with NO leader cut in the next 5 rounds:")
for lo, hi, lab in SB:
    sub = [s for s in S if lo <= s["share"] < hi and s["ncut"] == 0]
    pr("   %-26s | %s" % (lab, srow(sub)))
pr("   The same by rounds since the last leader cut (no cut in the next 5 rounds): under a quarter / a quarter or more")
for lo, hi in ((0, 4), (5, 9), (10, 14), (15, 24), (25, 39), (40, 999)):
    a = [s for s in S if s["ncut"] == 0 and s["since"] is not None and lo <= s["since"] <= hi and s["share"] < 0.25]
    b = [s for s in S if s["ncut"] == 0 and s["since"] is not None and lo <= s["since"] <= hi and s["share"] >= 0.25]
    pr("   %3d-%-3s rounds since the cut | %s | %s" % (lo, hi if hi < 999 else "up", srow(a), srow(b)))
a = [s for s in S if s["ncut"] == 0 and s["since"] is None and s["share"] < 0.25]
b = [s for s in S if s["ncut"] == 0 and s["since"] is None and s["share"] >= 0.25]
pr("   no leader cut yet            | %s | %s" % (srow(a), srow(b)))
pr("   Inside the same game (games with both kinds of sample, no cut in the next 5 rounds): mean of (a quarter or more) minus (under a quarter)")
by = defaultdict(lambda: [[], []])
for s in S:
    if s["ncut"]:
        continue
    by[s["rec"]["gid"]][0 if s["share"] < 0.25 else 1].append(s["g"])
d = [Y.mean(v[1]) - Y.mean(v[0]) for v in by.values() if v[0] and v[1]]
if d:
    m = Y.mean(d)
    sd = (sum((x - m) ** 2 for x in d) / max(1, len(d) - 1)) ** 0.5
    pr("   %+.2f per 5 rounds (se %.2f, %d games)" % (m, sd / math.sqrt(len(d)), len(d)))
for opp_id, lab in ((Y.T4, "vs test4"), (Y.WHQ, "vs WHQ"), (None, "vs others")):
    sub = [s for s in S if (s["rec"]["oteam"] == opp_id if opp_id else s["rec"]["oteam"] not in (Y.T4, Y.WHQ))]
    pr("   %-10s under a quarter %s | otherwise %s   (theirs 0.40 / 1.45, 0.35 / 2.41, 0.46 / 1.63)" % (
        lab, srow([s for s in sub if s["share"] < 0.25]), srow([s for s in sub if s["share"] >= 0.25])))

# -----------------------------------------------------------------------------------------------------------------
pr("\n== 5. What the feeders near a cut do in the next 25 rounds. Cuts from round 395 with 10+ other own dragons.")
pr("   Cohort = own dragons at most half the heir's length within 15 cells of the heir's or the stub's head at the cut.")
pr("   H died by choice within 3 steps of the heir | S ... of the stub | B ... of another dragon twice its length | N ... of none of these |")
pr("   R rammed | X boxed in | h alive, 3+ cells nearer the heir | s alive, 3+ nearer the stub | w alive, neither | c cut short (heir cut again or died before round 25)")
CODES = "HSBNRXhswc"
CG = [("meow live", lambda r: r["group"] == "meow" and r["build"] == "live"),
      ("meow test", lambda r: r["group"] == "meow" and r["build"] == "test"),
      ("meow readable", lambda r: r["group"] == "meow" and readable(r)),
      ("meow small", lambda r: r["group"] == "meow" and not r["big"]),
      ("meow big", lambda r: r["group"] == "meow" and r["big"]),
      ("opponents", lambda r: r["group"] == "opp"),
      ("test4 (vs us)", lambda r: r["group"] == "opp" and r["team"] == Y.T4),
      ("WHQ (vs us)", lambda r: r["group"] == "opp" and r["team"] == Y.WHQ),
      ("forgot", lambda r: r["group"] == "forgot"),
      ("SSS", lambda r: r["group"] == "SSS"),
      ("Vibing++", lambda r: r["group"] == "Vibing++")]


def cuts_of(r, lo=395, hi=499, need_units=11, races_only=True):
    if races_only and not r["race"]:
        return []
    return [c for c in r["w2"]["cuts"] if c["side"] == r["side"] and lo <= c["r"] <= hi and c["units"] >= need_units]


pr("   group | cuts | cut short before round 25 | cohort a cut | of the cohort of cuts NOT cut short: " + " ".join("%4s" % x for x in CODES[:-1]) + " | died next to the heir by round: 1-5 / 6-10 / 11-15 / 16-20 / 21-25")
for gname, pred in CG:
    cs = [c for r in recs if pred(r) for c in cuts_of(r)]
    if not cs:
        continue
    full = [c for c in cs if not (c["end"] and c["end"][0] in ("recut", "heirdead", "gameend") and c["end"][1] < 25)]
    cnt = Counter()
    tH = [0] * 5
    for c in full:
        for m in c["cohort"]:
            cnt[m[4]] += 1
            if m[4] == "H" and m[5] is not None:
                tH[min(4, max(0, (m[5] - 1) // 5))] += 1
    n = sum(cnt.values())
    why = Counter(c["end"][0] for c in cs if c["end"] and c["end"][1] < 25 and c["end"][0])
    pr("   %-14s %4d | %4d (%s) | %.1f | %s | %s" % (
        gname, len(cs), len(cs) - len(full), dict(why), Y.mean([len(c["cohort"]) for c in cs]),
        " ".join("%3.0f%%" % (100.0 * cnt[k] / max(1, n)) for k in CODES[:-1]),
        " / ".join("%.0f%%" % (100.0 * x / max(1, sum(tH))) for x in tH)))

pr("\n   The heir's own growth after a cut that was not cut short: mean length at the cut and 5 / 10 / 15 / 20 / 25 / 30 rounds later; share of heirs still the side's longest at 25")
for gname, pred in CG:
    cs = [c for r in recs if pred(r) for c in cuts_of(r)]
    full = [c for c in cs if len(c["track"]) >= 30]
    if len(full) < 5:
        continue
    cells = ["%.1f" % Y.mean([c["gets"] for c in full])]
    for t in (5, 10, 15, 20, 25, 30):
        cells.append("%.1f" % Y.mean([c["track"][t - 1][0] for c in full]))
    pr("   %-14s cuts %4d | %s | %.0f%%" % (gname, len(full), " / ".join(cells), 100 * Y.mean([c["track"][24][1] for c in full])))

pr("\n   How soon the next cut comes (all cuts from 395 of the group): the heir cuts again within 1 / 5 / 10 / 25 rounds; the game ends within 25")
for gname, pred in CG:
    cs = [c for r in recs if pred(r) for c in cuts_of(r)]
    if not cs:
        continue
    rc = [c["end"][1] for c in cs if c["end"] and c["end"][0] == "recut"]
    ge = sum(1 for c in cs if c["end"] and c["end"][0] == "gameend")
    hd = sum(1 for c in cs if c["end"] and c["end"][0] == "heirdead" and c["end"][1] < 25)
    pr("   %-14s cuts %4d | again within 1: %.0f%%, 5: %.0f%%, 10: %.0f%%, 25: %.0f%% | game ends within 25: %.0f%% | heir dies within 25: %.0f%%" % (
        gname, len(cs), 100 * sum(1 for x in rc if x <= 1) / len(cs), 100 * sum(1 for x in rc if x <= 5) / len(cs),
        100 * sum(1 for x in rc if x <= 10) / len(cs), 100 * sum(1 for x in rc if x < 25) / len(cs), 100 * ge / len(cs), 100 * hd / len(cs)))

# -----------------------------------------------------------------------------------------------------------------
pr("\n== 6. Readable games: what the cohort names after a cut (cuts from 395, 10+ others, not cut short), by round after the cut")
pr("   t | cohort alive | naming the heir | the stub | another living id | a dead id | nothing")
cs = [c for r in rd for c in cuts_of(r) if len(c["track"]) >= 30]
pr("   cuts:", len(cs))
for t in (1, 2, 3, 5, 8, 10, 12, 15, 18, 20, 22, 24, 25, 26, 27, 28, 30):
    a = [0] * 6
    for c in cs:
        tr = c["track"][t - 1]
        a[0] += tr[3]
        for i in range(5):
            a[1 + i] += tr[6 + i]
    tot = sum(a[1:]) or 1
    pr("   %2d | %.1f | %3.0f%% | %3.0f%% | %3.0f%% | %3.0f%% | %3.0f%%" % (t, a[0] / len(cs), 100 * a[1] / tot, 100 * a[2] / tot,
                                                                 100 * a[3] / tot, 100 * a[4] / tot, 100 * a[5] / tot))

pr("\n   Fast against slow, cut by cut (readable games, cuts not cut short): the round at which half of the living cohort first names the heir")
fast, slow = [], []
rows = []
for r in rd:
    for c in cuts_of(r):
        if len(c["track"]) < 30:
            continue
        t_half = None
        for t in range(1, 31):
            tr = c["track"][t - 1]
            tot = sum(tr[6:11])
            if tot >= 3 and tr[6] * 2 >= tot:
                t_half = t
                break
        g25 = c["track"][24][0] - c["gets"]
        nH = sum(1 for m in c["cohort"] if m[4] == "H")
        nS = sum(1 for m in c["cohort"] if m[4] == "S")
        rows.append((t_half, g25, nH, nS, len(c["cohort"]), r["gid"], c))
for lab, pred in (("half name the heir within 10 rounds", lambda t: t is not None and t <= 10),
                  ("in 11-20 rounds", lambda t: t is not None and 11 <= t <= 20),
                  ("in 21-30 rounds", lambda t: t is not None and t >= 21),
                  ("not within 30 rounds", lambda t: t is None)):
    sub = [x for x in rows if pred(x[0])]
    if not sub:
        pr("   %-38s none" % lab)
        continue
    pr("   %-38s cuts %3d | heir's growth in 25 rounds %+.1f | cohort %.1f | died next to the heir %.2f a cut | next to the stub %.2f" % (
        lab, len(sub), Y.mean([x[1] for x in sub]), Y.mean([x[4] for x in sub]), Y.mean([x[2] for x in sub]), Y.mean([x[3] for x in sub])))
by = defaultdict(lambda: [[], []])
for x in rows:
    k = 0 if (x[0] is not None and x[0] <= 15) else 1
    by[x[5]][k].append(x[1])
d = [Y.mean(v[0]) - Y.mean(v[1]) for v in by.values() if v[0] and v[1]]
if d:
    m = Y.mean(d)
    sd = (sum((x - m) ** 2 for x in d) / max(1, len(d) - 1)) ** 0.5
    pr("   inside the same game (named within 15 rounds minus later or never): heir's growth in 25 rounds %+.1f (se %.1f, %d games)" % (m, sd / math.sqrt(len(d)), len(d)))
OUTF.close()
