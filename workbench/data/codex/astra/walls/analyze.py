"""Read-only online census; output stays beside this script."""
import sys
sys.dont_write_bytecode = True
import json, hashlib
import multiprocessing
from pathlib import Path
from collections import Counter, defaultdict, deque
from datetime import datetime

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
sys.path[:0] = [str(OUT.parent/'audit-move'), str(OUT.parent/'deathcell'),
               str(OUT.parent/'evade'), str(ROOT/'tools'),
               str(ROOT/'data/analysis/ladder/dossier/online')]
from audit import bot_identity
from scan import initial
from analyze import Geo
import label_report as lr
from ladder_replay import replay, edge_id

BOTS = {'21126':'one8', '21200':'one10', '21269':'one11'}
SCHEMA = 1

def census(path, meta, root):
    g=Geo(root.text(0)); bs,teams=initial(root.text(0));bs={i:tuple(b) for i,b in bs.items()}
    own=int(meta['teamAId']!=1119);side=lambda i:int(teams[i]!=own)
    queens={s:min(i for i in bs if side(i)==s) for s in (0,1)}
    occ={c:i for i,b in bs.items() for c in b};heads={b[0]:i for i,b in bs.items()}
    ps=set();pending=None;turns=[0,0];hist=defaultdict(lambda:deque(maxlen=5));born={};splits={}
    closed={};lastfree={};free={};ds=[];logs=Counter();all_deaths=Counter();rnd=-1;actor=None;ctx=None;dirs=[];used=0
    def visible(c,h):return g.visible(c,h)
    def man(a,b):
        dx=abs(a[0]-b[0]);dy=abs(a[1]-b[1]);return min(dx,g.w-dx)+min(dy,g.h-dy)
    def options(i):
        b=bs[i];h=b[0];out=[]
        for d,n in enumerate(g.moves[h]):
            if n is None or n in occ:continue
            eat=n in ps or n==pending
            nb=(n,)+b if eat else (n,)+b[:-1]
            exits=[z for z in g.adj[n] if z not in nb and (z not in occ or occ[z]==i)]
            out.append(dict(d=d,n=n,eat=eat,exits=exits,seen=visible(n,h) and all(visible(z,h) for z in exits),
                            portal=g.edges.get(edge_id(g.w,g.h,*h,d),(0,-1))[0]==2))
        return out
    def context(i,idx):
        b=bs[i];h=b[0]
        return dict(r=rnd,event=idx,id=i,head=h,L=len(b),body=b,options=options(i),
                    mates=[dict(id=j,L=len(bb),head=bb[0],distance=man(h,bb[0])) for j,bb in bs.items() if j!=i and side(j)==side(i) and man(h,bb[0])<=5],
                    enemies=[dict(id=j,L=len(bb),head=bb[0],distance=man(h,bb[0])) for j,bb in bs.items() if side(j)!=side(i) and man(h,bb[0])<=5],
                    dirs=[],kind=None,logs=[],moves=[])
    def refresh(changed,movers,event):
        affected=set(movers)
        for c in changed:
            for h in g.reverse[c]:
                if h in heads:affected.add(heads[h])
        for i in affected:
            if i not in bs:continue
            ns=g.adj[bs[i][0]]-occ.keys();was=free.get(i,set())
            if ns:
                closed.pop(i,None);lastfree[i]=dict(r=rnd,event=event['event'],head=bs[i][0],cells=sorted(ns))
            elif was or i not in free:
                blockers=[dict(cell=c,id=occ[c],side=side(occ[c]),part=bs[occ[c]].index(c)) for c in g.adj[bs[i][0]] if c in occ]
                closed[i]=dict(**event,by=actor,by_side=side(actor) if actor is not None else None,
                               victim=i,head=bs[i][0],last_cells=sorted(was),blockers=blockers,
                               actor_turn=ctx,previous_free=lastfree.get(i))
            free[i]=ns
    refresh(set(occ),list(bs),dict(r=-1,event=-1,kind='initial'))
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0)
        if k not in (0,1,3,4,6,9,10,11):continue
        p=ev.pointer(0)
        if k==0:rnd=p.i32(0);actor=None;ctx=None
        elif k==1:
            actor=p.i32(0);dirs=[];used=0;turns[side(actor)]+=1
            ctx=context(actor,idx);hist[actor].append(ctx)
        elif k==4:
            a=p.pointer(0);kind=a.u16(0) if a else None
            dirs=list(a.pointer(0)) if a and kind==0 and a.pointer(0) is not None else [];used=0
            if ctx:ctx['kind']=kind;ctx['dirs']=dirs
        elif k==6:
            val=p.text(0);logs[val.split()[0] if val.split() else 'empty']+=1
            if ctx:ctx['logs'].append(val)
        elif k==3:
            c=replay.point(p.pointer(0))
            if p.u32(0):ps.add(c)
            else:ps.remove(c);pending=c
        elif k==9:
            i=p.i32(0);old=bs[i];h=replay.point(p.pointer(0));tail=replay.point(p.pointer(1));b=old
            moved=h!=old[0];step=None
            if moved:
                step=dict(r=rnd,event=idx,src=old[0],dest=h,eat=pending==h,L=len(old),options=options(i),
                          d=dirs[used] if i==actor and used<len(dirs) else None)
                b=(h,)+b
            while len(b)>1 and b[-1]!=tail:b=b[:-1]
            assert b[-1]==tail
            for c in old:occ.pop(c,None)
            heads.pop(old[0],None);bs[i]=b;heads[h]=i
            for c in b:occ[c]=i
            if moved and i==actor:
                used+=1;ctx['moves'].append(step)
            event=dict(r=rnd,event=idx,kind='move' if moved else 'shrink',step=step)
            refresh(set(old)^set(b),[i],event)
            if pending==h:pending=None
        elif k==10:
            parent,child=p.i32(0),p.i32(4);old=bs[parent]
            for c in old:occ.pop(c,None)
            heads.pop(old[0],None)
            for z,i in enumerate((parent,child)):
                b=tuple(replay.point(c) for c in p.pointer(z));bs[i]=b;teams[i]=p.u16(8);heads[b[0]]=i
                for c in b:occ[c]=i
            born[child]=dict(r=rnd,event=idx,parent=parent,body=bs[child]);splits[parent]=dict(r=rnd,event=idx,child=child,context=ctx)
            refresh(set(old),[parent,child],dict(r=rnd,event=idx,kind='split',parent=parent,child=child))
            born[child]['boxed']=not bool(free[child])
        elif k==11:
            i=p.i32(0);reason=p.u16(4);s=side(i);all_deaths[str(reason)]+=1;b=bs[i]
            if reason in (0,1):
                t=hist[i][-1] if hist[i] else None;c=closed.get(i)
                startfree=bool(t and t['r']==rnd and t['options'])
                birth=born.get(i);sp=splits.get(i)
                cl='chosen_free_start' if startfree else 'forced'
                if birth and birth['boxed'] and i not in lastfree:cl='born_boxed'
                if i==queens[s] and sp and sp['r']>=rnd-1 and not startfree:cl='queen_after_split'
                if t and any('FEEDDIE' in z for z in t['logs']):cl='feeding'
                if t and any('QSTRICT' in z and 'die' in z for z in t['logs']):cl='queen_exit_sacrifice'
                ds.append(dict(gid=meta['id'],r=rnd,event=idx,id=i,side=s,L=len(b),queen=i==queens[s],reason=reason,
                               head=b[0],body=b,classification=cl,startfree=startfree,free_at_death=sorted(g.adj[b[0]]-occ.keys()),
                               closure=c,lastfree=lastfree.get(i),birth=birth,lastsplit=sp,history=list(hist[i]),
                               blocked_for=rnd-c['r'] if c else None))
            for c in b:occ.pop(c,None)
            heads.pop(b[0],None);del bs[i];free.pop(i,None)
            refresh(set(b),[],dict(r=rnd,event=idx,kind='death',dead=i))
    for s in (0,1):
        ls=[len(b) for i,b in bs.items() if side(i)==s];st=root.pointer(4).pointer(own if s==0 else 1-own)
        assert (len(ls),max(ls,default=0),sum(ls))==(st.i32(0),st.i32(4),st.i32(8))
    return dict(schema=SCHEMA,gid=meta['id'],version=BOTS[root.text(own+1)],bot=root.text(own+1),opp=meta['team'+'AB'[1-own]+'Name'],
                ranked=meta.get('ranked'),path=str(path.relative_to(ROOT)),map=meta['mapName'],turns=turns,deaths=ds,logs=dict(logs),all_deaths=dict(all_deaths))

