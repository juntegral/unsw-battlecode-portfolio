#!/usr/bin/env python3
"""Counterfactual accounting on OUR games (meow, opp elo >= 2000) and leader-kill rates for all four teams.

1. Round-500 losses by queen state, and how many would flip if (a) their queen had died, (b) their longest
   dragon had died in the last rounds, (c) our queen had lived. Uses end-of-game lengths only (a static what-if:
   it ignores everything the change would cost or trigger).
2. How often each team kills / loses a "leader" (the team's longest dragon, >= 15 long) to a ram, by phase.
Reads q/*.json.
"""
import glob
import json
from collections import Counter, defaultdict

TOP = {306: "Vibing++", 91: "SSS", 264: "forgot", 1119: "meow"}
SEALED = {"Schooltime"}
games = [json.load(open(f)) for f in glob.glob("q/*.json")]


def size(d):
    c = d["w"] * d["h"]
    return "small" if c <= 700 else "medium" if c <= 1500 else "large"


def sides(team):
    for d in games:
        for s in "AB":
            o = "B" if s == "A" else "A"
            if d["sides"][s]["team"] == team and (d["sides"][o]["elo"] or 0) >= 2000:
                yield d, s, o


print("=== 1. our round-500 games (sealed-queen map Schooltime excluded)")
tab = Counter()
flip = Counter()
ex = defaultdict(list)
n_all = 0
for d, s, o in sides(1119):
    n_all += 1
    if d["map"] in SEALED:
        tab["sealed map"] += 1
        continue
    if d["end_type"] == "wipe-out":
        tab["wipe-out " + ("W" if d["winner"] == s else "L")] += 1
        continue
    me, op = d["sides"][s], d["sides"][o]
    mq, oq = me["final"]["queen"], op["final"]["queen"]
    win = d["winner"] == s
    key = f"r500 ownQ={'alive' if mq else 'dead'} theirQ={'alive' if oq else 'dead'} {'W' if win else 'L'}"
    tab[key] += 1
    if win:
        continue
    my_long = me["final"]["longest"]
    op_long = op["final"]["longest"]
    op_second = op["per"]["second"][-1]
    # their best dragon if the queen is removed
    op_noq = op_second if oq and oq == op_long else op_long
    if not mq and oq:
        flip["(a) their queen dies -> we win on longest"] += my_long > op_noq
        flip["(a) base"] += 1
        flip["(a+b) their queen AND their longest non-queen die -> we win"] += my_long > min(op_noq, op_second)
        ex["a"].append((d["game_id"], d["map"], my_long, op_long, op_second, oq))
    if not mq and not oq:
        flip["(b) their longest dies at the end -> we win on longest"] += my_long > op_second
        flip["(b) base"] += 1
        flip["(c) our queen lives -> we win"] += 1
        ex["b"].append((d["game_id"], d["map"], my_long, op_long, op_second))
    if mq and oq:
        flip["(d) both alive: our queen shorter"] += 1
print("games vs >=2000:", n_all)
for k, v in sorted(tab.items()):
    print(f"  {k:45s} {v}")
print("what-if flips among our round-500 losses:")
for k, v in flip.items():
    print(f"  {k:62s} {v}")
print("  by map size for (b):", dict(Counter(size(next(g for g in games if g['game_id'] == e[0])) for e in ex["b"])))

print("\n=== 2. leader kills: a team's longest dragon (>= 15) killed by an ENEMY ram; per game, by phase")
for team, name in TOP.items():
    for sz in ("small", "medium", "large"):
        n = 0
        c = Counter()
        klen = Counter()
        for d, s, o in sides(team):
            if size(d) != sz:
                continue
            n += 1
            # headons: [r, att_team, att_id, att_len, steps_used, steps_req, vic_team, vic_id, vic_len, vic_queen, vic_longest, att_queen, manh]
            for h in d["headons"]:
                if h[1] == h[6] or not h[10] or h[8] < 15:
                    continue
                ph = "r<300" if h[0] < 300 else "r300-399" if h[0] < 400 else "r400-449" if h[0] < 450 else "r450+"
                if h[1] == s:
                    c["we kill " + ph] += 1
                    klen["2" if h[3] <= 2 else "3-4" if h[3] <= 4 else "5-9" if h[3] <= 9 else "10+"] += 1
                else:
                    c["we lose " + ph] += 1
        if n:
            print(f"{name:9s} {sz:6s} n={n:3d} " + " ".join(f"{k}={c[k] / n:.2f}" for k in (
                "we kill r<300", "we kill r300-399", "we kill r400-449", "we kill r450+",
                "we lose r<300", "we lose r300-399", "we lose r400-449", "we lose r450+")) + f" | killer len {dict(sorted(klen.items()))}")

print("\n=== 3. does a late leader kill decide round-500 'longest' games? (top-team games, both queens dead at the end)")
for team, name in TOP.items():
    res = Counter()
    for d, s, o in sides(team):
        if d["end_type"] != "longest" or d["map"] in SEALED:
            continue
        mine = any(h[1] == s and h[6] == o and h[10] and h[8] >= 20 and h[0] >= 400 for h in d["headons"])
        theirs = any(h[1] == o and h[6] == s and h[10] and h[8] >= 20 and h[0] >= 400 for h in d["headons"])
        key = "only we killed their leader" if mine and not theirs else "only they killed ours" if theirs and not mine else "both" if mine else "neither"
        res[key + (" W" if d["winner"] == s else " L")] += 1
    print(f"{name:9s} " + " | ".join(f"{k}: {v}" for k, v in sorted(res.items())))
