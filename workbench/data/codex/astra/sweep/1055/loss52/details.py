import sys,json,importlib.util
from pathlib import Path
from collections import Counter
sys.dont_write_bytecode=True
from analyze import m
O=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('oldboards','data/codex/astra/sweep/0630/loss1/inspect.py')
bm=importlib.util.module_from_spec(spec)
sys.modules['analyze'].Geo=m.Geo;sys.modules['analyze'].OUT=O;sys.modules['analyze'].lr=m.lr
spec.loader.exec_module(bm)
for gid in (1517694,1517697,1517698):
 p=O/f'{gid}.json';raw=p.read_text().replace('one11-c1-old','one14-c1-old');p.write_text(raw);g=json.loads(raw)
 geo=m.Geo(g['w'],g['h'],g['edges']);w=g['w'];qs=g['queens'];sn=g['snapshots']
 nonlose=[int(r) for r,s in sn.items() if (s['us']['queen_length'],s['us']['longest'],s['us']['total']) >= (s['them']['queen_length'],s['them']['longest'],s['them']['total'])]
 print('\nGAME',gid,'last-nonlosing',max(nonlose,default=-1))
 if gid==1517698:
  qt=[t for t in g['qturns'] if t['id']==qs[0]][-3:];boards=[bm.board(g,t,-1) for t in qt]
  rows=['[M] r71 (5,1), W → (26,13); r72 (26,13), split → length 3; r73 (26,13), E → own neck (5,1).','```text','r71             r72             r73']
  rows+=['   '.join(r) for r in zip(*boards)];rows+=['```']
  (O/'boards.md').write_text('\n'.join(rows)+'\n');print('\n'.join(rows))
  for t in qt:
   c=t['body'][0][1]*w+t['body'][0][0];occ={tuple(c):(i,k) for i,b in t['state'].items() for k,c in enumerate(b)}
   print('neighbors',t['r'], [('NESW'[d],None if n<0 else (n%w,n//w),occ.get((n%w,n//w))) for d,n in enumerate(geo.nxt[c])]);print('queen component',geo.comp[c])
  ts=[t for t in g['qturns'] if t['id']==qs[1] and t['r']>=73];print('enemy queen heads',Counter(tuple(t['body'][0]) for t in ts));print('enemy component',set(geo.comp[t['body'][0][1]*w+t['body'][0][0]] for t in ts));print('post distances',Counter(t['d'] for t in g['post_near']))
 if gid==1517697:
  print('snapshots',[(r,sn[str(r)]) for r in (0,25,50,100,150,200,250,300,350,375,400,425,450,475,499)])
  for q in qs:
   ts=[t for t in g['qturns'] if t['id']==q];print('queen',q,'eats',[(t['r'],len(t['eats'])) for t in ts if t['eats']]);print('late',[(a,b,sum(len(t['eats']) for t in ts if a<=t['r']<=b),sum(len(t['moves']) for t in ts if a<=t['r']<=b)) for a,b in ((0,99),(100,299),(300,399),(400,499))]);print('q stationary count',sum(t['body']==t['end'] for t in ts))
  print('late deaths',[(d['round'],d['id'],d['length'],d['cause'],d['actor']) for d in g['deaths'] if d['side']=='us' and d['round']>=300]);print('r100 ids',[(t['id'],len(t['body']),t['body'][0]) for t in g['turns'] if t['r']==100 and t['side']==0])
 if gid==1517694:
  qts=[t for t in g['qturns'] if t['id']==qs[0]];print('queen component',geo.comp[qts[-1]['body'][0][1]*w+qts[-1]['body'][0][0]],'heads',Counter(tuple(t['body'][0]) for t in qts))
