#!/usr/bin/env python3
"""d_shed.py: does shedding 2 from the tail save a boxed-in queen? (sub-session A4, question h, second repair)

From q/*.json.  A "boxed episode" is a run of consecutive rounds in which the queen split with no free cell next to
her head (kinds as in d_cut.py: shed = she keeps 3 or more and the child gets 2-3; cut = she keeps 2-3 of 6 or
more).  Round-0 episodes (a queen that starts coiled) are shown apart.  For each team: episodes by the kind of their
first split, how long they lasted, her length before and after, and whether she was alive 5 and 20 rounds after
the last split of the episode.
"""
import csv
import json
from collections import Counter, defaultdict

T = {"1119": "meow", "306": "Vibing++", "91": "SSS", "264": "forgot"}
tab = defaultdict(Counter)
for g in csv.DictReader(open("games.csv")):
    if g["map"] == "Schooltime":
        continue
    q = None
    for s in "AB":
        o = "B" if s == "A" else "A"
        groups = []
        if g[f"team{s}Id"] in T and g[f"team{o}Elo"] and float(g[f"team{o}Elo"]) >= 2000:
            groups.append(T[g[f"team{s}Id"]])
        if g[f"team{o}Id"] == "1119" and g[f"team{s}Elo"] and float(g[f"team{s}Elo"]) >= 2000:
            groups.append("opp")
        if not groups:
            continue
        if q is None:
            q = json.load(open(f"q/{g['game_id']}.json"))
        sd = q["sides"][s]
        per = sd["per"]["q"]
        qd = sd["qdeath"]
        boxed = []
        for r, before, plen, clen in sd["qsplits"]:
            free = per[r][11] if r < len(per) and per[r] else None
            if free == 0 and before >= 6:
                kind = "cut" if plen <= 3 else "shed" if clen <= 3 else "other"
                boxed.append((r, before, plen, kind))
        eps = []
        for r, before, plen, kind in boxed:
            if eps and r - eps[-1][-1][0] <= 1:
                eps[-1].append((r, before, plen, kind))
            else:
                eps.append([(r, before, plen, kind)])
        for ep in eps:
            first, last = ep[0], ep[-1]
            when = "round 0" if first[0] == 0 else "later"
            alive5 = not qd or qd["round"] > last[0] + 5
            alive20 = not qd or qd["round"] > last[0] + 20
            for grp in groups:
                c = tab[(grp, first[3], when)]
                c["n"] += 1
                c["rounds"] += len(ep)
                c["before"] += first[1]
                c["after"] += last[2]
                c["alive5"] += alive5
                c["alive20"] += alive20
print("team | first split of the episode | when | episodes | mean rounds | mean length before | mean length after | alive 5 rounds later | alive 20 rounds later")
for grp in ("meow", "opp", "forgot", "SSS", "Vibing++"):
    for kind in ("cut", "shed", "other"):
        for when in ("round 0", "later"):
            c = tab[(grp, kind, when)]
            if c["n"]:
                n = c["n"]
                print(f"{grp} | {kind} | {when} | {n} | {c['rounds'] / n:.1f} | {c['before'] / n:.1f} | {c['after'] / n:.1f} | {c['alive5']} ({100 * c['alive5'] // n}%) | {c['alive20']} ({100 * c['alive20'] // n}%)")
