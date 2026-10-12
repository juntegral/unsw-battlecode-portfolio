#!/usr/bin/env python3
"""Candidate 5: what it could be worth, derived my own way; and the backfire counts.
Reads y_out/w1, y_out/w4 (and y_out/w4b if present). Output: y_out/c5d.txt

1. What is left unfed at the end: own dragons within 15 cells of the final longest, and farther, by group.
2. How close our two longest dragons are during feeding (the risk of "regional leaders" under an age rule).
3. The size. For each of our lost races: the pearls of feeders that died for a fresh stub or for a dragon under
   twice their length (what the record change and the "see it is long" test would stop), what the final lineage
   got of them, and what it would have got at the rate of deaths next to the true longest. Three readings.
   Plus A5's own what-ifs recounted (growth after round 400 times 1.25 / 1.5; +5 / +10 segments).
4. The "see it is long" test on today's deaths (needs y_out/w4b).
"""
import json
import os
from collections import Counter, defaultdict

import y_lib as Y
import y_r as R

OUTF = open(Y.out_path("c5d.txt"), "w")


def pr(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUTF.write(s + "\n")


w1 = R.load_w1()
recs = R.sides(w1)
races = [r for r in recs if r["race"]]
me = [r for r in races if r["group"] == "meow"]


def load_dir(name):
    out = {}
    p = os.path.join(Y.OUT, name)
    if not os.path.isdir(p):
        return out
    for f in os.listdir(p):
        if f.endswith(".json"):
            d = json.load(open(os.path.join(p, f)))
            out[d["gid"]] = d
    return out


w4 = load_dir("w4")
w4b = load_dir("w4b")

GROUPS = [("meow live", lambda r: r["group"] == "meow" and r["build"] == "live"),
          ("meow test", lambda r: r["group"] == "meow" and r["build"] == "test"),
          ("opponents", lambda r: r["group"] == "opp"),
          ("test4 (vs us)", lambda r: r["group"] == "opp" and r["team"] == Y.T4),
          ("WHQ (vs us)", lambda r: r["group"] == "opp" and r["team"] == Y.WHQ),
          ("forgot", lambda r: r["group"] == "forgot"),
          ("SSS", lambda r: r["group"] == "SSS"),
          ("Vibing++", lambda r: r["group"] == "Vibing++")]

pr("== 1. What is left unfed at the end of a race (medians): units | potential not in the longest (P - L) | of it within 15 cells of the longest | farther | share of P in the longest")
for cls, lab in ((False, "small maps"), (True, "big maps")):
    pr(" %s" % lab)
    for gname, pred in GROUPS:
        for wl, wlab in ((None, "all"), (True, "won"), (False, "lost")):
            rs = [r for r in races if pred(r) and r["big"] == cls and (wl is None or r["won"] == wl)]
            if len(rs) < 5:
                continue
            u = [R.snap(r, "end", "units") for r in rs]
            rest = [R.snap(r, "end", "P") - R.snap(r, "end", "L") for r in rs]
            near = [R.snap(r, "end", "Ploc") - R.snap(r, "end", "L") for r in rs]
            far = [a - b for a, b in zip(rest, near)]
            c = [R.snap(r, "end", "L") / R.snap(r, "end", "P") for r in rs if R.snap(r, "end", "P")]
            pr("   %-14s %-4s n=%3d | units %4.1f | unfed %5.1f | near %5.1f (mean %.1f) | far %5.1f (mean %.1f) | %.2f" % (
                gname, wlab, len(rs), Y.med(u), Y.med(rest), Y.med(near), Y.mean(near), Y.med(far), Y.mean(far), Y.med(c)))

pr("\n== 2. Our two longest dragons during feeding (races): longest minus second at rounds 400 / 425 / 450 / 475: share of races with a gap of 5 or less, 12 or less")
for gname, pred in GROUPS:
    for cls, lab in ((False, "small"), (True, "big")):
        rs = [r for r in races if pred(r) and r["big"] == cls]
        if not rs:
            continue
        cells = []
        for t in (400, 425, 450, 475):
            gaps = [R.snap(r, t, "L") - R.snap(r, t, "second") for r in rs if R.snap(r, t, "L") is not None and R.snap(r, t, "L") >= 8]
            if not gaps:
                cells.append("-")
                continue
            cells.append("%.0f%% / %.0f%% (median gap %s)" % (100 * sum(1 for x in gaps if x <= 5) / len(gaps),
                                                           100 * sum(1 for x in gaps if x <= 12) / len(gaps), Y.med(gaps)))
        pr("   %-14s %-5s %s" % (gname, lab, " | ".join(cells)))


# -----------------------------------------------------------------------------------------------------------------
def stubs_of(w, side):
    m = defaultdict(list)
    for row in w["lsplit"]:
        r, parent, child, before, plen, clen, s, fr, mx, seq = row
        if s == side and plen <= 3:
            m[parent].append(r)
    return m


def eat_index(w):
    m = defaultdict(list)
    for r, eater, dead in w["ceat"]:
        m[dead].append((r, eater))
    return m


def race_parts(r, lo=300):
    """Pearls dropped and pearls the final lineage got, per category of feeder death (see y_c5c.py)."""
    d4 = w4.get(r["gid"])
    w = r["w"]
    drop = [0] * 6
    got = [0] * 6
    if not d4:
        return drop, got
    readable = d4["ping"][0] >= 500 and d4["ping"][1] >= 0.95 * d4["ping"][0]
    st = stubs_of(w, r["side"])
    em = eat_index(w)
    fin = w["final"][r["side"]]
    chain = R.lineage(w, fin[0][1]) if fin else []
    for row in d4["rows"]:
        (rr, did, L, fr, bid, blen, bwhen, btrue, bman, bpath, bview,
         tl, tll, tlman, tlpath, vid, vlen, vman, vpath, nview, en) = row
        if rr < lo:
            continue
        if readable and bid >= 0 and bview == 1 and 0 <= bman <= 3:
            tid, tlen, tpath = bid, btrue, bpath
        elif vid >= 0:
            tid, tlen, tpath = vid, vlen, vpath
        else:
            tid = -1
        if tid < 0:
            c = 5
        elif tlen >= tll:
            c = 0 if 0 <= tpath <= 3 else 1
        elif tlen >= 2 * L:
            c = 2
        elif any(0 <= rr - x <= 26 for x in st.get(tid, [])):
            c = 3
        else:
            c = 4
        drop[c] += (L + 1) // 2
        for (er, e) in em.get(did, []):
            if chain and R.lineage_at(chain, er) == e:
                got[c] += 1
    return drop, got


def leader_cuts(rec, lo, hi):
    out = []
    for row in rec["w"]["lsplit"]:
        r, parent, child, before, plen, clen, side, fr, mx, seq = row
        if side == rec["side"] and before >= 8 and plen <= 3 and before >= mx and lo <= r <= hi:
            out.append(row)
    return out


pr("\n== 3. The size, on our lost races (the enemy unchanged; never above 0.9 of our final potential)")
TOT = [0] * 6
GOT = [0] * 6
per = []
for r in me:
    drop, got = race_parts(r)
    for i in range(6):
        TOT[i] += drop[i]
        GOT[i] += got[i]
    per.append((r, drop, got))
rate0 = GOT[0] / max(1, TOT[0])
pr("   over our 143 races, rounds 300-499: pearls of feeders dying next to the true longest %d, the final lineage ate %.0f%% of them;" % (TOT[0], 100 * rate0))
pr("   for a fresh stub %d (%.0f%%); for a dragon under twice their length %d (%.0f%%); across a wall %d (%.0f%%); for another big dragon %d (%.0f%%)" % (
    TOT[3], 100 * GOT[3] / max(1, TOT[3]), TOT[4], 100 * GOT[4] / max(1, TOT[4]), TOT[1], 100 * GOT[1] / max(1, TOT[1]),
    TOT[2], 100 * GOT[2] / max(1, TOT[2])))
pr("   per race: stub pearls %.1f, under-twice pearls %.1f, wall pearls %.1f, other-big-dragon pearls %.1f" % (
    TOT[3] / len(me), TOT[4] / len(me), TOT[1] / len(me), TOT[2] / len(me)))


def flips(rule, pool):
    out = []
    for r, drop, got in pool:
        if r["won"]:
            continue
        ours = R.snap(r, "end", "L")
        theirs = R.snap(r, "end", "L", False)
        cap = 0.9 * R.snap(r, "end", "P")
        gain = rule(r, drop, got)
        new = min(ours + gain, max(cap, ours))
        if new > theirs:
            out.append((r, gain, theirs - ours))
    return out


def g_strict(r, drop, got):
    # every stub and under-twice pearl goes to the true longest at the measured rate, plus the late-cut delay
    late = min(3, len(leader_cuts(r, 470, 499)))
    return rate0 * (drop[3] + drop[4]) - (got[3] + got[4]) + 1.2 * late


def g_mid(r, drop, got):
    # stub pearls go to the true longest; half of the under-twice feeders find it
    return rate0 * (drop[3] + 0.5 * drop[4]) - (got[3] + 0.5 * got[4])


def g_cautious(r, drop, got):
    # half of the stub feeders find the true longest; nothing else changes
    return 0.5 * (rate0 * drop[3] - got[3])


def g_wall(r, drop, got):
    return rate0 * drop[1] - got[1]


for name, rule in (("strict: all stub and under-twice pearls reach the true longest, +1.2 per leader cut after round 470", g_strict),
                   ("middle: stub pearls reach it, half of the under-twice ones", g_mid),
                   ("cautious: half of the stub pearls reach it", g_cautious),
                   ("for scale, not candidate 5: feeders that died across a wall from the longest die next to it instead", g_wall)):
    fl = flips(rule, per)
    live = [x for x in fl if x[0]["build"] == "live"]
    gains = [rule(r, d, g) for r, d, g in per if not r["won"]]
    pr("   %-100s -> lost races that turn: %d (live bot %d) | mean gain in lost races %.1f segments | vs test4 %d, WHQ %d, others %d | small maps %d, big %d" % (
        name, len(fl), len(live), Y.mean(gains), sum(1 for x in fl if x[0]["oteam"] == Y.T4),
        sum(1 for x in fl if x[0]["oteam"] == Y.WHQ), sum(1 for x in fl if x[0]["oteam"] not in (Y.T4, Y.WHQ)),
        sum(1 for x in fl if not x[0]["big"]), sum(1 for x in fl if x[0]["big"])))
    if fl:
        pr("        games: %s" % ", ".join("%s (gain %.1f, margin %d)" % (x[0]["gid"], x[1], x[2]) for x in fl[:14]))

pr("\n   A5's what-ifs recounted (theirs: growth after round 400 x1.25 / x1.5 / x2, capped at 0.9 P, only races with a leader cut after 395: 6 / 12 / 18; +5 / +10 / +15 segments: 4 / 11 / 20)")
for f in (1.25, 1.5, 2.0):
    n = nl = 0
    for r in me:
        if r["won"]:
            continue
        if not leader_cuts(r, 396, 499):
            continue
        L4 = R.snap(r, 400, "L")
        Le = R.snap(r, "end", "L")
        gain = max(0, Le - L4) * (f - 1)
        new = min(Le + gain, max(Le, 0.9 * R.snap(r, "end", "P")))
        if new > R.snap(r, "end", "L", False):
            n += 1
            nl += 1 if r["build"] == "live" else 0
    pr("   growth after 400 x%.2f: %d lost races turn (live bot %d)" % (f, n, nl))
for add in (2, 3, 5, 8, 10, 15):
    n = sum(1 for r in me if not r["won"] and R.snap(r, "end", "L") + add > R.snap(r, "end", "L", False))
    nw = sum(1 for r in me if r["won"] and R.snap(r, "end", "L") - add <= R.snap(r, "end", "L", False))
    pr("   our final longest +%d: %d lost races turn | for the other direction, our final longest -%d: %d of our 41 won races are lost" % (add, n, add, nw))
margins = sorted(R.snap(r, "end", "L", False) - R.snap(r, "end", "L") for r in me if not r["won"])
pr("   margins of our 102 lost races: %s ... median %s" % (margins[:25], Y.med(margins)))
wm = sorted(R.snap(r, "end", "L") - R.snap(r, "end", "L", False) for r in me if r["won"])
pr("   margins of our 41 won races: %s" % wm)

# -----------------------------------------------------------------------------------------------------------------
if w4b:
    pr("\n== 4. The 'see it is long' test on today's feeder deaths (rounds 300-499 of our races): the dying dragon must have min(2 x its length, 6) segments of its target in view")
    cnt = Counter()
    for r in me:
        d = w4b.get(r["gid"])
        if not d:
            continue
        for rr, did, L, tid, tlen, vis, islong, path in d["rows"]:
            if rr < 300:
                continue
            need = min(2 * L, 6)
            if tid < 0:
                k = "no target in view"
            elif islong:
                k = "target is the longest: " + ("passes" if vis >= need else "FAILS (too few segments in view)")
            elif tlen >= 2 * L:
                k = "target is another big dragon: " + ("passes" if vis >= need else "fails")
            else:
                k = "target under twice its length: " + ("passes" if vis >= need else "fails (as intended)")
            cnt[k] += 1
    tot = sum(cnt.values())
    for k, v in sorted(cnt.items()):
        pr("   %-70s %5d = %4.1f%%" % (k, v, 100.0 * v / tot))
OUTF.close()
