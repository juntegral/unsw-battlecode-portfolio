#!/usr/bin/env python3
"""Print selected rows of e_out/c_leader.txt (made by e_c.py) for the 'all such games' block of each group, so that
the leader's place and habits can be compared across groups in one screen.
Usage: python3 e_cx.py"""
import os

import e_lib as E

KEYS = ("own queen's start", "portals separate", "cells within 4", "own heads within 15", "path steps from the team's heads to it: median",
        "steps it took", "natural pearls it ate", "corpse pearls it ate", "end: longest", "losses in which", "died when 15+", "length of the enemy",
        "Manhattan distance to the nearest enemy", "median length lost")
part = ""
show = False
for line in open(os.path.join(E.HERE, "e_out", "c_leader.txt")):
    line = line.rstrip("\n")
    if line.startswith("====="):
        part = "SMALL" if "OR FEWER" in line else "BIG"
        continue
    if line.startswith("--- "):
        show = "all such games" in line and not line.startswith("--- top3") and "vs top3" not in line and not line.startswith("--- meow |")
        if show:
            print("\n%s %s" % (part, line[:70]))
        continue
    if show and any(k in line for k in KEYS):
        print(line[:170])
