# Scratch (diag-split): tables from sl_scan-*.jsonl (or sl_test.jsonl). Prints to stdout, writes nothing.
# Usage: python3 data/analysis/ladder/dossier/work/sl_agg.py <full|test> [section ...]
# Every rate is printed twice: pooled over games, and the mean of the 19 layouts weighted equally ("lay"),
# with the number of layouts on which rank-1 is higher.
import sys, json
from collections import defaultdict, Counter

D = 'data/analysis/ladder/dossier/work/'
MARKS = (50, 100, 150, 200, 250, 300, 350, 400, 450, 500)
B4 = ((0,), (1, 2), (3,), (4,), (5,))
B4N = ('0-100', '101-200', '201-300', '301-400', '401-500')
LBN = ('2', '3', '4', '5-7', '8+')
NBN = ('<32', '32-55', '56-59', '60-63', '64')
CLS = ('queen>200', 'longest,late', 'late,L>4', 'hard64', 'soft60-63', 'room0', 'room1-3', 'portal', 'headboxed', 'enemy<=3', 'open,L4', 'open,L5+')


def cls_of(k, big, late=None):
    bd, el, nk, role, rb, portal, enemy, free = k[:8]
    if late is None:
        late = bd >= 2 if big else bd >= 4
    if role == 0 and bd >= 3:
        return 'queen>200'
    if role == 1 and late:
        return 'longest,late'
    if late and el > 0:
        return 'late,L>4'
    if nk == 4:
        return 'hard64'
    if nk == 3:
        return 'soft60-63'
    if rb == 0:
        return 'room0'
    if rb == 1:
        return 'room1-3'
    if portal:
        return 'portal'
    if not free:
        return 'headboxed'
    if enemy:
        return 'enemy<=3'
    return 'open,L4' if el == 0 else 'open,L5+'


