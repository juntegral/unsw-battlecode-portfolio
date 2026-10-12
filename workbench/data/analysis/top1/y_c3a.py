#!/usr/bin/env python3
"""Candidate 3z, part 1: the free-pearl rate. Reads y_out/w3. Output: y_out/c3a.txt

"Pearl turn": a non-queen dragon of 2-4 gives a move order, no enemy head in its 7x7 view, a pearl on a free next
cell that has a further free neighbour. "Taken": its first step eats such a pearl.
1. The rate around our switch round (150 on maps over 1,200 cells, 300 otherwise), per build and team.
2. Inside against outside the zone, by the true longest dragon (all games) and by the dragon's own named leader
   (readable pings), natural pearls and corpse pearls apart.
3. How much of the fall comes back if every in-zone turn behaved like an out-of-zone turn.
4. By map (the zone's 181 cells as a share of the board).
5. Other teams near their own longest dragon, before and during feeding.
"""
import json
import os
from collections import defaultdict

import y_lib as Y

OUTF = open(Y.out_path("c3a.txt"), "w")


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

# one record per game-side of interest
RECS = []
for gid, d in W3.items():
    g = games[gid]
    for team, side in Y.study_sides(g):
        o = Y.opp(side)
        readable = (team == Y.ME and d["ping"][0] >= 500 and d["ping"][1] >= 0.95 * d["ping"][0])
        RECS.append(dict(gid=gid, d=d, g=g, team=team, side=side, group="meow" if team == Y.ME else Y.TOP[team],
                         build=Y.build_of(g) if team == Y.ME else "", big=Y.is_big(g), readable=readable,
                         oteam=g["team%sId" % o], rounds=d["rounds"], map=g["map"], cells=int(g["cells"])))
        if team == Y.ME:
            RECS.append(dict(gid=gid, d=d, g=g, team=g["team%sId" % o], side=o, group="opp", build=Y.build_of(g),
                             big=Y.is_big(g), readable=False, oteam=Y.ME, rounds=d["rounds"], map=g["map"], cells=int(g["cells"])))

GROUPS = [("meow live", lambda r: r["group"] == "meow" and r["build"] == "live"),
          ("meow test", lambda r: r["group"] == "meow" and r["build"] == "test"),
          ("meow readable", lambda r: r["group"] == "meow" and r["readable"]),
          ("opponents", lambda r: r["group"] == "opp"),
          ("test4 (vs us)", lambda r: r["group"] == "opp" and r["team"] == Y.T4),
          ("WHQ (vs us)", lambda r: r["group"] == "opp" and r["team"] == Y.WHQ),
          ("forgot", lambda r: r["group"] == "forgot"),
          ("SSS", lambda r: r["group"] == "SSS"),
          ("Vibing++", lambda r: r["group"] == "Vibing++")]


def rate(n, t):
    return "%2.0f%% of %d" % (100.0 * t / n, n) if n else "-"


def rate_s(n, t):
    return "%2.0f%%" % (100.0 * t / n) if n >= 20 else "  -"


