#!/usr/bin/env python3
"""c_mapsizes.py: the maps in games.csv with width, height, cells and size class, and whether our bot's
"aggressive" flag (cells <= 1200, AGGRESSIVE_MAX_CELLS in mybot2/main.cpp) is on for the map."""
import csv

seen = {}
for g in csv.DictReader(open("games.csv")):
    seen[g["map"]] = (int(g["cells"]), g["width"], g["height"], g["map_size"])
print("map | width x height | cells | size class | aggressive flag of our bot (cells <= 1200)")
for m, (cells, w, h, size) in sorted(seen.items(), key=lambda kv: -kv[1][0]):
    print(f"{m:18s} | {w:>2s} x {h:>2s} | {cells:5d} | {size:12s} | {'on' if cells <= 1200 else 'off'}")
