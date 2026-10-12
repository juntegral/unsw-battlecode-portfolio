import sys,json,gzip
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path[:0]=['tools','data/analysis/ladder/dossier/local']
import ladder_replay as lr
from count_local import Geo
OUT=Path('data/codex/astra/sweep/0519/loss2')
FILES=['data/online/live-one1/b1491740/M1491744.replay','data/online/smoke/one10-c1-old/M1492091.replay','data/online/smoke/one10-c1-old/M1492092.replay']

def run(path):
 path=Path(path); gid=int(path.stem[1:]); meta=json.loads(path.with_name(f'game-{gid}.json').read_text())
 base=lr.scan(path,meta,str(path.parent),set()); root=lr.replay.load(path).root()
 w,h=map(int,root.text(0).splitlines()[0].split()[1:]); b={};team={};raw=[];pearls=set()
 for line in root.text(0).splitlines():
  q=line.split()
  if q[0]=='DRAGON':
   i=len(b);b[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));team[i]=int(q[1])
  elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
  elif q[0]=='TILE' and int(q[3]):pearls.add(int(q[2])*w+int(q[1]))
 geo=Geo(w,h,raw);turns=[];cur=None;r=-1;close=[];qdeath=False;qs=[min(i for i in b if team[i]==s) for s in (0,1)]
 def finish():
  if cur is not None:
   cur['end']={str(i):list(v) for i,v in b.items()};cur['pearls_end']=sorted(pearls)
 def ball(src,depth=5):
  d={src:0};q=deque([src])
  while q:
   x=q.popleft()
   if d[x]==depth:continue
   for y in geo.adj[x]:
    if y not in d:d[y]=d[x]+1;q.append(y)
  return d
 def tile(p):
  x,y=lr.replay.point(p);return y*w+x
 for idx,e in enumerate(root.pointer(3)):
  k=e.u16(0);p=e.pointer(0)
  if k==0:finish();cur=None;r=p.i32(0)
  elif k==1:
   finish();actor=p.i32(0)
   cur={'r':r,'event':idx,'id':actor,'team':team[actor],'start':{str(i):list(v) for i,v in b.items()},'pearls':sorted(pearls),'eats':0,'updates':[],'deaths':[],'splits':[]};turns.append(cur)
   if qdeath and qs[1] in b and team[actor]==0:
    d=ball(b[actor][0]);dst=d.get(b[qs[1]][0],999)
    if dst<=5:close.append({'r':r,'id':actor,'L':len(b[actor]),'distance':dst,'head':b[actor][0],'queen':b[qs[1]][0]})
  elif k==4:
   a=p.pointer(0);cur['action']={'kind':a.u16(0),'dirs':list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) else []}
  elif k==3:
   cell=tile(p.pointer(0))
   if p.u32(0):pearls.add(cell)
   else:pearls.discard(cell);cur['eats']+=1
  elif k==9:
   i=p.i32(0);hd=tile(p.pointer(0));tail=tile(p.pointer(1));v=b[i]
   if hd!=v[0]:v.appendleft(hd)
   while len(v)>1 and v[-1]!=tail:v.pop()
   assert v[-1]==tail
   if cur is not None:cur['updates'].append({'id':i,'body':list(v)})
  elif k==10:
   ids=[p.i32(0),p.i32(4)];cur['splits'].append(ids)
   for z,i in enumerate(ids):b[i]=deque(tile(pt) for pt in p.pointer(z));team[i]=p.u16(8)
  elif k==11:
   i=p.i32(0);cur['deaths'].append({'id':i,'reason':p.u16(4),'body':list(b[i])});b.pop(i)
   if i==qs[0]:qdeath=True
 finish()
 summary={k:base[k] for k in ['gid','map','bots','queens','q_eats','q_splits','final','last_round','end_reason','winner','eats','anomalies']}
 summary['queen_deaths']=[d for d in base['deaths'] if d['id'] in qs];summary['close5']=close
 summary['checkpoints']={r:base['snapshots'][r] for r in [0,10,25,50,100,150,200,250,300,350,400,450,499] if r in base['snapshots']}
 def losing(st):
  a,c=st['us'],st['them'];return (a['queen_length'],a['longest'],a['total'])<(c['queen_length'],c['longest'],c['total'])
 rounds=sorted(base['snapshots']);summary['last_nonlosing']=max((r for r in rounds if not losing(base['snapshots'][r])),default=None)
 (OUT/f'{gid}-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));
 with gzip.open(OUT/f'{gid}-turns.json.gz','wt',compresslevel=1) as output:json.dump({'w':w,'h':h,'team':team,'turns':turns,'raw':raw},output,separators=(',',':'))
 print(json.dumps({k:v for k,v in summary.items() if k not in ['close5','checkpoints']},ensure_ascii=False));print('close5',len(close),close[:4]);print('queen last turns',[(t['r'],len(t['start'][str(qs[0])]),t.get('action'),t['deaths']) for t in turns if t['id']==qs[0]][-3:])
for path in FILES:run(path)
