import json
from pathlib import Path
P=Path(__file__).resolve().parent
out={}
for gid in (1497633,1497386,1497387):
 b=json.loads((P/f'{gid}-base.json').read_text());t=json.loads((P/f'{gid}-trace.json').read_text());own=t['own'];sn=b['snapshots'];rr=sorted(map(int,sn))
 def value(x):return tuple(x[k] for k in ('queen_length','longest','total'))
 row={'final':b['final'],'bot':b['bots'][b['ours']],'queens':b['queens'],'last_round':b['last_round'],'permanent_score_deficit':max(r for r in rr if value(sn[str(r)]['us'])>=value(sn[str(r)]['them']))+1,'near5_unique_round_dragons':len(set((x['round'],x['id']) for x in t['near'])),'near5_first':t['near'][0] if t['near'] else None,'near5_min':t['minimum'],'windows':{}}
 for side,s in [('us',own),('them',1-own)]:
  lengths=[len(bb) for i,bb in t['final_bodies'].items() if t['teams'][i]==s]
  assert (len(lengths),sum(lengths),max(lengths,default=0))==tuple(b['final'][side][k] for k in ('alive','total','longest'))
  assert sum(len(x['eats']) for x in t['turns'] if x['side']==s)==b['final'][side]['pearls']
 for lo,hi in [(43,100),(101,200),(201,300),(401,499)]:
  row['windows'][f'{lo}-{hi}']={}
  for side,s in [('us',own),('them',1-own)]:
   tt=[x for x in t['turns'] if x['side']==s and lo<=x['round']<=hi]
   row['windows'][f'{lo}-{hi}'][side]={'turns':len(tt),'pearls':sum(len(x['eats']) for x in tt),'no_eat_moving_turns':sum(not x['eats'] and bool(x['moves']) for x in tt),'splits':sum(bool(x['splits']) for x in tt)}
 if gid==1497387:
  row['leader_eats_401_499']={}
  for side,ids in [('us',[846]),('them',[970,1032,1072,1096])]:
   eats=sum(len(x['eats']) for x in t['turns'] if x['id'] in ids and x['round']>=401);drops=[x for x in b['pearls'] if x['eater_id'] in ids and x['eat_round']>=401]
   row['leader_eats_401_499'][side]={'ids':ids,'total':eats,'own_corpse':sum(x['drop_side']==side for x in drops),'natural':eats-len(drops)}
 out[str(gid)]=row
(P/'metrics.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print('Validated final states and all consumption counts for 3 games; wrote metrics.json')
