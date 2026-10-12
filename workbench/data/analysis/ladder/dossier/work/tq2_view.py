"""Scratch (diag-topqueen): one queen's turns from a scan file. Usage: python3 tq2_view.py <tag> <game> <side 0|1> [from] [to] [every]"""
import sys
import json
from pathlib import Path

W = Path('data/analysis/ladder/dossier/work')
tag, game, s = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
lo = int(sys.argv[4]) if len(sys.argv) > 4 else 0
hi = int(sys.argv[5]) if len(sys.argv) > 5 else 999
every = int(sys.argv[6]) if len(sys.argv) > 6 else 1
with open(W / ('tq2_scan-%s.jsonl' % tag)) as fh:
    for line in fh:
        if ('"game":%d,' % game) not in line:
            continue
        g = json.loads(line)
        w = g['w']
        print(g['game'], g['src'], g['map'], '%dx%d' % (w, g['h']), 'teams', g['t'], g['names'], 'win(side0)', g['win'], g['decided'], 'last', g['last'])
        print('start', [(c % w, c // w) for c in g['start']], 'fate', g['fate'][s])
        print('splits', g['splits'][s], 'attacks', g['attacks'][s], 'bodykills', g['bodykills'][s])
        print('snaps (queen len, own alive, longest, total):', {k: v[s] for k, v in g['snaps'].items()}, 'final', g['final'][s])
        print('rnd head L dstart own3 own5 en3steps(nq) nearestEnemySteps(len) act used Lafter ate(spawn/own/enemy) child longestOther ownN')
        for rec in g['recs'][s]:
            if lo <= rec[0] <= hi and (rec[0] % every == 0 or rec[27] > 0 or rec[28] > 0):
                print(rec[0], (rec[1] % w, rec[1] // w), rec[2], rec[3], rec[4], rec[5], rec[27], '%d(%d)' % (rec[9], rec[10]), 'MS-'[rec[19]], rec[20], rec[21],
                      '%d/%d/%d' % (rec[38], rec[39], rec[40]), rec[28], rec[42], rec[33], 'RAMMED' if rec[26] else '', 'DIED' if rec[25] else '')
