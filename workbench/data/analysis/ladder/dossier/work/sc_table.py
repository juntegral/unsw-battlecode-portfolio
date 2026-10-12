# Scratch (diag-sacrifice): the final kinds table. Their deaths by no valid action (all three labels) and their
# same-team head-ons, rounds 0-300, 500 games, sorted into eight kinds; one line of facts per kind.
# Usage: python3 data/analysis/ladder/dossier/work/sc_table.py
import sys, json
from collections import Counter, defaultdict
from statistics import median
from pathlib import Path

W = 'data/analysis/ladder/dossier/work/'
games = []
for n in range(4):
    for line in Path(W + 'sc_ev-%d.jsonl' % n).read_text().splitlines():
        if line:
            games.append(json.loads(line))


def win(r):
    return 0 if r <= 100 else 1 if r <= 200 else 2


rows = defaultdict(list)
label = Counter()
for g in games:
    hi = g['rating'] >= 2100
    by = {}
    for d in g['events']:
        if d['reason'] == 3:
            by[d['r'], d['id']] = d
    for d in g['events']:
        if d['side'] != 't' or d['r'] > 300:
            continue
        d['hi'] = hi
        d['team'] = g['opponent']
        if d['reason'] == 4:
            label[d['cause'], win(d['r']), 'boxed' if d['free'] == 0 else 'free'] += 1
            if d['free'] == 0:
                k = 'K1 boxed, front left by a split' if d['split_r'] >= 0 and d['r'] - d['split_r'] <= 1 else 'K2 boxed, other'
            elif d['n_side'] + 1 >= 60:
                k = 'K3 by choice, team at 60+'
            elif d['q_alive'] and 0 <= d['q_dist'] <= 4 and d['q_len'] > d['L']:
                k = 'K4 by choice, under 60, beside queen'
            elif d['tgt'][0] >= 0 and d['tgt'][2] <= 4 and d['tgt'][1] >= 2 * d['L']:
                k = 'K5 by choice, under 60, beside 2x mate'
            else:
                k = 'K6 by choice, under 60, other'
            rows[k].append([d])
        elif d.get('st') and d['mover']:
            k = 'K7 same-team head-on, mover boxed' if d['free'] <= 1 else 'K8 same-team head-on, other'
            rows[k].append([d, by[d['r'], d['o_id']]])

print('labels of their deaths by no valid action, r0-100 / 101-200 / 201-300, boxed and free:')
for c in ('noact', 'split', 'sprint', 'timeout'):
    print('  %-8s boxed %s  free %s' % (c, '/'.join(str(label[c, k, 'boxed']) for k in range(3)), '/'.join(str(label[c, k, 'free']) for k in range(3))))
b0, f0 = label['noact', 0, 'boxed'], label['noact', 0, 'free']
print('  no action r0-100: boxed share %.1f%%; r101-300: %.1f%%' % (100 * b0 / (b0 + f0),
      100 * (label['noact', 1, 'boxed'] + label['noact', 2, 'boxed']) / sum(label['noact', k, x] for k in (1, 2) for x in ('boxed', 'free'))))
print()
total = sum(len(v) for v in rows.values())
for k in sorted(rows):
    ev = rows[k]
    first = [e[0] for e in ev]
    every = [d for e in ev for d in e]
    n = len(ev)
    eat = Counter()
    drop = 0
    waits = []
    for d in every:
        drop += d['np']
        for es, wait, eid, elen, isq, istop in d['p']:
            if es != 't':
                eat['ours'] += 1
            else:
                eat['queen' if isq else 'longest' if istop else 'own 5+' if elen >= 5 else 'own 2-4'] += 1
                waits.append(wait)
    rs = sorted(d['r'] for d in first)
    teams = Counter(d['team'] for d in first)
    top4 = sum(v for _, v in teams.most_common(4))
    print('%-40s n %5d (%.0f%%) | windows %s | 2100+ %s | rounds q1/med %d/%d | length 2: %.0f%%, 3: %.0f%%, 4+: %.0f%%, length lost %d' % (
        k, n, 100 * n / total, '/'.join(str(sum(1 for d in first if win(d['r']) == w)) for w in range(3)),
        '/'.join(str(sum(1 for d in first if win(d['r']) == w and d['hi'])) for w in range(3)), rs[n // 4], rs[n // 2],
        100 * sum(1 for d in every if d['L'] == 2) / len(every), 100 * sum(1 for d in every if d['L'] == 3) / len(every),
        100 * sum(1 for d in every if d['L'] >= 4) / len(every), sum(d['L'] for d in every)))
    print('%-40s where: static dead-end cell %.0f%%, room behind the free cells 3 or less %.0f%% | mate head within 3: %.0f%%, nearest mate length (med) %s, it is the queen %.0f%%, it is their longest %.0f%% | our head within 4: %.0f%% | team alive (med) %s' % (
        '', 100 * sum(d['dead'] for d in first) / n, 100 * sum(1 for d in first if d['room'] <= 3) / n,
        100 * sum(1 for d in first if d['mates'] and d['mates'][0][0] <= 3) / n, median(d['mates'][0][2] for d in first if d['mates']),
        100 * sum(1 for d in first if d['mates'] and d['mates'][0][3]) / n, 100 * sum(1 for d in first if d['mates'] and d['mates'][0][4]) / n,
        100 * sum(1 for d in first if d['foes'] and d['foes'][0][0] <= 4) / n, median(d['n_side'] + 1 for d in first)))
    print('%-40s dropped %d: their queen %.1f%%, their longest %.1f%%, own 5+ %.1f%%, own 2-4 %.1f%%, ours %.1f%%, nobody %.1f%% | eaten by them within 3 rounds %.0f%%, median wait %s | top 4 teams hold %.0f%%: %s' % (
        '', drop, 100 * eat['queen'] / drop, 100 * eat['longest'] / drop, 100 * eat['own 5+'] / drop, 100 * eat['own 2-4'] / drop,
        100 * eat['ours'] / drop, 100 * (drop - sum(eat.values())) / drop, 100 * sum(1 for x in waits if x <= 3) / max(len(waits), 1),
        median(waits) if waits else '-', 100 * top4 / n, ', '.join('%s %d' % (a[:14], b) for a, b in teams.most_common(4))))
print('total events', total)
