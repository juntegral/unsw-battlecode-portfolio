#!/usr/bin/env python3
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
"""Verifier extras 12 (run of 2026-10-07 12:12 KST): the checks that try to break F42 and F38. Reads the x12 shards
and writes f42-f38-1212-extras.txt."""
import sys, json, math, random
from pathlib import Path
from collections import Counter, defaultdict
sys.dont_write_bytecode = True
V = Path('data/analysis/ladder/verify')
CUT = '2026-10-06T14:48:15'
LINES = []
THREE = ('Maze #1', 'weakhold #1', 'Tower Defense #1')


def say(*a):
    s = ' '.join(str(x) for x in a)
    LINES.append(s)
    print(s)


def load():
    games = []
    for k in range(6):
        for line in (V / ('x12-%d.jsonl' % k)).read_text().splitlines():
            if line.strip():
                games.append(json.loads(line))
    order = sorted(games, key=lambda g: (g.get('completedAt') or '', g['game']))
    maps = json.loads(Path('data/analysis/ladder/maps.json').read_text())
    seen = {}
    for g in order:
        lst = seen.setdefault(g['map'], [])
        if g['layout'] not in lst:
            lst.append(g['layout'])
        g['map_key'] = '%s #%d' % (g['map'], lst.index(g['layout']) + 1)
        e = g.get('opponentElo') or 0
        g['band'] = 'under 1700' if e < 1700 else '1700-1899' if e < 1900 else '1900-2099' if e < 2100 else '2100 on'
        g['free'] = not maps[g['map_key']]['queen_spawn_dead_end']
        g['half'] = 1 if g['completedAt'][:19] < CUT else 2
        g['p1'] = g['map_key'] == 'Portals #1'
        for s in (0, 1):
            prev_end = 0
            for st in sorted((x for x in g['stays'] if x['s'] == s), key=lambda x: x['r']):
                st['gap'] = st['r'] - prev_end
                prev_end = st['r'] + st['n']
    return order


def sh(a, n):
    return '%d of %d (%s)' % (a, n, '%.3f' % (a / n) if n else 'n/a')


def perm2(a1, n1, a0, n0, B=20000, seed=3):
    if not n1 or not n0:
        return 'n/a'
    rng = random.Random(seed)
    pool = [1] * (a1 + a0) + [0] * (n1 + n0 - a1 - a0)
    obs = abs(a1 / n1 - a0 / n0)
    hit = 0
    for _ in range(B):
        rng.shuffle(pool)
        x = sum(pool[:n1])
        if abs(x / n1 - (a1 + a0 - x) / n0) >= obs - 1e-12:
            hit += 1
    return '%d of %d' % (hit, B)


def kept42(g):
    f0, f1 = g['final']
    return g['last_round'] == 499 and f0['queen'] == 0 and f1['queen'] > 0 and g['free']


def flag42(g):
    return g['final'][0]['longest'] > g['final'][1]['longest']


def selfmade(g):
    qd = g['qdeath'][0]
    return qd['reason'] in (0, 1) or (qd['reason'] == 2 and qd['by'] == 1) or qd['reason'] == 4


