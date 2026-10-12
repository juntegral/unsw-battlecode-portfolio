# Scratch (diag-stripes): one line per game (ours against theirs) and the net length each room class gives a side.
# Usage: python3 data/analysis/ladder/dossier/work/st_pergame.py <rows file> [round limit, default 100]
import sys, json
from collections import Counter

LIM = int(sys.argv[2]) if len(sys.argv) > 2 else 100
games = [json.loads(line) for line in open(sys.argv[1])]


def cls(g, c):
    s = g['size'][g['comp'][c]]
    return 'main' if s >= 48 else ('loop%d' if g['loop'][g['comp'][c]] else 'dead%d') % s


tot = Counter()
print('per game, rounds 0-%d. P = pearls eaten (main/loop4/dead3+dead1), V = visits begun (loop4/dead), R = turns with a free portal step onto a pearl not taken (loop4/dead3), D,T = dragons and total length at the limit or at the end' % LIM)
print('game     vs   res  end | ours: P50  P    P by room   V     R       D  T | theirs: P50 P    P by room    V      R       D  T | their first dead-room dive, ours')
for g in games:
    P = Counter()
    for c, b, o, by, er, eid, eL, eq in g['pearls']:
        if by is None:
            continue
        if er <= 50:
            P[by, 50] += 1
        if er <= LIM:
            P[by, 'all'] += 1
            k = cls(g, c)
            P[by, 'dead' if k in ('dead3', 'dead1') else k] += 1
    V = Counter()
    R = Counter()
    first = {}
    where = {}
    net = Counter()
    for t in g['turns']:
        s, i = t['s'], t['id']
        if i not in where:
            where[i] = cls(g, t['head'])
        if t['r'] <= LIM and t['hs'] >= 48:
            took = t['dirs'][0][0] if t['dirs'] else None
            for d, o in enumerate(t['opts']):
                if o and o[0] == 2 and o[2] < 48 and o[6] == 0 and o[4] and took != d:
                    R[s, 'loop4' if o[3] else 'dead%d' % o[2]] += 1
        for c in t['steps']:
            k = cls(g, c)
            if k != where[i]:
                if k != 'main' and t['r'] <= LIM:
                    kk = 'dead' if k.startswith('dead') else k
                    V[s, kk] += 1
                    if kk == 'dead' and s not in first:
                        first[s] = t['r']
                where[i] = k
        # net length by the room class the head is in when the event happens (whole game)
        end = t['steps'][-1] if t['steps'] else t['head']
        k = cls(g, end)
        if t['ate']:
            tot['ate', s, k] += t['ate']
            if t['r'] <= LIM:
                tot['ateL', s, k] += t['ate']
        if t['died'] is not None:
            k0 = cls(g, t['head'])
            tot['deadlen', s, k0] += t['L'] + t['ate']
            tot['deaths', s, k0] += 1
            tot['deaths', s, k0, t['died']] += 1
            if t['r'] <= LIM:
                tot['deadlenL', s, k0] += t['L'] + t['ate']
                tot['deathsL', s, k0] += 1
    snap = None
    for srow in g['snaps']:
        if srow[0] <= LIM:
            snap = srow
    print('%d %4d %-4s %3d | %3d %3d  %3d/%3d/%3d  %2d/%2d  %3d/%3d  %2d %3d | %3d %3d  %3d/%3d/%3d  %2d/%2d  %3d/%3d  %2d %3d | %s, %s' % (
        g['game'], g['rating'], g['result'], g['last_round'],
        P['u', 50], P['u', 'all'], P['u', 'main'], P['u', 'loop4'], P['u', 'dead'], V['u', 'loop4'], V['u', 'dead'], R['u', 'loop4'], R['u', 'dead3'], snap[1], snap[2],
        P['t', 50], P['t', 'all'], P['t', 'main'], P['t', 'loop4'], P['t', 'dead'], V['t', 'loop4'], V['t', 'dead'], R['t', 'loop4'], R['t', 'dead3'], snap[4], snap[5],
        first.get('t', '-'), first.get('u', '-')))
    for s in 'ut':
        for kk in (50, 'all', 'main', 'loop4', 'dead'):
            tot['P', s, kk] += P[s, kk]
        for kk in ('loop4', 'dead'):
            tot['V', s, kk] += V[s, kk]
        for kk in ('loop4', 'dead3'):
            tot['R', s, kk] += R[s, kk]
        tot['D', s] += snap[1 if s == 'u' else 4]
        tot['T', s] += snap[2 if s == 'u' else 5]
        tot['first', s] += s in first
n = len(games)
print('mean of %d games           | %4.1f %4.1f  %.1f/%.1f/%.1f  %.1f/%.1f  %.1f/%.1f  %.1f %.1f | %4.1f %4.1f  %.1f/%.1f/%.1f  %.1f/%.1f  %.1f/%.1f  %.1f %.1f' % tuple(
    [n] + [tot[k] / n for s in 'ut' for k in (('P', s, 50), ('P', s, 'all'), ('P', s, 'main'), ('P', s, 'loop4'), ('P', s, 'dead'),
                                               ('V', s, 'loop4'), ('V', s, 'dead'), ('R', s, 'loop4'), ('R', s, 'dead3'), ('D', s), ('T', s))]))
print('games with a dead-room dive by the limit: ours', tot['first', 'u'], 'theirs', tot['first', 't'])
print()
print('net length by where the head is, whole game and rounds 0-%d: pearls eaten there minus length of the dragons that died there' % LIM)
for k in ('main', 'loop4', 'dead3', 'dead1'):
    for s in 'ut':
        print('  %-5s %s  pearls %5d  deaths %4d (length %5d)  net %+6d | to r%d: pearls %4d deaths %4d (length %4d) net %+5d | causes %s' % (
            k, 'ours  ' if s == 'u' else 'theirs', tot['ate', s, k], tot['deaths', s, k], tot['deadlen', s, k], tot['ate', s, k] - tot['deadlen', s, k],
            LIM, tot['ateL', s, k], tot['deathsL', s, k], tot['deadlenL', s, k], tot['ateL', s, k] - tot['deadlenL', s, k],
            {c: tot['deaths', s, k, c] for c in ('wall', 'own body', 'other body', 'head-on', 'no action') if tot['deaths', s, k, c]}))
