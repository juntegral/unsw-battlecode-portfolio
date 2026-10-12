#!/usr/bin/env python3
"""Candidate 2 ("our queen is never spent"): counts on the common footing.  Output: stdout -> h_out/c2.txt

Death kinds are sub-session A4's (d_tab.load(), d_haz.FAM, d_box.sub).  Parts of the candidate:
  a  core rule: no move that ends inside a visible enemy's reach when another exists  -> "ram: stepped in", "ram: stayed in"
  b  boxed in: shed 2 from the tail, never cut                                        -> boxed sub-kind "cut and stuck"
  c1 the queen never rams (on every map)                                              -> "own ram" with a free safe cell
  c2 the queen never takes a portal (on every map)                                    -> boxed deaths with a portal side on maps
                                                                                        of 600 cells or fewer (rules off today)
  c3 the queen never steps onto a cell with no way round                              -> "boxed: terrain dead end"
  d  team-mates keep off her last exit (NOT part of the candidate, shown for size)    -> nose to nose, team-mate's body, own child
1. Wins against losses, per team: how the own queen ended.
2. Our games by queen rules on / off (maps over / up to 600 cells): how the games end.
3. Each part: deaths, and expected wins gained under the strict and the two realistic readings (see h_joint.py).
"""
import json
import math
import os
import sys
from collections import Counter, defaultdict

sys.dont_write_bytecode = True
import d_box  # noqa: E402
import d_tab
from d_haz import FAM, FAMS

HERE = os.path.dirname(os.path.abspath(__file__))
BANDS4 = [(0, 50), (50, 100), (100, 300), (300, 500)]


def size(c):
    return "small" if c <= 700 else "medium" if c <= 1500 else "large"


def eband(x):
    return "<0.67" if x < 0.67 else "0.67-1" if x < 1 else "1-1.5" if x < 1.5 else ">1.5"


def part_of(x):
    """which part of candidate 2 this death belongs to (None = not touched)"""
    k = x["kind"]
    if k in ("ram: stepped in", "ram: stayed in"):
        return "a"
    if k == "own ram":
        T = x["det"]["T"]
        return "c1" if (T["nfree"] > 0 and T["nsafe"] > 0) else None
    if k.startswith("boxed"):
        name, info = d_box.sub(x)
        if name == "cut and stuck":
            return "b"
        if name == "terrain dead end":
            return "c3"
        if info["portal"] and x["cells"] <= 600:
            return "c2"
        if name in ("nose to nose", "team-mate's body", "own child on the exit"):
            return "d"
    return None


