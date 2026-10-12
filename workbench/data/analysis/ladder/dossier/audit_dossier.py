#!/usr/bin/env python3
"""Read-only cross-checks against earlier passes; writes an audit beside this script."""
import sys
sys.dont_write_bytecode = True
import json
import math
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
DATA = OUT.parent
SIDES = ('us', 'them')

def main():
    rows = [json.loads(s) for s in (OUT/'per-game.jsonl').read_text().splitlines()]
    by = {(r['game'], r['relation']): r for r in rows}
    frozen = json.loads((OUT/'input-snapshot.json').read_text())
    original = {r['game']: r for r in frozen['rows']}
    for r in rows:
        layout = frozen['maps'][r['layout_key']]
        assert (r['width'], r['height']) == (layout['width'], layout['height'])
        assert r['cells'] == layout['width']*layout['height']
    assert len(by) == len(rows) == 2*len(original)
    for game in original:
        for interval in ('0-100', '101-300'):
            u, t = (by[game, s]['ranges'][interval] for s in SIDES)
            assert u['cross_head_on_trades'] == t['cross_head_on_trades']
            assert u['head_on_net_length_lost'] == -t['head_on_net_length_lost']
    previous_checks = json.loads((DATA/'losses/counts/validation.json').read_text())
    for c in previous_checks:
        for s in SIDES:
            assert by[c['game'], s]['final_reconstructed'] == c['final_reconstructed'][s]
    old_births, old_snaps, death_checks = 0, 0, 0
    for r in rows:
        old = original[r['game']]
        s = r['relation']
        for interval in ('0-100', '101-300'):
            c = r['ranges'][interval]
            oc = old['deaths']['r'+interval][s]
            assert c['deaths']['head-on mover'] + c['deaths']['head-on hit'] == oc['head-on']
            for newkey, oldkey in [('wall','wall'), ('own body','own body'), ('another body','other dragon body')]:
                assert c['deaths'][newkey] == oc[oldkey]
            assert sum(c['deaths'][k] for k in ('no action', 'timeout', 'unpaid sprint', 'illegal split')) == oc['other']
            death_checks += 1
            for num, den, share in [('dither','no_view_pearl_moved','dither_share'),
                                   ('keeps','keeps_eligible','keeps_direction_share'),
                                   ('near6_births','births','near6_birth_share'),
                                   ('hot_turns','turns','hot_tile_share'),
                                   ('adjacent_pearl_missed','adjacent_pearl_turns','adjacent_pearl_missed_share')]:
                assert 0 <= c[num] <= c[den]
                assert c[share] is None if c[den] == 0 else math.isclose(c[share], c[num]/c[den])
            assert sum(c['cohort_eaten'].values()) + c['cohort_not_eaten'] == c['births']
            assert c['cohort_wait']['n'] == c['cohort_eaten'][s]
            assert 0 <= c['portal_room_births'] <= c['births']
            assert 0 <= c['portal_required_births'] <= c['births']
        for pooled, parts in [('0-100', ('0-50', '51-100')), ('101-300', ('101-200', '201-300'))]:
            for key in ('pearls_eaten','splits','turns','no_view_pearl_turns','no_view_pearl_moved','keeps_eligible',
                        'keeps','dither','adjacent_pearl_turns','adjacent_pearl_missed','hot_turns','portal_steps',
                        'cross_head_on_trades','head_on_length_lost','head_on_other_length_lost','births','near6_births'):
                assert r['ranges'][pooled][key] == sum(r['ranges'][p][key] for p in parts)
        assert r['portal_steps_game'] >= sum(r['ranges'][p]['portal_steps'] for p in ('0-50','51-100','101-200','201-300'))
        seen = [r['ranges'][p]['seen_tiles_end'] for p in ('0-50','51-100','101-200','201-300')]
        observed = [v for v in seen if v is not None]
        assert observed == sorted(observed)
    for n in range(4):
        for line in (DATA/'losses/work'/('eg_rows-%d.jsonl'%n)).read_text().splitlines():
            g = json.loads(line)
            if g['game'] not in original:
                continue
            for s, oldside in [('us','u'), ('them','t')]:
                r = by[g['game'], s]
                births = [p for p in g['pearls'] if p[1] <= 100]
                near = sum(p[3 if s == 'us' else 4] <= 6 for p in births)
                assert r['ranges']['0-100']['births'] == len(births)
                assert r['ranges']['0-100']['near6_births'] == near
                old_births += 1
                for snap in g['snaps']:
                    if snap[0] not in (50, 100):
                        continue
                    c = r['ranges']['0-50' if snap[0] == 50 else '0-100']['end_state']
                    offset = 1 if s == 'us' else 4
                    assert [c[k] for k in ('alive','total','longest')] == snap[offset:offset+3]
                    old_snaps += 1
    # Verify the within-layout Pearson through the fixed-effects residual formula.
    agg = json.loads((OUT/'aggregate.json').read_text())
    bylayout = {}
    for r in rows:
        if r['relation'] == 'us' and r['ranges']['0-100']['dither_share'] is not None:
            bylayout.setdefault(r['layout_key'], []).append((r['ranges']['0-100']['dither_share'], r['ranges']['0-100']['pearls_eaten']))
    sx2 = sy2 = sxy = 0
    count = 0
    for pairs in bylayout.values():
        count += len(pairs)
        sx, sy = sum(p[0] for p in pairs), sum(p[1] for p in pairs)
        sx2 += sum(p[0]*p[0] for p in pairs)-sx*sx/len(pairs)
        sy2 += sum(p[1]*p[1] for p in pairs)-sy*sy/len(pairs)
        sxy += sum(p[0]*p[1] for p in pairs)-sx*sy/len(pairs)
    expected = sxy/math.sqrt(sx2*sy2)
    assert math.isclose(expected, agg['within_layout_correlation']['pearson'], rel_tol=1e-10)
    assert count == agg['within_layout_correlation']['n']
    assert len((OUT/'summary.md').read_text().splitlines()) == agg['summary_lines'] <= 90
    assert len(agg['A']) == 19 and len(agg['B']) == 3 and len(agg['C']) == 8 and len(agg['D']) == 19
    for group in agg['C']:
        gaps = [m['relative_absolute_gap'] for m in group['measures'] if m['relative_absolute_gap'] is not None]
        assert gaps == sorted(gaps, reverse=True)
    report = dict(games=len(original), game_side_rows=len(rows), previous_final_comparisons=len(previous_checks),
                  death_window_side_comparisons=death_checks, earlier_birth_near6_comparisons=old_births,
                  earlier_round_end_comparisons=old_snaps, within_layout_pearson_recomputed=expected,
                  phase_additivity_and_rates=True, maps_dimensions_match=True, head_on_pairs_balance=True, summary_lines=agg['summary_lines'], all_checks_passed=True)
    (OUT/'audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(report, ensure_ascii=False), flush=True)

if __name__ == '__main__':
    main()
