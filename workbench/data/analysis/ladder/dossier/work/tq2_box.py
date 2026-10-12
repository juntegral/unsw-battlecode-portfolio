"""Scratch (diag-topqueen): queen deaths on her own move (wall, own body, another body, no valid action): was any tile beside her
head free at the start of that turn? (0 free = boxed in, not a choice.) Also deaths by round 30 by cause. Reads tq2_scan-*.jsonl."""
import json
from collections import Counter, defaultdict
from pathlib import Path

W = Path('data/analysis/ladder/dossier/work')
FILES = ['top3-0', 'top3-1', 't91-0', 't91-1', 't264-0', 't264-1', 't306-0', 't306-1', 't842-0', 't454-0', 't0-0', 't0-1', 'q1', 'm1', 'm2', 'm3', 'l1', 'l2']
NAMED = (454, 157, 306, 70, 91, 264, 842, 545, 19, 87)


def arm_of(g, s):
    src = g['src']
    t = g['t'][s]
    if src == 'top3':
        return 'f%d' % t if t in NAMED else 'fopp'
    if src == 'top1':
        return 'o%d' % t if t in NAMED else 'oopp'
    lab = {'agg8-q1': 'B7Q', 'agg7-m1': 'MAIN', 'agg7-m2': 'MAIN', 'agg7-m3': 'MAIN', 'top-l1': 'L1', 'top-l2': 'L2'}[src]
    if s == 0:
        return lab
    return 'v%d' % t if lab in ('L1', 'L2') else 'x' + lab


C = defaultdict(Counter)
for tag in FILES:
    p = W / ('tq2_scan-%s.jsonl' % tag)
    if not p.exists():
        continue
    with open(p) as fh:
        for line in fh:
            if not line.strip():
                continue
            g = json.loads(line)
            for s in (0, 1):
                c = C[arm_of(g, s)]
                c['games'] += 1
                f = g['fate'][s]
                if f is None:
                    continue
                c['deaths'] += 1
                if f['own_move'] and f['reason'] != 3:
                    last = g['recs'][s][-1]
                    kind = ('wall', 'own body', 'other body', '', 'no valid action')[f['reason']]
                    c['own'] += 1
                    c['own_' + kind] += 1
                    c['own_free0'] += int(last[14] == 0)
                    c['own_free1'] += int(last[14] >= 1)
                    c['own_thr'] += int(last[27] > 0)
                    c['own_r30'] += int(f['r'] <= 30)
                    c['own_r30_free0'] += int(f['r'] <= 30 and last[14] == 0)
                    c['own_mates63'] += int(f['mates'] >= 63)
                elif f['own_move']:
                    c['intohead'] += 1
                else:
                    c['rammed'] += 1
                    c['rammed_L2'] += int(f['L'] <= 2)
                    c['rammer_L2'] += int(f.get('mL', 9) <= 2)
                    c['rammer_L3'] += int(f.get('mL', 9) == 3)
                    c['rammer_steps1'] += int(f.get('msteps', 9) <= 1)
print('arm | games | deaths | rammed (she 2 long; rammer 2 long, 3 long; rammer moved 1 step) | ran into a head | other deaths on her move: n = wall/own body/other body/no valid action | of those with no free tile beside her head at turn start; with one or more | with an enemy head within 3 steps | by r30 (of which no free tile) | team at 64 dragons')
for a in ('f454', 'f70', 'f306', 'f157', 'f91', 'f545', 'f19', 'fopp', 'o306', 'o91', 'o264', 'o842', 'oopp', 'v157', 'v306', 'v454', 'v87', 'xB7Q', 'xMAIN', 'B7Q', 'L1', 'L2', 'MAIN'):
    c = C.get(a)
    if c is None:
        continue
    print(a, '|', c['games'], '|', c['deaths'], '|', c['rammed'], '(%d; %d, %d; %d)' % (c['rammed_L2'], c['rammer_L2'], c['rammer_L3'], c['rammer_steps1']), '|', c['intohead'], '|',
          '%d = %d/%d/%d/%d' % (c['own'], c['own_wall'], c['own_own body'], c['own_other body'], c['own_no valid action']), '|', c['own_free0'], c['own_free1'], '|', c['own_thr'], '|',
          '%d (%d)' % (c['own_r30'], c['own_r30_free0']), '|', c['own_mates63'])
