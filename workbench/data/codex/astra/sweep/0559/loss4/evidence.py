import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter
sys.path.insert(0,'tools')
import ladder_replay as lr
OUT=Path('data/codex/astra/sweep/0559/loss4');p=Path('data/online/smoke/one8-p1-old/M1494965.replay')
j=json.loads(p.with_name('game-1494965.json').read_text());a=lr.scan(p,j,'one8-p1-old',set());t=json.loads((OUT/'turns.json').read_text());teams=t['teams'];l=json.loads((OUT/'ledger.json').read_text())
result={'final':a['final'],'anomalies':a['anomalies'],'queen_drops':[],'bands':[]}
for x in a['pearls']:
 if x['eater_id'] in (0,1) and x['eat_round']>=400:result['queen_drops'].append(x)
for lo,hi in [(0,100),(101,300),(301,350),(351,400),(401,499),(483,499)]:
 row={'rounds':[lo,hi]}
 for s in (0,1):
  ts=[v for v in t['turns'] if lo<=v['r']<=hi and teams[str(v['i'])]==s]
  es=[e for e in l['eats'] if lo<=e[0]<=hi and e[1]==s]
  ds=[d for d in l['deaths'] if lo<=d[0]<=hi and d[1]==s]
  row[str(s)]={'turns':len(ts),'eats':dict(Counter(e[3] for e in es)),'queen_eats':dict(Counter(e[3] for e in es if e[2]=='q')),'deaths':dict(Counter(d[4] for d in ds))}
 result['bands'].append(row)
def man(x,y):
 dx,dy=abs(x[0]-y[0]),abs(x[1]-y[1]);return min(dx,48-dx)+min(dy,24-dy)
blocked=[]
for v in t['turns']:
 if v['r']<450 or v['i']==1 or teams[str(v['i'])]!=0:continue
 b=v['b'];n=sum(teams[i]==0 for i in b);q=b['1'][0];h=b[str(v['i'])][0]
 if n<=3 and man(q,h)<=5:blocked.append({'r':v['r'],'i':v['i'],'n':n,'head':h,'q':q,'distance':man(q,h)})
result['reserve_block_near5']=blocked
result['queen_splits']=a['q_splits'];result['last_queen_eat']=max(v['r'] for v in t['turns'] if v['i']==1 and any(e[0]=='pearl' and e[2]==0 for e in v['events']))
(OUT/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
print('event names',lr.replay.EVENT_NAMES)
