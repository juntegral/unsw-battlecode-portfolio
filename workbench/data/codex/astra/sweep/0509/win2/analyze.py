import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from collections import deque, defaultdict, Counter
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
import ladder_replay as lr
import o1_scan

OUT = Path(__file__).resolve().parent
JOBS = [(1490641,1490641), (1490642,1490641), (1490645,1490641), (1490797,1490796)]
STEP = ((0,-1),(1,0),(0,1),(-1,0))

def scan(path, meta, base):
    root = lr.replay.load(path).root()
    lines = root.text(0).splitlines()
    w,h = map(int,lines[0].split()[1:3])
    bodies,teams,raw = {},{},[]
    for line in lines:
        q=line.split()
        if q and q[0]=='DRAGON':
            i=len(bodies)
            bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])))
            teams[i]='AB'[int(q[1])]
        elif q and q[0]=='EDGE': raw.append(tuple(map(int,q[1:4])))
    edges=lr.canonical_edges(w,h,raw)
    portals=defaultdict(list)
    for e,(kind,pid) in edges.items():
        if kind==2: portals[pid].append(e)
    ours=base['ours']; queens=base['queens']; qid=queens['us']
    def gap(a,b):
        dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1])
        return min(dx,w-dx)+min(dy,h-dy)
    def view(a,b):
        dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1])
        return min(dx,w-dx)<=3 and min(dy,h-dy)<=3
    def dest(c,d):
        e=lr.edge_id(w,h,*c,d); kind,pid=edges.get(e,(0,-1))
        if kind==1: return None
        if kind==2:
            other=next(z for z in portals[pid] if z!=e)
            row,x=divmod(other,w+1)
            return ((x-(d==3))%w,(row//2-(d==0))%h)
        dx,dy=STEP[d]; return ((c[0]+dx)%w,(c[1]+dy)%h)
    def freepath(start,target,limit,occ):
        seen={start:0}; queue=deque([start])
        while queue:
            c=queue.popleft()
            if seen[c]>=limit: continue
            for d in range(4):
                nxt=dest(c,d)
                if nxt is None or nxt in seen: continue
                if nxt==target:return seen[c]+1
                if nxt in occ:continue
                seen[nxt]=seen[c]+1;queue.append(nxt)
        return None
    turns=[]; rnd=-1; actor=None; turn=None; present=set()
    def finish():
        nonlocal turn
        if turn is None:return
        turn['end_body']=list(bodies.get(turn['id'],()))
        turn['end_queen']=list(bodies.get(qid,()))
        turns.append(turn); turn=None
    for index,ev in enumerate(root.pointer(3)):
        kind=ev.u16(0);p=ev.pointer(0)
        if kind==0:
            finish();rnd=p.i32(0);actor=None
        elif kind==1:
            finish();actor=p.i32(0)
            if teams[actor]!=ours:continue
            b=bodies[actor]; hd=b[0];occ={c for bb in bodies.values() for c in bb}
            friends=[(i,len(bb),bb[0]) for i,bb in bodies.items() if teams[i]==ours and i!=actor]
            foes=[(i,len(bb),bb[0]) for i,bb in bodies.items() if teams[i]!=ours]
            nearq=[]
            if actor==qid and qid in bodies:
                qh=bodies[qid][0]
                for i,L,eh in foes:
                    dist=freepath(eh,qh,5,occ)
                    if dist is not None:nearq.append([i,L,eh,dist,int(view(qh,eh))])
            cut=[]
            if actor==qid:
                for i,L,eh in foes:
                    if not view(hd,eh):continue
                    visible=[c for c in bodies[i] if view(hd,c)]
                    edge=any(min(abs(c[0]-hd[0]),w-abs(c[0]-hd[0]))==3 or min(abs(c[1]-hd[1]),h-abs(c[1]-hd[1]))==3 for c in visible)
                    if edge:cut.append([i,L,len(visible),eh])
            adjacent=[]
            exits=[]
            for d in range(4):
                nxt=dest(hd,d)
                if nxt is not None and nxt not in occ:
                    exits.append([d,nxt])
                    if nxt in present:adjacent.append([d,nxt])
            leader=max([(len(bb),-i) for i,bb in bodies.items() if teams[i]==ours])
            turn=dict(r=rnd,event=index,id=actor,L=len(b),body=list(b),queen=list(bodies.get(qid,())),
                      queen_alive=qid in bodies,unit_count=1+len(friends),leader=-leader[1],
                      friends=friends,foes=[x for x in foes if view(hd,x[2])],nearq=nearq,cut=cut,
                      adjacent=adjacent,exits=exits,action=None,dirs=[],steps=[],eats=[],deaths=[],split=None)
        elif kind==3:
            c=lr.replay.point(p.pointer(0))
            if p.u32(0):present.add(c)
            else:
                present.remove(c)
                if turn is not None:turn['eats'].append(c)
        elif kind==4:
            if turn is not None:
                a=p.pointer(0);turn['action']=a.u16(0) if a else None
                turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
        elif kind==9:
            i=p.i32(0);hd,tl=lr.replay.point(p.pointer(0)),lr.replay.point(p.pointer(1));b=bodies[i]
            if b[0]!=hd:
                if turn is not None and i==actor:turn['steps'].append([b[0],hd])
                b.appendleft(hd)
            while len(b)>1 and b[-1]!=tl:b.pop()
        elif kind==10:
            parent,child=p.i32(0),p.i32(4)
            for z,i in enumerate((parent,child)):
                bodies[i]=deque(lr.replay.point(c) for c in p.pointer(z));teams[i]='AB'[p.u16(8)]
            if turn is not None:turn['split']=[parent,child,len(bodies[parent]),len(bodies[child])]
        elif kind==11:
            i=p.i32(0)
            if turn is not None:turn['deaths'].append([i,p.u16(4),len(bodies[i]),bodies[i][0]])
            bodies.pop(i)
    finish()
    assert sum(len(t['eats']) for t in turns)==base['final']['us']['pearls']
    return turns

def main():
    for gid,folder in JOBS:
        path=Path(f'data/online/live-one1/b{folder}/M{gid}.replay')
        meta=json.loads(path.with_name(f'game-{gid}.json').read_text())
        base=lr.scan(path,meta,'win2',set())
        base['intervals']={str(k):v for k,v in base['intervals'].items()}
        (OUT/f'raw-{gid}.json').write_text(json.dumps(base))
        ledger=o1_scan.scan('win2',path,meta)
        (OUT/f'ledger-{gid}.json').write_text(json.dumps(ledger))
        turns=scan(path,meta,base)
        with (OUT/f'turns-{gid}.jsonl').open('w') as out:
            for t in turns:out.write(json.dumps(t)+'\n')
        qid=base['queens']['us'];qid2=base['queens']['them']
        qs=[t for t in turns if t['id']==qid]
        attacks=[t for t in turns if any(d[0]==qid2 and d[1]==3 for d in t['deaths'])]
        print(gid,'queen_death',next((d for d in base['deaths'] if d['id']==qid),None))
        print('queen_attacks', [{k:t[k] for k in ('r','id','L','leader','queen_alive','foes','dirs','deaths')} for t in attacks])
        print('queen_adjacent_threats',[(t['r'],t['L'],t['body'][0],t['nearq'],t['dirs']) for t in qs if any(x[3]==1 for x in t['nearq'])][:12])
        print('queen_cut_count',sum(bool(t['cut']) for t in qs),'sample',[(t['r'],t['cut'],t['dirs']) for t in qs if t['cut']][:3])
        print('queen_splits',[(t['r'],t['L'],t['unit_count'],t['split']) for t in qs if t['split']])
        print('adjacent_pearl_turns/eaten',sum(bool(t['adjacent']) for t in turns),sum(bool(t['adjacent']) and bool(t['steps']) and t['steps'][0][1] in [x[1] for x in t['adjacent']] for t in turns))

if __name__=='__main__':main()
