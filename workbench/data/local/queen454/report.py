#!/usr/bin/env python3
"""Generate the English brief and fully stratified numerical tables from rows.json."""
import json,statistics,collections
from pathlib import Path
from datetime import datetime,timezone,timedelta
OUT=Path(__file__).resolve().parent
ROWS=json.loads((OUT/'rows.json').read_text())
GROUPS=('aAah','ours','38 off','38 on')
PHASES=('1-100','101-300','301-500')
CAUSES=('enemy head','wall','own body','dropped with no action','other')
def avg(x):
    x=[v for v in x if v is not None]
    return dict(mean=statistics.mean(x) if x else None,median=statistics.median(x) if x else None,n=len(x))
def ratio(a,n):return dict(count=a,n=n,share=a/n if n else None)
def aggregate(rs,ph=None):
    phases=(ph,) if ph else PHASES
    ini=collections.Counter();ps=[r['phases'][p] for r in rs for p in phases]
    for p in ps:ini.update(p['initiative'])
    ss=[s for r in rs for s in r['samples'] if s['phase'] in phases]
    ww=[w for r in rs for w in r['windows'] if w['phase'] in phases]
    deaths=[r['death'] for r in rs if r['death'] and (('1-100' if r['death']['round']<=100 else '101-300' if r['death']['round']<=300 else '301-500') in phases)]
    es=[e for r in rs for e in r['events'] if e['phase'] in phases];hd=[e for e in es if e['kind']=='head-on'];kills=[e for e in es if e['kind']=='queen kill']
    survival=ratio(sum(r['alive_end'] for r in rs),len(rs))
    if ph:
        end={'1-100':100,'101-300':300,'301-500':500}[ph]
        at=[r for r in rs if r['rounds']>=end]
        survival=ratio(sum(r['death'] is None or r['death']['round']>end for r in at),len(at))
    behind=[s['ahead'] for s in ss if s['ahead'] is not None]
    out=dict(games=len(rs),battles=len(set(str(r['battle']) for r in rs)),survival=survival,death_round=avg([d['round'] for d in deaths]),deaths=dict(collections.Counter(d['cause'] for d in deaths)),
        initiative=dict(ini),kills=len(kills),kill_methods=dict(collections.Counter(e['method'] for e in kills)),headons=len(hd),headons_queen_mover=sum(e['queen_moved_first'] for e in hd),
        teammate_ahead=ratio(sum(v>0 for v in behind),len(behind)),teammates_ahead=avg(behind),centre_distance=avg([s['centre_distance'] for s in ss]),nearest_teammate=avg([s['nearest_teammate'] for s in ss]),start_distance=avg([s['start_distance'] for s in ss]),
        unique_tiles50=avg([w['unique_tiles'] for w in ww]),net50=avg([w['net_displacement'] for w in ww]),bbox50_width=avg([w['bbox'][0] for w in ww]),bbox50_height=avg([w['bbox'][1] for w in ww]),
        loop2=ratio(sum(p['loop2'] for p in ps),sum(p['loop_eligible'] for p in ps)),loop3=ratio(sum(p['loop3'] for p in ps),sum(p['loop_eligible'] for p in ps)),
        pearls=avg([sum(r['phases'][p]['pearls'] for p in phases) for r in rs]),splits=avg([sum(r['phases'][p]['splits'] for p in phases) for r in rs]),splits_after200=avg([r['splits_after200'] for r in rs]),
        lengths={},ground={},previous5={},queen_rule=dict(n=0,our_length=None,opponent_length=None))
    for mark in (100,200,300,400,500):
        p='1-100' if mark<=100 else '101-300' if mark<=300 else '301-500'
        if p in phases:
            out['lengths'][str(mark)]=avg([r['lengths'][str(mark)] for r in rs])
            if mark!=500:out['ground'][str(mark)]=avg([r['ground'].get(str(mark),{}).get('share') for r in rs])
    for kind in ('queen kill','death'):
        ev=[e for e in es if e['kind']==kind];use=[e for e in ev if e['enemy_id'] is not None]
        out['previous5'][kind]=dict(n=len(ev),with_enemy=len(use),first_closer=dict(collections.Counter(e['previous5']['first_closer'] for e in use)),
                                  queen_net=avg([e['previous5']['queen'] for e in use]),enemy_net=avg([e['previous5']['enemy'] for e in use]))
    qr=[r for r in rs if r['queen_rule_decided']] if ph in (None,'301-500') else []
    out['queen_rule']=dict(n=len(qr),our_length=avg([r['final_lengths'][0] for r in qr]),opponent_length=avg([r['final_lengths'][1] for r in qr]),pairs=[[r['game'],*r['final_lengths']] for r in qr])
    return out
