#!/usr/bin/env python3
"""Read-only replay count. Run from the repo root; outputs stay beside this script.

Instrument the existing check's one() without changing its replay reconstruction,
queen selection, lap classification, view, wrapped distances, or round cutoff.
Decision pressure and distance use the head BEFORE the action; lap labels describe
that action. Source replacements fail loudly if the reference implementation changes.
"""
import sys
sys.dont_write_bytecode = True
import importlib.util
import inspect
import json
from pathlib import Path
from datetime import datetime

OUT = Path(__file__).resolve().parent
HUNTER = OUT.parent
NORMAL = Path('~/meow-loop-out/card-38/attempt-1')
SPEC = importlib.util.spec_from_file_location('card38_check', HUNTER / 'harness/work/card_38_check.py')
check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check)


def instrument():
    source = inspect.getsource(check.one)
    def replace(old, new):
        nonlocal source
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    replace('    spawn = bodies[queen][0]', '''    spawn = bodies[queen][0]
    enemy_queen = next(i for i in (0, 1) if team_of.get(i) != ours)
    enemy_spawn = bodies[enemy_queen][0]
    records = []
    death_round = None''')
    replace('        return p\n', '''        enemy_heads = [b[0] for did, b in bodies.items() if b and team_of.get(did) != ours]
        p['distance'] = far(head, spawn)
        p['enemy_distance'] = far(head, enemy_spawn)
        p['enemy_in_view'] = any(in_view(h) for h in enemy_heads)
        p['enemy_within_6'] = sum(far(head, h) <= 6 for h in enemy_heads)
        return p
''')
    replace("        lap.append(is_lap)", '''        lap.append(is_lap)
        if p['rnd'] < UNTIL:
            records.append(dict(round=p['rnd'], length=p['len'], head=p['start'],
                                distance=p['distance'], enemy_distance=p['enemy_distance'],
                                lap=is_lap, on_loop=p['on'], enemy_in_view=p['enemy_in_view'],
                                enemy_within_6=p['enemy_within_6']))''')
    replace('            alive = False', '            alive = False\n            death_round = rnd')
    replace("    return 'small' if W * H <= 600 else 'big', dict(c), track.hexdigest()", '''    centre = ((W - 1) / 2, (H - 1) / 2)
    scale = dict(width=W, height=H, queen=queen, spawn=spawn, enemy_spawn=enemy_spawn,
                 centre=centre, spawn_to_centre=far(spawn, centre), spawn_to_enemy=far(spawn, enemy_spawn))
    return dict(records=records, counters=dict(c), scale=scale, death_round=death_round)''')
    namespace = dict(check.__dict__)
    exec(compile(source, str(HUNTER / 'harness/work/card_38_check.py') + ':instrumented', 'exec'), namespace)
    return namespace['one']


def quantile(values, p):
    if not values:
        return None
    values = sorted(values)
    x = (len(values) - 1) * p
    i = int(x)
    return values[i] + (values[min(i + 1, len(values) - 1)] - values[i]) * (x - i)


def stats(records):
    n = len(records)
    distances = [r['distance'] for r in records]
    bins = [sum(lo <= d <= hi for d in distances) for lo, hi in [(0, 4), (5, 8), (9, 12), (13, float('inf'))]]
    visible = sum(r['enemy_in_view'] for r in records)
    enemy_side = sum(r['enemy_distance'] < r['distance'] for r in records)
    near = sum(r['enemy_within_6'] for r in records)
    return dict(decisions=n, p25=quantile(distances, .25), median=quantile(distances, .5), p75=quantile(distances, .75),
                distance_bin_counts=bins, distance_bin_shares=[v / n if n else None for v in bins],
                closer_to_enemy_count=enemy_side, closer_to_enemy_share=enemy_side / n if n else None,
                enemy_in_view_count=visible, enemy_in_view_share=visible / n if n else None,
                enemy_within_6_sum=near, enemy_within_6_mean=near / n if n else None)


def aggregate(games):
    records = [r for g in games for r in g['records']]
    return dict(games=len(games), queen_decisions_before_until=len(records),
                lap=stats([r for r in records if r['lap']]),
                length_2_3=stats([r for r in records if 2 <= r['length'] <= 3]),
                on_loop_decisions=sum(r['on_loop'] for r in records))


def number(x):
    return '—' if x is None else f'{x:.2f}'.rstrip('0').rstrip('.')


def percent(x):
    return '—' if x is None else f'{100*x:.1f}%'


