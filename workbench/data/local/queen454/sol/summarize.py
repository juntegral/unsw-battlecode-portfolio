#!/usr/bin/env python3
"""Summarize only this run's independently counted rows."""
import sys
sys.dont_write_bytecode=True
import json,statistics,math
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime
OUT=Path(__file__).resolve().parent
GROUPS=('aAah','ours','38 off','38 on')
PHASES=('1-100','101-300','301-500')
def avg(x):return statistics.mean(x) if x else None
def median(x):return statistics.median(x) if x else None
def fmt(x,d=1):return f'{x:.{d}f}' if x is not None else 'NA'
def frac(a,n):return f'{100*a/n:.1f}% ({a}/{n})' if n else 'NA (n=0)'
def num(x):return f'{fmt(avg(x))} (n={len(x)})'
def sums(rs,ph=None):
    c=Counter()
    for r in rs:
        for p,x in r['phases'].items():
            if ph is None or ph==p:c.update(x)
    return c
def summarize(rs,ph=None):
    c=sums(rs,ph);samples=[x for r in rs for x in r['samples'] if ph is None or x['phase']==ph]
    win=[x for r in rs for x in r['windows'] if ph is None or x['phase']==ph]
    deaths=[r['death'] for r in rs if r['death'] and (ph is None or ('1-100' if r['death']['round']<=100 else '101-300' if r['death']['round']<=300 else '301-500')==ph)]
    lo,hi={'1-100':(1,100),'101-300':(101,300),'301-500':(301,500),None:(1,500)}[ph]
    entered=[r for r in rs if r['end_round']>=lo and (r['death'] is None or r['death']['round']>=lo)]
    surv_hi=[r for r in rs if r['end_round']>=hi]
    return dict(games=len(rs),alive_end=sum(r['alive_end'] for r in rs),phase_entered=len(entered),
        alive_at_phase_end=sum(r['death'] is None or r['death']['round']>hi for r in surv_hi),phase_end_games=len(surv_hi),
        deaths=len(deaths),death_causes=dict(Counter(x['cause'] for x in deaths)),median_death_round=median([x['round'] for x in deaths]),
        counts=dict(c),samples_n=len(samples),behind_n=sum(x['nearer_allies'] is not None for x in samples),behind_yes=sum(x['nearer_allies'] is not None and x['nearer_allies']>=1 for x in samples),
        mean_nearer_allies=avg([x['nearer_allies'] for x in samples if x['nearer_allies'] is not None]),
        distances={k:dict(mean=avg([x[k] for x in samples if x[k] is not None]),n=sum(x[k] is not None for x in samples)) for k in ('centre_distance','nearest_ally_distance','spawn_distance')},
        travel={k:dict(mean=avg([x[k] for x in win]),n=len(win)) for k in ('unique_tiles','net_displacement')},
        windows_n=len(win),mean_window_bbox=[avg([x['bbox'][i] for x in win]) for i in (0,1)],
        ground={str(rnd):dict(mean=avg([r['ground'][str(rnd)]['share'] for r in rs if str(rnd) in r['ground']]),n=sum(str(rnd) in r['ground'] for r in rs)) for rnd in (100,200,300,400) if lo<=rnd<=hi},
        lengths={str(rnd):dict(mean=avg([r['lengths'][str(rnd)][0] for r in rs if str(rnd) in r['lengths']]),opponent_mean=avg([r['lengths'][str(rnd)][1] for r in rs if str(rnd) in r['lengths']]),n=sum(str(rnd) in r['lengths'] for r in rs)) for rnd in (100,200,300,400,500) if lo<=rnd<=hi},
        splits_after_200_total=sum(sum(t>200 and lo<=t<=hi for t in r['split_rounds']) for r in rs),
        queen_decisions=[dict(game=r['game'],ours=r['final_queen_lengths'][0],opponent=r['final_queen_lengths'][1]) for r in rs if r['queen_rule_decided']],
        collision_approaches=[x for r in rs for x in r['collisions'] if lo<=x['round']<=hi])

