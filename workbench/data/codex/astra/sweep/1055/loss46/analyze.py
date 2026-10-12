import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from collections import deque, Counter
ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'data/analysis/ladder/dossier/local')]
import ladder_replay as lr
from count_local import Geo
import scoreboard

def run(gid, label):
    folder = ROOT/'data/online/smoke'/label
    path = folder/f'M{gid}.replay'
    meta = json.loads((folder/f'game-{gid}.json').read_text())
    loaded = scoreboard.load_replay(path)
    root = loaded.root()
    lr.replay.load = lambda _: loaded
    raw = lr.scan(path, meta, label, set())
    w,h = map(int, root.text(0).splitlines()[0].split()[1:3])
    bodies,teams,edges = {},{},[]
    for line in root.text(0).splitlines():
        q=line.split()
        if q[0]=='DRAGON':
            i=len(bodies); teams[i]=int(q[1]); bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
        elif q[0]=='EDGE': edges.append(tuple(map(int,q[1:4])))
    geo=Geo(w,h,edges)
    queens=[min(i for i in bodies if teams[i]==s) for s in range(2)]
    turns=[]; cur=None; pearls=set(); rnd=-1; splits=[]; near=[]
    qdead=False; mindist=99999; closest=None
    tile=lambda p: lr.replay.point(p)[1]*w+lr.replay.point(p)[0]
    def board(head):
        window=geo.window(head)
        chars={c: ('Q' if i==queens[0] else 'K' if i==queens[1] else 'A' if teams[i]==0 else 'B') if j==0 else ('a' if teams[i]==0 else 'b') for i,b in bodies.items() for j,c in enumerate(b)}
        rows=[]
        for dy in range(-3,4):
            rows.append(''.join(chars.get(((head//w+dy)%h)*w+(head%w+dx)%w, '*' if ((head//w+dy)%h)*w+(head%w+dx)%w in pearls else '.') for dx in range(-3,4)))
        return dict(rows=rows,center=[head%w,head//w],dragons={i:dict(team=teams[i],length=len(b),body=[[c%w,c//w] for c in b]) for i,b in bodies.items() if any(c in window for c in b)},edges=[dict(x=c%w,y=c//w,d='NESW'[d],kind=k,to=[dst%w,dst//w]) for c in sorted(window) for d,(k,dst) in enumerate(geo.moves[c]) if k])
    distances={}
    def proximity(event):
        nonlocal mindist,closest
        if not qdead or queens[1] not in bodies:return
        target=bodies[queens[1]][0]
        if target not in distances:
            dist={target:0};queue=deque([target])
            while queue:
                c=queue.popleft()
                for dst in geo.adj[c]:
                    if dst not in dist:dist[dst]=dist[c]+1;queue.append(dst)
            distances[target]=dist
        dist=distances[target]
        for i,b in bodies.items():
            if teams[i]!=0:continue
            d=dist.get(b[0],99999)
            if d<mindist:
                mindist=d;closest=dict(round=rnd,event=event,id=i,distance=d,head=[b[0]%w,b[0]//w],queen=[target%w,target//w])
            if d<=5 and (not near or near[-1]['round']!=rnd):
                near.append(dict(round=rnd,event=event,id=i,distance=d,head=[b[0]%w,b[0]//w],queen=[target%w,target//w]))
    def close():
        if cur is not None:
            cur['end_length']=len(bodies.get(cur['id'],()))
            cur['end_head']=list(bodies[cur['id']])[0] if cur['id'] in bodies else None
    for idx,ev in enumerate(root.pointer(3)):
        kind=ev.u16(0);p=ev.pointer(0)
        if kind==0:close();cur=None;rnd=p.i32(0)
        elif kind==1:
            close();i=p.i32(0);hd=bodies[i][0]
            cur=dict(round=rnd,event=idx,id=i,team=teams[i],length=len(bodies[i]),head=hd,body=list(bodies[i]),steps=[],eats=0,split=None,action=None)
            if i in queens:cur['board']=board(hd)
            turns.append(cur);proximity(idx)
        elif kind==3:
            c=tile(p.pointer(0))
            if p.u32(0):pearls.add(c)
            else:pearls.remove(c);cur['eats']+=1
        elif kind==4:
            a=p.pointer(0)
            cur['action']=dict(kind=a.u16(0),dirs=list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else [])
        elif kind==9:
            i=p.i32(0);hd=tile(p.pointer(0));tail=tile(p.pointer(1));b=bodies[i]
            if b[0]!=hd:cur['steps'].append([b[0],hd]);b.appendleft(hd)
            while len(b)>1 and b[-1]!=tail:b.pop()
            assert b[-1]==tail
            proximity(idx)
        elif kind==10:
            parent,child=p.i32(0),p.i32(4)
            for z,i in enumerate((parent,child)):
                bodies[i]=deque(tile(pt) for pt in p.pointer(z));teams[i]=p.u16(8)
            cur['split']=child;splits.append(dict(round=rnd,parent=parent,child=child,lengths=[len(bodies[parent]),len(bodies[child])]))
            proximity(idx)
        elif kind==11:
            i=p.i32(0)
            if i==queens[0]:qdead=True
            bodies.pop(i);proximity(idx)
    close()
    summary={k:raw[k] for k in ('bots','final','last_round','end_reason','winner','q_eats','q_splits','eats','anomalies')}
    summary.update(gid=gid,map=meta['mapName'],size=[w,h],queens=queens,deaths=[d for d in raw['deaths'] if d['id'] in queens],closest=closest,near_rounds=near,checkpoints={r:raw['snapshots'][r] for r in (0,20,50,100,200,300,400,499) if r in raw['snapshots']},final_dragons={i:dict(team=teams[i],length=len(b),head=[b[0]%w,b[0]//w]) for i,b in bodies.items()})
    last_not_behind=-1
    for r,s in raw['snapshots'].items():
        a,b=s['us'],s['them']
        if tuple(a[k] for k in ('queen_length','longest','total'))>=tuple(b[k] for k in ('queen_length','longest','total')):last_not_behind=r
    summary['permanent_score_deficit_from']=last_not_behind+1
    raw['intervals'] = [[list(k),v] for k,v in raw['intervals'].items()]
    (OUT/f'{gid}.json').write_text(json.dumps(dict(summary=summary,turns=turns,splits=splits,raw=raw),ensure_ascii=False))
    print(json.dumps(summary,ensure_ascii=False))

if __name__=='__main__':
    for gid,label in [(1509109,'one13-k1-old'),(1509111,'one13-k1-old'),(1513834,'one13-k2-old')]:run(gid,label)
