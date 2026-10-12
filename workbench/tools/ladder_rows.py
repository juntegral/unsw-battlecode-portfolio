#!/usr/bin/env python3
"""Incremental, symmetric game rows from replay true state."""
import argparse
from collections import Counter, defaultdict, deque
import hashlib
import json
from pathlib import Path
from statistics import median, mean
import sys
sys.dont_write_bytecode=True
from ladder_collect import ROOT, OUT, RAW, atomic, read_lines
from ladder_replay import scan, base, edge_id, canonical_edges, OTHER

MARKS=(50,100,150,200,300,400)
WINDOWS=('r0-100','r101-300','r301-500')
CAUSES=('wall','own body','other dragon body','head-on','other')
# Source hash -> the name the team uses for that code. Add a line when a new main goes live; code without a line is named "v<version> <submission name>".
CODE={'29410932104f32fec287e2d0f84d2c3fceeb558e7c2f9ba1413420a6255d6cb4':'v31',
      '724684aa359f614ad97d5b7b976fcc9675dbaa766db4292a63322807002f2398':'main'}
ROOM_CAP=60
REGION_CAP=400
DEPTH=16

def window(r): return WINDOWS[0 if r<=100 else 1 if r<=300 else 2]

def submissions():
    p=RAW/'submissions.json'
    return json.loads(p.read_text()) if p.exists() else {}

def our_bot(bot_id,table):
    """(our_bot, our_code, note) from the bot id the replay stores for our side."""
    if not bot_id or not bot_id.isdigit():return None,'unknown','The replay stores no bot id for our side.'
    s=table.get(bot_id)
    if not s:return dict(id=int(bot_id),version=None,name=None,source=None,test=None,same_code_as=[]),'unknown','Bot id read from the replay; it is not in data/online/ladder/submissions.json, so the code is not named.'
    h=s.get('sourceHash');same=sorted(v['version'] for v in table.values() if h and v.get('sourceHash')==h and v.get('version') is not None)
    bot=dict(id=int(bot_id),version=s.get('version'),name=s.get('name'),source=h[:10] if h else None,test=(s.get('description') or '').startswith('TEST'),same_code_as=same)
    return bot,CODE.get(h) or f"v{s.get('version')} {s.get('name')}",None

