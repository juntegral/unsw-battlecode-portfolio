#!/usr/bin/env python3
"""c_batch.py <upto> <from> [jobs=4] [--teams 1119,264,91,306] [--sizes large,medium,small] [--skip-existing]:
run c_econ.py on every game of the given teams against 2000+ opponents (Schooltime left out) and keep only the JSON
(c_out/ec_<id>_<from>_<upto>.json). The text tables are not kept; run c_econ.py by hand for a game you want to read.
"""
import csv
import os
import subprocess
import sys
import time
from multiprocessing import Pool

args = sys.argv[1:]
upto, start = args[0], args[1]
jobs = int(args[2]) if len(args) > 2 and args[2].isdigit() else 4
teams = {1119, 264, 91, 306}
sizes = {"large", "medium", "small"}
if "--teams" in args:
    teams = {int(x) for x in args[args.index("--teams") + 1].split(",")}
if "--sizes" in args:
    sizes = set(args[args.index("--sizes") + 1].split(","))
skip = "--skip-existing" in args


def run(gid):
    out = f"c_out/ec_{gid}_{start}_{upto}.json"
    if skip and os.path.exists(out):
        return gid, 0
    r = subprocess.run(["nice", "python3", "c_econ.py", gid, upto, start], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    return gid, r.returncode if r.returncode == 0 else r.stderr.decode()[-300:]


if __name__ == "__main__":
    todo = []
    for g in csv.DictReader(open("games.csv")):
        if g["map"] == "Schooltime":
            continue
        size = "small" if g["map_size"].startswith("small") else "medium" if g["map_size"].startswith("medium") else "large"
        if size not in sizes:
            continue
        ok = False
        for s in "AB":
            o = "B" if s == "A" else "A"
            try:
                oelo = float(g[f"team{o}Elo"])
            except ValueError:
                oelo = 0
            if int(g[f"team{s}Id"]) in teams and oelo >= 2000:
                ok = True
        if ok:
            todo.append(g["game_id"])
    t0 = time.time()
    bad = 0
    with Pool(jobs) as pool:
        for i, (gid, rc) in enumerate(pool.imap_unordered(run, todo)):
            if rc != 0:
                bad += 1
                print("FAILED", gid, rc)
            if (i + 1) % 100 == 0:
                print(f"{i + 1} of {len(todo)} done, {time.time() - t0:.0f}s", flush=True)
    print(f"done: {len(todo)} games, {bad} failed, {time.time() - t0:.0f}s")