def main():
    # Snapshot eligibility before reading any replay; do not wait for another run.
    log = HUNTER / 'run.log'
    last = log.read_text().splitlines()[-1] if log.exists() and log.read_text().splitlines() else ''
    hunter_done = last.strip().endswith('DONE')
    sets = [('normal', NORMAL / 'replays')]
    if hunter_done and (HUNTER / 'replays').exists():
        sets.append(('hunter', HUNTER / 'replays'))
    one = instrument()
    result = dict(created=datetime.now().astimezone().isoformat(), until=check.UNTIL,
                  hunter_included=hunter_done, hunter_start_last_log_line=last, sets={})
    timelines = {}
    for set_name, directory in sets:
        games = []
        for arm in ('base', 'candidate'):
            for path in sorted(directory.glob(f'{arm}_*.replay')):
                map_name, seed, side = path.stem[len(arm)+1:].rsplit('_', 2)
                print(f'{set_name}: {path.name}', flush=True)
                game = one((str(path), side))
                game.update(map=map_name, seed=seed, side=side, arm=arm, file=path.name)
                assert len([r for r in game['records'] if r['lap']]) == game['counters'].get('lap_steps_early', 0)
                assert sum(r['on_loop'] for r in game['records']) == game['counters'].get('on_loop', 0)
                games.append(game)
                if set_name == 'normal' and path.name in ('candidate_weakhold_13801_0.replay', 'base_weakhold_13801_0.replay'):
                    by_round = {r['round']: r for r in game['records']}
                    timelines[arm] = dict(file=path.name, death_round=game['death_round'],
                                         rows=[by_round[r] for r in range(0, check.UNTIL, 20) if r in by_round],
                                         missing_marks=[r for r in range(0, min(check.UNTIL, game['death_round'] + 1 if game['death_round'] is not None else check.UNTIL), 20) if r not in by_round])
        maps = {}
        for m in sorted({g['map'] for g in games}):
            mg = [g for g in games if g['map'] == m]
            scales = []
            for g in mg:
                scale = dict(g['scale'], side=g['side'])
                if scale not in scales:
                    scales.append(scale)
            maps[m] = dict(scale=scales, **{arm: aggregate([g for g in mg if g['arm'] == arm]) for arm in ('base', 'candidate')})
        result['sets'][set_name] = dict(maps=maps, total={arm: aggregate([g for g in games if g['arm'] == arm]) for arm in ('base', 'candidate')},
                                             per_game=[{k: v for k, v in g.items() if k != 'records'} for g in games])
    reference = json.loads((NORMAL / 'check.json').read_text())
    normal = result['sets']['normal']['total']
    for arm in ('base', 'candidate'):
        assert normal[arm]['lap']['decisions'] == reference[arm]['lap_steps_before_r300']
        assert normal[arm]['on_loop_decisions'] == reference[arm]['on_the_loop_decisions']
        assert normal[arm]['length_2_3']['decisions'] == reference[arm]['of_those_2_or_3_long']
    result['reference_check'] = {arm: {k: reference[arm][k] for k in ('lap_steps_before_r300', 'on_the_loop_decisions', 'decisions_after_a_lap_step_where_the_rule_cannot_apply')} for arm in ('base', 'candidate')}
    result['timelines'] = timelines
    (OUT / 'rows.json').write_text(json.dumps(result, indent=2) + '\n')
    on, off = normal['candidate']['lap'], normal['base']['length_2_3']
    lines = [f"Against the normal bot, she mostly loops on her own side, a short distance from spawn: the median is {number(on['median'])} tiles (middle 50%: {number(on['p25'])}–{number(on['p75'])}).",
             f"{percent(on['distance_bin_shares'][0])} are within 4 tiles; {percent(on['distance_bin_shares'][1])} at 5–8, {percent(on['distance_bin_shares'][2])} at 9–12, and {percent(on['distance_bin_shares'][3])} at 13+.",
             f"{percent(on['closer_to_enemy_share'])} are closer to their queen's spawn than ours; centre distances below give the map scale, not proof she is at the centre.",
             f"Loop sites are less crowded in these pooled decisions: an enemy head is in view in {percent(on['enemy_in_view_share'])} versus {percent(off['enemy_in_view_share'])} of switch-off length-2–3 decisions; mean heads within 6: {number(on['enemy_within_6_mean'])} versus {number(off['enemy_within_6_mean'])}; weakhold is the exception for the within-6 mean (0.33 versus 0.31).",
             f"Normal set: {normal['candidate']['games']} games per arm, {on['decisions']} switch-on lap steps versus {off['decisions']} switch-off short decisions; this is descriptive, not a matched-site or causal comparison.", '']
    lines += ['Methods: only our queen, decisions at rounds <300. Distances are wrapped Manhattan distances, exactly as in the existing check; map centre is ((width−1)/2, (height−1)/2). Quartiles use linear interpolation. Distance and pressure are measured immediately before each action; “lap” classifies that action. “On the loop” classifies a decision immediately after a qualifying lap, using the existing length/home gates. Enemy pressure uses current true replay head positions, not remembered ghosts. The 7×7 head-presence box is visible; the Manhattan-6 count includes heads she cannot see. Geometry, spawn distances, and lap reconstruction also use replay truth.', '']
    if not hunter_done:
        lines += [f'Hunter set skipped: no final DONE line at start (last line: `{last}`). No partial hunter counts are used.', '']
    for set_name, data in result['sets'].items():
        groups = list(data['maps'].items()) + [('TOTAL', data['total'])]
        lines += [f'{set_name.capitalize()} set — 1. Lap-step distance', '', '| Map | Switch | Games | Lap decisions | Q25 / median / Q75 | ≤4 / 5–8 / 9–12 / 13+ |', '|---|---|---:|---:|---|---|']
        for m, group in groups:
            for arm in ('base', 'candidate'):
                a, s = group[arm], group[arm]['lap']
                lines.append(f"| {m} | {'off' if arm == 'base' else 'on'} | {a['games']} | {s['decisions']} | {' / '.join(number(s[k]) for k in ('p25','median','p75'))} | {' / '.join(percent(v) for v in s['distance_bin_shares'])} |")
        lines += ['', '2. All length-2–3 decisions', '', '| Map | Switch | Games | Short decisions | Q25 / median / Q75 | ≤4 / 5–8 / 9–12 / 13+ |', '|---|---|---:|---:|---|---|']
        for m, group in groups:
            for arm in ('base', 'candidate'):
                a, s = group[arm], group[arm]['length_2_3']
                lines.append(f"| {m} | {'off' if arm == 'base' else 'on'} | {a['games']} | {s['decisions']} | {' / '.join(number(s[k]) for k in ('p25','median','p75'))} | {' / '.join(percent(v) for v in s['distance_bin_shares'])} |")
        lines += ['', '3. Map scale and lap steps on their side (strictly closer to enemy spawn)', '', '| Map | Size | Our side: spawn → centre / enemy | Off games / laps / their-side share | On games / laps / their-side share |', '|---|---|---|---|---|']
        for m, group in data['maps'].items():
            scale = group['scale'][0]
            detail = '; '.join(f"{s['side']}: {tuple(s['spawn'])} → {number(s['spawn_to_centre'])} / {number(s['spawn_to_enemy'])}" for s in group['scale'])
            cells = [f"{group[a]['games']} / {group[a]['lap']['decisions']} / {percent(group[a]['lap']['closer_to_enemy_share'])}" for a in ('base','candidate')]
            lines.append(f"| {m} | {scale['width']}×{scale['height']} | {detail} | {' | '.join(cells)} |")
        cells = [f"{data['total'][a]['games']} / {data['total'][a]['lap']['decisions']} / {percent(data['total'][a]['lap']['closer_to_enemy_share'])}" for a in ('base','candidate')]
        lines.append(f"| TOTAL | — | — | {' | '.join(cells)} |")
        lines += ['', '4. Enemy pressure at decisions (true current heads)', '', '| Map | Switch / sample | Games | Decisions | ≥1 head in 7×7 | Mean heads within Manhattan 6 |', '|---|---|---:|---:|---:|---:|']
        for m, group in groups:
            for arm, sample in (('base','lap'), ('candidate','lap'), ('base','length_2_3')):
                a, s = group[arm], group[arm][sample]
                lines.append(f"| {m} | {'off' if arm == 'base' else 'on'} / {'laps' if sample == 'lap' else 'all length 2–3'} | {a['games']} | {s['decisions']} | {percent(s['enemy_in_view_share'])} | {number(s['enemy_within_6_mean'])} |")
        lines.append('')
    lines += ['5. Weakhold seed 13801, our side 0 (one game per arm; pre-action snapshots every 20 rounds)', '', '| Switch | Round | Distance from spawn | Length | Lap action? | On the loop? | Enemy heads within 6 |', '|---|---:|---:|---:|---|---|---:|']
    for arm in ('candidate', 'base'):
        if arm not in timelines:
            continue
        for r in timelines[arm]['rows']:
            lines.append(f"| {'on' if arm == 'candidate' else 'off'} | {r['round']} | {r['distance']} | {r['length']} | {'yes' if r['lap'] else 'no'} | {'yes' if r['on_loop'] else 'no'} | {r['enemy_within_6']} |")
    lines += ['', '; '.join(f"{arm}: death round {t['death_round']}; missing pre-death decision marks {t['missing_marks']}" for arm, t in timelines.items()) + '. No snapshot after death or at round 300 is counted.', '',
              f"Check against existing check.json: switch-on lap total = {on['decisions']} (matches lap_steps_before_r300); on-the-loop decisions = {normal['candidate']['on_loop_decisions']} (matches 1255). They are different event definitions: a lap step completes a lap; an on-the-loop decision follows one and requires a qualifying short queen and square entirely >4 from home. Counts can also differ at death, the final action, or r300. The check has 1302 all-round lap steps and 47 excluded following-lap decisions: 1302 − 47 = 1255; 19 lap steps occur at/after r300, giving 1283 before r300. Off lap/short/on-loop totals also match the reference. No missing measurement in the normal set; paths/maze routes and a categorical centre-region boundary were not requested or inferred."]
    (OUT / 'summary.md').write_text('\n'.join(lines) + '\n')
    print('Wrote summary.md and rows.json; reference totals match.', flush=True)


if __name__ == '__main__':
    main()
