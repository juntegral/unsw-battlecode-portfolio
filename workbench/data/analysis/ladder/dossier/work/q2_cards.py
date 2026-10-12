"""Scratch (diag-queenhit2): the candidate switches replayed on every queen turn of one arm: step away from the
nearest seen head, a floor under her length (no split at line 638, no paid sprint with a clean step open), keep 4
on paper, and where the deaths in pockets began. Usage: python3 .../q2_cards.py new|main"""
import sys
import json
sys.dont_write_bytecode = True
from collections import Counter, defaultdict
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')
ARMS = dict(new=('agg8-q1', 'agg8-q2'), main=('agg7-m1', 'agg7-m2', 'agg7-m3'))


def load(arm):
    fates, turns = {}, defaultdict(list)
    for label in ARMS[arm]:
        p = WORK / ('q2_scan-%s.jsonl' % label)
        if not p.exists():
            continue
        with p.open() as fh:
            for line in fh:
                r = json.loads(line)
                if r['k'] == 'f':
                    fates[r['game']] = r
                else:
                    turns[r['game']].append(r)
    return fates, turns


def true_reach(n):
    return (n + 3) // 4 + n - 2


def free_of(n):
    return (n + 3) // 4


def near_d(t):
    return t['near'][0][0] if t['near'] else 99


def first_step(t):
    a = t.get('action') or {}
    if a.get('kind') != 'move' or not a.get('dirs'):
        return None
    return [c for c in t['cands'] if c['d'] == a['dirs'][0]][0]


def clean(c):
    return c.get('enterable') and c['risk'] == 0 and not c['closed'] and c['kind'] == 'open'


def pct(a, b):
    return '%d/%d (%.1f%%)' % (a, b, 100.0 * a / b) if b else '0/0'


