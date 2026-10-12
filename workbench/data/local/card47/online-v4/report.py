import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from statistics import mean
OUT = Path(__file__).resolve().parent
SETS = ['new', 'main51', 'main48', 'main47']
CAUSES = ['wall','own body','another body','head-on mover','head-on hit','no action','timeout','unpaid sprint','illegal split']
rows = [json.loads(s) for s in (OUT/'rows.jsonl').read_text().splitlines()]
groups = {s: [r for r in rows if r['set'] == s] for s in SETS}
assert len(rows) == 60 and all(len(rs) == 15 for rs in groups.values())
assert all(len({r['map_id'] for r in rs}) == 15 for rs in groups.values())
assert all({r['map_id'] for r in rs} == {r['map_id'] for r in groups['new']} for rs in groups.values())
assert all(r['sonar']['unreadable'] == 0 and not r['anomalies'] for r in rows)
def value(r, keys):
    for k in keys: r = r[k]
    return r
def total(rs, *keys): return sum(value(r, keys) for r in rs)
def avgs(*keys): return [total(rs, *keys)/15 for rs in groups.values()]
def rates(*keys): return [1000*total(rs, *keys)/total(rs, 'turns') for rs in groups.values()]
def babies(rs, told=None):
    return [b for r in rs for b in r['dead_end_babies'] if told is None or b['told'] == told]
def baby_count(rs, told, key): return sum(bool(b[key]) for b in babies(rs,told))
def return_cell(rs,told):
    bs = babies(rs,told)
    return f"{sum(b['returned_after'] is not None for b in bs)} / {len(bs)}"
def harm_cell(rs,told):
    bs = [b for b in babies(rs,told) if b['returned_after'] is not None]
    return f"{sum(b['died_inside_after_return'] for b in bs)} / {sum(b['split_inside_after_return'] for b in bs)} / {sum(b['died_inside_after_return'] or b['split_inside_after_return'] for b in bs)}"
lines = ['# Card 47 fourth build: 60 online games, 7–8 Oct 2026',
    '15 games per set, the same maps versus team 946; our team is 1119; games are unpaired.',
    'Checker definitions: dead end ≤31 tiles, one gate, no portal; hit = mother’s split-turn message hit child on that turn or 2 after; return = outside-to-inside head move into the mother’s same dead end within 30 rounds of birth (birth inside is excluded until exit); subsequent death/split also within 30 rounds; wasted = <2 growth-counted pearls then split/died inside; early finishes carry final alive counts; rays count sent pings.']
def heading(text):
    lines.extend([text, '| Measure | new | main51 | main48 | main47 |', '|---|---:|---:|---:|---:|'])
def add(name, cells):
    lines.append('| '+name+' | '+' | '.join(f'{v:.3f}' if isinstance(v,float) else str(v) for v in cells)+' |')
