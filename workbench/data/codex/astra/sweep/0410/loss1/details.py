import sys,json
from pathlib import Path
from collections import Counter
sys.dont_write_bytecode=True
from analyze import lr,Geo,GAMES,OUT
rows=[]
for bid,gid in GAMES:
 a=json.loads((OUT/f'{gid}.json').read_text());ts=json.loads((OUT/f'{gid}-turns.json').read_text());ss=json.loads((OUT/f'{gid}-snapshots.json').read_text());ds=json.loads((OUT/f'{gid}-deaths.json').read_text())
 row=dict(gid=gid,total_deficit_since=max([int(r) for r,s in ss.items() if s[0]['total']>=s[1]['total']],default=-1)+1,windows=[])
 for lo,hi in [(0,49),(50,100),(101,300),(301,400),(401,499)]:
  sides=[]
  for s in [0,1]:
   sub=[t for t in ts if lo<=t['round']<=hi and t['side']==s]
   sides.append(dict(turns=len(sub),eats=sum(t['eats'] for t in sub),noeatmoves=sum(not t['eats'] and t['action']['kind']==0 for t in sub),splits=sum('split' in t for t in sub),stops=sum(t['action']['kind']==2 for t in sub)))
  row['windows'].append([lo,hi,sides])
 if gid==1486054:
  ids={1186};events=[]
  for t in reversed(ts):
   sp=t.get('split')
   if sp and sp[1] in ids:ids.add(sp[0]);events.append([t['round'],sp])
  row['lineage']=list(reversed(events))
  row['late_leaders']={}
  for side in [0,1]:
   target=1122 if side else None
   sub=[t for t in ts if t['round']>=432 and ((t['id']==1122) if side else (t['id']==1121 and t['round']<=475 or t['id']==1179 and t['round']<=495 or t['id']==1186))]
   row['late_leaders'][side]=dict(eats=sum(t['eats'] for t in sub),turns=len(sub),noeat=sum(not t['eats'] for t in sub),splits=[t['split'] for t in sub if 'split' in t])
 if gid in [1486052,1486053]:
  q=a['queen_turns'][-1];actor=next(d['actor'] for d in ds if d['id']==a['queens'][0]);row['attacker']=actor
  row['visible_parts']=[]
  for t in [x for x in ts if x['id']==a['queens'][0] and q['round']-4<=x['round']<=q['round']]:
   b=t['bodies'].get(str(actor),[]);w,h=a['dim'];hx,hy=t['start'];seen=[c for c in b if min(abs(c%w-hx),w-abs(c%w-hx))<=3 and min(abs(c//w-hy),h-abs(c//w-hy))<=3]
   row['visible_parts'].append([t['round'],len(b),len(seen)])
 rows.append(row)
(OUT/'details.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
print(json.dumps(rows,ensure_ascii=False))
