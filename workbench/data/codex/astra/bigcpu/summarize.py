#!/usr/bin/env python3
import sys
sys.dont_write_bytecode = True
import json, math, csv
from pathlib import Path
from collections import Counter, defaultdict
from statistics import median
from datetime import datetime
HERE=Path(__file__).resolve().parent

def corr(xs,ys):
    if len(xs)<3:return None
    mx,my=sum(xs)/len(xs),sum(ys)/len(ys)
    xx=sum((x-mx)**2 for x in xs);yy=sum((y-my)**2 for y in ys)
    return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/math.sqrt(xx*yy) if xx*yy else None

rows=[json.loads(l) for l in (HERE/'games.jsonl').read_text().splitlines()]
assert len(rows)==len(json.loads((HERE/'inventory.json').read_text())['entries'])
assert not [r for r in rows if 'scan_error' in r]
clean=[r for r in rows if r.get('finished')]
groups=defaultdict(list)
for r in clean:groups[r['arm'],r['cells']].append(r)
relationships=[]
for (arm,cells),rs in sorted(groups.items()):
    relationships.append(dict(arm=arm,cells=cells,n=len(rs),
        weighted_ms=sum(r['seconds'] for r in rs)*1000/sum(r['turns_total'] for r in rs),
        weighted_alive=sum(r['mean_alive_at_turn']*r['turns_total'] for r in rs)/sum(r['turns_total'] for r in rs),
        pearson_game_mean_alive_vs_game_ms=corr([r['mean_alive_at_turn'] for r in rs],[r['ms_per_turn'] for r in rs]),
        games=[dict(game=r['game'],ms_per_turn=r['ms_per_turn'],mean_alive_at_turn=r['mean_alive_at_turn'],
                    turns_total=r['turns_total'],seconds=r['seconds']) for r in rs]))
(HERE/'timing_relationships.json').write_text(json.dumps(relationships,indent=2)+'\n')
large=[r for r in clean if r['cells']>=4096]
ours,theirs=Counter(),Counter()
for r in large:ours.update(r['action_death_ours']);theirs.update(r['action_death_old_main'])
matched=[]
for r in clean:
    if r['arm']!='mGx6_vb' or r['cells']!=65536:continue
    smaller=r['game'].replace('256x256','64x64')
    family=r['game'].split('_')[1]
    q=next(q for q in clean if q['arm']==r['arm'] and q['cells']==4096 and
           q['game'].split('_')[1]==family and q['own_side']==r['own_side'])
    matched.append(dict(large_game=r['game'],small_game=q['game'],large_ms=r['ms_per_turn'],small_ms=q['ms_per_turn'],
                        ratio=r['ms_per_turn']/q['ms_per_turn'],large_alive=r['mean_alive_at_turn'],small_alive=q['mean_alive_at_turn']))
info=dict(as_of=datetime.now().astimezone().isoformat(),folders=len(rows),complete=len(clean),incomplete=[r for r in rows if not r.get('finished')],
          arms=len(set(r['arm'] for r in rows)),distinct_maps=len(set(r['game'].rsplit('-seed',1)[0] for r in rows)),
          native_games=sum(r['native'] is True for r in clean),turns=sum(r['turns_total'] for r in clean),
          turns_with_usage=sum(r['turns_with_usage'] for r in clean),bot_errors=sum(len(r['bot_errors'] or []) for r in clean),
          timeout_actions=sum(r['timeout_actions_ours']+r['timeout_actions_old_main'] for r in clean),
          large_games=len(large),large_turns=sum(r['turns_total'] for r in large),large_action_death_ours=dict(ours),large_action_death_old_main=dict(theirs),
          all_action_death_ours=dict(sum((Counter(r['action_death_ours']) for r in clean),Counter())),
          all_action_death_old_main=dict(sum((Counter(r['action_death_old_main']) for r in clean),Counter())),
          matched_4096_65536=matched)
(HERE/'findings.json').write_text(json.dumps(info,indent=2)+'\n')
print(json.dumps({k:v for k,v in info.items() if k!='incomplete'},indent=2))
print('TIMING')
for x in relationships:
 print(x['arm'],x['cells'],x['n'],round(x['weighted_ms'],3),round(x['weighted_alive'],1),None if x['pearson_game_mean_alive_vs_game_ms'] is None else round(x['pearson_game_mean_alive_vs_game_ms'],2))
