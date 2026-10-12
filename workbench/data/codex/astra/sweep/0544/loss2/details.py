import json,sys
from pathlib import Path
from collections import Counter
sys.dont_write_bytecode=True
P=Path('data/codex/astra/sweep/0544/loss2')
for gid in (1493881,1493882,1493883):
 d=json.loads((P/f'{gid}.json').read_text());w,h=d['w'],d['h'];xy=lambda c:(c%w,c//w);qt=[t for t in d['turns'] if t['id']==d['queens'][0]];print('\n',gid)
 for t in qt[-3:]:
  print('queen',t['r'],t['L'],xy(t['body'][0]),'->',xy(t['end'][0]),'neighbors',[(i,len(b),xy(b[0])) for i,b in t['bodies'].items() if i!=str(t['id']) and max(min(abs(b[0]%w-t['body'][0]%w),w-abs(b[0]%w-t['body'][0]%w)),min(abs(b[0]//w-t['body'][0]//w),h-abs(b[0]//w-t['body'][0]//w)))<=4])
 for lo,hi in ((0,30),(31,60),(61,100),(301,349),(350,399),(400,499)):
  if lo>d['lastRound']:continue
  for s in (0,1):
   ts=[t for t in d['turns'] if lo<=t['r']<=hi and d['teams'][str(t['id'])]==s];ds=[x for x in d['deaths'] if lo<=x['r']<=hi and x['side']==s];sp=[x for x in d['splits'] if lo<=x['r']<=hi and d['teams'][str(x['parent'])]==s]
   print('phase',lo,hi,s,'turns',len(ts),'eat',sum(len(t['eats']) for t in ts),'paid',sum(max(0,len(t['steps'])-(t['L']+3)//4) for t in ts),'splits',len(sp),'deaths',Counter(x['reason'] for x in ds))
 if gid==1493883:
  print('last large',[(t['id'],len(t['end']),xy(t['end'][0])) for t in d['turns'] if t['r']==499 and len(t['end'])>=15]);print('large splits', [s for s in d['splits'] if s['r']>=300 and s['before']>=15 and d['teams'][str(s['parent'])]==0])
  for i in [t['id'] for t in d['turns'] if t['r']==499 and len(t['end'])>=35]:
   ts=[t for t in d['turns'] if t['id']==i];print('leader',i,'s',d['teams'][str(i)],'growth',[(t['r'],t['L'],len(t['end'])) for t in ts if t['r']%25==0],'eaten301',sum(len(t['eats']) for t in ts if t['r']>=301),'paid301',sum(max(0,len(t['steps'])-(t['L']+3)//4) for t in ts if t['r']>=301))
  ss=d['snaps'];print('permanent longest lead',1+max(int(r) for r,s in ss.items() if s[0]['longest']>=s[1]['longest']));print('permanent total lead',1+max(int(r) for r,s in ss.items() if s[0]['total']>=s[1]['total']))
 else:
  ss=d['snaps'];print('permanent total lead',1+max(int(r) for r,s in ss.items() if s[0]['total']>=s[1]['total']))
