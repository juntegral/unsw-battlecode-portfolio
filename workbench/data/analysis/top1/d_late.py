#!/usr/bin/env python3
"""d_late.py: the live bot's queen splits after round 200 on maps over 600 cells (queen rules on), with the free
cells next to her head at that round (sub-session A4, check for question e).  From q/*.json."""
import csv
import json

LIVE = {"dl-20261003", "dl-20261004", "stride-old", "passage2-test-old", "qh31-test-old", "tc30-dev1-old"}
for g in csv.DictReader(open("games.csv")):
    if g["map"] == "Schooltime" or g["battle_id"] not in LIVE or int(g["cells"]) <= 600:
        continue
    for s in "AB":
        o = "B" if s == "A" else "A"
        if g[f"team{s}Id"] != "1119" or float(g[f"team{o}Elo"] or 0) < 2000:
            continue
        q = json.load(open(f"q/{g['game_id']}.json"))
        sd = q["sides"][s]
        per = sd["per"]["q"]
        for r, before, plen, clen in sd["qsplits"]:
            if r > 200:
                free = per[r][11] if r < len(per) and per[r] else None
                print(g["game_id"], g["map"], g["battle_id"], f"r{r} {before}->{plen}+{clen} free cells {free}")
