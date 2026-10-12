"""Offline small-map replay audit; all writes stay beside this script."""
import sys
sys.dont_write_bytecode = True
import json
import csv
from pathlib import Path
from collections import Counter, defaultdict, deque
from datetime import datetime

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'data/analysis/ladder/dossier/online'),
               str(ROOT/'data/analysis/ladder/dossier/work')]
import label_report
import ladder_replay as lr
import o1_scan

BUILDS = {'20910': 'one3', '20941': 'one4', '20980': 'one5'}
STEP = ((0,-1),(1,0),(0,1),(-1,0))

def inventory():
    header_path=OUT/'headers.json'
    headers=json.loads(header_path.read_text()) if header_path.exists() else {}
    previous=OUT/'inventory.json'
    if previous.exists():
        for inv in json.loads(previous.read_text())['inventories']:
            for rec in inv['included']:
                headers.setdefault(str(rec['gid']),dict(bot=next(k for k,v in BUILDS.items() if v==rec['build']),cells=rec['cells']))
    inventories = [label_report.inventory(f'{b}-{s}', 'old') for b in BUILDS.values() for s in ('w1','d1')]
    inventories.append(label_report.directory_inventory('ranked', str(ROOT/'data/online/live-one1/b*')))
    seen, jobs, audit = set(), [], []
    for inv in inventories:
        included = []
        for path, meta in inv['jobs']:
            if inv['label'] == 'ranked' and not meta.get('ranked'):
                continue
            if meta['id'] in seen:
                continue
            own = 'A' if meta['teamAId'] == 1119 else 'B'
            header=headers.get(str(meta['id']))
            if header is None:
                root = lr.replay.load(path).root()
                bot = root.text(1 if own == 'A' else 2)
                w,h = map(int,root.text(0).splitlines()[0].split()[1:3])
                header=dict(bot=bot,cells=w*h)
                headers[str(meta['id'])]=header
            bot=header['bot'];cells=header['cells']
            if bot not in BUILDS:
                continue
            seen.add(meta['id'])
            included.append(dict(gid=meta['id'], build=BUILDS[bot], cells=cells))
            if cells <= 1200:
                jobs.append((inv['label'],path,meta,BUILDS[bot]))
        audit.append(dict(label=inv['label'],planned=inv['planned'],notes=inv['notes'],included=included))
    header_path.write_text(json.dumps(headers))
    return jobs, audit

