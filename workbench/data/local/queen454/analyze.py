#!/usr/bin/env python3
"""Replay-only queen study; all writes stay beside this script. python3 -B analyze.py [workers]"""
import sys
sys.dont_write_bytecode = True
import json, math, statistics, concurrent.futures, os
from pathlib import Path
from collections import defaultdict, Counter, deque
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'data/analysis/top1'))
import lib
R=lib.rp
PHASES=('1-100','101-300','301-500')
def phase(r): return PHASES[0 if r<=100 else 1 if r<=300 else 2]
def span(vals,n):
    v=sorted(set(vals))
    return 0 if not v else n-max((v[(i+1)%len(v)]-v[i])%n if len(v)>1 else n for i in range(len(v)))+1

def manifest():
    rows=[]
    downloaded=json.loads((OUT/'downloaded.json').read_text()) if (OUT/'downloaded.json').exists() else []
    target=downloaded[0]['target'] if downloaded else 454
    for a in downloaded:
        d=json.loads((OUT/a['metadata']).read_text());m=d['match'];side='A' if m['teamAId']==target else 'B';o='B' if side=='A' else 'A'
        rows.append(dict(group='aAah',game=a['game'],battle=a['battle'],replay=a['replay'],side=side,
                         time=m['requestedAt'],opponent_id=m['team'+o+'Id'],opponent_rating=d['team'+o+'Elo'],
                         ranked=m['ranked'],version=None))
    if len(rows)<120:
        old=[]
        for p in (ROOT/'data/online').rglob('game-*.json'):
            j=json.loads(p.read_text())
            if target not in (j.get('teamAId'),j.get('teamBId')) or j['id'] in {a['game'] for a in rows}:continue
            if j.get('requestedAt','')<'2026-10-04T03:00:00Z':continue
            side='A' if j['teamAId']==target else 'B';o='B' if side=='A' else 'A'
            if j.get('team'+o+'Elo',0)<2000:continue
            rp=p.parent/('M'+str(j['id'])+'.replay')
            if rp.exists():old.append(dict(group='aAah',game=j['id'],battle=j.get('seriesId'),replay=str(rp.relative_to(ROOT)),side=side,time=j['requestedAt'],opponent_id=j['team'+o+'Id'],opponent_rating=j['team'+o+'Elo'],ranked=j['ranked'],version=None))
        rows.extend(sorted(old,key=lambda r:r['time'],reverse=True)[:120-len(rows)])
    ladder=[json.loads(l) for l in (ROOT/'data/analysis/ladder/rows.jsonl').read_text().splitlines() if l]
    seen=set()
    for j in ladder:
        if j.get('our_bot',{}).get('version') not in (44,47) or j['game'] in seen:continue
        seen.add(j['game']);p=ROOT/f"data/online/ladder/{j['battle']}/M{j['game']}.replay"
        assert p.exists(),str(p)
        rows.append(dict(group='ours',game=j['game'],battle=j['battle'],replay=str(p.relative_to(ROOT)),side=j['our_side'],time=j['time'],opponent_id=j['opponent_id'],opponent_rating=j['opponent_rating'],ranked=j['ranked'],version=j['our_bot']['version'],reference=j))
    for p in sorted((Path.home()/'meow-loop-out/card-38/attempt-2/replays').glob('*.replay')):
        arm,rest=p.stem.split('_',1);mp,seed,side=rest.rsplit('_',2)
        if arm not in ('base','candidate'):continue
        rows.append(dict(group='38 off' if arm=='base' else '38 on',game=p.stem,battle=None,replay=str(p),side='AB'[int(side)],time=None,opponent_id=None,opponent_rating=None,ranked=False,version='attempt-2/'+arm,pair=rest))
    return rows

