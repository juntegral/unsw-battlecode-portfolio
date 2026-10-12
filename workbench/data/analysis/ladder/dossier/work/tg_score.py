#!/usr/bin/env python3
"""Reuse fp_build metric definitions verbatim; compare the target's own games."""
import sys
sys.dont_write_bytecode = True
import ast
import hashlib
import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path

DOS=Path(__file__).resolve().parents[1]
OUT=DOS/'target'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def definitions(rows,extra):
    source=(DOS/'work/fp_build.py').read_text()
    tree=ast.parse(source)
    start=next(n.lineno for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='METRICS' for t in n.targets))
    end=next(n.lineno for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='pool')
    code='\n'.join(source.splitlines()[start-1:end-1])
    env=dict(ROWS=rows,EXTRA=extra,WINDOWS={'0-100':(0,100),'101-300':(101,300)})
    exec(compile(code,str(DOS/'work/fp_build.py'),'exec'),env)
    return env['METRICS'],hashlib.sha256(code.encode()).hexdigest()


def pool(rows,fn):
    pairs=[fn(r) for r in rows]
    pairs=[(n,d) for n,d in pairs if d>0]
    n=sum(n for n,d in pairs);d=sum(d for n,d in pairs)
    return dict(value=n/d if d else None,numerator_scaled=n,denominator=d,valid_games=len(pairs))


def sign(a,b): return None if a is None or b is None else (b>a)-(b<a)


def gap(a,b):
    if a is None or b is None: return None
    return (b-a)/max(abs(a),abs(b)) if max(abs(a),abs(b)) else 0


def fmt(x): return 'NA' if x is None else f'{x:.3f}'


