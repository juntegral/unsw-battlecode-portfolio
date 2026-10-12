#!/usr/bin/env python3
"""Table of queen-company counts: baseline arm against test arm(s) on the games both have (same map, seed, side).
Usage: python3 qh_table.py <base arm> <arm> [<arm> ...] [all]   ('all' = every game of each arm, not only the shared ones)"""
import sys
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BN = ('r0-50', 'r51-100', 'r101-300', 'r301+')


def rows(arm):
    p = HERE / ('rows-' + arm + '.jsonl')
    return {r['game']: r for r in map(json.loads, p.read_text().splitlines())} if p.exists() else {}


def snap(r, rr):
    s = r['snaps']
    return s.get(str(rr)) or s[str(r['rounds'])]


def summ(rs):
    n = len(rs)
    o = {'games': n}
    if not n:
        return o
    for b in range(4):
        T = sum(r['bands'][b]['turns'] for r in rs)
        f = lambda k: sum(r['bands'][b][k] for r in rs)
        rn = f('rank_n')
        hn = f('hrank_n')
        o['depth ' + BN[b]] = '%.2f' % (f('rank') / rn) if rn else '-'
        o['home-rank ' + BN[b]] = '%.2f' % (f('hrank') / hn) if hn else '-'
        o['own3 ' + BN[b]] = '%.2f' % (f('own3') / T) if T else '-'
        o['own5 ' + BN[b]] = '%.2f' % (f('own5') / T) if T else '-'
        o['alone5 % ' + BN[b]] = '%.0f' % (100 * f('alone5') / T) if T else '-'
        o['e3 per 100 turns ' + BN[b]] = '%.1f (%d/%d)' % (100 * f('e3') / T, f('e3'), T) if T else '-'
        o['pearls per 100 turns ' + BN[b]] = '%.1f' % (100 * f('pearls') / T) if T else '-'
        o['tiles from start ' + BN[b]] = '%.1f' % (f('home') / T) if T else '-'
        o['her length ' + BN[b]] = '%.1f' % (f('len') / T) if T else '-'
    T = sum(b['turns'] for r in rs for b in r['bands'])
    o['e3 per 100 turns all'] = '%.1f (%d/%d)' % (100 * sum(b['e3'] for r in rs for b in r['bands']) / T,
                                                  sum(b['e3'] for r in rs for b in r['bands']), T)
    ch = [c for r in rs for c in r['chases']]
    o['chases a game'] = '%.2f (%d)' % (len(ch) / n, len(ch))
    if ch:
        o['chases starting with no mate within 5 %'] = '%.0f (%d/%d)' % (100 * sum(c['n5'] == 0 for c in ch) / len(ch),
                                                                         sum(c['n5'] == 0 for c in ch), len(ch))
        o['turns per chase'] = '%.1f' % (sum(c['turns'] for c in ch) / len(ch))
        o['chases of 4+ turns %'] = '%.0f' % (100 * sum(c['turns'] >= 4 for c in ch) / len(ch))
        o['chases with a mate ramming a pursuer'] = '%d' % sum(c['mate_ram'] > 0 for c in ch)
        o['chases ending in her death'] = '%d' % sum(c['end'] != 'lost' for c in ch)
    for rr in (100, 150):
        o['queen alive r%d' % rr] = '%d/%d' % (sum(1 for r in rs if not r['death'] or r['death']['r'] > rr), n)
    o['queen alive end'] = '%d/%d' % (sum(1 for r in rs if not r['death']), n)
    for how in ('rammed', 'boxed', 'dead_end', 'into_head'):
        o['died: ' + how] = '%d' % sum(1 for r in rs if r['death'] and r['death']['how'] == how)
    o['pearls she eats a game'] = '%.1f' % (sum(b['pearls'] for r in rs for b in r['bands']) / n)
    for rr in (100, 300):
        o['own dragons r%d' % rr] = '%.1f' % (sum(snap(r, rr)['own'] for r in rs) / n)
        o['own total length r%d' % rr] = '%.1f' % (sum(snap(r, rr)['total'] for r in rs) / n)
    o['won'] = '%d/%d' % (sum(1 for r in rs if ('winner=%s' % r['game'][-1]) in r['result']), n)
    return o


def main():
    args = [a for a in sys.argv[1:] if a != 'all']
    every = 'all' in sys.argv
    base = rows(args[0])
    cols = []
    for arm in args[1:]:
        t = rows(arm)
        shared = sorted(set(base) & set(t))
        cols.append((args[0] + ' on ' + arm + ' games', summ([base[g] for g in shared])))
        cols.append((arm, summ([t[g] for g in (sorted(t) if every else shared)])))
    if every or len(args) == 1:
        cols.insert(0, (args[0] + ' all', summ(list(base.values()))))
    keys = []
    for _, o in cols:
        for k in o:
            if k not in keys:
                keys.append(k)
    print('| measure | ' + ' | '.join(c for c, _ in cols) + ' |')
    print('|---|' + '---|' * len(cols))
    for k in keys:
        print('| ' + k + ' | ' + ' | '.join(str(o.get(k, '')) for _, o in cols) + ' |')


main()
