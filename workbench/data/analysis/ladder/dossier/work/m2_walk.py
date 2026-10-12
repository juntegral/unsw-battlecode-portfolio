"""Scratch (diag-med20): walk statistics from m2_scan-*.jsonl.
Usage: python3 data/analysis/ladder/dossier/work/m2_walk.py <sim|fid|tie|straight|line|mouth>"""
import sys, json
sys.dont_write_bytecode = True
from pathlib import Path
from collections import defaultdict, Counter

WORK = Path('data/analysis/ladder/dossier/work')
FILES = ('m2_scan-T3.jsonl', 'm2_scan-O.jsonl', 'm2_scan-T1-0.jsonl', 'm2_scan-T1-1.jsonl')
TOP = {454: 'aAah', 157: 'larp', 306: 'Cutlery', 70: 'chad', 91: 'SSS', 264: 'ftm', 842: 'horse'}
LAYS = ('Queen Of Spades', 'Maze', 'Default', 'Trauma')
SHORT = {'Queen Of Spades': 'QoS', 'Maze': 'Maze', 'Default': 'Default', 'Trauma': 'Trauma'}
ORDER = ('aAah', 'larp', 'Cutlery', 'chad', 'top opp', 'direct larp', 'direct Cutlery', 'B7Q direct', 'B7Q', 'B7', 'MAIN', 'ours all', 'live all', 'ladder opp',
         'Cutlery old', 'SSS old', 'ftm old', 'horse old', 'aAah old', 'old opp')
OURS = ('B7Q direct', 'B7Q', 'B7', 'MAIN')
TERMS = ('centre', 'room', 'terr', 'cramped', 'pearl', 'soon', 'hot', 'unseen', 'portal', 'far', 'eat', 'look', 'mate', 'pocket', 'sc', 'queen')
NAMES = 'NESW'
TIELAST = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[1] == 'tie' else 20


def tb(d, wt):
    return 0.0 if d < 0 else max(0.0, wt * (260 - 40 * d))


