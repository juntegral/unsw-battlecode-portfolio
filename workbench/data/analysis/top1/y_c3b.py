#!/usr/bin/env python3
"""Candidate 3z, part 2: what happens to the pearls left in the zone, and what the zone costs in natural pearls.
Reads y_out/w3, y_out/w1. Output: y_out/c3b.txt

1. Pearls a small dragon of ours declined inside a zone: who ate them in the end, after how long.
2. Natural pearls eaten per 50 rounds, by our team and by its longest dragon, before and after the switch, in the
   same games, next to the other side of those games.
3. Small dragons inside against outside the zone: natural pearls per 100 dragon-rounds, before and after the
   switch; what comes back if the in-zone rate were the out-of-zone rate.
4. Units and total length through the switch on the same games.
"""
import json
import os
from collections import defaultdict

import y_lib as Y
import y_r as R

OUTF = open(Y.out_path("c3b.txt"), "w")


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

ME = []
for gid, d in W3.items():
    g = games[gid]
    side = Y.side_of(g, Y.ME)
    if side is None or not any(t == Y.ME for t, s in Y.study_sides(g)):
        continue
    readable = d["ping"][0] >= 500 and d["ping"][1] >= 0.95 * d["ping"][0]
    ME.append(dict(gid=gid, d=d, g=g, side=side, oside=Y.opp(side), build=Y.build_of(g), big=Y.is_big(g),
                   readable=readable, rounds=d["rounds"], map=g["map"], cells=int(g["cells"]), w=w1[gid],
                   oteam=g["team%sId" % Y.opp(side)]))

# -----------------------------------------------------------------------------------------------------------------
pr("== 1. Pearls a small dragon of ours declined inside a zone")
pr("   theirs (deep-read-5 2d, live bot): small maps rounds 300-349 / 350-399 / 400-449: left 4.3 / 3.9 / 5.1 a game, in the believed zone 1.1 / 1.0 / 1.2 a game (readable);")
pr("   of those: leader 12 / 11 / 30%, another own 8+ 2%, own under 8 69 / 73 / 52%, enemy 6 / 2 / 2%, nobody within 30 rounds 11 / 12 / 14%, median 9 / 8 / 6 rounds;")
pr("   big maps rounds 150-199 / 200-249 / 250-299: 11.3 / 11.4 / 10.2; 2.4 / 1.8 / 1.9; leader 7 / 17 / 6%, own 8+ 1 / 11 / 1%, own under 8 69 / 58 / 72%, enemy 13 / 8 / 12%, nobody 10 / 6 / 9%, median 10 / 7 / 10")
# left row: [r0, side, tz, bz, org, dur, eaten, same_side, eater id, eater len, eater_longest_now, eater_lead0, eater_bel0, ndecl, cx, cy]


def left_table(rs, phases, zone, org, title):
    pr(" %s" % title)
    pr("   rounds | games | pearls a game | eaten by: the leader | another own dragon 8+ | an own dragon under 8 | the enemy | never | still lying after 30 rounds | median rounds until eaten | pearl-rounds a tile was blocked, a game | declined more than once")
    for lo, hi in phases:
        gm = [r for r in rs if r["rounds"] > lo]
        rows = []
        for r in gm:
            for x in r["d"]["left"]:
                if x[1] != r["side"] or not (lo <= x[0] <= hi) or x[4] != org:
                    continue
                if zone == "b" and x[3] != 1:
                    continue
                if zone == "t" and x[2] != 1:
                    continue
                rows.append(x)
        if not gm or not rows:
            continue
        n = len(rows)
        lead = sum(1 for x in rows if x[6] and x[7] and (x[10] or x[11] or x[12]))
        big = sum(1 for x in rows if x[6] and x[7] and not (x[10] or x[11] or x[12]) and x[9] >= 8)
        small = sum(1 for x in rows if x[6] and x[7] and not (x[10] or x[11] or x[12]) and x[9] < 8)
        en = sum(1 for x in rows if x[6] and not x[7])
        never = sum(1 for x in rows if not x[6])
        late = sum(1 for x in rows if x[5] > 30)
        durs = sorted(x[5] for x in rows if x[6])
        pr("   %d-%d | %3d | %4.1f | %3.0f%% | %3.0f%% | %3.0f%% | %3.0f%% | %3.0f%% | %3.0f%% | %s | %5.1f | %3.0f%%" % (
            lo, hi, len(gm), n / len(gm), 100.0 * lead / n, 100.0 * big / n, 100.0 * small / n, 100.0 * en / n,
            100.0 * never / n, 100.0 * late / n, Y.med(durs), sum(x[5] for x in rows) / len(gm),
            100.0 * sum(1 for x in rows if x[13] > 1) / n))


