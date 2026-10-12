import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from collections import Counter, deque, defaultdict

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT / 'tools'))
import ladder_replay as lr
OUT = Path(__file__).resolve().parent
FOLDER = ROOT / 'data/online/live-one1/b1493690'

def run(gid):
    meta = json.loads((FOLDER / f'game-{gid}.json').read_text())
    path = FOLDER / f'M{gid}.replay'
    base = lr.scan(path, meta, str(FOLDER), set())
    root = lr.replay.load(path).root()
    w, h = map(int, root.text(0).splitlines()[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in root.text(0).splitlines():
        q = line.split()
        if q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3+2*k]), int(q[4+2*k])) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    edges = lr.canonical_edges(w, h, raw)
    portals = defaultdict(list)
    for e, (kind, pid) in edges.items():
        if kind == 2:
            portals[pid].append(e)
    queen, foe = base['queens']['us'], base['queens']['them']
    def dist(a, b):
        dx, dy = abs(a[0]-b[0]), abs(a[1]-b[1])
        return min(dx,w-dx)+min(dy,h-dy)
    def visible(a,b):
        dx, dy = abs(a[0]-b[0]), abs(a[1]-b[1])
        return min(dx,w-dx)<=3 and min(dy,h-dy)<=3
    def dest(a,d):
        e = lr.edge_id(w,h,*a,d)
        kind,pid = edges.get(e,(0,-1))
        if kind == 1:
            return None
        if kind == 2:
            pair = next(z for z in portals[pid] if z != e)
            row,x = divmod(pair,w+1)
            return ((x-(d==3))%w,(row//2-(d==0))%h)
        dx,dy = lr.base.STEP[d]
        return ((a[0]+dx)%w,(a[1]+dy)%h)
    # Legal current-state ram search: fixed starting free allowance, dynamic body and pearls.
    def ram_path(i,target,cap=8):
        start = tuple(bodies[i]); free=(len(start)+3)//4
        blocked={c for j,b in bodies.items() if j!=i for c in b}
        states=deque([(start,frozenset(),())]); seen=set()
        while states:
            body,eaten,path=states.popleft()
            paid=len(path)>=free
            if len(path)>=cap or (paid and len(body)<=2):
                continue
            for d in range(4):
                c=dest(body[0],d)
                if c is None or c in body:
                    continue
                if c==target:
                    return path+(d,)
                if c in blocked:
                    continue
                eat=c in present and c not in eaten
                new=(c,)+body
                if not eat:
                    new=new[:-1]
                if paid:
                    new=new[:-1]
                meal=eaten|{c} if eat else eaten
                key=(new,meal,len(path)+1)
                if key not in seen:
                    seen.add(key);states.append((new,meal,path+(d,)))
        return None
    present=set(); rnd=0; actor=None; turn=None; turns=[]; risks=[]
    def close():
        if turn is None:
            return
        turn['end']=list(bodies[actor][0]) if actor in bodies else None
        turn['end_length']=len(bodies.get(actor,()))
        turn['missed_adjacent']=bool(turn['adjacent'] and not set(map(tuple,turn['adjacent'])) & set(map(tuple,turn['meals'])))
        turns.append(turn)
    for idx,e in enumerate(root.pointer(3)):
        k=e.u16(0); p=e.pointer(0)
        if k==0:
            close();turn=None;rnd=p.i32(0);actor=None
        elif k==1:
            close();actor=p.i32(0)
            b=bodies[actor]; own=teams[actor]=='B'
            occupied={c:j for j,bb in bodies.items() for c in bb}
            adjacent=[dest(b[0],d) for d in range(4)]
            meals=[c for c in adjacent if c in present and c not in occupied]
            heads={j:(len(bb),list(bb[0])) for j,bb in bodies.items() if visible(b[0],bb[0])}
            turn=dict(round=rnd,event=idx,id=actor,own=own,length=len(b),head=list(b[0]),
                      dirs=[],steps=[],meals=[],split=False,deaths=[],adjacent=meals,
                      heads=heads,counts=[sum(t==s for j,t in teams.items() if j in bodies) for s in 'AB'])
            if actor==queen:
                turn['exits']=[list(c) for c in adjacent if c is not None and c not in occupied]
                turn['body']=list(map(list,b))
            if not own and queen in bodies:
                # Necessary geometric lower bound avoids searches in separated regions.
                if portals or dist(b[0],bodies[queen][0])<=min(8,(len(b)+3)//4+len(b)-2+len(present)):
                    hit=ram_path(actor,bodies[queen][0])
                    if hit is not None:
                        risks.append(dict(round=rnd,id=actor,length=len(b),head=list(b[0]),queen=list(bodies[queen][0]),
                                          queen_length=len(bodies[queen]),path=list(hit),actual=[],event=idx,
                                          queen_in_view=visible(b[0],bodies[queen][0])))
        elif k==3:
            c=lr.replay.point(p.pointer(0))
            if p.u32(0):
                present.add(c)
            else:
                present.remove(c);turn['meals'].append(list(c))
        elif k==4:
            a=p.pointer(0)
            turn['action_kind']=a.u16(0) if a else None
            turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
        elif k==9:
            i=p.i32(0);hd=lr.replay.point(p.pointer(0));tail=lr.replay.point(p.pointer(1));b=bodies[i]
            if b[0]!=hd:
                if i==actor:
                    turn['steps'].append(list(hd))
                b.appendleft(hd)
            while len(b)>1 and b[-1]!=tail:
                b.pop()
            assert b[-1]==tail
        elif k==10:
            turn['split']=True
            for z,i in enumerate((p.i32(0),p.i32(4))):
                bodies[i]=deque(lr.replay.point(pt) for pt in p.pointer(z));teams[i]='AB'[p.u16(8)]
        elif k==11:
            turn['deaths'].append(dict(id=p.i32(0),reason=p.u16(4)))
            bodies.pop(p.i32(0))
    close()
    turn_by_event={t['event']:t for t in turns}
    for risk in risks:
        risk['actual']=turn_by_event[risk['event']]['dirs']
    def score(s):
        return (int(s['alive']>0),s['queen_length'],s['longest'],s['total'])
    ahead=[r for r,ss in base['snapshots'].items() if score(ss['us'])>score(ss['them'])]
    permanent=next(r for r in ahead if all(rr in ahead for rr in range(r,base['last_round']+1)))
    ours=[t for t in turns if t['own']]
    summary=dict(gid=gid,map=meta['mapName'],bot=base['bots']['B'],queens=base['queens'],
                 final=base['final'],last_round=base['last_round'],ahead_for_good=permanent,
                 risks=risks,turns=len(ours),adjacent_turns=sum(bool(t['adjacent']) for t in ours),
                 missed_adjacent=sum(t['missed_adjacent'] for t in ours),
                 miss_without_split=sum(t['missed_adjacent'] and not t['split'] for t in ours),
                 empty_actions=[t for t in ours if t.get('action_kind')==2],
                 queen_splits=[t for t in ours if t['id']==queen and t['split']],
                 no_logs=not any(e.u16(0) in (5,6) for e in root.pointer(3)))
    (OUT/f'turns-{gid}.json').write_text(json.dumps(turns,ensure_ascii=False))
    (OUT/f'summary-{gid}.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    base['intervals']={str(k):v for k,v in base['intervals'].items()}
    (OUT/f'base-{gid}.json').write_text(json.dumps(base,ensure_ascii=False))
    print(json.dumps({k:v for k,v in summary.items() if k not in ('empty_actions','queen_splits','risks')},ensure_ascii=False))
    print('risks',json.dumps(risks[:10]),'total',len(risks))
    print('queen_splits',[(t['round'],t['length'],t['end_length']) for t in summary['queen_splits']])
    print('empty',[(t['round'],t['id'],t['length'],t['deaths']) for t in summary['empty_actions']][:15])

if __name__=='__main__':
    for gid in (1493691,1493692):
        run(gid)
