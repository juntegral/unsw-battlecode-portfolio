import json,sys
from collections import deque,Counter,defaultdict
import analyze as a
OUT=a.OUT

def focus(gid):
 job=next(x for x in json.loads((OUT/'inventory.json').read_text())['rows'] if x['gid']==gid);root=a.load_replay(a.Path(job['path'])).root();lines=[l.split() for l in root.text(0).splitlines()];w,h=map(int,lines[0][1:3]);own=int(job['meta']['teamAId']!=1119);g=a.Geo(w,h,[tuple(map(int,l[1:4])) for l in lines if l[0]=='EDGE']);bs={};ts={}
 for q in lines:
  if q[0]=='DRAGON':
   i=len(bs);bs[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));ts[i]=int(int(q[1])!=own)
 queen=[min(i for i in bs if ts[i]==s) for s in (0,1)];rnd=-1;actor=None;cur=None;rows=[];states=[];decoder=a.wire_decoder(w,h,2 if own==0 else 1);qgame=set();signalled=set();keycache={};signal_count=Counter();dist={}
 sys.path.insert(0,'../battlecode/work');from card_42_check import make_key,unseal
 key=make_key(w,h,2 if own==0 else 1);streams={}
 def finish():
  nonlocal cur
  if cur:
   cur['endL']=len(bs.get(actor,()));rows.append(cur);cur=None
 for ev in root.pointer(3):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:finish();rnd=p.i32(0)
  elif k==1:
   finish();actor=p.i32(0)
   if ts[actor]==0 and actor!=queen[0] and queen[0] in bs and len(bs[queen[0]])<6 and len(bs[actor]) in (2,3) and rnd>=300:
    q=bs[queen[0]][0];hd=bs[actor][0];man=g.tman(hd,q)
    if man<=15:
     if q not in dist:dist[q]=g.bfs([q])
     cur=dict(r=rnd,id=actor,L=len(bs[actor]),qL=len(bs[queen[0]]),head=hd,qhead=q,man=man,pathdist=dist[q][hd],visible=g.visible(hd,q),enemy4=sum(ts[i]==1 and g.visible(hd,b[0]) and g.tman(hd,b[0])<=4 for i,b in bs.items()),wires=[],action=None)
  elif k==4:
   if cur:
    ac=p.pointer(0);cur['action']=[ac.u16(0),list(ac.pointer(0)) if ac.u16(0)==0 and ac.pointer(0) is not None else []]
  elif k==9:
   i=p.i32(0);h1,t1=a.replay.point(p.pointer(0)),a.replay.point(p.pointer(1));hd,tail=h1[1]*w+h1[0],t1[1]*w+t1[0]
   if hd!=bs[i][0]:bs[i].appendleft(hd)
   while len(bs[i])>1 and bs[i][-1]!=tail:bs[i].pop()
  elif k==10:
   par,ch=p.i32(0),p.i32(4);ts[ch]=ts[par]
   for z,i in enumerate((par,ch)):bs[i]=deque(a.replay.point(c)[1]*w+a.replay.point(c)[0] for c in p.pointer(z))
  elif k==11:bs.pop(p.i32(0))
  elif k==12 and ts.get(p.i32(0))==0:
   wire=p.u64(16);plain=decoder(wire)
   if plain is None:continue
   state=(plain>>26)&3 if plain>>63==0 else (plain>>24)&3 if (plain>>42)&2047==0x2b5 else 0
   if state&1:
    mode='own_dead_foe_alive' if queen[0] not in bs and queen[1] in bs else 'other';signal_count[mode]+=1
    if len([r for r in states if r['mode']==mode])<3:
     independent=unseal(key,wire,streams);assert independent==plain
     states.append(dict(r=rnd,sender=p.i32(0),mode=mode,state=state,receiver=p.i32(12) if p.u16(6) else None,decoder_agrees=True))
   if plain>>63==0:
    if plain&32768:qgame.add(p.i32(0))
    if cur and p.i32(0)==actor:cur['wires'].append(dict(id=plain&32767,L=(plain>>16)&1023,r=(plain>>28)&511,qgame=actor in qgame))
 finish();result=dict(gid=gid,version=job['version'],rows=rows,signals=states,signal_count=dict(signal_count));(OUT/f'focus-{gid}.json').write_text(json.dumps(result,ensure_ascii=False));print(gid,len(rows),signal_count,flush=True)
if __name__=='__main__':
 for arg in sys.argv[1:]:focus(int(arg))
