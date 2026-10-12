import sys,json,importlib.util
from pathlib import Path
from collections import deque
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
sys.path.insert(0,'tools');import ladder_replay as lr
spec=importlib.util.spec_from_file_location('cr','data/analysis/ladder/losses/counts/count_replays.py');cr=importlib.util.module_from_spec(spec);spec.loader.exec_module(cr)
result={}
for gid in (1497389,1497390,1496711):
 b=json.loads((OUT/f'{gid}-base.json').read_text());d=json.loads((OUT/f'{gid}-detail.json').read_text());g=cr.Geometry(d['w'],d['h'],[tuple(map(int,x.split()[1:4])) for x in b['text'].splitlines() if x.startswith('EDGE ')])
 summary={'bots':b['bots'],'last_round':b['last_round'],'final':b['final'],'permanent_deficits':{},'bands':{}}
 for key in ('longest','total','queen_length'):
  equalbetter=[int(r) for r,v in b['snapshots'].items() if v['us'][key]>=v['them'][key]];last=max(equalbetter,default=-1);summary['permanent_deficits'][key]=last+1 if last<b['last_round'] else None
 for lo,hi in ((0,49),(50,99),(100,299),(300,399),(400,499),(450,499)):
  vals={}
  for side,si in [('us',d['own']),('them',1-d['own'])]:
   ts=[t for t in d['turns'] if t['side']==si and lo<=t['round']<=hi];gross=sum(t['eats'] for t in ts);drops=sum(x['eater']==side and x['eat_round'] is not None and lo<=x['eat_round']<=hi for x in b['pearls']);vals[side]={'turns':len(ts),'eats':gross,'natural':gross-drops,'splits':sum(t['action']['type']==1 for t in ts),'no_action':sum(t['action']['type']==2 for t in ts)}
  summary['bands'][f'{lo}-{hi}']=vals
 summary['own_deaths_ge10']=sum(x['side']=='us' and x['length']>=10 for x in b['deaths'])
 summary['our_final']=[{'id':int(i),'length':len(bb)} for i,bb in d['final'].items() if d['teams'][i]==d['own']]
 summary['post_queen_positions']={'unique':len(set(d['enemy_positions'].values())),'last':list(d['enemy_positions'].items())[-1:]}
 if gid==1497389:
  root=lr.replay.load('data/online/live-one1/b1497386/M1497389.replay').root();bodies={};pearls=set();r=-1;opps=[];w=d['w']
  for line in b['text'].splitlines():
   a=line.split()
   if a[0]=='DRAGON':bodies[len(bodies)]=deque(int(a[4+2*k])*w+int(a[3+2*k]) for k in range(int(a[2])))
  for ev in root.pointer(3):
   k=ev.u16(0);p=ev.pointer(0)
   if k==0:r=p.i32(0)
   elif k==1:
    i=p.i32(0)
    if d['teams'][str(i)]==d['own']:
     occ={c for bb in bodies.values() for c in bb};hd=bodies[i][0];ps=[n for kind,n in g.moves[hd] if kind!=1 and n in pearls and n not in occ]
     if ps:opps.append({'round':r,'id':i,'head':hd,'adjacent_pearls':ps})
   elif k==3:
    pt=lr.replay.point(p.pointer(0));c=pt[1]*w+pt[0]
    if p.u32(0):pearls.add(c)
    else:pearls.remove(c)
   elif k==9:
    i=p.i32(0);pt=lr.replay.point(p.pointer(0));hd=pt[1]*w+pt[0];pt=lr.replay.point(p.pointer(1));tl=pt[1]*w+pt[0];bb=bodies[i]
    if bb[0]!=hd:bb.appendleft(hd)
    while len(bb)>1 and bb[-1]!=tl:bb.pop()
   elif k==10:
    for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(lr.replay.point(c)[1]*w+lr.replay.point(c)[0] for c in p.pointer(z))
   elif k==11:bodies.pop(p.i32(0))
  summary['legal_adjacent_pearl_turns']=opps
 result[gid]=summary
(OUT/'checks.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
