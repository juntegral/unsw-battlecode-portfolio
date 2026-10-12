"""Scratch (diag-queenkill): tables from qk_scanf-*.jsonl (falls back to qk_scan-*.jsonl).
Usage: python3 qk_agg.py <group>=<tag,tag> ...   e.g. online=m1,sr51 ladder=L0,L1,L2 top1=T0,T1,T2"""
import sys, json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median, mean

W = 'data/analysis/ladder/dossier/work/'


def load(tags):
    games = []
    for tag in tags:
        p = Path(W + 'qk_scanf-' + tag + '.jsonl')
        if not p.exists():
            p = Path(W + 'qk_scan-' + tag + '.jsonl')
        for line in p.read_text().splitlines():
            if line.strip():
                games.append(json.loads(line))
    return games


def fate(q):
    if q is None:
        return 'alive'
    c = q['cause']
    if c == 'rammed':
        return 'rammed by enemy' if q['enemy'] else 'rammed by own'
    if c == 'she rammed':
        return 'she rammed enemy head' if q['enemy'] else 'she rammed own head'
    if c == 'another body':
        return 'enemy body' if q.get('enemy') == 1 else 'own team body' if q.get('enemy') == 0 else 'a body'
    return c


def when(q):
    return 'alive' if q is None else 'r<=100' if q['r'] <= 100 else 'r101-300' if q['r'] <= 300 else 'r>300'


def by_enemy(q):
    return q is not None and fate(q) in ('rammed by enemy', 'she rammed enemy head', 'enemy body')


def share(n, d):
    return '%d/%d=%.2f' % (n, d, n / d) if d else '0/0'


def dist(values, cuts):
    c = Counter()
    for v in values:
        for name, lo, hi in cuts:
            if lo <= v <= hi:
                c[name] += 1
                break
    n = len(values)
    return ' '.join('%s:%d(%.2f)' % (name, c[name], c[name] / n if n else 0) for name, _, _ in cuts)


LC = (('2', 2, 2), ('3', 3, 3), ('4', 4, 4), ('5-8', 5, 8), ('9+', 9, 999))
KC = (('1', 1, 1), ('2', 2, 2), ('3', 3, 3), ('4+', 4, 99))
PC = (('0', 0, 0), ('1', 1, 1), ('2', 2, 2), ('3+', 3, 99))


def first_dead(g):
    """0 or 1 = side whose queen died first, None if neither died."""
    a, b = g['qd']
    if a is None and b is None:
        return None
    if a is None:
        return 1
    if b is None:
        return 0
    if a['r'] != b['r']:
        return 0 if a['r'] < b['r'] else 1
    return 0 if a['oq'] > 0 else 1


