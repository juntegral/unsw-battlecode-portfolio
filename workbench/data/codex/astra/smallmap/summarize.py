"""Generate inspectable tables from analyze.py output."""
import json,csv
from pathlib import Path
from collections import Counter,defaultdict
from statistics import mean,median

OUT=Path(__file__).resolve().parent
G=json.loads((OUT/'games.json').read_text())
L=[g for g in G if g['result']=='loss']

def snapshot(g,r):
    return g['snapshots'][str(min(r,g['last_round']))]

def writecsv(name,rows):
    if not rows:return
    with (OUT/name).open('w') as f:
        w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)

curves=[]; pergame=[]; deaths=[]; collisions=[]; deficit=[]; drops=[]
for g in L:
    base=dict(gid=g['gid'],build=g['build'],label=g['label'],opponent=g['opponent'],map=g['map'],end=g['last_round'])
    curve=base.copy()
    for r in range(0,151,10):
        snap=snapshot(g,r)
        curve[f'r{r}']=f"{snap['us']['alive']}/{snap['them']['alive']}"
    curves.append(curve)
    row=base.copy()
    ds=[d for d in g['deaths'] if d['side']=='us' and d['round']<=150]
    for cause in ('rammed','rams','mate_head','wall','self','mate_body','enemy_body','unpaid sprint','illegal split','no action','timeout'):
        row[cause]=sum(d['category']==cause for d in ds)
    row['postsplit_boxed_proxy']=sum(d['postsplit_boxed_proxy'] for d in ds)
    for side in ('us','them'):
        cs=[c for c in g['collisions'] if c['cross_team'] and c['round']<=150 and c['side']==side and c['pre_counts']['us']<c['pre_counts']['them']]
        row[f'{side}_starts_us_behind']=len(cs)
        for s in ('us','them'):
            row[f'{side}_starts_lost_{s}']=sum(c['lengths'][s] for c in cs)
            row[f'{side}_starts_recovered5_{s}']=sum(c['recovered5'][s] for c in cs)
            row[f'{side}_starts_net5_{s}']=sum(c['direct_net5'][s] for c in cs)
            row[f'{side}_starts_mean_board_delta5_{s}']=mean(c['board_delta5'][s] for c in cs) if cs else None
        row[f'{side}_censored5']=sum(not c['window_complete'] for c in cs)
    pergame.append(row)
    for d in ds:
        t=d['turn'];deaths.append(dict(**base,round=d['round'],id=d['id'],length=d['length'],cause=d['category'],
               actor=d['actor'],actor_start_length=t['L0'],board_us=t['counts']['us'],board_them=t['counts']['them'],
               actor_view_us=t['view']['us'],actor_view_them=t['view']['them'],free_exits=d['free_exits'],
               since_split=d['since_split'],age=d['age'],postsplit_boxed_proxy=d['postsplit_boxed_proxy'],event=d['event']))
    for c in g['collisions']:
        if not c['cross_team'] or c['round']>150:continue
        for p in c['drops']:
            drops.append(dict(**base,collision=c['collision'],round=c['round'],initiator=c['side'],
                              pearl=p['pearl'],dead_id=p['dragon'],dead_side=p['drop_side'],xy=p['xy'],
                              nearest_us=p['near_at_collision']['us'],nearest_them=p['near_at_collision']['them'],
                              eater=p['eater'],eater_id=p['eater_id'],eat_round=p['eat_round'],wait=p['wait'],
                              eaten_within5=p['eater']!='nobody' and p['wait']<=5))
        t=c['turn'];collisions.append(dict(**base,round=c['round'],actor=c['actor'],side=c['side'],victim=c['victim'],
            us_L=c['lengths']['us'],them_L=c['lengths']['them'],actor_L0=t['L0'],
            board_us=c['pre_counts']['us'],board_them=c['pre_counts']['them'],view_us=t['view']['us'],view_them=t['view']['them'],
            target_visible_parts=t['visible_parts'].get(str(c['victim']),0),
            trade_even_geometry=c['trade_even_geometry'],hunt_small_geometry=c['hunt_small_geometry'],
            near_us=c['nearest_head']['us'],near_them=c['nearest_head']['them'],
            recovered5_us=c['recovered5']['us'],recovered5_them=c['recovered5']['them'],
            direct_net5_us=c['direct_net5']['us'],direct_net5_them=c['direct_net5']['them'],
            board_delta5_us=c['board_delta5']['us'],board_delta5_them=c['board_delta5']['them'],window_complete=c['window_complete']))
    before,after=snapshot(g,30),snapshot(g,100)
    row=base.copy()
    for s in ('us','them'):
        row[f'count30_{s}']=before[s]['alive'];row[f'count100_{s}']=after[s]['alive']
        row[f'splits31_100_{s}']=sum(d['side']==s and 30<d['round']<=100 for d in g['splits'])
        row[f'deaths31_100_{s}']=sum(d['side']==s and 30<d['round']<=100 for d in g['deaths'])
        assert row[f'count100_{s}']-row[f'count30_{s}']==row[f'splits31_100_{s}']-row[f'deaths31_100_{s}']
    row['gap_change']=(after['them']['alive']-after['us']['alive'])-(before['them']['alive']-before['us']['alive'])
    row['split_gap']=row['splits31_100_them']-row['splits31_100_us']
    row['death_gap']=row['deaths31_100_us']-row['deaths31_100_them']
    assert row['gap_change']==row['split_gap']+row['death_gap']
    deficit.append(row)