def flat(g):
    m = Counter()
    big = g['cells'] > 1200
    m['games'] = 1
    m['won'] = g['result'] == 'win'
    for z, bs in enumerate(B4):
        for b in bs:
            m['turns%d' % z] += g['turns'][0][b]
            m['oturns%d' % z] += g['turns'][1][b]
            for k in range(5):
                m['lt%d_%d' % (z, k)] += sum(g['lhist'][b][n] for n in range(17) if (0 if n == 2 else 1 if n == 3 else 2 if n == 4 else 3 if n <= 7 else 4) == k and n >= 2)
                m['eatl%d_%d' % (z, k)] += g['eatl'][b][k]
                m['rnb%d_%d' % (z, k)] += g['rounds_nb'][b][k]
                m['nbt%d_%d' % (z, k)] += g['nbt'][b][k]
            m['len%d' % z] += sum(n * g['lhist'][b][n] for n in range(17))
            m['eatn%d' % z] += g['eats'][0][b][0]
            m['eatd%d' % z] += g['eats'][0][b][1]
            m['oeatn%d' % z] += g['eats'][1][b][0]
            m['oeatd%d' % z] += g['eats'][1][b][1]
            m['spl%d' % z] += g['splits'][0][b]
            m['ospl%d' % z] += g['splits'][1][b]
            m['dth%d' % z] += g['deathsn'][0][b]
            m['odth%d' % z] += g['deathsn'][1][b]
            m['lost%d' % z] += g['lenlost'][0][b]
            m['olost%d' % z] += g['lenlost'][1][b]
            m['sparelost%d' % z] += g['spare_lost'][b]
            m['att%d' % z] += g['attempts'][b]
            m['natborn%d' % z] += g['natborn'][b]
            m['rounds%d' % z] += g['rounds'][b]
            m['alsum%d' % z] += g['alive_sum'][0][b]
            m['oalsum%d' % z] += g['alive_sum'][1][b]
    for z in range(5):
        for nm in ('turns', 'oturns', 'eatn', 'eatd', 'oeatn', 'oeatd', 'spl', 'ospl', 'dth', 'odth', 'lost', 'sparelost', 'att', 'len', 'natborn'):
            m[nm + 'G'] += m[nm + str(z)]
            if z in (1, 2):
                m[nm + 'M'] += m[nm + str(z)]
        for k in range(5):
            m['ltG_%d' % k] += m['lt%d_%d' % (z, k)]
            m['eatlG_%d' % k] += m['eatl%d_%d' % (z, k)]
    for key, n in g['splen'].items():
        bd, pl, c = map(int, key.split(','))
        m['sp_%s_%s' % (pl if pl < 8 else '8+', c if c < 4 else '4+')] += n
        m['spn'] += n
        m['sp_min'] += n * (c == 2)
        m['sp_rem2'] += n * (pl < 16 and c < 12 and pl - c == 2)
        if pl >= 5:
            m['sp5n'] += n
            m['sp5_child2'] += n * (c == 2)
            m['sp5_rem2'] += n * (pl < 16 and c < 12 and pl - c == 2)
        if pl >= 6:
            m['sp6n'] += n
            m['sp6_child2'] += n * (c == 2)
            m['sp6_rem2'] += n * (pl < 16 and c < 12 and pl - c == 2)
        m['spL_sum'] += pl * n
        m['spC_sum'] += c * n
    for key, v in g['elig'].items():
        k = tuple(map(int, key.split(',')))
        c = cls_of(k, big)
        for tag in ('C' + c, 'L%d' % k[1], 'B%d' % k[0], 'N%d' % k[2], 'Ro%d' % k[3], 'Rm%d' % k[4], 'P%d' % k[5], 'E%d' % k[6], 'F%d' % k[7], 'A%d' % k[8], 'ALL',
                    'X%s|L%d' % (c, k[1]), 'Y%s|A%d' % (c, k[8]), 'Z%s|B%d' % (c, k[0])):
            m['el_%s_t' % tag] += v[0]
            m['el_%s_s' % tag] += v[1]
            m['el_%s_sp' % tag] += v[2]
    for key, n in g['spells'].items():
        q = key.split(',')
        k = tuple(map(int, q[:8]))
        how, du = q[8], int(q[9])
        c = cls_of(k, big)
        for tag in (c, 'ALL'):
            m['spc_%s_n' % tag] += n
            if how == 's':
                m['spc_%s_s' % tag] += n
                if du == 0:
                    m['spc_%s_s0' % tag] += n
                if du <= 2:
                    m['spc_%s_s5' % tag] += n
            elif how == 'd':
                m['spc_%s_d' % tag] += n
            else:
                m['spc_%s_e' % tag] += n
    for key, n in g['deaths'].items():
        q = key.split(',')
        bd, cause, l5, nk, boxed, ageb, fr, hit = int(q[0]), q[1], int(q[2]), int(q[3]), int(q[4]), int(q[5]), int(q[6]), int(q[7])
        z = 0 if bd == 0 else 1 if bd <= 3 else 2
        for zz in (str(z), 'G'):
            m['d%s_%s' % (zz, cause)] += n
            m['d%s_boxed' % zz] += n * boxed
            if cause in ('wall', 'own', 'body', 'isplit', 'noact', 'sprint', 'timeout'):
                m['d%s_self' % zz] += n
                m['d%s_selfboxed' % zz] += n * boxed
                m['d%s_selffree' % zz] += n * (1 - boxed)
                if not boxed and nk >= 3:
                    m['d%s_selffree60' % zz] += n
                if not boxed and nk < 3:
                    m['d%s_selffreelow' % zz] += n
                if fr:
                    m['d%s_selffresh' % zz] += n
            if cause == 'isplit':
                m['d%s_isplit_L%d' % (zz, l5)] += n
                m['d%s_isplit_N%d' % (zz, nk)] += n
                m['d%s_isplit_box%d' % (zz, boxed)] += n
                if l5 >= 2 and nk == 4:
                    m['d%s_isplit_at64' % zz] += n
            m['dl%s_%d' % (zz, l5)] += n
    for key, n in g['life'].items():
        bb, lf, died = map(int, key.split(','))
        z = 0 if bb == 0 else 1 if bb <= 2 else 2 if bb == 3 else 3
        m['life%d_%d_%d' % (z, lf, died)] += n
    for r in MARKS:
        s = g['snaps'].get(str(r))
        if s is None and r == 500 and g['last'] >= 499:
            s = g['final']
        if s is None:
            continue
        f, o = s['sides']
        m['s%d_n' % r] = 1
        if r in (200, 300) and f['alive'] >= 56:
            m['av%d_%d' % (r, f['alive'])] = 1
        for nm in ('alive', 'total', 'longest', 'queen', 'spare'):
            m['s%d_%s' % (r, nm)] = f[nm]
            m['s%d_o%s' % (r, nm)] = o[nm]
        m['s%d_qalive' % r] = f['queen'] > 0
        m['s%d_oqalive' % r] = o['queen'] > 0
        m['s%d_ge56' % r] = f['alive'] >= 56
        m['s%d_ge60' % r] = f['alive'] >= 60
        m['s%d_eq64' % r] = f['alive'] >= 64
        late = r >= (150 if big else 300)
        for key, v in s['held'].items():
            c = cls_of(tuple(map(int, key.split(','))), big, late)
            m['h%d_%s_n' % (r, c)] += v[0]
            m['h%d_%s_sp' % (r, c)] += v[1]
        if str(r) in g['land']:
            a, b, t = g['land'][str(r)]
            m['land%d_f' % r] = a
            m['land%d_all' % r] = a + b + t
    f, o = g['final']['sides']
    how = 'elim' if f['alive'] == 0 or o['alive'] == 0 else 'queen' if f['queen'] != o['queen'] else 'longest' if f['longest'] != o['longest'] else 'total'
    m['end_%s_n' % how] = 1
    m['end_%s_w' % how] = g['result'] == 'win'
    m['max64'] = g['maxalive'][0] >= 64
    m['mx_%d' % g['maxalive'][0]] = 1
    m['max60'] = g['maxalive'][0] >= 60
    m['max56'] = g['maxalive'][0] >= 56
    m['maxover'] = g['maxalive'][0] > 64
    for r in (200, 300, 400):
        s = g['snaps'].get(str(r))
        if s is None:
            continue
        f2, o2 = s['sides']
        tag = 'ahead' if f2['longest'] > o2['longest'] else 'level' if f2['longest'] == o2['longest'] else 'behind'
        m['lg%d_%s_n' % (r, tag)] = 1
        m['lg%d_%s_w' % (r, tag)] = g['result'] == 'win'
        tag = 'more' if f2['alive'] > o2['alive'] else 'same' if f2['alive'] == o2['alive'] else 'fewer'
        m['al%d_%s_n' % (r, tag)] = 1
        m['al%d_%s_w' % (r, tag)] = g['result'] == 'win'
    return m