def main():
    recs = d_tab.load()
    base = {(str(r["gid"]), r["side"]): r for r in json.load(open(os.path.join(HERE, "h_out", "base.json")))}
    qcache = {}

    def q(gid):
        if gid not in qcache:
            qcache[gid] = json.load(open(os.path.join(HERE, "q", gid + ".json")))
        return qcache[gid]

    print("== 1. How the own queen ended, in wins and in losses (share of games) ==")
    for grp in ("meow", "meow live", "opp", "Vibing++", "SSS", "forgot"):
        for res in (True, False):
            xs = [x for x in recs if grp in x["groups"] and x["won"] == res]
            c = Counter("alive" if x["kind"] == "alive" else FAM[x["kind"]] for x in xs)
            n = len(xs)
            print(f"  {grp:10s} {'wins  ' if res else 'losses'} n={n:4d}  " + "  ".join(
                f"{k} {100 * c[k] / n:.0f}%" for k in ["alive"] + FAMS if c[k]))

    print("\n== 2. meow by queen rules (on = maps over 600 cells) ==")
    for grp in ("meow", "meow live"):
        for on in (True, False):
            xs = [x for x in recs if grp in x["groups"] and (x["cells"] > 600) == on]
            c = Counter(d_tab.outcome(x) for x in xs)
            alive = sum(x["kind"] == "alive" for x in xs)
            print(f"  {grp} rules {'on ' if on else 'off'}: {len(xs)} games, won {sum(x['won'] for x in xs)}, queen alive at the end {alive}; {dict(c)}")

    # ---- machinery of h_joint.py
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

    # our own death rates per part (not per family), by size class and round band
    expo = defaultdict(Counter)
    dead = defaultdict(Counter)
    for x in recs:
        if "meow" not in x["groups"]:
            continue
        sz = size(x["cells"])
        life = x["det"]["r"] if x["kind"] != "alive" else x["rounds"]
        for lo, hi in BANDS4:
            expo[sz][(lo, hi)] += max(0, min(life, hi) - lo)
        if x["kind"] != "alive":
            r = x["det"]["r"]
            for lo, hi in BANDS4:
                if lo <= r < hi:
                    dead[sz][(part_of(x) or "rest", (lo, hi))] += 1

    def p_own_rest(cells, removed, r):
        sz = size(cells)
        tot = 0.0
        for lo, hi in BANDS4:
            left = max(0, hi - max(lo, r))
            if not left or not expo[sz][(lo, hi)]:
                continue
            rate = sum(v for (p, band), v in dead[sz].items() if band == (lo, hi) and p not in removed) / expo[sz][(lo, hi)]
            tot += rate * left
        return math.exp(-tot)

    aa = [0, 0]
    for x in recs:
        if "meow" in x["groups"] and x["end"] != "wipe-out":
            b = base[(x["gid"], x["side"])]
            if b["my_fin"]["queen"] and b["op_fin"]["queen"]:
                aa[0] += 1
                aa[1] += x["won"]
    p_aa = aa[1] / aa[0]

    def evaluate(grp, parts):
        res = Counter()
        n = 0
        for x in recs:
            if grp not in x["groups"]:
                continue
            n += 1
            if x["kind"] == "alive":
                continue
            p = part_of(x)
            if p not in parts:
                continue
            res["deaths"] += 1
            res["deaths, rules off" if x["cells"] <= 600 else "deaths, rules on"] += 1
            if x["end"] == "wipe-out":
                res["... in wipe-out games"] += 1
                continue
            if x["won"]:
                res["... in round-500 wins"] += 1
                continue
            b = base[(x["gid"], x["side"])]
            oq = b["op_fin"]["queen"]
            r = x["det"]["r"]
            d = q(x["gid"])
            s = x["side"]
            o = "B" if s == "A" else "A"
            mine, theirs = d["sides"][s]["per"]["total"], d["sides"][o]["per"]["total"]
            ratio = mine[r] / theirs[r] if r < len(theirs) and theirs[r] else 1.0
            p2 = p_top(x["cells"], ratio, r)
            p3 = p_own_rest(x["cells"], parts, r)
            if not oq:
                res["... in round-500 losses with her queen dead (flip if ours lives)"] += 1
                res["strict"] += 1
                res["realistic, top-three survival"] += p2
                res["realistic, our own other death rates"] += p3
            else:
                res["... in round-500 losses with her queen alive"] += 1
                ql = d["sides"][s]["qdeath"]["len"]
                res["strict"] += 1 if ql > oq else 0
                res["realistic, top-three survival"] += p2 * p_aa
                res["realistic, our own other death rates"] += p3 * p_aa
        return n, res

    print("\n== 2b. Economy at the moment of death: own / enemy total length in the round our queen died, by part ==")
    for grp in ("meow", "meow live"):
        for name, parts in (("a core", ("a",)), ("b cut", ("b",)), ("c1 own ram", ("c1",)), ("cornered rams", None), ("all deaths", "all")):
            c = Counter()
            for x in recs:
                if grp not in x["groups"] or x["kind"] == "alive":
                    continue
                if parts == "all":
                    pass
                elif parts is None:
                    if FAM[x["kind"]] != "ram cornered":
                        continue
                elif part_of(x) not in parts:
                    continue
                d = q(x["gid"])
                s = x["side"]
                o = "B" if s == "A" else "A"
                r = x["det"]["r"]
                mine, theirs = d["sides"][s]["per"]["total"], d["sides"][o]["per"]["total"]
                units_m, units_t = d["sides"][s]["per"]["units"], d["sides"][o]["per"]["units"]
                if r >= len(theirs) or not theirs[r]:
                    continue
                c[eband(mine[r] / theirs[r])] += 1
                c["n"] += 1
                c["units own"] += units_m[r]
                c["units enemy"] += units_t[r]
                c["round"] += r
            n = max(1, c["n"])
            print(f"  {grp:9s} {name:14s} n={c['n']:3d}  ratio under 0.67: {c['<0.67']}, 0.67-1: {c['0.67-1']}, 1-1.5: {c['1-1.5']}, over 1.5: {c['>1.5']};"
                  f" mean units own {c['units own'] / n:.0f} vs enemy {c['units enemy'] / n:.0f}; mean round {c['round'] / n:.0f}")

    print("\n== 3. Each part of candidate 2 ==")
    cases = [("a   core: never end in a visible reach", ("a",)),
             ("b   shed, never cut", ("b",)),
             ("c1  never ram (free safe cell existed)", ("c1",)),
             ("c2  never a portal (boxed with a portal side, maps of 600 cells or fewer)", ("c2",)),
             ("c3  never onto a cell with no way round (terrain dead end)", ("c3",)),
             ("a+b", ("a", "b")),
             ("a+b+c1 (the candidate as proposed)", ("a", "b", "c1")),
             ("a+b+c1+c2", ("a", "b", "c1", "c2")),
             ("a+b+c1+c2+c3 (the whole candidate)", ("a", "b", "c1", "c2", "c3")),
             ("d   team-mates off her exit (not in the candidate)", ("d",)),
             ("everything she or her team controls (a-d)", ("a", "b", "c1", "c2", "c3", "d"))]
    for grp in ("meow", "meow live"):
        print(f"\n--- {grp}")
        for name, parts in cases:
            n, res = evaluate(grp, parts)
            print(f"  {name}: deaths {res['deaths']} (rules on {res['deaths, rules on']}, off {res['deaths, rules off']}); "
                  f"wipe-outs {res['... in wipe-out games']}, r500 wins {res['... in round-500 wins']}, "
                  f"r500 losses her dead {res['... in round-500 losses with her queen dead (flip if ours lives)']}, her alive {res['... in round-500 losses with her queen alive']}")
            print(f"       strict +{res['strict']:.0f} (+{100 * res['strict'] / n:.1f} pts) | top-three survival +{res['realistic, top-three survival']:.1f} "
                  f"(+{100 * res['realistic, top-three survival'] / n:.1f}) | our own other rates +{res['realistic, our own other death rates']:.1f} "
                  f"(+{100 * res['realistic, our own other death rates'] / n:.1f})")


if __name__ == "__main__":
    main()
