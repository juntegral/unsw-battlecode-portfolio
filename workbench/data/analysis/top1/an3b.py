#!/usr/bin/env python3
"""Effect estimate from turn-level chances (q3) for OUR games, opp elo >= 2000, sealed map excluded.

"Cheap" chance = a legal ram on her that needs at most MAXPAID paid steps, by a dragon that is not our longest.
1. Games in which we had a cheap chance and never rammed her; what those games became.
2. Among our round-500 losses with their queen alive: how many had a cheap chance, and how many of those flip if she dies.
3. The same per map.
4. Pooled headline numbers for the report.
"""
import glob
import json
from collections import Counter, defaultdict

SEALED = {"Schooltime"}
Q = {}
for f in glob.glob("q/*.json"):
    d = json.load(open(f))
    if d["map"] not in SEALED:
        Q[d["game_id"]] = d
Q3 = {json.load(open(f))["game_id"]: f for f in glob.glob("q3/*.json")}


def chances(gid):
    return json.load(open(Q3[gid]))["chances"]


def cheap(c, maxpaid):
    n, steps = c[3], c[4]
    return max(0, steps - (-(-n // 4))) <= maxpaid and not c[7]


for maxpaid in (1, 2):
    print(f"=== cheap = at most {maxpaid} paid step(s), attacker not our longest")
    out = Counter()
    bymap = defaultdict(lambda: [0, 0])
    for gid, d in Q.items():
        for s in "AB":
            o = "B" if s == "A" else "A"
            if d["sides"][s]["team"] != 1119 or (d["sides"][o]["elo"] or 0) < 2000:
                continue
            ch = [c for c in chances(gid) if c[1] == s]
            ck = [c for c in ch if cheap(c, maxpaid)]
            qd = d["sides"][o]["qdeath"]
            killed = bool(qd and qd["reason"] == "headon" and qd["killer"] and qd["killer"]["team"] == s)
            out["games"] += 1
            out["games with a cheap chance"] += bool(ck)
            out["games with any chance"] += bool(ch)
            out["we rammed her"] += killed
            if ck and not killed:
                out["cheap chance, never rammed her"] += 1
                me, op = d["sides"][s], d["sides"][o]
                win = d["winner"] == s
                if d["end_type"] == "wipe-out":
                    out["  -> wipe-out " + ("W" if win else "L")] += 1
                    continue
                oq, mq = op["final"]["queen"], me["final"]["queen"]
                out[f"  -> r500, their queen {'alive' if oq else 'dead'} " + ("W" if win else "L")] += 1
                if oq and not win:
                    op_long, op_second = op["final"]["longest"], op["per"]["second"][-1]
                    op_noq = op_second if oq == op_long else op_long
                    flip = bool(mq) or me["final"]["longest"] > op_noq
                    out["     ... of those losses, flips if she had died"] += flip
                    bymap[d["map"]][0] += 1
                    bymap[d["map"]][1] += flip
    for k, v in out.items():
        print(f"  {k:50s} {v}")
    print("  round-500 losses with her alive and a cheap chance, by map (games, flips):", {m: tuple(v) for m, v in sorted(bymap.items())})

print("\n=== pooled headline (chance-turns)")
TOP = {306: "Vibing++", 91: "SSS", 264: "forgot", 1119: "meow"}
acc = defaultdict(lambda: [0, 0])
for gid, d in Q.items():
    for s in "AB":
        o = "B" if s == "A" else "A"
        t = d["sides"][s]["team"]
        if t not in TOP or (d["sides"][o]["elo"] or 0) < 2000:
            continue
        for c in chances(gid):
            if c[1] != s:
                continue
            n = c[3]
            paid = max(0, c[4] - (-(-n // 4)))
            keys = [(TOP[t], "len 2-3" if n <= 3 else "len 4+")]
            keys.append((TOP[t], "at most 1 paid step, not the longest" if paid <= 1 and not c[7] else "other"))
            keys.append((TOP[t], "at most 2 paid steps, not the longest" if paid <= 2 and not c[7] else "other2"))
            for k in keys:
                acc[k][0] += 1
                acc[k][1] += c[5]
for name in TOP.values():
    print(f"  {name:9s} " + " | ".join(f"{k}: {acc[(name, k)][1]}/{acc[(name, k)][0]} = {acc[(name, k)][1] / max(1, acc[(name, k)][0]):.2f}"
                                    for k in ("len 2-3", "len 4+", "at most 1 paid step, not the longest", "at most 2 paid steps, not the longest")))