for name,rows in [('count-curves.csv',curves),('per-game.csv',pergame),('deaths.csv',deaths),('collisions.csv',collisions),('count-ledger.csv',deficit),('drops.csv',drops)]:writecsv(name,rows)

def summary(gs):
    cs=[(g,c) for g in gs for c in g['collisions'] if c['cross_team'] and c['round']<=150]
    out=dict(games=len(gs),by_build=dict(Counter(g['build'] for g in gs)),by_group=dict(Counter(g['label'] for g in gs)),
             eliminated=sum(g['final']['us']['alive']==0 for g in gs),
             curves={r:{s:mean(snapshot(g,r)[s]['alive'] for g in gs) for s in ('us','them')} for r in range(0,151,10)},
             deaths=dict(Counter(d['category'] for g in gs for d in g['deaths'] if d['side']=='us' and d['round']<=150)),
             postsplit_boxed_proxy=sum(d['postsplit_boxed_proxy'] for g in gs for d in g['deaths'] if d['side']=='us' and d['round']<=150))
    out['behind_collisions']={}
    for who in ('us','them'):
        selected=[(g,c) for g,c in cs if c['side']==who and c['pre_counts']['us']<c['pre_counts']['them']]
        out['behind_collisions'][who]=dict(n=len(selected),games=len(set(g['gid'] for g,c in selected)),
            lost={s:sum(c['lengths'][s] for g,c in selected) for s in ('us','them')},
            recovered5={s:sum(c['recovered5'][s] for g,c in selected) for s in ('us','them')},
            direct_net5={s:sum(c['direct_net5'][s] for g,c in selected) for s in ('us','them')},
            mean_board_delta5={s:mean(c['board_delta5'][s] for g,c in selected) if selected else None for s in ('us','them')},
            equal=sum(c['equal_at_impact'] for g,c in selected),
            trade_geometry=sum(c['trade_even_geometry'] for g,c in selected),
            hunt_geometry=sum(c['hunt_small_geometry'] for g,c in selected),
            censored=sum(not c['window_complete'] for g,c in selected))
    out['opportunities']={}
    for s in ('us','them'):
        for bal in ('behind','equal','ahead'):
            es=[e for g in gs for e in g['encounters'] if e['side']==s and e['balance']==bal]
            out['opportunities'][f'{s}_{bal}']=dict(n=len(es),taken=sum(e['rammed'] for e in es))
    out['opportunities_stratified']={}
    for opponent in sorted({g['opponent'] for g in gs}):
        for band,lo,hi in [('0-30',0,30),('31-100',31,100),('101-150',101,150)]:
            for bal in ('behind','equal','ahead'):
                es=[e for g in gs if g['opponent']==opponent for e in g['encounters'] if e['side']=='them' and e['balance']==bal and 2<=e['length']<=4 and lo<=e['round']<=hi]
                out['opportunities_stratified'][f'{opponent}|{band}|L2-4|{bal}']=dict(n=len(es),taken=sum(e['rammed'] for e in es))
    distance=defaultdict(Counter)
    for g,c in cs:
        for p in c['drops']:
            d=p['near_at_collision'];near='us' if d['us']<d['them'] else 'them' if d['them']<d['us'] else 'tie'
            k=distance[near];k['drops']+=1;k[p['eater'] if p['wait']<=5 and p['eater']!='nobody' else 'uneaten5']+=1
    out['drop_distance']={k:dict(v) for k,v in distance.items()}
    cards={}
    for kind in ('equal_behind','equal_behind_no_nearer','equal_view_behind','equal_us_lt8'):
        selected=[]
        for g,c in cs:
            if c['side']!='us' or not c['equal_at_impact'] or c['turn']['L0']>4 or c['actor']<=1:continue
            if kind.startswith('equal_behind') and c['pre_counts']['us']>=c['pre_counts']['them']:continue
            if kind=='equal_behind_no_nearer' and c['nearest_head']['us']<c['nearest_head']['them']:continue
            if kind=='equal_view_behind' and c['turn']['view']['us']>=c['turn']['view']['them']:continue
            if kind=='equal_us_lt8' and c['pre_counts']['us']>=8:continue
            selected.append((g,c))
        cards[kind]=dict(n=len(selected),games=len({g['gid'] for g,c in selected}),
                        lost={s:sum(c['lengths'][s] for g,c in selected) for s in ('us','them')},
                        recovered5={s:sum(c['recovered5'][s] for g,c in selected) for s in ('us','them')},
                        moments=[dict(gid=g['gid'],round=c['round'],actor=c['actor'],lengths=c['lengths'],counts=c['pre_counts'],near=c['nearest_head'],recovered5=c['recovered5']) for g,c in selected])
    out['candidate_filters']=cards
    return out

S=dict(all=summary(G),loss=summary(L),groups={key:summary([g for g in L if g['label']==key]) for key in sorted({g['label'] for g in L})},
       count_ledger={k:sum(r[k] for r in deficit) for k in ('gap_change','split_gap','death_gap','splits31_100_us','splits31_100_them','deaths31_100_us','deaths31_100_them')})
(OUT/'summary.json').write_text(json.dumps(S,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in S.items() if k!='groups'},ensure_ascii=False,indent=2))
