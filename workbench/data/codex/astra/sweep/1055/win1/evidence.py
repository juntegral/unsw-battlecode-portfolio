import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
from collections import Counter,defaultdict,deque
sys.path.insert(0,'tools')
from ladder_replay import edge_id,canonical_edges
OUT=Path(__file__).resolve().parent
rows=[]
for bfile in sorted(OUT.glob('*-base.json')):
 gid=int(bfile.stem.split('-')[0]);tf=OUT/f'{gid}-trace.json'
 if not tf.exists():continue
 b=json.loads(bfile.read_text());t=json.loads(tf.read_text());side='AB'.index(b['ours']);q=t['queens'][side];eq=t['queens'][1-side]
 w,h=map(int,b['text'].splitlines()[0].split()[1:3]);edges=canonical_edges(w,h,[tuple(map(int,l.split()[1:4])) for l in b['text'].splitlines() if l.startswith('EDGE ')])
 def md(a,z):
  dx,dy=abs(a[0]-z[0]),abs(a[1]-z[1]);return min(dx,w-dx)+min(dy,h-dy)
 ours=[a for a in t['turns'] if a['s']==side];qs=[a for a in ours if a['queen']]
 eaten=[a for a in ours if a['steps'] and a['dirs'] and a['steps'][0] in a['adjpearls'] and tuple(a['steps'][0]) in map(tuple,a['eaten']) and edges.get(edge_id(w,h,*a['h'],a['dirs'][0]),(0,-1))[0]==0]
 heading=[a for a in ours if a['r']<12 and a['L']<=4 and not a['queen'] and a['dirs'] and a['facing']==a['dirs'][0] and len(a['exits'])>=2]
 misses=[a for a in ours if a['adjpearls'] and not a['eaten'] and not a['split'] and a['end'] is not None]
 kept=[a for a in qs if a['L']==4 and a['n']>=6 and not a['split']]
 shortsplit=[a for a in qs if a['split'] and a['split']['parentL']==2 and a['n']<6]
 qram=[a for a in ours if any(d['i']==eq and d['reason']==3 and d['actor'] if False else False for d in [])]
 qram=[a for a in ours if any(d['i']==eq and d['reason']==3 for d in a['deaths'])]
 defend=[a for a in ours if a['L']<=4 and a['qh'] and any(d['reason']==3 and d['i']!=a['i'] and d['s']!=side and md(d['body'][0],a['qh'])<=3 for d in a['deaths'])]
 moves=[a for a in ours if not a['queen'] and a['L']>=8 and len(a['steps'])>=2 and not a['eaten'] and not a['deaths'] and a['end'] is not None and min((md(a['h'],n['h']) for n in a['near'] if n['s']!=side),default=100)<=3]
 stops=[d for d in b['deaths'] if d['side']=='us' and d['reason']==4];stopids={d['death'] for d in stops};prs=[p for p in b['pearls'] if p['death'] in stopids]
 stop_no_recovery=[d for d in stops if not any(p['eater']=='us' and p['death']==d['death'] for p in prs)]
 lost_long=[d for d in b['deaths'] if d['side']=='us' and d['reason']==3 and d['actor']!=d['id'] and d['length']>=8]
 def moments(arr):return [{k:a[k] for k in ('r','i','L','h','n','dirs','steps','eaten','adjpearls','split','exits','near') if k in a} for a in arr[:3]]
 cnt=dict(own_turns=len(ours),logs=len(t['logs']),ordinary_adjacent_eats=len(eaten),heading_continuations=len(heading),adjacent_pearl_misses=len(misses),queen_L4_retained=len(kept),queen_L2_split_small_side=len(shortsplit),queen_killing_rams=len(qram),defend_ram_candidates=len(defend),long_escape_candidates=len(moves),stationary_alive_unsplit=sum(a['h']==a['end'] and not a['split'] for a in ours),no_action_deaths=len(stops),no_action_deaths_no_own_recovery=len(stop_no_recovery),no_action_drop_pearls=len(prs),no_action_drop_eaten_by_queen=sum(p['eater_id']==q for p in prs),long_rammed=len(lost_long),queen_first100_L2=sum(a['r']<100 and a['L']==2 for a in qs),queen_first100_turns=sum(a['r']<100 for a in qs))
 row=dict(gid=gid,counts=cnt,examples=dict(eats=moments(eaten),heading=moments(heading),miss=moments(misses),qkeep=moments(kept),qsplit=moments(shortsplit),qkill=moments(qram),defend=moments(defend),longescape=moments(moves)),own_queen_splits=[a for a in t['qsplits'] if a['i']==q],long_rammed=lost_long,no_action_unrecovered=stop_no_recovery)
 rows.append(row)
 (OUT/f'{gid}-evidence.json').write_text(json.dumps(row,ensure_ascii=False))
 totals=dict(sum((Counter(r['counts']) for r in rows),Counter()))
(OUT/'evidence.json').write_text(json.dumps(dict(totals=totals,games=rows),ensure_ascii=False,indent=2))
print(json.dumps(totals))
for r in rows:print(r['gid'],r['counts'],'qsplits',[(s['r'],s['L'],s['parentL'],s['childL']) for s in r['own_queen_splits']])