SM = [(300, 349), (350, 399), (400, 449), (450, 499)]
BG = [(150, 199), (200, 249), (250, 299), (300, 399), (400, 499)]
for cls, lab, phases in ((False, "small maps", SM), (True, "big maps", BG)):
    live = [r for r in ME if r["build"] == "live" and r["big"] == cls]
    test = [r for r in ME if r["build"] == "test" and r["big"] == cls]
    rd = [r for r in ME if r["readable"] and r["big"] == cls]
    left_table(rd, phases, "b", "n", "%s, readable games, NATURAL pearls declined inside the decliner's own named zone" % lab)
    left_table(live, phases, "t", "n", "%s, live bot, NATURAL pearls declined within 9 cells of the true longest" % lab)
    left_table(test, phases, "t", "n", "%s, test builds, NATURAL pearls declined within 9 cells of the true longest" % lab)
    left_table(rd, phases, "b", "c", "%s, readable games, CORPSE pearls declined inside the named zone" % lab)
    left_table(live, phases, "t", "c", "%s, live bot, CORPSE pearls declined within 9 cells of the true longest" % lab)
    left_table(test, phases, "t", "c", "%s, test builds, CORPSE pearls declined within 9 cells of the true longest" % lab)

# -----------------------------------------------------------------------------------------------------------------
pr("\n== 2. Natural pearls eaten per 50 rounds (means per game over the same games throughout)")
pr("   theirs (live bot, any ending): small maps rounds 200-249 ... 450-499: team 24.1 / 20.8 / 15.6 / 14.7 / 9.6 / 7.9; the leader of the time 2.0 / 1.7 / 1.6 / 1.0 / 1.5 / 1.9;")
pr("   big maps rounds 100-149 ... 350-399: team 79.5 / 52.7 / 45.9 / 45.7 / 41.6 / 41.6; leader 4.0 / 3.4 / 2.5 / 2.2 / 1.6 / 2.0; opponents 131.6 / 131.6 / 128.9 / 124.7 / 117.9 / 109.7")