def analyze(meta):
    meta=dict(meta);reference=meta.pop('reference',None)
    path=Path(meta['replay']);path=path if path.is_absolute() else ROOT/path
    root=R.load(str(path)).root();board=lib.Board(root.text(0));bodies=board.bodies;teams=board.teams
    q=board.queen[meta['side']];other='B' if meta['side']=='A' else 'A';eq=board.queen[other];start=board.starts[q]
    dist=board.manhattan
    row=dict(meta,queen_id=q,enemy_queen_id=eq,width=board.w,height=board.h,size='<=600' if board.w*board.h<=600 else '>600',bot_id=root.text(1 if meta['side']=='A' else 2) or None,
             lengths={},ground={},samples=[],windows=[],phases={p:dict(initiative=Counter(),pearls=0,splits=0,alive_rounds=0,loop_eligible=0,loop2=0,loop3=0) for p in PHASES},events=[],death=None,pearls=0,splits=0,splits_after200=0)
    raw=-1;actor=None;dirs=[];used=0;action_kind=None;timeout=False;last_death=None;steps_this=[]
    round_paths=[];trail=[start];action_history=[];round_heads={};credits=defaultdict(list);seq=0;current_action=None;fatal_recorded=False
    open_tiles=[(x,y) for x in range(board.w) for y in range(board.h) if any(n is not None for n in board.nb((x,y)))]
    def distances(s):
        ds={b[0]:0 for i,b in bodies.items() if teams[i]==s};todo=deque(ds)
        while todo:
            c=todo.popleft()
            for n in board.nb(c):
                if n is not None and n not in ds:ds[n]=ds[c]+1;todo.append(n)
        return ds
    def snap(t):
        if t in (100,200,300,400,500):row['lengths'][str(t)]=len(bodies.get(q,()))
        if t in (100,200,300,400):
            a,e=distances(meta['side']),distances(other);owned=tied=none=0
            for c in open_tiles:
                da,de=a.get(c,math.inf),e.get(c,math.inf)
                if math.isinf(da) and math.isinf(de):none+=1
                elif da<de:owned+=1
                elif da==de:tied+=1
            row['ground'][str(t)]=dict(share=(owned+tied/2)/len(open_tiles),owned=owned,tied=tied,unreachable_both=none,n=len(open_tiles))
        if t and t%10==0 and q in bodies:
            h=bodies[q][0];mates=[b[0] for i,b in bodies.items() if i!=q and teams[i]==meta['side']];foes=[(i,b[0]) for i,b in bodies.items() if teams[i]==other]
            enemy=min(foes,key=lambda z:(dist(h,z[1]),z[0])) if foes else None
            ahead=sum(dist(m,enemy[1])<dist(h,enemy[1]) for m in mates) if enemy else None
            # Circular centre of all friendly heads, avoiding an artificial centre across a wrap seam.
            own=[b[0] for i,b in bodies.items() if teams[i]==meta['side']];centre=[]
            for ax,n in ((0,board.w),(1,board.h)):
                co=sum(math.cos(2*math.pi*p[ax]/n) for p in own);si=sum(math.sin(2*math.pi*p[ax]/n) for p in own)
                centre.append((math.atan2(si,co)%(2*math.pi))*n/(2*math.pi) if math.hypot(co,si)>1e-8 else None)
            row['samples'].append(dict(round=t,phase=phase(t),ahead=ahead,teammates=len(mates),enemy_id=enemy[0] if enemy else None,
                enemy_distance=dist(h,enemy[1]) if enemy else None,nearest_teammate=min((dist(h,m) for m in mates),default=None),
                centre_distance=dist(h,centre) if None not in centre else None,start_distance=dist(h,start)))
    def finish_round():
        if raw<0:return
        t=raw+1;alive=q in bodies
        if not alive:round_paths.append(None);return
        h=bodies[q][0];p=row['phases'][phase(t)];p['alive_rounds']+=1
        before=round_heads.get(raw,{}).get(q,h);path=[before]+steps_this
        if path[-1]!=h:path.append(h)
        round_paths.append(path)
        if len(round_paths)>=8 and all(z is not None for z in round_paths[-8:]):
            pts=[round_paths[-8][0]]
            for z in round_paths[-8:]:
                for c in z[1:]:
                    if c!=pts[-1]:pts.append(c)
            p['loop_eligible']+=1
            closed=any(pts[i]==pts[j] and len(set(pts[i:j]))>=4 for i in range(len(pts)) for j in range(i+4,len(pts)))
            sx,sy=span([c[0] for c in pts],board.w),span([c[1] for c in pts],board.h)
            p['loop2']+=int(closed and sx<=2 and sy<=2)
            p['loop3']+=int(closed and sx<=3 and sy<=3)
        if t%50==0 and len(round_paths)>=50 and all(z is not None for z in round_paths[-50:]):
            pts=[c for z in round_paths[-50:] for c in z]
            row['windows'].append(dict(end=t,phase=phase(t),unique_tiles=len(set(pts)),net_displacement=dist(pts[0],pts[-1]),bbox=[span([c[0] for c in pts],board.w),span([c[1] for c in pts],board.h)]))
    def movement(i,a,b,fatal=False):
        if a==b:return
        if i==q:
            for j,bb in bodies.items():
                if teams[j]==other:credits[j].append((raw,seq,'queen',dist(a,bb[0])-dist(b,bb[0])))
            vis=[bb[0] for j,bb in bodies.items() if teams[j]==other and board.cheb(a,bb[0])<=3]
            if vis:
                d0=min(dist(a,x) for x in vis);d1=min(dist(b,x) for x in vis)
                c=row['phases'][phase(raw+1)]['initiative'];c['shorten' if d1<d0 else 'lengthen' if d1>d0 else 'equal']+=1;c['steps']+=1;c['fatal_steps']+=int(fatal)
            if not fatal:steps_this.append(b);trail.append(b)
        elif teams.get(i)==other and q in bodies:
            h=bodies[q][0];credits[i].append((raw,seq,'enemy',dist(a,h)-dist(b,h)))
    def context(enemy):
        cs=[x for x in credits.get(enemy,()) if raw-5<=x[0]<raw]
        out={who:sum(x[3] for x in cs if x[2]==who) for who in ('queen','enemy')}
        positive={who:next(((x[0]+1,x[1]) for x in cs if x[2]==who and x[3]>0),None) for who in ('queen','enemy')}
        z=[(v,who) for who,v in positive.items() if v is not None]
        out.update(first_closer=min(z)[1] if z else 'neither',steps=len(cs),window=[max(1,raw-4),raw],enemy_id=enemy)
        return out
    def event(kind,enemy,**kw):
        row['events'].append(dict(kind=kind,round=raw+1,phase=phase(raw+1),enemy_id=enemy,previous5=context(enemy),**kw))
    for ev in root.pointer(3):
        seq+=1;k=ev.u16(0);pl=ev.pointer(0)
        if k==0:
            finish_round();raw=pl.i32(0);steps_this=[];actor=None;last_death=None
            round_heads[raw]={i:b[0] for i,b in bodies.items()}
            if raw:snap(raw)
        elif k==1:
            actor=pl.i32(0);dirs=[];used=0;action_kind=None;last_death=None;fatal_recorded=False
        elif k==4:
            actor=pl.i32(0);a=pl.pointer(0);action_kind=a.u16(0) if a else None
            dirs=list(a.pointer(0)) if a is not None and action_kind==0 and a.pointer(0) is not None else [];used=0
            resources=pl.pointer(1);timeout=pl.bit(32) or (resources is not None and resources.bit(64))
        elif k==3:
            if pl.u32(0)==0 and actor==q:
                row['pearls']+=1;row['phases'][phase(raw+1)]['pearls']+=1
        elif k==9:
            i=pl.i32(0);h=R.point(pl.pointer(0));tail=R.point(pl.pointer(1));bb=bodies[i]
            if bb[0]!=h:
                movement(i,bb[0],h);bb.appendleft(h)
                if i==actor:used+=1
            while len(bb)>1 and bb[-1]!=tail:bb.pop()
            assert bb[-1]==tail
        elif k==10:
            pa,ch=pl.i32(0),pl.i32(4)
            for idx,i in enumerate((pa,ch)):bodies[i]=deque(R.point(c) for c in pl.pointer(idx));teams[i]='AB'[pl.u16(8)]
            if pa==q:
                row['splits']+=1;row['splits_after200']+=raw+1>200;row['phases'][phase(raw+1)]['splits']+=1
        elif k==11:
            i=pl.i32(0);reason=pl.u16(4);bb=bodies[i];dest=None;hit=None
            if reason==3 and not fatal_recorded and actor in bodies and used<len(dirs):
                ah=bodies[actor][0];ad=board.step(ah,dirs[used])
                if ad is not None:movement(actor,ah,ad,True);fatal_recorded=True
            if i==actor and used<len(dirs):
                dest=board.step(bb[0],dirs[used])
                if dest is not None and not fatal_recorded:movement(i,bb[0],dest,True);fatal_recorded=True
            if reason in (2,3) and dest is not None:
                hit=next((j for j,b in bodies.items() if j!=i and (b[0]==dest if reason==3 else dest in b)),None)
            if reason==3 and i==actor and hit is None and last_death:hit=last_death['id']
            if reason==3 and i!=actor:hit=actor
            enemy=hit if hit is not None and teams.get(hit)==other else None
            if i==q:
                nearest=min(((dist(bb[0],b[0]),j) for j,b in bodies.items() if teams[j]==other),default=(None,None))[1]
                cause=('wall','own body','other','enemy head' if enemy is not None else 'other','dropped with no action')[reason] if reason<5 else 'other'
                if reason==4 and action_kind==2:cause='other'
                detail='friendly head' if reason==3 and enemy is None else ('timeout' if timeout else 'no action' if action_kind is None else 'suicide' if action_kind==2 else 'invalid move' if action_kind==0 else 'invalid split') if reason==4 else 'enemy body' if reason==2 and enemy is not None else 'friendly body' if reason==2 else None
                row['death']=dict(round=raw+1,raw_round=raw,cause=cause,detail=detail,length=len(bb),actor=actor,hit=hit)
                event('death',enemy if enemy is not None else nearest,cause=cause,partner_is_cause=enemy is not None)
                if reason==3:event('head-on',enemy,queen_moved_first=actor==q,cross_team=enemy is not None)
            if teams[i]==other:
                if reason==3 and actor==q and i!=q:event('queen kill',i,method='queen head moved into enemy')
                elif reason==2 and hit==q:event('queen kill',i,method='enemy hit queen body')
            last_death=dict(id=i,head=bb[0]);bodies.pop(i)
    finish_round();completed=raw+1;snap(completed)
    result=root.pointer(4);row['rounds']=completed;row['alive_end']=q in bodies;row['final_lengths']=[len(bodies.get(q,())),len(bodies.get(eq,()))]
    row['winner']='AB'[result.u16(6)] if result.u16(4)==1 else None;row['end_reason']='round limit' if result.u16(2)==1 else 'elimination'
    row['queen_rule_decided']=result.u16(2)==1 and row['final_lengths'][0]!=row['final_lengths'][1]
    row['bbox']=[span([p[0] for p in trail],board.w),span([p[1] for p in trail],board.h)]
    for t in (100,200,300,400,500):row['lengths'].setdefault(str(t),None)
    for side in 'AB':
        ls=[len(b) for i,b in bodies.items() if teams[i]==side];st=result.pointer('AB'.index(side))
        assert (len(ls),max(ls,default=0),sum(ls))==(st.i32(0),st.i32(4),st.i32(8)),(meta['game'],'final state')
        assert st.i32(12)==len(bodies.get(board.queen[side],())),(meta['game'],'queen')
    if row['queen_rule_decided']:
        assert row['winner']==(meta['side'] if row['final_lengths'][0]>row['final_lengths'][1] else other)
    if reference:
        ref=reference['queen']['us']
        assert ref['alive_end']==row['alive_end'] and ref['pearls_eaten']==row['pearls'] and ref['splits']==row['splits'],(meta['game'],'ladder counts')
        assert reference['final']['us']['queen_length']==row['final_lengths'][0]
        assert ref['death_round']==(row['death']['raw_round'] if row['death'] else None),(meta['game'],'death round')
        row['ladder_validation']='final queen, survival, death round, pearls and splits match'
    return row

def main():
    jobs=manifest();(OUT/'manifest.json').write_text(json.dumps([{k:v for k,v in j.items() if k!='reference'} for j in jobs],indent=2)+'\n')
    cache=OUT/'computed-v2';cache.mkdir(exist_ok=True);rows=[];todo=[]
    for j in jobs:
        p=cache/(str(j['game'])+'.json')
        if p.exists():rows.append(json.loads(p.read_text()))
        else:todo.append(j)
    print('jobs',len(jobs),'cached',len(rows),'new',len(todo),flush=True)
    with concurrent.futures.ProcessPoolExecutor(max_workers=int(sys.argv[1]) if len(sys.argv)>1 else 2) as pool:
        for i,row in enumerate(pool.map(analyze,todo)):
            (cache/(str(row['game'])+'.json')).write_text(json.dumps(row,separators=(',',':'))+'\n');rows.append(row)
            if i%10==0:print('processed',i+1,'/',len(todo),flush=True)
    rows.sort(key=lambda r:(r['group'],str(r['game'])))
    (OUT/'rows.json').write_text(json.dumps(rows,indent=2)+'\n')
    print('done',dict(Counter(r['group'] for r in rows)),flush=True)
if __name__=='__main__':main()
