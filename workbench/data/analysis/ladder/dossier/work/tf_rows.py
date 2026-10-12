"""Scratch (diag-topfight): chances of non-queen dragons of 2-4, classed by what our rule (agg8-bot/main.cpp 2650-2666,
2714-2732, 2748-2752) says about them, with the take rate of each group and the worth of the rams taken in the class.
Usage: python3 tf_rows.py <file> [file...]"""
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


def why(L, M, stp, vis, ov, ev, rnd, alive, cells):
    free = (L + 3) // 4
    own = free + L - 2
    pearl = stp > own
    hunt = (vis >= 10 and vis >= L + 4) or vis >= 2 * L
    if hunt and not pearl:
        return 'yes-hunt'
    out = []
    if M < L:
        out.append('short')
    elif vis < L:
        out.append('hid')
    if ov + 1 <= ev:
        out.append('cnt')
    if rnd > 400:
        out.append('late')
    if pearl:
        out.append('pearl')
    if cells > 1200 and alive < 8:
        out.append('few')
    return '+'.join(out) if out else 'yes-trade'


def sh(a, b):
    return '%.2f' % (a / b) if b else '-'


def main():
    G = defaultdict(lambda: dict(games=0, c=defaultdict(lambda: [0, 0]), v=defaultdict(lambda: [0] * 6), rel=defaultdict(lambda: [0, 0])))
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
            cells = r['cells']
            for row in r.get('rows', []):
                rnd, s, a, L, kd, j, M, tk, stp, free, pe, ov, ev, vis, taken, rc, al, ale = row[:18]
                if kd != 0 or L > 4:
                    continue
                rel = 'T' if M >= 2 * L else 'E' if M >= L else 'S'
                w = why(L, M, stp, vis, ov, ev, rnd, al, cells)
                v = G[gs[s]]['c'][(rel, w)]
                v[0] += 1
                v[1] += taken == 1
                v = G[gs[s]]['rel'][(rel, L)]
                v[0] += 1
                v[1] += taken == 1
            for h in r['hos']:
                if not h['cross'] or h['mk'] != 0 or h['L0'] > 4 or h['d'] < 0:
                    continue
                L, M = h['L0'], h['Lv']
                rel = 'T' if M >= 2 * L else 'E' if M >= L else 'S'
                w = why(L, M, h['d'], h['vis'], h['ov'], h['ev'], h['r'], h['nm'], cells)
                v = G[gs[h['ms']]]['v'][(rel, w)]
                v[0] += 1
                v[1] += L - h['mm'] - h['vm']
                v[2] += M - h['vv'] - h['mv']
                v[3] += L - h['mm15'] - h['vm15']
                v[4] += M - h['vv15'] - h['mv15']
                v[5] += M
    for k in sorted(G):
        g = G[k]
        print('==', k, 'games', g['games'])
        print('   by own length: ' + ' | '.join('%s L%d %.1f/g %s' % (rel, L, g['rel'][(rel, L)][0] / g['games'], sh(g['rel'][(rel, L)][1], g['rel'][(rel, L)][0]))
                                                for rel in 'SET' for L in (2, 3, 4)))
        for rel, nm in (('S', 'target shorter'), ('E', 'same to under twice'), ('T', 'twice or more')):
            items = sorted(((w, v) for (rl, w), v in g['c'].items() if rl == rel), key=lambda t: -t[1][0])
            tot = sum(v[0] for w, v in items)
            print('  %s: %.1f chances a game' % (nm, tot / g['games']))
            for w, v in items:
                if v[0] / g['games'] < 0.15:
                    continue
                x = g['v'].get((rel, w), [0] * 6)
                val = ''
                if x[0] >= 5:
                    val = ' | rams %d: victim %.1f; net 5r mover -%.2f victim -%.2f (gain %.2f); 15r -%.2f / -%.2f (gain %.2f)' % (
                        x[0], x[5] / x[0], x[1] / x[0], x[2] / x[0], (x[2] - x[1]) / x[0], x[3] / x[0], x[4] / x[0], (x[4] - x[3]) / x[0])
                print('     %-22s %6.2f/g taken %s (%.2f rams/g)%s' % (w, v[0] / g['games'], sh(v[1], v[0]), v[1] / g['games'], val))


main()
