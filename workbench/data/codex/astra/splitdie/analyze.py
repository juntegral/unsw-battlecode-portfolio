"""Read-only replay audit. Outputs are confined to this directory."""
import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from collections import Counter, defaultdict, deque
from datetime import datetime

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'data/analysis/ladder/dossier/online'),
               str(ROOT/'data/codex/astra/smallmap')]
import ladder_replay as lr
import label_report
import analyze as smallmap

def audit(g):
    root = lr.replay.load(ROOT/g['path']).root()
    w,h = map(int,root.text(0).splitlines()[0].split()[1:3])
    bodies,teams,edges0 = {},{},[]
    own = 0 if root.text(1) in ('20910','20941','20980') else 1
    # Metadata is authoritative when both teams happen to use the same bot id.
    meta=json.loads((ROOT/g['path']).with_name(f"game-{g['gid']}.json").read_text())
    own=int(meta['teamAId']!=1119)
    for line in root.text(0).splitlines():
        q=line.split()
        if q and q[0]=='DRAGON':
            i=len(bodies); teams[i]='us' if int(q[1])==own else 'them'
            bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])))
        elif q and q[0]=='EDGE': edges0.append(tuple(map(int,q[1:4])))
    queens={s:min(i for i in bodies if teams[i]==s) for s in ('us','them')}
    edges=lr.canonical_edges(w,h,edges0); portals=defaultdict(list)
    for e,(k,p) in edges.items():
        if k==2: portals[p].append(e)
    def dest(c,d):
        e=lr.edge_id(w,h,*c,d); k,p=edges.get(e,(0,-1))
        if k==1: return None
        if k==2:
            other=next(z for z in portals[p] if z!=e); row,x=divmod(other,w+1)
            return ((x-(d==3))%w,(row//2-(d==0))%h)
        dx,dy=((0,-1),(1,0),(0,1),(-1,0))[d]
        return ((c[0]+dx)%w,(c[1]+dy)%h)
    def visible(a,b):
        dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1])
        return min(dx,w-dx)<=3 and min(dy,h-dy)<=3
    def context(i,observer=None):
        hd=bodies[i][0]; occupied={c:z for z,b in bodies.items() for c in b}
        rows=[]
        for d in range(4):
            n=dest(hd,d); z=occupied.get(n)
            kind='wall' if n is None else 'free' if z is None else 'own' if z==i else 'mate' if teams[z]==teams[i] else 'enemy'
            rows.append(dict(dir=d,xy=n,kind=kind,owner=z,
                             visible=observer is None or (visible(hd,observer) and (n is None or visible(n,observer)))))
        return dict(head=hd,body=list(bodies[i]),length=len(bodies[i]),exits=sum(x['kind']=='free' for x in rows),edges=rows)
    deaths_by_event={d['event']:d for d in g['deaths']}
    splits=[]; recent={}; deaths=[]; turns=Counter(); r=-1; actor=None
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0); p=ev.pointer(0)
        if k==0:
            r=p.i32(0)
            if r>151: break
        elif k==1:
            actor=p.i32(0)
            if r<=150: turns[teams[actor]]+=1
            if actor in recent and r-recent[actor][0]['round']<=1:
                sp,role=recent[actor]
                sp['children'][role].setdefault('first_turn',dict(round=r,context=context(actor)))
        elif k==9:
            i=p.i32(0); hd=lr.replay.point(p.pointer(0)); tail=lr.replay.point(p.pointer(1)); b=bodies[i]
            if b[0]!=hd: b.appendleft(hd)
            while len(b)>1 and b[-1]!=tail: b.pop()
            assert b[-1]==tail
        elif k==10:
            parent,child=p.i32(0),p.i32(4); s=teams[parent]
            before=context(parent); origin=before['head']
            sp=dict(gid=g['gid'],round=r,event=idx,parent=parent,child=child,side=s,
                    queen=parent==queens[s],before=before,children={})
            for z,i in enumerate((parent,child)):
                bodies[i]=deque(lr.replay.point(c) for c in p.pointer(z)); teams[i]=s
            for role,i in [('parent',parent),('child',child)]:
                sp['children'][role]=context(i,origin);recent[i]=(sp,role)
            splits.append(sp)
        elif k==11:
            i=p.i32(0); d=dict(deaths_by_event[idx]); now=context(i)
            if r<=150:
                d['at_death']=now
                if i in recent and r-recent[i][0]['round']<=1:
                    sp,role=recent[i]; initial=sp['children'][role]
                    d.update(split_event=sp['event'],split_round=sp['round'],role=role,
                             split_parent=sp['parent'],split_child=sp['child'],split_queen=sp['queen'],
                             before=sp['before'],at_split=initial,
                             sibling=sp['children']['child' if role=='parent' else 'parent'])
                    original_open=[e for e in initial['edges'] if e['kind']=='free']
                    occupied={c:z for z,b in bodies.items() for c in b}
                    changed=[]
                    for e in original_open:
                        z=occupied.get(tuple(e['xy']))
                        changed.append('free' if z is None else 'own' if z==i else 'mate' if teams[z]==teams[i] else 'enemy')
                    d['original_exit_occupants_at_death']=changed
                    d['same_head']=now['head']==initial['head']
                deaths.append(d)
            bodies.pop(i)
    assert dict(turns)=={s:sum(t['n'] for t in g['turns'] if t['side']==s and t['metric']=='turns') for s in ('us','them')}
    assert len([s for s in splits if s['round']<=150])==len([s for s in g['splits'] if s['round']<=150])
    for d in deaths:
        assert d['at_death']['exits']==d['free_exits']
    return dict(gid=g['gid'],label=g['label'],build=g['build'],opponent=g['opponent'],map=g['map'],
                original=g.get('original',False),last_round=g['last_round'],turns=dict(turns),
                splits=[s for s in splits if s['round']<=150],deaths=deaths,pearls=g['pearls'])

def main():
    jobs=json.loads((OUT.parent/'smallmap/games.json').read_text())
    for g in jobs: g['original']=True
    original_ids=[g['gid'] for g in jobs]
    inv=label_report.inventory('one5-c1','old')
    for path,meta in inv['jobs']:
        cache=OUT/f"base-{meta['id']}.json"
        if cache.exists():
            g=json.loads(cache.read_text())
        else:
            root=lr.replay.load(path).root()
            w,h=map(int,root.text(0).splitlines()[0].split()[1:3])
            if w*h>1200: continue
            base=lr.scan(path,meta,'one5-c1',set())
            extra=smallmap.observe(path,meta,base)
            g={k:base[k] for k in ('gid','map','queens','last_round','deaths','pearls')}
            own='A' if meta['teamAId']==1119 else 'B'
            g.update(extra,build='one5',label='one5-c1',opponent=meta['team'+('B' if own=='A' else 'A')+'Name'],path=str(path.relative_to(ROOT)))
            cache.write_text(json.dumps(g,separators=(',',':')))
        jobs.append(g)
    (OUT/'inventory.json').write_text(json.dumps(dict(time=datetime.now().astimezone().isoformat(),original_ids=original_ids,
        additional_ids=[g['gid'] for g in jobs if not g.get('original')],notes=inv['notes']),indent=2))
    for g in jobs:
        cache=OUT/f"g{g['gid']}.json"
        if cache.exists(): continue
        a=audit(g); cache.write_text(json.dumps(a,separators=(',',':')))
        print(g['gid'],g['label'],len(a['splits']),len(a['deaths']),flush=True)

if __name__=='__main__': main()
