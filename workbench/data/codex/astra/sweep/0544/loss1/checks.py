import json,hashlib
from pathlib import Path
from datetime import datetime
OUT=Path(__file__).parent
facts={}
for gid in (1493878,1493879,1493880):
 d=json.loads((OUT/f'{gid}.json').read_text());ourq=d['queens'][0]
 own=[t for t in d['turns'] if d['teams'][str(t['id'])]==0]
 cap=[t for t in own if 351<=t['r']<=400]
 enemies=[t for t in own if 150<=t['r']<=400 and t['enemy10']]
 mid=[[t for t in d['turns'] if 201<=t['r']<=400 and d['teams'][str(t['id'])]==s] for s in (0,1)]
 facts[gid]=dict(queens=d['queens'],final=d['final'],queen_deaths=[{k:v for k,v in x.items() if k not in ('heads','actor_turn')} for x in d['deaths'] if x['id'] in d['queens']],
  permanent_longest_deficit=max(int(r) for r,s in d['rounds'].items() if s[0]['longest']>=s[1]['longest'])+1,
  permanent_queen_deficit=max(int(r) for r,s in d['rounds'].items() if s[0]['q']>=s[1]['q'])+1,
  mid=[dict(turns=len(ts),splits=sum(bool(t['split']) for t in ts),natural=sum(e[1]=='spawn' for t in ts for e in t['eat'])) for ts in mid],
  cap_turns=[sum(t['units']>=56 for t in cap),len(cap)],enemy10_turns=len(enemies),enemy10_first=[{k:v for k,v in t.items() if k in ('r','id','enemy10')} for t in enemies[:3]],
  long_deaths_over10=[x for x in d['deaths'] if d['teams'][str(x['id'])]==0 and len(x['body'])>10],
  near_turns=len(d['near']),near_ids=sorted(set(x['id'] for x in d['near'])),near_min=min([x['d'] for x in d['near']],default=None))
 for t in [t for t in d['queen_turns'] if t['id']==ourq][-3:]:
  assert 'action' in t
 assert d['bots'][0]=='21126'
assert facts[1493878]['mid'][0]['splits']==132
assert facts[1493879]['mid'][0]['splits']==206
assert facts[1493878]['cap_turns']==[0,2374]
assert facts[1493879]['cap_turns']==[583,2591]
source=Path('data/online/smoke/one8-bot/main.cpp')
(OUT/'checked-facts.json').write_text(json.dumps(dict(checked_at=datetime.now().astimezone().isoformat(),source=str(source),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),games=facts),ensure_ascii=False,indent=2)+'\n')
print('3 games checked; asserted replay result fields in analyze.py; report counts agree.')