def f42(games):
    say('=' * 20, 'F42 extras')
    both = [g for g in games if g['code'] in ('main', 'v31') and kept42(g)]
    for b in ('1700-1899', '1900-2099', '2100 on'):
        k = [g for g in both if g['band'] == b]
        say('both codes %s: %s' % (b, sh(sum(1 for g in k if flag42(g)), len(k))))
    lo = [g for g in both if g['band'] != '2100 on']
    hi = [g for g in both if g['band'] == '2100 on']
    say('both codes, under 2100 against 2100 on: %s against %s; label shuffles with a gap at least as large: %s' % (
        sh(sum(1 for g in lo if flag42(g)), len(lo)), sh(sum(1 for g in hi if flag42(g)), len(hi)),
        perm2(sum(1 for g in lo if flag42(g)), len(lo), sum(1 for g in hi if flag42(g)), len(hi))))
    lo = [g for g in both if g['band'] in ('under 1700', '1700-1899')]
    hi = [g for g in both if g['band'] not in ('under 1700', '1700-1899')]
    say('both codes, under 1900 against 1900 on: %s against %s; shuffles: %s' % (
        sh(sum(1 for g in lo if flag42(g)), len(lo)), sh(sum(1 for g in hi if flag42(g)), len(hi)),
        perm2(sum(1 for g in lo if flag42(g)), len(lo), sum(1 for g in hi if flag42(g)), len(hi))))
    for code in ('main', 'v31', 'both'):
        k = [g for g in both if code == 'both' or g['code'] == code]
        fl = [g for g in k if flag42(g)]
        nf = [g for g in k if not flag42(g)]
        a1, a0 = sum(1 for g in fl if selfmade(g)), sum(1 for g in nf if selfmade(g))
        say('%s: our queen died with no dragon of theirs in it (wall, own body, body of a dragon of ours, no action): flagged %s, not flagged %s; shuffles %s' % (
            code, sh(a1, len(fl)), sh(a0, len(nf)), perm2(a1, len(fl), a0, len(nf))))
        say('   %s flagged: we have 3 or fewer dragons left %d; their total over twice ours %d; our total over twice theirs %d; ours has more dragons %d' % (
            code, sum(1 for g in fl if g['final'][0]['alive'] <= 3), sum(1 for g in fl if g['final'][1]['total'] > 2 * g['final'][0]['total']),
            sum(1 for g in fl if g['final'][0]['total'] > 2 * g['final'][1]['total']), sum(1 for g in fl if g['final'][0]['alive'] > g['final'][1]['alive'])))
        say('   %s not flagged: we have 3 or fewer dragons left %d of %d; their total over twice ours %d' % (
            code, sum(1 for g in nf if g['final'][0]['alive'] <= 3), len(nf), sum(1 for g in nf if g['final'][1]['total'] > 2 * g['final'][0]['total'])))
        med = sorted(g['final'][1]['queen'] for g in fl)
        med2 = sorted(g['final'][1]['queen'] for g in nf)
        say('   %s their queen length median: flagged %s, not flagged %s; under 10: flagged %d of %d, not flagged %d of %d' % (
            code, med[len(med) // 2], med2[len(med2) // 2], sum(1 for x in med if x < 10), len(med), sum(1 for x in med2 if x < 10), len(med2)))
    # how many full games of each kind, to size the counts
    for code in ('main', 'v31'):
        gs = [g for g in games if g['code'] == code and g['free']]
        say('%s: games on free layouts %d, losses %d; flagged games are %d of those losses' % (
            code, len(gs), sum(1 for g in gs if not g['win'] and not g['drawn']), sum(1 for g in gs if kept42(g) and flag42(g))))


def stays(gs, s, lo=101, hi=200, kind='long'):
    out = []
    for g in gs:
        for st in g['stays']:
            if st['s'] != s or st['r'] < lo or st['r'] > hi:
                continue
            if (kind == 'long' and st['n'] >= 3) or (kind == 'short' and st['n'] <= 2) or kind == 'all':
                out.append((g, st))
    return out


def aw(sts):
    return sum(1 for g, st in sts if st['m'] and st['m']['aw'])


def en(sts):
    return sum(1 for g, st in sts if st['m'] and st['m']['en'])


def f38(games):
    say('')
    say('=' * 20, 'F38 extras')
    base = [g for g in games if g['code'] in ('main', 'v31') and g['free'] and not g['p1']]
    for code in ('main', 'v31'):
        gs = [g for g in base if g['code'] == code]
        say('--', code)
        for s, who in ((0, 'ours'), (1, 'theirs')):
            for kind in ('long', 'short'):
                sts = stays(gs, s, kind=kind)
                c = Counter()
                ca = Counter()
                for g, st in sts:
                    k = '1' if st['gap'] <= 1 else '2-3' if st['gap'] <= 3 else '4 on'
                    c[k] += 1
                    if st['m'] and st['m']['aw']:
                        ca[k] += 1
                say('%s %s %s: turn starts on wider tiles since her last stay: %s' % (
                    code, who, kind, '; '.join('%s: %d stays, another way %d' % (k, c[k], ca[k]) for k in ('1', '2-3', '4 on'))))
                ob = sum(1 for g, st in sts if st['m'] and st['m']['ob'])
                fb = sum(1 for g, st in sts if st['m'] and st['m']['fb'])
                say('      at the mouth: body of another dragon of her side on a neighbour tile %s; of the other side %s' % (sh(ob, len(sts)), sh(fb, len(sts))))
                noaw = [(g, st) for g, st in sts if st['m'] and not st['m']['aw']]
                say('      of the %d without another way: only one free neighbour %d; own other dragon beside %d; she dies in the stay %d (with another way: %d of %d)' % (
                    len(noaw), sum(1 for g, st in noaw if st['m']['nf'] == 1), sum(1 for g, st in noaw if st['m']['ob']),
                    sum(1 for g, st in noaw if st['died']), sum(1 for g, st in sts if st['died'] and st['m'] and st['m']['aw']), aw(sts)))
            lg = stays(gs, s)
            t3 = [x for x in lg if x[0]['map_key'] in THREE]
            rest = [x for x in lg if x[0]['map_key'] not in THREE]
            say('%s %s long: Maze, weakhold, Tower Defense: another way %s, enemy near %s; other layouts: another way %s, enemy near %s' % (
                code, who, sh(aw(t3), len(t3)), sh(en(t3), len(t3)), sh(aw(rest), len(rest)), sh(en(rest), len(rest))))
            st3 = [x for x in stays(gs, s, kind='short') if x[0]['map_key'] in THREE]
            srest = [x for x in stays(gs, s, kind='short') if x[0]['map_key'] not in THREE]
            say('%s %s short: the three layouts: another way %s; other layouts: %s' % (code, who, sh(aw(st3), len(st3)), sh(aw(srest), len(srest))))
            # base rate of an enemy head near at any turn start on a wider tile, by slice
            for label, sel in (('all', lambda g: True), ('half 1', lambda g: g['half'] == 1), ('half 2', lambda g: g['half'] == 2),
                               ('1700-1899', lambda g: g['band'] == '1700-1899'), ('1900-2099', lambda g: g['band'] == '1900-2099'),
                               ('three layouts', lambda g: g['map_key'] in THREE), ('other layouts', lambda g: g['map_key'] not in THREE)):
                tot = e1 = a1 = 0
                for g in gs:
                    if not sel(g):
                        continue
                    for key, n in g['wts'][s].items():
                        w, a, e, nfc, hn, out = key.split('|')
                        if w != '1':
                            continue
                        tot += n
                        e1 += n if e == '1' else 0
                        a1 += n if a == '1' else 0
                sl = [x for x in lg if sel(x[0])]
                say('      %s %s %s: every turn start on a wider tile r100-199: enemy near %s, free wider neighbour %s | mouths of long stays: enemy near %s, another way %s' % (
                    code, who, label, sh(e1, tot), sh(a1, tot), sh(en(sl), len(sl)), sh(aw(sl), len(sl))))
        # game level: share of games
        lg = stays(gs, 0)
        per = defaultdict(lambda: [0, 0])
        for g, st in lg:
            per[g['game']][1] += 1
            per[g['game']][0] += 1 if (st['m'] and st['m']['aw']) else 0
        say('%s ours long: games %d; games where under half have another way %d; exactly half %d; over half %d' % (
            code, len(per), sum(1 for a, n in per.values() if 2 * a < n), sum(1 for a, n in per.values() if 2 * a == n), sum(1 for a, n in per.values() if 2 * a > n)))
        bt = defaultdict(lambda: [0, 0])
        for g, st in lg:
            bt[g['battle']][1] += 1
            bt[g['battle']][0] += 1 if (st['m'] and st['m']['aw']) else 0
        rng = random.Random(11)
        vals = list(bt.values())
        outs = []
        for _ in range(4000):
            a = n = 0
            for _ in range(len(vals)):
                x = vals[rng.randrange(len(vals))]
                a += x[0]
                n += x[1]
            if n:
                outs.append(a / n)
        outs.sort()
        say('%s ours long: battles %d; battle bootstrap of the another way share %.2f to %.2f; resamples at one half or more: %d of %d' % (
            code, len(vals), outs[int(0.025 * len(outs))], outs[int(0.975 * len(outs)) - 1], sum(1 for x in outs if x >= 0.5), len(outs)))


def main():
    games = load()
    f42(games)
    f38(games)
    out = open(P + 'f42-f38-1212-extras.txt', 'w')
    out.write('\n'.join(LINES) + '\n')
    out.close()


main()
