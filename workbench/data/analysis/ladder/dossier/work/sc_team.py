# Scratch (diag-sacrifice): per opponent team, how its dragons die when boxed in and how often they die with a free
# cell beside the head (by choice), by window; and the first round of a death by choice beside the queen or a longer mate.
# Usage: python3 data/analysis/ladder/dossier/work/sc_team.py
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
    return 0 if r <= 100 else 1 if r <= 200 else 2 if r <= 300 else 3


def fed(d):
    # a death by choice that is placed for a longer team mate
    if d['free'] == 0:
        return None
    if d['q_alive'] and 0 <= d['q_dist'] <= 4 and d['q_len'] > d['L']:
        return 'q'
    t = d['tgt']
    if t[0] >= 0 and t[2] <= 4 and t[1] >= 2 * d['L']:
        return 'm'
    return 'x'


team = defaultdict(lambda: dict(games=0, rating=[], turns=[0, 0, 0], boxed=Counter(), nonram_boxed=[0, 0, 0],
                                free4=[Counter(), Counter(), Counter()], first=[], firstq=[], won=0, r300=0,
                                st=[0, 0, 0], st_boxed=[0, 0, 0], free_other=[0, 0, 0]))
for g in games:
    for s, name in (('t', g['opponent']), ('u', 'US (all games)')):
        t = team[name]
        t['games'] += 1
        t['rating'].append(g['rating'])
        t['won'] += int(g['result'] == ('loss' if s == 't' else 'win'))
        t['r300'] += int(g['last_round'] >= 300)
        for k in range(3):
            t['turns'][k] += g['turns'][s][k]
        for r, sd, L, cause, free, room, q, top, age, since, dead, nt, n_side in g['compact']:
            if sd != s or cause == 'headon':
                continue
            if free == 0:
                t['boxed'][cause] += 1
                t['nonram_boxed'][win(r)] += 1
            elif cause in ('wall', 'own', 'body'):
                t['free_other'][win(r)] += 1
        first = None
        firstq = None
        for d in g['events']:
            if d['side'] != s or d['r'] > 300:
                continue
            if d['reason'] == 4:
                f = fed(d)
                if f:
                    t['free4'][win(d['r'])][f] += 1
                    if f in 'qm' and first is None:
                        first = d['r']
                    if f == 'q' and firstq is None:
                        firstq = d['r']
            elif d.get('st') and d['mover']:
                t['st'][win(d['r'])] += 1
                t['st_boxed'][win(d['r'])] += int(d['free'] == 0)
        if first is not None:
            t['first'].append(first)
        if firstq is not None:
            t['firstq'].append(firstq)

print('team | games (won by them, reach r300) | rating | boxed non-ram deaths r0-300 by label | per 1,000 turns w0/w1/w2: boxed non-ram; by choice beside queen; beside longer mate; free, nobody near; wall/own/body with a free cell; same-team head-on (boxed mover) | games with a fed death by r300, first round q1/med')
order = sorted(team.items(), key=lambda kv: -median(kv[1]['rating']))
for name, t in order:
    def rate(xs):
        return '/'.join('%.2f' % (1000 * xs[k] / t['turns'][k]) if t['turns'][k] else '-' for k in range(3))
    b = t['boxed']
    tot = max(sum(b.values()), 1)
    lab = ' '.join('%s %.0f%%' % (k, 100 * b[k] / tot) for k in ('noact', 'split', 'sprint', 'wall', 'own', 'body') if b[k])
    fs = sorted(t['first'])
    print('%-22s | %3d (%3d, %3d) | %4d | %-44s | box %s | q %s | m %s | x %s | wob %s | st %s (%s) | fed games %d, first %s' % (
        name[:22], t['games'], t['won'], t['r300'], median(t['rating']), lab, rate(t['nonram_boxed']),
        rate([t['free4'][k]['q'] for k in range(3)]), rate([t['free4'][k]['m'] for k in range(3)]),
        rate([t['free4'][k]['x'] for k in range(3)]), rate(t['free_other']), rate(t['st']),
        '/'.join(str(x) for x in t['st_boxed']), len(fs), ('%d/%d' % (fs[len(fs) // 4], median(fs))) if fs else '-'))
