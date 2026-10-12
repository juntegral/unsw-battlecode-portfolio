"""Offline evade audit. Only this directory is writable by this script."""
import sys
sys.dont_write_bytecode = True
import csv
import json
import hashlib
from pathlib import Path
from collections import Counter, defaultdict, deque
from datetime import datetime

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'data/analysis/ladder/dossier/online')]
import ladder_replay as lr
import label_report

LABELS = ('one5-w1', 'one5-c1', 'one3-w1')
SCHEMA = 2
STEP = ((0,-1),(1,0),(0,1),(-1,0))

class Geo:
    def __init__(self, text):
        self.w,self.h=map(int,text.splitlines()[0].split()[1:3])
        raw=[tuple(map(int,q[1:4])) for line in text.splitlines() if (q:=line.split()) and q[0]=='EDGE']
        self.edges=lr.canonical_edges(self.w,self.h,raw)
        portals=defaultdict(list)
        for e,(k,p) in self.edges.items():
            if k==2: portals[p].append(e)
        self.moves={}
        for y in range(self.h):
            for x in range(self.w):
                ns=[]
                for d,(dx,dy) in enumerate(STEP):
                    e=lr.edge_id(self.w,self.h,x,y,d); k,p=self.edges.get(e,(0,-1))
                    if k==1: ns.append(None)
                    elif k==2:
                        other=next(z for z in portals[p] if z!=e)
                        row,px=divmod(other,self.w+1)
                        ns.append(((px-(d==3))%self.w,(row//2-(d==0))%self.h))
                    else: ns.append(((x+dx)%self.w,(y+dy)%self.h))
                self.moves[x,y]=ns
        self.adj={c:set(n for n in ns if n is not None) for c,ns in self.moves.items()}
        self.reverse=defaultdict(set)
        for c,ns in self.adj.items():
            for n in ns: self.reverse[n].add(c)
        self.ds={}

    def visible(self,c,hd):
        dx,dy=abs(c[0]-hd[0]),abs(c[1]-hd[1])
        return min(dx,self.w-dx)<=3 and min(dy,self.h-dy)<=3

    def distances_to(self,target):
        if target not in self.ds:
            ds={target:0}; q=deque([target])
            while q:
                c=q.popleft()
                for n in self.reverse[c]:
                    if n not in ds: ds[n]=ds[c]+1; q.append(n)
            self.ds[target]=ds
        return self.ds[target]

def good_room(g,body,others,window=None):
    """Room plus a reachable cycle; immediate reversals are not cycles."""
    hd=body[0]; blocked=others|set(body[1:])
    seen={hd}; q=deque([hd])
    while q:
        c=q.popleft()
        for n in g.adj[c]:
            if n in blocked or n in seen or (window is not None and n not in window): continue
            seen.add(n); q.append(n)
    if len(seen)<len(body)+2: return False
    # Mutual edges give a conservative cycle certificate, including portal pairs.
    adj={c:{n for n in g.adj[c] if n in seen and c in g.adj[n]} for c in seen}
    deg={c:len(ns) for c,ns in adj.items()}; leaves=deque(c for c,n in deg.items() if n<2)
    while leaves:
        c=leaves.popleft()
        if deg[c]<0: continue
        deg[c]=-1
        for n in adj[c]:
            if deg[n]>=0:
                deg[n]-=1
                if deg[n]<2: leaves.append(n)
    return any(n>=2 for n in deg.values())

def free_options(g,bodies,v,pearls):
    body=bodies[v]; other={c for i,b in bodies.items() if i!=v for c in b}
    out=[]; free=(len(body)+3)//4
    def visit(b,path,ps,ate):
        if path:
            if good_room(g,b,other):
                window={c for c in g.adj if g.visible(c,body[0])}
                known=all(c in window for c in b) and good_room(g,b,other,window)
                out.append(dict(body=b,path=path,ate=ate,remaining_pearls=list(ps),known_room=known,
                                path_seen=all(g.visible(c,body[0]) for c in path_cells(g,body[0],path))))
        if len(path)==free: return
        for d,n in enumerate(g.moves[b[0]]):
            if n is None or n in b or n in other: continue
            eaten=n in ps; nb=(n,)+b if eaten else (n,)+b[:-1]
            visit(nb,path+[d],ps-{n},ate+eaten)
    visit(body,[],set(pearls),0)
    return out

def path_cells(g,head,path):
    cells=[]
    for d in path:
        head=g.moves[head][d]; cells.append(head)
    return cells

def hits(g,bodies,a,v,target_body,pearls,include_pearls=True,extra_budget=False):
    """Exact dynamic attacking body; frozen third parties; bounded length budget."""
    body=bodies[a]; free=(len(body)+3)//4; limit=free+len(body)-2
    if extra_budget: limit+=len(pearls)
    goal=target_body[0]
    blocked={c for i,b in bodies.items() if i not in (a,v) for c in b}|set(target_body[1:])
    ds=g.distances_to(goal)
    if ds.get(body[0],99999)>limit: return False
    seen=set(); work=0
    def go(b,used,ps):
        nonlocal work
        if used>=limit or (used>=free and len(b)<3): return False
        left=limit-used
        if ds.get(b[0],99999)>left: return False
        key=(b,used,frozenset(ps) if include_pearls else None)
        if key in seen: return False
        seen.add(key); work+=1
        if work>100000: raise RuntimeError('attack search cap')
        for n in sorted(g.adj[b[0]],key=lambda c:ds.get(c,99999)):
            if n in b or n in blocked: continue
            if n==goal: return True
            eaten=include_pearls and n in ps
            nb=(n,)+b if eaten else (n,)+b[:-1]
            if used>=free: nb=nb[:-1]
            if go(nb,used+1,ps-{n} if eaten else ps): return True
        return False
    return go(body,0,set(pearls))

def scan(path,meta,label):
    base=lr.scan(path,meta,label,set())
    root=lr.replay.load(path).root(); g=Geo(root.text(0)); events=list(root.pointer(3))
    selected=[c for c in base['collisions'] if c['cross_team'] and c['round']<=200]
    deaths={d['death']:d for d in base['deaths']}
    targets={}
    last={}
    for idx,ev in enumerate(events):
        k=ev.u16(0); p=ev.pointer(0)
        if k==1: last[p.i32(0)]=idx
        elif k==11:
            for c in selected:
                if c['deaths'][0]!=f'{meta["id"]}:{idx}': continue
                v=p.i32(0); d=deaths[c['deaths'][0]]
                if v==base['queens'][d['side']]: continue
                targets[c['collision']]=dict(c=c,v=v,a=d['actor'],last=last.get(v))
    needed={t['last'] for t in targets.values() if t['last'] is not None}|{t['c']['turn_start'] for t in targets.values()}
    bodies={};teams={}
    own=0 if meta['teamAId']==1119 else 1
    for line in root.text(0).splitlines():
        q=line.split()
        if q and q[0]=='DRAGON':
            i=len(bodies); bodies[i]=tuple((int(q[3+2*z]),int(q[4+2*z])) for z in range(int(q[2])))
            teams[i]='us' if int(q[1])==own else 'them'
    snapshots={};history=defaultdict(list);turn=None;r=-1;actor=None;present=set()
    def finish():
        nonlocal turn
        if turn is None: return
        i=turn['id']; turn['endbody']=bodies.get(i,()); history[i].append(turn)
        if turn['event'] in needed:
            snapshots[turn['event']]['turn']=turn
            snapshots[turn['event']]['previous']=history[i][-2] if len(history[i])>=2 else None
        turn=None
    for idx,ev in enumerate(events):
        k=ev.u16(0);p=ev.pointer(0)
        if k==0: finish(); r=p.i32(0);actor=None
        elif k==1:
            finish();actor=p.i32(0)
            turn=dict(id=actor,event=idx,round=r,length=len(bodies[actor]),head=bodies[actor][0],kind=None,dirs=[],ate=0,eats=[],used=0)
            if idx in needed:
                snapshots[idx]=dict(bodies=dict(bodies),pearls=set(present),round=r)
        elif k==4:
            act=p.pointer(0);turn['kind']=act.u16(0) if act else None
            turn['dirs']=list(act.pointer(0)) if act and act.u16(0)==0 and act.pointer(0) is not None else []
        elif k==3:
            xy=lr.replay.point(p.pointer(0))
            if p.u32(0): present.add(xy)
            else:
                assert xy in present
                present.remove(xy);turn['ate']+=1;turn['eats'].append(dict(round=r,event=idx,xy=xy))
        elif k==9:
            i=p.i32(0);hd=lr.replay.point(p.pointer(0));tl=lr.replay.point(p.pointer(1));b=deque(bodies[i])
            if hd!=b[0]:
                b.appendleft(hd)
                if i==actor: turn['used']+=1
            while len(b)>1 and b[-1]!=tl: b.pop()
            assert b[-1]==tl
            bodies[i]=tuple(b)
        elif k==10:
            for z,i in enumerate((p.i32(0),p.i32(4))):
                bodies[i]=tuple(lr.replay.point(c) for c in p.pointer(z));teams[i]=teams[actor]
        elif k==11: bodies.pop(p.i32(0))
    finish()
    rows=[]
    for cid,t in targets.items():
        c=t['c'];v=t['v'];a=t['a'];s=teams[v];enemy=teams[a]
        vd=deaths[c['deaths'][0]];ad=deaths[c['deaths'][1]]
        drops=[p for p in base['pearls'] if p['death'] in c['deaths']]
        row=dict(label=label,gid=meta['id'],map=meta['mapName'],collision=cid,round=c['round'],side=s,victim=v,attacker=a,
                 victim_impact_length=vd['length'],attacker_impact_length=ad['length'],last_event=t['last'],
                 drops=drops,recovered5={z:sum(p['eater']==z and p['wait']<=5 for p in drops) for z in ('us','them')},
                 complete5=c['round']+5<=base['last_round'],attacking_turn=snapshots[c['turn_start']]['turn'])
        if t['last'] is None:
            row.update(status='not seen',reason='no prior turn'); rows.append(row);continue
        snap=snapshots[t['last']];bs=snap['bodies'];turn=snap['turn']; hd=bs[v][0]
        seen=a in bs and g.visible(bs[a][0],hd)
        view={z:sum(teams[i]==z and g.visible(b[0],hd) for i,b in bs.items()) for z in ('us','them')}
        prev=snap['previous'];L=len(bs[v]);A=len(bs[a]) if a in bs else None
        parts=sum(g.visible(x,hd) for x in bs[a]) if a in bs else 0
        row.update(last_round=turn['round'],turn=turn,previous=prev,victim_length=L,attacker_length=A,
                   attacker_head=bs[a][0] if a in bs else None,attacker_seen=seen,attacker_parts=parts,view=view,
                   distance=g.distances_to(hd).get(bs[a][0],99999) if a in bs else None,
                   free=(A+3)//4 if A else None,paid_budget=(A+3)//4+A-2 if A else None,
                   pearls_two_turns=turn['ate']+(prev['ate'] if prev else 0),
                   local_outnumbered=view[s]<view[enemy],attacker_equal_longer=A is not None and A>=L,
                   start_bodies=[[i,teams[i],list(b)] for i,b in bs.items()],start_pearls=list(snap['pearls']))
        if not seen:
            row.update(status='not seen',reason='head outside view or attacker not born');rows.append(row);continue
        options=free_options(g,bs,v,snap['pearls'])
        safe=[];safe_all=[];known=[];start_reachable=hits(g,bs,a,v,bs[v],snap['pearls'])
        visible_enemies=[i for i,b in bs.items() if teams[i]!=s and g.visible(b[0],hd)]
        eligible=[i for i in visible_enemies if len(bs[i])>=L]
        for op in options:
            op_pearls=set(tuple(c) for c in op['remaining_pearls'])
            if hits(g,bs,a,v,op['body'],op_pearls): continue
            safe.append(op)
            if op['known_room'] and op['path_seen']: known.append(op)
            if all(not hits(g,bs,i,v,op['body'],op_pearls) for i in eligible): safe_all.append(op)
        endbody=turn['endbody']
        row.update(status='avoidable' if safe else 'not avoidable',reason='free endpoint with room and cycle' if safe else 'no certified free endpoint',
                   options=len(options),safe=safe,safe_all=safe_all,known_safe=known,start_reachable=start_reachable,
                   chosen_reachable=hits(g,bs,a,v,endbody,snap['pearls']) if endbody else None,
                   chosen_distance=g.distances_to(endbody[0]).get(bs[a][0],99999) if endbody else None,
                   immediate_pearl_cost=max(0,turn['ate']-max((o['ate'] for o in safe_all),default=0)),
                   threat_blind_kind='parts>=5 omitted' if L<=4 and parts>=5 else 'one-step only' if L<=4 else 'full field',
                   trade_geometry=view[s]-view[enemy]>=1,
                   mate_distance=min((g.distances_to(vd['body'][0]).get(b[0],99999) for i,b in bs.items() if i!=v and teams[i]==s and g.visible(b[0],hd)),default=99999),
                   enemy_meeting_distance=g.distances_to(vd['body'][0]).get(bs[a][0],99999),
                   candidate_mate_nearer=any(min((g.distances_to(o['body'][0]).get(b[0],99999) for i,b in bs.items() if i!=v and teams[i]==s and g.visible(b[0],hd)),default=99999)<g.distances_to(o['body'][0]).get(bs[a][0],99999) for o in safe_all))
        first=g.moves[hd][turn['dirs'][0]] if turn['kind']==0 and turn['dirs'] else None
        row['first_step']=first
        row['first_attacker_adjacent']=first in g.adj[bs[a][0]] if first else None
        row['card_geometry']=L<=4 and row['local_outnumbered'] and parts>=L and bool(safe_all) and row['chosen_reachable'] and row['mate_distance']>=row['enemy_meeting_distance']
        rows.append(row)
    assert len(rows)==len(targets)
    return dict(schema=SCHEMA,label=label,gid=meta['id'],path=str(path.relative_to(ROOT)),cells=g.w*g.h,rows=rows,
                selected_nonqueen=len(targets),anomalies=base['anomalies'],last_round=base['last_round'],bots=base['bots'])

def main():
    inventory=[];games=[]
    for label in LABELS:
        inv=label_report.inventory(label,'old')
        inventory.append(dict(label=label,planned=inv['planned'],available=len(inv['jobs']),notes=inv['notes'],ids=[j['id'] for _,j in inv['jobs']]))
        for path,meta in inv['jobs']:
            cache=OUT/f'g{meta["id"]}.json'
            game=json.loads(cache.read_text()) if cache.exists() else None
            if game is None or game.get('schema')!=SCHEMA:
                game=scan(path,meta,label);cache.write_text(json.dumps(game,ensure_ascii=False,separators=(',',':')))
            games.append(game)
            print(label,meta['id'],len(game['rows']),flush=True)
    (OUT/'inventory.json').write_text(json.dumps(dict(time=datetime.now().astimezone().isoformat(),sets=inventory,source_sha256=hashlib.sha256((ROOT/'data/online/smoke/one5-bot/main.cpp').read_bytes()).hexdigest()),ensure_ascii=False,indent=2))
    rows=[r for game in games for r in game['rows']]
    (OUT/'collisions.json').write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':')))
    fields=['label','gid','map','round','side','victim','attacker','last_round','status','reason','victim_length','attacker_length','attacker_parts','distance','free','paid_budget','local_outnumbered','attacker_equal_longer','start_reachable','chosen_reachable','chosen_distance','options','pearls_two_turns','immediate_pearl_cost','threat_blind_kind','trade_geometry','mate_distance','enemy_meeting_distance','card_geometry']
    with (OUT/'collisions.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
    print('done',len(games),len(rows),flush=True)

if __name__=='__main__': main()