def main():
    arm = sys.argv[1]
    fates, turns = load(arm)
    hit_games = set(g for g, f in fates.items() if f['fate'] and not f['fate']['mover'] and f['fate']['cause'] == 'head-on')
    dead_games = set(g for g, f in fates.items() if f['fate'])
    print('arm', arm, 'games', len(fates), 'hit deaths', len(hit_games), 'all deaths', len(dead_games))

    def left(g, i):
        return len(turns[g]) - 1 - i

    def hit_in(g, i, n):
        return g in hit_games and left(g, i) < n

    print()
    print('== 1. step away: single-step moves with a seen head (not the enemy queen) within N tiles of the tile taken or her head ==')
    for N in (4, 5, 6):
        c = Counter()
        rows = []
        for g, ts in turns.items():
            for i, t in enumerate(ts):
                f = first_step(t)
                if f is None or not clean(f) or len(t.get('path', [])) != 1:
                    continue
                if f['edist'] > N:
                    continue
                alts = [x for x in t['cands'] if x is not f and clean(x)]
                if not alts:
                    continue
                far = max(x['edist'] for x in alts)
                if far > f['edist']:
                    c['closer'] += 1
                    c['closer h3'] += hit_in(g, i, 3)
                    c['closer pearl'] += bool(f.get('pearl'))
                    rows.append((g, left(g, i), f['edist'], far))
                else:
                    c['farthest'] += 1
                    c['farthest h3'] += hit_in(g, i, 3)
        last3 = [r for r in rows if r[0] in dead_games and r[1] < 3]
        games = sorted(set(r[0] for r in last3))
        print('  N<=%d: took a clean tile nearer to a seen head than another clean tile: %s hit within 3 (pearl steps %d) | took the farthest clean tile: %s | fires in the last 3 turns of %d deaths %s (hit deaths %d), fires elsewhere %d' % (
            N, pct(c['closer h3'], c['closer']), c['closer pearl'], pct(c['farthest h3'], c['farthest']), len(games), games, len([g for g in games if g in hit_games]), len(rows) - len(last3)))

    print()
    print('== 2. a floor under her length ==')
    c = Counter()
    for g, ts in turns.items():
        for i, t in enumerate(ts):
            a = t.get('action') or {}
            exposed = t['hit_head'] or t['pay_head']
            if a.get('kind') == 'split' and t['hit_blocked'] and not exposed and t.get('L_after', 9) < 3:
                c['split at 638 leaving 2'] += 1
                c['split at 638 leaving 2, any death within 2 turns'] += g in dead_games and left(g, i) < 3
                c['split at 638 leaving 2, pay tile open'] += t['open1']
            if a.get('kind') == 'move' and len(t.get('path', [])) > free_of(t['L']) and t['open0'] and not t['hit_blocked'] and t['L_after'] < 3:
                c['paid sprint to 2 with a clean step open'] += 1
                c['paid sprint to 2 with a clean step open, later died 2 long by a hit'] += g in hit_games and ts[-1]['L'] == 2 and all(x['L'] == 2 for x in ts[i + 1:])
                c['paid sprint to 2 with a clean step open, no head within 5 steps'] += near_d(t) > 5
                c['paid sprint to 2 with a clean step open, hit within 3'] += hit_in(g, i, 3)
    print('  ', dict(c))
    c = Counter()
    for g in sorted(dead_games):
        ts = turns[g]
        t = ts[-1]
        if t['L'] != 2:
            continue
        how = 'start'
        for j in range(len(ts) - 2, -1, -1):
            x = ts[j]
            if x['L'] > 2 and x['L_after'] <= 2:
                a = x.get('action') or {}
                exposed = x['hit_head'] or x['pay_head']
                if a.get('kind') == 'split':
                    how = 'split 638' if x['hit_blocked'] and not exposed else 'forced split' if exposed else 'wait split (695)'
                else:
                    how = 'paid escape, no clean step' if x['hit_blocked'] else 'paid sprint, clean step open'
                break
        kind = 'hit' if g in hit_games else 'own move'
        boxed_esc = t['hit_blocked'] and t['esc_open'] <= 2
        c[kind, how] += 1
        c[kind, how, 'boxed with a clean tile 2 steps off'] += boxed_esc
    for k in sorted(c, key=str):
        print('   died 2 long:', k, c[k])

    print()
    print('== 3. keep 4 on paper (same pearls, same paid steps, same forced and wait splits; a routine split only from 6) ==')
    c = Counter()
    for g, ts in turns.items():
        Lp = ts[0]['L']
        for i, t in enumerate(ts):
            t['paper'] = Lp
            a = t.get('action') or {}
            if t['round'] <= 300:
                c['turns'] += 1
                c['actual L%d' % min(t['L'], 5)] += 1
                c['paper L%d' % min(Lp, 5)] += 1
            after = t.get('L_after', 0)
            if not after:
                continue
            if a.get('kind') == 'split':
                exposed = t['hit_head'] or t['pay_head']
                routine = t['open0'] and not t['hit_blocked'] and not exposed and t['any_enterable']
                child = t['L'] - after
                if routine:
                    c['routine splits'] += 1
                    if Lp - 2 >= 4:
                        Lp -= 2
                        c['paper routine splits'] += 1
                elif Lp - child >= 2:
                    Lp -= child
            else:
                Lp = max(2, Lp + after - t['L'])
    print('  ', dict(c))
    for g in sorted(hit_games):
        t = turns[g][-1]
        if t['hit_blocked']:
            print('   boxed death %d: L %d, on paper %d, clean tile at %d steps, paid reach on paper %d -> %s' % (
                g, t['L'], t['paper'], t['esc_open'], true_reach(t['paper']) if t['paper'] >= 3 else 0, 'escape on paper' if t['paper'] >= 3 and t['esc_open'] <= true_reach(t['paper']) else 'no'))

    print()
    print('== 4. deaths in pockets (wall, own body): where they began ==')
    small = Counter()
    for g, f in fates.items():
        key = '<=600' if f['cells'] <= 600 else '>600'
        small[key, 'games'] += 1
        d = f['fate']
        if d and d['mover'] and d['cause'] in ('wall', 'own body'):
            small[key, 'pocket deaths'] += 1
    print('   by board size:', dict(small))
    for g, f in sorted(fates.items()):
        d = f['fate']
        if not d or not d['mover'] or d['cause'] not in ('wall', 'own body'):
            continue
        ts = turns[g]
        found = None
        for i in range(len(ts) - 1, -1, -1):
            t = ts[i]
            fs = first_step(t)
            alts = [x for x in t['cands'] if x.get('enterable') and x is not fs and not x['closed']]
            if alts:
                found = (i, t, fs, alts)
                break
        mate = 0
        for t in ts[-3:]:
            mate += any((not x.get('enterable')) and x.get('occ') in ('allyH', 'allyB') for x in t['cands'] if x['kind'] != 'kelp')
        waits = sum(1 for t in ts[-6:] if (t.get('action') or {}).get('kind') == 'split')
        pearls = sum(1 for t in ts[-6:] if first_step(t) is not None and first_step(t).get('pearl'))
        line = '   %d %dx%d (%d cells) r%d %s L%d | team mate on one of her sides in the last 3 turns: %d turns | splits in the last 6 turns %d, pearl steps %d' % (
            g, f['W'], f['H'], f['cells'], d['round'], d['cause'], d['L'], mate, waits, pearls)
        if found:
            i, t, fs, alts = found
            a = t.get('action') or {}
            line += ' | last turn with a tile that was not a pocket left untaken: %d turns before (L%d, %s, took %s; left %s)' % (
                len(ts) - 1 - i, t['L'], a.get('kind'),
                None if fs is None or not fs.get('enterable') else '%s open%d exits%d%s' % ('pocket' if fs['closed'] else 'free', 4 - fs['kelp'], fs['exits'], ' pearl' if fs['pearl'] else ''),
                ['open%d exits%d%s' % (4 - x['kelp'], x['exits'], ' pearl' if x['pearl'] else '') for x in alts])
        print(line)


main()
