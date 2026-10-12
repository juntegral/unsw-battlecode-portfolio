"""Attach outgoing leader claims, episode entries and recent actions to counted turns."""
import sys,json
from pathlib import Path
from collections import deque,Counter,defaultdict
sys.dont_write_bytecode=True
sys.path.insert(0,'tools'); sys.path.insert(0,'../battlecode/work')
from ladder_replay import replay,edge_id,canonical_edges
from card_42_check import make_key,unseal,parse
P=Path(__file__).resolve().parent
for label in ('one5-w1','one5-c1','one3-w1'):
    out=[]
    for g in map(json.loads,(P/(label+'-scan-v2.jsonl')).read_text().splitlines()):
        base=Path('data/online/smoke')/(label+'-old'); meta=json.loads((base/('game-%d.json'%g['gid'])).read_text())
        root=replay.load(base/('M%d.replay'%g['gid'])).root(); W,H=g['W'],g['H']
        own=0 if meta['teamAId']==1119 else 1; bodies={}; teams={}; raw=[]
        for line in root.text(0).splitlines():
            q=line.split()
            if q[0]=='DRAGON':
                i=len(bodies); teams[i]=int(q[1]); bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])))
            elif q[0]=='EDGE': raw.append(tuple(map(int,q[1:4])))
        edges=canonical_edges(W,H,raw); key=make_key(W,H,2 if own==0 else 1); streams={}; opened={}
        pearls=set(); rnd=-1; cur=None; prior={}; history=defaultdict(lambda:deque(maxlen=5)); counts=Counter(); episodes=[]
        d1={(r['i'],r['r']):r for r in g['d1']}; blind={(r['i'],r['r']):r for r in g['blind']}
        def view(h,c):
            dx=abs(h[0]-c[0]);dy=abs(h[1]-c[1]);return min(dx,W-dx)<=3 and min(dy,H-dy)<=3
        def gap(a,b):
            dx=abs(a[0]-b[0]);dy=abs(a[1]-b[1]);return min(dx,W-dx)+min(dy,H-dy)
        def close():
            global cur
            if cur is None:return
            i=cur['i']; target=blind.get((i,rnd)); miss=d1.get((i,rnd)); prev=prior.get(i)
            if target:
                if prev and prev['solo']:
                    counts['continuing']+=1
                else:
                    why='new/split' if not prev or prev['split'] else 'previous meal' if prev['ate'] else 'previous pearl view' if prev['P'] else 'previous mate view'
                    counts['entry:'+why]+=1
                    episodes.append(dict(r=rnd,i=i,why=why,history=list(history[i]),now=target))
                target['previous']=prev
            if miss:
                miss['chosen_portal']=cur['portal']; miss['leader']=cur['leader']; miss['zone_model']=False
                if cur['leader'] and W*H>1200 and rnd>150 and cur['units']>=56:
                    ld=cur['leader']; lid=ld['id']; pos=cur['live'].get(lid,ld['pos'])
                    if lid!=i:
                        miss['zone_model']=all(gap((c%W,c//W),pos)<=gap(cur['h'],(c%W,c//W)) and gap((c%W,c//W),pos)<=9 for c in miss['adj'])
                if miss['reason']=='unresolved_score':
                    miss['residual_context']='leader_zone' if miss['zone_model'] else 'chosen_portal' if cur['portal'] else 'tight' if all(f['room']<3*miss['L']+8 for f in miss['flags']) else 'ally_head_penalty' if all(f['ally_step'] for f in miss['flags']) else 'unresolved'
                counts['D1 zone_model']+=int(miss['zone_model'])
            brief={k:cur[k] for k in ('i','r','h','end','L','P','mates','ate','split','portal','solo')}
            prior[i]=brief; history[i].append(brief);cur=None
        for ev in root.pointer(3):
            k=ev.u16(0);p=ev.pointer(0)
            if k==0:
                close();rnd=p.i32(0)
                if rnd>300:break
            elif k==1:
                close();i=p.i32(0)
                if teams[i]!=own:continue
                h=bodies[i][0]; ps=[c for c in pearls if view(h,c)]; mates=[z for z,bb in bodies.items() if z!=i and teams[z]==own and view(h,bb[0])]
                cur=dict(i=i,r=rnd,h=h,end=h,L=len(bodies[i]),P=len(ps),mates=len(mates),ate=0,split=False,portal=False,solo=not ps and not mates,leader=None,
                         units=sum(teams[z]==own for z in bodies),live={z:bb[0] for z,bb in bodies.items() if teams[z]==own and view(h,bb[0])})
            elif k==3:
                c=replay.point(p.pointer(0))
                if p.u32(0):pearls.add(c)
                else:
                    pearls.remove(c)
                    if cur:cur['ate']+=1
            elif k==4 and cur:
                a=p.pointer(0)
                if a and a.u16(0)==0 and a.pointer(0) is not None:
                    dirs=list(a.pointer(0))
                    if dirs:cur['portal']=edges.get(edge_id(W,H,*cur['h'],dirs[0]),(0,-1))[0]==2
            elif k==9:
                i=p.i32(0);hd=replay.point(p.pointer(0));tl=replay.point(p.pointer(1));b=bodies[i]
                if b[0]!=hd:b.appendleft(hd)
                while len(b)>1 and b[-1]!=tl:b.pop()
                if cur and i==cur['i']:cur['end']=hd
            elif k==10:
                pa,ch=p.i32(0),p.i32(4)
                for z,i in enumerate((pa,ch)):bodies[i]=deque(replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
                if cur:cur['split']=True
            elif k==11:del bodies[p.i32(0)]
            elif k==12 and cur and (cur['i'],rnd) in d1:
                if p.i32(0)!=cur['i']:continue
                wire=p.u64(16)
                if wire not in opened:opened[wire]=unseal(key,wire,streams)
                plain=opened[wire]
                if plain is not None and parse(plain)[0]=='leader':
                    cur['leader']=dict(id=(plain&0xFFFF)&0x7FFF,length=(plain>>16)&0x3FF,pos=((plain>>37)&0x7F,(plain>>44)&0x7F),when=(plain>>28)&0x1FF)
        close()
        out.append(dict(gid=g['gid'],map=g['map'],C=counts,episodes=episodes,d1=list(d1.values())))
        print(label,g['gid'],flush=True)
    (P/(label+'-enrich.json')).write_text(json.dumps(out,separators=(',',':'))+'\n')