def section_fate(name, games):
    print('\n==== FATE', name, 'games', len(games), 'wins(side0)', sum(1 for g in games if g['win'] == 1), 'draw', sum(1 for g in games if g['win'] is None))
    print('decided:', dict(Counter((g['decided'], g['win']) for g in games)))
    for s, label in ((0, 'side0 queen (ours / rank-1)'), (1, 'side1 queen (opponent)')):
        qs = [g['qd'][s] for g in games]
        n = len(qs)
        print(' ', label, '| when:', ' '.join('%s %d (%.2f)' % (k, v, v / n) for k, v in sorted(Counter(when(q) for q in qs).items())))
        fc = Counter(fate(q) for q in qs)
        print('     cause:', ' | '.join('%s %d (%.2f)' % (k, v, v / n) for k, v in fc.most_common()))
        for w_ in ('r<=100', 'r101-300', 'r>300'):
            sub = Counter(fate(q) for q in qs if when(q) == w_)
            print('       ', w_, dict(sub.most_common()))
        rams = [q for q in qs if q is not None and q['cause'] == 'rammed' and q['enemy']]
        if rams:
            m = len(rams)
            print('     KILLER (enemy ram) n', m, '| killer L at turn start:', dist([q['kL0'] for q in rams], LC), '| mean %.2f median %s' % (mean(q['kL0'] for q in rams), median(q['kL0'] for q in rams)))
            print('        steps walked:', dist([q['k'] for q in rams], KC), '| segments paid before the hit:', dist([q['paid'] for q in rams], PC), '| ate on the way', sum(1 for q in rams if q['ate'] > 0))
            print('        killer is the enemy queen', sum(q['kq'] for q in rams), '| killer is its side longest and 5+', sum(1 for q in rams if q['ktop'] and q['kL0'] >= 5),
                  '| killer in her 7x7 at her last turn start', share(sum(1 for q in rams if q['seen'] >= 0), m),
                  '| walk d at killer turn start:', dist([q['d'] for q in rams], (('none', -1, -1), ('1', 1, 1), ('2', 2, 2), ('3', 3, 3), ('4+', 4, 99))))
            print('        her length:', dist([q['L'] for q in rams], LC), '| none of her side within 5:', share(sum(1 for q in rams if q['own5'] == 0), m),
                  '| mean enemy heads within 5: %.2f' % mean(q['foe5'] for q in rams), '| killer length lost mean %.2f, her length mean %.2f' % (mean(q['kLd'] for q in rams), mean(q['L'] for q in rams)))
            print('        by round:', dist([q['r'] for q in rams], (('<=100', 0, 100), ('101-300', 101, 300), ('>300', 301, 999))))
        boxed = [q for q in qs if q is not None and q['cause'] in ('wall', 'own body', 'another body')]
        if boxed:
            print('     wall/body deaths n', len(boxed), '| no free tile at her last turn start', sum(1 for q in boxed if q['qfree'] == 0), '| enemy head in her view', sum(1 for q in boxed if q['seenfoes'] > 0))
    # who dies first and who wins
    fd = Counter()
    for g in games:
        f = first_dead(g)
        if f is None:
            fd[('none', g['win'])] += 1
            continue
        q = g['qd'][f]
        fd[('side%d queen first' % f, 'by enemy' if by_enemy(q) else 'self', g['win'])] += 1
    print('  FIRST DEATH (side, how, side0 win):')
    for k in sorted(fd, key=str):
        print('     ', k, fd[k])
    for s in (0, 1):
        ks = [g for g in games if first_dead(g) == 1 - s and by_enemy(g['qd'][1 - s])]
        wins = sum(1 for g in ks if g['win'] == (1 if s == 0 else 0))
        print('  side%d kills the other queen first: %d of %d games; then wins %s' % (s, len(ks), len(games), share(wins, len(ks))))
        ks2 = [g for g in games if first_dead(g) == 1 - s]
        wins2 = sum(1 for g in ks2 if g['win'] == (1 if s == 0 else 0))
        print('  side%d queen outlives the other (any cause): %s' % (s, share(wins2, len(ks2))))
    # worth
    for s in (0, 1):
        o = 1 - s
        ks = [g for g in games if g['qd'][o] is not None and g['qd'][o]['cause'] == 'rammed' and g['qd'][o]['enemy']]
        al = [g for g in ks if g['qd'][o]['oq'] > 0]
        de = [g for g in ks if g['qd'][o]['oq'] == 0]
        won = lambda gs: sum(1 for g in gs if g['win'] == (1 if s == 0 else 0))
        print('  WORTH side%d rams the other queen dead: %d games | own queen alive then: won %s | own queen dead then: won %s' % (s, len(ks), share(won(al), len(al)), share(won(de), len(de))))
        if al:
            still = [g for g in al if g['final'][3 if s == 0 else 7] > 0]
            print('      own queen alive then and still alive at the end: won %s | killer length mean %.2f (turn start), her length mean %.2f' % (
                share(won(still), len(still)), mean(g['qd'][o]['kL0'] for g in al), mean(g['qd'][o]['L'] for g in al)))
        nk = [g for g in games if g not in ks]
        print('      games without such a kill: won %s' % share(won(nk), len(nk)))
    em = Counter()
    for g in games:
        em[(g['final'][3] > 0, g['final'][7] > 0, g['win'])] += 1
    print('  END STATE (side0 queen alive, side1 queen alive, side0 win):', dict(sorted(em.items(), key=str)))


def mclass(r):
    return 'queen' if r[4] else 'short' if r[3] <= 4 else 'mid' if r[3] <= 8 else 'long'


