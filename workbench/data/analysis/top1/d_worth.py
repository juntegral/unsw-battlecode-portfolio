#!/usr/bin/env python3
"""d_worth.py: what each kind of queen death cost us, under three stated readings (sub-session A4, question g).

Only one kind of game can flip without changing anything else on the board: a round-500 loss in which BOTH queens
are dead (decided by the longest dragon).  Had our queen been alive at round 500, the queen rule gives us the game.
For every such loss, by the kind of our queen's death:
  reading 1 (strict)   she does not die that way and then lives to the end: the game flips (count of games).
  reading 2 (top three) she does not die that way and from that round on lives as often as a top-three queen that
                       is alive at that round, on that map-size class (700 cells or fewer / up to 1,500 / more) and
                       in that economy band (own / enemy total length at that round: under 0.67, 0.67-1, 1-1.5,
                       over 1.5).  Expected flips = sum of those probabilities.
  reading 3 (our own)  she does not die that way but stays exposed to every OTHER kind of death at our own rates
                       (deaths per round of the other kinds, by size class and round band 0-49 / 50-99 / 100-299 /
                       300-499, all 401 games).  Expected flips = sum of exp(-sum of rates x rounds left).
Not counted: round-500 losses with her queen alive (ours would also have to be longer), and wipe-outs.
Kinds are those of d_tab.py; families join them as in d_haz.py.  Output for all 401 games and for the live bot.
"""
import json
import math
import os
from collections import Counter, defaultdict

import d_tab
from d_haz import FAM, FAMS

HERE = os.path.dirname(os.path.abspath(__file__))
BANDS = [(0, 50), (50, 100), (100, 300), (300, 500)]


def size(c):
    return "small" if c <= 700 else "medium" if c <= 1500 else "large"


def eband(x):
    return "<0.67" if x < 0.67 else "0.67-1" if x < 1 else "1-1.5" if x < 1.5 else ">1.5"


