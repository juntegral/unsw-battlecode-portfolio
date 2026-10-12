#!/usr/bin/env python3
"""Read-only independent comparisons; writes evidence only under ladder/checks."""
import importlib.util
import json
from pathlib import Path
import random
import sys
sys.dont_write_bytecode=True
from ladder_collect import ROOT, OUT, RAW, atomic, read_lines
from ladder_rows import make_row

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    battles=read_lines(OUT/'battles.jsonl');rows=read_lines(OUT/'rows.jsonl');lookup={r['game']:r for r in rows}
    mismatches=[];checked=0;complete=0;sides=[]
    for b in battles:
        if not b.get('complete'):continue
        games=b['games']
        if len(games)!=len(b['results']):mismatches.append(dict(battle=b['id'],reason='game/result count'));continue
        matched=[]
        for g,result in zip(games,b['results']):
            if g['id'] not in lookup:mismatches.append(dict(game=g['id'],reason='row missing'));continue
            row=lookup[g['id']];checked+=1;matched.append(row)
            if row['result']!=result or row['win']!=(result=='win'):mismatches.append(dict(game=g['id'],row=row['result'],battle=result))
            j=json.loads((RAW/str(b['id'])/f"game-{g['id']}.json").read_text())
            by_id='A' if j.get('teamAId')==1119 else 'B' if j.get('teamBId')==1119 else None
            if row['our_side']!=by_id or row.get('our_bot') is None or (j.get('winner') or '').upper()!=({'win':by_id,'loss':'B' if by_id=='A' else 'A'}.get(result) or ''):
                sides.append(dict(game=g['id'],row_side=row['our_side'],side_by_team_id=by_id,replay_bot=row.get('our_bot'),server_winner=j.get('winner'),battle=result))
        if len(matched)==len(games):
            complete+=1
            if sum(r['win'] for r in matched)!=b['wins']:mismatches.append(dict(battle=b['id'],reason='win count'))
    status='checked' if checked else f'unavailable: {len(battles)} battles in the ledger, none complete (run ladder_collect.py --recheck)' if battles else 'unavailable: no server battles collected'
    battle_check=dict(games=checked,battles=complete,mismatches=mismatches,side_mismatches=sides,status=status)
    drop=module('ladder_prior_drop',ROOT/'data/online/smoke/drop-analysis/count.py')
    prior={g['gid']:g for g in json.loads((ROOT/'data/online/smoke/drop-analysis/games.json').read_text())}
    folder=ROOT/'data/online/smoke/ns39-bob1-new';pairs=[];smoke_rows=[]
    for p in sorted(folder.glob('game-*.json')):
        j=json.loads(p.read_text());rp=folder/f'M{j["id"]}.replay';row,g=make_row(rp,j);smoke_rows.append(row)
        earlier=prior.get(j['id']) or drop.scan(rp,j,folder.name,set())
        cross=[c for c in earlier['collisions'] if c['cross_team']];ids={d for c in cross for d in c['deaths']}
        pp=[p for p in earlier['pearls'] if p['death'] in ids]
        expected={s:dict(total=sum(p['drop_side']==s for p in pp),eaten_by_end={e:sum(p['drop_side']==s and p['eater']==e for p in pp) for e in ('us','them','nobody')},
                        eaten_within_15={e:sum(p['drop_side']==s and p['eater']==e and p['wait']<=15 for p in pp) for e in ('us','them')}) for s in ('us','them')}
        actual={s:{k:row['head_on']['drops'][s][k] for k in ('total','eaten_by_end','eaten_within_15')} for s in ('us','them')}
        pairs.append(dict(game=j['id'],prior_head_on=len(cross),row_head_on=row['head_on']['count'],prior_drops=expected,row_drops=actual,match=len(cross)==row['head_on']['count'] and expected==actual))
    candidates=[]
    for folder in (RAW,ROOT/'data/online/dl-20261004',ROOT/'data/online/dl-20261003'):
        for p in folder.rglob('game-*.json'):
            j=json.loads(p.read_text())
            if j.get('ranked') and 1119 in (j.get('teamAId'),j.get('teamBId')) and (p.parent/f'M{j["id"]}.replay').exists():candidates.append((p,j))
    unique={j['id']:(p,j) for p,j in candidates};chosen=random.Random(20261007).sample(sorted(unique.values(),key=lambda x:x[1]['id']),min(5,len(unique)))
    card=module('ladder_card38',ROOT/'data/local/hunter38/harness/work/card_38_check.py');death_checks=[]
    for p,j in chosen:
        rp=p.parent/f'M{j["id"]}.replay';row,g=make_row(rp,j);_,counts,_=card.one((str(rp),'0' if row['our_side']=='A' else '1'))
        cause=next((cause for cause in card.CAUSE+['other'] if counts.get('queen_deaths_'+cause)), 'none')
        rnd=counts.get('queen_death_round_sum') if counts.get('queen_deaths') else None
        translated={'wall':'wall','self':'own body','body':'other dragon body','headon':'head-on','none':'none','other':'other'}[cause]
        check=dict(game=j['id'],replay=str(rp.relative_to(ROOT)),row_round=row['queen']['us']['death_round'],row_cause=row['queen']['us']['death_cause'],card_round=rnd,card_cause=cause,
                   match=row['queen']['us']['death_round']==rnd and row['queen']['us']['death_cause']==translated)
        death_checks.append(check);print(json.dumps(check,ensure_ascii=False),flush=True)
    report=dict(battle_results=battle_check,smoke=dict(games=len(pairs),mismatches=sum(not p['match'] for p in pairs),head_on=sum(p['row_head_on'] for p in pairs),pairs=pairs),
                queen_deaths=death_checks,queen_check_source='Previously downloaded ranked archive; not new ladder collection' if not rows else 'Ranked replay sample')
    atomic(OUT/'checks/validation.json',report);atomic(OUT/'checks/ns39-rows.json',smoke_rows)
    print('validation: '+json.dumps(dict(battle_results=battle_check,smoke_games=len(pairs),smoke_mismatches=sum(not p['match'] for p in pairs),head_on=report['smoke']['head_on'],queen_checks=len(death_checks),queen_mismatches=sum(not p['match'] for p in death_checks)),ensure_ascii=False))
if __name__=='__main__':main()
