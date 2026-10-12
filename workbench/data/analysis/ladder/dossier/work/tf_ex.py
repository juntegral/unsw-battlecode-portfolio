"""Scratch (diag-topfight): example turns from our own games (file with positions in the chance rows).
Usage: python3 tf_ex.py <file>"""
import sys, json
from collections import defaultdict, Counter
from pathlib import Path


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


def main():
    ex = defaultdict(list)
    tot = Counter()
    games = 0
    per = defaultdict(Counter)
    for line in Path(sys.argv[1]).read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        us = 0 if r['a'] == 1119 else 1
        won = r['winner'] == 'ab'[us]
        games += 1
        tag = '%d %s %s %dx%d' % (r['game'], 'won' if won else 'lost', r['map'], r['w'], r['h'])
        for row in r['rows']:
            rnd, s, a, L, kd, j, M, tk, stp, free, pe, ov, ev, vis, taken, rc, al, ale = row[:18]
            if s != us or kd != 0 or L > 4:
                continue
            w = why(L, M, stp, vis, ov, ev, rnd, al, r['cells'])
            if taken != 1 and w in ('short', 'pearl'):
                rel = 'T' if M >= 2 * L else 'E' if M >= L else 'S'
                tot[(w, rel)] += 1
                per[(w, rel)][r['game']] += 1
                ex[(w, rel)].append('%s r%d ours %d at (%d,%d), their %d at (%d,%d), %d steps, heads in view %d v %d' % (
                    tag, rnd, L, row[18], row[19], M, row[20], row[21], stp, ov + 1, ev))
        for h in r['hos']:
            if not h['cross'] or h['ms'] == us:
                continue
            own = (h['L0'] + 3) // 4 + h['L0'] - 2
            if h['vk'] != 1 and h['Lv'] <= 4 and h['vs'] == 1 and h['vsafe'] and 3 <= h['L0'] <= 4 and h['k'] <= own and h['k'] > 1:
                tot['lunge'] += 1
                per['lunge'][r['game']] += 1
                ex['lunge'].append('%s r%d their %d from (%d,%d) walks %d steps into ours %d at (%d,%d); own heads within 5: theirs %d, ours %d' % (
                    tag, h['r'], h['L0'], h['sx'], h['sy'], h['k'], h['Lv'], h['x'], h['y'], h['m5'], h['v5']))
            if h['vk'] != 1 and h['Lv'] >= 8 and h['vs'] > 0:
                tot['long'] += 1
                per['long'][r['game']] += 1
                ex['long'].append('%s r%d their %d from (%d,%d) walks %d steps into ours %d at (%d,%d); state %d safe %d' % (
                    tag, h['r'], h['L0'], h['sx'], h['sy'], h['k'], h['Lv'], h['x'], h['y'], h['vs'], h['vsafe']))
    print('games', games)
    for k, n in sorted(tot.items(), key=lambda t: str(t[0])):
        c = per[k]
        print(k, 'events', n, 'a game %.2f' % (n / games), 'games with one', len(c), 'max in a game', max(c.values()))
        step = max(1, len(ex[k]) // 6)
        for e in ex[k][::step][:7]:
            print('    ', e)


main()
