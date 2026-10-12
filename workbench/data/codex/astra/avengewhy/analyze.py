import sys,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,defaultdict,Counter
sys.path[:0]=['tools','data/analysis/ladder/dossier/work','../battlecode/work']
from ladder_replay import replay
import ast
from ladder_replay import canonical_edges,edge_id
_geo=Path("data/analysis/ladder/dossier/work/ta_scan.py")
_tree=ast.parse(_geo.read_text());_ns=dict(canonical_edges=canonical_edges,edge_id=edge_id,defaultdict=defaultdict,deque=deque,STEP=((0,-1),(1,0),(0,1),(-1,0)),INF=9999)
exec(compile(ast.Module(body=[n for n in _tree.body if isinstance(n,ast.ClassDef) and n.name=="Geo"],type_ignores=[]),str(_geo),"exec"),_ns)
Geo=_ns["Geo"]
from o1_scan import scan as ledger
from card_42_check import make_key,unseal
OUT=Path('data/codex/astra/avengewhy'); SM=Path('data/online/smoke')
TARGET={1485169,1485170,1485174,1485181,1485182}

def detail(path,j):
 root=replay.load(path).root(); lines=[l.split() for l in root.text(0).splitlines()]; w,h=map(int,lines[0][1:3]);raw=[];bs={};team={};pearls={}
 for q in lines:
  if q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
  if q[0]=='DRAGON':
   i=len(bs);bs[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));team[i]=int(q[1])
 g=Geo(w,h,raw); own=int(j['teamAId']!=1119); queens=[min(i for i in bs if team[i]==s) for s in (own,1-own)]
 tag=2 if own==0 else 1; key=make_key(w,h,tag);streams={};opened={};inbox=defaultdict(list);states=defaultdict(int);lastseen={};known={};distance={}
 rnd=-1;actor=None;cur=None;qd=None;expect=0;drop=None;snaps=[];turns=[];claims=[];pings=[];qturns=[];deaths=[];prev_qseen={};logs=Counter();steps=0;dirs=[];observations=[]
 def pt(p):x,y=replay.point(p);return y*w+x
 def xy(c):return [c%w,c//w]
 def dist(c):
  if c not in distance:distance[c]=g.bfs([c])
  return distance[c]
 def shot(src,target,L,occ):
  # Empty-cell shortest path, blocking every body's current cells. This matches hunt_path's body conservatism.
  limit=(L+3)//4+L-2; seen={src};qu=deque([(src,[])])
  while qu:
   c,path=qu.popleft()
   if len(path)>=limit:continue
   for d,(kind,n) in enumerate(g.moves[c]):
    if kind==1 or n in seen:continue
    np=path+[d]
    if n==target:return np
    if n in occ:continue
    seen.add(n);qu.append((n,np))
  return None
 def pearl_shot(src,target,L,occ):
  budget=(L+3)//4+L-2; qu=deque([(src,[],frozenset(),budget)]);best={(src,frozenset()):budget}
  while qu:
   c,path,ate,left=qu.popleft()
   if len(path)>=12:continue
   for d,(kind,n) in enumerate(g.moves[c]):
    if kind==1:continue
    if n==target and left>=1:return path+[d]
    if n in occ:continue
    gain=n in pearls and n not in ate
    if left+gain<1:continue
    na=ate|{n} if gain else ate;nl=left+gain-1
    if best.get((n,na),-1)>=nl:continue
    best[n,na]=nl;qu.append((n,path+[d],na,nl))
  return None
 def finish():
  nonlocal cur
  if cur is None:return
  cur['end']=xy(bs[actor][0]) if actor in bs else None
  cur['endL']=len(bs.get(actor,()))
  vals=cur.pop('sent_states');cur['state_wire']=sorted(set(vals));cur['state_after']=max(vals,default=cur['state_received'])
  states[actor]=cur['state_after']
  if vals and max(vals)>cur['state_received']:
   claims.append(dict(r=rnd,id=actor,before=cur['state_received'],after=max(vals),prev_queen=cur['prev_queen'],queen_seen=cur['queen_seen'],corpse_candidate=cur['corpse_candidate']))
  if cur['reach'] is not None:turns.append(cur)
  if actor==queens[0]:qturns.append(cur)
  cur=None
 def snapshot():
  if qd is None or queens[1] not in bs:return
  tq=bs[queens[1]][0];ours=[i for i in bs if team[i]==own];ds=dist(tq);near=min(ours,key=lambda i:(ds[bs[i][0]],i))
  snaps.append(dict(r=rnd,q=xy(tq),view=sum(g.visible(bs[i][0],tq) for i in ours),nearest=[near,ds[bs[near][0]],len(bs[near])],small=sum(len(bs[i])<=4 for i in ours),armed=sum(states[i]%2==1 for i in ours)))
 for ev in root.pointer(3):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:
   finish()
   if rnd>=0:snapshot()
   rnd=p.i32(0);actor=None
  elif k==1:
   finish();actor=p.i32(0);L=len(bs[actor]);hd=bs[actor][0];steps=0;dirs=[]
   if team[actor]!=own:continue
   received=inbox.pop(actor,[]);before=states[actor];state=max([before]+[z['state'] for z in received if 'state'in z]);seenq=queens[0] in bs and any(g.visible(hd,c) for c in bs[queens[0]])
   if seenq and state==1:state=2
   seenhead=queens[0] in bs and g.visible(hd,bs[queens[0]][0]);prev=prev_qseen.get(actor)
   candidate=prev is not None and prev[0]==rnd-1 and not seenq and g.visible(hd,prev[1]) and prev[1] in pearls and prev[2]==False
   cur=dict(r=rnd,id=actor,L=L,head=xy(hd),state_received=state,received=received,sent_states=[],queen_seen=seenq,prev_queen=prev,corpse_candidate=candidate,reach=None,path=[],action=None,eats=[],splits=[],hits=[],pings=[],queen_game_tag=False)
   if prev is not None or seenq:
    observations.append(dict(r=rnd,id=actor,head=xy(hd),prev=prev,queen_head=xy(bs[queens[0]][0]) if queens[0] in bs else None,seenq=seenq,prev_in_view=prev is not None and g.visible(hd,prev[1]),prev_pearl=prev is not None and prev[1] in pearls,prev_origin=pearls.get(prev[1]) if prev else None,candidate=candidate))
   if actor==queens[0]:
    cur['mates']=[[i,len(b),g.tman(hd,b[0]),g.visible(hd,b[0])] for i,b in bs.items() if i!=actor and team[i]==own]
    cur['enemy_heads']=sum(team[i]!=own and g.visible(hd,b[0]) for i,b in bs.items())
   prev_qseen[actor]=[rnd,bs[queens[0]][0],bs[queens[0]][0] in pearls] if seenhead else None
   if queens[1] in bs:
    tq=bs[queens[1]][0];vis=g.visible(hd,tq)
    if vis:known[actor]=(rnd,tq,'sight')
    for z in received:
     if z.get('kind')=='queen' and not z['dead'] and z['when']>known.get(actor,(-1,))[0]:known[actor]=(z['when'],z['cell'],'sonar')
    cur.update(foeq=xy(tq),foeL=len(bs[queens[1]]),visible=vis,known=known.get(actor))
    if qd is not None:
     if vis:lastseen.setdefault(rnd,[]).append(actor)
     ds=dist(tq)[hd];limit=(L+3)//4+L-2
     if ds<=max(limit,12 if L<=8 else limit):
      occ={c for b in bs.values() for c in b};pathhit=shot(hd,tq,L,occ)
      if pathhit is None and L<=8:
       pathhit=pearl_shot(hd,tq,L,occ);cur['pearl_extension']=pathhit is not None
      if pathhit is not None:cur['reach']=len(pathhit);cur['ram_path']=pathhit;cur['free']=len(pathhit)<=(L+3)//4
  elif k==3:
   c=pt(p.pointer(0))
   if p.u32(0):
    pearls[c]=drop if expect else None
    if expect:expect-=1
   else:
    origin=pearls.pop(c,None)
    if cur is not None:cur['eats'].append([xy(c),origin])
  elif k==4:
   a=p.pointer(0);dirs=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
   if cur is not None:cur['action']=dict(kind=a.u16(0) if a else None,dirs=dirs)
  elif k==9:
   i=p.i32(0);hd,tl=pt(p.pointer(0)),pt(p.pointer(1));b=bs[i]
   if b[0]!=hd:
    if i==actor:
     steps+=1
     if cur is not None:cur['path'].append(xy(hd))
    b.appendleft(hd)
   while len(b)>1 and b[-1]!=tl:b.pop()
   assert b[-1]==tl
  elif k==10:
   parent,child=p.i32(0),p.i32(4)
   for z,i in enumerate((parent,child)):
    bs[i]=deque(pt(c) for c in p.pointer(z));team[i]=p.u16(8)
   if cur is not None:cur['splits'].append([child,len(bs[parent]),len(bs[child])])
  elif k==11:
   i,reason=p.i32(0),p.u16(4);b=bs[i];target=None
   if i==actor and steps<len(dirs):
    d=dirs[steps];kind,c=g.moves[b[0]][d];target=next(([z,'head' if bb[0]==c else 'body'] for z,bb in bs.items() if c in bb),None)
   rec=dict(r=rnd,id=i,side=int(team[i]!=own),reason=reason,L=len(b),head=xy(b[0]),actor=actor,target=target)
   deaths.append(rec)
   if i==queens[0]:qd=rnd
   if cur is not None:cur['hits'].append(rec)
   drop=[rnd,i,team[i],reason];expect=(len(b)+1)//2;bs.pop(i)
  elif k==12:
   sender=p.i32(0)
   if team.get(sender)!=own:continue
   wire=p.u64(16)
   if wire not in opened:opened[wire]=unseal(key,wire,streams)
   plain=opened[wire]
   assert plain is not None
   if plain>>63==0:
    val=dict(kind='leader',state=(plain>>26)&3,leader=plain&0x7fff,qgame=bool(plain&0x8000),L=(plain>>16)&0x3ff,when=(plain>>28)&511)
   elif (plain>>42)&0x7ff==0x2b5:
    val=dict(kind='queen',state=(plain>>24)&3,dead=(plain>>23)&1,cell=plain&0x3fff,when=(plain>>14)&511)
   else:val=dict(kind='other')
   val.update(r=rnd,sender=sender,receiver=p.i32(12) if p.u16(6) else None,hit=p.u16(24))
   receiver=val['receiver']
   if receiver is not None and team.get(receiver)==own:inbox[receiver].append(val)
   if cur is not None:
    if 'state'in val:cur['sent_states'].append(val['state'])
    cur['pings'].append(val)
    if val.get('qgame'):cur['queen_game_tag']=True
   pings.append(val)
  elif k in (5,6):logs[k]+=1
 finish();snapshot()
 return dict(gid=j['id'],map=j['mapName'],size=[w,h],queens=queens,death=qd,finalQ=[len(bs.get(i,())) for i in queens],snaps=snaps,reach=turns,claims=claims,pings=pings,sightings=lastseen,qturns=qturns,deaths=deaths,logs=dict(logs),observations=observations)

def main():
 mode=sys.argv[1] if len(sys.argv)>1 else 'detail'
 for label in ('one8-k1','one8-w1','one8-c1'):
  for mp in sorted((SM/(label+'-old')).glob('game-*.json')):
   j=json.loads(mp.read_text());gid=j['id'];rp=mp.with_name(f'M{gid}.replay')
   if mode=='ledger':
    op=OUT/f'ledger-{gid}.json'
    if not op.exists():op.write_text(json.dumps(ledger(label,rp,j),separators=(',',':')))
   else:
    lp=OUT/f'ledger-{gid}.json';l=json.loads(lp.read_text()) if lp.exists() else None
    if gid not in TARGET and not(l and l['ends'][0][3] and l['ends'][1][3]):continue
    op=OUT/f'detail-{gid}.json'
    if True:op.write_text(json.dumps(detail(rp,j),separators=(',',':')))
   print(mode,gid,flush=True)
if __name__=='__main__':main()