def reach(r):
    if r[16] > 0:
        return 'pearl'
    paid = max(0, r[6] - r[7])
    return 'free' if paid == 0 else '1 paid' if paid == 1 else '2 paid' if paid == 2 else '3+ paid'


def instead(r):
    if r[18]:
        return 'taken'
    if r[23] == 3:
        return 'rammed another head'
    if r[23] >= 0:
        return 'died (wall/body/other)'
    if r[22]:
        return 'split'
    if r[20] < 0:
        return 'she died otherwise'
    if r[19] == 0:
        return 'no move'
    return 'moved away' if r[20] > r[17] else 'moved closer' if r[20] < r[17] else 'moved level'


def predict(r, cells):
    """Reading of sr51-bot/main.cpp for a non-queen: 1 hunt says yes, 2 trade says yes, 0 neither."""
    rnd, L = r[0], r[3]
    if L > 4:
        return 0
    lead = r[5] and rnd > (150 if cells > 1200 else 300)
    if lead:
        return 0
    plainreach = r[16] == 0
    if not plainreach:
        return 0
    revenge = r[14] == 0 and rnd >= 100
    other = 0 <= r[31] <= 20 if len(r) > 31 else False
    if rnd > 20 and (revenge or not other):
        return 1
    aggressive = cells <= 1200
    ok = rnd <= 300 and (aggressive or r[12] >= 8) and r[10] + 1 - r[11] >= 1
    worth = r[9] >= L if aggressive else r[9] >= max(5, L + 2)
    if ok and worth and r[6] <= (3 if aggressive else 4):
        return 2
    return 0


def section_chance(name, games):
    n = len(games)
    print('\n==== CHANCES', name, 'games', n)
    for s, label in ((0, 'side0 at the opponent queen'), (1, 'opponent at side0 queen')):
        rows = [(g, r) for g in games for r in g['chs'] if r[1] == s]
        print(' ', label, 'chance turns', len(rows), '(%.2f a game)' % (len(rows) / n), 'games with one', len({g['game'] for g, r in rows}))
        tab = defaultdict(Counter)
        for g, r in rows:
            tab[(mclass(r), reach(r), 'in view' if r[9] > 0 else 'not in view')][instead(r)] += 1
        for k in sorted(tab):
            c = tab[k]
            tot = sum(c.values())
            print('     %-34s n %4d taken %s | %s' % (' / '.join(k), tot, share(c['taken'], tot), ', '.join('%s %d' % kv for kv in c.most_common() if kv[0] != 'taken')))
        core = [(g, r) for g, r in rows if mclass(r) == 'short' and r[16] == 0 and r[9] > 0]
        print('     CORE (non-queen, L<=4, plain reach, her head in view): turns', len(core), '(%.3f a game)' % (len(core) / n), 'taken', share(sum(r[18] for g, r in core), len(core)),
              '| games', len({g['game'] for g, r in core}))
        for key, f in (('mover L', lambda r: r[3]), ('steps d', lambda r: r[6]), ('reach', reach), ('her length', lambda r: min(r[8], 5)),
                       ('own queen alive', lambda r: int(r[14] > 0)), ('round', lambda r: '<=20' if r[0] <= 20 else '<=100' if r[0] <= 100 else '<=300' if r[0] <= 300 else '>300'),
                       ('outnumbered in view', lambda r: int(r[10] + 1 - r[11] < 1)), ('she can hit back', lambda r: r[15]),
                       ('another short saw her <=20r', lambda r: int(0 <= r[31] <= 20) if len(r) > 31 else -1),
                       ('saw her last turn too', lambda r: int(r[32] == 1) if len(r) > 32 else -1)):
            c, t = Counter(), Counter()
            for g, r in core:
                c[f(r)] += 1
                t[f(r)] += r[18]
            print('        by %-28s' % key, ' '.join('%s: %d/%d' % (k, t[k], c[k]) for k in sorted(c, key=str)))
        c, t = Counter(), Counter()
        for g, r in rows:
            if r[4]:
                continue
            p = predict(r, g['cells']) if (r[9] > 0) else 0
            c[p] += 1
            t[p] += r[18]
        print('     code reading, non-queen movers (0 says no, 1 hunt yes, 2 trade yes): taken/turns', ' '.join('%s: %d/%d' % (k, t[k], c[k]) for k in sorted(c)))
        ic = Counter(instead(r) for g, r in core if not r[18])
        print('     CORE refused, what it did instead:', dict(ic.most_common()))
        after = Counter()
        for g, r in core:
            if r[18]:
                continue
            q = g['qd'][1 - s]
            if q is None:
                after['she lives to the end'] += 1
            elif q['r'] - r[0] <= 5:
                after['she dies within 5 rounds: ' + fate(q)] += 1
            else:
                after['she dies later'] += 1
        print('     CORE refused, her fate:', dict(after.most_common()))
        after = Counter()
        for g, r in core:
            if not r[18]:
                after['mover dead within 5 rounds' if r[25] >= 0 else 'mover alive 5 rounds on'] += 1
        print('     CORE refused, the mover:', dict(after))
        # the switch: refused turns by cap
        for cap in (4, 6, 8, 99):
            sel = [(g, r) for g, r in rows if not r[4] and r[3] <= cap and r[16] == 0 and r[9] > 0
                   and not (r[5] and r[3] >= 5) and not r[18]]
            gs = {}
            for g, r in sel:
                gs.setdefault(g['game'], g)
            lost = [g for g in gs.values() if g['win'] == (0 if s == 0 else 1)]
            lostq = [g for g in lost if g['qd'][1 - s] is None]
            flip = []
            for g in lostq:
                f = g['final']
                own_q, own_big = (f[3], f[1]) if s == 0 else (f[7], f[5])
                if g['decided'] == 'queen' and own_q > 0:
                    flip.append(g['game'])
                elif g['decided'] == 'queen':
                    flip.append(-g['game'])
            print('     SWITCH cap L<=%d (non-queen, not a longest of 5+): refused turns %d, games %d, lost %d, lost with her alive at the end %d, of those decided on queen length %d %s' % (
                cap, len(sel), len(gs), len(lost), len(lostq), len(flip), flip[:12]))


