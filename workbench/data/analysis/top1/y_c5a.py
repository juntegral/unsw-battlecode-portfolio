#!/usr/bin/env python3
"""Candidate 5, counts from walk 1 (positions only, all games). Output: y_out/c5a.txt

A "leader cut" = a split in which a side's longest dragon (8 or longer) keeps 2-3 segments and hands the rest to a
new dragon (the "heir"); the 2-3 segments that keep the old id are the "stub".
A death "by choice" = not a ram, and the dragon had a free cell next to its head when it gave its order.
1. Leader cuts per race, by phase; share made with a free cell.
2. Growth of the side's longest dragon per 25-round window from round 400 (windows that start with 10+ other own
   dragons), with a cut in the window or in the 25 rounds before against without; then the same split finer:
   cut inside the window / cut only in the 25 rounds before / none in 50 rounds; with the 2 segments per cut given
   back; inside the same game; as a share of what was left to feed.
3. Deaths by choice in races, rounds 300-499: next to the longest / another dragon twice as long / such a dragon at
   4-8 steps / nothing; and how many of the "nothing" deaths are next to a fresh stub; who ate the pearls.
4. The clock after a cut: deaths by choice within 3 steps of the side's longest, per 100 side-rounds, by rounds
   since the side's last leader cut.
5. Event study: the side's longest dragon from 30 rounds before a cut to 40 after.
"""
import math
from collections import defaultdict

import y_lib as Y
import y_r as R

OUTF = open(Y.out_path("c5a.txt"), "w")


