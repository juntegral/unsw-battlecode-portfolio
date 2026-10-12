#!/usr/bin/env python3
"""Candidate 1 cross-check: do the 25 round-500 losses with her queen alive still have an in-view chance under the
stricter path test of h_c1recount.py (every body blocked, as in the bot's hunt_path())?  And how do the what-if
counts come out when only the strict chances are used?  Output: stdout -> h_out/c1check.txt"""
import csv
import json

rows = {r["game_id"]: r for r in csv.DictReader(open("games.csv"))}
base = {r["gid"]: r for r in json.load(open("h_out/base.json")) if "meow" in r["groups"]}
rec = json.load(open("h_out/c1recount.json"))
n = keep = len_ = hard = 0
lost = []
for gid, r in sorted(base.items()):
    if r["end_type"] == "wipe-out" or r["win"] or not r["op_fin"]["queen"]:
        continue
    if not any(c[9] for c in r["my_ch"]):
        continue
    n += 1
    me = r["side"]
    strict = sorted(x for x in rec[str(gid)]["ch"] if x[1] == me)
    mq, oq = r["my_fin"]["queen"], r["op_fin"]["queen"]
    op_long, op_second = r["op_fin"]["longest"], r["op_second_fin"]
    op_noq = op_second if oq == op_long else op_long
    lenient = bool(mq) or r["my_fin"]["longest"] > op_noq
    hardf = bool(mq) or r["my_fin"]["longest"] > op_long
    if strict:
        keep += 1
        len_ += lenient
        hard += hardf
    else:
        lost.append((gid, r["map"], "lenient flip" if lenient else "no flip"))
print(f"round-500 losses with her queen alive and a chance by the lead's count: {n}")
print(f"... that also have a chance under the strict path test: {keep}; lenient flips among them {len_}, hard {hard}")
print("... without a strict chance:", lost)
# overall games with a strict chance and never a ram, by result
c = {}
for gid, r in base.items():
    me = r["side"]
    strict = [x for x in rec[str(gid)]["ch"] if x[1] == me]
    qd = r["op_qd"]
    killed = bool(qd and qd["by_enemy"])
    if strict and not killed:
        k = ("wipe-out " if r["end_type"] == "wipe-out" else "round 500 ") + ("W" if r["win"] else "L") + (" her alive" if r["op_fin"]["queen"] else " her dead")
        c[k] = c.get(k, 0) + 1
print("games with a strict chance and never a ram on her:", sum(c.values()), c)
