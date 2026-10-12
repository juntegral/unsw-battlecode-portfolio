import sys,json,ast,importlib.util,re
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,defaultdict,Counter
from functools import lru_cache
sys.path[:0]=['tools','data/analysis/ladder/dossier/work','data/analysis/ladder/dossier/online']
from ladder_replay import replay,canonical_edges,edge_id
from o1_scan import scan as ledger
import label_report as lr
load_replay=lr.agg.sb.load_replay
OUT=Path('data/codex/astra/audit-hunt')
# Import the existing geometry and decoder without their command-line entry points.
def definitions(path,names,ns):
 tree=ast.parse(Path(path).read_text());nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names]
 exec(compile(ast.Module(body=nodes,type_ignores=[]),path,'exec'),ns)
ns=dict(canonical_edges=canonical_edges,edge_id=edge_id,defaultdict=defaultdict,deque=deque,STEP=((0,-1),(1,0),(0,1),(-1,0)),INF=9999)
definitions('data/analysis/ladder/dossier/work/ta_scan.py',{'Geo'},ns);Geo=ns['Geo']
ns=dict(MASK=(1<<64)-1,CHECK=255<<55,TAG=3<<53)
definitions('data/codex/astra/rallyloss/analyze.py',{'rot','prf','wire_decoder'},ns);wire_decoder=ns['wire_decoder']