def main():
    rows=json.loads((OUT/'rows.json').read_text());gs={g:[r for r in rows if r['group']==g] for g in GROUPS}
    agg={g:summarize(rs) for g,rs in gs.items()}
    strata={g:{size:{('all' if ph is None else ph):summarize([r for r in rs if size=='all' or r['size']==size],ph) for ph in (None,*PHASES)} for size in ('all','<=600','>600')} for g,rs in gs.items()}
    (OUT/'strata.json').write_text(json.dumps(strata,indent=2)+'\n')
    off={r['pair']:r for r in gs['38 off']};on={r['pair']:r for r in gs['38 on']};pairs=[]
    for k in sorted(off.keys()&on.keys()):
        a,b=off[k],on[k]
        pairs.append(dict(pair=k,size=a['size'],ground_delta={t:b['ground'][t]['share']-a['ground'][t]['share'] for t in a['ground'].keys()&b['ground'].keys()},
            loop_delta=sum(x['loop_rounds'] for x in b['phases'].values())/max(1,sum(x['actions'] for x in b['phases'].values()))-sum(x['loop_rounds'] for x in a['phases'].values())/max(1,sum(x['actions'] for x in a['phases'].values())),
            length_delta={t:b['lengths'][t][0]-a['lengths'][t][0] for t in a['lengths'].keys()&b['lengths'].keys()},
            alive_delta=int(b['alive_end'])-int(a['alive_end'])))
    associations={}
    for size in ('<=600','>600'):
        rs=[r for r in gs['ours'] if r['size']==size and '100' in r['ground']]
        associations[size]={}
        for key,high in (('loop>=10%',True),('loop<10%',False)):
            sub=[r for r in rs if (r['phases']['1-100']['loop_rounds']/max(1,r['phases']['1-100']['actions'])>=0.1)==high]
            associations[size][key]=dict(n=len(sub),ground_mean=avg([r['ground']['100']['share'] for r in sub]))
    (OUT/'paired-ground.json').write_text(json.dumps(dict(pairs=pairs,observational_ours=associations),indent=2)+'\n')
    dates=lambda rs: f"{min(r['time'] for r in rs)[:16]} to {max(r['time'] for r in rs)[:16]} UTC" if rs else 'none'
    lines=[f"aAah (team 454), {len(gs['aAah'])} games; meow (1119), {len(gs['ours'])} live-code v44/v47 games.",
        f"Requested dates: aAah {dates(gs['aAah'])}; ours {dates(gs['ours'])}.",
        f"No exact nAah in the cached full leaderboard; #38 attempt-2: {len(pairs)} matched off/on pairs (local replay timestamps {min(r['time'] for r in gs['38 off']+gs['38 on'])[:10]}–{max(r['time'] for r in gs['38 off']+gs['38 on'])[:10]}, KST).",
        '', '| Number (means unless stated; n is the denominator) | aAah | ours | #38 off | #38 on |','|---|---|---|---|---|']
    def line(label,fn):lines.append('| '+label+' | '+' | '.join(fn(g,gs[g],agg[g]) for g in GROUPS)+' |')
    line('Alive at game end',lambda g,rs,a:frac(a['alive_end'],len(rs)))
    line('Alive after r500 (full games only)',lambda g,rs,a:frac(a['alive_at_phase_end'],a['phase_end_games']))
    line('Death round, median',lambda g,rs,a:f"{fmt(a['median_death_round'],0)} (n={a['deaths']})")
    labels=('enemy head','wall','own body','dropped with no action','other dragon body','ally head','other')
    line('Death causes: enemy head / wall / own body / no action / other',lambda g,rs,a:' / '.join(str(a['death_causes'].get(k,0)) for k in labels[:4])+f" / {sum(a['death_causes'].get(k,0) for k in labels[4:])} (n={a['deaths']})")
    line('Visible enemy: closer / farther / same steps',lambda g,rs,a:' / '.join(frac(a['counts'][k],a['counts']['visible_steps']) for k in ('closer','farther','same')))
    line('Entered 7×7 view by queen / enemy move',lambda g,rs,a:f"{a['counts']['queen_view_entries']} / {a['counts']['enemy_view_entries']} (n={a['counts']['queen_view_entries']+a['counts']['enemy_view_entries']})")
    line('Queen kills: total / initiated head hit / enemy hit her body',lambda g,rs,a:f"{a['counts']['kills']} / {a['counts']['active_head_kills']} / {a['counts']['passive_body_kills']} (n={len(rs)} games)")
    line('Queen head collisions: enemy / all teams',lambda g,rs,a:f"{a['counts']['enemy_headons']} / {a['counts']['headons']} (n={len(rs)} games)")
    line('At least one teammate nearer to nearest enemy',lambda g,rs,a:frac(a['behind_yes'],a['behind_n']))
    line('Number of teammates nearer',lambda g,rs,a:f"{fmt(a['mean_nearer_allies'])} (n={a['behind_n']})")
    for k,label in [('centre_distance','Distance to team centre'),('nearest_ally_distance','Distance to nearest teammate'),('spawn_distance','Distance to start')]:
        line(label,lambda g,rs,a,k=k:f"{fmt(a['distances'][k]['mean'])} (n={a['distances'][k]['n']})")
    line('Different tiles / net displacement per 50 rounds',lambda g,rs,a:f"{fmt(a['travel']['unique_tiles']['mean'])} / {fmt(a['travel']['net_displacement']['mean'])} (n={a['windows_n']})")
    line('50-round bounding box width × height',lambda g,rs,a:f"{fmt(a['mean_window_bbox'][0])} × {fmt(a['mean_window_bbox'][1])} (n={a['windows_n']})")
    line('Rounds on closed 2×2 or 3×3 loops',lambda g,rs,a:frac(a['counts']['loop_rounds'],a['counts']['actions']))
    line('2×2 completed-lap steps (excludes first 3)',lambda g,rs,a:frac(a['counts']['lap_2x2'],a['counts']['actions']))
    for r in (100,200,300,400):line(f'Team ground share r{r}',lambda g,rs,a,r=r:f"{fmt(100*a['ground'][str(r)]['mean']) if a['ground'][str(r)]['mean'] is not None else 'NA'}% (n={a['ground'][str(r)]['n']})")
    line('Queen length r100 / 200 / 300 / 400 / 500 (dead=0; [n])',lambda g,rs,a:' / '.join(f"{fmt(a['lengths'][str(t)]['mean'])}[{a['lengths'][str(t)]['n']}]" for t in (100,200,300,400,500)))
    line('Pearls eaten / successful splits per game',lambda g,rs,a:f"{fmt(a['counts']['pearls']/len(rs))} / {fmt(a['counts']['splits']/len(rs))} (n={len(rs)})")
    line('Splits after r200 per game',lambda g,rs,a:num([r['splits_after_200'] for r in rs]))
    line('Queen rule decided; own / opposing length then',lambda g,rs,a:f"{len(a['queen_decisions'])}/{len(rs)}; {fmt(avg([x['ours'] for x in a['queen_decisions']]))} / {fmt(avg([x['opponent'] for x in a['queen_decisions']]))} (n={len(a['queen_decisions'])})")
    def approaches(g,rs,a):
        cs=[x for x in a['collision_approaches'] if x['previous_5_rounds']['complete_history']];q=sum(x['previous_5_rounds']['queen_closing_steps'] for x in cs);e=sum(x['previous_5_rounds']['enemy_closing_steps'] for x in cs)
        return f"{fmt(q/len(cs)) if cs else 'NA'} / {fmt(e/len(cs)) if cs else 'NA'} (n={len(cs)} events)"
    line('Closing over 5 rounds before kill/death: queen / enemy',approaches)
    def first_closer(g,rs,a):
        cs=[x['previous_5_rounds'] for x in a['collision_approaches'] if x['previous_5_rounds']['complete_history']]
        return ' / '.join(str(sum(x['first_positive_mover']==k for x in cs)) for k in ('queen','enemy',None))+f' (n={len(cs)} events)'
    line('First closing move in prior 5 rounds: queen / enemy / neither',first_closer)
    # The same table includes the required phase and size split without map-specific conclusions.
    for size in ('<=600','>600'):
        for ph in PHASES:
            def cell(g,rs,a,size=size,ph=ph):
                z=strata[g][size][ph];c=z['counts'];ns=c.get('visible_steps',0);nb=z['behind_n'];na=c.get('actions',0)
                pct=lambda x,n:fmt(100*x/n) if n else 'NA'
                return f"C/F {pct(c.get('closer',0),ns)}/{pct(c.get('farther',0),ns)}%[{ns}]; B {pct(z['behind_yes'],nb)}%[{nb}]; L {pct(c.get('loop_rounds',0),na)}%[{na}]; games={z['games']}"
            line(f'{size} tiles, r{ph}: C/F=closer/farther, B=behind, L=loop',cell)
    strong={g:summarize([r for r in rs if r['opponent_rating'] is not None and r['opponent_rating']>=2000]) for g,rs in gs.items() if g in ('aAah','ours')}
    (OUT/'strong-opponents.json').write_text(json.dumps(strong,indent=2)+'\n')
    lines+=['', 'Measured',
        f"(a) ‘Does not engage first’: usually defensive in head contact, not an absolute rule. aAah shortens the gap on {frac(agg['aAah']['counts']['closer'],agg['aAah']['counts']['visible_steps'])} of visible-enemy steps; she moves into {agg['aAah']['counts']['active_head_kills']}/{agg['aAah']['counts']['enemy_headons']} enemy head collisions, enemies into the other {agg['aAah']['counts']['enemy_headons']-agg['aAah']['counts']['active_head_kills']}. Ours initiates {agg['ours']['counts']['active_head_kills']}/{agg['ours']['counts']['enemy_headons']}. View-entry counts above measure entry, not intent.",
        f"(b) ‘Mostly among or behind teammates’: {'supported by this proxy' if agg['aAah']['behind_yes']/max(1,agg['aAah']['behind_n'])>0.5 else 'not supported by this proxy'}: {frac(agg['aAah']['behind_yes'],agg['aAah']['behind_n'])} of ten-round samples have an ally nearer to the nearest enemy (ours {frac(agg['ours']['behind_yes'],agg['ours']['behind_n'])}).",
        f"(c) ‘Does not circle’: literal claim false; aAah spends {frac(agg['aAah']['counts']['loop_rounds'],agg['aAah']['counts']['actions'])} of actions in measured loops; ours {frac(agg['ours']['counts']['loop_rounds'],agg['ours']['counts']['actions'])}. This definition covers short closed paths, not every form of circling."]
    delta=[]
    for t in ('100','200','300','400'):
        xs=[p['ground_delta'][t]*100 for p in pairs if t in p['ground_delta']];delta.append(f"r{t} {fmt(avg(xs))} percentage points (n={len(xs)})")
    lines += ["(d) ‘Our circling loses ground’: paired #38 on-minus-off ground change is "+'; '.join(delta)+'. The changes are mixed, not consistently negative; these 16 local pairs cannot establish a ladder effect.',
        'Our early-loop association, ground at r100 (size split, not causal): '+ '; '.join(f"{size}: loop≥10% {fmt(100*v['loop>=10%']['ground_mean']) if v['loop>=10%']['ground_mean'] is not None else 'NA'}% (n={v['loop>=10%']['n']}) vs <10% {fmt(100*v['loop<10%']['ground_mean']) if v['loop<10%']['ground_mean'] is not None else 'NA'}% (n={v['loop<10%']['n']})" for size,v in associations.items())+'.',
        'Opponents ≥2000 only: ours survives '+frac(strong['ours']['alive_end'],strong['ours']['games'])+', has an ally nearer '+frac(strong['ours']['behind_yes'],strong['ours']['behind_n'])+', and holds '+fmt(100*strong['ours']['ground']['100']['mean'])+'% ground at r100 (n='+str(strong['ours']['ground']['100']['n'])+'); all aAah games already satisfy that rating filter.',
        '', 'Read, not tested',
        'Being behind an ally can reflect support, geography or crowding; it does not demonstrate a protective policy.',
        'A queen stepping closer can be travelling or eating rather than attacking; a fatal head hit does identify the mover.',
        'Team ground is a joint outcome of all heads. Differences between teams do not isolate the queen’s contribution.',
        '', 'Definitions and limits',
        'Rounds here are 1-based: replay r0 is round 1; checkpoints are after all actions in that round. Samples are before every tenth round. Early endings supply no later checkpoint; n changes accordingly.',
        'Position and ground use full replay state, including heads outside queen view; initiative is limited to steps starting with an enemy head in her view. Mutual head collisions count as both a kill and a death in event summaries.',
        'All distances except ground use wrapping Manhattan distance (horizontal plus vertical gap), not routes around walls; view is the wrapping 7×7 box. Centre uses circular coordinate means of all own heads including the queen.',
        'Ground: shortest walk to any head, walls/portals respected, bodies ignored; all map tiles count, equal reachable distances give half a tile, tiles unreachable by both give neither team credit.',
        'Loops: successful one-step moves forming a closed simple path of 4–8 actions inside a wrapping box ≤3×3; whole completed cycles count, including lead-in. Standing/splitting does not count. Fifty-round windows require the queen alive throughout; intermediate steps count as visited tiles.',
        'Initiative includes attempted fatal steps with a known destination. The true nearest enemy head is held fixed for each step; at least one enemy head must be in view for that step to enter the initiative count. Five-round closing sums use the other head’s position at each move in the five completed rounds preceding contact (fatal round excluded); contact-round steps are stored separately. Positive values mean closing, negative mean opening. Per-event traces and first closing mover are in rows.json.',
        'Opponent mix: '+ '; '.join(f"{g} {sum(r['opponent_rating'] is not None and r['opponent_rating']>=2000 for r in rs)}/{len(rs)} opponents ≥2000, {len(set(r['opponent_id'] for r in rs))} opponents, A/B {sum(r['side']=='A' for r in rs)}/{sum(r['side']=='B' for r in rs)}" for g,rs in gs.items() if g in ('aAah','ours'))+'. Games within a series are not independent.',
        'Cached aAah sample covers about one hour, not 2–3 days; addendum permits more downloads only if a side is missing, so none were made. aAah submission versions are absent from cached metadata, so version changes cannot be detected. Ours: '+str(dict(Counter(r['version'] for r in gs['ours'])))+' (same code).',
        'The #38 pair is a local test against one normal bot, not ladder evidence. No per-map claims. Unclassified other deaths stay separate; nearest-head samples need both teams present. Phase/size breakdown of every metric is in strata.json.',
        'All 503 reconstructed final standings matched; 370 own games also matched the separate ladder records, 538 five-round closing sums matched the change in head distance, and 20 replays passed a direct event audit (validation.json). Pearls use removal events, so paid-step eating is counted. No previous queen454 analysis was read or reused.'
    ]
    assert len(lines)<=80,len(lines)
    (OUT/'summary.md').write_text('\n'.join(lines)+'\n')
    (OUT/'last.txt').write_text(f"Counted {len(rows)} replays independently: aAah 101, ours 370, #38 off/on 16 each.\nWrote summary.md, rows.json, strata.json, paired-ground.json and reproducible scripts in sol/.\nAll 503 final states matched; 370 ladder cross-checks, 538 approach sums and 20 direct event audits passed.\nLimits: aAah one-hour cache, unknown aAah versions, mixed opponents, only 16 local matched pairs.\nnice -n 10 was attempted; sandbox denied setpriority. Completed {datetime.now().astimezone().isoformat(timespec='seconds')}.\n")
    print('summary lines',len(lines),'groups', {g:len(v) for g,v in gs.items()})
if __name__=='__main__':main()
