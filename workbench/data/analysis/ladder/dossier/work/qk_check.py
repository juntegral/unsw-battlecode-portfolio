"""Scratch (diag-queenkill): recount of qk_scan against two earlier, separately written counts.
1. Queen death round and cause, every side of every ladder and top1 game: per-game.jsonl / per-game-top1.jsonl (count_dossier.py).
2. Chances at a queen by a non-queen of length 4 or less on the 500 ladder games: at_scan-*.jsonl (diag-attack), rows whose target is a queen.
Usage: python3 qk_check.py"""
import json
from collections import Counter
from pathlib import Path

W = 'data/analysis/ladder/dossier/work/'
D = 'data/analysis/ladder/dossier/'


def load(tags):
    out = {}
    for tag in tags:
        p = Path(W + 'qk_scanf-' + tag + '.jsonl')
        if not p.exists():
            p = Path(W + 'qk_scan-' + tag + '.jsonl')
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            if line.strip():
                g = json.loads(line)
                out[g['game']] = g
    return out


def norm(q):
    if q is None:
        return None
    c = q['cause']
    c = 'head-on hit' if c == 'rammed' else 'head-on mover' if c == 'she rammed' else c
    return (q['r'], c)


def rowdeath(d):
    if d is None:
        return None
    c = d.get('cause')
    if c == 'head-on':
        c = 'head-on mover' if d.get('mover') else 'head-on'
    c = 'another body' if c == 'other dragon body' else c
    return (d['round'], c)


for name, tags, f in (('ladder', ('L0', 'L1', 'L2'), D + 'per-game.jsonl'), ('top1', ('T0', 'T1', 'T2'), D + 'target/per-game-top1.jsonl')):
    games = load(tags)
    same = diff = 0
    kinds = Counter()
    shown = 0
    for line in Path(f).read_text().splitlines():
        r = json.loads(line)
        g = games.get(r['game'])
        if g is None:
            continue
        s = 0 if r['relation'] == 'us' else 1
        mine = norm(g['qd'][s])
        theirs = rowdeath(r['queen']['death'])
        ok = (mine is None and theirs is None) or (mine is not None and theirs is not None and mine[0] == theirs[0] and (mine[1] == theirs[1] or theirs[1] == 'head-on' and mine[1].startswith('head-on') or theirs[1] == 'other' or mine[1] in ('no action', 'illegal split', 'unpaid sprint', 'timeout')))
        if ok:
            same += 1
        else:
            diff += 1
            kinds[(mine and mine[1], theirs and theirs[1])] += 1
            if shown < 5:
                shown += 1
                print('   differs', r['game'], s, mine, theirs, r['queen']['death'])
    print(name, 'games', len(games), 'queen fates equal', same, 'different', diff, dict(kinds))

games = load(('L0', 'L1', 'L2'))
mine = Counter()
for g in games.values():
    for r in g['chs']:
        if not r[4] and r[3] <= 4:
            mine[('turns', r[1])] += 1
            mine[('taken', r[1])] += r[18]
            mine[('plain turns', r[1])] += r[16] == 0
old = Counter()
n = 0
for k in range(5):
    p = Path(W + 'at_scan-%d.jsonl' % k)
    if not p.exists():
        continue
    for line in p.read_text().splitlines():
        if not line.strip():
            continue
        g = json.loads(line)
        n += 1
        for r in g['chs']:
            if r[8] == 1 and not r[4] and r[3] <= 4:
                old[('turns', r[1])] += 1
                old[('taken', r[1])] += r[22] == 1
                old[('plain turns', r[1])] += r[24] == 0
print('chances at a queen, mover a non-queen of 4 or less, 500 ladder games (side 0 ours, 1 theirs)')
print('   qk_scan', len(games), 'games', dict(sorted(mine.items())))
print('   at_scan', n, 'games', dict(sorted(old.items())))
