"""Scratch (diag-theirqueen): per game, the share of the queen's turns in rounds 0-100 spent more than R+2 tiles from her start,
against her fate. R = min(8, (w + h) // 8). Open-start games. Usage: python3 tq_pg.py [online|ladder]"""
import sys
import json
from collections import defaultdict
from pathlib import Path

W = Path('data/analysis/ladder/dossier/work')


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'online'
    tags = ('m1', 'm2', 'b1', 'b2', 'q1') if mode == 'online' else ('L0', 'T0')
    games = []
    for t in tags:
        p = W / ('tq_scan-%s.jsonl' % t)
        if p.exists():
            games += [json.loads(x) for x in p.read_text().splitlines() if x]
    rows = defaultdict(list)
    bymap = defaultdict(lambda: defaultdict(list))
    lay = defaultdict(lambda: defaultdict(list))
    for g in games:
        R = min(8, (g['w'] + g['h']) // 8)
        for s in (0, 1):
            if g['scomp'][s] * 2 < g['cells']:
                continue
            ts = [t for t in g['recs'][s] if t[0] <= 100]
            if len(ts) < 30:
                continue
            frac = sum(1 for t in ts if t[3] > R + 2) / len(ts)
            f = g['fate'][s]
            dead150 = f is not None and f['r'] <= 150
            dead300 = f is not None and f['r'] <= 300
            won = g['win'] is not None and (g['win'] == 1) == (s == 0)
            if mode == 'online':
                who = 'ours' if s == 0 else ('Bob' if g['opp'].startswith('Big') else 'Quiz')
            else:
                who = ('ours ladder', 'ladder opp') [s] if g['label'] == 'ladder' else ('rank1', 'rank1 opp')[s]
            rows[who].append((frac, dead150, dead300, won, f is None))
            lay[who][(g.get('layout') or g['map'], g['w'], g['h'], g.get('opp'))].append((frac, dead150, dead300, won, f is None, g['game']))
            bymap[who][g['map']].append((frac, dead150, f is None))
    for who, v in sorted(rows.items()):
        print('%s: %d games with 30+ queen turns by round 100' % (who, len(v)))
        for name, lo, hi in (('under 20% of turns outside', 0.0, 0.2), ('20-60%', 0.2, 0.6), ('over 60%', 0.6, 1.01)):
            x = [r for r in v if lo <= r[0] < hi]
            if x:
                n = len(x)
                print('   %-28s games %3d | dead by r150 %3d (%2.0f%%) | dead by r300 %3d (%2.0f%%) | alive at the end %3d | side won %3d (%2.0f%%)' % (
                    name, n, sum(r[1] for r in x), 100.0 * sum(r[1] for r in x) / n, sum(r[2] for r in x), 100.0 * sum(r[2] for r in x) / n,
                    sum(r[4] for r in x), sum(r[3] for r in x), 100.0 * sum(r[3] for r in x) / n))
    for who, d in sorted(lay.items()):
        lo, hi = [], []
        for key, v in d.items():
            if len(v) < 4:
                continue
            v = sorted(v, key=lambda r: (r[0], r[5]))
            half = len(v) // 2
            lo += v[:half]
            hi += v[len(v) - half:]
        if lo:
            n = len(lo)
            print('%s within layout (and opponent): the half of games with her LESS outside vs MORE outside, %d games each: outside share %2.0f%% vs %2.0f%% | dead by r150 %d vs %d | dead by r300 %d vs %d | alive at the end %d vs %d | side won %d vs %d' % (
                who, n, 100.0 * sum(r[0] for r in lo) / n, 100.0 * sum(r[0] for r in hi) / n, sum(r[1] for r in lo), sum(r[1] for r in hi),
                sum(r[2] for r in lo), sum(r[2] for r in hi), sum(r[4] for r in lo), sum(r[4] for r in hi), sum(r[3] for r in lo), sum(r[3] for r in hi)))
    if mode == 'online':
        print('by layout: mean share outside in r0-100 / dead by r150 / games, ours | Bob | Quiz')
        for m in sorted(bymap['ours']):
            cells = []
            for who in ('ours', 'Bob', 'Quiz'):
                x = bymap[who].get(m, [])
                cells.append('%3.0f%% %2d/%-2d' % (100.0 * sum(r[0] for r in x) / max(1, len(x)), sum(r[1] for r in x), len(x)))
            print('   %-18s %s' % (m[:18], ' | '.join(cells)))


main()
