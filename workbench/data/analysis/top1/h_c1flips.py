#!/usr/bin/env python3
"""Candidate 1: the 25 round-500 losses with her queen alive and an untaken in-view chance, one line each, with the
fate of the dragon that would have rammed (from h_out/c1walk.json) and every reading of the flip.
Output: stdout -> h_out/c1flips.txt"""
import json

base = {r["gid"]: r for r in json.load(open("h_out/base.json")) if "meow" in r["groups"]}
walk = json.load(open("h_out/c1walk.json"))
n = 0
tot = dict(len=0, hard=0, safe=0)
for gid, r in sorted(base.items()):
    if r["end_type"] == "wipe-out" or r["win"] or not r["op_fin"]["queen"]:
        continue
    ch = sorted((c for c in r["my_ch"] if c[9]), key=lambda c: c[0])
    if not ch:
        continue
    n += 1
    w = walk[str(gid)]
    rows = sorted(w["rows"], key=lambda p: p["round"])
    p = rows[0]
    mq, oq = r["my_fin"]["queen"], r["op_fin"]["queen"]
    op_long, op_second = r["op_fin"]["longest"], r["op_second_fin"]
    op_noq = op_second if oq == op_long else op_long
    mine, second = r["my_fin"]["longest"], w["final_second"]
    # if the rammer is our longest dragon at the end, our longest without it is the second
    mine_wo = second if p["is_final_longest"] else mine
    lenient = bool(mq) or mine > op_noq
    hard = bool(mq) or mine > op_long
    safe = bool(mq) or mine_wo > op_noq
    tot["len"] += lenient
    tot["hard"] += hard
    tot["safe"] += safe
    others = sorted({(q["len"], q["round"]) for q in rows[1:]})[:4]
    print(f"{gid} {r['map']:16s} {r['build']:4s} vs {r['opp'][:12]:12s} first chance r{p['round']:3d}: our #{p['id']} L{p['len']} needs {p['steps_needed']} steps, "
          f"her queen L{p['qlen']}; that dragon ended {'dead' if not p['final_len'] else 'L' + str(p['final_len'])}"
          f"{' = OUR FINAL LONGEST' if p['is_final_longest'] else ''}; chances in the game {len(rows)}; "
          f"end: ours longest {mine} (second {second}) queen {mq} | hers longest {op_long} queen {oq} best non-queen {op_noq} | "
          f"{'FLIP lenient' if lenient else 'no flip'}{' + hard' if hard else ''}{'' if safe == lenient else ' (NOT if the rammer is lost)'}")
print(f"\n{n} games; lenient flips {tot['len']}, hard {tot['hard']}, lenient with the rammer removed from our final lengths {tot['safe']}")
