import json
from pathlib import Path
O=Path(__file__).parent
for p in sorted(O.glob('case*.json')):
 x=json.loads(p.read_text());d=x['death'];cs=x['closures'];t=x['turns'][-2:]
 print(x['gid'],x['v'],'r'+str(d['r']),'L'+str(d['L']),'why'+str(d['reason']),x['map'],'Q',[(z['r'],len(z['before']),len(z['endexits']),z['split']) for z in t])
 for c in cs[-2:]:print('  close',c['r'],c['id'],c['L'],c['team']==x['own'],'strict',c['strict_certain'],'gate',c['strict_gate'],'vis',c['qvisible'],'port',c['queen_portal'],c['pathportal'],'from',c['body'],'to',c['endbody'],'alts',c['live_alternatives'])
 if d['reason']!=3:
  print('  neigh',[(n['d'],n['edge'],n['occupant']) for n in x['neighbors']])
  for z in t[:1]:print('  alt',z['r'],[(v['d'],v['kind'],len(v.get('own_exits',[])),v.get('portal')) for v in z['alternatives']])
