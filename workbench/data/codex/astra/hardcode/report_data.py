#!/usr/bin/env python3
"""Readable audit tables and independently checked supporting counts."""
import sys
sys.dont_write_bytecode = True
import csv
import gzip
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
import analyze as a

O = Path(__file__).resolve().parent
results = [json.loads(s) for s in (O/'results.jsonl').read_text().splitlines()]
pairs = json.loads((O/'pairs.json').read_text())
summary = json.loads((O/'summary.json').read_text())
jobs = json.loads((O/'jobs.json').read_text())
byid = {r['gid']: r for r in results}
jobid = {j['meta']['id']: j for j in jobs}
names = {545:'dev',87:'WHQ',1119:'우리'}


def tsv(name, fields, rows):
    with (O/name).open('w') as f:
        w = csv.DictWriter(f, fields, delimiter='\t')
        w.writeheader()
        for row in rows:
            w.writerow({k: json.dumps(row[k], ensure_ascii=False) if isinstance(row[k],(list,dict)) else row[k]
                        for k in fields})


def xy(r, c):
    return f'({c%r["w"]},{c//r["w"]})'


def orient(gid, team):
    s = byid[gid]['teams'].index(team)
    with gzip.open(O/f'turns-{gid}.json.gz','rt') as f:
        recs = json.load(f)[s]
    return min(x['id'] for x in recs if x['r']==0)


orientation = {(r['gid'],team): orient(r['gid'],team)
               for r in results if not r['extra'] for team in r['teams']}
for p in pairs:
    p['queen_id'] = orientation[p['games'][0],p['team']]
tsv('pair-divergences.tsv', ['team','map','side','queen_id','games','labels','first',
                           'same_turns_before','changed_view_turns_before_or_at','changed_view_same_path'],pairs)

lineage_rows = []
for p in pairs:
    side = 'AB'.index(p['side'])
    maps = []
    for gid in p['games']:
        with gzip.open(O/f'turns-{gid}.json.gz','rt') as f:
            recs = json.load(f)[side]
        d = defaultdict(dict)
        for x in recs:
            d[x['lineage']][x['r']] = x
        maps.append(d)
    for lin in sorted(set(maps[0]) | set(maps[1])):
        left,right = maps[0].get(lin,{}),maps[1].get(lin,{})
        first = None
        for rnd in sorted(set(left)|set(right)):
            x,y = left.get(rnd),right.get(rnd)
            if x is None or y is None:
                first = dict(r=rnd,kind='birth/death',view=['unmatched'])
                break
            if (x['h'],x['path'],x['split'],x['died']) != (y['h'],y['path'],y['split'],y['died']):
                first = dict(r=rnd,kind='path',view=[k for k in x['view'] if x['view'][k]!=y['view'][k]],
                             ids=[x['id'],y['id']],heads=[x['h'],y['h']],paths=[x['path'],y['path']])
                break
        lineage_rows.append(dict(team=p['team'],map=p['map'],queen_id=p['queen_id'],games=p['games'],lineage=lin,first=first))
tsv('dragon-divergences.tsv',['team','map','queen_id','games','lineage','first'],lineage_rows)

meals = []
for r in results:
    for s,t in enumerate(r['teams']):
        m = r['first_meal'][s]
        meals.append(dict(gid=r['gid'],label=r['label'],map=r['map'],team=t,side='AB'[s],
                          r=m['r'] if m else None,dragon=m['dragon'] if m else None,
                          tile=xy(r,m['tile']) if m else None,d=m['distance'] if m else None,
                          first_source_seen=m['first_source_seen'] if m else None,
                          lineage=m['lineage'] if m else None))
tsv('first-meals.tsv', list(meals[0]), meals)

