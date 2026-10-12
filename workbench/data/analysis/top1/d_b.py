#!/usr/bin/env python3
"""d_b.py: avoidable or not (sub-session A4, question b).  Reads d_out/cls/*.json through d_tab.load().

Part 1  rammed deaths: the queen's last six own turns (offset 0 = her last turn before the ram).  Per offset: was an
        enemy head in her view, was the later killer in her view, free one-step moves, one-step moves that end
        outside the reach of every visible enemy head ("safe"), where she ended.
Part 2  share of rammed deaths with a safe step on the last turn / on any of the last three turns.
Part 3  EVERY queen turn of every game with an enemy head in view (not only the fatal ones): what she does when a safe
        step exists, how often she steps nearer to a visible small enemy head (4 or shorter) when both a nearer and a
        farther one-step move exist, and how often a turn that ends inside reach is punished by a ram that round.
Reach model and "in view": see d_class.py.  Distances to a small enemy head are path distances with kelp and portals
respected and bodies ignored, the enemy taken where it stood at the start of her turn.
"""
import sys
from collections import Counter, defaultdict

import d_tab

GROUPS = ["meow", "meow live", "meow live rules on", "meow live rules off", "meow vs test4/WHQ", "cand passage2", "cand qh31", "cand stride",
          "cand tc30", "opp", "forgot", "SSS", "Vibing++", "top three", "top three vs test4/WHQ"]


def groups_of(x):
    gs = [g for g in x["groups"] if not g.startswith("run ")]
    if "meow live" in gs:
        gs.append("meow live rules on" if x["cells"] > 600 else "meow live rules off")
    return gs


def pct(a, b):
    return f"{100 * a / b:.0f}%" if b else "-"


