#!/usr/bin/env python3
"""Why did extract.py fail on two games? Prints the traceback and the game row."""
import csv
import sys
import traceback

import extract
import lib

rows = {r["game_id"]: r for r in csv.DictReader(open("games.csv"))}
for gid in sys.argv[1:]:
    row = rows[gid]
    print(gid, row["map"], row["rounds"], row["teamAName"], row["teamAElo"], row["teamBName"], row["teamBElo"], row["end_type"], row["winner"])
    try:
        x = extract.X()
        lib.Walk(row["replay_path"]).run(x)
        print("  walked fine; rounds", x.rounds)
    except Exception:  # noqa: BLE001
        traceback.print_exc(limit=3, file=sys.stdout)