def parts(row, o, k):
    dest, room, terr, tailhit, dp, ds, dh, du, dpo, dk, eat, sc, pocket, look, mate, cd, pk, kr, dsa, dpa = o
    L, r = row['L'], row['r']
    cr = 0.0
    want = 3.0 * L + 8.0
    if room < want:
        cr += 400.0 * (want - room)
    if room < L + 2.0:
        cr += 5000.0 * (L + 2.0 - room)
    if not tailhit:
        cr += 600.0
    t = dict.fromkeys(TERMS, 0.0)
    t['room'] = 1.5 * room
    t['terr'] = 1.5 * terr
    t['cramped'] = -cr
    if row['isq']:
        q = 0.0
        if ((not tailhit) and room < want) or room < L + 8:
            q += 6000.0
        if kr > 0:
            q += 6000.0 + 400.0 * kr
        t['queen'] = -q
    cand = (('pearl', tb(dp, 2.0)), ('soon', tb(ds, 0.45)), ('hot', tb(dh, 1.2)), ('unseen', tb(du, 0.2)), ('portal', tb(dpo, 0.4)))
    name, val = max(cand, key=lambda kv: kv[1])
    if val > 0:
        t[name] = val
    far = [x for x in (dp, ds, dh, du) if x >= 0]
    if far:
        t['far'] = 2.0 * max(0, 80 - min(far))
    grown = L + eat
    full = pocket < 48 and grown > pocket // 2
    if full:
        t['pocket'] = -1000.0 * (grown - pocket // 2)
    if eat and not full:
        t['eat'] = 300.0
    if sc:
        t['sc'] = -300.0
    if mate:
        t['mate'] = -450.0
    t['look'] = look
    if pk == 1:
        t['portal'] -= 150.0
    t['tie'] = 0.25 * ((row['i'] * 31 + r * 17 + k * 7) % 5)
    return t


def scores(row):
    out, ps = [None] * 4, [None] * 4
    base = None
    blind = []
    for k, o in enumerate(row['o']):
        if o is None:
            continue
        if len(o) == 2:
            blind.append(k)
            continue
        t = parts(row, o, k)
        ps[k] = t
        out[k] = sum(t.values())
        if o[16] == 0:
            b = out[k] - t['tie'] - max(t['pearl'], t['soon'], t['hot'], t['unseen'], max(t['portal'], 0.0))
            if base is None or b > base:
                base = b
    for k in blind:
        if base is not None:
            out[k] = base + 88.0 + 0.25 * ((row['i'] * 31 + row['r'] * 17 + k * 7) % 5)
            ps[k] = dict(blind=out[k], tie=0.25 * ((row['i'] * 31 + row['r'] * 17 + k * 7) % 5))
    return out, ps


def best(sc):
    v = [(s, -k) for k, s in enumerate(sc) if s is not None]
    return -max(v)[1] if v else -1


def group(g, side):
    if g['src'] == 'T3':
        return TOP.get(g['team'], '?') if side == 0 else 'top opp'
    if g['src'] == 'T1':
        return (TOP.get(g['team'], '?') + ' old') if side == 0 else 'old opp'
    if g['label'].startswith('top-l'):
        return 'B7Q direct' if side == 0 else 'direct ' + TOP.get(g['oppid'], str(g['oppid']))
    return g['arm'] if side == 0 else 'ladder opp'


def load():
    games, turns, pearls = {}, defaultdict(list), defaultdict(list)
    for f in FILES:
        p = WORK / f
        if not p.exists():
            continue
        cur = None
        for line in p.read_text().splitlines():
            if not line:
                continue
            r = json.loads(line)
            if r['k'] == 'g':
                cur = (f, r['g'])
                games[cur] = r
            elif r['k'] == 't':
                turns[cur].append(r)
            else:
                pearls[cur].append(r)
    return games, turns, pearls


def mean(v):
    return sum(v) / len(v) if v else float('nan')


def pct(a, b):
    return '%3.0f%%' % (100.0 * a / b) if b else '  NA'


def sides(games):
    for key, g in games.items():
        for s in (0, 1):
            grp = group(g, s)
            yield key, g, s, grp
            if grp in OURS:
                yield key, g, s, 'ours all'
            if grp in ('B7Q', 'B7Q direct'):
                yield key, g, s, 'live all'


def sim(games, turns, prl):
    """walk forward of our non-queen dragons born by round 5."""
    acc = defaultdict(lambda: defaultdict(list))
    agree = Counter()
    for key, g in games.items():
        if not g.get('sim'):
            continue
        real = defaultdict(list)
        for p in prl.get(key, ()):
            if p['s'] == 0:
                real[p['i']].append(p['r'])
        rpath = defaultdict(str)
        for r in turns.get(key, ()):
            if r['s'] == 0 and r['r'] <= 20:
                rpath[r['i']] += '*' if r['act'] == 's' else (NAMES[r['dir']] if r['act'] == 'm' and r['dir'] >= 0 else '?')
        for i, sv in g['sim'].items():
            i = int(i)
            kind = 'starter' if sv['ro'] == 'o' else 'queen' if sv['ro'] == 'q' else 'child'
            for name in (g['arm'] + (' direct' if g['label'].startswith('top-l') else ''), 'ours all'):
                a = acc[(g['map'], name, kind)]
                a['real20'].append(sum(1 for x in real[i] if x <= 20))
                a['real40'].append(sum(1 for x in real[i] if x <= 40))
                for v, s in sv['v'].items():
                    a[v + '20'].append(sum(1 for x in s['eats'] if x <= 20))
                    a[v + '40'].append(len(s['eats']))
                    a[v + 'p10'].append(1 if any(x <= 10 for x in s['portal']) else 0)
                    a[v + 'p20'].append(1 if any(x <= 20 for x in s['portal']) else 0)
                    a[v + 'dead'].append(1 if s['dead'] >= 0 else 0)
                    a[v + 'short'].append(1 if (s['dead'] < 0 and s['last'] < 40) else 0)
            bp = sv['v']['base']['path'].upper()[:21]
            rp = rpath[i][:21]
            n = min(len(bp), len(rp))
            same = 0
            while same < n and bp[same] == rp[same]:
                same += 1
            agree[(g['map'], kind, 'n')] += 1
            agree[(g['map'], kind, 'same')] += same
            agree[(g['map'], kind, 'len')] += n
    vs = ('base', 'head', 'head3', 'headblind', 'head20')
    print('Walk forward of our non-queen dragons born by round 5 (virtual dragon in the replay world; its children are not walked). Pearls eaten by the dragon itself.')
    for kind in ('starter', 'child', 'queen'):
        print('==', kind)
        tot = defaultdict(lambda: defaultdict(list))
        for lay in LAYS:
            for name in ('ours all', 'B7Q direct', 'B7Q', 'B7', 'MAIN'):
                a = acc.get((lay, name, kind))
                if not a:
                    continue
                n = len(a['real20'])
                print('%-8s %-11s walkers %3d | real r20 %.2f r40 %.2f | ' % (SHORT[lay], name, n, mean(a['real20']), mean(a['real40']))
                      + ' | '.join('%s r20 %.2f r40 %.2f portal r10 %s r20 %s dead %s cut %s' % (v, mean(a[v + '20']), mean(a[v + '40']), pct(sum(a[v + 'p10']), n), pct(sum(a[v + 'p20']), n),
                                                                                       pct(sum(a[v + 'dead']), n), pct(sum(a[v + 'short']), n)) for v in vs))
        for lay in LAYS:
            print('   base path equals the real path for the first %.1f of %.1f turns (%s, %d walkers)' % (
                agree[(lay, kind, 'same')] / max(1, agree[(lay, kind, 'n')]), agree[(lay, kind, 'len')] / max(1, agree[(lay, kind, 'n')]), SHORT[lay], agree[(lay, kind, 'n')]))
    print('== per game (sum over its walkers), mean of the four layouts, ours all')
    per = defaultdict(lambda: defaultdict(float))
    ng = Counter()
    for key, g in games.items():
        if not g.get('sim'):
            continue
        ng[g['map']] += 1
        real = defaultdict(list)
        for p in prl.get(key, ()):
            if p['s'] == 0:
                real[p['i']].append(p['r'])
        for i, sv in g['sim'].items():
            if sv['ro'] == 'q':
                for v, s in sv['v'].items():
                    per[g['map']]['Q' + v + '20'] += sum(1 for x in s['eats'] if x <= 20)
                per[g['map']]['Qreal20'] += sum(1 for x in real[int(i)] if x <= 20)
                continue
            per[g['map']]['real20'] += sum(1 for x in real[int(i)] if x <= 20)
            per[g['map']]['real40'] += sum(1 for x in real[int(i)] if x <= 40)
            for v, s in sv['v'].items():
                per[g['map']][v + '20'] += sum(1 for x in s['eats'] if x <= 20)
                per[g['map']][v + '40'] += len(s['eats'])
    for lay in LAYS:
        if ng[lay]:
            print('%-8s games %2d | real r20 %.2f r40 %.2f | ' % (SHORT[lay], ng[lay], per[lay]['real20'] / ng[lay], per[lay]['real40'] / ng[lay])
                  + ' | '.join('%s r20 %.2f r40 %.2f' % (v, per[lay][v + '20'] / ng[lay], per[lay][v + '40'] / ng[lay]) for v in vs))
    for lay in LAYS:
        if ng[lay]:
            print('%-8s the queen walker alone, pearls by r20: real %.2f | ' % (SHORT[lay], per[lay]['Qreal20'] / ng[lay]) + ' | '.join('%s %.2f' % (v, per[lay]['Q' + v + '20'] / ng[lay]) for v in vs))
    print('mean     | real r20 %.2f r40 %.2f | ' % (mean([per[l]['real20'] / ng[l] for l in LAYS if ng[l]]), mean([per[l]['real40'] / ng[l] for l in LAYS if ng[l]]))
          + ' | '.join('%s r20 %.2f r40 %.2f' % (v, mean([per[l][v + '20'] / ng[l] for l in LAYS if ng[l]]), mean([per[l][v + '40'] / ng[l] for l in LAYS if ng[l]])) for v in vs))


def tie(games, turns):
    """first order: turns of ours the heading tie-break would change; rebuild fidelity."""
    c = defaultdict(Counter)
    for key, g in games.items():
        if g['team'] != 1119:
            continue
        arm = g['arm'] + (' direct' if g['label'].startswith('top-l') else '')
        for name in (arm, 'ours all'):
            c[(g['map'], name)]['games'] += 1
            c[('all', name)]['games'] += 1
        for r in turns.get(key, ()):
            if r['s'] != 0 or 'o' not in r or r['act'] != 'm' or r['dir'] < 0 or r['r'] > TIELAST:
                continue
            sc, ps = scores(r)
            n = sum(1 for x in sc if x is not None)
            if n < 2:
                continue
            b = best(sc)
            for name in (arm, 'ours all'):
                for lay in (g['map'], 'all'):
                    a = c[(lay, name)]
                    a['turns'] += 1
                    a['fit'] += int(b == r['dir'])
                    if r['ro'] == 'q' or r['L'] > 4:
                        continue
                    a['short'] += 1
                    a['short fit'] += int(b == r['dir'])
                    blind = r['np'] == 0
                    a['blind'] += int(blind)
                    fc = r['fc']
                    if fc < 0 or sc[fc] is None:
                        continue
                    a['straight on offer'] += 1
                    a['played straight'] += int(r['dir'] == fc)
                    if blind:
                        a['blind straight on offer'] += 1
                        a['blind played straight'] += int(r['dir'] == fc)
                    raw = [None if x is None else x - ps[k]['tie'] for k, x in enumerate(sc)]
                    top = max(x for x in raw if x is not None)
                    gap = top - raw[fc]
                    a['straight within 1.0 of best'] += int(gap < 1.0)
                    if gap < 1.0 and b != fc:
                        a['noise picks a turn'] += 1
                        a['noise picks a turn, played'] += int(r['dir'] == b)
                    sc2 = list(sc)
                    sc2[fc] += 1.5
                    b2 = best(sc2)
                    if b2 != b:
                        a['changed'] += 1
                        a['changed blind'] += int(blind)
                        a['changed real'] += int(r['dir'] == b)
                        a['changed r0-10'] += int(r['r'] <= 10)
                        a['changed ' + r['ro']] += 1
    print('Rounds 0-20, move turns of ours with 2+ steps on offer. short = not the queen and length 4 or less (the dragons the card touches).')
    for lay in LAYS + ('all',):
        print('==', SHORT.get(lay, lay))
        for name in ('ours all', 'B7Q direct', 'B7Q', 'B7', 'MAIN'):
            a = c.get((lay, name))
            if not a or not a['turns']:
                continue
            n = a['games']
            print('%-11s games %2d | turns %4d rebuilt = played %s | short %4d (%s fit; blind %s) | straight on offer %4d played straight %s (blind: %s of %d) | straight within 1 point of the best %4d (%.1f a game), noise picks a turn %4d (%.1f a game; played so %s) | +1.5 changes %4d = %.1f a game (%s of short turns; blind %s; rebuilt step was the played one %s; r0-10 %d; starter %d child %d)'
                  % (name, n, a['turns'], pct(a['fit'], a['turns']), a['short'], pct(a['short fit'], a['short']), pct(a['blind'], a['short']), a['straight on offer'],
                     pct(a['played straight'], a['straight on offer']), pct(a['blind played straight'], a['blind straight on offer']), a['blind straight on offer'],
                     a['straight within 1.0 of best'], a['straight within 1.0 of best'] / n, a['noise picks a turn'], a['noise picks a turn'] / n,
                     pct(a['noise picks a turn, played'], a['noise picks a turn']), a['changed'], a['changed'] / n, pct(a['changed'], a['short']),
                     pct(a['changed blind'], a['changed']), pct(a['changed real'], a['changed']), a['changed r0-10'], a['changed o'], a['changed c']))


def straight(games, turns, r0, r1):
    c = defaultdict(Counter)
    ng = Counter()
    for key, g, s, grp in sides(games):
        if g['src'] == 'T1' and r1 > 20:
            continue
        ng[(g['map'], grp)] += 1
        ng[('all', grp)] += 1
        for r in turns.get(key, ()):
            if r['s'] != s or r['act'] != 'm' or r['dir'] < 0 or r['fc'] < 0 or r['L'] > 4 or not r0 <= r['r'] <= r1:
                continue
            blind = r['np'] == 0 and r['nso'] == 0
            for lay in (g['map'], 'all'):
                for ro in (r['ro'], 'any', 'nq' if r['ro'] != 'q' else 'q2'):
                    a = c[(lay, grp, ro)]
                    a['moves'] += 1
                    a['straight'] += int(r['dir'] == r['fc'])
                    if blind:
                        a['blind'] += 1
                        a['blind straight'] += int(r['dir'] == r['fc'])
                        a['blind back'] += int(r['dir'] == (r['fc'] ^ 2))
                        a['blind unseen'] += int(r['du2'] >= 0 and r['du2'] < r['du'])
                        a['blind tunseen'] += int(r['dut2'] >= 0 and r['dut2'] < r['dut'])
                        a['blind spawn'] += int(r['dsp2'] >= 0 and r['dsp2'] < r['dsp'])
                        a['blind mouth'] += int(r['dma2'] >= 0 and r['dma2'] < r['dma'])
                        a['blind mate'] += int(r['dmh2'] >= 0 and r['dmh'] >= 0 and r['dmh2'] > r['dmh'])
                        a['blind fresh'] += r['fresh']
                        a['blind tnew'] += r['tnew']
                        if r['nmo'] > 0 and r['dmo'] >= 0:
                            a['mouth seen'] += 1
                            a['mouth seen nearer'] += int(r['dma2'] >= 0 and r['dma2'] < r['dma'])
                            if r['dmo'] <= 6:
                                a['mouth6'] += 1
                                a['mouth6 nearer'] += int(r['dma2'] >= 0 and r['dma2'] < r['dma'])
                            if r['dmo'] == 0:
                                a['on mouth'] += 1
                                a['on mouth through'] += int(r['ps'] > 0)
                    if r['ps'] > 0:
                        a['through'] += 1
    print('Rounds %d-%d, move turns of dragons of length 4 or less. blind = no pearl and no tile about to spawn (8 rounds) in the 7 by 7.' % (r0, r1))
    print('columns: games | blind turns a game | straight ahead | ends nearer: own unseen, team unseen, a spawn tile, a portal mouth | farther from the nearest mate | new tiles (own / team) a blind turn | blind with a mouth in view within 6 steps: turns a game, ends nearer | blind on a mouth tile: turns a game, through | portal steps a game (any turn)')
    for lay in LAYS + ('all',):
        for ro in ('nq', 'q2'):
            print('==', SHORT.get(lay, lay), 'not the queen' if ro == 'nq' else 'the queen')
            for grp in ORDER:
                a = c.get((lay, grp, ro))
                if not a or not a['blind']:
                    continue
                b = a['blind']
                n = ng[(lay, grp)]
                print('%-15s %3d | %5.1f | %s | %s %s %s %s | %s | %4.1f / %4.1f | %4.1f %s | %4.2f %s | %4.2f' % (
                    grp, n, b / n, pct(a['blind straight'], b), pct(a['blind unseen'], b), pct(a['blind tunseen'], b), pct(a['blind spawn'], b), pct(a['blind mouth'], b),
                    pct(a['blind mate'], b), a['blind fresh'] / b, a['blind tnew'] / b, a['mouth6'] / n, pct(a['mouth6 nearer'], a['mouth6']), a['on mouth'] / n, pct(a['on mouth through'], a['on mouth']), a['through'] / n))


def mouth(games, turns):
    """ours on a portal mouth tile, rounds 0-40: what the rebuilt score offers."""
    c = defaultdict(Counter)
    for key, g in games.items():
        if g['team'] != 1119:
            continue
        w = g['w']
        pairs = set(g['mouths'])
        for r in turns.get(key, ()):
            if r['s'] != 0 or 'o' not in r or r['act'] != 'm' or r['dmo'] != 0 or r['L'] > 6:
                continue
            who = 'queen' if r['ro'] == 'q' else 'other'
            win = '0-20' if r['r'] <= 20 else '21-40'
            sc, ps = scores(r)
            kinds = []
            for k, o in enumerate(r['o']):
                if o is None:
                    continue
                if len(o) == 2:
                    kinds.append(('blind', k))
                elif o[16] == 1:
                    kinds.append(('known', k))
            for a in (c[(who, win)], c[(who, 'all')]):
                a['turns'] += 1
                a['pearl in view'] += int(r['np'] > 0)
                a['through'] += int(r['ps'] > 0)
                if not kinds:
                    a['no portal step on offer'] += 1
                    continue
                kd = 'blind' if any(x[0] == 'blind' for x in kinds) else 'known'
                a[kd + ' on offer'] += 1
                a[kd + ' taken'] += int(r['ps'] > 0)
                if r['ps'] == 0:
                    top = max(x for x in sc if x is not None)
                    pk = max(sc[k] for _, k in kinds)
                    gap = top - pk
                    a[kd + ' refused'] += 1
                    a[kd + ' refused gap'] += gap
                    a[kd + ' refused, pearl in view'] += int(r['np'] > 0)
    print('Ours on a portal mouth tile (length 6 or less), move turns. blind = the far side is unknown to this dragon, known = it has seen the far side.')
    for who in ('other', 'queen'):
        for win in ('0-20', '21-40', 'all'):
            a = c.get((who, win))
            if not a:
                continue
            print('%-6s r%-5s turns %4d (pearl in view %s) through %s | no portal step on offer %4d | unknown far side on offer %4d taken %s (refused %d, mean gap %.0f, pearl in view %d) | known far side on offer %4d taken %s (refused %d, mean gap %.0f, pearl in view %d)'
                  % (who, win, a['turns'], pct(a['pearl in view'], a['turns']), pct(a['through'], a['turns']), a['no portal step on offer'], a['blind on offer'], pct(a['blind taken'], a['blind on offer']),
                     a['blind refused'], a['blind refused gap'] / max(1, a['blind refused']), a['blind refused, pearl in view'],
                     a['known on offer'], pct(a['known taken'], a['known on offer']), a['known refused'], a['known refused gap'] / max(1, a['known refused']), a['known refused, pearl in view']))


def field(games, turns):
    """heads standing where pearls are born: dragons within 2 path steps of a spawn tile, and spawn tiles in view, by round."""
    acc = defaultdict(lambda: defaultdict(list))
    for key, g, s, grp in sides(games):
        if g['rounds'] < 200:
            continue
        per = defaultdict(lambda: [0, 0, 0, 0, 0])
        for r in turns.get(key, ()):
            if r['s'] != s:
                continue
            v = per[r['r']]
            v[0] += 1
            v[1] += int(0 <= r['dsp'] <= 2)
            v[2] += r['nsp']
            v[3] += int(r['np'] > 0)
            v[4] += int(0 <= r['dsn'] <= 3)
        a = acc[(g['map'], grp)]
        for R in (5, 10, 15, 20, 30, 40):
            if R in per:
                v = per[R]
                a[('n', R)].append(v[0])
                a[('near', R)].append(v[1])
                a[('nsp', R)].append(v[2] / v[0])
                a[('pv', R)].append(v[3])
                a[('soon', R)].append(v[4])
    print('Games of 200+ rounds. Per round: dragons | of them within 2 path steps of a spawn tile | within 3 steps of a tile that spawns in the next 10 rounds | with a pearl in view | spawn tiles in view per dragon')
    for lay in LAYS:
        print('==', SHORT[lay])
        for grp in ORDER:
            a = acc.get((lay, grp))
            if not a or not a[('n', 20)]:
                continue
            print('%-15s n=%3d | ' % (grp, len(a[('n', 5)])) + ' | '.join('r%d: %.1f %.1f %.1f %.1f %4.1f' % (R, mean(a[('n', R)]), mean(a[('near', R)]), mean(a[('soon', R)]), mean(a[('pv', R)]), mean(a[('nsp', R)])) for R in (5, 10, 15, 20, 30, 40) if a[('n', R)]))


def line(games, prl):
    acc = defaultdict(lambda: defaultdict(list))
    for key, g, s, grp in sides(games):
        qroot = [int(i) for i, v in g['starters'].items() if v[0] == 'q' and v[1] == s]
        row = Counter()
        for p in prl.get(key, ()):
            if p['s'] != s:
                continue
            ln = 'q' if p['root'] in qroot else 'o'
            for R in (10, 20, 30, 40):
                if p['r'] <= R:
                    row[(ln, R)] += 1
                    row[('portal' if p['pc'] > 0 else 'plain', R)] += 1
        a = acc[(g['map'], grp)]
        for ln in ('q', 'o', 'portal', 'plain'):
            for R in (10, 20, 30, 40):
                a[(ln, R)].append(row[(ln, R)])
    print('Pearls eaten a game by the line of the queen (she and her descendants) and by the lines of the other starters; then by dragons whose line had stepped through a portal, and the rest')
    for lay in LAYS:
        print('==', SHORT[lay])
        for grp in ORDER:
            a = acc.get((lay, grp))
            if not a:
                continue
            print('%-15s n=%3d | queen line r10 %4.2f r20 %5.2f r30 %5.2f r40 %5.2f | other lines r10 %4.2f r20 %5.2f r30 %5.2f r40 %5.2f | portal lines r20 %5.2f r40 %5.2f | no portal r20 %5.2f r40 %5.2f' % (
                grp, len(a[('q', 20)]), mean(a[('q', 10)]), mean(a[('q', 20)]), mean(a[('q', 30)]), mean(a[('q', 40)]), mean(a[('o', 10)]), mean(a[('o', 20)]), mean(a[('o', 30)]), mean(a[('o', 40)]),
                mean(a[('portal', 20)]), mean(a[('portal', 40)]), mean(a[('plain', 20)]), mean(a[('plain', 40)])))
    print('== mean of the four layouts')
    for grp in ORDER:
        if not all(acc.get((lay, grp)) for lay in LAYS):
            continue
        m = lambda k: mean([mean(acc[(lay, grp)][k]) for lay in LAYS])
        print('%-15s | queen line r20 %5.2f r40 %5.2f | other lines r20 %5.2f r40 %5.2f | portal lines r20 %5.2f r40 %5.2f | no portal r20 %5.2f r40 %5.2f' % (
            grp, m(('q', 20)), m(('q', 40)), m(('o', 20)), m(('o', 40)), m(('portal', 20)), m(('portal', 40)), m(('plain', 20)), m(('plain', 40))))


def main():
    mode = sys.argv[1]
    games, turns, prl = load()
    if mode == 'sim':
        sim(games, turns, prl)
    elif mode == 'tie':
        tie(games, turns)
    elif mode == 'straight':
        straight(games, turns, int(sys.argv[2]) if len(sys.argv) > 2 else 0, int(sys.argv[3]) if len(sys.argv) > 3 else 20)
    elif mode == 'mouth':
        mouth(games, turns)
    elif mode == 'field':
        field(games, turns)
    elif mode == 'line':
        line(games, prl)


main()
