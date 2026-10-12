#!/usr/bin/env python3
"""Independent replay count. Run from repository root; writes only beside this script."""
import sys
sys.dont_write_bytecode = True
import json, math, statistics, concurrent.futures, argparse
from pathlib import Path
from collections import deque, Counter
from datetime import datetime
sys.path.insert(0, '~/01. Project/개인 프로젝트/battlecode')
import replay as R
OUT = Path(__file__).resolve().parent
CACHE = OUT.parent
PHASES = ('1-100','101-300','301-500')
def phase(r): return PHASES[0 if r<=100 else 1 if r<=300 else 2]
def mean(x): return statistics.mean(x) if x else None

def inputs():
    jobs=[]
    for d in json.loads((CACHE/'downloaded.json').read_text()):
        meta=json.loads((CACHE/d['metadata']).read_text());m=meta['match']
        assert 454 in (m['teamAId'],m['teamBId'])
        s='A' if m['teamAId']==454 else 'B';o='B' if s=='A' else 'A'
        jobs.append(dict(group='aAah',game=m['id'],battle=d['battle'],replay=d['replay'],side=s,
            time=m['requestedAt'],opponent_id=m['team'+o+'Id'],opponent_rating=meta.get('team'+o+'Elo'),
            ranked=m['ranked'],version=None))
    available={p.name:p for p in Path('data/online').rglob('M*.replay')}
    seen=set()
    for line in Path('data/analysis/ladder/rows.jsonl').read_text().splitlines():
        d=json.loads(line)
        if d.get('our_bot',{}).get('version') not in (44,47) or d['game'] in seen: continue
        seen.add(d['game']);p=available.get('M'+str(d['game'])+'.replay')
        if p is None: raise ValueError('missing our replay '+str(d['game']))
        jobs.append(dict(group='ours',game=d['game'],battle=d['battle'],replay=str(p),side=d['our_side'],
            time=d['time'],opponent_id=d['opponent_id'],opponent_rating=d['opponent_rating'],
            ranked=d['ranked'],version=d['our_bot']['version']))
    folder=Path.home()/'meow-loop-out/card-38/attempt-2/replays'
    for p in sorted(folder.glob('*.replay')):
        arm,rest=p.stem.split('_',1);mp,seed,side=rest.rsplit('_',2)
        jobs.append(dict(group='38 '+('off' if arm=='base' else 'on'),game=p.stem,battle=None,
            replay=str(p),side='AB'[int(side)],time=datetime.fromtimestamp(p.stat().st_mtime).astimezone().isoformat(),
            opponent_id=None,opponent_rating=None,ranked=False,version='attempt-2/'+arm,pair=rest))
    return jobs