def trace(job):
 root=load_replay(Path(job['path'])).root();j=job['meta'];own=int(j['teamAId']!=1119);ver=int(job['version'][3:]);lines=[l.split() for l in root.text(0).splitlines()];w,h=map(int,lines[0][1:3]);raw=[];bs={};teams={};tt={};serial=0
 def new():
  nonlocal serial
  serial+=1;return serial
 for q in lines:
  if q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
  elif q[0]=='DRAGON':
   i=len(bs);bs[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));teams[i]=int(int(q[1])!=own);tt[i]=deque(new() for c in bs[i])
 starts=[sum(len(b) for i,b in bs.items() if teams[i]==s) for s in (0,1)]
 queens=[min(i for i in bs if teams[i]==s) for s in (0,1)];geo=Geo(w,h,raw);decode=wire_decoder(w,h,2 if own==0 else 1)
 rev=[[] for _ in geo.adj]
 for c,ns in enumerate(geo.adj):
  for n in ns:rev[n].append(c)
 @lru_cache(maxsize=256)
 def distances(target):
  ds=[99999]*(w*h);ds[target]=0;queue=deque([target])
  while queue:
   c=queue.popleft()
   for n in rev[c]:
    if ds[n]==99999:ds[n]=ds[c]+1;queue.append(n)
  return ds
 def top(s):return max((i for i in bs if teams[i]==s),key=lambda i:(len(bs[i]),-i),default=None)
 def shot(src,target,L,occ,visible_only=False,noportal=False,cap=None):
  limit=(L+3)//4+L-2
  if cap is not None:limit=min(limit,cap)
  ds=distances(target)
  if ds[src]>limit+len(pearls):return None
  plainq=deque([(src,[])]);plainseen={src};plainpath=None
  while plainq:
   c,path=plainq.popleft()
   for d,(kind,n) in enumerate(geo.moves[c]):
    if kind==1 or n in plainseen or (noportal and kind==2) or (visible_only and not geo.visible(src,n)):continue
    if n==target:plainpath=path+[d];break
    if n in occ:continue
    plainseen.add(n);plainq.append((n,path+[d]))
   if plainpath is not None:break
  if plainpath is None:return None
  if len(plainpath)<=limit:return plainpath
  # Simple paths, with consumed pearls in the state; no reliance on vacating bodies.
  queue=deque([(src,[],frozenset([src]),frozenset(),limit)]);best={};work=0
  while queue:
   c,path,seen,ate,left=queue.popleft();work+=1
   if work>20000:
    coverage['path_search_truncated']+=1;return None
   for d,(kind,n) in enumerate(geo.moves[c]):
    if kind==1 or n in seen or (noportal and kind==2) or (visible_only and not geo.visible(src,n)):continue
    if n==target and left>=1:return path+[d]
    if n in occ:continue
    gain=n in pearls and n not in ate
    nl=left-1+gain
    if nl<1 or ds[n]>nl+len(pearls)-len(ate)-gain:continue
    na=ate|{n} if gain else ate;key=(n,na)
    if best.get(key,-1)>=nl:continue
    best[key]=nl;queue.append((n,path+[d],seen|{n},na,nl))
  return None
 rnd=-1;actor=None;cur=None;pearls={};pending=None;drop=None;expected=0
 deaths=[];transfers=[];reach=[];qturns=[];snaps={};states=Counter();coverage=Counter();logs=Counter();wires={};qgame=set();candidates={};labels=defaultdict(set);lost=Counter();ever=defaultdict(set);transport=defaultdict(set);all_eats=[0,0];all_dead=[0,0];all_paid=[0,0]
 def snapshot():return [[sum(teams[i]==s for i in bs),sum(len(b) for i,b in bs.items() if teams[i]==s),len(bs[top(s)]) if top(s) is not None else 0,len(bs.get(queens[s],()))] for s in (0,1)]
 def candidate(i,wire):
  if i in candidates:return
  c=dict(id=i,r=rnd,L=len(bs[i]),leader=wire['id'],leaderL=wire['L'],age=rnd-wire['r'],distance=geo.tman(bs[i][0],wire['cell']),tokens=list(tt[i]),arrival=None,death=None,inward=0,moves=0)
  c.update(actual_leaderL=len(bs.get(wire['id'],())),global_top=top(0),actual_ratio_ok=len(bs.get(wire['id'],()))>=len(bs[i])*2)
  candidates[i]=c
  for token in tt[i]:labels[token].add(i)
 def finish():
  nonlocal cur
  if cur is None:return
  i=cur['id'];s=teams[i];cur['endL']=len(bs.get(i,()));cur['paid']=cur['total0']+cur['eats']-cur['deadmass']-sum(len(b) for z,b in bs.items() if teams[z]==s)
  assert cur['paid']>=0,(j['id'],cur)
  all_paid[s]+=cur['paid'];cur['end']=bs[i][0] if i in bs else None
  if s==0:
   wire=cur['wire'];qg=i in qgame;fr=300 if qg else 400;phase=rnd>fr or (rnd>350 and cur['units']>=56)
   islead=wire and wire['id']==i and rnd>(300 if w*h<=1200 else 150) and not(w*h>1200 and not phase and cur['units']<56 and cur['L']<10)
   cur['is_leader_proxy']=bool(islead)
   if cur.get('reach') is not None:
    reasons=[]
    if not cur['visible']:reasons.append('head_not_visible:2359,2381')
    if i==queens[0]:reasons.append('real_queen_excluded:3533')
    if islead:reasons.append('leader_excluded:3533,4769')
    limit=0 if ver in (5,7) else 64 if ver==10 else 4;steps=5 if ver==10 else 3
    if cur['L']>limit:reasons.append('sure_len_disabled_or_exceeded:75,3533')
    if cur['man']>steps:reasons.append('sure_manhattan_limit:3535')
    if cur['sure_path'] is None:reasons.append('no_sure_path_within_code_budget:3597-3631')
    if not cur['hitqueen'] and not reasons:reasons.append('unresolved_internal_memory_or_override')
    cur['reasons']=reasons;reach.append({k:v for k,v in cur.items() if k not in ('total0','deadmass','mates')})
   if i==queens[0]:qturns.append({k:v for k,v in cur.items() if k in ('r','id','L','head','end','endL','nearest','mate5','units','visible_mates','is_leader_proxy','paid')})
   # Proxy only: source does not emit RALLY activation or hidden trader/escape state.
   lengthok=wire and (cur['L']*2<=wire['L'] or (ver==10 and wire['id']==queens[0] and 2<=wire['L']<6 and cur['L'] in (2,3)))
   eligible=wire and rnd>=350 and rnd>fr and i!=queens[0] and i!=wire['id'] and rnd-wire['r']<=5 and lengthok and cur['units']>3 and geo.tman(cur['head'],wire['cell'])>15
   if eligible and i in bs:
    candidate(i,wire);c=candidates[i];coverage['rally_proxy_turns']+=1
    if cur['end']!=cur['head']:
     c['moves']+=1;c['inward']+=geo.tman(cur['end'],wire['cell'])<geo.tman(cur['head'],wire['cell'])
  cur=None
 def arrivals():
  lead=top(0)
  if lead is None:return
  for i,c in candidates.items():
   if c['arrival'] is None and i in bs and i!=lead and geo.tman(bs[i][0],bs[lead][0])<=3:c['arrival']=[rnd,lead]
 for ev in root.pointer(3):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:
   finish();arrivals()
   if rnd in (300,350,400):snaps[str(rnd)]=snapshot()
   rnd=p.i32(0);actor=None
  elif k==1:
   finish();arrivals();actor=p.i32(0);s=teams[actor];L=len(bs[actor]);hd=bs[actor][0]
   cur=dict(r=rnd,id=actor,L=L,head=hd,total0=sum(len(b) for i,b in bs.items() if teams[i]==s),units=sum(teams[i]==s for i in bs),eats=0,deadmass=0,steps=0,hitqueen=False,wire=None,action=None,logs=[],reach=None,sure_path=None)
   if s==0 and queens[1] in bs:
    target=bs[queens[1]][0];vis=geo.visible(hd,target);budget=(L+3)//4+L-2
    cur.update(visible=vis,man=geo.tman(hd,target),queen_alive=queens[0] in bs,foeqL=len(bs[queens[1]]),rank=1+sum(len(b)>L for i,b in bs.items() if teams[i]==0),second_by_id=sorted((i for i in bs if teams[i]==0),key=lambda i:(-len(bs[i]),i))[1:2]==[actor])
    if distances(target)[hd]<=budget+min(len(pearls),5):
     occ={c for b in bs.values() for c in b};path=shot(hd,target,L,occ)
     if path is not None:
      cur['reach']=len(path);cur['path']=path;cur['free_reach']=len(path)<=(L+3)//4
      if vis:cur['sure_path']=shot(hd,target,L,occ,True,True,5 if ver==10 else 3)
   if s==0 and actor==queens[0]:
    mates=[b[0] for i,b in bs.items() if teams[i]==0 and i!=actor];cur.update(nearest=min((geo.tman(hd,c) for c in mates),default=999),mate5=sum(geo.tman(hd,c)<=5 for c in mates),visible_mates=sum(geo.visible(hd,c) for c in mates))
  elif k==3:
   c=replay.point(p.pointer(0));cell=c[1]*w+c[0]
   if p.u32(0):
    if expected:
     token,coord=drop['drop_tokens'].popleft();assert coord==cell;pearls[cell]=(token,drop);expected-=1
    else:pearls[cell]=(new(),None)
   else:
    pending=pearls.pop(cell);token,src=pending;all_eats[teams[actor]]+=1;cur['eats']+=1
    if src:
     row=dict(r=rnd,eater=actor,side=teams[actor],queen=actor==queens[teams[actor]],top=actor==top(teams[actor]),source=src['id'],source_side=src['side'],death_r=src['r'],cause=src['cause'],sourceL=src['L'],eaterL=len(bs[actor]),cell=cell)
     transfers.append(row);src['eaters'].append(row)
     for i in labels[token]:
      if teams[actor]==0:
       transport[i].add(token)
       if row['top']:ever[i].add(token)
  elif k==4:
   a=p.pointer(0);cur['action']=dict(kind=a.u16(0) if a else None,dirs=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else [])
  elif k==6:
   val=p.text(0);logs[val.split()[0] if val.split() else 'empty']+=1
   if cur:cur['logs'].append(val)
  elif k==9:
   i=p.i32(0);a,b=replay.point(p.pointer(0)),replay.point(p.pointer(1));hd,tail=a[1]*w+a[0],b[1]*w+b[0];bb=bs[i];tokens=tt[i]
   if hd!=bb[0]:
    token=pending[0] if pending else tokens.pop();pending=None;bb.appendleft(hd);tokens.appendleft(token)
    while len(bb)>1 and bb[-1]!=tail:bb.pop()
    while len(tokens)>len(bb):
     tok=tokens.pop()
     for z in labels[tok]:lost[z]+=1
    assert len(tokens)==len(bb)
    if i==actor:cur['steps']+=1
   assert bb[-1]==tail
  elif k==10:
   i,child=p.i32(0),p.i32(4);mapping=dict(zip(bs[i],tt[i]));teams[child]=teams[i]
   for z,unit in enumerate((i,child)):
    bs[unit]=deque(replay.point(c)[1]*w+replay.point(c)[0] for c in p.pointer(z));tt[unit]=deque(mapping[c] for c in bs[unit])
  elif k==11:
   i=p.i32(0);reason=p.u16(4);s=teams[i];L=len(bs[i]);cause=['wall','own body','body','ram','stop'][reason] if reason<=4 else str(reason)
   if reason==3:cause='rammed' if i!=actor and teams[actor]!=s else 'rams' if any(d['r']==rnd and d['actor']==actor and d['cause']=='rammed' for d in deaths[-2:]) else 'mate head'
   d=dict(id=i,r=rnd,side=s,L=L,queen=i==queens[s],actor=actor,cause=cause,reason=reason,eaters=[],top=i==top(s))
   if reason==3 and i==queens[1] and teams[actor]==0 and actor!=i:
    cur['hitqueen']=True;d['rammer']=dict(id=actor,L=cur['L'],steps=cur['steps']+1,free_steps=(cur['L']+3)//4,paid_before_hit=cur['L']+cur['eats']-len(bs[actor]),L_at_hit=len(bs[actor]),rank=cur['rank'],second_by_id=cur['second_by_id'])
   if s==teams[actor]:cur['deadmass']+=L
   all_dead[s]+=L;deaths.append(d)
   if i in candidates:candidates[i]['death']=[rnd,cause,L]
   for z,tok in enumerate(tt[i]):
    if z%2:
     for who in labels[tok]:lost[who]+=1
   d['drop_tokens']=deque((tok,c) for z,(tok,c) in enumerate(zip(tt[i],bs[i])) if z%2==0);drop=d;expected=len(d['drop_tokens']);bs.pop(i);tt.pop(i)
  elif k==12:
   sender=p.i32(0)
   if teams.get(sender)!=0:continue
   plain=decode(p.u64(16));assert plain is not None
   coverage['decoded_sonar']+=1
   if plain>>63==0:
    state=(plain>>26)&3;states[state]+=1;wire=dict(state=state,id=plain&32767,L=(plain>>16)&1023,r=(plain>>28)&511,cell=((plain>>44)&127)*w+((plain>>37)&127))
    if plain&32768:qgame.add(sender)
    if cur and sender==actor:cur['wire']=wire
   elif (plain>>42)&2047==0x2b5:states[(plain>>24)&3]+=1
 finish();arrivals();snaps['end']=snapshot();snaps['last_round']=rnd
 checks=[]
 for s in (0,1):
  residual=starts[s]+all_eats[s]-all_dead[s]-all_paid[s]-snaps['end'][s][1];assert residual==0
  official=root.pointer(4).pointer(own if s==0 else 1-own);actual=snaps['end'][s];assert actual==[official.i32(0),official.i32(8),official.i32(4),official.i32(12)],(j['id'],actual)
  checks.append(residual)
 live_tokens={t for tokens in tt.values() for t in tokens}|{p[0] for p in pearls.values()};lead=top(0);endtokens=set(tt[lead]) if lead is not None else set()
 for i,c in candidates.items():
  initial=set(c.pop('tokens'));c.update(lost=lost[i],remaining=len(initial&live_tokens),ever_top=len(ever[i]),end_top=len(initial&endtokens&transport[i]))
  assert c['L']==c['lost']+c['remaining']
 for d in deaths:d.pop('drop_tokens',None)
 fin=root.pointer(4);winner=fin.u16(6) if fin.u16(4)==1 else None;end=snaps['end'];how='elim' if not end[0][0] or not end[1][0] else 'queen' if end[0][3]!=end[1][3] else 'longest' if end[0][2]!=end[1][2] else 'total'
 return dict(revision=3,gid=j['id'],version=job['version'],bot=job['bot'],map=j['mapName'],opponent=j['teamBName' if own==0 else 'teamAName'],path=job['path'],queens=queens,result='draw' if winner is None else 'win' if winner==own else 'loss',how=how,snaps=snaps,deaths=deaths,transfers=transfers,reach=reach,qturns=qturns,candidates=list(candidates.values()),states=dict(states),coverage=dict(coverage),logs=dict(logs),checks=checks)

def work(job):
 dest=OUT/f"game-{job['gid']}.json"
 if dest.exists() and json.loads(dest.read_text()).get('revision',0)>=2 and not json.loads(dest.read_text())['coverage'].get('path_search_truncated',0):return str(job['gid'])+' cached'
 result=trace(job);dest.write_text(json.dumps(result,separators=(',',':'),ensure_ascii=False));return f"{job['version']} {job['gid']} reach={len(result['reach'])}"
def main():
 from concurrent.futures import ProcessPoolExecutor,as_completed
 jobs=json.loads((OUT/'inventory.json').read_text())['rows']
 with ProcessPoolExecutor(max_workers=2) as pool:
  for f in as_completed([pool.submit(work,job) for job in jobs]):print(f.result(),flush=True)
if __name__=='__main__':main()