def ni_bin(r, side, lo):
    """[team natural, by the longest, by 2-4, by 5-7, by 8+ non-longest, inside zone, outside] for rounds lo..lo+49"""
    out = [0] * 7
    ni = r["d"]["ni"][side]
    for b in (lo // 25, lo // 25 + 1):
        v = ni.get(str(b))
        if not v:
            continue
        out[0] += sum(v)
        out[1] += v[0] + v[1]
        out[2] += v[2] + v[3]
        out[3] += v[4] + v[5]
        out[4] += v[6] + v[7]
        out[5] += v[0] + v[2] + v[4] + v[6]
        out[6] += v[1] + v[3] + v[5] + v[7]
    return out


def intake_table(rs, bins, need_round, title):
    gm = [r for r in rs if r["rounds"] >= need_round]
    pr(" %s: %d games that reach round %d" % (title, len(gm), need_round))
    if not gm:
        return
    pr("   rounds | our team | our longest of the time | our 2-4-longs | 5-7 | 8+ (not the longest) | eaten within 9 cells of our longest | the other side's team | their longest | our units / total length at the bin start | theirs")
    for lo in bins:
        a = [0.0] * 7
        b = [0.0] * 7
        for r in gm:
            x = ni_bin(r, r["side"], lo)
            y = ni_bin(r, r["oside"], lo)
            for i in range(7):
                a[i] += x[i]
                b[i] += y[i]
        n = len(gm)
        sn = [r["w"]["snap"].get(str(lo)) for r in gm]
        ou = Y.mean([s[r["side"]][0] for s, r in zip(sn, gm) if s])
        ot = Y.mean([s[r["side"]][1] for s, r in zip(sn, gm) if s])
        eu = Y.mean([s[r["oside"]][0] for s, r in zip(sn, gm) if s])
        et = Y.mean([s[r["oside"]][1] for s, r in zip(sn, gm) if s])
        pr("   %d-%d | %5.1f | %4.1f | %5.1f | %4.1f | %4.1f | %5.1f | %5.1f | %4.1f | %4.1f / %5.1f | %4.1f / %5.1f" % (
            lo, lo + 49, a[0] / n, a[1] / n, a[2] / n, a[3] / n, a[4] / n, a[5] / n, b[0] / n, b[1] / n, ou, ot, eu, et))


for cls, lab, bins, need in ((False, "small maps", [200, 250, 300, 350, 400, 450], 400), (True, "big maps", [100, 150, 200, 250, 300, 350, 400, 450], 300)):
    intake_table([r for r in ME if r["build"] == "live" and r["big"] == cls], bins, need, "%s, live bot" % lab)
    intake_table([r for r in ME if r["build"] == "test" and r["big"] == cls], bins, need, "%s, test builds" % lab)
    intake_table([r for r in ME if r["build"] == "live" and r["big"] == cls], bins, 500, "%s, live bot, round-500 games only" % lab)

# -----------------------------------------------------------------------------------------------------------------
pr("\n== 3. Small dragons (2-4, not the queen) inside against outside the zone: natural pearls per 100 dragon-rounds")


def dr_sum(rs, lo, hi, key):
    tot = None
    for r in rs:
        src = r["d"]["drb"] if key == "b" else r["d"]["dr"][r["side"]]
        for b in range(lo // 25, hi // 25 + 1):
            v = src.get(str(b))
            if not v:
                continue
            if tot is None:
                tot = [0] * len(v)
            for i, x in enumerate(v):
                tot[i] += x
    return tot


def dr_table(rs, phases, pre, key, title, need_round):
    gm = [r for r in rs if r["rounds"] >= need_round]
    if not gm:
        return
    pr(" %s (%d games that reach round %d)" % (title, len(gm), need_round))
    k = 4 if key == "b" else 3
    p0 = dr_sum(gm, pre[0], pre[1], key)
    kappa = None
    if p0 and p0[0] and p0[1] and p0[k + 1]:
        kappa = (p0[k] / p0[0]) / (p0[k + 1] / p0[1])
    for lo, hi in [pre] + phases:
        v = dr_sum(gm, lo, hi, key)
        if not v:
            continue
        ng = len(gm)
        span = (hi - lo + 1) / 50.0
        exp_in, exp_out, exp_self = v[0], v[1], v[2]
        eat_in, eat_out, eat_self = v[k], v[k + 1], v[k + 2]
        r_in = 100.0 * eat_in / exp_in if exp_in else 0
        r_out = 100.0 * eat_out / exp_out if exp_out else 0
        r_self = 100.0 * eat_self / exp_self if exp_self else 0
        extra = exp_in * (r_out * (kappa or 1.0) - r_in) / 100.0 / ng / span
        s = "   %d-%d | dragon-rounds a game per 50 rounds: inside %5.0f, outside %5.0f, itself the leader %4.0f" % (
            lo, hi, exp_in / ng / span, exp_out / ng / span, exp_self / ng / span)
        if key == "b":
            s += ", no message %4.0f" % (v[3] / ng / span)
        s += " | pearls per 100 dragon-rounds: inside %.2f, outside %.2f, leader itself %.2f | pearls a game per 50 rounds: inside %.1f, outside %.1f" % (
            r_in, r_out, r_self, eat_in / ng / span, eat_out / ng / span)
        if (lo, hi) != pre:
            s += " | if inside ate like outside (scaled by the before-switch ratio %.2f): %+.1f pearls a game per 50 rounds" % (kappa or 1.0, extra)
        pr(s)


for cls, lab, pre, phases, need in ((False, "small maps", (250, 299), [(300, 349), (350, 399), (400, 449), (450, 499)], 400),
                                    (True, "big maps", (100, 149), [(150, 199), (200, 249), (250, 299), (300, 349), (350, 399), (400, 499)], 300)):
    dr_table([r for r in ME if r["readable"] and r["big"] == cls], phases, pre, "b", "%s, readable games, by the dragon's own named zone" % lab, need)
    dr_table([r for r in ME if r["build"] == "live" and r["big"] == cls], phases, pre, "t", "%s, live bot, by the true longest" % lab, need)
    dr_table([r for r in ME if r["build"] == "test" and r["big"] == cls], phases, pre, "t", "%s, test builds, by the true longest" % lab, need)

# -----------------------------------------------------------------------------------------------------------------
pr("\n== 4. By map, live bot and test builds together: natural pearls a game in the 50 rounds before the switch and in the two 50-round blocks after; the other side's; games that reach 100 rounds past the switch")
bymap = defaultdict(list)
for r in ME:
    bymap[(r["map"], r["cells"])].append(r)
for (mp, cells), rs in sorted(bymap.items(), key=lambda kv: kv[0][1]):
    sw = 150 if cells > 1200 else 300
    gm = [r for r in rs if r["rounds"] >= sw + 100]
    if len(gm) < 3:
        pr("   %-18s %5d cells: %d games reach round %d" % (mp, cells, len(gm), sw + 100))
        continue
    a = [Y.mean([ni_bin(r, r["side"], lo)[0] for r in gm]) for lo in (sw - 50, sw, sw + 50)]
    b = [Y.mean([ni_bin(r, r["oside"], lo)[0] for r in gm]) for lo in (sw - 50, sw, sw + 50)]
    u = [Y.mean([r["w"]["snap"][str(t)][r["side"]][0] for r in gm]) for t in (sw - 50, sw, sw + 50, sw + 100)]
    pr("   %-18s %5d cells, zone %2.0f%% of the board, %2d games | ours %5.1f -> %5.1f -> %5.1f (%+.0f%%) | theirs %5.1f -> %5.1f -> %5.1f (%+.0f%%) | our units %.0f / %.0f / %.0f / %.0f" % (
        mp, cells, 100.0 * min(1.0, 181.0 / cells), len(gm), a[0], a[1], a[2], 100.0 * (a[1] / a[0] - 1) if a[0] else 0,
        b[0], b[1], b[2], 100.0 * (b[1] / b[0] - 1) if b[0] else 0, u[0], u[1], u[2], u[3]))
OUTF.close()