def make_row(path,j,battle=None,table=None):
    b=battle or {}; g=scan(path,j,str(path.parent),set()); ours=g['ours']; other='B' if ours=='A' else 'A'
    bot,code,code_note=our_bot(g['bots'][ours],submissions() if table is None else table)
    row=dict(battle=b.get('id'),game=j['id'],map=j['mapName'],map_version=None,map_key=None,time=j.get('completedAt'),
             opponent_id=b.get('opponentId',j.get('team'+other+'Id')),opponent=b.get('opponent',j.get('team'+other+'Name')),
             opponent_rating=b.get('opponentElo',j.get('team'+other+'Elo')),ranked=j.get('ranked'),our_submission=b.get('our_submission'),
             our_bot=bot,our_code=code,our_side=ours,win=g['winner']==ours,result='win' if g['winner']==ours else 'loss' if g['winner'] else 'draw',last_round=g['last_round'],notes={})
    if row['our_submission'] is None:row['notes']['our_submission']='No unambiguous enclosing submission-count poll interval; use our_bot.'
    if code_note:row['notes']['our_code']=code_note
    if bot is None:row['notes']['our_bot']=code_note
    final=g['final'];row['final']={s:{k:v for k,v in final[s].items() if k in ('queen_length','longest','total','alive')} for s in ('us','them')}
    us,them=final['us'],final['them']
    row['ended_by']=('elimination' if g['end_reason']==0 else 'queen rule' if us['queen_length']!=them['queen_length'] else 'longest dragon' if us['longest']!=them['longest']
                     else 'total length' if us['total']!=them['total'] else 'draw')
    row['queens_at_end']='both alive' if us['queen_alive'] and them['queen_alive'] else 'only ours' if us['queen_alive'] else 'only theirs' if them['queen_alive'] else 'both dead'
    lead=lambda k:'us' if us[k]>them[k] else 'them' if us[k]<them[k] else None
    expect=lead('alive') if g['end_reason']==0 else lead('queen_length') or lead('longest') or lead('total')
    if row['result']!={'us':'win','them':'loss',None:'draw'}[expect] or (g['end_reason']==0 and us['alive'] and them['alive']):
        row['notes']['result']='The stored winner is not the one the written rules give for this final state; ended_by describes the final state, result the stored winner.'
    row['curves']={}
    for r in (*MARKS,'end'):
        snap=g['snapshots'].get(r) if r!='end' else final
        row['curves'][str(r)]=snap
        if snap is None:row['notes'][f'curves.{r}']='Game ended before this round; no extrapolation.'
    row['queen']={}
    for s in ('us','them'):
        q=g['queens'][s];d=next((d for d in g['deaths'] if d['id']==q),None)
        ram=None
        if d and d['cause']=='head-on':
            c=next(c for c in g['collisions'] if c['collision']==d['collision']);ds=[x for x in g['deaths'] if x['death'] in c['deaths']]
            ram=dict(attacker=d['actor'],victim=next(x['id'] for x in ds if x['id']!=d['actor']),attacker_side=next(x['side'] for x in ds if x['id']==d['actor']))
        row['queen'][s]=dict(id=q,alive={str(r):g['snapshots'][r][s]['queen_alive'] if r in g['snapshots'] else None for r in MARKS},
            alive_end=final[s]['queen_alive'],death_round=d['round'] if d else None,death_cause=d['cause'] if d else 'none',
            death_other=d['other'] if d and d['cause']=='other' else None,
            death_length=d['length'] if d else None,death_hit_id=d['hit'] if d else None,head_on=ram,
            length={str(r):g['snapshots'][r][s]['queen_length'] if r in g['snapshots'] else None for r in (100,200,300,400,500)},
            pearls_eaten=g['q_eats'].get(s,0),splits=g['q_splits'].get(s,0))
        if not d:row['notes'][f'queen.{s}.death_round/death_length']='Queen survived.'
        for r in (100,200,300,400,500):
            if r not in g['snapshots']:row['notes'][f'queen.{s}.length.{r}']='Game ended before this round.'
    row['deaths']={w:{s:{c:sum(d['side']==s and d['cause']==c and window(d['round'])==w for d in g['deaths']) for c in CAUSES} for s in ('us','them')} for w in WINDOWS}
    row['deaths_other']={w:{s:{k:sum(d['side']==s and d['cause']=='other' and d['other']==k and window(d['round'])==w for d in g['deaths']) for k in OTHER} for s in ('us','them')} for w in WINDOWS}
    cross=[c for c in g['collisions'] if c['cross_team']];death_ids={v for c in cross for v in c['deaths']}
    row['head_on']=dict(count=len(cross),same_team_count=len(g['collisions'])-len(cross),drops={})
    for s in ('us','them'):
        ps=[p for p in g['pearls'] if p['death'] in death_ids and p['drop_side']==s]
        eligible=[p for p in ps if p['eat_round'] is not None and p['wait']<=15]
        censored=sum(p['eat_round'] is None and p['wait']<15 for p in ps)
        row['head_on']['drops'][s]=dict(total=len(ps),eaten_within_15={e:sum(p['eater']==e for p in eligible) for e in ('us','them')},
            not_eaten_within_15=len(ps)-len(eligible)-censored,censored=censored,
            eaten_by_end={e:sum(p['eater']==e for p in ps) for e in ('us','them','nobody')})
    for side in ('us','them'):
        if g['end_reason']==1 and g['last_round']==499:
            row['queen'][side]['length']['500']=final[side]['queen_length']
            row['notes'].pop(f'queen.{side}.length.500',None)
    row['pearls']={}
    for w in WINDOWS:
        counts={s:sum(window(r)==w and side==s for r,side in g['eaten_rounds']) for s in ('us','them')};n=sum(counts.values())
        row['pearls'][w]=dict(eaten=counts,our_share=counts['us']/n if n else None)
        if not n:row['notes'][f'pearls.{w}.our_share']='No pearls eaten in this window.'
    def explain(value,prefix=''):
        if isinstance(value,dict):
            for k,v in value.items():
                if k!='notes':explain(v,f'{prefix}.{k}' if prefix else k)
        elif value is None and prefix not in row['notes'] and prefix not in ('map_version','map_key'):
            row['notes'][prefix]='Not applicable or unavailable in the source metadata; no inferred value.'
    explain(row)
    return row,g


def signature(text):
    """Identity of a map's layout: size, edges and starting dragons, the same for both team colourings."""
    h=base.header(text);dragons=[tuple(d) for d in h['dragons']];swapped=[(str(1-int(d[0])),*d[1:]) for d in dragons]
    return hashlib.sha1(json.dumps([h['size'],h['edges'],min(dragons,swapped)]).encode()).hexdigest()[:10]