def observe(path, meta, base):
    root = lr.replay.load(path).root()
    w,h = map(int,root.text(0).splitlines()[0].split()[1:3])
    bodies,teams,raw = {},{},[]
    own = 0 if meta['teamAId']==1119 else 1
    for line in root.text(0).splitlines():
        q=line.split()
        if q and q[0]=='DRAGON':
            i=len(bodies); teams[i]='us' if int(q[1])==own else 'them'
            bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])))
        elif q and q[0]=='EDGE': raw.append(tuple(map(int,q[1:4])))
    edges=lr.canonical_edges(w,h,raw)
    portals=defaultdict(list)
    for e,(k,p) in edges.items():
        if k==2: portals[p].append(e)
    def dest(c,d):
        e=lr.edge_id(w,h,*c,d); k,p=edges.get(e,(0,-1))
        if k==1: return None
        if k==2:
            other=next(z for z in portals[p] if z!=e)
            row,x=divmod(other,w+1)
            return ((x-(d==3))%w,(row//2-(d==0))%h)
        return ((c[0]+STEP[d][0])%w,(c[1]+STEP[d][1])%h)
    cells=[(x,y) for y in range(h) for x in range(w)]
    graph={c:[n for d in range(4) if (n:=dest(c,d)) is not None] for c in cells}
    reverse=defaultdict(list)
    for c,ns in graph.items():
        for n in ns: reverse[n].append(c)
    distance_cache={}
    def distances(c):
        if c not in distance_cache:
            ds={c:0}; q=deque([c])
            while q:
                a=q.popleft()
                for n in reverse[a]:
                    if n not in ds: ds[n]=ds[a]+1; q.append(n)
            distance_cache[c]=ds
        return distance_cache[c]
    def visible(c,center):
        dx,dy=abs(c[0]-center[0]),abs(c[1]-center[1])
        return min(dx,w-dx)<=3 and min(dy,h-dy)<=3
    def counts(): return {s:sum(teams[i]==s for i in bodies) for s in ('us','them')}
    def totals(): return {s:sum(len(b) for i,b in bodies.items() if teams[i]==s) for s in ('us','them')}
    def exits(i):
        occupied={c for b in bodies.values() for c in b}
        return sum(n not in occupied for n in graph[bodies[i][0]])
    deaths_by_event={d['event']:d for d in base['deaths']}
    collisions={c['turn_start']:c for c in base['collisions']}
    pearl_by_id={p['pearl']:p for p in base['pearls']}
    lastsplit={}; born={}; turns=Counter(); splits=[]; r=-1; actor=None; turn=None
    extras={}; encounters=[]; action_kind=None; dirs=[]; used=0
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0); p=ev.pointer(0)
        if k==0: r=p.i32(0)
        elif k==1:
            actor=p.i32(0); s=teams[actor]; enemy='them' if s=='us' else 'us'
            hd=bodies[actor][0]; L=len(bodies[actor]); cnt=counts()
            balance='behind' if cnt[s]<cnt[enemy] else 'ahead' if cnt[s]>cnt[enemy] else 'equal'
            vw={z:sum(teams[i]==z and visible(b[0],hd) for i,b in bodies.items()) for z in ('us','them')}
            turn=dict(round=r,actor=actor,side=s,L0=L,counts=cnt,view=vw,total=totals(),
                      visible_parts={i:sum(visible(c,hd) for c in b) for i,b in bodies.items()},
                      head=hd,free_exits=exits(actor),balance=balance)
            dirs=[];used=0;action_kind=None
            if r<=150:
                turns[(s,balance,'turns')]+=1
                # Conservative opportunities: visible target, <=3 free steps, static clear path.
                heads={b[0]:i for i,b in bodies.items() if teams[i]!=s and visible(b[0],hd)}
                occupied={c for b in bodies.values() for c in b}
                q=deque([(hd,0)]); seen={hd}; targets=[]; reach=min(3,(L+3)//4)
                while q:
                    a,depth=q.popleft()
                    if depth>=reach: continue
                    for n in graph[a]:
                        if n in seen: continue
                        seen.add(n)
                        if n in heads: targets.append(heads[n])
                        elif n not in occupied: q.append((n,depth+1))
                if targets:
                    turns[(s,balance,'opportunities')]+=1
                    hit=idx in collisions and collisions[idx]['cross_team']
                    turns[(s,balance,'taken')]+=hit
                    encounters.append(dict(round=r,actor=actor,side=s,length=L,balance=balance,
                                           counts=cnt,targets=targets,rammed=hit))
        elif k==4:
            a=p.pointer(0); action_kind=a.u16(0) if a else None
            dirs=list(a.pointer(0)) if a and action_kind==0 and a.pointer(0) is not None else []
            used=0
        elif k==9:
            i=p.i32(0); hd=lr.replay.point(p.pointer(0)); tail=lr.replay.point(p.pointer(1)); b=bodies[i]
            if b[0]!=hd:
                b.appendleft(hd)
                if i==actor: used+=1
            while len(b)>1 and b[-1]!=tail: b.pop()
            assert b[-1]==tail
        elif k==10:
            parent,child=p.i32(0),p.i32(4)
            L=len(bodies[parent]); s=teams[parent]
            for z,i in enumerate((parent,child)):
                bodies[i]=deque(lr.replay.point(c) for c in p.pointer(z));teams[i]=s;lastsplit[i]=r
            born[child]=r
            splits.append(dict(round=r,side=s,parent=parent,child=child,before=L,
                               after=[len(bodies[parent]),len(bodies[child])],child_exits=exits(child)))
        elif k==11:
            i=p.i32(0); d=deaths_by_event[idx]; s=teams[i]
            ex=dict(turn=turn,free_exits=exits(i),since_split=r-lastsplit[i] if i in lastsplit else None,
                    age=r-born[i] if i in born else None,action_kind=action_kind,
                    collided_with_side=teams.get(d['hit']))
            d.update(ex)
            if d['reason']==3 and i!=actor:
                excluded={i,actor}
                survivors=[(z,b[0],teams[z]) for z,b in bodies.items() if z not in excluded]
                cid=d['collision']; c=next(c for c in base['collisions'] if c['collision']==cid)
                c.update(round=r,actor=actor,side=teams[actor],victim=i,lengths={teams[actor]:len(bodies[actor]),s:len(bodies[i])},
                         turn=turn,pre_total=totals(),pre_counts=counts(),nearest_head={})
                for z in ('us','them'):
                    ds=distances(bodies[i][0]); c['nearest_head'][z]=min((ds.get(hd,9999) for _,hd,ss in survivors if ss==z),default=9999)
                for did in c['deaths']:
                    victim=next(dd for dd in base['deaths'] if dd['death']==did)
                    for pid in victim['pearls']:
                        pr=pearl_by_id[pid]; ds=distances(tuple(pr['xy']))
                        pr['near_at_collision']={z:min((ds.get(hd,9999) for _,hd,ss in survivors if ss==z),default=9999) for z in ('us','them')}
            bodies.pop(i)
    for c in base['collisions']:
        if not c['cross_team']: continue
        ds=[d for d in base['deaths'] if d['death'] in c['deaths']]
        ps=[pearl_by_id[pid] for d in ds for pid in d['pearls']]
        c['drops']=ps
        c['recovered5']={s:sum(p['eater']==s and p['wait']<=5 for p in ps) for s in ('us','them')}
        c['direct_net5']={s:-sum(d['length'] for d in ds if d['side']==s)+c['recovered5'][s] for s in ('us','them')}
        after=base['snapshots'][min(c['round']+5,base['last_round'])]
        c['board_delta5']={s:after[s]['total']-c['pre_total'][s] for s in ('us','them')}
        c['window_complete']=c['round']+5<=base['last_round']
        t=c['turn']; enemy='them' if c['side']=='us' else 'us'; v=c['victim']
        c['equal_at_impact']=c['lengths']['us']==c['lengths']['them']
        c['trade_even_geometry']=(t['L0']<=4 and t['view'][c['side']]-t['view'][enemy]>=1 and t['visible_parts'].get(v,0)>=t['L0'])
        c['hunt_small_geometry']=(t['L0']<=4 and t['visible_parts'].get(v,0)>=2*t['L0'])
    for d in base['deaths']:
        if d['reason']==3:
            d['category']=('rams' if d['id']==d['actor'] else 'rammed') if d['collision'] and next(c for c in base['collisions'] if c['collision']==d['collision'])['cross_team'] else 'mate_head'
        elif d['reason']==0: d['category']='wall'
        elif d['reason']==1: d['category']='self'
        elif d['reason']==2: d['category']='mate_body' if d['collided_with_side']==d['side'] else 'enemy_body'
        else: d['category']=d['other']
        d['postsplit_boxed_proxy']=(d['since_split'] is not None and d['since_split']<=1 and d['free_exits']==0 and d['reason']!=3)
    return dict(splits=splits,turns=[dict(side=s,balance=b,metric=m,n=n) for (s,b,m),n in turns.items()],encounters=encounters)

def run():
    jobs,audit=inventory()
    (OUT/'inventory.json').write_text(json.dumps(dict(time=datetime.now().astimezone().isoformat(),inventories=audit),ensure_ascii=False,indent=2))
    output=[]
    for label,path,meta,build in jobs:
        cache=OUT/f'g{meta["id"]}.json'
        if cache.exists():
            output.append(json.loads(cache.read_text()));continue
        base=lr.scan(path,meta,label,set())
        extra=observe(path,meta,base)
        validation=o1_scan.scan(label,path,meta)
        assert len(base['deaths'])==len(validation['deaths'])
        assert len(extra['splits'])==len(validation['splits'])
        for r,vs in validation['snaps'].items():
            for z,s in enumerate(('us','them')):
                snap=base['snapshots'][int(r)][s]
                assert [snap['alive'],snap['total']]==vs[z][:2],(meta['id'],r,s)
        assert Counter(d['category'] for d in base['deaths'] if d['category'] in ('rams','rammed'))==Counter(d[4] for d in validation['deaths'] if d[4] in ('rams','rammed'))
        result='draw' if base['winner'] is None else 'win' if base['winner']==base['ours'] else 'loss'
        keep=('gid','map','queens','last_round','snapshots','final','deaths','collisions','pearls','anomalies')
        row={k:base[k] for k in keep}
        row.update(extra,build=build,label=label,result=result,cells=validation['cells'],
                   opponent=validation['opp'],path=str(path.relative_to(ROOT)),verified=True)
        cache.write_text(json.dumps(row,ensure_ascii=False,separators=(',',':')))
        output.append(row)
        print(meta['id'],build,label,row['map'],result,len(row['collisions']),flush=True)
    (OUT/'games.json').write_text(json.dumps(output,ensure_ascii=False,separators=(',',':')))
    print('DONE',len(output),Counter(g['result'] for g in output),flush=True)

if __name__=='__main__': run()
