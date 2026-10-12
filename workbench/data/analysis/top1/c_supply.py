#!/usr/bin/env python3
"""c_supply.py <map name> [max_games=60] [jobs=4]: where natural pearls appear on a map, pooled over many replays.

A replay hides each tile's spawn gap, so the supply is counted: for every tile the number of natural pearls that
appeared on it per game (a pearl dropped right after a death event is a corpse pearl and is not counted).
Writes c_out/supply_<map>.json: {"games": n, "w":, "h":, "cells": {"x,y": appearances summed over the games},
"first": {"x,y": mean round of the first appearance}} and prints the classes and an ASCII map
(per-game rate: '#' 40+, '8' 20-39, '4' 10-19, '2' 5-9, '1' 2-4, '.' under 2, ' ' never).
"""
import csv
import json
import sys
from collections import Counter
from multiprocessing import Pool

sys.dont_write_bytecode = True
import lib  # noqa: E402
from lib import rp  # noqa: E402


def scan(path):
    root = rp.load(path).root()
    cnt = Counter()
    first = {}
    rnd = -1
    after_death = False
    for event in root.pointer(3):
        kind = event.u16(0)
        if kind == 12 or kind == 9 or kind == 1 or kind == 4:
            if kind != 12:
                after_death = False
            continue
        p = event.pointer(0)
        if kind == 0:
            rnd = p.i32(0)
            after_death = False
        elif kind == 11:
            after_death = True
        elif kind == 3:
            if p.bit(0):
                if not after_death and rnd >= 0:
                    cell = rp.point(p.pointer(0))
                    cnt[cell] += 1
                    first.setdefault(cell, rnd)
            else:
                after_death = False
        else:
            after_death = False
    return cnt, first


if __name__ == "__main__":
    name = sys.argv[1]
    maxg = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    jobs = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    games = [g for g in csv.DictReader(open("games.csv")) if g["map"].lower() == name.lower()]
    games = games[:: max(1, len(games) // maxg)][:maxg]
    w, h = int(games[0]["width"]), int(games[0]["height"])
    total = Counter()
    firsts = {}
    with Pool(jobs) as pool:
        for cnt, first in pool.imap_unordered(scan, [g["replay_path"] for g in games]):
            total.update(cnt)
            for c, r in first.items():
                firsts.setdefault(c, []).append(r)
    rounds = sum(int(g["rounds"]) for g in games)
    n = rounds / 500.0      # games of 500 rounds
    key = name.lower().replace(" ", "_")
    json.dump({"games": n, "w": w, "h": h, "cells": {f"{x},{y}": v for (x, y), v in total.items()},
               "first": {f"{x},{y}": round(sum(v) / len(v), 1) for (x, y), v in firsts.items()}},
              open(f"c_out/supply_{key}.json", "w"))
    rate = {c: v / n for c, v in total.items()}
    classes = Counter()
    mass = Counter()
    for c, r in rate.items():
        k = "40+" if r >= 40 else "20-39" if r >= 20 else "10-19" if r >= 10 else "5-9" if r >= 5 else "2-4" if r >= 2 else "<2"
        classes[k] += 1
        mass[k] += r
    allmass = sum(rate.values())
    print(f"=== SUPPLY {name} {w}x{h} = {w * h} cells | {len(games)} games, {rounds} rounds = {n:.1f} games of 500 rounds | natural pearls appearing per 500 rounds {allmass:.0f} | tiles that ever spawned {len(rate)}")
    for k in ("40+", "20-39", "10-19", "5-9", "2-4", "<2"):
        print(f"   tiles with {k:>5s} appearances per game: {classes[k]:4d} tiles, {mass[k]:6.0f} pearls per game ({100 * mass[k] / max(1, allmass):.0f}%)")
    print("   map (x across, y down):")
    print("      " + "".join(str(x // 10 % 10) if x % 10 == 0 else " " for x in range(w)))
    for y in range(h):
        line = []
        for x in range(w):
            r = rate.get((x, y))
            line.append(" " if r is None else "#" if r >= 40 else "8" if r >= 20 else "4" if r >= 10 else "2" if r >= 5 else "1" if r >= 2 else ".")
        print(f"   {y:2d} " + "".join(line))