def load(mode):
    files = ['sl_test.jsonl'] if mode == 'test' else ['sl_scan-%d.jsonl' % k for k in range(4)]
    acc = {'O': defaultdict(Counter), 'R': defaultdict(Counter)}
    games = []
    for f in files:
        for line in open(D + f):
            g = json.loads(line)
            games.append(g)
            acc[g['tm']][g['layout']].update(flat(g))
    return acc, games


ACC = None


def val(tm, num, den, scale=1.0):
    a = ACC[tm]
    n = sum(a[l][num] for l in a)
    d = sum(a[l][den] for l in a) if den else 1
    pooled = scale * n / d if d else float('nan')
    per = {l: scale * a[l][num] / a[l][den] for l in a if (a[l][den] if den else 1)} if den else {l: scale * a[l][num] for l in a}
    eq = sum(per.values()) / len(per) if per else float('nan')
    return pooled, eq, per


def row(label, num, den, scale=1.0, fmt='%.2f'):
    po, eo, lo = val('O', num, den, scale)
    pr, er, lr = val('R', num, den, scale)
    both = [l for l in lo if l in lr]
    hi = sum(1 for l in both if lr[l] > lo[l])
    print(('%-34s O ' + fmt + ' R ' + fmt + ' | lay O ' + fmt + ' R ' + fmt + ' | R higher %d/%d') % (label, po, pr, eo, er, hi, len(both)))


