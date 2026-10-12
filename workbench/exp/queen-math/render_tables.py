#!/usr/bin/env python3
"""Refresh only marked numerical tables in the Korean report."""
import csv
import re
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPORT=HERE.parents[1]/'research/observations/queen-mechanics.md'
content=REPORT.read_text()

def replace(name,table):
    global content
    start=f'<!-- {name} -->'; end=f'<!-- END_{name} -->'
    block=start+'\n\n'+table+'\n\n'+end
    if end in content:
        content=re.sub(re.escape(start)+r'.*?'+re.escape(end),lambda m:block,content,flags=re.S)
    else:
        assert content.count(start)==1
        content=content.replace(start,block)

reach=list(csv.DictReader((HERE/'reach.csv').open()))
table=['| L | f | M | d₁(그 머리) | d₁(자식 포함) | T₂(그 머리) | T₂(자식 포함) | d₂(자식 포함·옛 칸) | MOVE 전체 몸 합집합 |',
       '|---:|---:|---:|---:|---:|---:|---:|---:|---|']
for r in reach:
    l=int(r['L']); m=r['max_steps_no_food']
    union=f'D_{m}'+(' − 원점' if l<6 else '')
    table.append(f"| {l} | {r['free']} | {m} | {r['same_round_safe_distance']} | {r['same_round_safe_distance_with_split_descendants']} | {r['two_turn_reach_no_food']} | {r['two_turn_reach_with_split_descendants']} | {r['two_turn_old_tile_safe_distance_with_split_descendants']} | {union} |")
replace('REACH_TABLE','\n'.join(table))
drop=list(csv.DictReader((HERE/'drops.csv').open()))
table=['| 기증 길이 L | 드롭 | 최대 질량 효율 |','|---:|---:|---:|']
for r in drop:
    table.append(f"| {r['L']} | {r['drops']} | {100*float(r['efficiency']):.1f}% |")
replace('DROP_TABLE','\n'.join(table))
REPORT.write_text(content)
print('report tables refreshed: 39 reach rows, 39 drop rows')
