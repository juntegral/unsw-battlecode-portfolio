#!/usr/bin/env python3
"""Verifier run 5, F26 extra: is a walk-away from a pearl born next to the head a blocked tile rather than a choice?
Reads the x5b shards (large layouts only). Fields 20 and 21 of a birth: what stands on the pearl tile at the birth and
at the start of the nearer dragon's turn (0 nothing, 1 its own body, 2 a team mate, 3 an enemy; -1 not looked at
because the pearl was gone or the dragon dead by then)."""
import sys, json, random
from pathlib import Path
from collections import Counter
sys.dont_write_bytecode = True
V = Path('data/analysis/ladder/verify')
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
LINES = []


def say(*a):
    s = ' '.join(str(x) for x in a)
    LINES.append(s)
    print(s)


def sh(k, n):
    return '%d of %d (%s)' % (k, n, ('%.3f' % (k / n)) if n else '-')


def units(gs, flt):
    out = []
    for g in gs:
        u = [0, 0, 0, 0]
        for b in g['births']:
            if not b[4] or not b[14] or not flt(b):
                continue
            if b[1] == 0:
                u[1] += 1
                if b[9] == 1:
                    u[0] += 1
            else:
                u[3] += 1
                if b[9] == 1:
                    u[2] += 1
        out.append(u)
    return out


def boot(us, n=2000, seed=1):
    rng = random.Random(seed)
    m = len(us)
    vals = []
    for _ in range(n):
        t = [0, 0, 0, 0]
        for _k in range(m):
            u = us[rng.randrange(m)]
            t[0] += u[0]
            t[1] += u[1]
            t[2] += u[2]
            t[3] += u[3]
        if t[1] and t[3]:
            vals.append(t[0] / t[1] - t[2] / t[3])
    vals.sort()
    return vals


def report(label, gs, flt):
    us = units(gs, flt)
    t = [sum(u[i] for u in us) for i in range(4)]
    if not t[1] or not t[3]:
        say('   %-58s ours %s, theirs %s' % (label, sh(t[0], t[1]), sh(t[2], t[3])))
        return
    v = boot(us)
    say('   %-58s ours %s, theirs %s, gap %+.3f, games resampled %+.3f to %+.3f, at or below zero %.3f' % (
        label, sh(t[0], t[1]), sh(t[2], t[3]), t[0] / t[1] - t[2] / t[3], v[int(0.025 * len(v))], v[int(0.975 * len(v)) - 1],
        sum(1 for x in v if x <= 0) / len(v)))


def main():
    games = []
    err = 0
    for k in range(6):
        for line in (V / ('x5b-%d.jsonl' % k)).read_text().splitlines():
            if not line.strip():
                continue
            g = json.loads(line)
            if 'error' in g:
                err += 1
                say('error', g['game'], g['error'])
                continue
            if g.get('skip'):
                continue
            games.append(g)
    say('large-layout games read', len(games), 'errors', err)
    for code in ('main', 'v31'):
        gs = [g for g in games if g['code'] == code]
        say('')
        say('=====', code, 'large games', len(gs))
        report('all in view (must equal the first pass)', gs, lambda b: True)
        for s, sn in ((0, 'ours'), (1, 'theirs')):
            c0 = Counter()
            c1 = Counter()
            c1t = Counter()
            for g in gs:
                for b in g['births']:
                    if b[4] and b[14] and b[1] == s:
                        c0[b[20]] += 1
                        if b[2] == 1:
                            c1[b[20]] += 1
                            c1t[b[21]] += 1
            say('   %s: on the pearl tile at the birth (0 nothing, 1 own body, 2 mate, 3 enemy): all in view %s; nearer distance 1 %s; distance 1 at the start of its turn %s' % (
                sn, sorted(c0.items()), sorted(c1.items()), sorted(c1t.items())))
        say('  walked share, nearer distance 1')
        report('all', gs, lambda b: b[2] == 1)
        report('tile free at the birth', gs, lambda b: b[2] == 1 and b[20] == 0)
        report('tile under a body at the birth', gs, lambda b: b[2] == 1 and b[20] > 0)
        report('tile free at the start of its turn', gs, lambda b: b[2] == 1 and b[21] == 0)
        report('tile free at its turn start and one path step away', gs, lambda b: b[2] == 1 and b[21] == 0 and b[18] == 1)
        report('tile under a body at its turn start', gs, lambda b: b[2] == 1 and b[21] > 0)
        report('one path step away (no kelp between)', gs, lambda b: b[2] == 1 and b[18] == 1)
        report('kelp between (path longer than 1)', gs, lambda b: b[2] == 1 and b[18] != 1)
        say('  walked share, all distances')
        report('tile free at its turn start, no kelp in the way', gs, lambda b: b[21] == 0 and b[18] == b[2])
        report('distance 2 or more, tile free at its turn start, no kelp', gs, lambda b: b[2] >= 2 and b[21] == 0 and b[18] == b[2])
        say('  finished share (eaten by the nearer side) uses the same filter below: ours, theirs')
        for label, flt in (('distance 1, tile free at its turn start, one path step', lambda b: b[2] == 1 and b[21] == 0 and b[18] == 1),
                           ('distance 1, all', lambda b: b[2] == 1)):
            t = [0, 0, 0, 0]
            for g in gs:
                for b in g['births']:
                    if b[4] and b[14] and flt(b):
                        if b[1] == 0:
                            t[1] += 1
                            t[0] += 1 if b[15] == 0 else 0
                        else:
                            t[3] += 1
                            t[2] += 1 if b[15] == 1 else 0
            say('   %-58s %s, %s' % (label, sh(t[0], t[1]), sh(t[2], t[3])))
        say('  what the nearer dragon did with a free pearl one path step away (status: 1 walked away, 2 not farther, 3 ate it that turn, 4 another ate it first, 5 died first)')
        for s, sn in ((0, 'ours'), (1, 'theirs')):
            c = Counter()
            ate = 0
            for g in gs:
                for b in g['births']:
                    if b[4] and b[14] and b[1] == s and b[2] == 1 and b[21] == 0 and b[18] == 1:
                        c[b[9]] += 1
                        if b[9] == 1 and b[10] > 0:
                            ate += 1
            n = sum(c.values())
            say('   %s n %d: %s; walked away while eating another pearl %d' % (sn, n, ', '.join('%d: %d (%.3f)' % (k, v, v / n) for k, v in sorted(c.items())), ate))
    f = open(P + 'f26-blocked.txt', 'w')
    f.write('\n'.join(LINES) + '\n')
    f.close()


main()
