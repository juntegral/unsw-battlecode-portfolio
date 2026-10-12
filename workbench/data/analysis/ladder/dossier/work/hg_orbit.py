# Scratch (diag-hungry): hungry turns spent beside or near a pearl that counts as a target (hg_scan3 rows).
#   A. a pearl on a step on offer (not in the leader zone): eaten that turn or not, and what the pearl step carries
#      (a team mate's head beside it: 450 off, main.cpp 5142-5144; tight / trapped / no tail: 5042-5052).
#   B. runs of turns in a row with a target pearl within 3 steps and no meal: lengths, how they end, what the step
#      toward the pearl carries on those turns.
# Usage: python3 data/analysis/ladder/dossier/work/hg_orbit.py <arm|test>
import sys, json
sys.dont_write_bytecode = True
from collections import defaultdict, Counter
from pathlib import Path

WORK = 'data/analysis/ladder/dossier/work/'


def pct(a, b):
    return '%.1f%%' % (100.0 * a / b) if b else '-'


def carries(v):
    out = []
    if v[7]:
        out.append('mate head beside')
    cr = v[9]
    if cr >= 5000:
        out.append('trapped')
    elif cr >= 1000 or (cr > 0 and cr != 600):
        out.append('tight')
    elif cr == 600:
        out.append('no tail')
    return ' + '.join(out) if out else 'nothing rebuilt'


def main():
    arm = sys.argv[1]
    names = [WORK + 'hg_scan3-test.jsonl'] if arm == 'test' else [WORK + 'hg_scan3-%s-%d.jsonl' % (arm, s) for s in range(4)]
    n_all = 0
    A = Counter()
    A_why = Counter()
    A_eat = Counter()
    runs = []
    near_carry = Counter()
    for nm in names:
        cur = {}
        with open(nm) as f:
            for line in f:
                r = json.loads(line)
                if r.get('kind') == 'game':
                    for v in cur.values():
                        runs.append(v)
                    cur = {}
                    continue
                n_all += 1
                legal = [d for d in range(4) if r['dirs'][d] is not None]
                eatd = [d for d in legal if r['dirs'][d][6]]
                if eatd:
                    A['pearl on a step on offer'] += 1
                    A['... eaten'] += r['ate']
                    why = carries(r['dirs'][eatd[0]])
                    if len(eatd) > 1:
                        best = min(eatd, key=lambda d: (r['dirs'][d][7], r['dirs'][d][9]))
                        why = carries(r['dirs'][best])
                    A_eat[why] += 1
                    if not r['ate']:
                        A_why[why + (' (enemy head in view)' if r['ne'] else '')] += 1
                dps = [r['dirs'][d][2] for d in legal if r['dirs'][d][2] >= 0]
                near = bool(dps) and min(dps) <= 3
                k = r['i']
                run = cur.get(k)
                if near:
                    if run is None or r['r'] != run['last'] + 1:
                        if run is not None:
                            runs.append(run)
                        run = dict(n=0, last=r['r'], ate=0, carry=Counter())
                        cur[k] = run
                    run['n'] += 1
                    run['last'] = r['r']
                    run['ate'] = r['ate']
                    bd = min((d for d in legal if r['dirs'][d][2] >= 0), key=lambda d: r['dirs'][d][2])
                    run['carry'][carries(r['dirs'][bd])] += 1
                    if r['ate']:
                        runs.append(run)
                        cur.pop(k)
                elif run is not None:
                    runs.append(run)
                    cur.pop(k)
        for v in cur.values():
            runs.append(v)
    print('hungry turns', n_all)
    print('\n== A. a pearl on a step on offer')
    print('  turns %d, eaten that turn %s' % (A['pearl on a step on offer'], pct(A['... eaten'], A['pearl on a step on offer'])))
    print('  what the pearl step carries, all such turns:', [(k, v, pct(v, A['pearl on a step on offer'])) for k, v in A_eat.most_common()])
    tot = sum(A_why.values())
    print('  not eaten %d:' % tot, [(k, v, pct(v, tot)) for k, v in A_why.most_common()])
    print('\n== B. runs with a target pearl within 3 steps')
    turns = sum(x['n'] for x in runs)
    print('  runs %d, turns %d (%s of hungry turns), ended by a meal %s' % (len(runs), turns, pct(turns, n_all), pct(sum(x['ate'] for x in runs), len(runs))))
    for lo, hi in ((1, 3), (4, 7), (8, 15), (16, 999)):
        sel = [x for x in runs if lo <= x['n'] <= hi]
        t = sum(x['n'] for x in sel)
        c = Counter()
        for x in sel:
            c.update(x['carry'])
        print('  runs of %d-%d turns: %d runs, %d turns (%s of hungry turns), ended by a meal %s; the step toward the pearl carries: %s' % (
            lo, hi, len(sel), t, pct(t, n_all), pct(sum(x['ate'] for x in sel), len(sel)), ', '.join('%s %s' % (k, pct(v, t)) for k, v in c.most_common())))


main()
