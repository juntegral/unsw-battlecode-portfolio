#!/usr/bin/env python3
"""c_splitjsonl.py [jsonl=c_out/ramlocal_1119_large.jsonl]: write the per-game ram lists of c_ramlocal.py as two files,
one for the runs of the test build with TRADE_CONTACT (battle ids tc30-test-new, tc30-dev1b-new) and one for all other
runs: <name>_tc.jsonl and <name>_notc.jsonl. They can then be read by c_front.py."""
import csv
import json
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "c_out/ramlocal_1119_large.jsonl"
BATTLE = {g["game_id"]: g["battle_id"] for g in csv.DictReader(open("games.csv"))}
TC = ("tc30-test-new", "tc30-dev1b-new")
base = path[:-len(".jsonl")]
out = {True: open(base + "_tc.jsonl", "w"), False: open(base + "_notc.jsonl", "w")}
n = {True: 0, False: 0}
for line in open(path):
    tc = BATTLE.get(json.loads(line)["gid"], "") in TC
    out[tc].write(line)
    n[tc] += 1
for f in out.values():
    f.close()
print(f"{base}_tc.jsonl: {n[True]} games; {base}_notc.jsonl: {n[False]} games")
