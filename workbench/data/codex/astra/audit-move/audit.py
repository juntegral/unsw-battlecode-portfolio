"""Offline replay audit; all outputs are confined to this directory."""
import sys
sys.dont_write_bytecode = True
import json, hashlib, csv, gzip
from pathlib import Path
from collections import Counter, defaultdict, deque
from datetime import datetime

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'data/analysis/ladder/dossier/online'),
               str(ROOT/'data/analysis/ladder/dossier/work'), str(OUT.parent/'deathcell'),
               str(OUT.parent/'evade')]
import label_report as lr
import o1_scan
from scan import initial
from analyze import Geo
from ladder_replay import replay, edge_id

BOTS = {'20980':'one5', '21086':'one7', '21126':'one8', '21165':'one9', '21200':'one10'}
SCHEMA = 1

def bot_identity(path, own):
    with path.open('rb') as f: zipped=f.read(2)==b'\x1f\x8b'
    opener=gzip.open if zipped else open
    with opener(path,'rb') as f: prefix=f.read(131072)
    for trim in range(17):
        try:
            root=replay.Message(replay.unpack_packed(prefix[:-trim] if trim else prefix)).root()
            ptr=root.pointer(own+1)
            if ptr is None:return ''
            raw=ptr.raw_bytes()
            if len(raw)==ptr.count and raw[-1:]==b'\x00':return root.text(own+1)
        except (IndexError,ValueError,AttributeError):pass
    return replay.load(path).root().text(own+1)

