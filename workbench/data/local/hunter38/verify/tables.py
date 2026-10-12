#!/usr/bin/env python3
"""Tables from verify/deaths.json and verify/games.json (written by recount.py). Run from the repo root:
    python3 data/local/hunter38/verify/tables.py [deaths|maps|foe|claimD|head]
"""
import sys
sys.dont_write_bytecode = True
import json, os, statistics
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, 'deaths.json')))
G = json.load(open(os.path.join(HERE, 'games.json')))
what = sys.argv[1] if len(sys.argv) > 1 else 'deaths'
SOLO = ('wall', 'self', 'body', 'none')


def line(d):
    l = d['last']
    pre = d.get('pre') or {}
    return (f"{d['who']:3} {d['cause']:6} {d['file']:38} r{d['rnd']:3} len{d['len']} own={int(d['own_action'])} "
            f"act={l['what']}:{l['steps']} opt={d.get('opt_code')} "
            f"forced={int(d['forced'])} trapped_from={d['trapped_from']} ({d['trapped_actions']} actions) "
            f"kind={d['trap_kind']} pre={pre.get('rnd')}:{pre.get('what')}:{pre.get('steps')} ways={pre.get('ways')} "
            f"preopt={pre.get('opt')} dsp={d['dist_from_spawn']} nb={d['neigh_at_death']}")


if what == 'deaths':
    for run in ('hunter', 'plain'):
        print('=====', run)
        rows = [d for d in D if d['run'] == run and d['who'] == 'our' and d['cause'] in SOLO]
        for d in sorted(rows, key=lambda d: (d['map'], d['cause'], d['file'])):
            print(line(d))
        for cause in ('wall', 'self'):
            r = [d for d in rows if d['cause'] == cause]
            print(f"-- {run} {cause}: n={len(r)} forced={sum(d['forced'] for d in r)} "
                  f"forced_hard={sum(d['forced_hard'] for d in r)} before_r50={sum(d['rnd'] < 50 for d in r)} "
                  f"own_action={sum(d['own_action'] for d in r)} one_step={sum(d['n_steps'] == 1 for d in r)} "
                  f"trap_kind={dict(Counter(d['trap_kind'] for d in r))} "
                  f"by_arm={dict(Counter(d['arm'] for d in r))}")
elif what == 'last3':
    # the last three of her actions before each wall / own-body death that was not a spawn trap
    print('columns per action: round, action, what N E S W held (w wall, s self, f free, m/M mate body/head, x/X foe body/head), '
          'length, first steps with a way out')
    for run in ('hunter', 'plain'):
        rows = [d for d in D if d['run'] == run and d['who'] == 'our' and d['cause'] in ('wall', 'self', 'body')
                and d['trap_kind'] != 'trapped at spawn']
        tally = Counter()
        for d in sorted(rows, key=lambda d: (d['map'], d['file'])):
            h = d['room_hist'][-3:]
            closer = set()
            for x in h[-2:]:
                closer |= {c for c in x[3] if c in 'mMxX'}
            kind = 'mate' if closer & set('mM') and not closer & set('xX') else 'foe' if closer & set('xX') and not closer & set('mM') \
                else 'both' if closer else 'walls and herself only'
            tally[kind] += 1
            print(f"{run:6} {d['file']:36} r{d['rnd']:3} {d['cause']:4} len{d['len']} | "
                  + ' | '.join(f"r{x[0]} {x[4]} {x[3]} L{x[2]} ways={x[6] or '-'}" for x in h) + f" | blockers in the last two actions: {kind}")
        print(run, 'non-spawn wall/self/body deaths', len(rows), dict(tally))
elif what == 'foe':
    for run in ('hunter', 'plain'):
        print('=====', run, 'enemy queen (hunter in the hunter run, plain main in the check run)')
        rows = [d for d in D if d['run'] == run and d['who'] == 'foe']
        print('  causes', dict(Counter(d['cause'] for d in rows)), 'games', sum(g['run'] == run for g in G))
        for d in sorted([d for d in rows if d['cause'] in SOLO], key=lambda d: (d['map'], d['cause'], d['file'])):
            print(line(d))
