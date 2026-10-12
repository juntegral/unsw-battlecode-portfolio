#!/usr/bin/env python3
"""Candidate 5, part (c): what do our feeders die next to? Reads y_out/w4 (our "no order" deaths), y_out/w1.
Output: y_out/c5c.txt

Our bot lets a feeder die when the head of the dragon in its leader record is in its 7x7 view and within 3 cells
(straight-line cells, walls ignored: `beside_visible_leader()`). So every such death has a target: in readable games
the id named one turn before, if that head is in view and within 3 cells; otherwise the longest own head in view
within 3 cells.
"""
import json
import os
from collections import Counter, defaultdict

import y_lib as Y
import y_r as R

OUTF = open(Y.out_path("c5c.txt"), "w")


def pr(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUTF.write(s + "\n")


w1 = R.load_w1()
recs = [r for r in R.sides(w1) if r["group"] == "meow"]
w4 = {}
for f in os.listdir(os.path.join(Y.OUT, "w4")):
    if f.endswith(".json"):
        d = json.load(open(os.path.join(Y.OUT, "w4", f)))
        w4[d["gid"]] = d

CATS = ["the longest, 3 path steps or fewer", "the longest, a wall between (over 3 path steps)",
        "another dragon twice its length", "the stub of a cut in the last 26 rounds", "a dragon under twice its length (no fresh stub)",
        "no own head in view within 3 cells"]


def stubs_of(w, side):
    """parent id -> list of rounds at which it kept 3 or fewer segments of a 6+ body"""
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


def analyse(rs, lo, hi, title, only_readable=False):
    cnt = Counter()
    pearls = Counter()
    lin = Counter()
    own = Counter()
    enemy = Counter()
    n = 0
    stale_len = 0
    named_known = 0
    named_is_target = 0
    lenbuckets = Counter()
    for r in rs:
        d4 = w4.get(r["gid"])
        if not d4:
            continue
        readable = d4["ping"][0] >= 500 and d4["ping"][1] >= 0.95 * d4["ping"][0]
        if only_readable and not readable:
            continue
        w = r["w"]
        st = stubs_of(w, r["side"])
        em = eat_index(w)
        fin = w["final"][r["side"]]
        chain = R.lineage(w, fin[0][1]) if fin else []
        team = w["team"]
        for row in d4["rows"]:
            (rr, did, L, fr, bid, blen, bwhen, btrue, bman, bpath, bview,
             tl, tll, tlman, tlpath, vid, vlen, vman, vpath, nview, en) = row
            if rr < lo or rr > hi:
                continue
            n += 1
            # target
            if readable and bid >= 0:
                named_known += 1
            if readable and bid >= 0 and bview == 1 and 0 <= bman <= 3:
                tid, tlen, tpath = bid, btrue, bpath
                named_is_target += 1
                if blen >= 2 * L and btrue < 2 * L:
                    stale_len += 1
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
            cnt[c] += 1
            drop = (L + 1) // 2
            pearls[c] += drop
            for (er, e) in em.get(did, []):
                if team.get(str(e)) != r["side"]:
                    enemy[c] += 1
                elif chain and R.lineage_at(chain, er) == e:
                    lin[c] += 1
                else:
                    own[c] += 1
            if c == 4:
                lenbuckets[(L, min(tlen, 9))] += 1
    pr("\n-- %s: %d deaths" % (title, n))
    if not n:
        return
    for c, name in enumerate(CATS):
        if not cnt[c]:
            continue
        p = max(1, pearls[c])
        pr("   %-52s %5d = %4.1f%% | pearls %5d: final lineage %3.0f%%, other own %3.0f%%, enemy %4.1f%%, nobody %3.0f%%" % (
            name, cnt[c], 100.0 * cnt[c] / n, pearls[c], 100.0 * lin[c] / p, 100.0 * own[c] / p, 100.0 * enemy[c] / p,
            100.0 * (p - lin[c] - own[c] - enemy[c]) / p))
    if named_known:
        pr("   readable part: the id named one turn before was in view within 3 cells in %s of deaths with a named id; of those the named length was twice its own while the true length was not in %s" % (
            Y.pct(named_is_target, named_known), Y.pct(stale_len, named_is_target)))
    if lenbuckets:
        top = lenbuckets.most_common(8)
        pr("   'under twice its length': (own length, target length) most often: %s" % ", ".join("(%d,%d) x%d" % (k[0], k[1], v) for k, v in top))


races = [r for r in recs if r["race"]]
analyse(races, 300, 499, "our races, rounds 300-499, all builds")
analyse([r for r in races if not r["big"]], 300, 499, "our races, small maps, rounds 300-499")
analyse([r for r in races if r["big"]], 300, 499, "our races, big maps, rounds 300-499")
analyse([r for r in races if r["build"] == "live"], 300, 499, "our races, live bot, rounds 300-499")
analyse([r for r in races if r["build"] == "test"], 300, 499, "our races, test builds, rounds 300-499")
analyse(races, 400, 499, "our races, rounds 400-499")
analyse(races, 300, 499, "our races with readable pings only, rounds 300-499", only_readable=True)
analyse(recs, 150, 499, "all our 401 games, rounds 150-499")
analyse([r for r in races if r["oteam"] == Y.T4], 300, 499, "our races against test4")
analyse([r for r in races if r["oteam"] == Y.WHQ], 300, 499, "our races against WHQ")
for mp in ("Maze", "Portals", "weakhold", "Default", "Trauma", "Queen Of Spades", "Slithery Fight", "Around UNSW", "Australia", "Islands"):
    analyse([r for r in races if r["map"] == mp], 300, 499, "our races on %s" % mp)
OUTF.close()
