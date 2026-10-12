import sys, json
sys.dont_write_bytecode = True
from pathlib import Path
from collections import deque, Counter
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
import o1_scan
sys.path.insert(0, 'tools')
import ladder_replay as lr

OUT = Path('data/codex/astra/kraken')

def detail(path, meta):
    root = lr.replay.load(path).root()
    lines = root.text(0).splitlines()
    w,h = map(int, lines[0].split()[1:3])
    own = int(meta['teamAId'] != 1119)
    bodies, teams = {}, {}
    for line in lines:
        q=line.split()
        if q and q[0]=='DRAGON':
            i=len(bodies); teams[i]=int(int(q[1])!=own)
            bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])))
    queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
    def gap(a,b):
        dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1])
        return min(dx,w-dx)+min(dy,h-dy)
    def snap():
        return [[len(bodies.get(queens[s],())),max((len(b) for i,b in bodies.items() if teams[i]==s),default=0),sum(len(b) for i,b in bodies.items() if teams[i]==s),sum(teams[i]==s for i in bodies)] for s in (0,1)]
    turns=[]; qt=[[],[]]; deaths=[]; snaps={}; rnd=-1; turn=None
    first=[None,None]; opening=[set(),set()]; splits=[]
    def close():
        nonlocal turn
        if turn is None:return
        i=turn['id']; turn['end']=list(bodies[i]) if i in bodies else []
        turns.append({k:v for k,v in turn.items() if k!='context'})
        if i in queens:qt[queens.index(i)].append(dict(turn))
        turn=None
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0);p=ev.pointer(0)
        if k==0:
            close()
            if rnd>=0:snaps[rnd]=snap()
            rnd=p.i32(0)
        elif k==1:
            close();i=p.i32(0);s=teams[i]
            turn=dict(id=i,s=s,r=rnd,L=len(bodies[i]),body=list(bodies[i]),steps=[],eat=0,action=None,dirs=[])
            if i in queens:turn['context']={j:list(b) for j,b in bodies.items()}
            if rnd<=30:opening[s].add(bodies[i][0])
        elif k==4:
            a=p.pointer(0)
            turn['action']=a.u16(0) if a else None
            turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
        elif k==3 and p.u32(0)==0:
            turn['eat']+=1
            s=turn['s']
            if first[s] is None:first[s]=rnd
        elif k==9:
            i=p.i32(0);hd,tl=lr.replay.point(p.pointer(0)),lr.replay.point(p.pointer(1));b=bodies[i]
            if b[0]!=hd:
                b.appendleft(hd);turn['steps'].append(hd)
                if rnd<=30:opening[teams[i]].add(hd)
            while len(b)>1 and b[-1]!=tl:b.pop()
            assert b[-1]==tl
        elif k==10:
            parent,child=p.i32(0),p.i32(4)
            splits.append(dict(r=rnd,s=teams[parent],id=parent,child=child,L=len(bodies[parent])))
            for z,i in enumerate((parent,child)):
                bodies[i]=deque(lr.replay.point(pt) for pt in p.pointer(z));teams[i]=int(p.u16(8)!=own)
        elif k==11:
            i=p.i32(0)
            deaths.append(dict(r=rnd,id=i,s=teams[i],L=len(bodies[i]),reason=p.u16(4),actor=turn['id'],actorL=turn['L'],step=len(turn['steps'])+1,body=list(bodies[i]),context={j:list(b) for j,b in bodies.items()} if i in queens else {}))
            bodies.pop(i)
    close();snaps[rnd]=snap()
    for s in (0,1):
        raw=root.pointer(4).pointer(own if s==0 else 1-own)
        assert (snaps[rnd][s][3],snaps[rnd][s][1],snaps[rnd][s][2],snaps[rnd][s][0]) == tuple(raw.i32(x) for x in (0,4,8,12))
    return dict(gid=meta['id'],map=meta['mapName'],w=w,h=h,queens=queens,teams=teams,bots=[root.text(1),root.text(2)],own=own,first=first,spread=[len(x) for x in opening],splits=splits,turns=turns,qt=qt,deaths=deaths,snaps=snaps,final={i:list(b) for i,b in bodies.items()})

if __name__=='__main__':
    folders=[Path('data/online/live-one1')/x for x in ('b1482056','b1483343')]
    folders += [Path('data/online/smoke')/x for x in ('one7-w1-old','one7-c1-old','one8-w1-old','one8-c1-old','one8-k1-old')]
    targets={json.loads(p.read_text())['mapName'] for f in folders[:2] for p in f.glob('game-*.json')}
    for folder in folders:
        for mp in sorted(folder.glob('game-*.json')):
            meta=json.loads(mp.read_text());rp=folder/f"M{meta['id']}.replay"
            if not rp.exists() or (meta['mapName'] not in targets and 'k1' not in folder.name):continue
            dest=OUT/f"M{meta['id']}.json"
            if dest.exists():continue
            g=o1_scan.scan(folder.name,rp,meta)
            d=detail(rp,meta)
            dest.write_text(json.dumps(dict(meta=meta,ledger=g,detail=d),separators=(',',':')))
            print(folder.name,meta['id'],meta['mapName'],g['result'],g['how'],g['ends'],flush=True)