def main():
    recs = d_tab.load()
    # ---------- part 1 and 2
    print("=== 1. rammed deaths: her last six own turns (offset 0 = last turn before the ram)")
    print("group | offset | deaths with that turn on record | enemy head in view | later killer in view | mean free steps | mean safe steps | "
          "a safe step existed (of turns with an enemy in view) | ended inside reach of a visible enemy | ...although a safe step existed | she split or gave no move")
    p2 = defaultdict(Counter)
    for grp in GROUPS:
        xs = [x for x in recs if grp in groups_of(x) and x["kind"].startswith("ram")]
        for off in range(6):
            n = vis = kvis = free = safe = safe_n = had = inr = inr_av = nomove = 0
            for x in xs:
                turns = x["sd"]["turns"]
                if len(turns) <= off:
                    continue
                t = turns[-1 - off]
                kid = x["det"]["k"]["id"]
                n += 1
                free += t["nfree"]
                if t["nvis"]:
                    vis += 1
                    safe += t["nsafe"]
                    safe_n += 1
                    had += t["nsafe"] > 0
                    e = t.get("end_reach", 0) > 0
                    inr += e
                    inr_av += e and t["nsafe"] > 0
                kvis += any(row[0] == kid and row[6] for row in t["en"])
                nomove += t["kind"] != 0
            if n:
                print(f"{grp} | {off} | {n} | {vis} ({pct(vis, n)}) | {kvis} ({pct(kvis, n)}) | {free / n:.2f} | {safe / safe_n if safe_n else 0:.2f} | "
                      f"{had} ({pct(had, vis)}) | {inr} ({pct(inr, vis)}) | {inr_av} ({pct(inr_av, vis)}) | {nomove}")
        for x in xs:
            turns = x["sd"]["turns"]
            kid = x["det"]["k"]["id"]
            c = p2[grp]
            c["n"] += 1
            last = turns[-1]
            kin = lambda t: any(row[0] == kid and row[6] for row in t["en"])
            c["last: killer in view"] += kin(last)
            c["last: killer in view and a safe step"] += kin(last) and last["nsafe"] > 0
            c["last: killer in view, safe step only by paying segments"] += kin(last) and last["nsafe"] == 0 and last["nsafe_paid"] > 0
            l3 = turns[-3:]
            c["last 3: killer in view at some turn and a safe step then"] += any(kin(t) and t["nsafe"] > 0 for t in l3)
            c["last 3: ended a move inside a visible enemy's reach although a safe step existed"] += any(
                t["nvis"] and t["nsafe"] > 0 and t.get("end_reach", 0) > 0 for t in l3)
            c["last 6: the same"] += any(t["nvis"] and t["nsafe"] > 0 and t.get("end_reach", 0) > 0 for t in turns[-6:])
            c["last 3: any enemy head in view"] += any(t["nvis"] for t in l3)
            c["last 6: any enemy head in view"] += any(t["nvis"] for t in turns[-6:])
            c["last 6: killer in view at some turn"] += any(kin(t) for t in turns[-6:])
            c["killer in view 3+ turns before the ram"] += any(kin(t) for t in turns[:-2][-10:])
    print("\n=== 2. rammed deaths: was there a way out")
    keys = [k for k in p2["meow"] if k != "n"]
    print("measure | " + " | ".join(GROUPS))
    print("rammed deaths | " + " | ".join(str(p2[g]["n"]) for g in GROUPS))
    for k in keys:
        print(f"{k} | " + " | ".join(f"{p2[g][k]} ({pct(p2[g][k], p2[g]['n'])})" for g in GROUPS))

    # ---------- part 3: every turn with an enemy head in view
    print("\n=== 3. every queen turn with an enemy head in view (whole games)")
    tab = defaultdict(Counter)
    for x in recs:
        gs = groups_of(x)
        sd = x["sd"]
        rows = sd["enc"] + [t for t in sd["turns"] if t["nvis"]]
        for t in rows:
            for grp in gs:
                c = tab[grp]
                c["turns"] += 1
                L = t["len"]
                small = t["nvis_small"] > 0
                c["turns, small enemy in view"] += small
                e = t.get("end_reach", 0) > 0
                rammed = t["fate"] == "rammed"
                c["rammed that round"] += rammed
                if t["nfree"] == 0:
                    c["boxed"] += 1
                    continue
                if t["nsafe"] > 0:
                    key = "out" if t["reach0"] == 0 else "in"
                    c[f"{key}: n"] += 1
                    c[f"{key}: ended in reach"] += e
                    c[f"{key}: ended in reach and rammed"] += e and rammed
                    c[f"{key}: ended in reach, ate on the move"] += e and t["ate"] > 0
                    c[f"{key}: ended next to an enemy head"] += t.get("end_reach", 0) == 1
                    c[f"{key}: ended safe and rammed anyway"] += (not e) and rammed
                    if L <= 3:
                        c[f"{key} L2-3: n"] += 1
                        c[f"{key} L2-3: ended in reach"] += e
                else:
                    c["nosafe: n"] += 1
                    c["nosafe: rammed"] += rammed
                    c["nosafe: a paid move would be safe"] += t["nsafe_paid"] > 0
                c["ended in reach"] += e
                c["ended in reach and rammed"] += e and rammed
                # nearer or farther from the nearest visible small enemy head
                if small and t["d0_small"] > 0 and t["kind"] == 0 and t.get("end_dsmall", -1) >= 0:
                    rel = t["rel"]
                    if rel[0] > 0 and rel[2] > 0:
                        d0 = t["d0_small"]
                        b = "2" if d0 <= 2 else "3" if d0 == 3 else "4" if d0 == 4 else "5+"
                        nearer = t["end_dsmall"] < d0
                        for kk in ("all", b):
                            c[f"choice {kk}: n"] += 1
                            c[f"choice {kk}: nearer"] += nearer
                        if nearer:
                            c["choice all: nearer and ate"] += t["ate"] > 0
    cols = GROUPS
    print("measure | " + " | ".join(cols))

    def line(name, f):
        print(f"{name} | " + " | ".join(f(tab[g]) for g in cols))

    line("queen turns with an enemy head in view", lambda c: str(c["turns"]))
    line("... with a small enemy head (4 or shorter) in view", lambda c: str(c["turns, small enemy in view"]))
    line("... boxed (no free step)", lambda c: str(c["boxed"]))
    line("A. began OUTSIDE every visible reach, a safe step existed: turns", lambda c: str(c["out: n"]))
    line("A. ended inside a visible enemy's reach", lambda c: f"{c['out: ended in reach']} ({100 * c['out: ended in reach'] / max(1, c['out: n']):.1f}%)")
    line("A. ... queen 2-3 long only", lambda c: f"{c['out L2-3: ended in reach']} of {c['out L2-3: n']} ({100 * c['out L2-3: ended in reach'] / max(1, c['out L2-3: n']):.1f}%)")
    line("A. ... and ate a pearl on that move", lambda c: f"{c['out: ended in reach, ate on the move']} ({pct(c['out: ended in reach, ate on the move'], c['out: ended in reach'])})")
    line("A. ... and was rammed that round", lambda c: f"{c['out: ended in reach and rammed']} ({pct(c['out: ended in reach and rammed'], c['out: ended in reach'])})")
    line("A. ended on the cell next to an enemy head", lambda c: f"{c['out: ended next to an enemy head']} ({100 * c['out: ended next to an enemy head'] / max(1, c['out: n']):.1f}%)")
    line("B. began INSIDE a visible reach, a safe step existed: turns", lambda c: str(c["in: n"]))
    line("B. ended inside reach again", lambda c: f"{c['in: ended in reach']} ({pct(c['in: ended in reach'], c['in: n'])})")
    line("B. ... queen 2-3 long only", lambda c: f"{c['in L2-3: ended in reach']} of {c['in L2-3: n']} ({pct(c['in L2-3: ended in reach'], c['in L2-3: n'])})")
    line("B. ... and was rammed that round", lambda c: f"{c['in: ended in reach and rammed']} ({pct(c['in: ended in reach and rammed'], c['in: ended in reach'])})")
    line("C. no safe one-step move: turns", lambda c: str(c["nosafe: n"]))
    line("C. rammed that round", lambda c: f"{c['nosafe: rammed']} ({pct(c['nosafe: rammed'], c['nosafe: n'])})")
    line("C. a paid (multi-step) move would have been safe", lambda c: f"{c['nosafe: a paid move would be safe']} ({pct(c['nosafe: a paid move would be safe'], c['nosafe: n'])})")
    line("all: turns that ended inside reach", lambda c: str(c["ended in reach"]))
    line("all: ... rammed that round", lambda c: f"{c['ended in reach and rammed']} ({pct(c['ended in reach and rammed'], c['ended in reach'])})")
    line("ended on a 'safe' cell and rammed anyway (A+B)", lambda c: str(c["out: ended safe and rammed anyway"] + c["in: ended safe and rammed anyway"]))
    line("choice: a nearer and a farther step both existed (small enemy in view): turns", lambda c: str(c["choice all: n"]))
    line("choice: she stepped nearer", lambda c: f"{c['choice all: nearer']} ({pct(c['choice all: nearer'], c['choice all: n'])})")
    for b in ("2", "3", "4", "5+"):
        line(f"choice, small enemy {b} path steps away: stepped nearer", lambda c, b=b: f"{c[f'choice {b}: nearer']} of {c[f'choice {b}: n']} ({pct(c[f'choice {b}: nearer'], c[f'choice {b}: n'])})")
    line("choice: nearer steps that ate a pearl", lambda c: f"{c['choice all: nearer and ate']} ({pct(c['choice all: nearer and ate'], c['choice all: nearer'])})")


if __name__ == "__main__":
    main()
