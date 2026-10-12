# Scratch (diag-sacrifice): sorts every death by "no valid action" (no action, illegal split, unpaid sprint) and
# every same-team head-on up to round 300 into kinds, for both sides, and prints who ate what they dropped.
# Usage: python3 data/analysis/ladder/dossier/work/sc_kind.py [test]
import sys, json
from collections import Counter, defaultdict
from statistics import median
from pathlib import Path

W = 'data/analysis/ladder/dossier/work/'
names = ['sc_ev-test.jsonl'] if len(sys.argv) > 1 and sys.argv[1] == 'test' else ['sc_ev-%d.jsonl' % n for n in range(4)]
games = []
for name in names:
    for line in Path(W + name).read_text().splitlines():
        if line:
            games.append(json.loads(line))
print('games', len(games))


def band(g):
    return 'lo' if g['rating'] < 1900 else 'mid' if g['rating'] < 2100 else 'hi'


def win(r):
    return 0 if r <= 100 else 1 if r <= 200 else 2 if r <= 300 else 3


def kind(d, crash):
    L = d['L']
    if crash:
        return 'X many at once'
    if d['free'] == 0:
        if d['split_r'] >= 0 and d['r'] - d['split_r'] <= 1:
            return 'B1 boxed, front left by a split'
        if d['r'] - d['born'] <= 1 and d['nturns'] <= 2 and d['par'] >= 0:
            return 'B2 boxed, new child'
        if d['dead']:
            return 'B3 boxed, dead-end cell'
        return 'B4 boxed, other'
    if d['q_alive'] and 0 <= d['q_dist'] <= 4 and d['q_len'] > L:
        return 'F1 free, beside queen'
    t = d['tgt']
    if t[0] >= 0 and t[2] <= 4 and t[1] >= 2 * L:
        return 'F2 free, beside longest' if t[1] >= d['rest'] else 'F3 free, beside a longer mate'
    return 'F4 free, no long mate near'


rows = []
for g in games:
    per_round = Counter()
    alive_before = {}
    for d in g['events']:
        if d['reason'] == 4:
            per_round[d['side'], d['r']] += 1
            alive_before.setdefault((d['side'], d['r']), d['n_side'] + 1)
    for d in g['events']:
        if d['reason'] != 4:
            continue
        key = (d['side'], d['r'])
        crash = per_round[key] >= 4 and per_round[key] >= 0.5 * alive_before[key]
        d['kind'] = kind(d, crash)
        d['band'] = band(g)
        d['game'] = g['game']
        d['layout'] = g['layout']
        d['opp'] = g['opponent']
        rows.append(d)

turns = defaultdict(lambda: [0, 0, 0, 0])
for g in games:
    for s in 'ut':
        for k in range(4):
            turns[s, 'all'][k] += g['turns'][s][k]
            turns[s, band(g)][k] += g['turns'][s][k]


def eaters(ds):
    c = Counter()
    waits = []
    for d in ds:
        c['dropped'] += d['np']
        tid = d['tgt'][0]
        for s, wait, eid, elen, isq, istop in d['p']:
            if s != d['side']:
                c['enemy'] += 1
            elif isq:
                c['queen'] += 1
            elif istop:
                c['longest'] += 1
            elif eid == tid:
                c['long mate beside'] += 1
            elif elen >= 5:
                c['other own 5+'] += 1
            else:
                c['other own 2-4'] += 1
            if s == d['side']:
                waits.append(wait)
        c['nobody'] += d['np'] - len(d['p'])
    return c, waits


