#!/usr/bin/env python3
"""b_run.py <game_id> [<game_id> ...]: run the close-read tools for both teams of each game into b_out/ (sub-session A2).

For each game: b_pack.py for side A and side B (pk2_<id>_<team>.txt), digest.py for both (dg_<id>_<team>.txt),
b_open.py (op2_<id>.txt). Skips outputs that already exist unless --force is given.
"""
import csv
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GAMES = {g["game_id"]: g for g in csv.DictReader(open(os.path.join(HERE, "games.csv")))}
force = "--force" in sys.argv
ids = [a for a in sys.argv[1:] if not a.startswith("--")]


def run(args, out):
    path = os.path.join(HERE, "b_out", out)
    if os.path.exists(path) and os.path.getsize(path) > 0 and not force:
        return
    with open(path, "w") as f:
        r = subprocess.run([sys.executable] + args, cwd=HERE, stdout=f, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        print("FAILED", args, r.stderr[-600:])


for gid in ids:
    g = GAMES[gid]
    for side in "AB":
        t = g["team%sId" % side]
        run(["b_pack.py", gid, t], f"pk2_{gid}_{t}.txt")
        run(["digest.py", gid, t], f"dg_{gid}_{t}.txt")
    run(["b_open.py", gid, "100"], f"op2_{gid}.txt")
    print("done", gid, g["map"], g["teamAName"], "vs", g["teamBName"], flush=True)
