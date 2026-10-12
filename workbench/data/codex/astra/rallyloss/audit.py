import sys
sys.dont_write_bytecode=True
import json,csv
from pathlib import Path
from collections import deque,Counter,defaultdict
from statistics import median
sys.path.insert(0,'tools')
from ladder_replay import replay
OUT=Path('data/codex/astra/rallyloss')
def main():
    gs=list(map(json.loads,(OUT/'games.jsonl').read_text().splitlines()));totals=[];candidate_rows=[];fold_rows=[];stop_rows=[];fed_rows=[];seedrows=[];bands=defaultdict(Counter)
    for g in gs:
        root=replay.load(g['path'] if 'path' in g else f"data/online/smoke/{g['label']}-old/M{g['gid']}.replay").root();lines=root.text(0).splitlines();W,H=map(int,lines[0].split()[1:3]);j=json.loads(Path(f"data/online/smoke/{g['label']}-old/game-{g['gid']}.json").read_text());own=int(j['teamAId']!=1119)
        bodies={};teams={};starts=Counter()
        def gap(a,b):
            dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1]);return min(dx,W-dx)+min(dy,H-dy)
        def top(s):return max((i for i in bodies if teams[i]==s),key=lambda i:(len(bodies[i]),-i),default=None)
        for line in lines:
            q=line.split()
            if q and q[0]=='DRAGON':
                i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]=int(int(q[1])!=own);starts[teams[i]]+=len(bodies[i])
        for s in (0,1):
            b=g['base'];res=starts[s]+sum(e[1]==s for e in b['eats'])-sum(d[2] for d in b['deaths'] if d[1]==s)-sum(p[3] for p in b['paids'] if p[1]==s)-b['ends'][s][1];assert res==0;totals.append(dict(label=g['label'],gid=g['gid'],side=s,residual=res))
        wanted={(c['round'],c['id']):c for c in g['trace']['records'] if c['kind']=='rally-proxy'};r=-1
        for ev in root.pointer(3):
            k=ev.u16(0);p=ev.pointer(0)
            if k==0:r=p.i32(0)
            elif k==1:
                i=p.i32(0);c=wanted.get((r,i))
                if c is not None:
                    lead=c['leader'];actual=top(0);row=dict(label=g['label'],gid=g['gid'],map=g['map'],id=i,round=r,mass=c['length'],distance=c['distance'],age=r-c['leader_when'],advertised_id=lead,advertised_length=c['leader_length'],actual_length=len(bodies[lead]) if lead in bodies else 0,actual_head=list(bodies[lead][0]) if lead in bodies else None,target_error=gap(c['target'],bodies[lead][0]) if lead in bodies else None,global_top=actual,global_top_length=len(bodies[actual]) if actual is not None else 0,leader_is_global=lead==actual,inward=c['inward_rounds']>0,arrived=c['arrival'] is not None,ever_top=c['ever_top'],retained=c['end_transported']);candidate_rows.append(row)
            elif k==9:
                i=p.i32(0);hd,tl=replay.point(p.pointer(0)),replay.point(p.pointer(1));bb=bodies[i]
                if bb[0]!=hd:bb.appendleft(hd)
                while len(bb)>1 and bb[-1]!=tl:bb.pop()
            elif k==10:
                parent,child=p.i32(0),p.i32(4);teams[child]=teams[parent]
                for z,i in enumerate((parent,child)):bodies[i]=deque(replay.point(c) for c in p.pointer(z))
            elif k==11:bodies.pop(p.i32(0))
        for s in (0,1):
            lengths=[len(bb) for i,bb in bodies.items() if teams[i]==s];official=root.pointer(4).pointer(own if s==0 else 1-own)
            assert (len(lengths),max(lengths,default=0),sum(lengths))==(official.i32(0),official.i32(4),official.i32(8)),g['gid']
            assert len(bodies.get(g['queens'][s],()))==official.i32(12),g['gid']
        for c in g['trace']['records']:
            d=c['death']
            if c['kind']=='fold':
                ts=[t for t in d['eaters'] if t['side']==1 and t['eater']==d['top_id']];fold_rows.append(dict(label=g['label'],gid=g['gid'],id=c['id'],round=c['round'],mass=c['length'],distance=d['distance'],dropped=(d['length']+1)//2,to_longest=len(ts),to_mates=sum(t['side']==1 for t in d['eaters']),to_enemy=sum(t['side']==0 for t in d['eaters']),uneaten=(d['length']+1)//2-len(d['eaters']),waits=[t['wait'] for t in ts],cause=d['cause'],head=d['head']))
            if c['kind']=='rally-proxy' and d and d['cause']=='stop':
                wire=d['advertised_leader'] or {};stop_rows.append(dict(label=g['label'],gid=g['gid'],id=c['id'],round=d['round'],length=d['length'],global_distance=d['distance'],last_advertised_distance=d['advertised_distance'],to_global=sum(t['top'] and t['side']==0 for t in d['eaters']),to_reported=sum(t['eater']==wire.get('id') for t in d['eaters']),mates=sum(t['side']==0 for t in d['eaters']),foes=sum(t['side']==1 for t in d['eaters']),dropped=(d['length']+1)//2,uneaten=(d['length']+1)//2-len(d['eaters']),timeout=d['timeout']))
        fed_ids={t['eater'] for t in g['trace']['direct'] if t['side']==t['source_side'] and t['cause']=='stop' and t['top'] and t['round']>350}
        for i in fed_ids:
            st=g['all_dragons'][str(i)];death=st['death'];fed_rows.append(dict(label=g['label'],gid=g['gid'],id=i,side=st['side'],death=death,alive=death is None,stop_pearls=st['stop_drop'],final_top=i==g['snapshots'][str(g['last'])][st['side']]['id']))
        seedrows.append(dict(label=g['label'],gid=g['gid'],map=g['map'],seed=j['seed']))
    def write(name,rows):
        if not rows:return
        with (OUT/name).open('w') as f:
            wr=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');wr.writeheader();wr.writerows({k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in x.items()} for x in rows)
    write('audit.tsv',totals);write('candidate_truth.tsv',candidate_rows);write('fold.tsv',fold_rows);write('rally_stops.tsv',stop_rows);write('fed_leaders.tsv',fed_rows);write('seeds.tsv',seedrows)
    result={}
    for label in sorted({g['label'] for g in gs}):
        cs=[c for c in candidate_rows if c['label']==label];fs=[c for c in fold_rows if c['label']==label];ss=[c for c in stop_rows if c['label']==label];fds=[c for c in fed_rows if c['label']==label and c['side']==0];byage={}
        for lo,hi in [(0,5),(6,15),(16,25)]:
            xs=[c for c in cs if lo<=c['age']<=hi];byage[f'{lo}-{hi}']=dict(n=len(xs),mass=sum(c['mass'] for c in xs),wrong_top=sum(not c['leader_is_global'] for c in xs),dead_leader=sum(c['actual_length']==0 for c in xs),overstated=sum(c['advertised_length']>c['actual_length'] for c in xs),bad_ratio=sum(c['mass']*2>c['actual_length'] for c in xs),retained=sum(c['retained'] for c in xs),arrived=sum(c['arrived'] for c in xs))
        bydist={}
        for lo,hi in [(0,1),(2,3),(4,999)]:
            xs=[c for c in ss if lo<=c['global_distance']<=hi];bydist[f'{lo}-{hi}']=dict(n=len(xs),drop=sum(c['dropped'] for c in xs),to_global=sum(c['to_global'] for c in xs),mates=sum(c['mates'] for c in xs),foes=sum(c['foes'] for c in xs),uneaten=sum(c['uneaten'] for c in xs))
        result[label]=dict(age=byage,stop_distance_global=bydist,fold=dict(n=len(fs),mass=sum(c['mass'] for c in fs),drop=sum(c['dropped'] for c in fs),to_longest=sum(c['to_longest'] for c in fs),to_mates=sum(c['to_mates'] for c in fs),to_enemy=sum(c['to_enemy'] for c in fs),uneaten=sum(c['uneaten'] for c in fs),distance=dict(Counter(c['distance'] for c in fs)),wait=dict(Counter(w for c in fs for w in c['waits'])),cause=dict(Counter(c['cause'] for c in fs))),fed_our_leaders=dict(n=len(fds),alive=sum(c['alive'] for c in fds),final_top=sum(c['final_top'] for c in fds),causes=dict(Counter(c['death']['cause'] for c in fds if c['death'])),ids=fds))
    (OUT/'audit.json').write_text(json.dumps(dict(games=len(gs),all_round_ledgers=len(totals),official_final_checks=2*len(gs),official_queen_checks=2*len(gs),residuals=sum(x['residual']!=0 for x in totals),sets=result),ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