def describe(title, ds):
    if not ds:
        return
    c, waits = eaters(ds)
    n = len(ds)
    L = Counter('2' if d['L'] == 2 else '3' if d['L'] == 3 else '4-5' if d['L'] <= 5 else '6-9' if d['L'] <= 9 else '10+' for d in ds)
    foe = sum(1 for d in ds if d['foes'] and d['foes'][0][0] <= 4)
    mate3 = sum(1 for d in ds if d['mates'] and d['mates'][0][0] <= 3)
    qn = sum(1 for d in ds if d['q'])
    tp = sum(1 for d in ds if d['top'])
    w3 = sum(1 for x in waits if x <= 3)
    print('  %-34s n %5d | round q1/med/q3 %d/%d/%d | L %s | queen itself %d, team longest %d | our head within 4: %.0f%% | mate head within 3: %.0f%%' % (
        title, n, sorted(d['r'] for d in ds)[n // 4], median(d['r'] for d in ds), sorted(d['r'] for d in ds)[(3 * n) // 4],
        ' '.join('%s:%d' % (k, L[k]) for k in ('2', '3', '4-5', '6-9', '10+')), qn, tp, 100 * foe / n, 100 * mate3 / n))
    dr = max(c['dropped'], 1)
    print('  %-34s length %d, dropped %d: queen %.0f%% longest %.0f%% long mate beside %.0f%% other own 5+ %.0f%% other own 2-4 %.0f%% ours %.0f%% nobody %.0f%% | own eat within 3 rounds %.0f%%' % (
        '', sum(d['L'] for d in ds), c['dropped'], 100 * c['queen'] / dr, 100 * c['longest'] / dr, 100 * c['long mate beside'] / dr,
        100 * c['other own 5+'] / dr, 100 * c['other own 2-4'] / dr, 100 * c['enemy'] / dr, 100 * c['nobody'] / dr,
        100 * w3 / max(len(waits), 1)))


kinds = sorted({d['kind'] for d in rows})
for s, label in (('t', 'THEIRS'), ('u', 'OURS')):
    print()
    print(label, 'deaths by no valid action up to round 300: count by kind, window (0-100 / 101-200 / 201-300), band (all; lo mid hi)')
    for kd in kinds:
        cells = []
        for b in ('all', 'lo', 'mid', 'hi'):
            cells.append('/'.join(str(sum(1 for d in rows if d['side'] == s and d['kind'] == kd and win(d['r']) == wn and (b == 'all' or d['band'] == b))) for wn in range(3)))
        lab = Counter(d['cause'] for d in rows if d['side'] == s and d['kind'] == kd and d['r'] <= 300)
        print('  %-34s all %-16s lo %-14s mid %-14s hi %-14s labels %s' % (kd, cells[0], cells[1], cells[2], cells[3], dict(lab)))
    print('  per 1,000 turns by window and band, boxed (B) / free (F) / many at once (X):')
    for b in ('all', 'lo', 'mid', 'hi'):
        out = []
        for wn in range(3):
            t = turns[s, b][wn]
            sel = [d for d in rows if d['side'] == s and win(d['r']) == wn and (b == 'all' or d['band'] == b)]
            out.append('w%d B %.2f F %.2f X %.2f' % (wn, 1000 * sum(1 for d in sel if d['kind'][0] == 'B') / t,
                                                    1000 * sum(1 for d in sel if d['kind'][0] == 'F') / t,
                                                    1000 * sum(1 for d in sel if d['kind'][0] == 'X') / t))
        print('   ', b, ' | '.join(out))
    for wn, wl in ((0, 'rounds 0-100'), (1, 'rounds 101-200'), (2, 'rounds 201-300')):
        print(' ', wl)
        for kd in kinds:
            describe(kd, [d for d in rows if d['side'] == s and d['kind'] == kd and win(d['r']) == wn])

# same-team head-ons
print()
for s, label in (('t', 'THEIRS'), ('u', 'OURS')):
    pairs = []
    for g in games:
        for d in g['events']:
            if d['reason'] == 3 and d.get('st') and d['mover'] and d['side'] == s and d['r'] <= 300:
                hit = [e for e in g['events'] if e['reason'] == 3 and e['r'] == d['r'] and e['id'] == d['o_id']][0]
                d['hit'] = hit
                d['band'] = band(g)
                pairs.append(d)
    print(label, 'same-team head-ons up to round 300:', len(pairs))
    for wn in range(3):
        sel = [d for d in pairs if win(d['r']) == wn]
        if not sel:
            continue
        n = len(sel)
        boxed = sum(1 for d in sel if d['free'] == 0)
        hit_boxed = sum(1 for d in sel if d['hit']['free'] == 0)
        split1 = sum(1 for d in sel if d['split_r'] >= 0 and d['r'] - d['split_r'] <= 1)
        qm = sum(1 for d in sel if d['q'])
        qh = sum(1 for d in sel if d['hit']['q'])
        short = sum(1 for d in sel if d['L'] <= 3)
        hshort = sum(1 for d in sel if d['hit']['L'] <= 3)
        foe = sum(1 for d in sel if d['foes'] and d['foes'][0][0] <= 4)
        third = sum(1 for d in sel if len([m for m in d['mates'] if m[1] != d['o_id'] and m[0] <= 4 and m[2] >= 2 * d['L']]) > 0)
        sib = sum(1 for d in sel if d['par'] == d['o_id'] or d['hit']['par'] == d['id'])
        print('  w%d n %d | mover boxed %d (%.0f%%), hit one boxed %d | mover is front left by a split %d | parent and child %d | mover 2-3 long %d, hit 2-3 long %d | mover is queen %d, hit is queen %d | our head within 4: %d | a third mate at least twice the mover within 4: %d | bands %s' % (
            wn, n, boxed, 100 * boxed / n, hit_boxed, split1, sib, short, hshort, qm, qh, foe, third, dict(Counter(d['band'] for d in sel))))
        both = sel + [d['hit'] for d in sel]
        describe('both dragons of the pair', both)