def run_job(job):
    path,meta=job
    row=census(path,meta,replay.load(path).root())
    (OUT/f"game-{meta['id']}.json").write_text(json.dumps(row,separators=(',',':')))
    return dict(gid=row['gid'],version=row['version'],turns=row['turns'],n=len(row['deaths']))

def main():
    inv=lr.directory_inventory('walls','data/online/smoke/one8*-old,data/online/smoke/one10*-old,data/online/smoke/one11*-old,data/online/live-one1/b*')
    stamp=datetime.now().astimezone().isoformat();rows=[];excluded=[]
    old=json.loads((OUT/'coverage.json').read_text()) if (OUT/'coverage.json').exists() else {}
    prior=json.loads((OUT.parent/'audit-move/coverage.json').read_text())
    prev={z['gid']:z for z in prior.get('excluded',[])+old.get('excluded',[]) if z['bot'] not in BOTS}
    pending_jobs=[]
    for n,(path,meta) in enumerate(inv['jobs']):
        gid=meta['id'];cache=OUT/f'game-{gid}.json'
        if cache.exists():
            row=json.loads(cache.read_text())
            if row['schema']==SCHEMA:rows.append(row);continue
        if gid in prev:excluded.append(prev[gid]);continue
        bot=bot_identity(path,int(meta['teamAId']!=1119))
        if bot not in BOTS:excluded.append(dict(gid=gid,bot=bot));continue
        pending_jobs.append((path,meta))
    print('PENDING',len(pending_jobs),'CACHED',len(rows),flush=True)
    with multiprocessing.get_context('fork').Pool(3) as pool:
        for done in pool.imap_unordered(run_job,pending_jobs):
            rows.append(done);print('SCANNED',done,flush=True)
    (OUT/'coverage.json').write_text(json.dumps(dict(at=stamp,finished=datetime.now().astimezone().isoformat(),versions=dict(Counter(g['version'] for g in rows)),excluded=excluded,duplicates=inv['duplicate_ids'],notes=inv['notes'],games=[g['gid'] for g in rows]),indent=2))
    print('DONE',dict(Counter(g['version'] for g in rows)),flush=True)

if __name__=='__main__':main()
