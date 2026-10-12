#!/usr/bin/env python3
"""Candidate 3z, part 3: the leader's side, the backfire counts and the size. Reads y_out/w1, y_out/w3.
Output: y_out/c3c.txt

A. Natural pearls per 25 rounds around the switch (same games), ours and the other side's; per small dragon.
B. Where the segments of our final longest dragon come from, per 50 rounds, all our races and our race wins.
C. What the zone gives the leader: declined-in-zone pearls that the final lineage ate; wins with a margin under it.
D. The leader boxed in: how often our longest dragon has no free cell, and who blocks; other teams for scale.
E. The size: extra natural pearls at the small dragons' before-switch rate per dragon-round (plain, and scaled by
   the other side's trend), and what that would be worth on our own win curve.
"""
import json
import math
import os
from collections import defaultdict

import y_lib as Y
import y_r as R

OUTF = open(Y.out_path("c3c.txt"), "w")


def pr(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUTF.write(s + "\n")


games = {g["game_id"]: g for g in Y.load_games()}
W3 = {}
for f in os.listdir(os.path.join(Y.OUT, "w3")):
    if f.endswith(".json"):
        d = json.load(open(os.path.join(Y.OUT, "w3", f)))
        W3[d["gid"]] = d
w1 = R.load_w1()
allrecs = R.sides(w1)
for r in allrecs:
    r["d"] = W3[r["gid"]]
ME = [r for r in allrecs if r["group"] == "meow"]


def sw_of(r):
    return 150 if r["big"] else 300


# -----------------------------------------------------------------------------------------------------------------
pr("== A. Natural pearls eaten per 25 rounds around our switch round (games that last 100 rounds past it): ours | the other side's; and per 100 dragon-rounds of small dragons (2-4)")


def natcls_bin(w, side, b):
    v = w["natcls"][side].get(str(b))
    return sum(v) if v else 0


def dr_bin(d, side, b):
    v = d["dr"][side].get(str(b))
    if not v:
        return 0, 0
    return v[0] + v[1] + v[2], v[3] + v[4] + v[5]


for cls, lab in ((False, "small maps (switch at 300)"), (True, "big maps (switch at 150)")):
    for bname, pred in (("live bot", lambda r: r["build"] == "live"), ("test builds", lambda r: r["build"] == "test")):
        rs = [r for r in ME if r["big"] == cls and pred(r) and r["rounds"] >= sw_of(r) + 100]
        if not rs:
            continue
        sw = 150 if cls else 300
        pr(" %s, %s, %d games" % (lab, bname, len(rs)))
        for off in (-75, -50, -25, 0, 25, 50, 75):
            b = (sw + off) // 25
            o = Y.mean([natcls_bin(r["w"], r["side"], b) for r in rs])
            e = Y.mean([natcls_bin(r["w"], r["oside"], b) for r in rs])
            ex = sum(dr_bin(r["d"], r["side"], b)[0] for r in rs)
            ea = sum(dr_bin(r["d"], r["side"], b)[1] for r in rs)
            ox = sum(dr_bin(r["d"], r["oside"], b)[0] for r in rs)
            oa = sum(dr_bin(r["d"], r["oside"], b)[1] for r in rs)
            pr("   rounds %3d-%3d | ours %5.1f | theirs %5.1f | our small dragons: %5.0f dragon-rounds a game, %.2f pearls per 100 | theirs: %5.0f, %.2f" % (
                sw + off, sw + off + 24, o, e, ex / len(rs), 100.0 * ea / max(1, ex), ox / len(rs), 100.0 * oa / max(1, ox)))

# -----------------------------------------------------------------------------------------------------------------
pr("\n== B. Where the segments of our final longest dragon come from (its lineage), means per race per 50 rounds")
pr("   theirs (table B1, live bot, small maps, rounds 250-299 ... 450-499): natural 4.0 / 5.0 / 3.7 / 3.5 / 5.0; own dragons dead by choice 0.1 / 0.2 / 0.2 / 10.2 / 6.1;")
pr("   other own corpses 2.2 / 2.0 / 2.0 / 1.7 / 1.5; enemy corpses 0.2 / 0.4 / 0.3 / 0.4 / 1.2; big maps: natural 3.1 / 2.0 / 2.6 / 2.8 / 4.1; by choice 1.7 / 2.6 / 1.7 / 9.0 / 5.6")


def sources(r):
    """per 50-round bin (index = round // 50): [natural, feeder pearls, other own corpses, enemy corpses] of the lineage"""
    w = r["w"]
    fin = w["final"][r["side"]]
    out = defaultdict(lambda: [0, 0, 0, 0])
    if not fin:
        return out
    chain = R.lineage(w, fin[0][1])
    ids = set(c[0] for c in chain)
    for k, n in w["nat"].items():
        did, b25 = k.split(":")
        did, b25 = int(did), int(b25)
        if did in ids and R.lineage_at(chain, b25 * 25 + 12) == did:
            out[b25 // 2][0] += n
    death = {}
    for dd in w["deaths"]:
        death[dd[1]] = dd
    team = w["team"]
    for rr, eater, dead in w["ceat"]:
        if eater not in ids or R.lineage_at(chain, rr) != eater:
            continue
        dside = team.get(str(dead))
        if dside != r["side"]:
            out[rr // 50][3] += 1
            continue
        dd = death.get(dead)
        if dd is not None and dd[3] != "headon" and dd[8] >= 1:
            out[rr // 50][1] += 1
        else:
            out[rr // 50][2] += 1
    return out


SRC = {}
for cls, lab in ((False, "small maps"), (True, "big maps")):
    for name, pred in (("all our races, live bot", lambda r: r["race"] and r["build"] == "live"),
                       ("all our races, test builds", lambda r: r["race"] and r["build"] == "test"),
                       ("our race wins (all builds)", lambda r: r["race"] and r["won"]),
                       ("our race losses (all builds)", lambda r: r["race"] and not r["won"])):
        rs = [r for r in ME if pred(r) and r["big"] == cls]
        if not rs:
            continue
        acc = defaultdict(lambda: [0, 0, 0, 0])
        for r in rs:
            if r["gid"] not in SRC:
                SRC[r["gid"]] = sources(r)
            for b, v in SRC[r["gid"]].items():
                for i in range(4):
                    acc[b][i] += v[i]
        bins = range(2, 10)
        pr(" %s, %s (%d races): rounds %s" % (lab, name, len(rs), " | ".join("%d-%d" % (b * 50, b * 50 + 49) for b in bins)))
        for i, nm in enumerate(("natural pearls", "pearls of own dragons dead by choice", "pearls of other own corpses", "pearls of enemy corpses")):
            pr("   %-38s %s" % (nm, " | ".join("%4.1f" % (acc[b][i] / len(rs)) for b in bins)))

# -----------------------------------------------------------------------------------------------------------------
pr("\n== C. What the zone gives the leader: pearls that a small dragon of ours declined inside a zone (9 cells from the true longest, or its own named zone)")
pr("   and that the dragon which ends as our longest (its lineage) ate later. Per race, from the switch round to the end.")


def zone_yield(r):
    """natural and corpse pearls declined in a zone by our side and later eaten by our final lineage, after the switch"""
    w = r["w"]
    fin = w["final"][r["side"]]
    if not fin:
        return 0, 0, 0, 0
    chain = R.lineage(w, fin[0][1])
    sw = sw_of(r)
    nat = cor = nat_all = cor_all = 0
    for x in r["d"]["left"]:
        if x[1] != r["side"] or x[0] <= sw:
            continue
        if x[4] == "n":
            nat_all += 1
        else:
            cor_all += 1
        if x[6] and x[7] and R.lineage_at(chain, x[0] + x[5]) == x[8]:
            if x[4] == "n":
                nat += 1
            else:
                cor += 1
    return nat, cor, nat_all, cor_all


def lineage_natural_after_switch(r):
    s = SRC.get(r["gid"]) or sources(r)
    sw = sw_of(r)
    return sum(v[0] for b, v in s.items() if b * 50 >= sw)


for cls, lab in ((False, "small maps"), (True, "big maps")):
    for name, pred in (("our races", lambda r: r["race"]), ("our race wins", lambda r: r["race"] and r["won"])):
        rs = [r for r in ME if pred(r) and r["big"] == cls]
        if not rs:
            continue
        ys = [zone_yield(r) for r in rs]
        ln = [lineage_natural_after_switch(r) for r in rs]
        pr(" %s, %s (%d): declined in a zone per race: natural %.1f, corpse %.1f | of them eaten by the final lineage: natural %.1f (median %s), corpse %.1f (median %s) | all natural pearls the lineage ate after the switch %.1f" % (
            lab, name, len(rs), Y.mean([y[2] for y in ys]), Y.mean([y[3] for y in ys]), Y.mean([y[0] for y in ys]),
            Y.med([y[0] for y in ys]), Y.mean([y[1] for y in ys]), Y.med([y[1] for y in ys]), Y.mean(ln)))
wins = [r for r in ME if r["race"] and r["won"]]
pr(" Our %d race wins: margin (our final longest minus theirs) against what the zone gave the final lineage" % len(wins))
n1 = n2 = n3 = n4 = 0
rows = []
for r in wins:
    m = R.snap(r, "end", "L") - R.snap(r, "end", "L", False)
    nat, cor, _, _ = zone_yield(r)
    lna = lineage_natural_after_switch(r)
    rows.append((m, nat, cor, lna, r["gid"], r["map"], r["build"]))
    if m < nat:
        n1 += 1
    if m < nat + cor:
        n2 += 1
    if m < lna:
        n3 += 1
    if m < lna + cor:
        n4 += 1
pr("   wins with a margin smaller than: the declined natural pearls the lineage ate: %d | those plus the declined corpse pearls it ate: %d | ALL natural pearls the lineage ate after the switch: %d | all natural plus declined corpse: %d" % (n1, n2, n3, n4))
rows.sort()
pr("   the closest wins (margin, declined natural eaten by lineage, declined corpse eaten by lineage, all natural after the switch, game, map, build):")
for x in rows[:14]:
    pr("     %s" % (x,))
losses = [r for r in ME if r["race"] and not r["won"]]
pr(" Our %d race losses: margins of 5 or less: %d; of 10 or less: %d" % (
    len(losses), sum(1 for r in losses if R.snap(r, "end", "L", False) - R.snap(r, "end", "L") <= 5),
    sum(1 for r in losses if R.snap(r, "end", "L", False) - R.snap(r, "end", "L") <= 10)))

# -----------------------------------------------------------------------------------------------------------------
pr("\n== D. The longest dragon (8+) boxed in: share of its turns with no free cell / with one; what blocks its neighbour cells then; small own heads near it")
pr("   group | phase | leader turns a game | no free cell | one free cell | of blocked cells at 0-1 free: kelp / its own body / an own dragon under 8 / an own dragon 8+ / an enemy | own heads under 8 within 3 cells (mean) | turns with one touching its head")
GD = [("meow live", lambda r: r["group"] == "meow" and r["build"] == "live"),
      ("meow test", lambda r: r["group"] == "meow" and r["build"] == "test"),
      ("opponents", lambda r: r["group"] == "opp"),
      ("WHQ (vs us)", lambda r: r["group"] == "opp" and r["team"] == Y.WHQ),
      ("test4 (vs us)", lambda r: r["group"] == "opp" and r["team"] == Y.T4),
      ("forgot", lambda r: r["group"] == "forgot"),
      ("SSS", lambda r: r["group"] == "SSS"),
      ("Vibing++", lambda r: r["group"] == "Vibing++")]
for cls, lab, phases in ((False, "small maps", [(200, 299), (300, 399), (400, 499)]), (True, "big maps", [(100, 149), (150, 299), (300, 399), (400, 499)])):
    pr(" %s" % lab)
    for gname, pred in GD:
        rs = [r for r in allrecs if pred(r) and r["big"] == cls]
        if not rs:
            continue
        for lo, hi in phases:
            acc = [0] * 10
            for r in rs:
                bx = r["d"]["box"][r["side"]]
                for b in range(lo // 50, hi // 50 + 1):
                    v = bx.get(str(b))
                    if v:
                        for i in range(10):
                            acc[i] += v[i]
            if acc[0] < 200:
                continue
            blk = sum(acc[3:8]) or 1
            pr("   %-14s %d-%d | %5.1f | %4.1f%% | %4.1f%% | %2.0f%% / %2.0f%% / %2.0f%% / %2.0f%% / %2.0f%% | %.2f | %4.1f%%" % (
                gname, lo, hi, acc[0] / len(rs), 100.0 * acc[1] / acc[0], 100.0 * acc[2] / acc[0], 100.0 * acc[3] / blk,
                100.0 * acc[4] / blk, 100.0 * acc[5] / blk, 100.0 * acc[6] / blk, 100.0 * acc[7] / blk, acc[8] / acc[0],
                100.0 * acc[9] / acc[0]))

# -----------------------------------------------------------------------------------------------------------------
pr("\n== E. The size. Extra natural pearls if our small dragons had kept the rate per dragon-round they had in the 50 rounds before the switch")
pr("   'plain' = that rate times the dragon-rounds they really had; 'trend' = the same scaled by how the other side's small dragons' rate moved in those rounds")


def extra_pearls(r, upto):
    """(plain, trend) extra natural pearls from the switch to round `upto` for our side."""
    d = r["d"]
    sw = sw_of(r)
    s, o = r["side"], r["oside"]
    px = pa = ox = oa = 0
    for b in ((sw - 50) // 25, (sw - 25) // 25):
        x, a = dr_bin(d, s, b)
        px += x
        pa += a
        x, a = dr_bin(d, o, b)
        ox += x
        oa += a
    if px < 50:
        return 0.0, 0.0
    rate = pa / px
    orate = oa / ox if ox >= 50 else None
    plain = trend = 0.0
    for b in range(sw // 25, upto // 25):
        x, a = dr_bin(d, s, b)
        plain += x * rate - a
        f = 1.0
        if orate:
            x2, a2 = dr_bin(d, o, b)
            if x2 >= 25:
                f = (a2 / x2) / orate
        trend += x * rate * min(1.5, f) - a
    return plain, trend


for cls, lab, upto_list in ((False, "small maps", (400, 500)), (True, "big maps", (300, 400, 500))):
    for bname, pred in (("live bot", lambda r: r["build"] == "live"), ("test builds", lambda r: r["build"] == "test"),
                        ("all builds, races", lambda r: r["race"]), ("all builds, race wins", lambda r: r["race"] and r["won"])):
        for upto in upto_list:
            rs = [r for r in ME if r["big"] == cls and pred(r) and r["rounds"] >= upto]
            if not rs:
                continue
            ex = [extra_pearls(r, upto) for r in rs]
            tot = [R.snap(r, upto if upto < 500 else "end", "total") for r in rs]
            pr("   %-10s %-22s switch to round %d (%3d games): extra pearls a game: plain %+6.1f (median %+.1f), trend %+6.1f (median %+.1f) | our total length then %.0f -> plain %+.0f%%, trend %+.0f%%" % (
                lab, bname, upto, len(rs), Y.mean([e[0] for e in ex]), Y.med([e[0] for e in ex]), Y.mean([e[1] for e in ex]),
                Y.med([e[1] for e in ex]), Y.mean(tot), 100.0 * Y.mean([e[0] for e in ex]) / Y.mean(tot),
                100.0 * Y.mean([e[1] for e in ex]) / Y.mean(tot)))

pr("\n   Our own win curve on total length: win ~ c + b*ln(own total / enemy total at round T), all our games that reach round T (any ending)")
FITS = {}
for cls, lab, T in ((False, "small maps", 400), (True, "big maps", 300), (True, "big maps", 400)):
    rs = [r for r in ME if r["big"] == cls and r["rounds"] >= T and R.ratio(r, T, "total")]
    X = [[1.0, math.log(R.ratio(r, T, "total"))] for r in rs]
    y = [1 if r["won"] else 0 for r in rs]
    beta, cov, ll = Y.logit_fit(X, y, ridge=1e-4)
    FITS[(cls, T)] = beta
    pr("   %-10s round %d: %d games, %d won; c=%+.2f b=%.2f (se %.2f)" % (lab, T, len(rs), sum(y), beta[0], beta[1], math.sqrt(cov[1][1])))


def win_gain(rs, T, beta, which, share, races_only=False, leader_cost=0.0):
    """Expected extra wins if each game's own total at round T rises by share * its extra pearls."""
    g = 0.0
    n = 0
    for r in rs:
        if r["rounds"] < T:
            continue
        if races_only and not r["race"]:
            continue
        ratio = R.ratio(r, T, "total")
        if not ratio:
            continue
        ex = extra_pearls(r, T)[which] * share - leader_cost
        own = R.snap(r, T, "total")
        new = ratio * max(0.5, (own + ex) / own)
        p0 = Y.sigmoid(beta[0] + beta[1] * math.log(ratio))
        p1 = Y.sigmoid(beta[0] + beta[1] * math.log(new))
        g += p1 - p0
        n += 1
    return g, n


pr("\n   Extra wins on that curve (a curve earned with the bot as it is; see the text for why this is an upper reading):")
for name, pred in (("all 401 games", lambda r: True), ("live bot, 275 games", lambda r: r["build"] == "live")):
    for which, wl in ((0, "plain"), (1, "trend")):
        for share, sl in ((1.0, "all of it"), (0.5, "half of it")):
            tot = 0.0
            parts = []
            for cls, T in ((False, 400), (True, 300)):
                rs = [r for r in ME if r["big"] == cls and pred(r)]
                g, n = win_gain(rs, T, FITS[(cls, T)], which, share)
                tot += g
                parts.append("%s %+.1f of %d games" % ("big" if cls else "small", g, n))
            pr("   %-20s %-5s %-10s -> %+.1f wins (%s)" % (name, wl, sl, tot, ", ".join(parts)))
OUTF.close()
