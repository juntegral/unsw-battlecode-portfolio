#!/usr/bin/env python3
"""Shared true-state reconstruction, adapted from drop-analysis/count.py's scan."""
import sys
sys.dont_write_bytecode = True
import importlib.util
from pathlib import Path
from collections import Counter, defaultdict, deque
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('ladder_fountain',ROOT/'data/online/smoke/fountain-analysis-2/count.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
replay=base.replay
OTHER=('unpaid sprint','illegal split','no action','timeout')

def edge_id(W,H,x,y,d):
    """Canonical edge id of tile (x,y) in direction d (0 N, 1 E, 2 S, 3 W). The east edge of the last column is the west edge of column 0 and the south edge of the last row is the north edge of row 0; server maps list each shared edge once."""
    return ((2*y)*(W+1)+x if d==0 else (2*y+1)*(W+1)+(x+1)%W if d==1 else (2*((y+1)%H))*(W+1)+x if d==2 else (2*y+1)*(W+1)+x)

def canonical_edges(W,H,rows):
    """{canonical id: (kind, portal id)} from (id, kind, portal id) rows; a border duplicate, if a file lists one, folds onto its wrapped twin and the stronger kind wins."""
    edges={}
    for e,k,p in rows:
        row,x=divmod(e,W+1)
        if row%2==0 and x==W:continue
        e=(2*((row//2)%H))*(W+1)+x if row%2==0 else row*(W+1)+x%W
        if e not in edges or k>edges[e][0]:edges[e]=(k,p)
    return edges

def scan(path, j, folder, fountains):
    root = replay.load(path).root(); text=root.text(0)
    W,H=map(int,text.splitlines()[0].split()[1:3])
    bodies={};teams={};raw_edges=[]
    for line in text.splitlines():
        q=line.split()
        if q and q[0]=='DRAGON':
            i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])))
            teams[i]='AB'[int(q[1])]
        elif q and q[0]=='EDGE':raw_edges.append(tuple(map(int,q[1:4])))
    edges=canonical_edges(W,H,raw_edges);portals=defaultdict(list)
    for e,(k,p) in edges.items():
        if k==2:portals[p].append(e)
    ours='A' if j['teamAId']==1119 else 'B'
    assert j['team'+ours+'Id']==1119
    queens={s:min(i for i in bodies if teams[i]==t) for s,t in [('us',ours),('them','B' if ours=='A' else 'A')]}
    q_eats=Counter();q_splits=Counter();snapshots={};eaten_rounds=[];natural=[];removed={};intervals=defaultdict(list)
    def side(i): return 'us' if teams[i]==ours else 'them'
    def destination(h,d):
        x,y=h
        e=edge_id(W,H,x,y,d)
        kind,pid=edges.get(e,(0,-1))
        if kind==2:
            assert len(portals[pid])==2 and e in portals[pid]
            partner=next(z for z in portals[pid] if z!=e)
            row,x=divmod(partner,W+1); y=row//2
            return ((x-(d==3))%W,(y-(d==0))%H)
        dx,dy=base.STEP[d];return ((x+dx)%W,(y+dy)%H)
    rnd=0;actor=None;dirs=[];used=0;turn=[];seq=0;turn_start=0;act=None
    present={};pending=None;expected=deque();deaths=[];drops=[];collisions=[]
    eats=Counter();anomalies=Counter();births=Counter();events=list(root.pointer(3))
    def snapshot():
        return {s:dict(alive=sum(side(i)==s for i in bodies),total=sum(len(b) for i,b in bodies.items() if side(i)==s),longest=max((len(b) for i,b in bodies.items() if side(i)==s),default=0),pearls=sum(eats[s,o] for o in ('drop','spawn')),queen_alive=queens[s] in bodies,queen_length=len(bodies.get(queens[s],()))) for s in ('us','them')}
    def finish_turn(end):
        hs=[d for d in turn if d['reason']==3]
        if hs:
            assert len(hs)==2 and hs[1]['id']==actor and hs[0]['id']!=actor
            assert hs[0]['body'][0]==hs[1]['destination']
            cid=f"{j['id']}:{hs[0]['event']}"
            c=dict(collision=cid,gid=j['id'],map=j['mapName'],round=rnd,
                   cross_team=hs[0]['side']!=hs[1]['side'],deaths=[d['death'] for d in hs],
                   turn_start=turn_start,event_end=end)
            collisions.append(c)
            for d in hs:d['cause']='head-on';d['collision']=cid
        turn.clear()
    for idx,ev in enumerate(events):
        k=replay.EVENT_NAMES[ev.u16(0)];p=ev.pointer(0)
        if expected:
            assert k=='tileChange' and p.u32(0)==1, (j['id'],idx,k,len(expected))
        if k=='roundStart':
            assert pending is None;finish_turn(idx);snapshots[rnd]=snapshot();rnd=p.i32(0);actor=None
        elif k=='turnStart':
            assert pending is None;finish_turn(idx);actor=p.i32(0);dirs=[];used=0;seq+=1;turn_start=idx;act=None
        elif k=='dragonAction':
            assert actor==p.i32(0)
            a=p.pointer(0);dirs=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else [];used=0
            used_up=p.pointer(1)
            act='timeout' if p.bit(32) or (used_up is not None and used_up.bit(64)) else OTHER[a.u16(0)] if a and a.u16(0)<3 else 'no action'
        elif k=='tileChange':
            c=replay.point(p.pointer(0));value=p.u32(0);assert value in (0,1)
            if value:
                assert c not in present, (j['id'],idx,'existing pearl',c)
                if expected:
                    xy,d,seg=expected.popleft();assert c==xy, (j['id'],idx,c,xy)
                    pearl=dict(pearl=f"{j['id']}:{idx}",gid=j['id'],map=j['mapName'],death=d['death'],
                               dragon=d['id'],drop_side=d['side'],drop_round=rnd,spawn_event=idx,
                               xy=c,segment_index=seg,fountain=c in fountains,eater='nobody',
                               eat_round=None,remove_event=None,update_event=None,eater_id=None,wait=None)
                    drops.append(pearl);d['pearls'].append(pearl['pearl'])
                    present[c]=dict(origin='drop',round=rnd,event=idx,record=pearl)
                else:
                    assert actor is None, (j['id'],idx,'natural spawn within turn')
                    present[c]=dict(origin='spawn',round=rnd,event=idx)
                    natural.append(c)
                    if c in removed:intervals[c].append(rnd-removed.pop(c))
                births[present[c]['origin']]+=1
            else:
                assert pending is None and c in present and actor in bodies
                pending=dict(xy=c,remove=idx,actor=actor,pearl=present.pop(c));removed[c]=rnd
        elif k=='dragonUpdate':
            i=p.i32(0);h=replay.point(p.pointer(0));tail=replay.point(p.pointer(1));b=bodies[i];before=len(b)
            moved=b[0]!=h
            if moved:b.appendleft(h)
            while len(b)>1 and b[-1]!=tail:b.pop()
            assert b[-1]==tail
            if pending:
                assert i==pending['actor'] and h==pending['xy'] and moved
                s=side(i);origin=pending['pearl']['origin'];eats[s,origin]+=1
                eaten_rounds.append((rnd,s));q_eats[s]+=i==queens[s]
                if origin=='drop':
                    pr=pending['pearl']['record'];pr.update(eater=s,eat_round=rnd,remove_event=pending['remove'],
                                                          update_event=idx,eater_id=i,wait=rnd-pr['drop_round'])
                pending=None
            elif moved and len(b)>before:anomalies['growth_without_remove']+=1
            if i==actor and moved:used+=1
        elif k=='dragonSplit':
            q_splits[side(p.i32(0))]+=p.i32(0)==queens[side(p.i32(0))]
            for z,i in enumerate((p.i32(0),p.i32(4))):
                bodies[i]=deque(replay.point(c) for c in p.pointer(z));teams[i]='AB'[p.u16(8)]
        elif k=='dragonDeath':
            assert not expected and pending is None
            i=p.i32(0);reason=p.u16(4);b=list(bodies[i]);dest=None;hit=None;cause='other'
            if i==actor and used<len(dirs):dest=destination(b[0],dirs[used])
            if reason==0:cause='wall'
            elif reason==1:cause='own body'
            elif reason==2 and dest is not None:
                owners=[z for z,bb in bodies.items() if z!=i and dest in bb]
                assert len(owners)==1, (j['id'],idx,dest,owners)
                hit=owners[0];cause='other dragon body'
            elif reason==2:anomalies['unresolved_body_cause']+=1
            d=dict(death=f"{j['id']}:{idx}",gid=j['id'],map=j['mapName'],folder=folder,ours=ours,
                   id=i,side=side(i),round=rnd,event=idx,length=len(b),dropped=(len(b)+1)//2,
                   cause=cause,reason=reason,actor=actor,hit=hit,destination=dest,body=b,pearls=[],collision=None,
                   other=(act or 'no action') if reason==4 and i==actor else 'no action' if reason==4 else None)
            deaths.append(d);turn.append(d);bodies.pop(i)
            expected.extend((c,d,seg) for seg,c in enumerate(b) if seg%2==0)
    finish_turn(len(events));snapshots[rnd]=snapshot();assert not expected and pending is None
    for pr in drops:
        if pr['eater']=='nobody':pr['wait']=rnd-pr['drop_round']
    for d in deaths:assert len(d['pearls'])==d['dropped']
    for z,t in enumerate('AB'):
        ls=[len(b) for i,b in bodies.items() if teams[i]==t];st=root.pointer(4).pointer(z)
        assert (len(ls),max(ls,default=0),sum(ls))==(st.i32(0),st.i32(4),st.i32(8))
        if root.u32(0)>=2:assert st.i32(12)==len(bodies.get(min(i for i in teams if teams[i]==t),())), (j['id'],'queen length')
    assert births['drop']==len(drops)
    assert sum(births.values())==sum(eats.values())+len(present)
    return dict(text=text,bots=dict(A=root.text(1),B=root.text(2)),queens=queens,q_eats=dict(q_eats),q_splits=dict(q_splits),snapshots=snapshots,eaten_rounds=eaten_rounds,natural=natural,intervals=dict(intervals),final=snapshot(),end_reason=root.pointer(4).u16(2),winner=('A','B')[root.pointer(4).u16(6)] if root.pointer(4).u16(4)==1 else None,gid=j['id'],map=j['mapName'],folder=folder,ours=ours,last_round=rnd,
                deaths=deaths,pearls=drops,collisions=collisions,eats={s:{o:eats[s,o] for o in ('drop','spawn')} for s in ('us','them')},
                births=dict(births),remaining=len(present),anomalies=dict(anomalies))