def section_funnel(name, games):
    if not games or 'fun' not in games[0]:
        return
    n = len(games)
    print('\n==== FUNNEL', name, '(non-queen movers with the enemy queen head in their 7x7 at turn start)')
    for s, label in ((0, 'side0 looking at the opponent queen'), (1, 'opponent looking at side0 queen')):
        c = Counter()
        for g in games:
            for a in g['fun']:
                if a[0] == s:
                    c[('short' if a[1] <= 4 else 'long', a[2], a[5])] += a[6]
                    c[('short' if a[1] <= 4 else 'long', a[2], 'all')] += a[6]
        seen = [g['first_seen'][s] for g in games if g['first_seen'][s] >= 0]
        print(' ', label, '| games in which she is ever seen', share(len(seen), n), '| first seen round median', median(seen) if seen else None,
              '| sighting turns a game %.1f' % (sum(g['seen_n'][s] for g in games) / n))
        for cl in ('short', 'long'):
            for db, text in (('R', 'in sprint reach'), ('N', 'walk 1-3, out of reach'), ('M', 'walk 4-6'), ('F', 'walk 7+ or no way')):
                tot = c[(cl, db, 'all')]
                if not tot:
                    continue
                print('     %-5s %-24s turns %6d (%.2f a game) | rammed her %.3f closer %.2f level %.2f farther %.2f died %.3f she died otherwise %.3f' % (
                    cl, text, tot, tot / n, c[(cl, db, 'T')] / tot, c[(cl, db, 'C')] / tot, c[(cl, db, 'S')] / tot, c[(cl, db, 'F')] / tot, c[(cl, db, 'D')] / tot, c[(cl, db, 'X')] / tot))
        lat = []
        for g in games:
            q = g['qd'][1 - s]
            if q is not None and q['cause'] == 'rammed' and q['enemy'] and g['first_seen'][s] >= 0:
                lat.append(q['r'] - g['first_seen'][s])
        if lat:
            print('     rounds from first sighting to the ram that kills her: median', median(lat), 'mean %.1f' % mean(lat), 'n', len(lat))