heading('## A. Baby case (counts; rates labelled)')
add('Dragon turns', [total(rs,'turns') for rs in groups.values()])
add('Dead-end splits / split message names own end / children hit', [f"{len(babies(rs))} / {baby_count(rs,None,'own_end_sent')} / {len(babies(rs,True))}" for rs in groups.values()])
add('Told: returned / children', [return_cell(rs,True) for rs in groups.values()])
add('Not told: returned / children', [return_cell(rs,False) for rs in groups.values()])
add('Told returners: died / split / either inside', [harm_cell(rs,True) for rs in groups.values()])
add('Not-told returners: died / split / either inside', [harm_cell(rs,False) for rs in groups.values()])
add('Born inside / exited or born outside', [f"{baby_count(rs,None,'born_inside')} / {baby_count(rs,None,'left')}" for rs in groups.values()])
add('Incomplete 30-round watch (alive at game end)', [baby_count(rs,None,'censored') for rs in groups.values()])
add('Wasted stays / pooled per 1,000 dragon turns', [f"{total(rs,'stays','wasted')} / {1000*total(rs,'stays','wasted')/total(rs,'turns'):.3f}" for rs in groups.values()])
heading('## B. Cost (per-game means; deaths = pooled per 1,000 dragon turns)')
add('Wins per game; W/D/L counts', [f"{sum(r['result']=='W' for r in rs)/15:.3f}; {sum(r['result']=='W' for r in rs)}/{sum(r['result']=='D' for r in rs)}/{sum(r['result']=='L' for r in rs)}" for rs in groups.values()])
add('Final total length / longest', [f"{total(rs,'final','total')/15:.2f} / {total(rs,'final','longest')/15:.2f}" for rs in groups.values()])
add('Pearls by r100 / r300', [f"{total(rs,'pearls','100')/15:.2f} / {total(rs,'pearls','300')/15:.2f}" for rs in groups.values()])
add('Alive r100 / r200 / r300', [' / '.join(f"{total(rs,'alive',str(r))/15:.2f}" for r in (100,200,300)) for rs in groups.values()])
add('Queen pings / leader reports / new-kind rays', [' / '.join(f"{total(rs,'sonar',k)/15:.2f}" for k in ('queen','leader','new_rays')) for rs in groups.values()])
for cause in CAUSES[:6]: add('Deaths: '+cause, rates('deaths',cause))
add('Deaths: timeout / unpaid sprint / illegal split', [' / '.join(f"{1000*total(rs,'deaths',k)/total(rs,'turns'):.3f}" for k in CAUSES[6:]) for rs in groups.values()])
add('Turns out of time', avgs('timeout_turns'))
lines.extend(['## C. Per map', '| Map | new | main51 | main48 | main47 | Pearls r100 new / main51 |', '|---|---|---|---|---|---:|'])
lookup = {s: {r['map_id']: r for r in rs} for s,rs in groups.items()}
for r in groups['new']:
    lines.append('| '+r['map']+' | '+' | '.join(lookup[s][r['map_id']]['result'] for s in SETS)+f" | {r['pearls']['100']} / {lookup['main51'][r['map_id']]['pearls']['100']} |")
nb = babies(groups['new']); told = babies(groups['new'],True); untold = babies(groups['new'],False)
returns = lambda bs: sum(b['returned_after'] is not None for b in bs)
lines.append(f"Of {len(nb)} new dead-end splits, {len(told)} children were hit; {returns(told)}/{len(told)} told children returned against {returns(untold)}/{len(untold)} not told and "+', '.join(f"{returns(babies(groups[s]))}/{len(babies(groups[s]))} in {s}" for s in SETS[1:])+'.')
lines.append('Return cases are too few to tell whether the message stops babies going back; told and not-told children differ in geometry, and the games are unpaired.')
measures = {'wins/game':[sum(r['result']=='W' for r in rs)/15 for rs in groups.values()]}
for name, keys in [('final total',('final','total')),('final longest',('final','longest')),('pearls r100',('pearls','100')),('pearls r300',('pearls','300')),*[(f'alive r{r}',('alive',str(r))) for r in (100,200,300)],*[(('new-kind rays' if k=='new_rays' else f'{k} rays'),('sonar',k)) for k in ('queen','leader','new_rays')],('timeout turns',('timeout_turns',))]: measures[name] = avgs(*keys)
for cause in CAUSES: measures['death '+cause+'/1,000'] = rates('deaths',cause)
spread = {}; outside=[]
for name, vals in measures.items():
    n,*refs = vals; lo,hi = min(refs),max(refs)
    out = n < lo-1e-9 or n > hi+1e-9
    spread[name] = dict(zip(SETS, vals),main_min=lo,main_max=hi,outside=out)
    if out: outside.append(f"{name} {n:.3f} ({'below' if n < lo else 'above'} {lo:.3f}–{hi:.3f})")
lines.append('Outside the three-main range: '+('; '.join(outside) if outside else 'none')+'.')
lines.append('All other B measures are within that range; these counts cannot attribute costs to the build.')
assert len(lines) <= 55, len(lines)
(OUT/'table.md').write_text('\n'.join(lines)+'\n')
(OUT/'spread.json').write_text(json.dumps(spread,indent=2)+'\n')
print('table lines:',len(lines))
print('\n'.join(lines[-4:]))