class Board:
    def __init__(self,text):
        self.bodies={};self.teams={};edge={};self.w=self.h=0
        for line in text.splitlines():
            a=line.split()
            if not a: continue
            if a[0]=='MAP': self.w,self.h=map(int,a[1:3])
            elif a[0]=='MAP_NAME': self.name=' '.join(a[1:])
            elif a[0]=='DRAGON':
                i=len(self.bodies);self.teams[i]='AB'[int(a[1])]
                self.bodies[i]=deque((int(a[3+2*k]),int(a[4+2*k])) for k in range(int(a[2])))
            elif a[0]=='EDGE':
                row,x=divmod(int(a[1]),self.w+1)
                if row%2==0 and x==self.w or row%2==1 and row//2>=self.h: continue
                k=(x%self.w,(row//2)%self.h,'N' if row%2==0 else 'W');v=(int(a[2]),int(a[3]) if len(a)>3 else -1)
                if v[0]>=edge.get(k,(0,-1))[0]: edge[k]=v
        self.walls={k for k,v in edge.items() if v[0]==1};ports={}
        for k,(v,pid) in edge.items():
            if v==2: ports.setdefault(pid,[]).append(k)
        self.portals={}
        for ks in ports.values():
            if len(ks)==2 and ks[0][2]==ks[1][2]: self.portals[ks[0]]=ks[1];self.portals[ks[1]]=ks[0]
        self.orphans={k for k,v in edge.items() if v[0]==2 and k not in self.portals}
        self.cells=[(x,y) for y in range(self.h) for x in range(self.w)]
        self.nb={c:tuple(n for d in range(4) if (n:=self.step(c,d)) is not None) for c in self.cells}
        self.queens={s:min(i for i,t in self.teams.items() if t==s) for s in 'AB'}
    def step(self,c,d):
        x,y=c;w,h=self.w,self.h
        key=((x,y,'N') if d==0 else (x,(y+1)%h,'N') if d==2 else (x,y,'W') if d==3 else ((x+1)%w,y,'W'))
        if key in self.walls or key in self.orphans: return None
        if key in self.portals:
            px,py,o=self.portals[key];negative=d in (0,3)
            return (px,(py-1)%h if negative else py) if o=='N' else ((px-1)%w if negative else px,py)
        return ((x+(0,1,0,-1)[d])%w,(y+(-1,0,1,0)[d])%h)
    def gap(self,a,b,n):
        d=abs(a-b)%n;return min(d,n-d)
    def dist(self,a,b): return self.gap(a[0],b[0],self.w)+self.gap(a[1],b[1],self.h)
    def visible(self,a,b): return self.gap(a[0],b[0],self.w)<=3 and self.gap(a[1],b[1],self.h)<=3
    def flood(self,heads):
        ds={c:0 for c in heads};todo=deque(ds)
        while todo:
            c=todo.popleft()
            for n in self.nb[c]:
                if n not in ds: ds[n]=ds[c]+1;todo.append(n)
        return ds
    def span(self,vals,n):
        v=sorted(set(vals));return n-max((v[(i+1)%len(v)]-x)%n for i,x in enumerate(v))+1 if len(v)>1 else 1
    def bbox(self,cells):
        return [self.span([c[i] for c in cells],n) for i,n in enumerate((self.w,self.h))] if cells else [0,0]
    def centre(self,heads,q):
        ans=[]
        for i,n in enumerate((self.w,self.h)):
            sx=sum(math.cos(2*math.pi*c[i]/n) for c in heads);sy=sum(math.sin(2*math.pi*c[i]/n) for c in heads)
            if math.hypot(sx,sy)<1e-8: return None
            ans.append((math.atan2(sy,sx)*n/(2*math.pi))%n)
        return self.dist(q,ans)


def one(job):
    root=R.load(job['replay']).root();b=Board(root.text(0));bodies,teams=b.bodies,b.teams
    queen=b.queens[job['side']];enemy=b.queens['B' if job['side']=='A' else 'A'];spawn=bodies[queen][0]
    row=dict(job,queen_id=queen,map=b.name,tiles=b.w*b.h,size='<=600' if b.w*b.h<=600 else '>600',
        phases={k:dict(actions=0,move_steps=0,visible_steps=0,closer=0,farther=0,same=0,pearls=0,splits=0,kills=0,active_head_kills=0,passive_body_kills=0,headons=0,enemy_headons=0,queen_view_entries=0,enemy_view_entries=0) for k in PHASES},
        death=None,collisions=[],samples=[],windows=[],ground={},lengths={},round_positions=[],split_rounds=[])
    history={};round_visits={};actions=[];movements=deque();rnd=0;actor=None;dirs=[];idx=0;act_kind=None;collision=None;pending=None;all_q_cells=[spawn];start_pair=None
    def snapshot(): return {i:bb[0] for i,bb in bodies.items() if bb}
    def finish_action():
        nonlocal pending
        if pending is not None:
            pending['end']=bodies[queen][0] if queen in bodies else pending['last'];actions.append(pending);pending=None
    def finish_round():
        if rnd:
            row['round_positions'].append(dict(round=rnd,head=bodies[queen][0] if queen in bodies else None,
                length=len(bodies.get(queen,())),visited=round_visits.get(rnd,[])))
            if rnd in (100,200,300,400,500):
                row['lengths'][str(rnd)]=[len(bodies.get(queen,())),len(bodies.get(enemy,()))]
            if rnd in (100,200,300,400):
                ds=[b.flood([bb[0] for i,bb in bodies.items() if teams[i]==s]) for s in 'AB'];n=len(b.cells)
                wins=ties=unreached=0;z='AB'.index(job['side'])
                for c in b.cells:
                    da,db=ds[z].get(c,math.inf),ds[1-z].get(c,math.inf)
                    wins+=da<db;ties+=da==db and da<math.inf;unreached+=da==db==math.inf
                row['ground'][str(rnd)]=dict(share=(wins+0.5*ties)/n,strict_share=wins/n,tied=ties,unreached=unreached,tiles=n)
    def step_measure(did,old,new,fatal=False):
        if new is None:return
        if queen in bodies:
            q=bodies[queen][0];pc=row['phases'][phase(rnd)]
            if did==queen:
                for i,bb in bodies.items():
                    if teams[i]!=job['side'] and not b.visible(old,bb[0]) and b.visible(new,bb[0]):pc['queen_view_entries']+=1
            elif teams.get(did)!=job['side'] and not b.visible(q,old) and b.visible(q,new):pc['enemy_view_entries']+=1
        refs=({i:bb[0] for i,bb in bodies.items() if teams[i]!=job['side']} if did==queen else {queen:bodies[queen][0]} if queen in bodies else {})
        movements.append((rnd,did,old,new,refs));
        if did==queen:
            pc=row['phases'][phase(rnd)];pc['move_steps']+=1
            foes=[(b.dist(old,bb[0]),i,bb[0]) for i,bb in bodies.items() if teams[i]!=job['side']]
            if foes and any(b.visible(old,h) for _,_,h in foes):
                _,i,h=min(foes);delta=b.dist(new,h)-b.dist(old,h);pc['visible_steps']+=1;pc['closer' if delta<0 else 'farther' if delta>0 else 'same']+=1
            if not fatal:
                all_q_cells.append(new);round_visits.setdefault(rnd,[]).append(new)
                if pending: pending['moved']+=1;pending['last']=new
    def collision_context(other,kind):
        if other is None or teams.get(other)==job['side']: return None
        cur=snapshot();past=history.get(rnd-5);cur.update(collision.get('heads',{}) if collision else {})
        qnow=cur.get(queen);onow=cur.get(other)
        if qnow is None or onow is None:return None
        def closing(lo,hi):
            qc=oc=0;first=None;trace=[]
            for rr,did,old,new,refs in movements:
                if not lo<=rr<=hi or did not in (queen,other):continue
                h=refs.get(other if did==queen else queen)
                if h is None:continue
                gain=b.dist(old,h)-b.dist(new,h)
                if did==queen:qc+=gain
                else:oc+=gain
                if gain>0 and first is None:first='queen' if did==queen else 'enemy'
                trace.append(dict(round=rr,mover='queen' if did==queen else 'enemy',old=old,new=new,other_head=h,closing=gain))
            return dict(queen_closing_steps=qc,enemy_closing_steps=oc,first_positive_mover=first,steps=trace)
        oldgap=b.dist(past[queen],past[other]) if past and queen in past and other in past else None
        prior=closing(rnd-5,rnd-1);prior.update(distance_before=oldgap,
            distance_at_contact_round_start=b.dist(history[rnd][queen],history[rnd][other]) if queen in history[rnd] and other in history[rnd] else None,
            complete_history=oldgap is not None,method='Five completed rounds preceding contact. Each move compared with the other head at that moment.')
        return dict(round=rnd,kind=kind,other_id=other,actor=actor,queen_moved_into=actor==queen,
            previous_5_rounds=prior,contact_round=closing(rnd,rnd))
    for ev in root.pointer(3):
        k=ev.u16(0);p=ev.pointer(0)
        if k==0:
            finish_action();finish_round();rnd=p.i32(0)+1;actor=None;collision=None
            history[rnd]=snapshot()
            while movements and movements[0][0]<rnd-5:movements.popleft()
            if queen in bodies:round_visits[rnd]=[bodies[queen][0]]
            if rnd%10==0 and queen in bodies:
                q=bodies[queen][0];own=[bb[0] for i,bb in bodies.items() if teams[i]==job['side']];allies=[bb[0] for i,bb in bodies.items() if teams[i]==job['side'] and i!=queen]
                foes=[bb[0] for i,bb in bodies.items() if teams[i]!=job['side']]
                foe=min(foes,key=lambda h:b.dist(q,h)) if foes else None
                nearer=sum(b.dist(h,foe)<b.dist(q,foe) for h in allies) if foe is not None else None
                row['samples'].append(dict(round=rnd,phase=phase(rnd),nearer_allies=nearer,own_heads=len(own),
                    nearest_ally_distance=min((b.dist(q,h) for h in allies),default=None),centre_distance=b.centre(own,q),spawn_distance=b.dist(q,spawn)))
        elif k==1:
            finish_action();actor=p.i32(0);dirs=[];idx=0;act_kind=None;collision=None
        elif k==4:
            finish_action();actor=p.i32(0);a=p.pointer(0);act_kind=a.u16(0) if a else None
            dirs=list(a.pointer(0)) if a and act_kind==0 and a.pointer(0) is not None else [];idx=0;collision=None
            if actor==queen and queen in bodies:
                row['phases'][phase(rnd)]['actions']+=1
                pending=dict(round=rnd,start=bodies[queen][0],last=bodies[queen][0],kind=act_kind,requested=len(dirs),moved=0,dead=False)
        elif k==3:
            if not p.bit(0) and actor==queen and act_kind==0: row['phases'][phase(rnd)]['pearls']+=1
        elif k==9:
            did=p.i32(0);head,tail=R.point(p.pointer(0)),R.point(p.pointer(1));bb=bodies[did];old=bb[0]
            if head!=old:step_measure(did,old,head);bb.appendleft(head)
            while len(bb)>1 and bb[-1]!=tail:bb.pop()
            assert bb[-1]==tail,(job['game'],did,'tail mismatch')
            if did==actor:idx+=1
        elif k==10:
            pa,ch=p.i32(0),p.i32(4);oldlen=len(bodies[pa]);pb=deque(R.point(x) for x in p.pointer(0));cb=deque(R.point(x) for x in p.pointer(1))
            assert len(pb)+len(cb)==oldlen,(job['game'],'split conservation')
            bodies[pa],bodies[ch]=pb,cb;teams[pa]=teams[ch]='AB'[p.u16(8)]
            if pa==queen:
                row['phases'][phase(rnd)]['splits']+=1;row['split_rounds'].append(rnd)
        elif k==11:
            did,reason=p.i32(0),p.u16(4)
            if reason==3 and collision is None:
                heads=snapshot();dest=b.step(bodies[actor][0],dirs[idx]) if actor in bodies and idx<len(dirs) else None
                target=next((i for i,h in heads.items() if i!=actor and h==dest),None)
                collision=dict(actor=actor,target=target,heads=heads)
                if actor in bodies:step_measure(actor,bodies[actor][0],dest,True)
            elif did==actor and reason in (0,1,2) and idx<len(dirs):
                step_measure(did,bodies[did][0],b.step(bodies[did][0],dirs[idx]),True)
            if reason==2 and actor in bodies and idx<len(dirs):
                dest=b.step(bodies[actor][0],dirs[idx]);hit=next((i for i,bb in bodies.items() if i!=actor and dest in bb),None)
                if did!=queen and hit==queen and teams[did]!=job['side']:
                    row['phases'][phase(rnd)]['kills']+=1;row['phases'][phase(rnd)]['passive_body_kills']+=1
                    ctx=collision_context(did,'enemy hit queen body')
                    if ctx:row['collisions'].append(ctx)
            if reason==3 and collision and queen in (actor,collision['target']):
                other=collision['target'] if actor==queen else actor
                if teams.get(other)!=job['side'] and did!=queen:
                    row['phases'][phase(rnd)]['kills']+=1
                    if actor==queen:row['phases'][phase(rnd)]['active_head_kills']+=1
                    ctx=collision_context(other,'queen kill');
                    if ctx:row['collisions'].append(ctx)
            if did==queen:
                other=(collision['target'] if actor==queen else actor) if reason==3 and collision else None
                cause=('enemy head' if other is not None and teams.get(other)!=job['side'] else 'ally head') if reason==3 else ('wall','own body','other dragon body','?','dropped with no action')[reason] if reason<5 else 'other'
                row['death']=dict(round=rnd,raw_round=rnd-1,cause=cause,raw_reason=reason,length=len(bodies[did]),actor=actor,other_id=other)
                if reason==3:
                    row['phases'][phase(rnd)]['headons']+=1
                    if cause=='enemy head':row['phases'][phase(rnd)]['enemy_headons']+=1
                if other is None or teams.get(other)==job['side']:
                    foes=[i for i in bodies if teams[i]!=job['side']]
                    other=min(foes,key=lambda i:b.dist(bodies[queen][0],bodies[i][0])) if foes else None
                ctx=collision_context(other,'queen death; nearest enemy for non-enemy-head causes')
                if ctx:row['collisions'].append(ctx)
                if pending:pending['dead']=True
            bodies.pop(did)
    finish_action();finish_round();result=root.pointer(4)
    row.update(end_round=rnd,alive_end=queen in bodies,final_queen_lengths=[len(bodies.get(queen,())),len(bodies.get(enemy,()))],
        end_reason=result.u16(2),winner='AB'[result.u16(6)] if result.u16(4)==1 else None,terminated=result.bit(0))
    row['queen_rule_decided']=rnd==500 and result.u16(2)==1 and row['final_queen_lengths'][0]!=row['final_queen_lengths'][1]
    for s in 'AB':
        ls=[len(bb) for i,bb in bodies.items() if teams[i]==s];st=result.pointer('AB'.index(s))
        assert [len(ls),max(ls,default=0),sum(ls)]==[st.i32(i) for i in (0,4,8)],(job['game'],s,'final standing mismatch')
        if root.u32(0)>=2:assert len(bodies.get(b.queens[s],()))==st.i32(12),(job['game'],s,'final queen mismatch')
    if row['queen_rule_decided']:
        assert row['winner']==(job['side'] if row['final_queen_lengths'][0]>row['final_queen_lengths'][1] else ('B' if job['side']=='A' else 'A'))
    loop_rounds=set();lap_rounds=set()
    for i,a in enumerate(actions):
        if i>=3:
            chunk=actions[i-3:i+1];pts=[x['start'] for x in chunk];box=b.bbox(pts)
            if all(x['kind']==0 and x['requested']==x['moved']==1 and not x['dead'] for x in chunk) and a['end']==chunk[0]['start'] and len(set(pts))==4 and box==[2,2]:lap_rounds.add(a['round'])
        for period in range(4,9):
            if i+1<period:continue
            chunk=actions[i-period+1:i+1];pts=[x['start'] for x in chunk];box=b.bbox(pts)
            if (all(x['kind']==0 and x['requested']==x['moved']==1 and not x['dead'] for x in chunk)
                and chunk[-1]['round']-chunk[0]['round']==period-1 and a['end']==chunk[0]['start']
                and len(set(pts))==period and max(box)<=3):
                loop_rounds.update(x['round'] for x in chunk)
    for ph in PHASES:
        pc=row['phases'][ph];pc['loop_rounds']=sum(phase(r)==ph for r in loop_rounds);pc['lap_2x2']=sum(phase(r)==ph for r in lap_rounds)
        pc['alive_rounds']=sum(phase(x['round'])==ph and bool(x['visited']) for x in row['round_positions'])
    pos={x['round']:x for x in row['round_positions']}
    for lo in range(1,501,50):
        block=[pos.get(r) for r in range(lo,lo+50)]
        if not all(x and x['head'] is not None for x in block):continue
        pts=[c for x in block for c in x['visited']];start=history[lo][queen];end=block[-1]['head']
        row['windows'].append(dict(start_round=lo,end_round=lo+49,phase=phase(lo+49),unique_tiles=len(set(pts)),net_displacement=b.dist(start,end),bbox=b.bbox(pts)))
    row['bbox']=b.bbox(all_q_cells);row['unique_tiles']=len(set(all_q_cells));row['splits_after_200']=sum(r>200 for r in row['split_rounds'])
    row['queen_actions']=actions
    row['verified_final_state']=True
    return row

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--workers',type=int,default=3);ap.add_argument('--limit',type=int);args=ap.parse_args()
    jobs=inputs();(OUT/'selected.json').write_text(json.dumps(jobs,indent=2)+'\n')
    if args.limit:jobs=jobs[:args.limit]
    rows=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
        for row in pool.map(one,jobs):
            rows.append(row)
            if len(rows)%20==0:print('counted',len(rows),'/',len(jobs),flush=True)
    (OUT/('trial.json' if args.limit else 'rows.json')).write_text(json.dumps(rows,indent=2)+'\n')
    print('done',len(rows),flush=True)
if __name__=='__main__':main()
