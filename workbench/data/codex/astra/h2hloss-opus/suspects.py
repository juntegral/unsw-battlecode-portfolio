"""Per-suspect counts over every finished game of an arm (side 0 = newer). Usage: suspects.py <arm> ..."""
import sys, json
from collections import Counter, defaultdict
from pathlib import Path
HERE = Path('data/codex/astra/h2hloss-opus')
for arm in sys.argv[1:]:
    S = {json.loads(l)['folder']: json.loads(l) for l in (HERE / ('scan-%s.jsonl' % arm)).read_text().splitlines()}
    tf = HERE / ('turns-%s.jsonl' % arm)
    T = {json.loads(l)['folder']: json.loads(l) for l in tf.read_text().splitlines()} if tf.exists() else {}
    n = len(S)
    print('==== %s: %d games, newer wins %d, losses %d' % (arm, n, sum(g['result'] == 'win' for g in S.values()), sum(g['result'] == 'loss' for g in S.values())))
    # (a) rams on the enemy queen by rammer length
    for s, nm in ((0, 'NEW rams old queen'), (1, 'old rams NEW queen')):
        rows = [(f, d) for f, g in S.items() for d in g['deaths'] if d[6] and d[1] == 1 - s and d[4] == 'rammed' and d[18]]
        small = [d for f, d in rows if d[18][0] <= 4]
        big = [(f, d) for f, d in rows if d[18][0] > 4]
        print('(a) %s: %d kills; rammer 2-4: %d; rammer 5+: %d, their lengths %s (sum %d), rounds %s, steps %s; results of those games %s' % (
            nm, len(rows), len(small), len(big), [d[18][0] for f, d in big], sum(d[18][0] for f, d in big), [d[0] for f, d in big], [d[18][1] for f, d in big],
            dict(Counter(S[f]['result'] for f, d in big))))
        print('     steps of the killing move: %s; 4-5 steps (outside the one8 rule of 3): %d' % (dict(sorted(Counter(d[18][1] for f, d in rows).items())), sum(1 for f, d in rows if d[18][1] >= 4)))
    first = Counter()
    for f, g in S.items():
        qd = [d for d in g['deaths'] if d[6]]
        who = 'none' if not qd else ('old queen first' if qd[0][1] == 1 else 'NEW queen first')
        if len(qd) >= 2 and qd[0][0] == qd[1][0] and 'rams' in (qd[0][4], qd[1][4]):
            who = 'queen rams queen'
        first[(who, g['result'])] += 1
    print('    first queen death x result:', dict(sorted(first.items())))
    both = sum(1 for g in S.values() if sum(1 for d in g['deaths'] if d[6]) == 2)
    print('    both queens dead before the end: %d of %d' % (both, n))
    for s, nm in ((0, 'NEW'), (1, 'old')):
        qd = sorted(d[0] for g in S.values() for d in g['deaths'] if d[6] and d[1] == s)
        alive = n - len(qd)
        L = Counter(d[2] for g in S.values() for d in g['deaths'] if d[6] and d[1] == s)
        cause = Counter(d[4] for g in S.values() for d in g['deaths'] if d[6] and d[1] == s)
        print('    %s queen: died in %d games (median round %s), alive at the end in %d; length at death %s; cause %s' % (nm, len(qd), qd[len(qd) // 2] if qd else '-', alive, dict(sorted(L.items())), dict(cause)))
    # (b) queen length and splits
    if T:
        for s, nm in ((0, 'NEW'), (1, 'old')):
            c = Counter()
            rounds = 0
            for g in T.values():
                for r, L in enumerate(g['qlen'][s][:101]):
                    if L:
                        c[min(L, 5)] += 1
                        rounds += 1
            sp = Counter()
            for g in T.values():
                for k, v in g['splits'][s].items():
                    if k[0] == 'q':
                        sp[k] += v
            at = {r: sum(g['qlen'][s][r] for g in T.values() if len(g['qlen'][s]) > r and g['qlen'][s][r]) / max(1, sum(1 for g in T.values() if len(g['qlen'][s]) > r and g['qlen'][s][r])) for r in (25, 50, 75, 100)}
            print('(b) %s queen, alive rounds 0-100: share at length 2/3/4/5+ = %s; queen splits by parent length (a = r<=100, c = later) %s; mean length when alive at r25/50/75/100 %s' % (
                nm, ' '.join('%.0f%%' % (100 * c[k] / rounds) for k in (2, 3, 4, 5)), dict(sorted(sp.items())), ' '.join('%.1f' % at[r] for r in (25, 50, 75, 100))))
        # (e) self-kills beside the own queen: reason 0 wall, 1 own body, by a non-queen of 2-3 as actor, queen alive, distance <= 2
        for s, nm in ((0, 'NEW'), (1, 'old')):
            near = Counter()
            far = Counter()
            for g in T.values():
                for rnd, sd, L, reason, qd, isactor, isq, qL in g['dl']:
                    if sd != s or isq or not isactor or reason not in (0, 1):
                        continue
                    if 0 <= qd <= 2:
                        near['L%d' % min(L, 4)] += 1
                    elif qd > 2:
                        far['queen alive, farther'] += 1
                    else:
                        far['queen dead'] += 1
            print('(e) %s self-kills (wall or own body, as the mover): within 2 of the own queen %s (total %d, length lost counted below); elsewhere %s' % (nm, dict(near), sum(near.values()), dict(far)))
    # (d) queen alive and under 6 in the feeding phase
    for s, nm in ((0, 'NEW'), (1, 'old')):
        rows = []
        for f, g in S.items():
            for r in ('350', '400', '450'):
                if r in g['snaps'] and g['snaps'][r][s][3] > 0:
                    rows.append((f[3:-12] + f[-2:], r, g['snaps'][r][s][3], g['snaps'][r][s][2], g['result'], g['how']))
        print('(d) %s queen alive at r350/400/450: %s' % (nm, rows))
    # (g) end phase: longest at r350/400/450/475/end on maps that reach r499
    big = [g for g in S.values() if g['last'] >= 499]
    for r in (350, 400, 425, 450, 475, 499):
        a = [g['snaps'][str(r)][0][2] for g in big]
        b = [g['snaps'][str(r)][1][2] for g in big]
        print('(g) r%d longest mean NEW %.1f old %.1f; NEW longer in %d, old longer in %d of %d' % (r, sum(a) / len(a), sum(b) / len(b), sum(x > y for x, y in zip(a, b)), sum(x < y for x, y in zip(a, b)), len(big)))
    flips = Counter()
    for g in big:
        x, y = g['snaps']['450'][0][2], g['snaps']['450'][1][2]
        flips[('NEW ahead at r450' if x > y else 'old ahead at r450' if y > x else 'level at r450', g['result'])] += 1
    print('    lead at r450 x result:', dict(sorted(flips.items())))
    for s, nm in ((0, 'NEW'), (1, 'old')):
        st = [d for g in big for d in g['deaths'] if d[1] == s and d[4] == 'stop' and d[0] > 350]
        print('    %s feeders stopping after r350: %d, length %d, of which eaten by own side %d' % (nm, len(st), sum(d[2] for d in st), sum(d[10] for d in st)))
    # leader rams
    for lo, hi in ((301, 400), (401, 499)):
        for s, nm in ((0, 'NEW'), (1, 'old')):
            for thr in (10, 20, 40):
                rr = [d for g in big for d in g['deaths'] if d[1] == s and d[4] == 'rammed' and d[2] >= thr and lo <= d[0] <= hi]
                print('    r%d-%d %s dragons of %d+ rammed: %d (length %d); rammer length <=4: %d, 5-9: %d, 10+: %d; steps 1-2: %d, 3: %d, 4+: %d' % (
                    lo, hi, nm, thr, len(rr), sum(d[2] for d in rr), sum(d[18][0] <= 4 for d in rr), sum(5 <= d[18][0] <= 9 for d in rr), sum(d[18][0] >= 10 for d in rr),
                    sum(d[18][1] <= 2 for d in rr), sum(d[18][1] == 3 for d in rr), sum(d[18][1] >= 4 for d in rr)))
    # decisive leader ram: in games decided on longest, the loser lost after r400 a dragon at least as long as the winner's final longest
    dec = Counter()
    for g in big:
        if g['how'] != 'longest':
            continue
        loser = 0 if g['result'] == 'loss' else 1
        win_long = g['ends'][1 - loser][2]
        lost = [d[2] for d in g['deaths'] if d[1] == loser and d[4] == 'rammed' and d[0] > 400]
        wl = [d[2] for d in g['deaths'] if d[1] == 1 - loser and d[4] == 'rammed' and d[0] > 400]
        dec[('NEW lost' if loser == 0 else 'old lost', 'loser had a dragon rammed after r400 that was >= the winner final longest' if lost and max(lost) >= win_long else 'no such ram')] += 1
    print('    longest-dragon games:', dict(sorted(dec.items())))
