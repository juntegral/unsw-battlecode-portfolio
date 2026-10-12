import sys
sys.dont_write_bytecode=True
import json, hashlib, importlib.util, re
from pathlib import Path
from collections import Counter,defaultdict,deque
from datetime import datetime
ROOT=Path.cwd(); OUT=ROOT/'data/codex/astra/audit-threat'
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'data/analysis/ladder/dossier/local'),str(ROOT/'data/analysis/ladder/dossier/online')]
import ladder_replay as lr
import scoreboard as sb
import label_report
spec=importlib.util.spec_from_file_location('evade_geo',ROOT/'data/codex/astra/evade/analyze.py'); geo_mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(geo_mod)
BOTS={'20980':5,'21086':7,'21126':8,'21165':9,'21200':10}
CLASSES=('one_free','several_free','paid','pearl_extended','view_cut','unseen')

def inventory():
    patterns=[str(ROOT/f'data/online/smoke/one{v}-{s}-old') for v in (5,7,8,9,10) for s in ('w1','c1','k1')]+[str(ROOT/'data/online/live-one1/b*')]
    inv=label_report.directory_inventory('audit-threat',','.join(patterns))
    manifest=[];ignored=Counter(); errors=[]
    for path,meta in inv['jobs']:
        try:
            root=sb.load_replay(path).root(); own=0 if meta['teamAId']==1119 else 1; bot=root.text(1+own)
            if bot not in BOTS:ignored[bot]+=1;continue
            if root.pointer(4) is None or not root.pointer(4).bit(0):errors.append([meta['id'],'unfinished']);continue
            manifest.append(dict(gid=meta['id'],path=str(path.relative_to(ROOT)),meta=meta,bot=bot,version=BOTS[bot],sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        except Exception as e:errors.append([str(path),repr(e)])
    data=dict(cutoff=datetime.now().astimezone().isoformat(),games=manifest,ignored=dict(ignored),errors=errors,duplicates=inv['duplicate_ids'],notes=inv['notes'])
    (OUT/'inventory.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
    print('inventory',dict(Counter(x['version'] for x in manifest)),len(data['duplicates']),flush=True)
    return manifest

def scan(job):
    path=ROOT/job['path']; root=sb.load_replay(path).root(); text=root.text(0); g=geo_mod.Geo(text)
    own=0 if job['meta']['teamAId']==1119 else 1
    bodies={};teams={}
    for line in text.splitlines():
        q=line.split()
        if q and q[0]=='DRAGON':
            i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]=int(q[1])
    queen=min(i for i in bodies if teams[i]==own)
    enemyqueen=min(i for i in bodies if teams[i]!=own)
    present={}; actor=None;rnd=0;current=None; rows=[];last={};deaths=[];rams=[];logs=[];seen_cells=defaultdict(set);all_logs=Counter();counts=Counter();qlens=Counter()
    points=[]; born={i:0 for i in bodies};finalround=0
    def window(h):return {((h[0]+dx)%g.w,(h[1]+dy)%g.h) for dx in range(-3,4) for dy in range(-3,4)}
    def edge(c,h):
        dx=abs(c[0]-h[0]);dy=abs(c[1]-h[1]);return min(dx,g.w-dx)==3 or min(dy,g.h-dy)==3
    def food_dist(start, goals):
        if start in goals:return 0
        seen={start};queue=deque([(start,0)])
        while queue:
            c,d=queue.popleft()
            for n in g.adj[c]:
                if n in goals:return d+1
                if n not in seen:seen.add(n);queue.append((n,d+1))
        return 10**9
    def finish():
        nonlocal current
        if current is None:return
        i=current['id'];current['end']=list(bodies[i][0]) if i in bodies else None;current['endL']=len(bodies.get(i,()))
        if teams[i]==own:
            current['logs']=[x['text'] for x in logs if x['seq']==current['seq'] and x['id']==i]
            if current['q']:
                # Distance to pearls visible at turn start, frozen topology; this is a movement proxy, not policy intent.
                ps=[tuple(p) for p in current.pop('_food')]
                if ps:
                    start=tuple(current['head']);end=tuple(current['end']) if current['end'] else start
                    ds0=food_dist(start,set(ps))
                    ds1=food_dist(end,set(ps))
                    current['food_distance_start']=ds0;current['food_distance_end']=ds1
                    current['not_toward_food']=int(current['ate']==0 and ds1>=ds0)
                    counts['queen_food_known_turns']+=1;counts['queen_not_toward_food']+=current['not_toward_food']
                else:counts['queen_food_absent_turns']+=1
            rows.append(current)
        last[i]=current;current=None
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0);p=ev.pointer(0)
        if k==0:
            finish();rnd=p.i32(0);finalround=rnd;actor=None
        elif k==1:
            finish();actor=p.i32(0);b=bodies[actor];h=b[0];win=window(h) if teams[actor]==own else set()
            current=dict(seq=idx,r=rnd,id=actor,q=int(actor==queen),L=len(b),head=list(h),steps=0,ate=0,natural=0,dirs=[],path=[],split=0,pearl_path=[],seen={},born=born.get(actor,0))
            # Last decision's direct view is the information relevant to a later ram.
            for j,bb in bodies.items():
                if teams[actor]==own and teams[j]!=own and bb[0] in win:
                    parts=sum(c in win for c in bb)
                    if parts:current['seen'][j]=dict(head=list(bb[0]),head_seen=bb[0] in win,parts=parts,L=len(bb),edge=any(c in win and edge(c,h) for c in bb),cut=parts<len(bb))
            if teams[actor]==own:
                counts['queen_turns' if actor==queen else 'other_turns']+=1
                if actor!=queen and len(b)<=4:counts['short_turns']+=1
                if actor==queen:
                    qlens[len(b)]+=1;current['_food']=[list(c) for c in present if c in win]
                    current['open_start']=sum(n is not None and not any(n in bb for bb in bodies.values()) for n in g.moves[h])
                    current['portal_options']=[d for d in range(4) if g.edges.get(lr.edge_id(g.w,g.h,*h,d),(0,-1))[0]==2]
                    current['known_cells_before']=len(seen_cells[actor]);current['unseen_portal_options']=[d for d in current['portal_options'] if g.moves[h][d] not in seen_cells[actor] and g.moves[h][d] not in win]
                current['ally_heads']=sum(j!=actor and teams[j]==own and bb[0] in win for j,bb in bodies.items())
                current['enemy_heads']=sum(teams[j]!=own and bb[0] in win for j,bb in bodies.items())
                seen_cells[actor].update(win)
        elif k==4:
            a=p.pointer(0)
            if current is not None:
                current['action']=a.u16(0) if a else None;current['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
                current['points']=p.pointer(1).u64(0) if p.pointer(1) else None
        elif k==6:
            txt=p.text(0);di=p.i32(0)
            if teams.get(di)==own:
                all_logs[txt.split()[0] if txt.split() else 'empty']+=1
                logs.append(dict(r=rnd,id=di,seq=current['seq'] if current else None,text=txt))
        elif k==3:
            c=lr.replay.point(p.pointer(0))
            if p.u32(0):
                assert c not in present
                present[c]='natural' if actor is None else 'drop'
            else:
                origin=present.pop(c);assert current is not None
                current['ate']+=1;current['natural']+=origin=='natural';current['pearl_path'].append(dict(c=list(c),at_step=current['steps']+1,origin=origin))
                if teams[actor]==own:
                    cat='queen' if actor==queen else 'other'
                    counts[cat+'_pearls']+=1;counts[cat+'_natural']+=origin=='natural'
                    if actor!=queen and current['L']<=4:counts['short_pearls']+=1;counts['short_natural']+=origin=='natural'
        elif k==9:
            i=p.i32(0);h=lr.replay.point(p.pointer(0));tail=lr.replay.point(p.pointer(1));b=bodies[i]
            if b[0]!=h:
                prev=b[0];b.appendleft(h)
                if i==actor:
                    if current['q']:
                        d=current['dirs'][current['steps']] if current['steps']<len(current['dirs']) else None
                        if d is not None and g.edges.get(lr.edge_id(g.w,g.h,*prev,d),(0,-1))[0]==2:
                            current.setdefault('portals',[]).append(dict(step=current['steps']+1,exit=list(h),exit_seen=h in seen_cells[i],open_start=current['open_start']))
                    current['steps']+=1;current['path'].append(list(h))
            while len(b)>1 and b[-1]!=tail:b.pop()
            assert b[-1]==tail
        elif k==10:
            par,ch=p.i32(0),p.i32(4)
            for z,i in enumerate((par,ch)):
                bodies[i]=deque(lr.replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
            born[ch]=rnd
            if current:current['split']=1
        elif k==11:
            i=p.i32(0);reason=p.u16(4);b=bodies[i]
            dr=dict(gid=job['gid'],v=job['version'],r=rnd,id=i,q=i==queen,L=len(b),reason=reason,actor=actor,event=idx,ours=teams[i]==own,head=list(b[0]))
            if reason==3 and i!=actor and teams[i]==own and teams[actor]!=own:
                prior=last.get(i);info=prior['seen'].get(actor) if prior else None
                step=current['steps']+1;free=(current['L']+3)//4;plain=free+current['L']-2
                cls=('unseen' if not info or not info['head_seen'] else 'view_cut' if info['cut'] else 'pearl_extended' if step>plain else 'paid' if step>free else 'several_free' if step>1 else 'one_free')
                ram=dict(dr,reach_class=cls,attacker=actor,attacker_L=current['L'],steps=step,free=free,ate=current['ate'],pearl_extended=step>plain,view_cut=bool(info and info['cut']),view_edge=bool(info and info['edge']),visible_parts=info['parts'] if info else 0,last_turn=prior['r'] if prior else None,turn=prior,attacker_start=current['head'],born_after_decision=bool(prior and born[actor]>=prior['r'] and actor not in prior['seen']),pearl_path=current['pearl_path'])
                # Preserve a compact exact last-decision witness for queen cases.
                rams.append(ram);dr['reach_class']=cls
            elif i==queen:
                dr['reach_class']='queen_ram_mover' if reason==3 else {0:'wall',1:'own_body',2:'other_body',4:'no_action'}.get(reason,'other')
                dr['turn']=current.copy() if actor==i and current else last.get(i)
            deaths.append(dr);bodies.pop(i)
    finish()
    for s in (0,1):
        ls=[len(b) for i,b in bodies.items() if teams[i]==s];st=root.pointer(4).pointer(s)
        assert (len(ls),max(ls,default=0),sum(ls))==(st.i32(0),st.i32(4),st.i32(8)),job['gid']
    death_by={d['id']:d for d in deaths};fates=[]
    for row in rows:
        dd=death_by.get(row['id']);row['next5']='dead' if dd and row['r']<=dd['r']<=row['r']+5 else 'alive' if finalround>=row['r']+5 else 'censored'
        if row['next5']=='dead':row['death_r']=dd['r'];row['death_reason']=dd.get('reach_class',str(dd['reason']))
        for tag in ('SEVADE','QEXIT'):
            matches=[s for s in row['logs'] if s.startswith(tag+' ')]
            if matches:fates.append(dict(tag=tag,r=row['r'],id=row['id'],L=row['L'],q=row['q'],next5=row['next5'],death_r=row.get('death_r'),death_reason=row.get('death_reason'),logs=matches,ate=row['ate'],steps=row['steps'],food=row.get('not_toward_food'),head=row['head'],end=row['end'],dirs=row['dirs'],action=row.get('action')))
    game=dict(gid=job['gid'],v=job['version'],bot=job['bot'],path=job['path'],opp=job['meta']['teamBName' if own==0 else 'teamAName'],opp_id=job['meta']['teamBId' if own==0 else 'teamAId'],opp_bot=root.text(2-own),map=job['meta']['mapName'],side=own,rounds=finalround,counts=dict(counts),qlens=dict(qlens),qfinal=len(bodies.get(queen,())),queen=queen,enemyqueen=enemyqueen,deaths=[d for d in deaths if d['ours']],rams=rams,logs=dict(all_logs),fates=fates)
    import gzip
    with gzip.open(OUT/f'turns-{job["gid"]}.json.gz','wt') as f:json.dump(rows,f,separators=(',',':'))
    (OUT/f'g{job["gid"]}.json').write_text(json.dumps(game,ensure_ascii=False,separators=(',',':')))
    return game

def main():
    jobs=inventory() if '--refresh' in sys.argv or not (OUT/'inventory.json').exists() else json.loads((OUT/'inventory.json').read_text())['games']
    jobs.sort(key=lambda j:(-j['version'],j['gid']))
    shard=int(sys.argv[sys.argv.index('--shard')+1]) if '--shard' in sys.argv else 0
    shards=int(sys.argv[sys.argv.index('--shard')+2]) if '--shard' in sys.argv else 1
    jobs=[j for j in jobs if j['gid']%shards==shard]
    for n,j in enumerate(jobs):
        if (OUT/f'g{j["gid"]}.json').exists() and '--rescan' not in sys.argv:continue
        try:
            g=scan(j);print(n+1,len(jobs),j['gid'],j['version'],g['opp'],'rams',len(g['rams']),flush=True)
        except Exception:
            import traceback;traceback.print_exc();raise
if __name__=='__main__':main()