def main():
    global ACC
    mode = sys.argv[1]
    want = set(sys.argv[2:])
    ACC, games = load(mode)
    on = lambda s: not want or s in want
    print('games', Counter(g['tm'] for g in games), 'layouts', len(ACC['O']), len(ACC['R']))
    if on('check'):
        print('== check against scoreboard (shared: splits 22.661/30.580, deaths 20.065/27.789, splits 101-300 21.072/28.904, splits per pearl .382/.362)')
        row('splits /1k turns game', 'splG', 'turnsG', 1000)
        row('deaths /1k turns game', 'dthG', 'turnsG', 1000)
        row('splits /1k turns 101-300', 'splM', 'turnsM', 1000)
        for tm in 'OR':
            a = ACC[tm]
            pe = sum(a[l]['eatnG'] + a[l]['eatdG'] for l in a)
            print(tm, 'splits per pearl pooled %.3f' % (sum(a[l]['splG'] for l in a) / pe),
                  'lay %.3f' % (sum(a[l]['splG'] / (a[l]['eatnG'] + a[l]['eatdG']) for l in a) / len(a)),
                  'max alive over 64 in games:', sum(a[l]['maxover'] for l in a), 'reached 64:', sum(a[l]['max64'] for l in a), '60:', sum(a[l]['max60'] for l in a), '56:', sum(a[l]['max56'] for l in a), 'of', sum(a[l]['games'] for l in a))
    if on('len'):
        print('== 1a share of dragon turns by length, %')
        for z in range(5):
            for k in range(5):
                row('r%s len %s' % (B4N[z], LBN[k]), 'lt%d_%d' % (z, k), 'turns%d' % z, 100, '%.1f')
            row('r%s mean length (cap 16)' % B4N[z], 'len%d' % z, 'turns%d' % z, 1, '%.2f')
        for k in range(5):
            row('game len %s' % LBN[k], 'ltG_%d' % k, 'turnsG', 100, '%.1f')
    if on('split'):
        print('== 1b splits by parent length and child size, % of splits')
        for pl in ('4', '5', '6', '7', '8+'):
            for c in ('2', '3', '4+'):
                row('parent %s child %s' % (pl, c), 'sp_%s_%s' % (pl, c), 'spn', 100, '%.1f')
        row('child is 2', 'sp_min', 'spn', 100, '%.1f')
        row('parent keeps 2', 'sp_rem2', 'spn', 100, '%.1f')
        row('parent 5+: share of splits', 'sp5n', 'spn', 100, '%.1f')
        row('parent 6+: child is 2', 'sp6_child2', 'sp6n', 100, '%.1f')
        row('parent 6+: parent keeps 2', 'sp6_rem2', 'sp6n', 100, '%.1f')
        row('splits per game', 'spn', 'games', 1, '%.1f')
        row('mean parent length', 'spL_sum', 'spn', 1, '%.2f')
        row('mean child length', 'spC_sum', 'spn', 1, '%.2f')
        for z in range(5):
            row('split attempts /1k turns r%s' % B4N[z], 'att%d' % z, 'turns%d' % z, 1000)
            row('splits /1k turns r%s' % B4N[z], 'spl%d' % z, 'turns%d' % z, 1000)
    if on('life'):
        print('== 1c rounds lived (dragons born in the band; Kaplan-Meier over buckets)')
        edges = (0, 1, 2, 5, 10, 20, 40, 80, 160, 999)
        for z, nm in enumerate(('0-100', '101-200', '201-300', '301+')):
            for tm in 'OR':
                a = ACC[tm]
                d = [sum(a[l]['life%d_%d_1' % (z, k)] for l in a) for k in range(10)]
                c = [sum(a[l]['life%d_%d_0' % (z, k)] for l in a) for k in range(10)]
                n = sum(d) + sum(c)
                at = n
                s = 1.0
                out = []
                med = None
                for k in range(10):
                    if at > 0:
                        s *= 1 - d[k] / at
                    at -= d[k] + c[k]
                    out.append('<=%d:%.0f%%' % (edges[k], 100 * (1 - s)))
                    if med is None and s <= 0.5:
                        med = edges[k]
                print('born r%s %s n=%d dead by: %s | median bucket <=%s' % (nm, tm, n, ' '.join(out), med))
    if on('alive'):
        print('== 1d dragons alive against the limit of 64')
        for tm in 'OR':
            a = ACC[tm]
            print(tm, 'most dragons alive in a game (56+): ' + ' '.join('%d:%d' % (v, sum(a[l]['mx_%d' % v] for l in a)) for v in range(56, 66)))
            for r in (200, 300):
                print(tm, 'alive at r%d (56+): ' % r + ' '.join('%d:%d' % (v, sum(a[l]['av%d_%d' % (r, v)] for l in a)) for v in range(56, 66)))
        for r in MARKS:
            row('r%d alive (games reaching)' % r, 's%d_alive' % r, 's%d_n' % r, 1, '%.1f')
            row('r%d games at 56+ %%' % r, 's%d_ge56' % r, 's%d_n' % r, 100, '%.1f')
            row('r%d games at 60+ %%' % r, 's%d_ge60' % r, 's%d_n' % r, 100, '%.1f')
            row('r%d games at 64 %%' % r, 's%d_eq64' % r, 's%d_n' % r, 100, '%.1f')
        for z in range(5):
            for k in range(5):
                row('r%s rounds with %s alive %%' % (B4N[z], NBN[k]), 'rnb%d_%d' % (z, k), 'rounds%d' % z, 100, '%.1f')
        for z in range(5):
            for k in range(5):
                row('r%s turns with %s alive %%' % (B4N[z], NBN[k]), 'nbt%d_%d' % (z, k), 'turns%d' % z, 100, '%.1f')
    if on('elig'):
        print('== 2 turns at length 4+ (could split): turns per game, splits per 100 such turns')
        tags = ['ALL'] + ['C' + c for c in CLS] + ['L%d' % k for k in range(4)] + ['B%d' % k for k in range(6)] + ['N%d' % k for k in range(5)] + ['Ro%d' % k for k in range(3)] + ['Rm%d' % k for k in range(4)] + ['P0', 'P1', 'E0', 'E1', 'F0', 'F1', 'A0', 'A1', 'A2']
        tags += ['X%s|L%d' % (c, k) for c in CLS for k in range(4)] + ['Y%s|A%d' % (c, k) for c in CLS for k in range(3)] + ['Z%s|B%d' % (c, k) for c in CLS for k in range(6)]
        go = sum(ACC['O'][l]['games'] for l in ACC['O'])
        gr = sum(ACC['R'][l]['games'] for l in ACC['R'])
        tot = 0.0
        for tag in tags:
            ot = sum(ACC['O'][l]['el_%s_t' % tag] for l in ACC['O'])
            os_ = sum(ACC['O'][l]['el_%s_s' % tag] for l in ACC['O'])
            osp = sum(ACC['O'][l]['el_%s_sp' % tag] for l in ACC['O'])
            rt = sum(ACC['R'][l]['el_%s_t' % tag] for l in ACC['R'])
            rs = sum(ACC['R'][l]['el_%s_s' % tag] for l in ACC['R'])
            rsp = sum(ACC['R'][l]['el_%s_sp' % tag] for l in ACC['R'])
            if ot + rt == 0:
                continue
            ho = os_ / ot if ot else 0.0
            hr = rs / rt if rt else 0.0
            ex = ot / go * (hr - ho)
            if tag[0] == 'C':
                tot += ex
            hi = lays = 0
            for l in ACC['O']:
                a, b = ACC['O'][l], ACC['R'][l]
                if a['el_%s_t' % tag] >= 30 and b['el_%s_t' % tag] >= 30:
                    lays += 1
                    hi += b['el_%s_s' % tag] / b['el_%s_t' % tag] > a['el_%s_s' % tag] / a['el_%s_t' % tag]
            print('%-24s O turns/g %7.1f spare-turns/g %7.1f splits/g %6.2f haz %5.1f | R turns/g %7.1f spare-turns/g %7.1f splits/g %6.2f haz %5.1f | O turns x (R haz - O haz) = %+7.2f /g | R haz higher in %d/%d layouts' % (
                tag, ot / go, osp / go, os_ / go, 100 * ho, rt / gr, rsp / gr, rs / gr, 100 * hr, ex, hi, lays))
        print('sum over classes of O turns x (R haz - O haz): %.2f per game' % tot)
        for nm in ('turnsG', 'splG'):
            print(nm, 'per game O %.1f R %.1f' % (sum(ACC['O'][l][nm] for l in ACC['O']) / go, sum(ACC['R'][l][nm] for l in ACC['R']) / gr))
        print('== 2b spells at length 4+ by the class of their first turn: per game, split on first turn %, within 5 turns %, ever %, died unsplit %, unsplit at game end %')
        for c in ('ALL',) + CLS:
            line = '%-14s' % c
            for tm, gg in (('O', go), ('R', gr)):
                a = ACC[tm]
                n = sum(a[l]['spc_%s_n' % c] for l in a)
                if not n:
                    line += ' | %s none' % tm
                    continue
                f = lambda nm: 100 * sum(a[l]['spc_%s_%s' % (c, nm)] for l in a) / n
                line += ' | %s %.1f/g first %.0f in5 %.0f ever %.0f died %.0f end %.0f' % (tm, n / gg, f('s0'), f('s5'), f('s'), f('d'), f('e'))
            print(line)
    if on('held'):
        print('== 2c dragons of 4+ alive at the round, by class: dragons per game and spare splits per game (games reaching the round)')
        for r in (100, 150, 200, 300, 400, 500):
            for c in CLS:
                line = 'r%d %-14s' % (r, c)
                for tm in 'OR':
                    a = ACC[tm]
                    n = max(1, sum(a[l]['s%d_n' % r] for l in a))
                    line += ' | %s %.2f dragons %.2f spare' % (tm, sum(a[l]['h%d_%s_n' % (r, c)] for l in a) / n, sum(a[l]['h%d_%s_sp' % (r, c)] for l in a) / n)
                print(line)
            row('r%d spare splits held' % r, 's%d_spare' % r, 's%d_n' % r, 1, '%.2f')
    if on('buys'):
        print('== 4 what it buys')
        for z in ('0', '1', '2', '3', '4', 'G', 'M'):
            nm = B4N[int(z)] if z.isdigit() else {'G': 'game', 'M': '101-300'}[z]
            row('r%s natural pearls /1k turns' % nm, 'eatn' + z, 'turns' + z, 1000, '%.1f')
            row('r%s dropped pearls /1k turns' % nm, 'eatd' + z, 'turns' + z, 1000, '%.1f')
            row('r%s deaths /1k turns' % nm, 'dth' + z, 'turns' + z, 1000, '%.1f')
            row('r%s length lost /1k turns' % nm, 'lost' + z, 'turns' + z, 1000, '%.1f')
            row('r%s spare splits lost in deaths /1k' % nm, 'sparelost' + z, 'turns' + z, 1000, '%.2f')
            row('r%s mean length' % nm, 'len' + z, 'turns' + z, 1, '%.2f')
            row('r%s OPP natural pearls /1k opp turns' % nm, 'oeatn' + z, 'oturns' + z, 1000, '%.1f')
            row('r%s OPP splits /1k opp turns' % nm, 'ospl' + z, 'oturns' + z, 1000, '%.1f')
            row('r%s OPP deaths /1k opp turns' % nm, 'odth' + z, 'oturns' + z, 1000, '%.1f')
        for z in range(5):
            for tm in 'OR':
                a = ACC[tm]
                f = sum(a[l]['eatn%d' % z] for l in a)
                o = sum(a[l]['oeatn%d' % z] for l in a)
                fd = sum(a[l]['eatd%d' % z] for l in a)
                od = sum(a[l]['oeatd%d' % z] for l in a)
                gms = sum(a[l]['games'] for l in a)
                lay = [a[l]['eatn%d' % z] / (a[l]['eatn%d' % z] + a[l]['oeatn%d' % z]) for l in a if a[l]['eatn%d' % z] + a[l]['oeatn%d' % z]]
                print('r%s %s share of natural pearls eaten %.1f%% (lay %.1f%%), of dropped %.1f%%; per game: natural %.1f dropped %.1f splits %.1f deaths %.1f turns %.0f; alive mean %.1f opp %.1f' % (
                    B4N[z], tm, 100 * f / (f + o), 100 * sum(lay) / len(lay), 100 * fd / max(1, fd + od), f / gms, fd / gms,
                    sum(a[l]['spl%d' % z] for l in a) / gms, sum(a[l]['dth%d' % z] for l in a) / gms, sum(a[l]['turns%d' % z] for l in a) / gms,
                    sum(a[l]['alsum%d' % z] for l in a) / max(1, sum(a[l]['rounds%d' % z] for l in a)), sum(a[l]['oalsum%d' % z] for l in a) / max(1, sum(a[l]['rounds%d' % z] for l in a))))
        print('-- pearls eaten per 1k turns by the length of the eater, and deaths per 1k turns by length')
        for z in ('0', '1', '2', '3', 'G'):
            nm = B4N[int(z)] if z.isdigit() else 'game'
            for k in range(5):
                row('r%s eaten /1k turns at len %s' % (nm, LBN[k]), 'eatl%s_%d' % (z, k), 'lt%s_%d' % (z, k), 1000, '%.1f')
        for k in range(5):
            row('game deaths /1k turns at len %s' % LBN[k], 'dlG_%d' % k, 'ltG_%d' % k, 1000, '%.1f')
        print('-- standings')
        for r in (100, 200, 300, 400, 500):
            for nm in ('alive', 'oalive', 'total', 'ototal', 'longest', 'olongest', 'queen', 'oqueen', 'spare', 'ospare'):
                row('r%d %s' % (r, nm), 's%d_%s' % (r, nm), 's%d_n' % r, 1, '%.1f')
            row('r%d queen alive %%' % r, 's%d_qalive' % r, 's%d_n' % r, 100, '%.1f')
            row('r%d OPP queen alive %%' % r, 's%d_oqalive' % r, 's%d_n' % r, 100, '%.1f')
            if r < 500:
                row('r%d tiles nearer to our heads %%' % r, 'land%d_f' % r, 'land%d_all' % r, 100, '%.1f')
        print('-- how games end: n and won')
        for tm in 'OR':
            a = ACC[tm]
            print(tm, ' '.join('%s %d/%d' % (h, sum(a[l]['end_%s_w' % h] for l in a), sum(a[l]['end_%s_n' % h] for l in a)) for h in ('elim', 'queen', 'longest', 'total')),
                  'won', sum(a[l]['won'] for l in a), 'of', sum(a[l]['games'] for l in a))
            for r in (200, 300, 400):
                print('  r%d longest: ' % r + ' '.join('%s %d/%d' % (h, sum(a[l]['lg%d_%s_w' % (r, h)] for l in a), sum(a[l]['lg%d_%s_n' % (r, h)] for l in a)) for h in ('ahead', 'level', 'behind')),
                      '| dragons: ' + ' '.join('%s %d/%d' % (h, sum(a[l]['al%d_%s_w' % (r, h)] for l in a), sum(a[l]['al%d_%s_n' % (r, h)] for l in a)) for h in ('more', 'same', 'fewer')))
    if on('death'):
        print('== deaths of the focal side per 1k turns')
        for z, tz in (('0', '0'), ('1', None), ('G', 'G')):
            nm = {'0': '0-100', '1': '101-300', 'G': 'game'}[z]
            den = 'turns0' if z == '0' else 'turnsM' if z == '1' else 'turnsG'
            for c in ('wall', 'own', 'body', 'isplit', 'noact', 'sprint', 'timeout', 'hmx', 'hms', 'hvx', 'hvs', 'boxed', 'self', 'selfboxed', 'selffree', 'selffree60', 'selffreelow', 'selffresh', 'isplit_L0', 'isplit_L1', 'isplit_L2', 'isplit_L3', 'isplit_L4', 'isplit_box0', 'isplit_box1', 'isplit_at64', 'isplit_N3', 'isplit_N4'):
                row('r%s %s' % (nm, c), 'd%s_%s' % (z, c), den, 1000, '%.2f')


main()