def census(path, meta, root):
    g = Geo(root.text(0)); bodies, teams = initial(root.text(0))
    bodies = {i:tuple(b) for i,b in bodies.items()}
    own = int(meta['teamAId'] != 1119)
    queen = min(i for i in bodies if teams[i] == own)
    bot = root.text(own+1); version = BOTS[bot]
    start_units = sum(teams[i] == own for i in bodies)
    known = defaultdict(set); windows = {}; window_edges = {}
    pairs = defaultdict(set); kinds = {}; components = {}; comp_edges = {}
    for e,(kind,pid) in g.edges.items():
        if kind == 2: pairs[pid].add(e)
    for c in g.moves:
        kinds[c] = [g.edges.get(edge_id(g.w,g.h,*c,d),(0,-1))[0] for d in range(4)]
    for c in g.moves:
        if c in components: continue
        seen={c}; q=deque([c])
        while q:
            a=q.popleft()
            for d,n in enumerate(g.moves[a]):
                if kinds[a][d] == 0 and n not in seen: seen.add(n); q.append(n)
        frozen=frozenset(seen)
        for a in seen: components[a]=frozen
        if len(seen)<48:
            comp_edges[frozen] = {edge_id(g.w,g.h,*a,d) for a in seen for d in range(4)}
    C=Counter(); moments=defaultdict(list); births={}; splits=[]; deaths=[]; snapshots={}; last={}
    pearls=set(); occ={c:i for i,b in bodies.items() for c in b}
    r=-1; actor=None; turn=None; dirs=[]; used=0
    def sample(key, **kw):
        if len(moments[key])<12: moments[key].append(dict(r=r,id=actor,**kw))
    def man(a,b):
        dx=abs(a[0]-b[0]);dy=abs(a[1]-b[1])
        return min(dx,g.w-dx)+min(dy,g.h-dy)
    def window(h):
        if h not in windows:
            windows[h] = {( (h[0]+x)%g.w,(h[1]+y)%g.h) for x in range(-3,4) for y in range(-3,4)}
            window_edges[h] = {edge_id(g.w,g.h,*c,d) for c in windows[h] for d in range(4)}
        return windows[h]
    def one_step(i,d):
        b=bodies[i]; n=g.moves[b[0]][d]
        if n is None or n in occ: return None
        return (n,)+b if n in pearls else (n,)+b[:-1]
    def exits(b,other): return {n for n in g.moves[b[0]] if n is not None and n not in b and n not in other}
    def forced(mate, moving, after, consumed=frozenset()):
        mb=bodies[mate]
        ate=set(consumed)
        for depth in range(5):
            ns={n for n in g.adj[mb[0]] if n not in mb and n not in after and occ.get(n,mate) in (mate,moving)}
            if not ns:return 2 if depth==0 else 1
            if len(ns)>1 or depth==4:return 0
            n=next(iter(ns)); eat=n in pearls and n not in ate
            mb=(n,)+mb if eat else (n,)+mb[:-1]
            if eat:ate.add(n)
        return 0
    def snapshot():return dict(units=sum(teams[i]==own for i in bodies),queen=len(bodies.get(queen,())))
    def finish():
        nonlocal turn
        if turn is None:return
        t=turn;i=t['id'];C['turns']+=1;C['pearls']+=t['ate']
        C['queen_turns']+=i==queen;C['queen_L2_turns']+=i==queen and t['L']==2
        C['portal_turns']+=t['portal'];C['portal_noeat']+=t['portal'] and t['ate']==0
        if t['portal'] and t['ate']==0:sample('portal_noeat',head=t['h'],L=t['L'])
        if i in bodies and bodies[i][0]==t['h'] and not t['split']:C['stationary_alive']+=1
        if t['kind']==0 and not t['dirs']:C['empty_move']+=1
        for key in ('mate_near','mate_risk_choice','pocket_choice','target_geometry','split_portal_window','split_portal_safe','qs_L4','qs_release2','qs_release6'):
            C[key]+=int(t.get(key,False))
            if t.get(key):
                C[key+'_pearls']+=t['ate'];C[key+'_splits']+=t['split']
                sample(key,head=t['h'],L=t['L'],ate=t['ate'],split=t['split'],units=t['units'])
        if t['split_portal_window'] and t['split']:C['split_portal_window_realized']+=1
        if t['qs_release6'] and t['split']:C['qs_release6_realized']+=1
        if t['qs_release2'] and t['split']:C['qs_release2_realized']+=1
        if i in bodies and t['near'] and not t['split']:
            risks=[forced(m,i,bodies[i],set(t['eaten'])) for m in t['near'] if m in bodies]
            if risks and max(risks):C['mate_chosen_risk']+=1
        last[i] = dict(r=t['r'],event=t['event'],L=t['L'],head=t['h'],near=t['near'],ate=t['ate'])
        turn=None
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0)
        if k not in (0,1,3,4,6,9,10,11):continue
        p=ev.pointer(0)
        if k==0:
            finish()
            if r in (50,100):snapshots[str(r)]=snapshot()
            r=p.i32(0);actor=None
        elif k==1:
            finish();actor=p.i32(0);dirs=[];used=0
            if teams[actor]!=own:continue
            b=bodies[actor];h=b[0];L=len(b);view=window(h);known[actor]|=window_edges[h]
            friends={occ[c] for c in view if c in occ and teams[occ[c]]==own}
            near=[i for i in friends if i!=actor and man(h,bodies[i][0])<=2]
            t=dict(id=actor,r=r,event=idx,h=h,L=L,ate=0,eaten=[],split=False,kind=None,dirs=[],near=near,
                   units=sum(teams[i]==own for i in bodies),portal=2 in kinds[h],mate_near=bool(near),
                   mate_risk_choice=False,pocket_choice=False,target_geometry=False,
                   split_portal_window=False,split_portal_safe=False,qs_L4=actor==queen and L==4)
            t['qs_release2']=t['qs_L4'] and t['units']<2
            t['qs_release6']=t['qs_L4'] and t['units']<6
            options=[(d,one_step(actor,d)) for d in range(4)];options=[(d,nb) for d,nb in options if nb]
            if actor==queen or L<=3:
                risk=[not any(n not in nb and occ.get(n,actor)==actor for n in g.adj[nb[0]]) for d,nb in options]
                t['pocket_choice']=bool(risk) and any(risk) and not all(risk)
            if near and options:
                risk=[max(forced(m,actor,nb,{nb[0]} if nb[0] in pearls else set()) for m in near) for d,nb in options]
                t['mate_risk_choice']=max(risk)>min(risk)
            if t['portal']:
                for c in pearls&view:
                    comp=components[c]
                    if len(comp)>=48 or h in comp or not comp_edges[comp]<=known[actor]:continue
                    portals_known=all(pairs[g.edges[e][1]]<=known[actor] for e in comp_edges[comp] if g.edges.get(e,(0,-1))[0]==2)
                    if portals_known and L+1>len(comp)//2:
                        t['target_geometry']=True;break
            if actor!=queen and L==4 and r<=100 and 2 in kinds[b[-1]]:
                t['split_portal_window']=True
                if set(b)<=view:
                    for d,n in enumerate(g.moves[b[-1]]):
                        if kinds[b[-1]][d]!=0 or n in occ or n not in view:continue
                        enemies=[j for j,bb in bodies.items() if teams[j]!=own and bb[0] in view]
                        danger=False
                        for enemy in enemies:
                            seen={bodies[enemy][0]};front=set(seen)
                            for depth in range((len(bodies[enemy])+3)//4+1):
                                front={z for c in front for z in g.adj[c] if z not in occ}-seen;seen|=front
                                if n in seen:danger=True;break
                            if danger:break
                        if danger:continue
                        seen={n};q=deque([n])
                        while q and len(seen)<5:
                            c=q.popleft()
                            for z in g.adj[c]:
                                if z in view and z not in occ and z not in seen:seen.add(z);q.append(z)
                        if len(seen)>=5:t['split_portal_safe']=True;break
            turn=t
        elif k==4:
            a=p.pointer(0);kind=a.u16(0) if a else None
            dirs=list(a.pointer(0)) if a and kind==0 and a.pointer(0) is not None else [];used=0
            if turn is not None:turn.update(kind=kind,dirs=dirs)
        elif k==6:
            C['log_events']+=1
        elif k==3:
            c=replay.point(p.pointer(0))
            if p.u32(0):pearls.add(c)
            else:
                pearls.remove(c)
                if turn is not None:turn['ate']+=1;turn['eaten'].append(c)
        elif k==9:
            i=p.i32(0);hd=replay.point(p.pointer(0));tl=replay.point(p.pointer(1));b=bodies[i]
            for c in b:occ.pop(c,None)
            moved=b[0]!=hd
            if moved:b=(hd,)+b
            while len(b)>1 and b[-1]!=tl:b=b[:-1]
            assert b[-1]==tl
            bodies[i]=b
            for c in b:occ[c]=i
            if i==actor and moved:used+=1
        elif k==10:
            parent,child=p.i32(0),p.i32(4);old=bodies[parent]
            for c in old:occ.pop(c,None)
            for z,i in enumerate((parent,child)):
                bodies[i]=tuple(replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
                for c in bodies[i]:occ[c]=i
            births[child]=r
            if teams[parent]==own:
                if turn is not None:turn['split']=True
                rec=dict(r=r,parent=parent,child=child,L=len(old),queen=parent==queen,
                         portal=2 in kinds[old[-1]],head=old[0],tail=old[-1],child_died3=False,censored=False)
                splits.append(rec);C['splits']+=1
                if rec['portal']:C['portal_splits']+=1;sample('portal_split',child=child,tail=old[-1],L=len(old),queen=rec['queen'])
        elif k==11:
            i=p.i32(0);reason=p.u16(4);b=bodies[i];h=b[0]
            if teams[i]==own:
                ns=g.adj[h];free=ns-set(occ)
                mates={c for c,z in occ.items() if z!=i and teams[z]==own}
                unblocked=ns-(set(occ)-mates)
                pinned=not free and bool(unblocked) and reason in (0,1,2)
                neck_only=bool(ns) and len(b)>=2 and ns<={b[1]}
                self_shut=bool(ns) and ns<=set(b)
                C['deaths']+=1;C['pinned_deaths']+=pinned;C['neck_only_deaths']+=neck_only
                C['self_shut_deaths']+=self_shut;C['queen_L2_deaths']+=i==queen and len(b)==2
                rec=dict(r=r,id=i,reason=reason,L=len(b),head=h,body=b,queen=i==queen,
                         pinned=pinned,neck_only=neck_only,self_shut=self_shut,last=last.get(i),
                         mates=sorted({occ[c] for c in ns if c in mates}),actor=actor)
                deaths.append(rec)
                if pinned:sample('pinned_death',victim=i,head=h,L=len(b),mates=rec['mates'])
                if neck_only:sample('neck_death',victim=i,head=h,L=len(b),queen=i==queen)
            for c in b:occ.pop(c,None)
            del bodies[i]
    finish()
    if r in (50,100):snapshots[str(r)]=snapshot()
    if not any(teams[i]==own for i in bodies):
        for checkpoint in ('50','100'):
            if int(checkpoint)>r:snapshots[checkpoint]=dict(units=0,queen=0)
    ds={d['id']:d for d in deaths}
    for sp in splits:
        d=ds.get(sp['child']);sp['death_round']=d['r'] if d else None
        sp['child_died3']=d is not None and d['r']-sp['r']<=3
        sp['censored']=d is None and r<sp['r']+3
        if sp['portal']:
            C['portal_child_died3']+=sp['child_died3'];C['portal_child_censored']+=sp['censored']
        if sp['portal'] and sp['r']<=100 and sp['L']==4 and not sp['queen']:
            C['early_portal_splits']+=1;C['early_portal_child_died3']+=sp['child_died3'];C['early_portal_censored']+=sp['censored']
    original=o1_scan.replay.load
    o1_scan.replay.load=lambda _:type('Loaded',(),{'root':lambda _:root})()
    try:base=o1_scan.scan(path.parent.name,path,meta)
    finally:o1_scan.replay.load=original
    assert C['pearls']==sum(e[1]==0 for e in base['eats'])
    assert C['deaths']==sum(d[1]==0 for d in base['deaths'])
    assert C['splits']==sum(s[1]==0 for s in base['splits'])
    start_b,start_t=initial(root.text(0))
    for side in (0,1):
        ls=[len(b) for i,b in bodies.items() if int(teams[i]!=own)==side]
        st=root.pointer(4).pointer(own if side==0 else 1-own)
        assert (len(ls),max(ls,default=0),sum(ls))==(st.i32(0),st.i32(4),st.i32(8))
        assert sum(len(b) for i,b in start_b.items() if int(start_t[i]!=own)==side)+sum(e[1]==side for e in base['eats'])-sum(d[2] for d in base['deaths'] if d[1]==side)-sum(p[3] for p in base['paids'] if p[1]==side)==sum(ls)
    return dict(schema=SCHEMA,gid=meta['id'],path=str(path.relative_to(ROOT)),version=version,bot=bot,
                map=meta['mapName'],opp=meta['team'+'AB'[1-own]+'Name'],oppid=meta['team'+'AB'[1-own]+'Id'],side=own,
                start_units=start_units,last=r,counts=dict(C),snapshots=snapshots,splits=splits,deaths=deaths,
                first_split=splits[0]['r'] if splits else None,
                first_queen_split=next((s['r'] for s in splits if s['queen']),None),moments=dict(moments),verified=True)

def main():
    patterns=','.join([f'data/online/smoke/one{v}-{x}1-old' for v in (5,7,8,9,10) for x in 'wck']+['data/online/live-one1/b*'])
    inv=lr.directory_inventory('audit-move',patterns)
    stamp=datetime.now().astimezone().isoformat()
    (OUT/'inventory.json').write_text(json.dumps(dict(at=stamp,patterns=patterns,notes=inv['notes'],duplicates=inv['duplicate_ids'],jobs=[dict(path=str(p.relative_to(ROOT)),gid=m['id']) for p,m in inv['jobs']]),ensure_ascii=False,indent=2))
    rows=[];excluded=[];errors=[]
    prior_excluded={g['gid']:g for g in json.loads((OUT/'coverage.json').read_text()).get('excluded',[])} if (OUT/'coverage.json').exists() else {}
    for n,(path,meta) in enumerate(inv['jobs']):
        cache=OUT/f"game-{meta['id']}.json"
        if cache.exists():
            row=json.loads(cache.read_text())
            if row.get('schema')==SCHEMA:rows.append(row);continue
        if meta['id'] in prior_excluded:
            excluded.append(prior_excluded[meta['id']]);continue
        own=int(meta['teamAId']!=1119);bot=bot_identity(path,own)
        if bot not in BOTS:excluded.append(dict(gid=meta['id'],bot=bot));continue
        root=replay.load(path).root()
        assert bot==root.text(own+1)
        try:row=census(path,meta,root)
        except Exception as e:
            errors.append(dict(gid=meta['id'],error=repr(e)));print('ERROR',meta['id'],repr(e),flush=True);raise
        cache.write_text(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n');rows.append(row)
        print(n+1,'/',len(inv['jobs']),row['version'],row['gid'],row['counts']['turns'],flush=True)
    (OUT/'games.jsonl').write_text(''.join(json.dumps(g,ensure_ascii=False,separators=(',',':'))+'\n' for g in rows))
    (OUT/'coverage.json').write_text(json.dumps(dict(at=stamp,finished=datetime.now().astimezone().isoformat(),versions=dict(Counter(g['version'] for g in rows)),excluded=excluded,errors=errors),ensure_ascii=False,indent=2))
    keys=sorted(set().union(*(g['counts'] for g in rows)))
    with (OUT/'per-game.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=['gid','version','map','opp','side','start_units','first_split','first_queen_split','units50','units100']+keys);w.writeheader()
        for g in rows:w.writerow({**{k:g[k] for k in ('gid','version','map','opp','side','start_units','first_split','first_queen_split')},'units50':g['snapshots'].get('50',{}).get('units'),'units100':g['snapshots'].get('100',{}).get('units'),**{k:g['counts'].get(k,0) for k in keys}})
    print('DONE',dict(Counter(g['version'] for g in rows)),flush=True)

if __name__=='__main__':main()