STATS={g:{size:{p:aggregate([r for r in ROWS if r['group']==g and (size=='all' or r['size']==size)],None if p=='all' else p) for p in ('all',)+PHASES} for size in ('all','<=600','>600')} for g in GROUPS}
(OUT/'strata.json').write_text(json.dumps(STATS,indent=2)+'\n')
A={g:STATS[g]['all']['all'] for g in GROUPS}
def f(x,d=1):return 'NA' if x is None else f'{x:.{d}f}'
def pct(r):return f"{f(100*r['share'])}% ({r['count']}/{r['n']})" if r['share'] is not None else 'NA (n=0)'
def mean(r,percent=False):return f"{f(r['mean']*100 if percent and r['mean'] is not None else r['mean'])}{'%' if percent else ''} (n={r['n']})"
def cell(fn):return [fn(A['aAah']),fn(A['ours']),fn(A['38 off'])+' → '+fn(A['38 on'])]
def table(label,fn):return '| '+label+' | '+' | '.join(cell(fn))+' |'
def initiative(a):
    n=a['initiative'].get('steps',0);s=a['initiative'].get('shorten',0);l=a['initiative'].get('lengthen',0)
    return f'{f(100*s/n) if n else "NA"}/{f(100*l/n) if n else "NA"}% (n={n})'
def closers(a,kind):
    d=a['previous5'][kind];c=d['first_closer'];return f"{c.get('queen',0)}/{c.get('enemy',0)}/{c.get('neither',0)} (n={d['with_enemy']})"
def stratum(a):
    return f"{a['games']}; {initiative(a)}; {pct(a['teammate_ahead'])}; {pct(a['loop3'])}"
pairs={}
for r in ROWS:
    if r['group'].startswith('38 '):pairs.setdefault(r['pair'],{})[r['group']]=r
PAIR={}
for t in ('100','200','300','400'):
    ds=[p['38 on']['ground'][t]['share']-p['38 off']['ground'][t]['share'] for p in pairs.values() if all(t in p[g]['ground'] for g in ('38 off','38 on'))]
    PAIR[t]=dict(**avg(ds),lower=sum(d<0 for d in ds),higher=sum(d>0 for d in ds),equal=sum(d==0 for d in ds))
(OUT/'paired-ground.json').write_text(json.dumps(PAIR,indent=2)+'\n')
DATES={g:sorted(r['time'] for r in ROWS if r['group']==g and r['time']) for g in GROUPS}
SIDES={g:dict(collections.Counter(r['side'] for r in ROWS if r['group']==g)) for g in GROUPS}
def dates(g):
    return DATES[g][0][:16].replace('T',' ')+' to '+DATES[g][-1][:16].replace('T',' ')+' UTC'