def geometry(text):
    h=base.header(text); W,H=h['size']; edges=canonical_edges(W,H,[tuple(map(int,e)) for e in h['edges']])
    degrees=[sum(edges.get(edge_id(W,H,x,y,d),(0,-1))[0]!=1 for d in range(4)) for y in range(H) for x in range(W)]
    open_n=sum(n>0 for n in degrees)
    portals=defaultdict(list)
    for e,(k,pid) in edges.items():
        if k==2:portals[pid].append(e)
    def step(c,d):
        x,y=c;e=edge_id(W,H,x,y,d);k,pid=edges.get(e,(0,-1))
        if k==1:return None
        if k==2:
            partner=[z for z in portals[pid] if z!=e]
            if len(partner)!=1:return None
            row,px=divmod(partner[0],W+1)
            return ((px-(d==3))%W,(row//2-(d==0))%H)
        dx,dy=base.STEP[d];return ((x+dx)%W,(y+dy)%H)
    bodies=[[(int(d[2+2*k]),int(d[3+2*k])) for k in range(int(d[1]))] for d in h['dragons']]
    assert h['dragons'][0][0]!=h['dragons'][1][0], 'dragons 0 and 1 are on the same team'
    occupied={c for b in bodies for c in b}
    def flood(start,blocked,cap):
        seen={start};todo=deque([start])
        while todo and len(seen)-1<cap:
            c=todo.popleft()
            for d in range(4):
                n=step(c,d)
                if n is not None and n not in seen and n not in blocked:seen.add(n);todo.append(n)
        return min(len(seen)-1,cap)
    def way_out(body):
        frozen=occupied-set(body);seen=set();left=[20000]
        def go(b,n):
            if n==0 or left[0]<=0:return True
            if (b,n) in seen:return False
            seen.add((b,n));left[0]-=1
            for d in range(4):
                t=step(b[0],d)
                if t is None or t in b or t in frozen:continue
                if go((t,)+b[:-1],n-1):return True
            return False
        return go(tuple(body),DEPTH)
    queens=bodies[:2];a,z=queens[0][0],queens[1][0];gap=lambda a,b,n:min(abs(a-b),n-abs(a-b))
    return h,dict(width=W,height=H,open_tiles=open_n,wall_share=sum(4-n for n in degrees)/(4*W*H),
        portals=len(portals),queen_spawn_distance=gap(a[0],z[0],W)+gap(a[1],z[1],H),
        corridor_share=sum(n==2 for n in degrees)/open_n if open_n else None,
        dragons_at_spawn=len(bodies)//2,queen_spawn_length=min(len(b) for b in queens),
        queen_spawn_room=min(flood(b[0],occupied,ROOM_CAP) for b in queens),
        queen_spawn_region=min(flood(b[0],set(),REGION_CAP-1)+1 for b in queens),
        queen_spawn_dead_end=not all(way_out(b) for b in queens))

def local_ranges(name,h):
    rel=base.LOCAL.get(name)
    candidates=[base.BC/rel] if rel else []
    candidates+=list((ROOT/'maps').rglob('*.map'))
    for p in candidates:
        if not p.exists():continue
        try:
            text=base.replay.load(p).root().text(0) if p.suffix=='.replay' else p.read_text();l=base.header(text)
            if l['size']!=h['size'] or l['edges']!=h['edges'] or set(l['ranges'])!=set(h['ranges']):continue
            swapped=[(str(1-int(d[0])),*d[1:]) for d in l['dragons']]
            if h['dragons'] not in (l['dragons'],swapped):continue
            if any(hi>0 for lo,hi in l['ranges'].values()):return l['ranges'],str(p)
        except (ValueError,KeyError,IndexError):continue
    return None,None

def map_keys(observations):
    """{game id: (version, key)}. Every layout seen under a map name is a version, numbered by its first game."""
    first=defaultdict(dict)
    for gid,o in observations.items():
        sig=o.get('sig') or signature(o['text']);o['sig']=sig;t=(o.get('time') or '',int(gid))
        first[o['map']][sig]=min(t,first[o['map']].get(sig,t))
    order={name:{sig:n+1 for n,(sig,_) in enumerate(sorted(v.items(),key=lambda x:x[1]))} for name,v in first.items()}
    return {gid:(order[o['map']][o['sig']],f"{o['map']} #{order[o['map']][o['sig']]}") for gid,o in observations.items()}

def build_maps(observations):
    keys=map_keys(observations);grouped=defaultdict(list)
    for gid,o in observations.items():grouped[keys[gid]].append(o)
    names=Counter(obs[0]['map'] for obs in grouped.values())
    maps={}
    for (version,key),obs in sorted(grouped.items(),key=lambda x:x[0][1]):
        name=obs[0]['map'];h,shape=geometry(obs[0]['text']);ranges,source=local_ranges(name,h)
        intervals=defaultdict(list);births=Counter()
        for o in obs:
            births.update(o['natural'])
            for c,vs in o['intervals'].items():intervals[c].extend(vs)
        total=sum(births.values());notes={};times=sorted(o['time'] for o in obs if o.get('time'))
        m=dict(name=name,version=version,versions_of_name=names[name],first_game=times[0] if times else None,last_game=times[-1] if times else None,games_observed=len(obs),**shape)
        spawning={f'{x},{y}':v for (x,y),v in (ranges or {}).items() if v[1]>0}
        stray=sum(n for c,n in births.items() if c not in spawning) if ranges else 0
        if stray:
            notes['source']=f'{source} has this layout but not these pearls: {stray} of {total} natural births were on tiles it says never spawn. Its gaps are not used.'
            ranges=None
        if ranges:
            rates={c:2/(lo+hi) for c,(lo,hi) in spawning.items()};fast={c for c,(lo,hi) in spawning.items() if 1<=hi<=12}
            m.update(pearl_tiles=len(spawning),fast_tiles=len(fast),fast_rate_share=sum(rates[c] for c in fast)/sum(rates.values()),supply_method='local gaps',source=source)
        else:
            fast={c for c,vs in intervals.items() if len(vs)>=5 and median(vs)<=12}
            notes.setdefault('source','No structurally matching local map with real gaps.')
            notes.update(pearl_tiles='Tiles seen to spawn a pearl in the observed games; a lower bound.',
                         fast_tiles='Tiles with >=5 removal-to-next-natural-spawn intervals whose median is <=12; fast tiles that were rarely eaten are missed.',
                         fast_rate_share='Needs real gaps.')
            m.update(pearl_tiles=len(births),fast_tiles=len(fast),fast_rate_share=None,supply_method='observed intervals',source=None,
                     observed_intervals={c:dict(n=len(v),median=median(v),mean=mean(v),fast=c in fast) for c,v in intervals.items()})
        m['fast_supply_share']=sum(births[c] for c in fast)/total if total else None
        m['natural_births']=total;m['notes']=notes;maps[key]=m
    return maps

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--rebuild',action='store_true');args=ap.parse_args()
    old={r['game']:r for r in read_lines(OUT/'rows.jsonl')};observations=json.loads((OUT/'map-observations.json').read_text()) if (OUT/'map-observations.json').exists() else {};added=0
    table=submissions()
    def save():
        keys=map_keys(observations)
        for r in old.values():
            if str(r['game']) in keys:r['map_version'],r['map_key']=keys[str(r['game'])]
        atomic(OUT/'rows.jsonl',sorted(old.values(),key=lambda r:(r.get('time') or '',r['game'])),True)
        atomic(OUT/'map-observations.json',observations)
    for b in read_lines(OUT/'battles.jsonl'):
        for entry in b.get('games',[]):
            gid=entry['id'];folder=RAW/str(b['id']);p=folder/f'M{gid}.replay';jp=folder/f'game-{gid}.json'
            if gid in old and str(gid) in observations and not args.rebuild:
                r=old[gid];r['our_submission']=b.get('our_submission')
                if b.get('our_submission') is not None:r['notes'].pop('our_submission',None)
                else:r['notes']['our_submission']='No unambiguous enclosing submission-count poll interval; use our_bot.'
                if r.get('our_code')=='unknown' and r.get('our_bot'):
                    r['our_bot'],r['our_code'],note=our_bot(str(r['our_bot']['id']),table)
                    if note is None:r['notes'].pop('our_code',None)
                continue
            if not p.exists() or not jp.exists():continue
            row,g=make_row(p,json.loads(jp.read_text()),b,table);old[gid]=row;added+=1
            observations[str(gid)]=dict(map=row['map'],time=row['time'],sig=signature(g['text']),text=g['text'],natural=dict(Counter(f'{x},{y}' for x,y in g['natural'])),intervals={f'{x},{y}':vs for (x,y),vs in g['intervals'].items()})
            if added%10==0:save()
    save()
    atomic(OUT/'maps.json',build_maps(observations))
    print(f'rows: rebuilt {added}, total {len(old)} games, {len({r["map"] for r in old.values()})} maps, {len({r.get("map_key") for r in old.values()})} map layouts')
if __name__=='__main__':main()
