import sys
sys.dont_write_bytecode = True
import json, importlib.util, hashlib
from pathlib import Path
from collections import deque, Counter
sys.path[:0] = ['tools', 'data/analysis/ladder/dossier/work']
from ladder_replay import replay, edge_id
from o1_scan import scan as ledger_scan

OUT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('win5_geo', 'data/codex/astra/evade/analyze.py')
geo_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(geo_module)
JOBS = [(1512750,'live-one1/b1512747'),(1512751,'live-one1/b1512747'),
        (1507573,'live-one1/b1507572'),(1507574,'live-one1/b1507572'),(1507576,'live-one1/b1507572'),
        (1508960,'live-one1/b1508960'),(1508961,'live-one1/b1508960'),(1508964,'live-one1/b1508960'),
        *[(i,'smoke/one13-p1-old') for i in (1507914,1507920,1507924,1507927)]]

def scan(gid, folder):
    path = Path('data/online') / folder / f'M{gid}.replay'
    meta = json.loads(path.with_name(f'game-{gid}.json').read_text())
    root = replay.load(path).root()
    ledger = ledger_scan('1055-win5', path, meta)
    assert int(ledger['bot']) == 21377 and ledger['result'] == 'win'
    own = int(meta['teamAId'] != 1119)
    g = geo_module.Geo(root.text(0))
    bodies, teams = {}, {}
    for line in root.text(0).splitlines():
        a = line.split()
        if a and a[0] == 'DRAGON':
            i = len(bodies)
            teams[i] = int(a[1])
            bodies[i] = deque((int(a[3+2*k]),int(a[4+2*k])) for k in range(int(a[2])))
    queens = [min(i for i in bodies if int(teams[i]!=own)==s) for s in (0,1)]
    pearls, snapshots, turns, logs, deaths, risks = set(), {}, [], [], [], []
    seen = set()
    rnd, cur, actor = -1, None, None
    acted = set()
    def state():
        return [[sum(int(teams[i]!=own)==s for i in bodies),
                 sum(len(b) for i,b in bodies.items() if int(teams[i]!=own)==s),
                 max((len(b) for i,b in bodies.items() if int(teams[i]!=own)==s), default=0),
                 len(bodies.get(queens[s],()))] for s in (0,1)]
    def gap(a,b):
        dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1])
        return min(dx,g.w-dx)+min(dy,g.h-dy)
    def close():
        nonlocal cur
        if cur is None: return
        i=cur['id']
        cur['endL']=len(bodies.get(i,()))
        cur['end']=list(bodies[i][0]) if i in bodies else None
        if i==queens[0] and i in bodies:
            h=bodies[i][0]
            attackers=[dict(id=j,L=len(b),head=list(b[0]),visible=g.visible(b[0],h))
                       for j,b in bodies.items() if teams[j]!=own and j not in acted
                       and h in g.adj[b[0]] and h not in b]
            if attackers: risks.append(dict(r=rnd,event=cur['event'],queenL=len(bodies[i]),head=list(h),attackers=attackers))
        turns.append(cur)
        cur=None
    for ei,ev in enumerate(root.pointer(3)):
        k=ev.u16(0); p=ev.pointer(0)
        if k==0:
            close()
            if rnd>=0: snapshots[rnd]=state()
            rnd=p.i32(0); acted=set(); actor=None
        elif k==1:
            close(); actor=p.i32(0); acted.add(actor)
            b=bodies[actor]; h=b[0]; side=int(teams[actor]!=own)
            occupied={c for bb in bodies.values() for c in bb}
            adj=[n for n in g.moves[h] if n is not None and n not in occupied]
            win={((h[0]+dx)%g.w,(h[1]+dy)%g.h) for dx in range(-3,4) for dy in range(-3,4)}
            if side==0: seen.update(win)
            ports=[]
            for d,n in enumerate(g.moves[h]):
                if n is not None and g.edges.get(edge_id(g.w,g.h,*h,d),(0,-1))[0]==2:
                    ports.append(dict(dir=d,dest=list(n),unseen=n not in seen,pearl=n in pearls,free=n not in occupied))
            mates=[(gap(h,bb[0]),j,list(bb[0])) for j,bb in bodies.items() if j!=actor and teams[j]==teams[actor]]
            cur=dict(r=rnd,event=ei,id=actor,s=side,L=len(b),head=list(h),body=list(b),N=state()[side][0],
                     dirs=[],steps=[],eats=[],split=None,death=None,logs=[],
                     adjacent_pearls=[list(n) for n in adj if n in pearls],free=[list(n) for n in adj],ports=ports,
                     visible_enemies=[dict(id=j,L=len(bb),head=list(bb[0])) for j,bb in bodies.items() if teams[j]!=teams[actor] and bb[0] in win],
                     mate=min(mates) if mates else None)
        elif k==3:
            c=replay.point(p.pointer(0))
            if p.u32(0): pearls.add(c)
            else:
                pearls.remove(c)
                cur['eats'].append(list(c))
        elif k==4:
            a=p.pointer(0)
            if cur is not None:
                cur['action']=a.u16(0) if a else None
                cur['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
        elif k==6:
            log=dict(r=rnd,id=p.i32(0),text=p.text(0))
            if teams.get(log['id'])==own:
                logs.append(log)
                if cur is not None: cur['logs'].append(log['text'])
        elif k==9:
            i=p.i32(0); hd,tl=replay.point(p.pointer(0)),replay.point(p.pointer(1)); b=bodies[i]
            if hd!=b[0]:
                b.appendleft(hd)
                if cur is not None and i==actor: cur['steps'].append(list(hd))
            while len(b)>1 and b[-1]!=tl: b.pop()
            assert b[-1]==tl
        elif k==10:
            ids=[p.i32(0),p.i32(4)]
            for z,i in enumerate(ids):
                bodies[i]=deque(replay.point(pt) for pt in p.pointer(z)); teams[i]=p.u16(8)
            cur['split']=[ids,[len(bodies[i]) for i in ids]]
        elif k==11:
            i=p.i32(0)
            deaths.append(dict(r=rnd,event=ei,id=i,s=int(teams[i]!=own),L=len(bodies[i]),reason=p.u16(4),actor=actor,
                               actorSide=int(teams[actor]!=own),actorL=cur['L'] if cur else None,steps=len(cur['steps']) if cur else None,
                               queen=i in queens,head=list(bodies[i][0]),state=state()))
            if cur is not None and actor==i: cur['death']=p.u16(4)
            bodies.pop(i)
    close(); snapshots[rnd]=state()
    assert state()==[x[:4] for x in ledger['ends']]
    fin=root.pointer(4)
    assert fin.bit(0) and fin.u16(4)==1 and fin.u16(6)==own
    for side in (0,1):
        st=fin.pointer(own if side==0 else 1-own)
        assert state()[side]==[st.i32(0),st.i32(8),st.i32(4),st.i32(12)]
    for side in (0,1):
        start=sum(int(a.split()[2]) for a in root.text(0).splitlines() if a.startswith('DRAGON ') and int(int(a.split()[1])!=own)==side)
        assert start+sum(e[1]==side for e in ledger['eats'])-sum(d[2] for d in ledger['deaths'] if d[1]==side)-sum(d[3] for d in ledger['paids'] if d[1]==side)==state()[side][1]
    def verdict(s):
        a,b=s
        if not a[0] or not b[0]: return (a[0]>0)-(b[0]>0)
        return ((a[3],a[2],a[1])>(b[3],b[2],b[1]))-((a[3],a[2],a[1])<(b[3],b[2],b[1]))
    ahead=rnd
    for r in reversed(sorted(snapshots)):
        if verdict(snapshots[r])!=1: break
        ahead=r
    ours=[t for t in turns if t['s']==0]
    sig={
        'eat_adj':[t for t in ours if any(p in t['eats'] for p in t['adjacent_pearls'])],
        'pass_adj':[t for t in ours if t['adjacent_pearls'] and not any(p in t['eats'] for p in t['adjacent_pearls']) and not t['split']],
        'idle':[t for t in ours if not t['steps'] and not t['split'] and t['death'] is None],
        'queen_split':[t for t in ours if t['id']==queens[0] and t['split']],
        'blind_portal_declined':[t for t in ours if t['id']!=queens[0] and t['L']<4 and t['steps'] and any(p['unseen'] and p['free'] for p in t['ports']) and not any(p['dest'] in t['steps'] for p in t['ports'] if p['unseen'])],
        'long_sprint':[t for t in ours if t['id']!=queens[0] and t['L']>=8 and len(t['steps'])>=2 and t['visible_enemies'] and not t['split']],
    }
    data=dict(gid=gid,path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),own=own,queens=queens,
              meta=meta,ledger=ledger,ahead=ahead,states=snapshots,risks=risks,deaths=deaths,logs=logs,
              signatures={k:dict(n=len(v),examples=v[:3]) for k,v in sig.items()})
    (OUT/f'{gid}.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
    (OUT/f'{gid}-turns.jsonl').write_text(''.join(json.dumps(t,ensure_ascii=False,separators=(',',':'))+'\n' for t in turns))
    print(gid,meta['mapName'],'side','AB'[own],ledger['how'],ledger['last'],'end',state(),'ahead',ahead,
          'Qdead',[(d['s'],d['r'],d['L'],d['reason'],d['actor'],d['actorL']) for d in deaths if d['queen']],
          'risks',risks[:2], 'logs',dict(Counter(l['text'].split()[0] for l in logs)),flush=True)
    return data

if __name__=='__main__':
    rows=[scan(*job) for job in JOBS]
    (OUT/'summary.json').write_text(json.dumps([dict(gid=r['gid'],how=r['ledger']['how'],end=r['ledger']['ends'],ahead=r['ahead']) for r in rows],ensure_ascii=False,indent=2)+'\n')
