#!/usr/bin/env python3
"""d_ramdet.py: details of the rammed deaths by kind and group (sub-session A4, questions a and b).

For each kind of ram (see d_tab.py) and each group: the free and safe one-step moves she had on her last turn, whether
she began that turn inside a visible enemy's reach, whether she ended next to an enemy head, whether she ate on the
move, the killer's length, for how many of her turns in a row the killer's head had been in her view, own heads
within 3 path steps, and for the unseen rams how far away the killer started (Chebyshev) and whether any part of
its body was in her view.  Reads d_out/cls through d_tab.load().
"""
from collections import Counter, defaultdict

import d_tab

GROUPS = ["meow", "meow live", "opp", "forgot", "SSS", "Vibing++", "top three"]
KINDS = ["ram: stepped in", "ram: stayed in", "ram: cornered", "ram: unseen"]


def dist(c, keys):
    return "/".join(str(c[k]) for k in keys)


def main():
    recs = d_tab.load()
    for kind in KINDS:
        print(f"\n===== {kind}")
        for grp in GROUPS:
            xs = [x for x in recs if grp in x["groups"] and x["kind"] == kind]
            if not xs:
                continue
            n = len(xs)
            free = Counter(min(x["det"]["T"]["nfree"], 3) for x in xs)
            safe = Counter(min(x["det"]["T"]["nsafe"], 3) for x in xs)
            inr0 = sum(x["det"]["T"]["reach0"] > 0 for x in xs)
            adj = sum(x["det"]["T"].get("end_reach", 0) == 1 for x in xs)
            ate = sum(x["det"]["T"]["ate"] > 0 for x in xs)
            split = sum(x["det"]["T"]["kind"] != 0 for x in xs)
            ksmall = sum(x["det"]["k"]["len"] <= 3 for x in xs)
            k4 = sum(x["det"]["k"]["len"] == 4 for x in xs)
            a3 = sum(x["det"]["T"]["a3"] > 0 for x in xs)
            paid = sum(x["det"]["T"]["nsafe_paid"] > 0 for x in xs)
            run = Counter()
            for x in xs:
                kid = x["det"]["k"]["id"]
                c = 0
                for t in reversed(x["sd"]["turns"]):
                    if any(row[0] == kid and row[6] for row in t["en"]):
                        c += 1
                    else:
                        break
                run["1" if c <= 1 else "2" if c == 2 else "3-5" if c <= 5 else "6+"] += 1
            line = (f"  {grp:9s} n={n:3d} | free steps 0/1/2/3: {dist(free, range(4))} | safe steps 0/1/2/3: {dist(safe, range(4))} | began inside reach {inr0} ({100 * inr0 // n}%)"
                    f" | ended next to an enemy head {adj} ({100 * adj // n}%) | ate on the move {ate} | split instead of moving {split} | killer 3 or shorter {ksmall} ({100 * ksmall // n}%), 4 long {k4}"
                    f" | own head within 3 steps {a3} ({100 * a3 // n}%) | a paid move would have been safe {paid}")
            if kind != "ram: unseen":
                line += f" | killer in view for 1/2/3-5/6+ turns in a row: {dist(run, ('1', '2', '3-5', '6+'))}"
            else:
                nv = sum(x["det"]["T"]["nvis"] == 0 for x in xs)
                born = sum(x["det"]["k"]["born"] for x in xs)
                far = Counter(min(x["det"]["k"]["cheb_now"], 6) for x in xs)
                body = 0
                for x in xs:
                    kid = x["det"]["k"]["id"]
                    body += any(row[0] == kid and len(row) > 9 and row[9] for row in x["det"]["T"]["en"])
                seen3 = sum(x["det"]["k"]["seen_last3"] for x in xs)
                klen = Counter("2-3" if x["det"]["k"]["len"] <= 3 else "4" if x["det"]["k"]["len"] == 4 else "5-9" if x["det"]["k"]["len"] <= 9 else "10+" for x in xs)
                line += (f" | nothing at all in her view {nv} | killer born that round {born} | killer's start, Chebyshev distance to where she died 1/2/3/4/5/6+: {dist(far, range(1, 7))}"
                         f" | part of the killer's body in her view {body} | its head was in her view within her last 3 turns {seen3} | killer length 2-3/4/5-9/10+: {dist(klen, ('2-3', '4', '5-9', '10+'))}")
            print(line)
    # how good was the safe step she did not take?
    print("\n===== stepped in / stayed in: the safe step she did not take")
    print("  'roomy' = the cell is not a tree cell and at least (her length + 2) body-free cells can be reached from it; 'no portal' = the step does not cross a portal")
    for kind in ("ram: stepped in", "ram: stayed in"):
        for grp in GROUPS + ["meow live rules on", "meow live rules off"]:
            if grp.startswith("meow live rules"):
                on = grp.endswith("on")
                xs = [x for x in recs if "meow live" in x["groups"] and x["kind"] == kind and (x["cells"] > 600) == on]
            else:
                xs = [x for x in recs if grp in x["groups"] and x["kind"] == kind]
            c = Counter()
            for x in xs:
                T = x["det"]["T"]
                L = T["len"]
                safe = [s for s in T["sides"] if s[0] in "FP" and s[4] == 0]
                roomy = [s for s in safe if not s[7] and s[8] >= L + 2]
                noportal = [s for s in roomy if not s[3]]
                c["n"] += 1
                c["roomy"] += bool(roomy)
                c["roomy no portal"] += bool(noportal)
                c["only into a pocket"] += not roomy
                c["only through a portal"] += bool(roomy) and not noportal
                c["her length 6+"] += L >= 6
            if c["n"]:
                print(f"  {kind} | {grp:20s} n={c['n']:3d} | a roomy safe step existed {c['roomy']} | ... that did not cross a portal {c['roomy no portal']} | "
                      f"the only safe step led into a pocket or dead end {c['only into a pocket']} | the only roomy safe step crossed a portal {c['only through a portal']} | queen 6 or longer {c['her length 6+']}")
    # cornered: the shape of the corner
    print("\n===== ram: cornered, the corner: free steps x began inside reach or not")
    for grp in GROUPS:
        xs = [x for x in recs if grp in x["groups"] and x["kind"] == "ram: cornered"]
        c = Counter()
        for x in xs:
            T = x["det"]["T"]
            c[(min(T["nfree"], 3), "in" if T["reach0"] > 0 else "out")] += 1
        print(f"  {grp:9s} n={len(xs):3d} | " + " | ".join(f"free {f} began {io}side reach: {c[(f, io)]}" for f in range(4) for io in ("out", "in")))


if __name__ == "__main__":
    main()
