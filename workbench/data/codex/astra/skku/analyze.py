"""Read-only serial replay audit. Run from repository root with python3 -B."""
import sys
sys.dont_write_bytecode = True
sys.path[:0] = ['tools', 'data/analysis/ladder/dossier/work', 'data/codex/astra/stuck-opus']
import json
from pathlib import Path
from collections import deque, defaultdict, Counter
import ladder_replay as lr
import o1_scan
import detect

OUT = Path('data/codex/astra/skku')
STEP = ((0,-1),(1,0),(0,1),(-1,0))
WATCH={1514288:(718,737,204),1514290:(783,128),1519938:(3,16,21),1519940:(3,12),1519941:(21,105,2)}

def details(path, j, watch=()):
    root = lr.replay.load(path).root()
    lines = root.text(0).splitlines()
    W,H = map(int,lines[0].split()[1:3])
    bodies,teams,raw = {},{},[]
    for line in lines:
        q=line.split()
        if q and q[0]=='DRAGON':
            i=len(bodies); bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])))
            teams[i]=int(q[1])
        elif q and q[0]=='EDGE': raw.append(tuple(map(int,q[1:4])))
    own = 0 if j['teamAId']==1119 else 1
    side=lambda i: 0 if teams[i]==own else 1
    queens=[min(i for i in bodies if side(i)==s) for s in (0,1)]
    edges=lr.canonical_edges(W,H,raw); portals=defaultdict(list)
    for e,(k,p) in edges.items():
        if k==2: portals[p].append(e)
    def gap(a,b):
        dx=abs(a[0]-b[0]);dy=abs(a[1]-b[1]);return min(dx,W-dx)+min(dy,H-dy)
    def view(a,b):
        dx=abs(a[0]-b[0]);dy=abs(a[1]-b[1]);return min(dx,W-dx)<=3 and min(dy,H-dy)<=3
    def dest(h,d):
        e=lr.edge_id(W,H,*h,d); k,p=edges.get(e,(0,-1))
        if k==2:
            partner=next(z for z in portals[p] if z!=e);row,x=divmod(partner,W+1)
            return ((x-(d==3))%W,(row//2-(d==0))%H),True
        dx,dy=STEP[d];return ((h[0]+dx)%W,(h[1]+dy)%H),False
    rnd=-1;turn=None;pearls=set();qturn=[[],[]];deaths=[];splits=[];turns=[];watched=defaultdict(list);logs=[]
    starts={i:b[0] for i,b in bodies.items()}
    def close():
        if turn is not None:
            turn['Lend']=len(bodies.get(turn['id'],()))
            if not turn['split']:
                turn['paid']=turn['L']+turn['eat']-turn.get('death_length',turn['Lend'])
            turns.append(turn.copy())
    for ev in root.pointer(3):
        k=ev.u16(0);p=ev.pointer(0)
        if k==0: close();turn=None;rnd=p.i32(0)
        elif k==1:
            close();i=p.i32(0);b=bodies[i]
            turn=dict(r=rnd,id=i,s=side(i),L=len(b),h=b[0],path=[b[0]],portal=[],dirs=[],eat=0,paid=0,split=False)
            if i in queens or i in watch:
                s=side(i);foes=[dict(id=z,L=len(bb),h=bb[0],seen=sum(view(c,b[0]) for c in bb)) for z,bb in bodies.items() if side(z)!=s and view(bb[0],b[0])]
                local={str(z):list(bb) for z,bb in bodies.items() if any(view(c,b[0]) for c in bb)}
                record=dict(r=rnd,h=b[0],L=len(b),foes=foes,bodies=local,pearls=[c for c in pearls if view(c,b[0])],units=sum(side(z)==s for z in bodies),home=gap(b[0],starts.get(i,b[0])))
                watched[i].append(record)
                if i in queens:qturn[s].append(record)
        elif k==4:
            a=p.pointer(0);turn['action']=a.u16(0) if a else None
            if a and a.u16(0)==0 and a.pointer(0) is not None:turn['dirs']=list(a.pointer(0))
        elif k==3:
            c=lr.replay.point(p.pointer(0))
            if p.u32(0):pearls.add(c)
            else:pearls.remove(c);turn['eat']+=1
        elif k==9:
            i=p.i32(0);h=lr.replay.point(p.pointer(0));tail=lr.replay.point(p.pointer(1));b=bodies[i];before=len(b)
            if h!=b[0]:
                if i==turn['id']:
                    step=len(turn['path'])-1
                    turn['portal'].append(dest(b[0],turn['dirs'][step])[1])
                    turn['path'].append(h)
                b.appendleft(h)
            while len(b)>1 and b[-1]!=tail:b.pop()
        elif k==10:
            par,ch=p.i32(0),p.i32(4);L=len(bodies[par]);turn['split']=True
            for z,i in enumerate((par,ch)):
                bodies[i]=deque(lr.replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
            splits.append(dict(r=rnd,s=side(par),id=par,child=ch,L=L,keep=len(bodies[par]),childL=len(bodies[ch]),queen=par in queens))
        elif k==11:
            i=p.i32(0);reason=p.u16(4);b=bodies[i]
            d=dict(r=rnd,id=i,s=side(i),L=len(b),reason=reason,head=b[0],actor=turn['id'],body=list(b))
            if i==turn['id']:turn['death_length']=len(b)
            if i in queens or i in watch:
                s=side(i);d['enemy_queen_alive']=queens[1-s] in bodies;d['last']=watched[i][-3:]
                a=turn.copy();a['path']=a['path'][:];a['portal']=a['portal'][:]
                step=len(a['path'])-1
                if step<len(a['dirs']):
                    h,port=dest(bodies[a['id']][0],a['dirs'][step]);a['path'].append(h);a['portal'].append(port)
                a['steps']=len(a['path'])-1;a['free_budget']=(a['L']+3)//4
                a['free']=min(a['steps'],a['free_budget']);a['paid']=max(0,a['steps']-a['free_budget'])
                a['spent_before_collision']=a['L']+a['eat']-len(bodies[a['id']])
                a['distance']=gap(a['h'],b[0]);a['seen_last']=any(f['id']==a['id'] for f in watched[i][-1]['foes'])
                d['attack']=a
            deaths.append(d);bodies.pop(i)
        elif k==6:
            logs.append(dict(r=rnd,id=p.i32(0),text=p.text(0)))
    close()
    return dict(W=W,H=H,queens=queens,qturn=qturn,deaths=deaths,splits=splits,turns=turns,watched=dict(watched),logs=logs)

def main():
    summary=[]
    for battle in ('b1514288','b1519937'):
        folder=Path('data/online/live-one1')/battle
        for mp in sorted(folder.glob('game-*.json')):
            j=json.loads(mp.read_text());gid=j['id'];path=folder/f'M{gid}.replay'
            base=lr.scan(path,j,battle,set())
            scan=o1_scan.scan(battle,path,j)
            det=details(path,j,WATCH.get(gid,()))
            loops=detect.scan(path,0 if j['teamAId']==1119 else 1)
            behind=None
            for r,v in sorted(base['snapshots'].items(),reverse=True):
                def key(s):
                    x=v[s];return (int(x['alive']>0),x['queen_length'],x['longest'],x['total'])
                if key('us')<key('them'):behind=r
                else:break
            g=dict(meta=j,base=base,scan=scan,detail=det,loops=loops,behind=behind)
            # Interval keys are coordinates in the imported reader; omit unused map.
            base.pop('intervals')
            (OUT/f'{gid}.json').write_text(json.dumps(g,separators=(',',':')))
            qd=[{k:v for k,v in d.items() if k not in ('body','last')} for d in det['deaths'] if d['id'] in det['queens']]
            row=dict(gid=gid,map=j['mapName'],bots=base['bots'],ours=base['ours'],result=scan['result'],how=scan['how'],last=scan['last'],ends=[x[:4] for x in scan['ends']],behind=behind,qd=qd)
            summary.append(row)
            print(json.dumps(row),flush=True)
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2))

if __name__=='__main__':main()