elif what == 'maps':
    for run in ('hunter', 'plain'):
        print('=====', run)
        maps = sorted({g['map'] for g in G if g['run'] == run})
        for m in maps:
            gs = [g for g in G if g['run'] == run and g['map'] == m]
            for who in ('our', 'foe'):
                ds = [d for d in D if d['run'] == run and d['map'] == m and d['who'] == who]
                solo = sorted(d['rnd'] for d in ds if d['cause'] in ('wall', 'self'))
                c = Counter(d['cause'] for d in ds)
                spawn = sum(d['trap_kind'] == 'trapped at spawn' for d in ds if d['cause'] in ('wall', 'self'))
                print(f"{m:22} {who} games={len(gs)} size={gs[0]['W']}x{gs[0]['H']} our_spawn_len={gs[0]['spawn_len']} deaths={dict(c)} "
                      f"wall/self rounds={solo} of those trapped at spawn={spawn}")
elif what == 'head':
    # headon deaths: whose action, and what "forced" would mean there
    for run in ('hunter', 'plain'):
        rows = [d for d in D if d['run'] == run and d['who'] == 'our' and d['cause'] == 'headon']
        print(run, 'headon', len(rows), 'during her own action', sum(d['own_action'] for d in rows),
              'during an enemy action', sum((not d['own_action']) and d['mover_team'] != d.get('team') for d in rows),
              'mover is the enemy queen', sum(d['mover_is_queen'] and not d['own_action'] for d in rows),
              'forced at her own last action', sum(d['forced'] for d in rows))
elif what == 'claimD':
    def mean(v):
        v = [x for x in v if x is not None]
        return round(statistics.mean(v), 2) if v else None
    for run in ('hunter', 'plain'):
        print('=====', run)
        for label, pick in (('all', lambda g: True), ('ended on the queen rule', lambda g: g['how'] == 'queen'),
                            ('trauma', lambda g: g['map'] == 'trauma'), ('schooltime', lambda g: g['map'] == 'schooltime')):
            for arm in ('base', 'candidate'):
                gs = [g for g in G if g['run'] == run and g['arm'] == arm and pick(g)]
                if not gs:
                    continue
                print(f"{label:24} {arm:9} n={len(gs)} wins={sum(g['win'] for g in gs)} "
                      f"our len r100/r200/r300/end={mean(g['our_queen_len_r100'] for g in gs)}/{mean(g['our_queen_len_r200'] for g in gs)}/"
                      f"{mean(g['our_queen_len_r300'] for g in gs)}/{mean(g['our_queen_final'] for g in gs)} "
                      f"foe len r100/r200/r300/end={mean(g['foe_queen_len_r100'] for g in gs)}/{mean(g['foe_queen_len_r200'] for g in gs)}/"
                      f"{mean(g['foe_queen_len_r300'] for g in gs)}/{mean(g['foe_queen_final'] for g in gs)} "
                      f"our eats <300={sum(g['our_queen_eats_before300'] for g in gs)} >=300={sum(g['our_queen_eats_from300'] for g in gs)} "
                      f"foe eats <300={sum(g['foe_queen_eats_before300'] for g in gs)} >=300={sum(g['foe_queen_eats_from300'] for g in gs)} "
                      f"our alive={sum(g['our_queen_alive'] for g in gs)} foe alive={sum(g['foe_queen_alive'] for g in gs)}")
        print('-- per game, games ended on the queen rule and trauma')
        for g in sorted(G, key=lambda g: (g['map'], g['seed'], g['side'], g['arm'])):
            if g['run'] != run or not (g['how'] == 'queen' or g['map'] == 'trauma'):
                continue
            print(f"{g['file']:36} how={g['how']:7} win={g['win']} our r100={g['our_queen_len_r100']} r300={g['our_queen_len_r300']} "
                  f"end={g['our_queen_final']} eats<300={g['our_queen_eats_before300']} eats>=300={g['our_queen_eats_from300']} "
                  f"splits={g['our_queen_splits']} | foe r100={g['foe_queen_len_r100']} r300={g['foe_queen_len_r300']} "
                  f"end={g['foe_queen_final']} eats<300={g['foe_queen_eats_before300']} eats>=300={g['foe_queen_eats_from300']} "
                  f"splits={g['foe_queen_splits']}")
        print('-- how the games ended', dict(Counter((g['arm'], g['how']) for g in G if g['run'] == run)))
        print('-- wins by how', dict(Counter((g['arm'], g['how']) for g in G if g['run'] == run and g['win'])))
