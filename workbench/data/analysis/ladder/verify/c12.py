#!/usr/bin/env python3
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
"""Verifier claims 12 (run of 2026-10-07 12:12 KST). F42: full-game losses with only their queen alive in which
our longest living dragon is the longer one. F38: what the queen had beside her at the mouth of a stay on narrow
tiles. Reads the x12 shards (own extraction from the raw replays) and writes f42-f38-1212-numbers.txt. maps.json is
read for the dead-end flag of a layout; rows.jsonl is read only in the last section, to compare."""
import sys, json, math, random
from pathlib import Path
from collections import Counter, defaultdict
sys.dont_write_bytecode = True
V = Path('data/analysis/ladder/verify')
CUT = '2026-10-06T14:48:15'
LINES = []
REASON = ['wall', 'own body', 'other dragon body', 'head-on', 'other']


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
    bad = [g for g in games if 'error' in g]
    games = [g for g in games if 'error' not in g]
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
        g['opp'] = '%s (%s)' % (g.get('opponent'), g.get('opponentId'))
        g['day'] = (g.get('at_kst') or '')[:13]
    return order, bad, maps


def wilson(a, n, z=1.96):
    if n == 0:
        return 'n/a'
    p = a / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return '%.2f to %.2f' % ((c - h) / d, (c + h) / d)


def boot(pairs, B=4000, seed=7):
    rng = random.Random(seed)
    k = len(pairs)
    out = []
    for _ in range(B):
        a = n = 0
        for _ in range(k):
            x = pairs[rng.randrange(k)]
            a += x[0]
            n += x[1]
        if n:
            out.append(a / n)
    out.sort()
    if not out:
        return 'n/a'
    return '%.2f to %.2f' % (out[int(0.025 * len(out))], out[int(0.975 * len(out)) - 1])


def sh(a, n):
    return '%d of %d (%s)' % (a, n, '%.3f' % (a / n) if n else 'n/a')


def perm2(a1, n1, a0, n0, B=20000, seed=3):
    """share of label shuffles with a gap in shares at least as large (two sided)"""
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


# ---------------------------------------------------------------- F42

def kept42(g, need_free=True):
    f0, f1 = g['final']
    return g['last_round'] == 499 and f0['queen'] == 0 and f1['queen'] > 0 and (g['free'] or not need_free)


def flag42(g):
    return g['final'][0]['longest'] > g['final'][1]['longest']


def mirror42(g):
    f0, f1 = g['final']
    return g['last_round'] == 499 and f0['queen'] > 0 and f1['queen'] == 0 and g['free']


def line42(label, gs):
    k = [g for g in gs if kept42(g)]
    fl = [g for g in k if flag42(g)]
    say('%-44s %s   interval %s' % (label, sh(len(fl), len(k)), wilson(len(fl), len(k))))
    return k, fl