def main():
    baseline=json.loads((DOS/'fingerprint.json').read_text())
    ours=[json.loads(s) for s in (DOS/'per-game.jsonl').read_text().splitlines()]
    target=[json.loads(s) for s in (OUT/'per-game-top1.jsonl').read_text().splitlines()]
    assert len(ours)==1000 and len({r['game'] for r in ours})==500
    assert baseline['source_sha256']==sha(DOS/'per-game.jsonl')
    mine,digest=definitions(ours,json.loads((DOS/'work/fp_recount.json').read_text())['games'])
    theirs,digest2=definitions(target,json.loads((OUT/'recount.json').read_text()))
    assert digest==digest2
    us=[r for r in ours if r['relation']=='us']; tg=[r for r in target if r['relation']=='us']
    op=[r for r in target if r['relation']=='them']
    shared=sorted({r['layout_key'] for r in us}&{r['layout_key'] for r in tg})
    rates=[]
    for m,t,b in zip(mine,theirs,baseline['rates']):
        assert (m['name'],m['window'])==(t['name'],t['window'])==(b['name'],b['window'])
        for s in ('us','them'):
            recomputed=pool([r for r in ours if r['relation']==s],m['fn'])
            assert recomputed==b['pooled'][s], (m['name'],m['window'],s)
            elite=pool([r for r in ours if r['relation']==s and r['opponent_rating']>=2100],m['fn'])
            assert elite==b['rating_bands']['2100+'][s]
        r={k:v for k,v in m.items() if k!='fn'}
        r['pooled']=dict(ours=b['pooled']['us'],rank1=pool(tg,t['fn']),rank1_opponents=pool(op,t['fn']),
                         our_2100plus_opponents=b['rating_bands']['2100+']['them'])
        layouts={}
        for layout in sorted({x['layout_key'] for x in tg} | {x['layout_key'] for x in us}):
            a=b['layouts'].get(layout,{}).get('us')
            z=pool([x for x in tg if x['layout_key']==layout],t['fn'])
            layouts[layout]=dict(ours=a,rank1=z,
                rank1_opponents=pool([x for x in op if x['layout_key']==layout],t['fn']))
        valid=[l for l in shared if layouts[l]['ours']['value'] is not None and layouts[l]['rank1']['value'] is not None]
        a=sum(layouts[l]['ours']['value'] for l in valid)/len(valid) if valid else None
        z=sum(layouts[l]['rank1']['value'] for l in valid)/len(valid) if valid else None
        signs=Counter(sign(layouts[l]['ours']['value'],layouts[l]['rank1']['value']) for l in valid)
        direction=sign(a,z)
        r['layouts']=layouts
        r['shared_equal_layouts']=dict(ours=a,rank1=z,valid_layouts=valid,layout_count=len(shared),
            valid_layout_count=len(valid),rank1_higher=signs[1],rank1_lower=signs[-1],tied=signs[0],missing=len(shared)-len(valid))
        r['gap']=gap(a,z)
        r['pooled_gap']=gap(r['pooled']['ours']['value'],r['pooled']['rank1']['value'])
        r['consistent']=bool(direction and signs[direction]>=math.ceil(15*len(valid)/19) and
                             sign(r['pooled']['ours']['value'],r['pooled']['rank1']['value'])==direction)
        rates.append(r)
    assert len(rates)==len(baseline['rates'])
    assert sum(not r['context'] for r in rates)==109
    bykey={(r['name'],r['window']):r for r in rates}
    top=[bykey[r['name'],r['window']] for r in baseline['top30']]
    seen={(r['name'],r['window']) for r in top}
    extra=sorted([r for r in rates if not r['context'] and (r['name'],r['window']) not in seen and
                  any(g is not None and abs(g)>=.25 for g in (r['gap'],r['pooled_gap']))],
                 key=lambda r:(-abs(r['gap'] or 0),r['name'],r['window']))
    displayed=top+extra
    consistent=sorted([r for r in rates if not r['context'] and r['consistent']],key=lambda r:(-abs(r['gap']),r['name'],r['window']))[:12]
    matches=[r for r in rates if not r['context'] and r['gap'] is not None and abs(r['gap'])<.1]
    match_names={'Splits per eaten pearl','Blind successful movement','Tiles visited per 20-round dragon block',
                 'Board seen by endpoint','Heads in enemy half','Portal steps','Queen dies before game end'}
    short_matches=[r for r in matches if r['name'] in match_names and
                   (r['name'] not in {'Splits per eaten pearl','Portal steps'} or r['window']=='game')][:12]
    snapshot=json.loads((OUT/'input-snapshot.json').read_text())
    validation=json.loads((OUT/'validation.json').read_text())
    metadata=validation['metadata']
    assert len(metadata)==len(tg)==snapshot['selected_games']
    dates=sorted(m['completedAt'] for m in metadata if m.get('completedAt'))
    opponents={}; elite_ids=set(); unknown=[]
    for m in metadata:
        other='B' if m['teamAId']==306 else 'A'
        oid=m['team'+other+'Id']; elo=m.get('team'+other+'Elo')
        opponents.setdefault(str(oid),dict(name=m.get('team'+other+'Name'),games=0,games_2100plus=0,ratings=[]))
        d=opponents[str(oid)];d['games']+=1
        if elo is None: unknown.append(m['id'])
        else:
            d['ratings'].append(elo)
            if elo>=2100: d['games_2100plus']+=1;elite_ids.add(oid)
    summary=dict(target_team_id=306,target_team='Vibing++',games=len(tg),side_rows=len(target),
                 replay_files=snapshot['replay_files'],excluded_non_target=len(snapshot['excluded_non_target']),
                 layouts=dict(Counter(r['layout_key'] for r in tg)),record=dict(Counter(r['result'] for r in tg)),
                 date_range_utc=[dates[0],dates[-1]],opponents=opponents,unique_opponents=len(opponents),
                 opponents_ever_2100plus=len(elite_ids),games_against_2100plus=sum(d['games_2100plus'] for d in opponents.values()),
                 missing_opponent_rating_games=unknown,shared_layouts=shared,ours_games=500,ours_2100plus_games=baseline['rating_band_games']['2100+'])
    result=dict(created_at=datetime.now().astimezone().isoformat(timespec='seconds'),summary=summary,
                metric_definition_sha256=digest,inputs_sha256={str(p.relative_to(DOS)):sha(p) for p in
                    (DOS/'fingerprint.json',DOS/'per-game.jsonl',DOS/'work/fp_build.py',DOS/'work/fp_recount.json',
                     OUT/'per-game-top1.jsonl',OUT/'recount.json',OUT/'input-snapshot.json',OUT/'validation.json')},
                pooled_definition='Unchanged fp_build.py: sum scaled numerators / sum denominators over valid games.',
                shared_definition='Mean of per-layout pooled rates, equal weights; both sides must have valid denominators for that metric. NA stays missing.',
                gap_definition='(rank1 - ours) / max(abs(rank1), abs(ours)) on shared equal-layout means; both zero -> 0.',
                consistent_definition='Same sign in pooled and shared means, and >= ceil(15*N/19) valid shared layouts agree; ties count against agreement.',
                display_definition='Original top30 in original order; then other behaviour rates with absolute pooled or shared gap >= 0.25. Context excluded from selection.',
                rates=rates,displayed=[dict(name=r['name'],window=r['window']) for r in displayed],
                largest_consistent_gaps=[dict(name=r['name'],window=r['window']) for r in consistent],
                matches=[dict(name=r['name'],window=r['window']) for r in matches],
                match_shortlist=[dict(name=r['name'],window=r['window']) for r in short_matches])
    for name in ('tg_count.py','tg_score.py','tg_verify.py','tg_run.py','tg_unpack.c'):
        result['inputs_sha256']['work/'+name]=sha(DOS/'work'/name)
    lines=['# Rank-1 behaviour scoreboard','',
        f"Vibing++ (306): {len(tg)} games / {len(target)} side rows, {len(summary['layouts'])} layouts; {summary['record'].get('win',0)} wins, {summary['record'].get('loss',0)} losses, {summary['record'].get('draw',0)} draws. Selected by team ID from {snapshot['replay_files']} replays; excluded {len(snapshot['excluded_non_target'])} other-team games.",
        f"Completed UTC: {dates[0]} to {dates[-1]}. Opponents: {len(opponents)} distinct; {len(elite_ids)} rated 2100+ in at least one sampled game, across {summary['games_against_2100plus']} games; missing ratings: {len(unknown)}.",
        'Layouts (games): '+ '; '.join(f'{l}: {n}' for l,n in sorted(summary['layouts'].items()))+'.',
        f"O = ours (500 games); R = rank-1; RO = its opponents; E = our ladder opponents rated 2100+ (70 games). Shared O/R: equal-weight means over {len(shared)} matching layouts (size, edges, starting dragons; colour swaps equivalent).",
        'Unchanged fingerprint definitions; pooled numerator/denominator rates, inclusive windows, percentages 0–100; full 20-round blocks only. Harvest follows birth cohorts to game end; wait/death/contact means are conditional; incidence uses original follow-up eligibility.',
        'Shared means use the same valid layouts for both bots per rate; higher excludes ties/missing. Gap = (R−O)/max(|R|,|O|) on shared means (zero/zero = 0). NA means no denominator.',
        'First 30 rows reproduce the fingerprint ranked table; extra rows have ≥25% absolute pooled or shared gap. Every rate and denominator is in scoreboard.json.',
        '', '| Rate (unit) | Window | O | R | RO | E | Shared O | Shared R | R higher/valid | Gap |',
        '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in displayed:
        p=r['pooled'];s=r['shared_equal_layouts']
        lines.append(f"| {r['name']} ({r['unit']}) | {r['window']} | "+' | '.join(fmt(p[k]['value']) for k in ('ours','rank1','rank1_opponents','our_2100plus_opponents'))+
                     f" | {fmt(s['ours'])} | {fmt(s['rank1'])} | {s['rank1_higher']}/{s['valid_layout_count']} | {r['gap']:+.1%} |" if r['gap'] is not None else
                     f"| {r['name']} ({r['unit']}) | {r['window']} | "+' | '.join(fmt(p[k]['value']) for k in ('ours','rank1','rank1_opponents','our_2100plus_opponents'))+' | NA | NA | 0/0 | NA |')
    lines[6]+=' Consistency: pooled/shared directions agree and ≥ceil(15×valid layouts/19) layout signs agree; descriptive counts, no uncertainty test. The 12 gaps below are largest among consistent behaviour rates.'
    lines+=['','## Where we differ most from rank-1','']
    cause_phrases={'no action':'fails to provide a move or split and dies','illegal split':'dies after an illegal split',
                   'timeout':'dies after an action timeout','unpaid sprint':'dies after a sprint it cannot pay for',
                   'wall':'dies by hitting a wall','own body':'dies by hitting its own body','another body':"dies by hitting another dragon’s body",
                   'head-on mover':'initiates a head-on collision and dies','head-on hit':'is struck head-on and dies'}
    for r in consistent:
        phrase=r['description'];subject='A dragon of theirs'
        if r['name'].startswith('Queen '): subject='Their queen'
        if r['name'].startswith('Death: '): phrase=cause_phrases[r['name'].split(': ',1)[1]]
        elif r['name'].startswith('Queen death: '): phrase=cause_phrases[r['name'].split(': ',1)[1]]
        if r['name']=='Queen dies in window': phrase='dies during the window, among queens alive at its start with complete follow-up or death'
        if r['name']=='Queen dies before game end': phrase='dies before the game ends'
        if r['name']=='Queen death round': phrase='dies among deaths observed in this window'
        if r['name'].startswith('First contact'):
            subject='Their team';phrase='first sees an enemy head'+(' during this window' if r['name']=='First contact in window' else ' before game end')
        if r['name']=='Board seen by endpoint': subject='Their team';phrase='covers the board by the endpoint'
        if 'birth' in r['name'].lower(): subject='Their team'
        direction='more often' if r['gap']>0 else 'less often'
        if r['unit'].startswith('rounds'): direction='with a higher mean' if r['gap']>0 else 'with a lower mean'
        if r['unit']=='tiles/block': direction='with more distinct tiles' if r['gap']>0 else 'with fewer distinct tiles'
        lines.append(f"- {r['window']}: {subject} {phrase} {direction} than ours ({r['gap']:+.1%}); fields: `"+'`, `'.join(r['fields'])+'`.')
    lines+=['','## Where we already match','']
    # Compact window grouping keeps the complete short list within the brief's line budget.
    for windows in (('0-100',),('101-300',),('game','r50','r100')):
        group=[r for r in short_matches if r['window'] in windows]
        if group: lines.append(f"- {' / '.join(windows)} (|shared gap| <10%): "+'; '.join(r['name']+(' ['+r['window']+']' if len(windows)>1 else '')+f" ({r['gap']:+.1%})" for r in group)+'.')
    lines+=['', 'Re-run from the repository root: `nice -n 10 python3 -B data/analysis/ladder/dossier/work/tg_run.py`.']
    lines[2]+=' '+lines[3]
    lines[5]+=' '+lines[7]
    lines[6]+=' '+lines[8]
    for index in (8,7,3): del lines[index]
    assert len(lines)<=90,(len(lines),len(displayed))
    (OUT/'scoreboard.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    (OUT/'scoreboard.md').write_text('\n'.join(lines)+'\n')
    print(f'Scoreboard: {len(lines)} lines, {len(displayed)} table rows, {len(rates)} metrics/context entries',flush=True)


if __name__=='__main__': main()