def pr(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUTF.write(s + "\n")


w1 = R.load_w1()
allrecs = R.sides(w1)
races = [r for r in allrecs if r["race"]]

GROUPS = [("meow live", lambda r: r["group"] == "meow" and r["build"] == "live"),
          ("meow test", lambda r: r["group"] == "meow" and r["build"] == "test"),
          ("meow all", lambda r: r["group"] == "meow"),
          ("opponents", lambda r: r["group"] == "opp"),
          ("test4 (vs us)", lambda r: r["group"] == "opp" and r["team"] == Y.T4),
          ("WHQ (vs us)", lambda r: r["group"] == "opp" and r["team"] == Y.WHQ),
          ("forgot", lambda r: r["group"] == "forgot"),
          ("SSS", lambda r: r["group"] == "SSS"),
          ("Vibing++", lambda r: r["group"] == "Vibing++")]


def leader_cuts(rec, lo=0, hi=999):
    """Leader cuts of this side: rows of lsplit with before>=8, keeps<=3, parent was the side's longest."""
    out = []
    for row in rec["w"]["lsplit"]:
        r, parent, child, before, plen, clen, side, fr, mx, seq = row
        if side != rec["side"] or before < 8 or plen > 3 or before < mx:
            continue
        if lo <= r <= hi:
            out.append(row)
    return out


def units_at(rec, rnd):
    return R.snap(rec, rnd, "units")


# -------------------------------------------------------------------------------------------------------------
pr("== 1. Leader cuts per race (theirs, table C1: live small 2.3 / 3.8, 68% with a free cell; big 3.1 / 3.9, 67%;")
pr("      opponents 2.6 / 2.3, 40%; 2.5 / 2.5, 37%; forgot 1.0 / 4.1, 15%; SSS 1.6 / 2.0, 93%; Vibing++ 3.4 / 2.6, 61%)")
for cls, lab in ((False, "small maps"), (True, "big maps")):
    pr(" %s: group | races | cuts per race in rounds 300-394 / 395-499 | of the cuts from 395: with a free cell | races with 0 / 1-2 / 3-5 / 6+ cuts from 395" % lab)
    for gname, pred in GROUPS:
        rs = [r for r in races if pred(r) and r["big"] == cls]
        if not rs:
            continue
        a = [len(leader_cuts(r, 300, 394)) for r in rs]
        b = [leader_cuts(r, 395, 499) for r in rs]
        nb = sum(len(x) for x in b)
        free = sum(1 for x in b for row in x if row[7] >= 1)
        dist = [sum(1 for x in b if lo <= len(x) <= hi) for lo, hi in ((0, 0), (1, 2), (3, 5), (6, 999))]
        pr("   %-14s %3d | %.1f / %.1f | %s | %s" % (gname, len(rs), Y.mean(a), nb / len(rs), Y.pct(free, nb), dist))

pr("\n   Final-lineage cuts from round 400 (theirs: meow 2.7 a race, 1.7 with a free cell; opponents 2.0 / 0.8; forgot 3.3 / 0.3; SSS 1.6 / 1.6; Vibing++ 2.0 / 1.2)")
pr("   and lost races in which the segments left behind in those cuts exceed the losing margin (theirs: meow 10 of 102; top three 25 of 181)")
for gname, pred in GROUPS:
    rs = [r for r in races if pred(r)]
    if not rs:
        continue
    tot = vol = seg = 0
    lost = turn = turnv = 0
    for r in rs:
        w = r["w"]
        fin = w["final"][r["side"]]
        if not fin:
            continue
        chain = R.lineage(w, fin[0][1])
        ids = {}
        for did, frm in chain:
            ids[did] = frm
        s_all = s_vol = 0
        for row in w["lsplit"]:
            rr, parent, child, before, plen, clen, side, fr, mx, seq = row
            if side != r["side"] or rr < 400 or plen > 3 or before < 8:
                continue
            if child in ids:   # the child continues the lineage: the parent keeps plen segments
                tot += 1
                s_all += plen
                if fr >= 1:
                    vol += 1
                    s_vol += plen
        seg += s_all
        if not r["won"]:
            lost += 1
            margin = R.snap(r, "end", "L", False) - R.snap(r, "end", "L", True)
            if s_all > margin:
                turn += 1
            if s_vol > margin:
                turnv += 1
    pr("   %-14s races %3d | cuts %.1f a race, with a free cell %.1f | segments left %.1f a race | lost %d, cuts exceed the margin in %d (free-cell cuts alone %d)" % (
        gname, len(rs), tot / len(rs), vol / len(rs), seg / len(rs), lost, turn, turnv))

# -------------------------------------------------------------------------------------------------------------
pr("\n== 2. Growth of the longest per 25-round window from round 400 (windows starting with 10+ other own dragons)")
pr("   theirs: meow 5.0 (291 windows) with a cut in it or in the 25 rounds before, 10.8 (91) without; live 4.5 / 11.4; test 6.1 / 9.3;")
pr("   vs test4 4.9 / 11.4; vs WHQ 5.5 / 10.9; others 3.7 / 9.6; small 6.0 / 12.4; big 4.3 / 8.7; opponents 6.0 (216) / 6.9 (156)")
WIN = (400, 425, 450, 475)


def windows(rec):
    """Rows: dict per window with growth, cut classes, units, L, P."""
    out = []
    cuts = leader_cuts(rec, 300, 499)
    for t in WIN:
        u = units_at(rec, t)
        if u is None or u < 11:
            continue
        L0 = R.snap(rec, t, "L")
        L1 = R.snap(rec, t + 25 if t + 25 < 500 else "end", "L")
        if L0 is None or L1 is None:
            continue
        inside = [c for c in cuts if t <= c[0] < t + 25]
        before = [c for c in cuts if t - 25 <= c[0] < t]
        P0 = R.snap(rec, t, "P")
        out.append(dict(t=t, g=L1 - L0, n_in=len(inside), n_bef=len(before), L0=L0, P0=P0, u=u, rec=rec,
                        seg_in=sum(c[4] for c in inside), free_in=sum(1 for c in inside if c[7] >= 1)))
    return out


def wsum(ws):
    if not ws:
        return "-"
    return "%.1f (%d)" % (Y.mean([w["g"] for w in ws]), len(ws))


WG = [("meow all", lambda r: r["group"] == "meow"),
      ("meow live", lambda r: r["group"] == "meow" and r["build"] == "live"),
      ("meow test", lambda r: r["group"] == "meow" and r["build"] == "test"),
      ("meow vs test4", lambda r: r["group"] == "meow" and r["oteam"] == Y.T4),
      ("meow vs WHQ", lambda r: r["group"] == "meow" and r["oteam"] == Y.WHQ),
      ("meow vs others", lambda r: r["group"] == "meow" and r["oteam"] not in (Y.T4, Y.WHQ)),
      ("meow small", lambda r: r["group"] == "meow" and not r["big"]),
      ("meow big", lambda r: r["group"] == "meow" and r["big"]),
      ("meow live small", lambda r: r["group"] == "meow" and r["build"] == "live" and not r["big"]),
      ("meow test small", lambda r: r["group"] == "meow" and r["build"] == "test" and not r["big"]),
      ("opponents", lambda r: r["group"] == "opp"),
      ("opponents small", lambda r: r["group"] == "opp" and not r["big"]),
      ("opponents big", lambda r: r["group"] == "opp" and r["big"]),
      ("test4 (vs us)", lambda r: r["group"] == "opp" and r["team"] == Y.T4),
      ("WHQ (vs us)", lambda r: r["group"] == "opp" and r["team"] == Y.WHQ),
      ("forgot small", lambda r: r["group"] == "forgot" and not r["big"]),
      ("forgot big", lambda r: r["group"] == "forgot" and r["big"]),
      ("SSS small", lambda r: r["group"] == "SSS" and not r["big"]),
      ("SSS big", lambda r: r["group"] == "SSS" and r["big"]),
      ("Vibing++ small", lambda r: r["group"] == "Vibing++" and not r["big"]),
      ("Vibing++ big", lambda r: r["group"] == "Vibing++" and r["big"])]

ALLW = {}
pr("   group            | with a cut (in it or 25 before) | without | cut INSIDE the window | cut only in the 25 rounds BEFORE | none in 50 rounds | inside, 2 per cut given back")
for gname, pred in WG:
    ws = [w for r in races if pred(r) for w in windows(r)]
    ALLW[gname] = ws
    withc = [w for w in ws if w["n_in"] or w["n_bef"]]
    without = [w for w in ws if not (w["n_in"] or w["n_bef"])]
    inside = [w for w in ws if w["n_in"]]
    befonly = [w for w in ws if not w["n_in"] and w["n_bef"]]
    back = [dict(g=w["g"] + w["seg_in"]) for w in inside]
    pr("   %-16s | %-12s | %-12s | %-12s | %-12s | %-12s | %s" % (gname, wsum(withc), wsum(without), wsum(inside),
                                                                 wsum(befonly), wsum(without), wsum(back)))

pr("\n   By run of ours (theirs, era.txt: ladder 4 Oct 4.3 / 11.9; stride 3.8 / 10.4; passage2 5.1 / 9.2; qh31 5.3 / 14.1)")
runs = sorted(set(r["battle"] for r in races if r["group"] == "meow"))
for b in runs:
    ws = [w for r in races if r["group"] == "meow" and r["battle"] == b for w in windows(r)]
    withc = [w for w in ws if w["n_in"] or w["n_bef"]]
    without = [w for w in ws if not (w["n_in"] or w["n_bef"])]
    inside = [w for w in ws if w["n_in"]]
    befonly = [w for w in ws if not w["n_in"] and w["n_bef"]]
    pr("   %-20s with %-11s without %-11s | inside %-11s before-only %-11s" % (b, wsum(withc), wsum(without), wsum(inside), wsum(befonly)))

pr("\n   What kind of window is which? means at the window start: longest / potential / units / what is left to feed (P - L); and growth as a share of what is left")
for gname in ("meow all", "meow small", "meow big", "opponents", "SSS small", "forgot small", "Vibing++ small", "SSS big", "forgot big", "Vibing++ big"):
    ws = ALLW[gname]
    for lab, sub in (("cut inside", [w for w in ws if w["n_in"]]), ("cut before only", [w for w in ws if not w["n_in"] and w["n_bef"]]),
                     ("no cut", [w for w in ws if not (w["n_in"] or w["n_bef"])])):
        if not sub:
            continue
        left = [w["P0"] - w["L0"] for w in sub]
        share = sum(w["g"] for w in sub) / max(1, sum(left))
        shareb = sum(w["g"] + w["seg_in"] for w in sub) / max(1, sum(left))
        pr("   %-15s %-16s n=%3d longest %.1f potential %.1f units %.1f left %.1f | growth %.1f = %.0f%% of what is left (%.0f%% with the cut segments given back)" % (
            gname, lab, len(sub), Y.mean([w["L0"] for w in sub]), Y.mean([w["P0"] for w in sub]), Y.mean([w["u"] for w in sub]),
            Y.mean(left), Y.mean([w["g"] for w in sub]), 100 * share, 100 * shareb))

pr("\n   By the length of the longest at the window start (meow; a short leader cannot cut and is just starting): growth with a cut inside / before only / none")
for lo, hi in ((0, 7), (8, 14), (15, 24), (25, 39), (40, 999)):
    for gname in ("meow all", "opponents", "SSS small", "SSS big", "forgot small", "Vibing++ small"):
        ws = [w for w in ALLW[gname] if lo <= w["L0"] <= hi]
        pr("   L %2d-%-3d %-15s inside %-11s before-only %-11s none %-11s" % (
            lo, hi, gname, wsum([w for w in ws if w["n_in"]]), wsum([w for w in ws if not w["n_in"] and w["n_bef"]]),
            wsum([w for w in ws if not (w["n_in"] or w["n_bef"])])))

pr("\n   Inside the same game: races that have both kinds of window (mean of per-game means)")
for gname in ("meow all", "meow live", "meow test", "opponents", "SSS small", "SSS big", "forgot small", "forgot big", "Vibing++ small", "Vibing++ big"):
    by = defaultdict(lambda: [[], [], []])
    for w in ALLW[gname]:
        k = 0 if w["n_in"] else (1 if w["n_bef"] else 2)
        by[w["rec"]["gid"]][k].append(w["g"])
    d_in, d_bef, d_any = [], [], []
    for gid, (a, b, c) in by.items():
        if c and a:
            d_in.append(Y.mean(c) - Y.mean(a))
        if c and b:
            d_bef.append(Y.mean(c) - Y.mean(b))
        if c and (a or b):
            d_any.append(Y.mean(c) - Y.mean(a + b))
    def ms(x):
        if not x:
            return "-"
        m = Y.mean(x)
        sd = (sum((v - m) ** 2 for v in x) / max(1, len(x) - 1)) ** 0.5
        return "%+.1f (se %.1f, %d games)" % (m, sd / math.sqrt(len(x)), len(x))
    pr("   %-15s no-cut minus any-cut %s | minus cut-inside %s | minus cut-before-only %s" % (gname, ms(d_any), ms(d_in), ms(d_bef)))

# -------------------------------------------------------------------------------------------------------------
pr("\n== 3. Deaths by choice in races, rounds 300-499 (theirs, 'the same test for every team': live small 33.2 a race: 42 / 16 / 17 / 26%, lineage eats 36%;")
pr("      test 44 / 16 / 15 / 25%, 45%; live big 30 / 36 / 14 / 20%, 27%; opponents small 42 / 26 / 16 / 15%, 39%; forgot 51 / 25 / 17 / 8%; SSS 73 / 14 / 3 / 10%; Vibing++ 35 / 18 / 33 / 14%)")


def choice_deaths(rec, lo=300, hi=499):
    out = []
    for d in rec["w"]["deaths"]:
        r, did, side, reason, L, hx, hy, actor, fr, lid, llen, dl, near, en = d
        if side != rec["side"] or r < lo or r > hi or reason == "headon" or fr < 1:
            continue
        out.append(d)
    return out


def classify(d):
    r, did, side, reason, L, hx, hy, actor, fr, lid, llen, dl, near, en = d
    if 0 <= dl <= 3:
        return 0
    if any(n[1] >= 2 * L and n[2] <= 3 for n in near):
        return 1
    if any(n[1] >= 2 * L and n[2] <= 8 for n in near):
        return 2
    return 3


def eaters(w):
    """dead id -> list of eater ids"""
    m = defaultdict(list)
    for r, eater, dead in w["ceat"]:
        m[dead].append((r, eater))
    return m


EAT = {}


def pearl_fate(rec, deaths):
    """Counts of pearls: dropped, eaten by final lineage, other own, enemy."""
    w = rec["w"]
    if rec["gid"] not in EAT:
        EAT[rec["gid"]] = eaters(w)
    em = EAT[rec["gid"]]
    fin = w["final"][rec["side"]]
    chain = R.lineage(w, fin[0][1]) if fin else []
    team = w["team"]
    drop = lin = own = enemy = 0
    for d in deaths:
        drop += (d[4] + 1) // 2
        for (rr, e) in em.get(d[1], []):
            if team.get(str(e)) != rec["side"]:
                enemy += 1
            elif chain and R.lineage_at(chain, rr) == e:
                lin += 1
            else:
                own += 1
    return drop, lin, own, enemy


for cls, lab in ((False, "small maps"), (True, "big maps")):
    pr(" %s: group | races | deaths by choice a race | next to the longest / another twice as long / such at 4-8 steps / nothing | of 'nothing': next to a stub of a cut in the last 26 rounds | pearls a race | final lineage / other own / enemy / nobody" % lab)
    for gname, pred in GROUPS:
        rs = [r for r in races if pred(r) and r["big"] == cls]
        if not rs:
            continue
        cnt = [0, 0, 0, 0]
        stubn = 0
        fate = [0, 0, 0, 0]
        fate_by = [[0, 0, 0, 0] for _ in range(4)]
        n = 0
        for r in rs:
            ds = choice_deaths(r)
            n += len(ds)
            cuts = leader_cuts(r, 250, 499)
            bycls = [[], [], [], []]
            for d in ds:
                c = classify(d)
                cnt[c] += 1
                bycls[c].append(d)
                if c == 3:
                    stubs = set(row[1] for row in cuts if 0 <= d[0] - row[0] <= 26)
                    if any(nn[0] in stubs and nn[2] <= 3 for nn in d[12]):
                        stubn += 1
            f = pearl_fate(r, ds)
            for i in range(4):
                fate[i] += f[i]
            for c in range(4):
                fc = pearl_fate(r, bycls[c])
                for i in range(4):
                    fate_by[c][i] += fc[i]
        drop = fate[0]
        pr("   %-14s %3d | %.1f | %.0f%% / %.0f%% / %.0f%% / %.0f%% | %s | %.1f | %.0f%% / %.0f%% / %.1f%% / %.0f%%" % (
            gname, len(rs), n / len(rs), 100 * cnt[0] / n, 100 * cnt[1] / n, 100 * cnt[2] / n, 100 * cnt[3] / n,
            Y.pct(stubn, cnt[3]), drop / len(rs), 100 * fate[1] / drop, 100 * fate[2] / drop, 100 * fate[3] / drop,
            100 * (drop - fate[1] - fate[2] - fate[3]) / drop))
        pr("   %-14s       lineage's share by where the death was (longest / another / 4-8 / nothing): %s" % (
            "", " / ".join("%.0f%%" % (100 * fate_by[c][1] / max(1, fate_by[c][0])) for c in range(4))))

# -------------------------------------------------------------------------------------------------------------
pr("\n== 4. The clock after a cut. Rounds 400-499 of races, sides with 10+ other own dragons at the round's 25-round mark.")
pr("   Deaths by choice within 3 path steps of the side's longest dragon (which must be twice the dying dragon's length), per 100 side-rounds,")
pr("   by rounds since the side's last leader cut. If a stale record holds our feeders back for 25 rounds, our rate is low until 25 and jumps after.")
TB = [(0, 4), (5, 9), (10, 14), (15, 19), (20, 24), (25, 29), (30, 39), (40, 59), (60, 999)]


def clock(rs, lo=400, hi=499, need_units=11):
    expo = defaultdict(int)
    hit = defaultdict(int)
    hit_any = defaultdict(int)
    hit_none = defaultdict(int)
    for r in rs:
        cuts = sorted(c[0] for c in leader_cuts(r, 250, 499))
        ok = {}
        for t in range(lo, hi + 1):
            base = t - t % 25
            u = units_at(r, base)
            ok[t] = (u is not None and u >= need_units)
        def since(t):
            last = None
            for c in cuts:
                if c <= t:
                    last = c
                else:
                    break
            return None if last is None else t - last
        for t in range(lo, hi + 1):
            if not ok[t]:
                continue
            s = since(t)
            expo["none" if s is None else s] += 1
        for d in choice_deaths(r, lo, hi):
            if not ok[d[0]]:
                continue
            s = since(d[0])
            k = "none" if s is None else s
            c = classify(d)
            hit_any[k] += 1
            if c == 0 and d[10] >= 2 * d[4]:
                hit[k] += 1
            if c == 3:
                hit_none[k] += 1
    return expo, hit, hit_any, hit_none


def clock_row(gname, rs):
    expo, hit, hit_any, hit_none = clock(rs)
    cells = []
    for lo, hi in TB:
        e = sum(v for k, v in expo.items() if k != "none" and lo <= k <= hi)
        h = sum(v for k, v in hit.items() if k != "none" and lo <= k <= hi)
        a = sum(v for k, v in hit_any.items() if k != "none" and lo <= k <= hi)
        cells.append("%5.1f/%5.1f" % (100.0 * h / e, 100.0 * a / e) if e >= 40 else "    -      ")
    e = expo.get("none", 0)
    cells.append("%5.1f/%5.1f" % (100.0 * hit.get("none", 0) / e, 100.0 * hit_any.get("none", 0) / e) if e >= 40 else "    -      ")
    pr("   %-16s %s" % (gname, " ".join(cells)))


pr("   (each cell: deaths next to the longest / all deaths by choice, per 100 side-rounds)")
pr("   %-16s %s" % ("rounds since cut", " ".join("%11s" % ("%d-%d" % b if b[1] < 999 else "60+") for b in TB) + "     no cut yet"))
for gname, pred in WG:
    clock_row(gname, [r for r in races if pred(r)])

# -------------------------------------------------------------------------------------------------------------
pr("\n== 5. Event study: the side's longest dragon around a leader cut made in rounds 395-460 with 10+ other own dragons")
pr("   (mean length of the side's longest at 5-round marks; 0 = the last mark at or before the cut; 'lone' = no other leader cut of the side from 25 rounds before to 30 after)")
OFFS = (-25, -20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40)


def event_rows(rs, lone):
    rows = []
    for r in rs:
        cuts = leader_cuts(r, 250, 499)
        for c in cuts:
            if not (395 <= c[0] <= 460):
                continue
            base = c[0] - c[0] % 5
            u = units_at(r, base)
            if u is None or u < 11:
                continue
            others = [x for x in cuts if x is not c and -25 <= x[0] - c[0] <= 30]
            if lone and others:
                continue
            prof = []
            for o in OFFS:
                t = base + o
                v = R.snap(r, t if t < 500 else "end", "L") if t <= 500 else None
                prof.append(v)
            rows.append((prof, c, r))
    return rows


for lone in (False, True):
    pr("   %s cuts: group | cuts | %s" % ("lone" if lone else "all", " ".join("%5d" % o for o in OFFS)))
    for gname, pred in WG:
        rows = event_rows([r for r in races if pred(r)], lone)
        if len(rows) < 8:
            continue
        cells = []
        for i in range(len(OFFS)):
            v = [p[0][i] for p in rows if p[0][i] is not None]
            cells.append("%5.1f" % Y.mean(v) if len(v) >= 5 else "    -")
        pr("   %-16s %4d | %s" % (gname, len(rows), " ".join(cells)))
OUTF.close()