def f42(games):
    say('=' * 30, 'F42')
    for code in ('main', 'v31'):
        gs = [g for g in games if g['code'] == code]
        say('')
        say('--', code, 'games', len(gs), 'ranked', sum(1 for g in gs if g.get('ranked')),
            'full length (raw round 499)', sum(1 for g in gs if g['last_round'] == 499),
            'full length on free layouts', sum(1 for g in gs if g['last_round'] == 499 and g['free']))
        full = [g for g in gs if g['last_round'] == 499 and g['free']]
        qe = Counter()
        for g in full:
            f0, f1 = g['final']
            key = ('both alive' if f0['queen'] and f1['queen'] else 'only ours' if f0['queen'] else
                   'only theirs' if f1['queen'] else 'both dead')
            qe[(key, 'win' if g['win'] else 'draw' if g['drawn'] else 'loss')] += 1
        say('   full games on free layouts by queens at end and result:', dict(sorted((('%s / %s' % k), v) for k, v in qe.items())))
        k, fl = line42(code, gs)
        say('   kept games that are not losses:', sum(1 for g in k if g['win'] or g['drawn']))
        say('   equal longest in kept:', sum(1 for g in k if g['final'][0]['longest'] == g['final'][1]['longest']),
            '  ours shorter:', sum(1 for g in k if g['final'][0]['longest'] < g['final'][1]['longest']))
        if code == 'main':
            line42('main half 1', [g for g in gs if g['half'] == 1])
            line42('main half 2', [g for g in gs if g['half'] == 2])
        for b in ('under 1700', '1700-1899', '1900-2099', '2100 on'):
            line42(code + ' ' + b, [g for g in gs if g['band'] == b])
        say('   by layout (flagged of kept):', ', '.join('%s %d of %d' % (m, sum(1 for g in k if g['map_key'] == m and flag42(g)), n)
                                                         for m, n in sorted(Counter(g['map_key'] for g in k).items(), key=lambda x: -x[1])))
        say('   flagged by layout:', ', '.join('%s %d' % (m, n) for m, n in Counter(g['map_key'] for g in fl).most_common()))
        say('   by opponent (flagged of kept):', ', '.join('%s %d of %d' % (m, sum(1 for g in k if g['opp'] == m and flag42(g)), n)
                                                           for m, n in sorted(Counter(g['opp'] for g in k).items(), key=lambda x: -x[1])))
        say('   by KST date:', ', '.join('%s %d of %d' % (m, sum(1 for g in k if g['day'][:10] == m and flag42(g)), n)
                                         for m, n in sorted(Counter(g['day'][:10] for g in k).items())))
        bt = defaultdict(lambda: [0, 0])
        for g in k:
            bt[g['battle']][1] += 1
            bt[g['battle']][0] += 1 if flag42(g) else 0
        say('   battles with a kept game:', len(bt), ' battle bootstrap of the share:', boot(list(bt.values())))
        lo = []
        for m in sorted(set(g['opp'] for g in k)):
            kk = [g for g in k if g['opp'] != m]
            lo.append((sum(1 for g in kk if flag42(g)) / len(kk), m, sum(1 for g in kk if flag42(g)), len(kk)))
        lo.sort()
        say('   one opponent left out: %.3f (%s, %d of %d) to %.3f (%s, %d of %d)' % (lo[0][0], lo[0][1], lo[0][2], lo[0][3], lo[-1][0], lo[-1][1], lo[-1][2], lo[-1][3]))
        lo = []
        for m in sorted(set(g['map_key'] for g in k)):
            kk = [g for g in k if g['map_key'] != m]
            lo.append((sum(1 for g in kk if flag42(g)) / len(kk), m, sum(1 for g in kk if flag42(g)), len(kk)))
        lo.sort()
        say('   one layout left out: %.3f (%s, %d of %d) to %.3f (%s, %d of %d)' % (lo[0][0], lo[0][1], lo[0][2], lo[0][3], lo[-1][0], lo[-1][1], lo[-1][2], lo[-1][3]))
        say('   three flagged games removed: %s' % sh(len(fl) - 3, len(k) - 3))
        say('   flagged games:')
        say('   game battle layout | opponent rating | our longest, their longest (margin) | their queen | our total, their total | alive ours, theirs | our queen died r, cause, length, killer side | kst')
        for g in fl:
            f0, f1 = g['final']
            qd = g['qdeath'][0]
            say('   %d %s %s | %s %s | %d, %d (+%d) | %d%s | %d, %d | %d, %d | r%d, %s, %d, by %d, their longest then %d, ours %d | %s' % (
                g['game'], g['battle'], g['map_key'], g['opp'], g.get('opponentElo'), f0['longest'], f1['longest'],
                f0['longest'] - f1['longest'], f1['queen'], ' (their longest)' if f1['queen'] == f1['longest'] else '',
                f0['total'], f1['total'], f0['alive'], f1['alive'], qd['round'], REASON[qd['reason']], qd['length'], qd['by'],
                qd['longest'][1], qd['longest'][0], g['day']))
        say('   their queen length in flagged, sorted:', sorted(g['final'][1]['queen'] for g in fl))
        say('   their queen is their longest:', sh(sum(1 for g in fl if g['final'][1]['queen'] == g['final'][1]['longest']), len(fl)))
        say('   their queen 4 or less:', sh(sum(1 for g in fl if g['final'][1]['queen'] <= 4), len(fl)),
            ' 6 or less:', sum(1 for g in fl if g['final'][1]['queen'] <= 6), ' 10 or more:', sum(1 for g in fl if g['final'][1]['queen'] >= 10))
        nf = [g for g in k if not flag42(g)]
        say('   their queen length in the kept games not flagged, sorted:', sorted(g['final'][1]['queen'] for g in nf))
        say('   their queen 4 or less in not flagged:', sh(sum(1 for g in nf if g['final'][1]['queen'] <= 4), len(nf)))
        say('   our queen death round in flagged, sorted:', sorted(g['qdeath'][0]['round'] for g in fl))
        say('   our queen death cause in flagged:', dict(Counter(REASON[g['qdeath'][0]['reason']] for g in fl)))
        say('   our queen death round in not flagged, sorted:', sorted(g['qdeath'][0]['round'] for g in nf))
        say('   our queen death cause in not flagged:', dict(Counter(REASON[g['qdeath'][0]['reason']] for g in nf)))
        say('   our total larger in flagged:', sh(sum(1 for g in fl if g['final'][0]['total'] > g['final'][1]['total']), len(fl)),
            ' equal:', sum(1 for g in fl if g['final'][0]['total'] == g['final'][1]['total']))
        say('   our total larger in not flagged:', sh(sum(1 for g in nf if g['final'][0]['total'] > g['final'][1]['total']), len(nf)))
        say('   margin of the longest in flagged, sorted:', sorted(g['final'][0]['longest'] - g['final'][1]['longest'] for g in fl))
        say('   margin 1 or 2:', sum(1 for g in fl if g['final'][0]['longest'] - g['final'][1]['longest'] <= 2),
            '  margin 5 or more:', sum(1 for g in fl if g['final'][0]['longest'] - g['final'][1]['longest'] >= 5))
        say('   our longest over their queen length in flagged:', sum(1 for g in fl if g['final'][0]['longest'] > g['final'][1]['queen']), 'of', len(fl))
        say('   flagged with our queen dead before raw round 100:', sum(1 for g in fl if g['qdeath'][0]['round'] < 100),
            ' not flagged:', sum(1 for g in nf if g['qdeath'][0]['round'] < 100), 'of', len(nf))
        say('   at the round our queen died, in flagged: our longest other dragon longer than their longest:',
            sum(1 for g in fl if g['qdeath'][0]['longest'][0] > g['qdeath'][0]['longest'][1]), 'of', len(fl))
        # Slithery Fight
        sf = [g for g in gs if g['map_key'] == 'Slithery Fight #1' and kept42(g, need_free=False)]
        say('   Slithery Fight #1 (dead end at spawn): flagged %s; their queen there: %s' % (
            sh(sum(1 for g in sf if flag42(g)), len(sf)), sorted(g['final'][1]['queen'] for g in sf if flag42(g))))
        de = [g for g in gs if not g['free'] and kept42(g, need_free=False)]
        say('   all dead-end layouts: flagged of kept by layout:', ', '.join('%s %d of %d' % (m, sum(1 for g in de if g['map_key'] == m and flag42(g)), n)
                                                                               for m, n in sorted(Counter(g['map_key'] for g in de).items())))
        mi = [g for g in gs if mirror42(g)]
        say('   mirror: full games with only our queen alive on free layouts: %d, not wins %d, our longest strictly shorter %s, equal %d' % (
            len(mi), sum(1 for g in mi if not g['win']), sh(sum(1 for g in mi if g['final'][0]['longest'] < g['final'][1]['longest']), len(mi)),
            sum(1 for g in mi if g['final'][0]['longest'] == g['final'][1]['longest'])))
        a1, n1 = len(fl), len(k)
        a0 = sum(1 for g in mi if g['final'][0]['longest'] < g['final'][1]['longest'])
        say('   flagged share against mirror share, label shuffles with a gap at least as large:', perm2(a1, n1, a0, len(mi)))
    m = [g for g in games if g['code'] == 'main']
    v = [g for g in games if g['code'] == 'v31']
    km = [g for g in m if kept42(g)]
    kv = [g for g in v if kept42(g)]
    say('')
    say('main against v31 share, label shuffles with a gap at least as large:',
        perm2(sum(1 for g in km if flag42(g)), len(km), sum(1 for g in kv if flag42(g)), len(kv)))
    both = km + kv
    say('both codes: %s  interval %s' % (sh(sum(1 for g in both if flag42(g)), len(both)), wilson(sum(1 for g in both if flag42(g)), len(both))))
    oth = [g for g in games if g['code'] == 'other' and kept42(g)]
    say('other codes (test builds): %s' % sh(sum(1 for g in oth if flag42(g)), len(oth)))


