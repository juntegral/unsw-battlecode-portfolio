"""Scratch (diag-opening2): table of the forward what-if (o2_sim-*.jsonl). Usage: python3 .../o2_simagg.py [paths <layout prefix>]"""
import sys, json
sys.dont_write_bytecode = True
from pathlib import Path
from collections import defaultdict, Counter
from statistics import median

WORK = Path('data/analysis/ladder/dossier/work')


def mean(v):
    return sum(v) / len(v) if v else float('nan')


def main():
    games = []
    for f in ('o2_sim-O0.jsonl', 'o2_sim-L0.jsonl'):
        for line in (WORK / f).read_text().splitlines():
            g = json.loads(line)
            if g['k'] == 'g':
                games.append(g)
    if len(sys.argv) > 2 and sys.argv[1] == 'paths':
        for g in games:
            if g['map'].startswith(sys.argv[2]):
                print(g['src'], g['arm'], g['gid'], 'real pearls by r40', sum(1 for e in g['eats'][str(g['me'])] if e[0] <= 40))
                for v, s in g['sim'].items():
                    print('    %-14s %s eats %s portal %s dead %s' % (v, s['path'], s['eats'], s['portal'], s['dead']))
        return
    acc = defaultdict(lambda: defaultdict(list))
    for g in games:
        grp = ('O ' + g['arm']) if g['src'] == 'O' else 'L ours'
        real = [e[0] for e in g['eats'][str(g['me'])]]
        base = g['sim']['base']['path']
        for name in ('%s %dx%d' % (g['map'], g['w'], g['h']), 'ALL'):
            for grp2 in (grp, 'O all' if g['src'] == 'O' else None):
                if grp2 is None:
                    continue
                a = acc[(grp2, name, 'REAL')]
                a['first'].append(real[0] if real else 99)
                a['p20'].append(sum(1 for x in real if x <= 20))
                a['p40'].append(sum(1 for x in real if x <= 40))
                for v, s in g['sim'].items():
                    a = acc[(grp2, name, v)]
                    a['first'].append(s['eats'][0] if s['eats'] else 99)
                    a['p20'].append(sum(1 for x in s['eats'] if x <= 20))
                    a['p40'].append(sum(1 for x in s['eats'] if x <= 40))
                    a['portal10'].append(1 if any(x <= 10 for x in s['portal']) else 0)
                    a['portal20'].append(1 if any(x <= 20 for x in s['portal']) else 0)
                    a['dead'].append(1 if s['dead'] >= 0 else 0)
                    a['cd20'].append(s['cd20'] if s['cd20'] >= 0 else 0)
                    diff = [k for k in range(min(len(base), len(s['path']))) if base[k] != s['path'][k]]
                    a['differs'].append(1 if diff else 0)
                    a['first diff'].append(diff[0] if diff else 99)
                    a['changed'].append(len(diff))
    print('group | layout | variant | games | first pearl, median round | pearls by r20, r40 | through a portal by r10, r20 | dead by r40 | centre distance r20 | path differs from base in games; first at round (median); steps that differ a game')
    for (grp, name, v), a in sorted(acc.items()):
        n = len(a['first'])
        if v == 'REAL':
            print('%-8s | %-24s | %-14s | %3d | r%s | %.2f, %.2f |' % (grp, name, v, n, median(a['first']), mean(a['p20']), mean(a['p40'])))
        else:
            print('%-8s | %-24s | %-14s | %3d | r%s | %.2f, %.2f | %.0f%%, %.0f%% | %.0f%% | %.1f | %d; r%s; %.1f' % (
                grp, name, v, n, median(a['first']), mean(a['p20']), mean(a['p40']), 100 * mean(a['portal10']), 100 * mean(a['portal20']),
                100 * mean(a['dead']), mean(a['cd20']), sum(a['differs']), median(a['first diff']), mean(a['changed'])))


main()
