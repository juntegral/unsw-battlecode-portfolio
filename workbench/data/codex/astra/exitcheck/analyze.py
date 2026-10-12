import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, importlib.util, hashlib, gzip
from collections import Counter,deque
from datetime import datetime
R=Path.cwd(); O=Path(__file__).parent
sys.path[:0]=[str(R/'tools'),str(R/'data/analysis/ladder/dossier/online')]
import ladder_replay as lr
import label_report
spec=importlib.util.spec_from_file_location('geo',R/'data/codex/astra/evade/analyze.py');gm=importlib.util.module_from_spec(spec);spec.loader.exec_module(gm)
BOTS={'21126':8,'21165':9,'21200':10,'21269':11}
def inventory():
 inv=label_report.directory_inventory('exitcheck',','.join(str(R/p) for p in ['data/online/smoke/one8-*-old','data/online/smoke/one9-*-old','data/online/smoke/one10-*-old','data/online/smoke/one11-*-old','data/online/live-one1/b*']))
 jobs=[];ignored=Counter(); errors=[]
 for jnum,(path,meta) in enumerate(inv['jobs']):
  if jnum%100==0:print('header',jnum,flush=True)
  try:
   with path.open('rb') as fh: prefix=fh.read(262144)
   if prefix[:2]==b'\x1f\x8b':
    with gzip.open(path,'rb') as fh:prefix=fh.read(262144)
   try:raw=lr.replay.unpack_packed(prefix+bytes(4096))
   except IndexError:raw=lr.replay.unpack_packed(prefix+bytes(4097))
   root=lr.replay.Message(raw).root();bot=root.text(1+int(meta['teamAId']!=1119))
   if not bot.isdigit():root=lr.replay.load(path).root();bot=root.text(1+int(meta['teamAId']!=1119))
   if bot not in BOTS:ignored[bot]+=1;continue
   jobs.append(dict(gid=meta['id'],v=BOTS[bot],bot=bot,path=str(path.relative_to(R)),meta=meta,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
  except Exception as e:errors.append([str(path),repr(e)])
 out=dict(time=datetime.now().astimezone().isoformat(),games=jobs,duplicates=inv['duplicate_ids'],notes=inv['notes'],errors=errors,ignored=dict(ignored))
 (O/'inventory.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('inventory',dict(Counter(j['v'] for j in jobs)),flush=True)
 return jobs

def scan(j):
 root=lr.replay.load(R/j['path']).root();assert root.text(1+int(j['meta']['teamAId']!=1119))==j['bot'];assert root.pointer(4).bit(0);g=gm.Geo(root.text(0));bs={};ts={};ps=set();own=int(j['meta']['teamAId']!=1119)
 for q in map(str.split,root.text(0).splitlines()):
  if q and q[0]=='DRAGON':
   i=len(bs);bs[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));ts[i]=int(q[1])
 queen=min(i for i in bs if ts[i]==own);rnd=0;cur=None;qt=[];closures=[];death=None;sig=[];logs=[];history=deque(maxlen=2000);logcount=0
 def man(a,b):
  dx=abs(a[0]-b[0]);dy=abs(a[1]-b[1]);return min(dx,g.w-dx)+min(dy,g.h-dy)
 def occ():return {c:(i,k) for i,b in bs.items() for k,c in enumerate(b)}
 def exits(qh=None,skip=None):
  if qh is None:
   if queen not in bs:return []
   qh=bs[queen][0]
  oc={c for i,b in bs.items() if i!=skip for c in b}
  return [n for n in g.moves[qh] if n is not None and n not in oc]
 def state():return {'bodies':{i:list(b) for i,b in bs.items()},'pearls':list(ps)}
 def snap():
  qh=bs[queen][0];oc=occ();n=[]
  for d,c in enumerate(g.moves[qh]):
   n.append(dict(d='NESW'[d],cell=c,edge=g.edges.get(lr.edge_id(g.w,g.h,*qh,d),(0,-1))[0],occupant=oc.get(c)))
  return dict(head=qh,L=len(bs[queen]),exits=exits(),neighbors=n,**state())
 def finish():
  nonlocal cur
  if not cur:return
  i=cur['id'];cur['endbody']=list(bs.get(i,()));cur['endexits']=exits();cur['qh_end']=bs[queen][0] if queen in bs else None
  if i==queen:qt.append(cur)
  if queen in bs and i!=queen and cur['before'] and not cur['endexits']:
   cur['remove_exits']=exits(skip=i);cur['afterstate']=state();closures.append(cur)
  if j['v']==11 and i!=queen and ts[i]==own and cur['L'] in (2,3) and cur.get('qvisible') and cur.get('distance',99)<=2:
   if cur.get('self_death'):
    cur['signal']='self-death';cur['remove_exits']=exits();sig.append(cur)
   elif cur.get('snapshot') and cur['endbody'] and cur['endexits']:
    st=cur['snapshot'];bb={int(z):list(map(tuple,b)) for z,b in st['bodies'].items()};oo={c for z,b in bb.items() if z!=i for c in b};pe=set(map(tuple,st['pearls']));blocked=[]
    for di,n in enumerate(g.moves[tuple(cur['body'][0])]):
     if n is None or n in oo or n in cur['body']:continue
     nb=[n]+cur['body'] if n in pe else [n]+cur['body'][:-1]
     if all(t is None or t in oo or t in nb for t in g.moves[tuple(cur['qh'])]):blocked.append(di)
    if blocked:cur['signal']='alternative-cell';cur['blocking_alternatives']=blocked;sig.append(cur)
  history.append(cur);cur=None
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k in (0,1):finish()
  if k==0:rnd=p.i32(0)
  elif k==1:
   i=p.i32(0)
   if queen not in bs:
    cur=None
    continue
   h=bs[i][0];qh=bs[queen][0]
   cur=dict(r=rnd,event=idx,id=i,team=ts[i],L=len(bs[i]),body=list(bs[i]),before=exits(),qh=qh,qvisible=g.visible(qh,h),distance=man(qh,h),dirs=[],path=[],split=0)
   if i==queen:cur['snapshot']=snap()
   elif ts[i]==own and (g.visible(qh,h) or rnd%100==999):cur['snapshot']=snap()
  elif k==4 and cur:
   a=p.pointer(0);cur['action']=a.u16(0) if a else None;cur['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) else [];cur['split_size']=a.i32(4) if a and a.u16(0)==1 else 0
  elif k==6:
   logcount+=1;t=p.text(0)
   if 'QSTRICT' in t:logs.append(dict(r=rnd,id=p.i32(0),text=t))
  elif k==3:
   c=lr.replay.point(p.pointer(0))
   if p.u32(0):ps.add(c)
   else:ps.discard(c)
  elif k==9:
   i=p.i32(0);h=lr.replay.point(p.pointer(0));tail=lr.replay.point(p.pointer(1));b=bs[i]
   if h!=b[0]:
    b.appendleft(h)
    if cur and cur['id']==i:cur['path'].append(h)
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):bs[i]=deque(lr.replay.point(c) for c in p.pointer(z));ts[i]=p.u16(8)
   if cur:cur['split']=p.i32(4)
  elif k==11:
   i=p.i32(0);reason=p.u16(4)
   if cur and i==cur['id']:cur['death_reason']=reason;cur['self_death']=reason==1
   if i==queen:
    death=dict(r=rnd,L=len(bs[i]),reason=reason,actor=cur['id'] if cur else None,event=idx,snapshot=snap())
   bs.pop(i)
  if death and j['v']!=11:
   finish();break
 finish()
 for x in sig:x['queen_next10']='dead' if death and death['r']<=x['r']+10 else 'alive' if rnd>=x['r']+10 else 'censored'
 if death:
  recent=qt[-2:]; corner=any(len(t['before'])<=1 or (t['endbody'] and len(t['endexits'])<=1) for t in recent)
  selected=death['reason']!=3 or corner
 else:recent=[];selected=False
 return dict(gid=j['gid'],v=j['v'],path=j['path'],map=j['meta']['mapName'],queen=queen,own=own,w=g.w,h=g.h,death=death,selected=selected,turns=qt[-8:] if death else [],closures=[x for x in closures if not death or x['r']>=death['r']-8],signals=sig,logs=logs,logcount=logcount,last_round=rnd,history=[t for t in history if death and t['r']>=death['r']-6])
if __name__=='__main__':
 jobs=inventory()
 for j in jobs:
  f=O/f'g{j["gid"]}.json'
  if not f.exists():
   out=scan(j);f.write_text(json.dumps(out,ensure_ascii=False));print(j['gid'],j['v'],out['death'] and (out['death']['r'],out['death']['reason']),out['selected'],flush=True)
 rows=[json.loads((O/f'g{j["gid"]}.json').read_text()) for j in jobs]
 (O/'summary.json').write_text(json.dumps(dict(games=dict(Counter(x['v'] for x in rows)),deaths=dict(Counter(x['v'] for x in rows if x['death'])),selected=dict(Counter(x['v'] for x in rows if x['selected'])),rows=[{k:x[k] for k in ('gid','v','selected','logcount','logs')} for x in rows]),indent=2))