# ---------------------------------------------------------------- F38

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


def line38(label, sts):
    n = len(sts)
    nm = sum(1 for g, st in sts if not st['m'])
    say('%-52s another way %s [%s], enemy near %s [%s]%s' % (label, sh(aw(sts), n), wilson(aw(sts), n), sh(en(sts), n), wilson(en(sts), n),
                                                         '  (no mouth turn: %d)' % nm if nm else ''))


def gboot(sts, fn):
    d = defaultdict(lambda: [0, 0])
    for g, st in sts:
        d[g['game']][1] += 1
        d[g['game']][0] += 1 if fn(st) else 0
    return boot(list(d.values())), len(d)


def split38(label, sts):
    n = len(sts)
    c = Counter()
    for g, st in sts:
        m = st['m']
        if not m:
            c['no mouth turn'] += 1
        elif m['aw']:
            c['a free wider neighbour'] += 1
        elif m['nw'] == 0:
            c['no wider neighbour tile at all (every neighbour narrow)'] += 1
        elif m['nw'] - m['nfw'] == m['sb'] and m['ob'] + m['fb'] == 0:
            c['wider neighbours all under her own body'] += 1
        else:
            c['wider neighbours under bodies, another dragon among them (own other %d, foe %d)' % (1 if m['ob'] else 0, 1 if m['fb'] else 0)] += 1
    say('   %s (%d):' % (label, n), '; '.join('%s %d' % kv for kv in c.most_common()))
    c2 = Counter()
    for g, st in sts:
        m = st['m']
        if m:
            c2['free neighbours %d (wider %d, narrow %d)' % (m['nf'], m['nfw'], m['nfn'])] += 1
    say('      free neighbour tiles at the mouth:', '; '.join('%s: %d' % kv for kv in sorted(c2.items())))
    say('      mouth tile open sides:', dict(Counter(st['m']['no'] for g, st in sts if st['m'])),
        ' first narrow tile next to the mouth tile:', sum(1 for g, st in sts if st['m'] and st['m']['adj']),
        ' steps in the mouth turn:', dict(Counter(st['m']['ms'] for g, st in sts if st['m'])),
        ' three open sides and every neighbour narrow:', sum(1 for g, st in sts if st['m'] and st['m']['no'] == 3 and st['m']['nw'] == 0),
        ' only one free neighbour:', sum(1 for g, st in sts if st['m'] and st['m']['nf'] == 1))


