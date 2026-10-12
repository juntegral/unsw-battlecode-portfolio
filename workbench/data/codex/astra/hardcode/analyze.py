#!/usr/bin/env python3
"""Offline hardcode audit. All outputs remain beside this script."""
import sys
sys.dont_write_bytecode = True
import csv
import gzip
import hashlib
import itertools
import json
from collections import Counter, defaultdict, deque
from datetime import datetime
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'data/analysis/ladder/dossier/online'))
import label_report as lr
sys.path.insert(0, str(ROOT/'data/analysis/ladder/losses/counts'))
from count_replays import Geometry, INF
sb = lr.agg.sb
point = sb.replay_format.point


def dump(name, obj):
    (OUT/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')


def hashed(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:20]


def inventory():
    jobs, notes = [], []
    for opp, versions in [('d1', (1,3,4,5)), ('w1', (1,2,3,4,5))]:
        for v in versions:
            label = f'one{v}-{opp}'
            inv = lr.inventory(label, 'old')
            notes.extend(inv['notes'])
            jobs.extend(dict(label=label, path=str(p), meta=m, extra=False) for p,m in inv['jobs'])
    indices = [json.loads(s) for s in (ROOT/'data/top1/index.jsonl').read_text().splitlines() if s.strip()]
    battles = {j['battle'] for j in indices if 545 in (j.get('team'),j.get('opp'))}
    for bid in sorted(battles):
        folder = ROOT/'data/online/top1'/str(bid)
        for p in sorted(folder.glob('game-*.json')):
            m = json.loads(p.read_text())
            rp = p.with_name(f"M{m['id']}.replay")
            if 545 in (m.get('teamAId'), m.get('teamBId')) and rp.exists():
                jobs.append(dict(label='top1',path=str(rp),meta=m,extra=True))
    assert len({j['meta']['id'] for j in jobs}) == len(jobs)
    dump('inventory.json', dict(at=datetime.now().astimezone().isoformat(), notes=notes, jobs=jobs,
        ladder_check='data/analysis/ladder has no game-*.json; top1 index resolves to data/online/top1/'))
    return jobs


def header(root):
    lines = root.text(0).splitlines()
    w,h = map(int, lines[0].split()[1:3])
    raw, bodies, teams, params = [], {}, {}, {}
    for line in lines:
        q = line.split()
        if not q:
            continue
        if q[0] == 'EDGE':
            raw.append(tuple(map(int,q[1:4])))
        elif q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
            teams[i] = int(q[1])
        elif q[0] == 'TILE':
            params[int(q[2])*w+int(q[1])] = tuple(map(int,q[3:5]))
    key = hashed([w,h,raw])
    startkey = hashed([[teams[i],list(b)] for i,b in bodies.items()])
    return w,h,raw,bodies,teams,params,key,startkey


def build_support(jobs):
    support = defaultdict(set)
    manifest = []
    for n,j in enumerate(jobs):
        root = sb.load_replay(Path(j['path'])).root()
        assert root.u32(0) == 2 and root.pointer(4).bit(0)
        w,h,raw,b,t,params,key,startkey = header(root)
        actor, rnd, natural, kinds = None,-1,set(),Counter()
        for e in root.pointer(3):
            k = e.u16(0)
            kinds[k] += 1
            if k == 0:
                actor = None
                rnd = e.pointer(0).i32(0)
            elif k == 1:
                actor = e.pointer(0).i32(0)
            elif k == 3 and actor is None:
                p = e.pointer(0)
                assert p.u32(0) == 1
                x,y = point(p.pointer(0))
                natural.add(y*w+x)
        support[key].update(natural)
        support[key].update(c for c, (_,hi) in params.items() if hi > 0)
        j.update(geometry=key,startkey=startkey,w=w,h=h,natural=sorted(natural))
        manifest.append(dict(gid=j['meta']['id'],key=key,startkey=startkey,
                             natural=len(natural),countdown_events=kinds[2],last_round=rnd,
                             nonzero_map_tiles=sum(hi>0 for lo,hi in params.values())))
        if n % 25 == 0:
            print('support', n, '/',len(jobs), flush=True)
    dump('support.json',dict(tiles={k:sorted(v) for k,v in support.items()}, games=manifest))
    dump('jobs.json',jobs)
    return support


def scan(j, support):
    root = sb.load_replay(Path(j['path'])).root()
    w,h,raw,bodies,teams,params,key,startkey = header(root)
    g = Geometry(w,h,raw)
    tile = lambda p: p[1]*w+p[0]
    starts = [[b[0] for i,b in bodies.items() if teams[i] == s] for s in (0,1)]
    startds = [g.bfs(v) for v in starts]
    sources = support[key]
    dist = g.bfs(sources)
    own_sources = set(j['natural'])
    own_dist = g.bfs(own_sources)
    lineages = {i:f'S{[z for z in bodies if teams[z] == teams[i]].index(i)}' for i in bodies}
    children = Counter()
    seen = [set(), set()]
    seen_pearl = [False,False]
    counts = [Counter(),Counter()]
    first_meal = [None,None]
    first_source_seen = [None,None]
    records, misses, blind, checkpoints = [[],[]], [], [], {}
    occ = {c:(i,k) for i,b in bodies.items() for k,c in enumerate(b)}
    pearls = {}
    rnd, actor, cur = -1,None,None
    checks = Counter()
    cumulative = [Counter(),Counter()]

    def finish():
        nonlocal cur
        if cur is None:
            return
        s = cur['s']
        st = counts[s]
        st['turns'] += 1
        rec = dict(r=cur['r'],id=cur['id'],lineage=cur['lineage'],h=cur['h'],L=cur['L'],
                   path=cur['path'],split=cur['split'],died=cur['died'],
                   action=cur.get('action'),view=cur['view'],self=cur['self'])
        records[s].append(rec)
        first = cur['path'][0] if cur['path'] else None
        for suffix, eligible, ds in [('',cur['eligible'],dist),('_single',cur['eligible_single'],own_dist)]:
            if cur['r'] > 60 or not eligible:
                continue
            st['blind_turns'+suffix] += 1
            free = cur['free']
            if first is None or first not in free or ds[cur['h']] == INF:
                st['blind_unusable'+suffix] += 1
                continue
            n = sum(ds[t] < ds[cur['h']] for t in free)
            st['blind_moves'+suffix] += 1
            st['blind_toward'+suffix] += int(ds[first] < ds[cur['h']])
            st['blind_expected'+suffix] += n/len(free)
            st['blind_free'+suffix] += len(free)
            st['blind_free_good'+suffix] += n
            if len(free)>1:
                st['blind_choice_moves'+suffix] += 1
                st['blind_choice_toward'+suffix] += int(ds[first] < ds[cur['h']])
                st['blind_choice_expected'+suffix] += n/len(free)
            if not suffix:
                blind.append(dict(gid=j['meta']['id'],side=s,r=cur['r'],dragon=cur['id'],
                    head=cur['h'],first=first,free=free,d0=int(ds[cur['h']]),d1=int(ds[first]),expected=n/len(free)))
        if cur['adjacent']:
            st['adjacent_turns'] += 1
            remaining = [c for c in cur['adjacent'] if c not in cur['ate']]
            visible_adjacent = set(cur['adjacent']) & set(cur['pearl_view'])
            st['visible_adjacent_turns'] += bool(visible_adjacent)
            st['visible_miss_turns'] += bool(visible_adjacent - set(cur['ate']))
            st['visible_none_taken'] += bool(visible_adjacent) and not bool(visible_adjacent & set(cur['ate']))
            if remaining:
                st['miss_turns'] += 1
                st['miss_tiles'] += len(remaining)
                st['miss_split'] += bool(cur['split'])
                st['miss_dead'] += cur['died']
                st['miss_other_meal'] += bool(cur['ate'])
                st['miss_foe3'] += cur['foe3']
                misses.append(dict(gid=j['meta']['id'],map=j['meta']['mapName'],label=j['label'],side=s,
                    r=cur['r'],dragon=cur['id'],head=cur['h'],pearls=remaining,first=first,
                    end=cur['path'][-1] if cur['path'] else cur['h'],path=cur['path'],L=cur['L'],
                    split=cur['split'],died=cur['died'],other_meals=cur['ate'],foe3=cur['foe3'],
                    pearl_view=cur['pearl_view'],enemy_heads=cur['enemy_heads'],free=cur['free'],
                    adjacent=cur['adjacent'],visible_adjacent=sorted(visible_adjacent),
                    pearl_origin={str(c):cur['origins'][c] for c in remaining}))
        cur = None

    for e in root.pointer(3):
        k = e.u16(0)
        if k not in (0,1,3,4,9,10,11):
            continue
        p = e.pointer(0)
        if k == 0:
            finish()
            if rnd >= 0:
                checkpoints[rnd] = [dict(c) for c in cumulative]
            rnd, actor = p.i32(0),None
            if rnd>100:
                break
        elif k == 1:
            finish()
            actor = p.i32(0)
            b = bodies[actor]
            hd, s = b[0],teams[actor]
            window = g.window(hd)
            seen[s].update(window)
            if first_source_seen[s] is None and seen[s]&sources:
                first_source_seen[s] = rnd
            visible_pearl = sorted(window & pearls.keys())
            seen_pearl[s] |= bool(visible_pearl)
            view = dict(pearl=hashed(visible_pearl),enemy=hashed(sorted((c,occ[c][0],int(occ[c][1]==0))
                for c in window & occ.keys() if teams[occ[c][0]]!=s)),
                ally=hashed(sorted((c,occ[c][0],int(occ[c][1]==0))
                for c in window & occ.keys() if teams[occ[c][0]]==s and occ[c][0]!=actor)))
            free = [dst for kind,dst in g.moves[hd] if kind != 1 and dst not in occ]
            adjacent = sorted(set(free) & pearls.keys())
            enemy_heads = [bb[0] for i,bb in bodies.items() if teams[i]!=s and bb[0] in window]
            cur = dict(r=rnd,id=actor,s=s,lineage=lineages[actor],h=hd,L=len(b),
                path=[],split=None,died=False,ate=[],view=view,self=hashed(list(b)),
                eligible=not seen_pearl[s] and not bool(seen[s]&sources),
                eligible_single=not seen_pearl[s] and not bool(seen[s]&own_sources),
                free=free,adjacent=adjacent,origins={c:pearls[c] for c in adjacent},
                pearl_view=visible_pearl,enemy_heads=enemy_heads,foe3=bool(enemy_heads))
            checks['turns'] += 1
        elif k == 4:
            assert actor == p.i32(0)
            a = p.pointer(0)
            cur['action'] = [a.u16(0),list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else None]
        elif k == 3:
            c = tile(point(p.pointer(0)))
            if p.u32(0):
                assert c not in pearls
                pearls[c] = 'natural' if actor is None else 'drop'
            else:
                origin = pearls.pop(c)
                assert cur is not None and actor in bodies
                s = teams[actor]
                cur['ate'].append(c)
                cumulative[s]['pearls'] += 1
                cumulative[s][origin] += 1
                if first_meal[s] is None:
                    first_meal[s] = dict(r=rnd,dragon=actor,tile=c,distance=int(startds[s][c]),
                        origin=origin,seen_spawn_before=bool(seen[s]&sources),
                        first_source_seen=first_source_seen[s],lineage=lineages[actor])
        elif k == 9:
            i = p.i32(0)
            hd,tl = tile(point(p.pointer(0))),tile(point(p.pointer(1)))
            b = bodies[i]
            old = list(b)
            if b[0]!=hd:
                assert hd in g.adj[b[0]], ('bad movement geometry',j['meta']['id'],rnd,i,b[0],hd)
                b.appendleft(hd)
                if cur is not None and actor == i:
                    cur['path'].append(hd)
            while len(b)>1 and b[-1]!=tl:
                b.pop()
            assert b[-1]==tl
            for c in old:
                occ.pop(c,None)
            for z,c in enumerate(b):
                assert c not in occ
                occ[c] = (i,z)
            checks['updates'] += 1
        elif k == 10:
            parent,child = p.i32(0),p.i32(4)
            for c in bodies[parent]:
                occ.pop(c)
            children[parent] += 1
            lineages[child] = lineages[parent]+f'.C{children[parent]}'
            for z,i in enumerate((parent,child)):
                bodies[i] = deque(tile(point(c)) for c in p.pointer(z))
                teams[i] = p.u16(8)
                for seg,c in enumerate(bodies[i]):
                    assert c not in occ
                    occ[c] = (i,seg)
            if cur is not None and actor==parent:
                cur['split'] = [len(bodies[parent]),len(bodies[child])]
        elif k == 11:
            i = p.i32(0)
            for c in bodies[i]:
                occ.pop(c)
            bodies.pop(i)
            if cur is not None and actor==i:
                cur['died'] = True
    finish()
    if rnd<=100:
        checkpoints[rnd] = [dict(c) for c in cumulative]
    assert sum(c['turns'] for c in counts) == checks['turns']
    result = dict(gid=j['meta']['id'],map=j['meta']['mapName'],label=j['label'],extra=j['extra'],
        teams=[j['meta']['teamAId'],j['meta']['teamBId']],geometry=key,startkey=startkey,
        w=w,h=h,cells=w*h,counts=[dict(c) for c in counts],first_meal=first_meal,
        pearls100=[dict(c) for c in cumulative],checks=dict(checks),bots=[root.text(1),root.text(2)],
        blind=blind,misses=misses)
    with gzip.open(OUT/f"turns-{result['gid']}.json.gz",'wt') as f:
        json.dump(records,f,separators=(',',':'))
    return result


def compare(results):
    groups = defaultdict(list)
    for r in results:
        if r['extra']:
            continue
        for s,team in enumerate(r['teams']):
            groups[team,r['geometry'],r['startkey'],s,r['label'].split('-')[1]].append((r,s))
    pairs=[]
    for group, entries in groups.items():
        loaded=[]
        for r,s in entries:
            with gzip.open(OUT/f"turns-{r['gid']}.json.gz",'rt') as f:
                recs=json.load(f)[s]
            loaded.append((r,{(t['r'],t['lineage']):t for t in recs}))
        for (ra,a),(rb,b) in itertools.combinations(loaded,2):
            same, changed, changed_same, diff = 0,0,0,None
            for k in sorted(set(a)|set(b)):
                x,y=a.get(k),b.get(k)
                if x is None or y is None:
                    diff=dict(r=k[0],lineage=k[1],kind='birth/death',view=['unmatched'],ids=[x and x['id'],y and y['id']])
                    break
                vd=[v for v in ('pearl','enemy','ally') if x['view'][v]!=y['view'][v]]
                if x['self']!=y['self']:
                    vd.append('self')
                action_same=(x['h'],x['path'],x['split'],x['died'])==(y['h'],y['path'],y['split'],y['died'])
                changed += bool(vd)
                if not action_same:
                    diff=dict(r=k[0],lineage=k[1],kind='path',view=vd or ['nothing'],ids=[x['id'],y['id']],
                        heads=[x['h'],y['h']],paths=[x['path'],y['path']],actions=[x['action'],y['action']])
                    break
                same += 1
                changed_same += bool(vd)
            pairs.append(dict(team=group[0],map=ra['map'],side='AB'[group[3]],opponent_set=group[4],
                games=[ra['gid'],rb['gid']],labels=[ra['label'],rb['label']],first=diff,
                same_turns_before=same,changed_view_turns_before_or_at=changed,changed_view_same_path=changed_same))
    dump('pairs.json',pairs)
    return pairs


def aggregate(results,pairs):
    grouped=defaultdict(Counter)
    meals=defaultdict(list)
    passby=defaultdict(list)
    for r in results:
        if r['extra']:
            continue
        for s,team in enumerate(r['teams']):
            group=(team,'small' if r['cells']<=1200 else 'big')
            grouped[group].update(r['counts'][s])
            grouped[group]['games']+=1
            if r['first_meal'][s] is not None:
                meals[group].append(dict(gid=r['gid'],map=r['map'],**r['first_meal'][s]))
            for m in r['misses']:
                if m['side']==s:
                    passby[team].append(dict(**m,w=r['w'],h=r['h']))
    rows=[]
    for (team,size),c in sorted(grouped.items()):
        m=meals[team,size]
        row=dict(team=team,size=size,**c)
        for suffix in ('','_single'):
            den=c['blind_expected'+suffix]
            row['ratio'+suffix]=c['blind_toward'+suffix]/den if den else None
        row['first_meals']=m
        row['first_r_median']=median(x['r'] for x in m) if m else None
        row['start_d_median']=median(x['distance'] for x in m) if m else None
        row['arrival_extra_median']=median(x['r']+1-x['distance'] for x in m) if m else None
        row['by_shortest_rounds']=sum(x['r']+1<=x['distance'] for x in m)
        rows.append(row)
    recurrences=[]
    for team,events in passby.items():
        tiles=defaultdict(list)
        for m in events:
            for c in m['pearls']:
                tiles[m['map'],m['side'],c].append(m)
        for (mp,s,c),ev in sorted(tiles.items()):
            recurrences.append(dict(team=team,map=mp,side=s,tile=[c%ev[0]['w'],c//ev[0]['w']],
                games=sorted({m['gid'] for m in ev}),sets=sorted({m['label'] for m in ev}),
                events=len(ev),moments=[[m['gid'],m['r'],m['dragon']] for m in ev]))
    extra=[]
    for mp in sorted({r['map'] for r in results}):
        row=dict(map=mp)
        for team in (545,87,1119):
            rs=[(r,s) for r in results if not r['extra'] and r['map']==mp for s,t in enumerate(r['teams']) if t==team]
            row[str(team)]=dict(n=len(rs),mean_lead=sum(r['pearls100'][s].get('pearls',0)-r['pearls100'][1-s].get('pearls',0) for r,s in rs)/len(rs) if rs else None)
        er=[(r,r['teams'].index(545)) for r in results if r['extra'] and r['map']==mp]
        row['545_other']=dict(n=len(er),opponents=sorted({r['teams'][1-s] for r,s in er}),
            mean_lead=sum(r['pearls100'][s].get('pearls',0)-r['pearls100'][1-s].get('pearls',0) for r,s in er)/len(er) if er else None,
            games=[r['gid'] for r,s in er])
        extra.append(row)
    dump('summary.json',dict(groups=rows,recurrence=recurrences,map_leads=extra,
         validation=dict(games=len(results),turns=sum(sum(c['turns'] for c in r['counts']) for r in results),
                         updates=sum(r['checks']['updates'] for r in results))))
    dump('misses.json',{str(k):v for k,v in passby.items()})
    print(json.dumps([dict((k,v) for k,v in r.items() if k!='first_meals') for r in rows],indent=2),flush=True)


def main():
    mode=sys.argv[1] if len(sys.argv)>1 else 'all'
    if mode=='all':
        jobs=inventory()
        support=build_support(jobs)
    else:
        jobs=json.loads((OUT/'jobs.json').read_text())
        support={k:set(v) for k,v in json.loads((OUT/'support.json').read_text())['tiles'].items()}
    if mode!='aggregate':
        with (OUT/'results.jsonl').open('w') as f:
            for n,j in enumerate(jobs):
                r=scan(j,support)
                f.write(json.dumps(r,separators=(',',':'))+'\n')
                f.flush()
                if n%10==0:
                    print('scan',n,'/',len(jobs),flush=True)
    results=[json.loads(s) for s in (OUT/'results.jsonl').read_text().splitlines()]
    pairs=compare(results)
    aggregate(results,pairs)


if __name__=='__main__':
    main()
