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

def analyze(gid):
    path = ROOT/f'data/online/smoke/one11-c1-old/M{gid}.replay'
    root = lr.replay.load(path).root()
    w,h = map(int, root.text(0).splitlines()[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in root.text(0).splitlines():
        q = line.split()
        if q and q[0]=='DRAGON':
            i=len(bodies); teams[i]=int(q[1]); bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
        elif q and q[0]=='EDGE': raw.append(tuple(map(int,q[1:4])))
    queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
    geo=Geo(w,h,raw); pearls=set(); turns=[]; rnd=-1; cur=None; history=[]; near=[]; cache={}
    qdead=False; lastq=None; closest_event=None
    tile=lambda p: lr.replay.point(p)[1]*w+lr.replay.point(p)[0]
    xy=lambda c: [c%w,c//w]
    def dist(src):
        if src not in cache:
            ds={src:0}; queue=deque([src])
            while queue:
                c=queue.popleft()
                for t in geo.adj[c]:
                    if t not in ds: ds[t]=ds[c]+1; queue.append(t)
            cache[src]=ds
        return cache[src]
    def board(src):
        chars={c:('*' if c in pearls else '.') for c in geo.window(src)}
        labels=[]
        for i,b in bodies.items():
            for k,c in enumerate(b):
                if c in chars:
                    chars[c]=('Q' if i==queens[0] else 'K' if i==queens[1] else 'A' if teams[i]==0 else 'B') if k==0 else ('a' if teams[i]==0 else 'b')
            if b[0] in chars: labels.append([i,teams[i],len(b),xy(b[0])])
        x,y=xy(src)
        # Each cell carries N/E/S/W edge markers in a separate 7x7 table.
        rows=[''.join(chars[((y+dy)%h)*w+(x+dx)%w] for dx in range(-3,4)) for dy in range(-3,4)]
        edges=[]
        for dy in range(-3,4):
            edges.append(' '.join(''.join('NESW'[d].lower() if k==2 else 'NESW'[d] for d,(k,t) in enumerate(geo.moves[((y+dy)%h)*w+(x+dx)%w]) if k) or '-' for dx in range(-3,4)))
        return dict(center=xy(src),rows=rows,edges=edges,heads=labels)
    def close():
        if cur is not None:
            cur['end_body']=list(bodies.get(cur['id'],[])); turns.append(cur)
    def snap():
        return [[sum(teams[i]==s for i in bodies),sum(len(b) for i,b in bodies.items() if teams[i]==s),max((len(b) for i,b in bodies.items() if teams[i]==s),default=0),len(bodies.get(queens[s],[]))] for s in (0,1)]
    for ei,ev in enumerate(root.pointer(3)):
        k=ev.u16(0); p=ev.pointer(0)
        if k==0:
            close(); cur=None
            if rnd>=0: history.append([rnd,snap()])
            rnd=p.i32(0)
        elif k==1:
            close(); i=p.i32(0); b=bodies[i]
            cur=dict(round=rnd,event=ei,id=i,side=teams[i],body=list(b),steps=[],eats=0,deaths=[],split=None)
            if i in queens or (gid==1496848 and i==8 and 109<=rnd<=114) or (gid==1496849 and rnd in range(73,77)) or (gid==1496850 and rnd in range(349,353)):
                cur['board']=board(b[0]); cur['all_bodies']={j:list(bb) for j,bb in bodies.items()}
            if qdead and queens[1] in bodies and teams[i]==0:
                qh=bodies[queens[1]][0]; ds=dist(b[0]); distance=ds.get(qh,99999)
                if distance<=5: near.append(dict(round=rnd,id=i,length=len(b),distance=distance,head=xy(b[0]),queen=xy(qh)))
                if lastq is None or distance<lastq['distance']:lastq=dict(round=rnd,id=i,distance=distance,head=xy(b[0]),queen=xy(qh))
        elif k==3:
            c=tile(p.pointer(0))
            if p.u32(0): pearls.add(c)
            else: pearls.remove(c); cur['eats']+=1
        elif k==4:
            a=p.pointer(0)
            cur['action_kind']=a.u16(0) if a else None
            cur['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
        elif k==9:
            i=p.i32(0); hd=tile(p.pointer(0)); tail=tile(p.pointer(1)); b=bodies[i]
            if b[0]!=hd: b.appendleft(hd); cur['steps'].append(hd)
            while len(b)>1 and b[-1]!=tail:b.pop()
            assert b[-1]==tail
        elif k==10:
            cur['split']=[p.i32(0),p.i32(4)]
            for z,i in enumerate(cur['split']): bodies[i]=deque(tile(pt) for pt in p.pointer(z)); teams[i]=p.u16(8)
        elif k==11:
            i=p.i32(0); cur['deaths'].append([i,p.u16(4),list(bodies[i])]); bodies.pop(i)
            if i==queens[0]: qdead=True
        if qdead and queens[1] in bodies and k in (1,9,10,11):
            qh=bodies[queens[1]][0]
            for i,b in bodies.items():
                if teams[i]!=0: continue
                dd=dist(b[0]).get(qh,99999)
                if closest_event is None or dd<closest_event['distance']:
                    closest_event=dict(round=rnd,event=ei,id=i,distance=dd,head=xy(b[0]),queen=xy(qh))
    close(); history.append([rnd,snap()])
    for s in (0,1):
        st=root.pointer(4).pointer(s); assert snap()[s]==[st.i32(0),st.i32(8),st.i32(4),st.i32(12)]
    result=dict(gid=gid,w=w,h=h,queens=queens,turns=turns,history=history,near=near,nearest=lastq,closest_event=closest_event,teams=teams)
    (OUT/f'{gid}-detail.json').write_text(json.dumps(result,separators=(',',':')))
    qt=[t for t in turns if t['id']==queens[0]]
    print(gid,'queen last',[(t['round'],len(t['body']),xy(t['body'][0]),t.get('dirs'),[xy(c) for c in t['steps']],t['split'],t['deaths']) for t in qt[-4:]])
    print('death turns',[(t['round'],t['id'],len(t['body']),xy(t['body'][0]),t.get('dirs'),[xy(c) for c in t['steps']],t['eats'],t['deaths']) for t in turns if any(d[0]==queens[0] for d in t['deaths'])])
    print('near',len(near),near[:3],lastq)
    print('closest at any event',closest_event)
    print('bots',root.text(1)[:250],root.text(2)[:250])

if __name__=='__main__':
    for gid in (1496848,1496849,1496850): analyze(gid)