def f38(games):
    say('')
    say('=' * 30, 'F38')
    base = [g for g in games if g['code'] in ('main', 'v31') and g['free'] and not g['p1']]
    for code in ('main', 'v31'):
        gs = [g for g in base if g['code'] == code]
        say('')
        say('--', code, 'games', len(gs), ' half 1:', sum(1 for g in gs if g['half'] == 1), ' half 2:', sum(1 for g in gs if g['half'] == 2))
        for s, who in ((0, 'ours'), (1, 'theirs')):
            lg = stays(gs, s)
            st_all = stays(gs, s, kind='all')
            say('%s %s: stays begun in r101-200: %d, long %d, short %d' % (code, who, len(st_all), len(lg), len(stays(gs, s, kind='short'))))
            line38('%s %s long' % (code, who), lg)
            line38('%s %s short (1 or 2 turn starts)' % (code, who), stays(gs, s, kind='short'))
            b1, ng = gboot(lg, lambda st: st['m'] and st['m']['aw'])
            b2, ng = gboot(lg, lambda st: st['m'] and st['m']['en'])
            say('   long: games holding them %d; game bootstrap another way %s, enemy near %s' % (ng, b1, b2))
            split38('%s %s long' % (code, who), lg)
            split38('%s %s short' % (code, who), stays(gs, s, kind='short'))
            sh_ = stays(gs, s, kind='short')
            say('   long against short, another way: label shuffles with a gap at least as large:', perm2(aw(lg), len(lg), aw(sh_), len(sh_)),
                ' enemy near:', perm2(en(lg), len(lg), en(sh_), len(sh_)))
            if s == 0:
                line38('%s ours long half 1' % code, [x for x in lg if x[0]['half'] == 1])
                line38('%s ours long half 2' % code, [x for x in lg if x[0]['half'] == 2])
                for b in ('under 1700', '1700-1899', '1900-2099', '2100 on'):
                    line38('%s ours long %s' % (code, b), [x for x in lg if x[0]['band'] == b])
                for m, n in Counter(x[0]['map_key'] for x in lg).most_common():
                    line38('%s ours long %s' % (code, m), [x for x in lg if x[0]['map_key'] == m])
                for m, n in sorted(Counter(x[0]['day'][:10] for x in lg).items()):
                    line38('%s ours long KST %s' % (code, m), [x for x in lg if x[0]['day'][:10] == m])
                opp = Counter(x[0]['opp'] for x in lg)
                say('   by opponent:', ', '.join('%s %d of %d' % (m, aw([x for x in lg if x[0]['opp'] == m]), n) for m, n in opp.most_common()))
                lo = []
                for m in opp:
                    kk = [x for x in lg if x[0]['opp'] != m]
                    lo.append((aw(kk) / len(kk), m, aw(kk), len(kk)))
                lo.sort()
                say('   one opponent left out: %.3f (%s, %d of %d) to %.3f (%s, %d of %d)' % (lo[0][0], lo[0][1], lo[0][2], lo[0][3], lo[-1][0], lo[-1][1], lo[-1][2], lo[-1][3]))
                lo = []
                for m in set(x[0]['map_key'] for x in lg):
                    kk = [x for x in lg if x[0]['map_key'] != m]
                    lo.append((aw(kk) / len(kk), m, aw(kk), len(kk)))
                lo.sort()
                say('   one layout left out: %.3f (%s, %d of %d) to %.3f (%s, %d of %d)' % (lo[0][0], lo[0][1], lo[0][2], lo[0][3], lo[-1][0], lo[-1][1], lo[-1][2], lo[-1][3]))
                pg = Counter()
                pa = Counter()
                for g, st in lg:
                    pg[g['game']] += 1
                    if st['m'] and st['m']['aw']:
                        pa[g['game']] += 1
                top = sorted(pg, key=lambda x: -(pg[x] - pa[x]))[:3]
                say('   three games with the most long stays without another way:', ', '.join('%d (%d of %d with another way)' % (x, pa[x], pg[x]) for x in top))
                kk = [x for x in lg if x[0]['game'] not in top]
                line38('%s ours long without those three games' % code, kk)
                top = sorted(pg, key=lambda x: -pg[x])[:3]
                say('   three games with the most long stays:', ', '.join('%d (%d of %d)' % (x, pa[x], pg[x]) for x in top))
                line38('%s ours long without those three' % code, [x for x in lg if x[0]['game'] not in top])
                say('   games by share: games with long stays %d; with none having another way %d; with all having %d' % (
                    len(pg), sum(1 for x in pg if pa[x] == 0), sum(1 for x in pg if pa[x] == pg[x])))
            # all rounds, long stays that end in her death
            dl = [x for x in stays(gs, s, lo=0, hi=499) if x[1]['died']]
            line38('%s %s long, any round, ending in her death' % (code, who), dl)
            al = stays(gs, s, lo=0, hi=499)
            line38('%s %s long, any round, all' % (code, who), al)
            dl2 = [x for x in lg if x[1]['died']]
            line38('%s %s long r101-200 ending in her death' % (code, who), dl2)
            line38('%s %s long r101-200 she leaves alive' % (code, who), [x for x in lg if not x[1]['died']])
        ol = stays(gs, 0)
        tl = stays(gs, 1)
        say('   ours against theirs, long, another way: label shuffles with a gap at least as large:', perm2(aw(ol), len(ol), aw(tl), len(tl)),
            ' enemy near:', perm2(en(ol), len(ol), en(tl), len(tl)))
        # every turn start on a wider tile whose next turn start falls in r101-200
        for s, who in ((0, 'ours'), (1, 'theirs')):
            c = Counter()
            for g in gs:
                for key, n in g['wts'][s].items():
                    w, a, e, nfc, hn, out = key.split('|')
                    if w != '1':
                        continue
                    c[(int(a), int(e), int(hn), out)] += n
            tot = sum(c.values())
            a1 = sum(n for (a, e, hn, out), n in c.items() if a == 1)
            e1 = sum(n for (a, e, hn, out), n in c.items() if e == 1)
            say('%s %s: turn starts on a wider tile in r100-199: %d; with a free wider neighbour %s; enemy head within 3 %s' % (code, who, tot, sh(a1, tot), sh(e1, tot)))
            for a in (1, 0):
                for hn in (1, 0):
                    n = sum(v for (a_, e, hn_, out), v in c.items() if a_ == a and hn_ == hn)
                    nar = c[(a, 0, hn, 'narrow')] + c[(a, 1, hn, 'narrow')]
                    died = c[(a, 0, hn, 'died')] + c[(a, 1, hn, 'died')]
                    say('      free wider neighbour %d, free narrow neighbour %d: %d turn starts, next turn start on a narrow tile %s, died before it %d' % (a, hn, n, sh(nar, n), died))
            for e in (1, 0):
                n = sum(v for (a, e_, hn, out), v in c.items() if e_ == e)
                nar = sum(v for (a, e_, hn, out), v in c.items() if e_ == e and out == 'narrow')
                say('      enemy near %d: %d turn starts, next on a narrow tile %s' % (e, n, sh(nar, n)))
            st_all = stays(gs, s, kind='all')
            say('      check: next-on-narrow total %d equals stays begun in r101-200 %d' % (sum(v for (a, e, hn, out), v in c.items() if out == 'narrow'), len(st_all)))
    # new games
    for code in ('main', 'v31'):
        new = [g for g in base if g['code'] == code and int(g['battle']) > 1298211]
        say('%s games of battles after 1298211: %d' % (code, len(new)),
            ' long share r101-200: ours %s, theirs %s' % (sh(len(stays(new, 0)), len(stays(new, 0, kind='all'))), sh(len(stays(new, 1)), len(stays(new, 1, kind='all')))))
        if new:
            line38('   %s ours long in those' % code, stays(new, 0))
    m = [g for g in base if g['code'] == 'main']
    say('main, long share r101-200: ours %s, theirs %s' % (sh(len(stays(m, 0)), len(stays(m, 0, kind='all'))), sh(len(stays(m, 1)), len(stays(m, 1, kind='all')))))
    v = [g for g in base if g['code'] == 'v31']
    say('v31, long share r101-200: ours %s, theirs %s' % (sh(len(stays(v, 0)), len(stays(v, 0, kind='all'))), sh(len(stays(v, 1)), len(stays(v, 1, kind='all')))))
    say('main against v31, ours long, another way: label shuffles with a gap at least as large:',
        perm2(aw(stays(m, 0)), len(stays(m, 0)), aw(stays(v, 0)), len(stays(v, 0))))
    both = stays(m, 0) + stays(v, 0)
    line38('both codes ours long', both)
    both = stays(m, 1) + stays(v, 1)
    line38('both codes theirs long', both)