def flip_class(g, s):
    """For the side s that refused: would her death have changed rule 1 on the final board?"""
    f = g['final']
    own_q, own_big, her, their_big = (f[3], f[1], f[7], f[5]) if s == 0 else (f[7], f[5], f[3], f[1])
    lost = g['win'] == (0 if s == 0 else 1)
    if not lost:
        return 'won anyway'
    if her == 0:
        return 'lost, she died anyway'
    if g['decided'] != 'queen':
        return 'lost on another rule'
    if own_q > 0 or own_big > their_big:
        return 'lost on queen length: SURE flip on the final board'
    if their_big == her:
        return 'lost on queen length: she is their longest, open'
    return 'lost on queen length: their longest still ahead'


def section_switch(name, games):
    print('\n==== SWITCH', name, '(non-queen mover, not its side longest when 5+, her head in view, free way of at most 3 steps inside sprint reach, no portal)')
    for s, label in ((0, 'side0 at the opponent queen'), (1, 'opponent at side0 queen')):
        for cap in (4, 6, 8):
            took = 0
            per = {}
            rows = []
            for g in games:
                for r in g['chs']:
                    if r[1] != s or r[4] or r[3] > cap or r[16] != 0 or r[9] == 0 or r[6] > 3 or (r[5] and r[3] >= 5) or r[17] > r[6]:
                        continue
                    if r[18]:
                        took += 1
                    else:
                        per.setdefault(g['game'], g)
                        rows.append((g, r))
            fc = Counter(flip_class(g, s) for g in per.values())
            print('  %s | L<=%d: taken %d, refused turns %d in %d games (own queen alive at the turn %d, dead %d; her length mean %.1f, mover mean %.1f) | %s' % (
                label, cap, took, len(rows), len(per), sum(1 for g, r in rows if r[14] > 0), sum(1 for g, r in rows if r[14] == 0),
                mean(r[8] for g, r in rows) if rows else 0, mean(r[3] for g, r in rows) if rows else 0, dict(fc.most_common())))
            if cap == 8:
                for g in per.values():
                    fcl = flip_class(g, s)
                    if 'queen length' in fcl:
                        rr = [r for gg, r in rows if gg is g]
                        print('       ', g['game'], g['map'], g['cells'], fcl, 'final', g['final'], 'turns (round, L, d, her L, own queen):', [(r[0], r[3], r[6], r[8], r[14]) for r in rr][:6])
        if s == 0:
            c = Counter()
            for g in games:
                for r in g['chs']:
                    if r[1] != 0 or r[4] or r[16] != 0 or r[9] == 0 or r[6] > 3 or r[18] or (r[5] and r[3] >= 5) or r[3] > 8 or r[17] > r[6]:
                        continue
                    lead = r[5] and r[0] > (150 if g['cells'] > 1200 else 300)
                    if r[3] <= 4:
                        why = ('believes it leads' if lead else 'round<=20' if r[0] <= 20 else
                               'our queen dead, round>=100: revenge should fire' if r[14] == 0 and r[0] >= 100 else
                               ('another short saw her within 20 rounds' if (len(r) > 31 and 0 <= r[31] <= 20) else 'no other short saw her') +
                               (', outnumbered in view' if r[10] + 1 - r[11] < 1 else ', not outnumbered') +
                               (', her parts under own length' if r[9] < r[3] else ''))
                        c[('L<=4', why)] += 1
                    else:
                        c[('L5-8', ('after round 300' if r[0] > 300 else 'round<=300') + (', her parts 10+' if r[9] >= 10 else ', her parts 6-9' if r[9] >= 6 else ', her parts <6'))] += 1
            print('  side0 refusals by the clause that fits (sr51-bot reading):')
            for k, v in sorted(c.items(), key=lambda kv: (kv[0][0], -kv[1])):
                print('      ', k, v)


def main():
    for arg in sys.argv[1:]:
        name, tags = arg.split('=')
        games = load(tags.split(','))
        section_fate(name, games)
        section_chance(name, games)
        section_funnel(name, games)
        section_switch(name, games)


main()
