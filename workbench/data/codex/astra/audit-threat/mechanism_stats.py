import sys
sys.dont_write_bytecode=True
import json,gzip
from pathlib import Path
from collections import Counter
O=Path(__file__).resolve().parent;m=json.loads((O/'matched.json').read_text());out={}
for pair in ('7->8','8->9','9->10'):
 out[pair]={}
 for arm in ('before','after'):
  z=m[pair][arm];c=Counter();eg={}
  for gid in z['ids']:
   g=json.loads((O/f'g{gid}.json').read_text())
   for r in g['rams']:
    row=r['turn'];info=row['seen'].get(str(r['attacker'])) if row else None;tags=[]
    if not r['q'] and row and row['L']<=4 and info and info['parts']<5 and r['steps']>1:tags.append('small_visible_multistep')
    if r['q'] and r['ate'] and r['reach_class']!='unseen':tags.append('queen_visible_pearl')
    if r['q'] and r['view_cut']:tags.append('queen_cut')
    if not r['q'] and row and row['L']<=4 and info and r['steps']<=r['free']+1 and row['ally_heads']+1<=row['enemy_heads']:tags.append('short_evade_gate_ram')
    for k in tags:
     c[k]+=1;eg.setdefault(k,[])
     if len(eg[k])<3:eg[k].append(dict(gid=gid,r=r['r'],id=r['id'],attacker=r['attacker']))
  out[pair][arm]=dict(counts=dict(c),rates_per_1000={k:v*1000/z['counts']['short_turns' if k.startswith(('small','short')) else 'queen_turns'] for k,v in c.items()},examples=eg)
(O/'mechanism-stats.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
inv=json.loads((O/'inventory.json').read_text());deaths=[]
for j in inv['games']:
 if j['version'] not in (9,10):continue
 g=json.loads((O/f'g{j["gid"]}.json').read_text())
 for d in g['deaths']:
  if not d['q']:continue
  row=d.get('turn');category='no_open_exit' if d['reason'] in (0,1,2) and row and row.get('open_start')==0 else d.get('reach_class','unknown')
  ram=next((r for r in g['rams'] if r['q']),None)
  deaths.append(dict(gid=j['gid'],v=j['version'],r=d['r'],category=category,raw_cause=d.get('reach_class'),length=d['L'],split_child_after_queen=ram['born_after_decision'] if ram else False))
assert len(deaths)==sum(sum(d['q'] for d in json.loads((O/f'g{j["gid"]}.json').read_text())['deaths']) for j in inv['games'] if j['version'] in (9,10))
card=[]
for x in json.loads((O/'exit-card-witnesses.json').read_text()):
 if not x['queen_visible'] or not x['walls']:continue
 rows=json.load(gzip.open(O/f'turns-{x["gid"]}.json.gz','rt'));r=next(r for r in rows if r['id']==x['id'] and r['r']==x['r'])
 card.append(dict(x,mate_next5=r['next5'],queen_death=next(d['r'] for d in deaths if d['gid']==x['gid'])))
(O/'queen-deaths.json').write_text(json.dumps(dict(classes=dict(Counter(d['category'] for d in deaths)),deaths=deaths,card=card),ensure_ascii=False,indent=2))
print(dict(Counter(d['category'] for d in deaths)),len(card))
