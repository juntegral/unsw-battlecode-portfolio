import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from collections import Counter, defaultdict, deque
sys.path[:0] = ['tools', 'data/analysis/ladder/dossier/work']
import ladder_replay as lr
import o1_scan

OUT = Path(__file__).resolve().parent
FOLDER = Path('data/online/smoke/one8-p1-old')
IDS = [1494956, 1494960, 1494963, 1494966, 1494967]

def trace(root, gid):
    w, h = map(int, root.text(0).splitlines()[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in root.text(0).splitlines():
        q = line.split()
        if q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3+2*k]), int(q[4+2*k])) for k in range(int(q[2])))
            teams[i] = int(q[1])
        elif q[0] == 'EDGE': raw.append(tuple(map(int, q[1:4])))
    queens = [min(i for i in teams if teams[i] == s) for s in (0, 1)]
    edges = lr.canonical_edges(w, h, raw)
    portals = defaultdict(list)
    for e, (k, p) in edges.items():
        if k == 2: portals[p].append(e)
    def dest(c, d):
        e = lr.edge_id(w, h, *c, d)
        k, p = edges.get(e, (0, -1))
        if k == 1: return None
        if k == 2:
            other = next(x for x in portals[p] if x != e)
            row, x = divmod(other, w+1)
            return ((x-(d == 3)) % w, (row//2-(d == 0)) % h)
        dx, dy = o1_scan.STEP[d]
        return ((c[0]+dx) % w, (c[1]+dy) % h)
    def delta(a,b):
        dx,dy = abs(a[0]-b[0]), abs(a[1]-b[1])
        return min(dx,w-dx),min(dy,h-dy)
    def view(a,b): return max(delta(a,b)) <= 3
    def path(a, b, occ, cap=3):
        seen, qu = {a: []}, deque([a])
        while qu:
            c = qu.popleft()
            if len(seen[c]) >= cap: continue
            for d in range(4):
                n = dest(c,d)
                if n is None or n in seen: continue
                if n == b: return seen[c]+[d]
                if n in occ: continue
                seen[n] = seen[c]+[d];qu.append(n)
        return None
    pearls = set()
    rnd, actor, cur = -1, None, None
    turns, deaths, qsplits, logs = [], [], [], []
    facing = {}
    event_counts = Counter()
    def finish():
        nonlocal cur
        if cur is None: return
        cur['end'] = list(bodies[actor][0]) if actor in bodies else None
        cur['endL'] = len(bodies[actor]) if actor in bodies else 0
        cur['passed_adjacent'] = [c for c in cur['adjpearls'] if tuple(c) not in cur['eaten']]
        turns.append(cur);cur = None
    for idx, e in enumerate(root.pointer(3)):
        k,p = e.u16(0),e.pointer(0)
        event_counts[lr.replay.EVENT_NAMES[k]] += 1
        if k == 0:
            finish();rnd,actor = p.i32(0),None
        elif k == 1:
            finish();actor = p.i32(0)
            b, side = bodies[actor],teams[actor]
            occ = set(c for bb in bodies.values() for c in bb)
            qh = bodies[queens[side]][0] if queens[side] in bodies else None
            eh = bodies[queens[1-side]][0] if queens[1-side] in bodies else None
            cur = dict(gid=gid,event=idx,r=rnd,i=actor,s=side,L=len(b),h=list(b[0]),
                queen=actor==queens[side],qL=len(bodies.get(queens[side],())),
                eqL=len(bodies.get(queens[1-side],())),n=sum(teams[i]==side for i in bodies),
                qh=qh,eqh=eh,steps=[],eaten=[],deaths=[],dirs=[],split=None,
                facing=facing.get(actor),
                adjpearls=[list(dest(b[0],d)) for d in range(4) if dest(b[0],d) in pearls and dest(b[0],d) not in occ],
                near=[dict(i=i,s=teams[i],L=len(bb),h=list(bb[0]),body=list(bb)) for i,bb in bodies.items() if i!=actor and view(b[0],bb[0])],
                exits=[d for d in range(4) if dest(b[0],d) is not None and dest(b[0],d) not in occ],
                qpath=path(b[0],eh,occ,3) if eh is not None and not actor==queens[side] and sum(delta(b[0],eh))<=3 else None,
                qadj=[d for d in range(4) if dest(b[0],d)==eh] if eh is not None else [])
        elif k == 3:
            c=lr.replay.point(p.pointer(0))
            if p.u32(0): pearls.add(c)
            else:
                pearls.remove(c)
                if cur is not None: cur['eaten'].append(c)
        elif k == 4:
            a=p.pointer(0)
            if cur is not None:
                cur['action']=a.u16(0) if a else None
                cur['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) else []
        elif k == 6: logs.append(dict(r=rnd,i=p.i32(0),text=p.text(0)))
        elif k == 9:
            i=p.i32(0);hd,tl=lr.replay.point(p.pointer(0)),lr.replay.point(p.pointer(1))
            b=bodies[i]
            if b[0]!=hd:
                if cur is not None and actor==i:
                    d=cur['dirs'][len(cur['steps'])] if len(cur['steps'])<len(cur['dirs']) else None
                    cur['steps'].append(hd)
                    facing[i]=d
                b.appendleft(hd)
            while len(b)>1 and b[-1]!=tl:b.pop()
        elif k == 10:
            parent,child=p.i32(0),p.i32(4)
            before=len(bodies[parent])
            for z,i in enumerate((parent,child)):
                bodies[i]=deque(lr.replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
            split=dict(r=rnd,i=parent,child=child,L=before,parentL=len(bodies[parent]),childL=len(bodies[child]))
            if cur is not None: cur['split']=split
            if parent in queens: qsplits.append(split)
        elif k == 11:
            i=p.i32(0);d=dict(r=rnd,event=idx,i=i,s=teams[i],actor=actor,L=len(bodies[i]),reason=p.u16(4),body=list(bodies[i]))
            deaths.append(d)
            if cur is not None:cur['deaths'].append(d)
            bodies.pop(i)
    finish()
    return dict(turns=turns,deaths=deaths,qsplits=qsplits,logs=logs,event_counts=event_counts,queens=queens)

def main():
    rows=[]
    for gid in IDS:
        meta=json.loads((FOLDER/f'game-{gid}.json').read_text())
        root=lr.replay.load(FOLDER/f'M{gid}.replay').root()
        assert root.text(1)=='21126' and meta['teamAId']==1119
        original=lr.replay.load
        lr.replay.load=lambda _:type('Loaded',(),{'root':lambda _:root})()
        basic=lr.scan(FOLDER/f'M{gid}.replay',meta,str(FOLDER),set())
        ledger=o1_scan.scan('one8-p1-old',FOLDER/f'M{gid}.replay',meta)
        lr.replay.load=original
        detail=trace(root,gid)
        def score(s):return (int(s['alive']>0),s['queen_length'],s['longest'],s['total'])
        nonleading=[r for r,s in basic['snapshots'].items() if score(s['us'])<=score(s['them'])]
        lead=max(nonleading)+1 if nonleading else min(basic['snapshots'])
        assert all(score(s['us'])>score(s['them']) for r,s in basic['snapshots'].items() if r>=lead)
        row=dict(gid=gid,map=meta['mapName'],botA=root.text(1),botB=root.text(2),last=basic['last_round'],
                 final=basic['final'],lead_forever_round_end=lead,
                 qdeaths=[d for d in basic['deaths'] if d['id'] in basic['queens'].values()],
                 eats=basic['eats'],anomalies=basic['anomalies'])
        rows.append(row)
        basic['intervals']={str(k):v for k,v in basic['intervals'].items()}
        (OUT/f'{gid}-base.json').write_text(json.dumps(basic,ensure_ascii=False))
        (OUT/f'{gid}-ledger.json').write_text(json.dumps(ledger,ensure_ascii=False))
        (OUT/f'{gid}-trace.json').write_text(json.dumps(detail,ensure_ascii=False))
        print(json.dumps(row,ensure_ascii=False),flush=True)
    (OUT/'summary.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
