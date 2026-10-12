#!/usr/bin/env python3
"""Candidate 3, the number that could get worse: our wins on maps over 1,200 cells, one line each, with the margin on
the longest dragon and how the leader stood at rounds 150 / 300 / 400.  Also the round-500 both-dead losses on those
maps that were close (margin of 10 or less), since a later leader could cost or gain those.
Output: stdout -> h_out/c3wins.txt"""
import json

rows = [r for r in json.load(open("h_out/base.json")) if "meow" in r["groups"] and r["cells"] > 1200]
wins = [r for r in rows if r["win"]]
print(f"our games on maps over 1,200 cells: {len(rows)}; wins {len(wins)}")
for r in sorted(wins, key=lambda r: r["gid"]):
    m = r["my_fin"]["longest"] - r["op_fin"]["longest"]
    print(f"  {r['gid']} {r['map']:15s} {r['build']:4s} {r['end_type']:10s} our longest r150 {r['my_lon150']:3d} r300 {r['my_lon300']:3d} r400 {r['my_lon400']:3d} end {r['my_fin']['longest']:3d}"
          f" | theirs r300 {r['op_lon300']:3d} r400 {r['op_lon400']:3d} end {r['op_fin']['longest']:3d} | margin {m:+d} | our total r300 {r['my_tot300']} vs {r['op_tot300']}, units {r['my_uni300']} vs {r['op_uni300']}")
margins = sorted(r["my_fin"]["longest"] - r["op_fin"]["longest"] for r in wins)
print("win margins on the longest dragon:", margins)
dd = [r for r in rows if not r["win"] and r["end_type"] != "wipe-out" and not r["my_fin"]["queen"] and not r["op_fin"]["queen"]]
close = [r for r in dd if r["op_fin"]["longest"] - r["my_fin"]["longest"] <= 10]
print(f"round-500 losses with both queens dead on these maps: {len(dd)}; lost by 10 or less on the longest dragon: {len(close)}")
for r in sorted(close, key=lambda r: r["gid"]):
    print(f"  {r['gid']} {r['map']:15s} {r['build']:4s} ours {r['my_fin']['longest']} vs {r['op_fin']['longest']}; our total r300 {r['my_tot300']} vs {r['op_tot300']}")