report=[f"aAah (team 454; no nAah in the full leaderboard): {A['aAah']['games']} games, sides {SIDES['aAah']}; {dates('aAah')}.",
        f"Ours, meow (1119), same-code versions 44/47: {A['ours']['games']} games, sides {SIDES['ours']}; {dates('ours')}.",
        '#38 attempt 2: 16 paired games per arm (off → on), local replays created 6–7 Oct 2026 KST; comparison opponent is a local bot.',
        '',
        'All distances are wrapped Manhattan tile distances unless stated. Rounds are 1–500; raw replay rounds are 0–499. n means games, steps, samples or windows as named.',
        'Ground = fraction of tiles with an open edge closest by legal walking distance to friendly heads; walls/portals respected, bodies ignored, ties half, unreachable by both unclaimed.',
        'Behind = at least one teammate nearer to the enemy head nearest the queen; sampled every 10 completed rounds while she lives. Centre uses the circular mean of friendly heads.',
        'A small loop needs a closed path through ≥4 distinct tiles within a trailing 8-round box; loop 3 includes loop 2. Stationary queens do not count. First 7 rounds excluded.',
        'Travel windows are complete, non-overlapping 50-round blocks with a living queen. Box = smallest wrapped width × height. Early-ended games are absent from later checkpoints; dead queens count as length 0.',
        '',
        '| Number | aAah | Ours v44/47 | #38 off → on |','|---|---|---|---|',
        table('Alive at end / games',lambda a:pct(a['survival'])),
        table('Death round, mean / deaths',lambda a:mean(a['death_round'])),
        table('Deaths: enemy head / wall / own body / no action / other',lambda a:'/'.join(str(a['deaths'].get(c,0)) for c in CAUSES)+f" (n={sum(a['deaths'].values())})"),
        table('Visible-enemy steps: closer / farther',initiative),
        table('Queen kills / head-on hits (queen moving)',lambda a:f"{a['kills']} / {a['headons']} ({a['headons_queen_mover']}); n={a['games']} games"),
        table('Before kills: first closer queen / enemy / neither',lambda a:closers(a,'queen kill')),
        table('Before deaths: first closer queen / enemy / neither',lambda a:closers(a,'death')),
        table('At least one teammate ahead / samples',lambda a:pct(a['teammate_ahead'])),
        table('Teammates ahead, mean / samples',lambda a:mean(a['teammates_ahead'])),
        table('Distance to centre / nearest teammate / start, means',lambda a:' / '.join(mean(a[k]) for k in ('centre_distance','nearest_teammate','start_distance'))),
        table('Unique tiles / net displacement per 50 rounds, means',lambda a:mean(a['unique_tiles50'])+' / '+mean(a['net50'])),
        table('50-round box, mean width × height / windows',lambda a:f"{f(a['bbox50_width']['mean'])} × {f(a['bbox50_height']['mean'])} (n={a['bbox50_width']['n']})"),
        table('Loop 2×2 / ≤3×3 / eligible living rounds',lambda a:pct(a['loop2'])+' / '+pct(a['loop3'])),
        table('Ground r100 / 200 / 300 / 400, means',lambda a:'; '.join(mean(a['ground'][t],True) for t in ('100','200','300','400'))),
        table('Queen length r100 / 200 / 300 / 400 / 500, means',lambda a:'; '.join(mean(a['lengths'][t]) for t in ('100','200','300','400','500'))),
        table('Pearls eaten / splits after r200, mean per game',lambda a:mean(a['pearls'])+' / '+mean(a['splits_after200'])),
        table('Queen-rule endings; mean own : opposing length',lambda a:f"{a['queen_rule']['n']}/{a['games']}; {f(a['queen_rule']['our_length']['mean'])} : {f(a['queen_rule']['opponent_length']['mean'])}"),
        '| Phase × area: games; closer/farther; behind; loop ≤3×3 | | | |']
for size in ('<=600','>600'):
    for p in PHASES:
        vals={g:STATS[g][size][p] for g in GROUPS}
        report.append('| '+p+'; '+size+' tiles | '+stratum(vals['aAah'])+' | '+stratum(vals['ours'])+' | '+stratum(vals['38 off'])+' → '+stratum(vals['38 on'])+' |')