misses = json.loads((O/'misses.json').read_text())
recurrence = []
summary3 = []
visible_events = {}
for team in (545,87,1119):
    all_events = misses[str(team)]
    events = [x for x in all_events if set(x['pearls']) & set(x['visible_adjacent'])]
    visible_events[team] = events
    tiles = defaultdict(list)
    for x in events:
        for c in set(x['pearls']) & set(x['visible_adjacent']):
            tiles[x['map'],x['side'],c].append(x)
    for (mp,s,c),xs in sorted(tiles.items()):
        recurrence.append(dict(team=team,map=mp,side='AB'[s],tile=xy(xs[0],c),
                               n_games=len({x['gid'] for x in xs}),games=sorted({x['gid'] for x in xs}),
                               events=len(xs),moments=[[x['gid'],x['r'],x['dragon']] for x in xs]))
    trs = [x for x in recurrence if x['team']==team]
    counts = Counter()
    for r in results:
        if not r['extra'] and team in r['teams']:
            counts.update(r['counts'][r['teams'].index(team)])
    summary3.append(dict(team=team,counts=dict(counts),unique_tiles=len(trs),
                         repeated_tiles=sum(x['n_games']>=2 for x in trs),
                         games4_tiles=sum(x['n_games']>=4 for x in trs),
                         clean=sum(not x['split'] and not x['died'] and not x['other_meals'] and
                                   not x['foe3'] and len(x['pearl_view'])==1 and x['first'] is not None for x in events)))
tsv('missed-tiles.tsv',['team','map','side','tile','n_games','games','events','moments'],recurrence)

recindex = {(x['team'],x['map'],x['side'],x['tile']): x for x in recurrence}
clean = [x for x in visible_events[545] if not x['split'] and not x['died'] and not x['other_meals'] and
         not x['foe3'] and len(x['pearl_view'])==1 and x['first'] is not None]
for x in clean:
    c = next(iter(set(x['pearls'])&set(x['visible_adjacent'])))
    x['tile_xy'] = xy(x,c)
    x['recurrence'] = recindex[545,x['map'],'AB'[x['side']],x['tile_xy']]
clean.sort(key=lambda x:(-x['recurrence']['n_games'],x['r'],x['gid']))
selected, used_tiles, used_games = [],set(),set()
for x in clean:
    key=(x['map'],x['tile_xy'])
    if key in used_tiles or x['gid'] in used_games:
        continue
    selected.append(x)
    used_tiles.add(key)
    used_games.add(x['gid'])
    if len(selected)==10:
        break
a.dump('clearest-ten.json',selected)

blind_maps=[]
for team in (545,87,1119):
    z=defaultdict(lambda:dict(n=0,toward=0,expected=0,rounds=[],games=set()))
    for r in results:
        if r['extra'] or team not in r['teams']:
            continue
        side=r['teams'].index(team)
        for x in r['blind']:
            if x['side']!=side:
                continue
            v=z[r['map']];v['n']+=1;v['toward']+=x['d1']<x['d0'];v['expected']+=x['expected']
            v['rounds'].append(x['r']);v['games'].add(x['gid'])
    for mp,v in z.items():
        blind_maps.append(dict(team=team,map=mp,**{k:value for k,value in v.items() if k!='games'},games=sorted(v['games'])))
a.dump('details.json',dict(test3=summary3,blind_maps=blind_maps,orientation={f'{k[0]}:{k[1]}':v for k,v in orientation.items()}))

lines=[]
for t in (545,87,1119):
    ps=[p for p in pairs if p['team']==t]
    lines.append(f'{names[t]} pairs={len(ps)}, median first r={median(p["first"]["r"] for p in ps)}, '
                 f'first view={dict(Counter(str(p["first"]["view"]) for p in ps))}, '
                 f'changed view / same path before first={sum(p["changed_view_same_path"] for p in ps)}')
for x in summary3:
    c=x['counts']
    lines.append(f'{names[x["team"]]} visible={c["visible_miss_turns"]}/{c["visible_adjacent_turns"]}, '
                 f'none taken={c["visible_none_taken"]}, tiles={x["repeated_tiles"]}/{x["unique_tiles"]}, '
                 f'>=4games={x["games4_tiles"]}, clean={x["clean"]}')
for x in selected:
    lines.append(f'{x["map"]} {x["gid"]} r{x["r"]} #{x["dragon"]} '
                 f'{xy(x,x["head"])}->{[xy(x,c) for c in x["path"]]} pearl={x["tile_xy"]} '
                 f'recurrence={x["recurrence"]["n_games"]}/4')
(O/'table-notes.txt').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))
