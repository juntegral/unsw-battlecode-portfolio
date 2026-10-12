"""Scratch (diag-topfight): the 'shorter head, not outnumbered' class and the pearl class, cut finer.
Usage: python3 tf_sub.py <file> [file...]"""
import sys, json
from collections import defaultdict, Counter
from pathlib import Path

NAMES = {454: 'aAah', 157: 'larp', 306: 'Cutlery', 70: 'chad gdp', 91: 'SSS', 264: 'forgot', 842: 'horse', 1119: 'ours'}
STUDY = {'T3': {454, 157, 306, 70}, 'T1': {306, 91, 264, 842, 454}}


def grp(rec, s):
    team = rec['a'] if s == 0 else rec['b']
    lab = rec['label']
    if lab in STUDY:
        return '%s:%s' % (lab, NAMES.get(team, team)) if team in STUDY[lab] else lab + ':opp'
    return lab + (':us' if team == 1119 else ':' + str(NAMES.get(team, 'opp')) if lab == 'OT' else ':opp')


def cls(L, M, stp, vis, ov, ev, rnd):
    free = (L + 3) // 4
    own = free + L - 2
    pearl = stp > own
    if rnd > 400:
        return None
    if ov + 1 <= ev:
        if M >= L and M < 2 * L and not pearl:
            return ('C', 'L%d' % L, 'margin%d' % max(ov + 1 - ev, -2), 'free' if stp <= free else 'paid')
        return None
    if M < L:
        if pearl:
            return None
        return ('S', 'L%d>M%d' % (L, M), 'free' if stp <= free else 'paid%d' % min(stp - free, 2), 'edge%d' % min(ov + 1 - ev, 3))
    if pearl:
        return ('P', 'L%d' % L, 'twice' if M >= 2 * L else 'same', 'edge%d' % min(ov + 1 - ev, 3))
    return None


def sh(a, b):
    return '%.2f' % (a / b) if b else '-'


def main():
    G = defaultdict(lambda: dict(games=0, c=defaultdict(lambda: [0, 0]), v=defaultdict(lambda: [0] * 6)))
    seen = set()
    for f in sys.argv[1:]:
        p = Path(f)
        if not p.is_file():
            continue
        for line in p.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if (r['label'], r['game']) in seen:
                continue
            seen.add((r['label'], r['game']))
            gs = [grp(r, 0), grp(r, 1)]
            for s in (0, 1):
                G[gs[s]]['games'] += 1
            for row in r.get('rows', []):
                rnd, s, a, L, kd, j, M, tk, stp, free, pe, ov, ev, vis, taken, rc, al, ale = row[:18]
                if kd != 0 or L > 4:
                    continue
                c = cls(L, M, stp, vis, ov, ev, rnd)
                if c is None:
                    continue
                for key in ((c[0], 'all'), (c[0], c[1]), (c[0], c[2]), (c[0], c[3])):
                    v = G[gs[s]]['c'][key]
                    v[0] += 1
                    v[1] += taken == 1
            for h in r['hos']:
                if not h['cross'] or h['mk'] != 0 or h['L0'] > 4 or h['d'] < 0:
                    continue
                L, M = h['L0'], h['Lv']
                c = cls(L, M, h['d'], h['vis'], h['ov'], h['ev'], h['r'])
                if c is None:
                    continue
                for key in ((c[0], 'all'), (c[0], c[1]), (c[0], c[2]), (c[0], c[3])):
                    v = G[gs[h['ms']]]['v'][key]
                    v[0] += 1
                    v[1] += L - h['mm'] - h['vm']
                    v[2] += M - h['vv'] - h['mv']
                    v[3] += L - h['mm15'] - h['vm15']
                    v[4] += M - h['vv15'] - h['mv15']
    for k in sorted(G):
        g = G[k]
        print('==', k, 'games', g['games'])
        for key in sorted(set(list(g['c']) + list(g['v']))):
            v = g['c'].get(key, [0, 0])
            x = g['v'].get(key, [0] * 6)
            val = ''
            if x[0] >= 8:
                val = ' | rams %d: 5r mover -%.2f victim -%.2f gain %+.2f ; 15r gain %+.2f' % (x[0], x[1] / x[0], x[2] / x[0], (x[2] - x[1]) / x[0], (x[4] - x[3]) / x[0])
            print('   %s %-8s %6.2f/g taken %s%s' % (key[0], key[1], v[0] / g['games'], sh(v[1], v[0]), val))


main()