report+=['',
         'All requested numbers, including deaths, lengths, ground, travel and five-round approach credits, are also split by phase × area in strata.json; rows.json retains each game and encounter.',
         'Visible-enemy steps include executed steps and the attempted fatal step, comparing the same visible enemy-head set before/after. Walls are not traversed. Closer is movement, not intent.',
         'Before-kill/death counts use the previous five completed rounds and the first positive distance reduction against that specific head. Queen kills include her rams and enemies hitting her body; mutual head hits are separate.',
         'For wall/self/no-action deaths, the paired head is the nearest remaining enemy (not a claimed cause). Positive/negative net approach credits and the exact pairs are in rows.json.',
         '',
         'Measured',
         f"(a) ‘Their queen does not engage first’: not established. aAah closer/farther steps are {initiative(A['aAah'])}; she is the moving head in {A['aAah']['headons_queen_mover']}/{A['aAah']['headons']} head-on hits. These measure actions, not intent.",
         f"(b) ‘Mostly among or behind teammates’: supported by the stated position proxy in {pct(A['aAah']['teammate_ahead'])} of samples; ours {pct(A['ours']['teammate_ahead'])}. This is relative to one nearest enemy, not a battle line.",
         f"(c) ‘She does not circle’: not literally true; aAah spends {pct(A['aAah']['loop3'])} of eligible living rounds in a ≤3×3 loop, versus ours {pct(A['ours']['loop3'])} and #38 on {pct(A['38 on']['loop3'])}.",
         "(d) ‘Our circling queen holds less ground’: paired #38 on-minus-off changes at r100/200/300/400 are "+'; '.join(f"{f(100*PAIR[t]['mean'])} percentage points ({PAIR[t]['lower']} lower/{PAIR[t]['n']} pairs)" for t in ('100','200','300','400'))+'. This small local sample cannot establish a general causal effect.',
         '',
         'Read, not tested',
         'The observations can motivate testing queen placement behind active teammates; they do not identify an opponent policy or prove a survival benefit.',
         'Queen movement and team ground can share causes: teammate population, opponent pressure, map geometry, and the survival of either queen.',
         '',
         'Limits',
         f"aAah: {A['aAah']['games']} games from {A['aAah']['battles']} series, recent and clustered; ours {A['ours']['games']} from {A['ours']['battles']} series. Games within a series are not independent.",
         'Opponent ratings (mean/min/max; ≥2000 games): '+ '; '.join(g+' '+f(statistics.mean([r['opponent_rating'] for r in ROWS if r['group']==g]))+'/'+str(min(r['opponent_rating'] for r in ROWS if r['group']==g))+'/'+str(max(r['opponent_rating'] for r in ROWS if r['group']==g))+f"; {sum(r['opponent_rating']>=2000 for r in ROWS if r['group']==g)}/{A[g]['games']}" for g in ('aAah','ours'))+'. This is not a matched ladder comparison.',
         'aAah submission IDs are hidden in public replays/API, so version changes could not be identified. Our v44/v47 labels come from the existing ladder ledger. #38 attempt 2 is a separate local experiment.',
         'True replay positions include enemies/teammates outside the queen’s view; only the initiative filter uses her 7×7 view. Geometric distances ignore walls; ground walking distances do not.',
         'Loops larger than 3×3 or with interruptions can be missed; centre can be undefined for a perfectly balanced wrap-around distribution. Ground is a head-distance proxy, not possession or reachable moves through bodies.',
         'All final body counts/lengths were checked against replay result fields; our 370 queen outcomes, death rounds, pearls and split totals match the existing ladder ledger. No games were run or requested; no submission or post was made.'
]
assert len(report)<=80,len(report)
(OUT/'summary.md').write_text('\n'.join(report)+'\n')
print('summary lines',len(report))
print('\n'.join(report[report.index('Measured'):report.index('Read, not tested')]))
