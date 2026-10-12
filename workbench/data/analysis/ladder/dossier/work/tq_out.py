"""Scratch (diag-theirqueen): what a leash to the start tile would touch and cost, on tq_scan-*.jsonl.
R = min(8, (w + h) // 8) tiles (torus Manhattan from the queen's start tile). Open-start games only unless 'all'.
Usage: python3 tq_out.py [online|ladder] [all] [list]"""
import sys
import json
from collections import Counter, defaultdict
from pathlib import Path

W = Path('data/analysis/ladder/dossier/work')
F = dict(r=0, head=1, L=2, ds=3, o3=4, o5=5, e3m=6, e5m=7, ep3=8, ne=9, neL=10, nem=11, nom=12, kc=13, fx=14, pk=15, mn=16, inr=17, ob2=18,
         act=19, steps=20, La=21, ate=22, end=23, da=24, died=25, hit=26, ep3n=27, child=28, sep=29, db=30, ep5n=31, o3c=32, nown=33, nen=34,
         pd=35, p3=36, ep3s=37)
ARM = {'agg7-m1': 'MAIN', 'agg7-m2': 'MAIN', 'agg7-b1': 'B7', 'agg7-b2': 'B7', 'agg8-q1': 'B7Q'}
CAUSE = ('wall', 'own body', 'other body', 'head-on', 'other')


def man(a, b, w, h):
    dx = abs(a % w - b % w)
    dy = abs(a // w - b // w)
    return min(dx, w - dx) + min(dy, h - dy)


def leash(g):
    return min(8, (g['w'] + g['h']) // 8)


def xy(c, g):
    return '(%d,%d)' % (c % g['w'], c // g['w'])


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'online'
    every = 'all' in sys.argv
    tags = ('m1', 'm2', 'b1', 'b2', 'q1') if mode == 'online' else ('L0', 'T0')
    games = []
    for t in tags:
        p = W / ('tq_scan-%s.jsonl' % t)
        if p.exists():
            games += [json.loads(x) for x in p.read_text().splitlines() if x]
    groups = defaultdict(list)
    for g in games:
        if mode == 'online':
            arm = ARM[g['label']]
            opp = 'Bob' if g['opp'].startswith('Big') else 'Quiz'
            for a in (arm, 'ALL'):
                groups[a + ' ours'].append((g, 0))
                groups[a + ' ' + opp].append((g, 1))
        elif g['label'] == 'ladder':
            groups['ours ladder'].append((g, 0))
            groups['ladder opp'].append((g, 1))
        else:
            groups['rank1'].append((g, 0))
            groups['rank1 opp'].append((g, 1))
    for name in sorted(groups):
        v = [(g, s) for g, s in groups[name] if every or g['scomp'][s] * 2 >= g['cells']]
        c = Counter()
        for g, s in v:
            R = leash(g)
            w, h = g['w'], g['h']
            recs = g['recs'][s]
            c['games'] += 1
            for t in recs:
                c['turns'] += 1
                ds = t[F['ds']]
                c['out'] += 1 if ds > R else 0
                c['out2'] += 1 if ds > R + 2 else 0
                c['ate'] += t[F['ate']]
                end = t[F['end']]
                if end < 0:
                    continue
                de = man(end, g['start'][s], w, h)
                if t[F['ate']] and de > R + 1:
                    c['ate_out'] += t[F['ate']]
                if t[F['ate']] and de > R:
                    c['ate_outR'] += t[F['ate']]
                if de > ds and de > R:
                    c['step_out'] += 1
                    if t[F['ate']]:
                        c['so_ate'] += 1
                    elif len(t) > F['pd']:
                        pd = t[F['pd']]
                        c['so_p3' if pd <= 3 else 'so_p8' if pd <= 8 else 'so_none'] += 1
                    if t[F['ep5n']] > 0:
                        c['so_enemy5'] += 1
                elif de < ds and ds > R:
                    c['step_in'] += 1
            f = g['fate'][s]
            if f is not None:
                kind = 'self' if f['own_move'] else 'ram' if f['mside'] != s else 'mate'
                c['dead'] += 1
                c[kind] += 1
                c[kind + '_out'] += 1 if f['ds'] > R else 0
                c[kind + '_out2'] += 1 if f['ds'] > R + 2 else 0
                if f['ds'] > R + 2:
                    c['dead_out2'] += 1
                    c['dead_out2_lost'] += 1 if (g['win'] == 1) != (s == 0) else 0
                    c['dead_out2_q'] += 1 if g['decided'] == 'queen' and (g['win'] == 1) != (s == 0) else 0
                    c['dead_out2_qalive'] += 1 if g['final'][1 - s][0] > 0 else 0
        n = max(1, c['turns'])
        print('%-12s games %3d turns %6d | beyond R %2.0f%% beyond R+2 %2.0f%% | pearls %d (%.1f/g), eaten beyond R %d, beyond R+1 %d (%.1f/g) | steps outward beyond R %d: pearl eaten %d, pearl <=3 steps %d, 4-8 %d, none in 8 %d; enemy head <=5 steps %d | steps inward %d' % (
            name, c['games'], c['turns'], 100.0 * c['out'] / n, 100.0 * c['out2'] / n, c['ate'], c['ate'] / max(1, c['games']), c['ate_outR'], c['ate_out'],
            c['ate_out'] / max(1, c['games']), c['step_out'], c['so_ate'], c['so_p3'], c['so_p8'], c['so_none'], c['so_enemy5'], c['step_in']))
        print('             deaths %d: rammed %d (beyond R %d, R+2 %d), own move %d (%d, %d), by a mate %d | beyond R+2: %d deaths, game lost %d (on queen length %d), other queen alive at the end %d' % (
            c['dead'], c['ram'], c['ram_out'], c['ram_out2'], c['self'], c['self_out'], c['self_out2'], c['mate'], c['dead_out2'], c['dead_out2_lost'],
            c['dead_out2_q'], c['dead_out2_qalive']))
    if 'list' in sys.argv:
        for g in games:
            if mode == 'online' and ARM[g['label']] != 'B7Q':
                continue
            f = g['fate'][0]
            if f is None:
                continue
            R = leash(g)
            recs = g['recs'][0]
            last_in = max((t[0] for t in recs if t[F['ds']] <= R), default=-1)
            other = g['recs'][1]
            od = next((t[F['ds']] for t in reversed(other) if t[0] <= f['r']), None)
            print('%d %-16s %2dx%-2d R%d open %d | r%-3d %-10s L%d at %s, %d tiles from start %s; last inside R at r%d; own heads <=5: %d | their queen %s tiles from her start | %s %s' % (
                g['game'], g['map'][:16], g['w'], g['h'], R, int(g['scomp'][0] * 2 >= g['cells']), f['r'], 'own:' + CAUSE[min(f['reason'], 4)] if f['own_move'] else 'rammed',
                f['L'], xy(f['head'], g), f['ds'], xy(g['start'][0], g), last_in, f['o5'], od, 'won' if g['win'] == 1 else 'lost', g['decided']))


main()