def main():
    recs = d_tab.load()
    qcache = {}

    def q(gid):
        if gid not in qcache:
            qcache[gid] = json.load(open(os.path.join(HERE, "q", gid + ".json")))
        return qcache[gid]

    # ---- top-three survival: alive at the end given alive at round r, by size and economy band at r
    surv = defaultdict(lambda: [0, 0])
    for x in recs:
        if "top three" not in x["groups"]:
            continue
        d = q(x["gid"])
        s = x["side"]
        o = "B" if s == "A" else "A"
        mine, theirs = d["sides"][s]["per"]["total"], d["sides"][o]["per"]["total"]
        life = x["det"]["r"] if x["kind"] != "alive" else 10 ** 6
        alive_end = x["kind"] == "alive"
        for r in range(0, min(len(mine), len(theirs)), 25):
            if life <= r or not theirs[r] or not mine[r]:
                continue
            for key in ((size(x["cells"]), eband(mine[r] / theirs[r]), r), ("all", eband(mine[r] / theirs[r]), r), ("all", "all", r)):
                surv[key][0] += 1
                surv[key][1] += alive_end

    def p_top(cells, ratio, r):
        r0 = (r // 25) * 25
        for key in ((size(cells), eband(ratio), r0), ("all", eband(ratio), r0), ("all", "all", r0)):
            n, k = surv[key]
            if n >= 20:
                return k / n
        return 0.0

    # ---- our own rates by family, size class and round band
    expo = defaultdict(Counter)
    dead = defaultdict(Counter)
    for x in recs:
        if "meow" not in x["groups"]:
            continue
        sz = size(x["cells"])
        life = x["det"]["r"] if x["kind"] != "alive" else x["rounds"]
        for lo, hi in BANDS:
            expo[sz][(lo, hi)] += max(0, min(life, hi) - lo)
        if x["kind"] != "alive":
            r = x["det"]["r"]
            for lo, hi in BANDS:
                if lo <= r < hi:
                    dead[sz][(FAM[x["kind"]], (lo, hi))] += 1

    def p_own(cells, fam, r):
        sz = size(cells)
        tot = 0.0
        for lo, hi in BANDS:
            left = max(0, hi - max(lo, r))
            if not left or not expo[sz][(lo, hi)]:
                continue
            rate = sum(dead[sz][(f, (lo, hi))] for f in FAMS if f != fam) / expo[sz][(lo, hi)]
            tot += rate * left
        return math.exp(-tot)

    OWN = ("ram stepped/stayed in", "boxed bodies", "boxed terrain", "own ram")

    def p_bundle(cells, r):
        """survival to round 500 from round r if only cornered, unseen and 'other' deaths remain, at our own rates"""
        sz = size(cells)
        tot = 0.0
        for lo, hi in BANDS:
            left = max(0, hi - max(lo, r))
            if not left or not expo[sz][(lo, hi)]:
                continue
            rate = sum(dead[sz][(f, (lo, hi))] for f in FAMS if f not in OWN) / expo[sz][(lo, hi)]
            tot += rate * left
        return math.exp(-tot)

    for grp in ("meow", "meow live"):
        b1 = b2 = b3 = 0.0
        nb = 0
        for x in recs:
            if grp not in x["groups"]:
                continue
            nb += 1
            if x["kind"] == "alive" or FAM[x["kind"]] not in OWN:
                continue
            if x["end"] == "wipe-out" or x["won"] or x["oq_alive"]:
                continue
            d = q(x["gid"])
            s = x["side"]
            o = "B" if s == "A" else "A"
            r = x["det"]["r"]
            mine, theirs = d["sides"][s]["per"]["total"], d["sides"][o]["per"]["total"]
            ratio = mine[r] / theirs[r] if r < len(theirs) and theirs[r] else 1.0
            b1 += 1
            b2 += p_top(x["cells"], ratio, r)
            b3 += p_bundle(x["cells"], r)
        print(f"\n===== {grp}: the four families she controls herself together (stepped/stayed in, boxed by bodies, terrain, own ram): "
              f"reading 1 {b1:.0f} flips (+{100 * b1 / nb:.1f} points), reading 2 {b2:.1f} (+{100 * b2 / nb:.1f}), "
              f"reading 3 with only cornered and unseen rams left at our own rates {b3:.1f} (+{100 * b3 / nb:.1f})")

    for grp in ("meow", "meow live"):
        rows = Counter()
        flips1 = Counter()
        flips2 = defaultdict(float)
        flips3 = defaultdict(float)
        n = 0
        listing = defaultdict(list)
        for x in recs:
            if grp not in x["groups"]:
                continue
            n += 1
            if x["kind"] == "alive":
                continue
            fam = FAM[x["kind"]]
            rows[fam] += 1
            if x["end"] == "wipe-out" or x["won"] or x["oq_alive"]:
                continue
            d = q(x["gid"])
            s = x["side"]
            o = "B" if s == "A" else "A"
            r = x["det"]["r"]
            mine, theirs = d["sides"][s]["per"]["total"], d["sides"][o]["per"]["total"]
            ratio = mine[r] / theirs[r] if r < len(theirs) and theirs[r] else 1.0
            flips1[fam] += 1
            p2 = p_top(x["cells"], ratio, r)
            p3 = p_own(x["cells"], fam, r)
            flips2[fam] += p2
            flips3[fam] += p3
            listing[fam].append((x["gid"], x["map"], r, round(ratio, 2), round(p2, 2), round(p3, 2)))
        wins = sum(1 for x in recs if grp in x["groups"] and x["won"])
        print(f"\n===== {grp}: {n} games, {wins} won ({100 * wins / n:.1f}%)")
        print("family of death | deaths | round-500 losses with both queens dead (reading 1: flips if she lives to the end) | reading 2: expected flips, top-three survival | reading 3: expected flips, our own other rates | in points of win rate (1 / 2 / 3)")
        for fam in FAMS:
            print(f"{fam} | {rows[fam]} | {flips1[fam]} | {flips2[fam]:.1f} | {flips3[fam]:.1f} | +{100 * flips1[fam] / n:.1f} / +{100 * flips2[fam] / n:.1f} / +{100 * flips3[fam] / n:.1f}")
        print(f"all | {sum(rows.values())} | {sum(flips1.values())} | {sum(flips2.values()):.1f} | {sum(flips3.values()):.1f} | +{100 * sum(flips1.values()) / n:.1f} / +{100 * sum(flips2.values()) / n:.1f} / +{100 * sum(flips3.values()) / n:.1f}")
        if grp == "meow":
            print("\nthe games (game, map, death round, own / enemy total length then, reading-2 probability, reading-3 probability):")
            for fam in FAMS:
                print(f"  {fam}: " + "; ".join(f"{g} {m} r{r} x{ra} {p2}/{p3}" for g, m, r, ra, p2, p3 in sorted(listing[fam], key=lambda t: t[1])))
    print("\ntop-three survival to the end, given alive at round r (all sizes; by economy band): r, n, share alive at the end")
    for band in ("<0.67", "0.67-1", "1-1.5", ">1.5", "all"):
        print(f"  {band}: " + " | ".join(f"r{r} {surv[('all', band, r)][1]}/{surv[('all', band, r)][0]}={100 * surv[('all', band, r)][1] / max(1, surv[('all', band, r)][0]):.0f}%" for r in (0, 50, 100, 150, 200, 300, 400)))
    for sz in ("small", "medium", "large"):
        print(f"  {sz}, all bands: " + " | ".join(
            f"r{r} {100 * sum(surv[(sz, b, r)][1] for b in ('<0.67', '0.67-1', '1-1.5', '>1.5')) / max(1, sum(surv[(sz, b, r)][0] for b in ('<0.67', '0.67-1', '1-1.5', '>1.5'))):.0f}%"
            for r in (0, 50, 100, 150, 200, 300, 400)))


if __name__ == "__main__":
    main()
