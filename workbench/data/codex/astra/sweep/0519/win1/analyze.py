import sys
sys.dont_write_bytecode = True
import json,gzip
from pathlib import Path
from collections import deque, defaultdict, Counter
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
import ladder_replay as lr
import o1_scan

OUT = Path('data/codex/astra/sweep/0519/win1')
FILES = [Path('data/online/live-one1/b1491740/M1491740.replay')] + [
    Path(f'data/online/smoke/one10-c1-old/M{i}.replay') for i in (1492100,1492101,1492105)]

def detail(path):
    root = lr.replay.load(path).root()
    w,h = map(int, root.text(0).splitlines()[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in root.text(0).splitlines():
        q=line.split()
        if q[0]=='DRAGON':
            i=len(bodies); bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2]))); teams[i]=int(q[1])
        elif q[0]=='EDGE': raw.append(tuple(map(int,q[1:4])))
    queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
    edges=lr.canonical_edges(w,h,raw); portals=defaultdict(list)
    for e,(kind,pid) in edges.items():
        if kind==2: portals[pid].append(e)
    def delta(a,b):
        dx=abs(a[0]-b[0]); dy=abs(a[1]-b[1]);return min(dx,w-dx),min(dy,h-dy)
    def gap(a,b): return sum(delta(a,b))
    def step(pos,d):
        e=lr.edge_id(w,h,*pos,d);kind,pid=edges.get(e,(0,-1))
        if kind==1:return None
        if kind==2:
            other=next(x for x in portals[pid] if x!=e);row,x=divmod(other,w+1);return ((x-(d==3))%w,(row//2-(d==0))%h)
        dx,dy=o1_scan.STEP[d];return ((pos[0]+dx)%w,(pos[1]+dy)%h)
    def snap():
        rows=[]
        for s in (0,1):
            ls=[len(b) for i,b in bodies.items() if teams[i]==s]
            rows.append(dict(count=len(ls),total=sum(ls),longest=max(ls,default=0),queen=len(bodies.get(queens[s],()))))
        return rows
    turns=[];snaps={};rnd=-1;t=None;pearls=set();count_logs=Counter()
    def close():
        nonlocal t
        if t is None:return
        t['end']=list(bodies[t['id']][0]) if t['id'] in bodies else None
        t['end_len']=len(bodies.get(t['id'],()))
        turns.append(t);t=None
    for ix,ev in enumerate(root.pointer(3)):
        k=lr.replay.EVENT_NAMES[ev.u16(0)];p=ev.pointer(0)
        if k=='roundStart':
            close()
            if rnd>=0:snaps[rnd]=snap()
            rnd=p.i32(0)
        elif k=='turnStart':
            close();i=p.i32(0);b=bodies[i];head=b[0];s=teams[i]
            t=dict(r=rnd,id=i,side=s,length=len(b),start=list(head),dirs=[],eaten=[],deaths=[],split=None,
                   queen_lengths=[len(bodies.get(q,())) for q in queens],units=[sum(teams[z]==a for z in bodies) for a in (0,1)])
            occ=set(x for bb in bodies.values() for x in bb)
            t['adj_pearls']=[list(n) for d in range(4) if (n:=step(head,d)) is not None and n in pearls and n not in occ]
            t['heads']=[dict(id=z,side=teams[z],length=len(bb),pos=list(bb[0]),gap=gap(head,bb[0]),
                            visible=max(delta(head,bb[0]))<=3,parts=sum(max(delta(head,c))<=3 for c in bb),
                            cut=any(max(delta(head,c))==3 for c in bb)) for z,bb in bodies.items() if z!=i and max(delta(head,bb[0]))<=8]
            if i in queens:
                t['body']=list(b)
                t['local_bodies']={z:list(bb) for z,bb in bodies.items() if any(max(delta(head,c))<=4 for c in bb)}
                t['pearls']=list(pearls)
        elif k=='dragonAction':
            a=p.pointer(0);t['action']=a.u16(0) if a else None
            t['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) else []
        elif k=='tileChange':
            c=lr.replay.point(p.pointer(0))
            if p.u32(0):pearls.add(c)
            else:
                pearls.remove(c)
                if t:t['eaten'].append(list(c))
        elif k=='dragonUpdate':
            i=p.i32(0);hd=lr.replay.point(p.pointer(0));tail=lr.replay.point(p.pointer(1));b=bodies[i]
            if b[0]!=hd:b.appendleft(hd)
            while len(b)>1 and b[-1]!=tail:b.pop()
            assert b[-1]==tail
        elif k=='dragonSplit':
            parent,child=p.i32(0),p.i32(4)
            if t:t['split']=[parent,child,len(bodies[parent])]
            for z,i in enumerate((parent,child)):
                bodies[i]=deque(lr.replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
        elif k=='dragonDeath':
            i=p.i32(0)
            if t:t['deaths'].append(dict(id=i,side=teams[i],reason=p.u16(4),length=len(bodies[i]),head=list(bodies[i][0])))
            bodies.pop(i)
        elif k in ('dragonLog','engineLog'):count_logs[k]+=1
    close();snaps[rnd]=snap()
    score=lambda st:(int(st['count']>0),st['queen'],st['longest'],st['total'])
    behind=[r for r,st in snaps.items() if score(st[0])<=score(st[1])]
    permanent=max(behind)+1 if behind else min(snaps)
    assert all(score(st[0])>score(st[1]) for r,st in snaps.items() if r>=permanent)
    return dict(queens=queens,w=w,h=h,rounds=snaps,permanent_ahead=permanent,turns=turns,logs=dict(count_logs))

def main():
    for path in FILES:
        gid=int(path.stem[1:]); meta=json.loads((path.parent/f'game-{gid}.json').read_text())
        base=lr.scan(path,meta,str(path.parent),set())
        base.pop('intervals');base.pop('text')
        old=o1_scan.scan('win1',path,meta)
        det=detail(path)
        assert base['bots']['A']=='21200' and base['winner']=='A'
        assert [base['final'][s]['total'] for s in ('us','them')]==[x[1] for x in old['ends']]
        assert [base['final'][s]['total'] for s in ('us','them')]==[x['total'] for x in det['rounds'][base['last_round']]]
        (OUT/f'{gid}.json.gz').write_bytes(gzip.compress(json.dumps(dict(base=base,ledger=old,detail=det),ensure_ascii=False).encode(),compresslevel=5))
        print(json.dumps(dict(gid=gid,map=meta['mapName'],end=base['last_round'],final=base['final'],ahead=det['permanent_ahead'],queens=det['queens'],queen_deaths=[x for x in base['deaths'] if x['id'] in base['queens'].values()],logs=det['logs']),ensure_ascii=False))

if __name__=='__main__':main()
