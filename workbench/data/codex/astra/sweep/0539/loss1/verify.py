import json
from pathlib import Path
from datetime import datetime
O=Path(__file__).resolve().parent
out={}
for gid in [1493690,1493693,1493694]:
 a=json.loads((O/f'{gid}-ledger.json').read_text());m=json.loads((O/f'{gid}-moments.json').read_text())
 assert a['bots']['B']=='21126'
 for q in m['qt']:
  assert len(q['board'])==7 and all(len(row)==7 for row in q['board'])
 lastnot=-1
 for r,st in m['snapshots'].items():
  def score(s,q):
   ls=[b[1] for b in st.values() if b[0]==s]
   return (bool(ls),st.get(str(q),[0,0])[1],max(ls,default=0),sum(ls))
  if score(1,m['qu'])>=score(0,m['qe']):lastnot=int(r)
 out[gid]=dict(final=a['final'],permanent_losing_round=lastnot+1,near5_turns=len(m['near']),queen_turns=[t['r'] for t in m['qt']])
 if gid!=1493690:
  i,lo=(982,480) if gid==1493693 else (843,466)
  ts=[t for t in m['turns'] if t['id']==i and t['r']>=lo]
  out[gid]['plateau']=dict(id=i,from_round=lo,turns=len(ts),pearls=sum(len(t['eats']) for t in ts))
  assert out[gid]['plateau']['pearls']==0
assert [out[g]['permanent_losing_round'] for g in out]==[187,229,486]
assert [out[g]['near5_turns'] for g in out]==[0,0,0]
(O/'verified.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
p=O/'report.md';s=p.read_text();s=s.replace('[M] 최상위 공통 원인:', '[M/E] 최상위 공통 원인:');s=s.replace('작성 2026-10-09 05:45 KST.', '작성 '+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+' KST.');p.write_text(s)
print('Verified bot IDs, 9 boards, final states, turning rounds, and both zero-eating intervals.')