def pt10(rs, lo, hi):
    n = t = 0
    for r in rs:
        p = r["d"]["pt10"]
        s = r["side"]
        for b in range(lo // 10, hi // 10 + 1):
            v = p.get("%s|%d" % (s, b))
            if v:
                n += v[0]
                t += v[1]
    return n, t


pr("== 1. The free-pearl rate around our switch round")
pr("   theirs: maps over 1,200 cells: live 83% (rounds 0-149) -> 58% (150-399); 10-round blocks 130-139 ... 170-179: 84, 84, 64, 60, 58%;")
pr("   other maps: 88% (0-299) -> 53% (300-399); blocks 280-289 ... 310-319: 85, 83, 64, 51%; opponents 84-85% and 84 -> 78%; top three 80-94%")
for cls, lab, cuts in ((True, "maps over 1,200 cells", [(50, 99), (100, 129), (130, 139), (140, 149), (150, 159), (160, 169), (170, 199), (200, 299), (300, 399), (400, 499)]),
                       (False, "maps of 1,200 cells or fewer", [(100, 199), (200, 279), (280, 289), (290, 299), (300, 309), (310, 319), (320, 349), (350, 399), (400, 449), (450, 499)])):
    pr(" %s: rounds %s" % (lab, " | ".join("%d-%d" % c for c in cuts)))
    for gname, pred in GROUPS:
        rs = [r for r in RECS if pred(r) and r["big"] == cls]
        if not rs:
            continue
        pr("   %-14s %s" % (gname, " | ".join(rate_s(*pt10(rs, lo, hi)) for lo, hi in cuts)))
    for b in sorted(set(r["g"]["battle_id"] for r in RECS if r["group"] == "meow")):
        rs = [r for r in RECS if r["group"] == "meow" and r["g"]["battle_id"] == b and r["big"] == cls]
        if rs:
            pr("     run %-18s %s" % (b, " | ".join(rate_s(*pt10(rs, lo, hi)) for lo, hi in cuts)))


# ---- pt aggregation -------------------------------------------------------------------------------------------
def pt_sum(rs, lo, hi, want):
    """Sum [n, taken] over pt keys of the records' own side in 25-round bins lo..hi (inclusive rounds), where
    want(len, td, lc, bd, org) is true."""
    n = t = 0
    blo, bhi = lo // 25, hi // 25
    for r in rs:
        s = r["side"]
        for k, v in r["d"]["pt"].items():
            p = k.split("|")
            if p[0] != s:
                continue
            b = int(p[1])
            if b < blo or b > bhi:
                continue
            if want(int(p[2]), p[3], p[4], p[5], p[6]):
                n += v[0]
                t += v[1]
    return n, t


IN = ("0", "1", "2")
OUT = ("3", "4", "5")

pr("\n== 2. Inside against outside the zone (9 cells), natural pearls only unless said")
pr("   theirs (deep-read-5 2d, by the dragon's own belief): small maps rounds 300-349 / 350-399: inside 26% / 22%, outside 87% / 87%, names itself 78% / 72%;")
pr("   before the switch (200-249 / 250-299): 84 / 85% inside, 86 / 86% outside; big maps 150-199 / 200-249: inside 24% / 19%, outside 77% / 77%; before (100-149): 83% / 81%")
for cls, lab, phases in ((False, "small maps", [(200, 249), (250, 299), (300, 349), (350, 399), (400, 449), (450, 499)]),
                         (True, "big maps", [(100, 149), (150, 199), (200, 249), (250, 299), (300, 349), (350, 399), (400, 449), (450, 499)])):
    pr(" %s, rounds %s" % (lab, " | ".join("%d-%d" % p for p in phases)))
    rd = [r for r in RECS if r["group"] == "meow" and r["readable"] and r["big"] == cls]
    pr("   by the dragon's own named leader (readable games: %d)" % len(rd))
    for name, want in (("inside the named leader's zone", lambda L, td, lc, bd, org: bd in IN and org == "n"),
                       ("outside it", lambda L, td, lc, bd, org: bd in OUT and org == "n"),
                       ("it names itself", lambda L, td, lc, bd, org: bd == "s" and org == "n"),
                       ("it sent no leader message", lambda L, td, lc, bd, org: bd == "n" and org == "n"),
                       ("all natural", lambda L, td, lc, bd, org: org == "n"),
                       ("corpse pearls, inside the zone", lambda L, td, lc, bd, org: bd in IN and org == "c"),
                       ("corpse pearls, outside", lambda L, td, lc, bd, org: bd in OUT and org == "c")):
        pr("     %-34s %s" % (name, " | ".join(rate(*pt_sum(rd, lo, hi, want)) for lo, hi in phases)))
    pr("     by cells from the pearl to the named zone head, natural pearls: 0-3 / 4-6 / 7-9 / 10-12 / 13-16 / 17+")
    for lo, hi in phases:
        pr("       rounds %d-%d: %s" % (lo, hi, " / ".join(
            rate_s(*pt_sum(rd, lo, hi, lambda L, td, lc, bd, org, b=b: bd == b and org == "n")) for b in "012345")))
    for gname, pred in GROUPS[:2] + GROUPS[3:]:
        rs = [r for r in RECS if pred(r) and r["big"] == cls]
        if not rs:
            continue
        pr("   %s, by the true longest dragon at the round's start" % gname)
        for name, want in (("pearl within 9 cells of the longest", lambda L, td, lc, bd, org: td in IN and org == "n"),
                           ("farther", lambda L, td, lc, bd, org: td in OUT and org == "n"),
                           ("the dragon is itself the longest", lambda L, td, lc, bd, org: td == "s" and org == "n"),
                           ("within 9 cells, the longest is 10+", lambda L, td, lc, bd, org: td in IN and lc == "2" and org == "n"),
                           ("corpse pearls within 9 cells", lambda L, td, lc, bd, org: td in IN and org == "c"),
                           ("corpse pearls farther", lambda L, td, lc, bd, org: td in OUT and org == "c")):
            pr("     %-34s %s" % (name, " | ".join(rate(*pt_sum(rs, lo, hi, want)) for lo, hi in phases)))

pr("\n== 3. How much of the fall comes back if an in-zone turn were taken like an out-of-zone turn of the same rounds")
for cls, lab, pre, posts in ((False, "small maps", (250, 299), [(300, 349), (350, 399), (400, 449), (450, 499)]),
                             (True, "big maps", (100, 149), [(150, 199), (200, 249), (250, 299), (300, 399)])):
    for sel_name, rs, zkey in (("readable games, the dragon's own named zone", [r for r in RECS if r["group"] == "meow" and r["readable"] and r["big"] == cls], "bd"),
                               ("live bot, zone of the true longest", [r for r in RECS if r["group"] == "meow" and r["build"] == "live" and r["big"] == cls], "td"),
                               ("test builds, zone of the true longest", [r for r in RECS if r["group"] == "meow" and r["build"] == "test" and r["big"] == cls], "td")):
        n0, t0 = pt_sum(rs, pre[0], pre[1], lambda L, td, lc, bd, org: True)
        if not n0:
            continue
        r_pre = t0 / n0
        for lo, hi in posts:
            def zk(td, bd):
                return bd if zkey == "bd" else td
            n_all, t_all = pt_sum(rs, lo, hi, lambda L, td, lc, bd, org: True)
            n_in, t_in = pt_sum(rs, lo, hi, lambda L, td, lc, bd, org: zk(td, bd) in IN)
            n_out, t_out = pt_sum(rs, lo, hi, lambda L, td, lc, bd, org: zk(td, bd) in OUT)
            if not (n_all and n_in and n_out):
                continue
            r_after = t_all / n_all
            r_out = t_out / n_out
            r_cf = (t_all - t_in + n_in * r_out) / n_all
            share = (r_cf - r_after) / (r_pre - r_after) if r_pre > r_after else 0
            pr("   %-10s %-46s rounds %d-%d: before the switch %.0f%%, now %.0f%% (in zone %.0f%% of %d turns, outside %.0f%% of %d), with the zone off %.0f%% -> %.0f%% of the fall comes back; in-zone turns are %.0f%% of all pearl turns" % (
                lab, sel_name, lo, hi, 100 * r_pre, 100 * r_after, 100 * t_in / n_in, n_in, 100 * r_out, n_out, 100 * r_cf,
                100 * share, 100.0 * n_in / n_all))

pr("\n== 4. By map: the zone (181 cells) as a share of the board; our live bot's free-pearl rate 50 rounds before / after the switch; in-zone share of pearl turns after it")
bymap = defaultdict(list)
for r in RECS:
    if r["group"] == "meow":
        bymap[(r["map"], r["cells"])].append(r)
for (mp, cells), rs in sorted(bymap.items(), key=lambda kv: kv[0][1]):
    sw = 150 if cells > 1200 else 300
    n0, t0 = pt_sum(rs, sw - 50, sw - 1, lambda L, td, lc, bd, org: True)
    n1, t1 = pt_sum(rs, sw, sw + 99, lambda L, td, lc, bd, org: True)
    ni, ti = pt_sum(rs, sw, sw + 99, lambda L, td, lc, bd, org: td in IN)
    no, to = pt_sum(rs, sw, sw + 99, lambda L, td, lc, bd, org: td in OUT)
    pr("   %-18s %5d cells, zone %3.0f%% of the board | before %s | after (100 rounds) %s | within 9 cells of the longest %s, farther %s | share of pearl turns within 9 cells %.0f%%" % (
        mp, cells, 100.0 * min(1.0, 181.0 / cells), rate_s(n0, t0), rate_s(n1, t1), rate_s(ni, ti), rate_s(no, to),
        100.0 * ni / max(1, n1)))

pr("\n== 5. Does anybody else leave pearls near its own longest dragon? Natural pearls, pearl within 9 cells of the side's longest (5+ long) / farther")
for cls, lab in ((False, "small maps"), (True, "big maps")):
    pr(" %s: rounds 150-299 | 300-399 | 400-499 ; then the same with the longest 10+ long" % lab)
    for gname, pred in GROUPS:
        rs = [r for r in RECS if pred(r) and r["big"] == cls]
        if not rs:
            continue
        cells = []
        for lcs in (("1", "2"), ("2",)):
            for lo, hi in ((150, 299), (300, 399), (400, 499)):
                a = pt_sum(rs, lo, hi, lambda L, td, lc, bd, org: td in IN and lc in lcs and org == "n")
                b = pt_sum(rs, lo, hi, lambda L, td, lc, bd, org: td in OUT and lc in lcs and org == "n")
                cells.append("%s / %s" % (rate_s(*a), rate_s(*b)))
        pr("   %-14s %s || %s" % (gname, " | ".join(cells[:3]), " | ".join(cells[3:])))
    pr("   ... corpse pearls (feeder pearls are among them), within 9 cells of the longest 10+ / farther, rounds 300-399 | 400-499")
    for gname, pred in GROUPS:
        rs = [r for r in RECS if pred(r) and r["big"] == cls]
        if not rs:
            continue
        cells = []
        for lo, hi in ((300, 399), (400, 499)):
            a = pt_sum(rs, lo, hi, lambda L, td, lc, bd, org: td in IN and lc == "2" and org == "c")
            b = pt_sum(rs, lo, hi, lambda L, td, lc, bd, org: td in OUT and lc == "2" and org == "c")
            cells.append("%s / %s" % (rate(*a), rate(*b)))
        pr("   %-14s %s" % (gname, " | ".join(cells)))
OUTF.close()
