import json
from collections import Counter
from statistics import mean,median
from pathlib import Path
O=Path('data/codex/astra/worstmaps');rs=json.loads((O/'rows.json').read_text());names=['Australia','Tower Defense','Stripes','Around UNSW','Schooltime','Default','Devil']
for name in names:
 rr=[r for r in rs if r['map']==name];f=rr[0]['features'];print('\n',name,'n',len(rr),'versions',dict(Counter(r['src'] for r in rr)),'win',sum(r['result']=='win' for r in rr),'turn',[r['turn'] for r in rr]);print('FEATURE',f)
 print('first split',[[r['first_split'][s] for r in rr] for s in (0,1)])
 for t in (50,100,150,300):
  print(t,[[round(mean(r['spatial'][str(t)][s][k] for r in rr),2) for k in ['N','L','Q','home','far','neutral','bearing_near','bearing_tie','portal_moves','bearing_rate','fast_near']] for s in (0,1)])
 for hi in (100,300,999):
  print('DEATHS',hi,[dict(Counter(d[4] for r in rr for d in r['deaths'] if d[1]==s and d[0]<=hi)) for s in (0,1)])
 print('EATS100',[[sum(e[1]==s and e[0]<=100 and e[3]==origin for r in rr for e in r['eats']) for origin in ['n','own','foe']] for s in (0,1)])
 print('LOSS',dict(Counter(r['how'] for r in rr if r['result']=='loss')))
 print('GAMES',[(r['gid'],r['src'],r['opp'],r['result'],r['how'],r['last']) for r in rr])