def compare(games):
    say('')
    say('=' * 30, 'rows.jsonl, read last, to compare')
    rows = {}
    for line in Path('data/analysis/ladder/rows.jsonl').read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            rows[r['game']] = r
    n = 0
    diff = Counter()
    for g in games:
        r = rows.get(g['game'])
        if r is None:
            diff['game not in rows'] += 1
            continue
        n += 1
        if r['our_code'] != g['code'] and not (g['code'] == 'other' and r['our_code'] not in ('main', 'v31')):
            diff['code'] += 1
        if r['map_key'] != g['map_key']:
            diff['map_key'] += 1
        if r['last_round'] != g['last_round']:
            diff['last_round'] += 1
        if bool(r['win']) != bool(g['win']):
            diff['win'] += 1
        for s, side in ((0, 'us'), (1, 'them')):
            fr = r['final'][side]
            fg = g['final'][s]
            if (fr['queen_length'], fr['longest'], fr['total'], fr['alive']) != (fg['queen'], fg['longest'], fg['total'], fg['alive']):
                diff['final ' + side] += 1
            qd = g['qdeath'][s]
            qr = r['queen'][side]
            if (qr['death_round'], qr['death_length']) != ((qd['round'], qd['length']) if qd else (None, None)):
                diff['queen death ' + side] += 1
            if qd and qr['death_cause'] != REASON[qd['reason']]:
                diff['queen death cause ' + side + ' (%s vs %s)' % (qr['death_cause'], REASON[qd['reason']])] += 1
        if r.get('opponent_rating') != g.get('opponentElo'):
            diff['rating'] += 1
        if (r.get('time') or '')[:19] != (g.get('completedAt') or '')[:19]:
            diff['time'] += 1
    say('games compared', n, 'of', len(games), ' rows in file', len(rows), ' differences:', dict(diff))
    for code in ('main', 'v31'):
        kr = [r for r in rows.values() if r['our_code'] == code and r['last_round'] == 499 and r.get('ended_by') == 'queen rule'
              and r.get('queens_at_end') == 'only theirs']
        say('rows: %s full games ended by queen rule with only their queen alive: %d, lost %d' % (code, len(kr), sum(1 for r in kr if r['result'] == 'loss')))


def main():
    games, bad, maps = load()
    say('games read', len(games), 'errors', len(bad), [b.get('error') for b in bad][:5])
    say('final state equals the result block in', sum(1 for g in games if g['final_ok']), 'of', len(games),
        '; body tiles consistent in', sum(1 for g in games if g['own_ok']), '; anomalies', dict(sum((Counter(g['anomalies']) for g in games), Counter())),
        '; portals that cannot be followed', sum(g['bad_portals'] for g in games))
    say('codes', dict(Counter(g['code'] for g in games)), ' ranked', dict(Counter(str(g.get('ranked')) for g in games)))
    say('dead-end layouts in maps.json:', sorted(k for k, v in maps.items() if v['queen_spawn_dead_end']))
    f42(games)
    f38(games)
    compare(games)
    out = open(P + 'f42-f38-1212-numbers.txt', 'w')
    out.write('\n'.join(LINES) + '\n')
    out.close()


main()
