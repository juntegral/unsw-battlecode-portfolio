#!/usr/bin/env python3
"""d_prof.py <game_id>: time and profile d_class on one game (sub-session A4, helper)."""
import cProfile
import csv
import json
import os
import pstats
import sys
import time

import d_class
import lib

HERE = os.path.dirname(os.path.abspath(__file__))
gid = sys.argv[1]
row = [g for g in csv.DictReader(open(os.path.join(HERE, "games.csv"))) if g["game_id"] == gid][0]
q = json.load(open(os.path.join(HERE, "q", gid + ".json")))
deaths = {s: (q["sides"][s]["qdeath"]["round"] if q["sides"][s]["qdeath"] else None) for s in "AB"}
print(row["map"], row["cells"], "deaths", deaths)
t = time.time()
lib.Walk(row["replay_path"]).run(lib.Hooks())
print("plain walk %.2fs" % (time.time() - t))
h = d_class.H(deaths)
pr = cProfile.Profile()
t = time.time()
pr.enable()
lib.Walk(row["replay_path"]).run(h)
pr.disable()
print("with hooks %.2fs; enc rows A %d B %d; full turns A %d B %d" % (time.time() - t, len(h.enc["A"]), len(h.enc["B"]), len(h.turns["A"]), len(h.turns["B"])))
pstats.Stats(pr).sort_stats("cumulative").print_stats(14)
