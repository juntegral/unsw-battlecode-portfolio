"""Scratch (diag-topfight): builds the report tables from the tf_scan files (single source for every table cell).
Usage: python3 tf_tables.py   (prints markdown tables A to E and a list of facts)"""
import sys, json
from collections import defaultdict, Counter
from pathlib import Path

W = 'data/analysis/ladder/dossier/work/'
REPORT = '~/01. Project/\u1100\u1162\u110b\u1175\u11ab \u1111\u1173\u1105\u1169\u110c\u1166\u11a8\u1110\u1173/unsw-swarm/data/analysis/ladder/dossier/diag-topfight.md'
FILES = ['tf_scan-T3-1.jsonl', 'tf_scan-T3b-0.jsonl', 'tf_scan-T3c-0.jsonl', 'tf_scan-T3d-0.jsonl', 'tf_scan-T1-0.jsonl', 'tf_scan-OQ-1.jsonl',
         'tf_scan-OM-1.jsonl', 'tf_scan-OT-0.jsonl', 'tf_scan-OT-1.jsonl']
NAMES = {454: 'aAah', 157: 'larp', 306: 'Cutlery', 70: 'chad gdp', 91: 'SSS', 264: 'forgot', 842: 'horse', 1119: 'ours'}
STUDY = {'T3': {454, 157, 306, 70}, 'T1': {306, 91, 264, 842}}
COLS = [('T3:aAah', 'aAah'), ('T3:chad gdp', 'chad gdp'), ('T3:larp', 'larp'), ('T3:Cutlery', 'Cutlery'), ('T1:Cutlery', 'Cutlery to 5 Oct'),
        ('T1:SSS', 'SSS'), ('T1:forgot', 'forgot'), ('T1:horse', 'horse'), ('OQ:us', 'ours B7Q'), ('OM:us', 'ours main'),
        ('OT:us', 'ours B7Q v top'), ('OT:Cutlery', 'Cutlery v ours'), ('OT:larp', 'larp v ours')]
ROWCOLS = [c for c in COLS if not c[0].startswith('T1')]


def grp(rec, s):
    team = rec['a'] if s == 0 else rec['b']
    lab = rec['label']
    if lab in STUDY:
        return '%s:%s' % (lab, NAMES.get(team, team)) if team in STUDY[lab] else lab + ':opp'
    return lab + (':us' if team == 1119 else ':' + str(NAMES.get(team, 'opp')) if lab == 'OT' else ':opp')


def lc(L):
    return 0 if L <= 2 else 1 if L == 3 else 2 if L == 4 else 3 if L <= 7 else 4 if L <= 14 else 5


def tor(a, b, n):
    d = abs(a - b)
    return min(d, n - d)


def klass(L, M, stp, vis, ov, ev, rnd, seen=True):
    if rnd > 400 or not seen:
        return None
    free = (L + 3) // 4
    pearl = stp > free + L - 2
    margin = ov + 1 - ev
    if M < L:
        if pearl:
            return None
        if margin >= 1:
            return '3on2' if (L, M) == (3, 2) else '4on3' if (L, M) == (4, 3) else '4on2'
        return 'short-outn'
    hunt = vis >= 2 * L or (vis >= 10 and vis >= L + 4)
    if pearl:
        return 'pearl' if (margin >= 1 or hunt) else None
    if hunt:
        return 'yes'
    if vis < L:
        return 'hid' if margin >= 1 else None
    if margin >= 1:
        return 'yes'
    return 'm0' if margin == 0 else 'm1' if margin == -1 else 'm2'


def sh(a, b, d=2):
    return ('%.' + str(d) + 'f') % (a / b) if b else '-'


def load():
    recs, seen = [], set()
    for f in FILES:
        p = Path(W + f)
        if not p.is_file():
            continue
        for line in p.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if (r['label'], r['game']) in seen:
                continue
            seen.add((r['label'], r['game']))
            recs.append(r)
    return recs


def build(recs):
    G = defaultdict(lambda: dict(games=0, wins=0, turns=Counter(), hos=[], hov=[], ch=defaultdict(lambda: [0, 0]),
                                 ex=defaultdict(lambda: [0] * 8), lr=defaultdict(lambda: [0] * 8), tr=Counter(),
                                 kc=defaultdict(lambda: [0, 0]), kv=defaultdict(lambda: [0] * 3), rowgames=0, trgames=0,
                                 ev=defaultdict(lambda: [0, 0, 0]), evg=defaultdict(set), evx=defaultdict(list)))
    for r in recs:
        gs = [grp(r, 0), grp(r, 1)]
        for s in (0, 1):
            g = G[gs[s]]
            g['games'] += 1
            g['wins'] += r.get('winner') == 'ab'[s]
            g['rowgames'] += 'rows' in r
            g['trgames'] += 'tr' in r
        for s, bd, L, kd, n in r['turns']:
            G[gs[s]]['turns'][bd] += n
        for row in r['ch']:
            v = G[gs[row[0]]]['ch'][tuple(row[1:8])]
            v[0] += row[8]
            v[1] += row[9]
        for row in r['ex']:
            v = G[gs[row[0]]]['ex'][tuple(row[1:4])]
            for z in range(8):
                v[z] += row[4 + z]
        for row in r['lr']:
            v = G[gs[row[0]]]['lr'][tuple(row[1:6])]
            for z in range(8):
                v[z] += row[6 + z]
        for row in r.get('tr', []):
            G[gs[row[0]]]['tr'][tuple(row[1:5])] += row[5]
        hits = [defaultdict(list), defaultdict(list)]
        for h in r['hos']:
            if h['cross']:
                hits[h['ms']][h['vid']].append(h)
        for row in r.get('rows', []):
            rnd, s, a, L, kd, j, M, tk, stp, free, pe, ov, ev, vis, taken, rc, al, ale = row[:18]
            if kd != 0 or L > 4:
                continue
            seen = len(row) < 22 or (tor(row[18], row[20], r['w']) <= 3 and tor(row[19], row[21], r['h']) <= 3)
            c = klass(L, M, stp, vis, ov, ev, rnd, seen)
            if c:
                v = G[gs[s]]['kc'][c]
                v[0] += 1
                v[1] += taken == 1
                if taken != 1 and c in ('3on2', '4on3', 'pearl', 'm0', 'hid'):
                    e = G[gs[s]]['ev'][c]
                    e[0] += 1
                    G[gs[s]]['evg'][c].add(r['game'])
                    hh = [h for h in hits[1 - s].get(a, []) if rnd <= h['r'] <= rnd + 5]
                    if hh:
                        e[1] += 1
                        if any(h['mid'] == j for h in hh):
                            e[2] += 1
                            G[gs[s]]['evx'][c].append((r['game'], 'won' if r.get('winner') == 'ab'[s] else 'lost', r['w'], r['h'], rnd, L, row[18], row[19], M, row[20],
                                                      row[21], stp, ov + 1, ev, [h for h in hh if h['mid'] == j][0]['r']))
        for h in r['hos']:
            if not h['cross']:
                continue
            h['game'] = r['game']
            G[gs[h['ms']]]['hos'].append(h)
            G[gs[1 - h['ms']]]['hov'].append(h)
            if 'rows' in r and h['mk'] == 0 and h['L0'] <= 4 and h['d'] >= 0:
                seen = tor(h['sx'], h['x'], r['w']) <= 3 and tor(h['sy'], h['y'], r['h']) <= 3
                c = klass(h['L0'], h['Lv'], h['d'], h['vis'], h['ov'], h['ev'], h['r'], seen)
                if c:
                    v = G[gs[h['ms']]]['kv'][c]
                    v[0] += 1
                    v[1] += h['L0'] - h['mm'] - h['vm']
                    v[2] += h['Lv'] - h['vv'] - h['mv']
    return G


def table(title, cols, rows):
    out = ['| ' + title + ' | ' + ' | '.join(h for k, h in cols) + ' |', '|---|' + '---|' * len(cols)]
    for name, f in rows:
        out.append('| ' + name + ' | ' + ' | '.join(f(k) for k, h in cols) + ' |')
    return '\n'.join(out)


def main():
    G = build(load())
    band = lambda r: 0 if r <= 100 else 1 if r <= 300 else 2

    def H(k):
        return G[k]['hos']

    def A_rate(k):
        g = G[k]
        n = Counter(band(h['r']) for h in g['hos'])
        return ' / '.join('%.2f' % (1000 * n[b] / max(1, g['turns'][b])) for b in (0, 1, 2))

    def dist(k, f, keys):
        hs = H(k)
        c = Counter(f(h) for h in hs)
        return ' / '.join(sh(c[z], len(hs)) for z in keys)

    def A_paid(k):
        hs = H(k)
        n = len(hs)
        over = [max(0, h['k'] - h['free']) for h in hs]
        gone = [max(0, h['k'] - 1 - h['free']) for h in hs]
        bey = sum(1 for h in hs if h['k'] > h['free'] + h['L0'] - 2)
        return '%s; %.2f; %.2f; %s' % (sh(sum(1 for x in over if x), n), sum(over) / n, sum(gone) / n, sh(bey, n))

    def A_gross(k):
        hs = H(k)
        n = len(hs)
        return '%.2f; %.2f' % (sum(h['L0'] for h in hs) / n, sum(h['Lv'] for h in hs) / n)

    def A_drops(k):
        hs = H(k)
        n = len(hs)
        s_ = lambda key: sum(h[key] for h in hs) / n
        return '%.2f: %.2f, %.2f; %.2f: %.2f, %.2f' % (s_('dm'), s_('mm'), s_('mv'), s_('dv'), s_('vm'), s_('vv'))

    def A_net(k):
        hs = H(k)
        n = len(hs)
        m = sum(h['L0'] - h['mm'] - h['vm'] for h in hs) / n
        v = sum(h['Lv'] - h['vv'] - h['mv'] for h in hs) / n
        m15 = sum(h['L0'] - h['mm15'] - h['vm15'] for h in hs) / n
        v15 = sum(h['Lv'] - h['vv15'] - h['mv15'] for h in hs) / n
        return '%.2f, %.2f; %.2f (%.2f)' % (m, v, m / v, m15 / v15)

    def A_heads(k):
        hs = H(k)
        n = len(hs)
        return '%.2f, %.2f; %s; %s' % (sum(h['m5'] for h in hs) / n, sum(h['v5'] for h in hs) / n, sh(sum(1 for h in hs if h['m5'] > h['v5']), n),
                                       sh(sum(1 for h in hs if h['v5'] == 0), n))

    def A_group(k):
        hs = H(k)
        n = len(hs)
        bygame = defaultdict(list)
        for h in hs:
            bygame[h['game']].append(h)
        pair = 0
        for lst in bygame.values():
            for h in lst:
                for h2 in lst:
                    if h2 is not h and abs(h2['r'] - h['r']) <= 3 and abs(h2['x'] - h['x']) + abs(h2['y'] - h['y']) <= 5:
                        pair += 1
                        break
        drops = sum(h['dm'] + h['dv'] for h in hs)
        return '%s; %s; %s' % (sh(pair, n), sh(sum(1 for h in hs if h['ml'] <= 5), n), sh(sum(h['fb'] + h['fq'] for h in hs), drops))

    def A_far(k):
        hs = H(k)
        q = [h for h in hs if h['vk'] == 1 and h['g10'] >= 0]
        o = [h for h in hs if h['vk'] != 1 and h['g10'] >= 0]
        return '%s (%d); %s' % (sh(sum(1 for h in q if h['g10'] >= 10), len(q)), len(q), sh(sum(1 for h in o if h['g10'] >= 10), len(o)))

    def xr(sel):
        def f(k):
            hs = [h for h in H(k) if sel(h)]
            if len(hs) < 5:
                return '- (%.2f)' % (len(hs) / G[k]['games'])
            m = sum(h['L0'] - h['mm'] - h['vm'] for h in hs)
            v = sum(h['Lv'] - h['vv'] - h['mv'] for h in hs)
            return '%.2f, %.2f (%.2f)' % (sum(h['L0'] for h in hs) / sum(h['Lv'] for h in hs), m / v if v else 0, len(hs) / G[k]['games'])
        return f

    short = lambda h: h['vk'] == 0 and h['Lv'] <= 4
    rowsA = [
        ('games (won)', lambda k: '%d (%d)' % (G[k]['games'], G[k]['wins'])),
        ('head-ons started per 1,000 own dragon turns, r0-100 / r101-300 / r301-500', A_rate),
        ('started a game; suffered a game', lambda k: '%.1f; %.1f' % (len(H(k)) / G[k]['games'], len(G[k]['hov']) / G[k]['games'])),
        ('attacker length at its turn start 2 / 3 / 4 / 5+', lambda k: dist(k, lambda h: min(lc(h['L0']), 3), (0, 1, 2, 3))),
        ('target: queen / side\'s longest of 8+ / other 5+ / short 2-4', lambda k: dist(k, lambda h: 'q' if h['vk'] == 1 else 't' if h['vk'] == 2 else 's' if h['Lv'] <= 4 else 'm', 'qtms')),
        ('target shorter / same / longer / twice the attacker or more', lambda k: dist(k, lambda h: 0 if h['Lv'] < h['L0'] else 1 if h['Lv'] == h['L0'] else 2 if h['Lv'] < 2 * h['L0'] else 3, (0, 1, 2, 3))),
        ('steps walked, the hit counted: 1 / 2 / 3 / 4+', lambda k: dist(k, lambda h: min(h['k'], 4), (1, 2, 3, 4))),
        ('went past its free steps; steps past them a ram; segments gone before the hit a ram; went past what its length pays for (always over a pearl)', A_paid),
        ('length lost a ram, gross: attacker, target', A_gross),
        ('pearls dropped a ram by the attacker: eaten in 5 rounds by its side, by the other; by the target: eaten by the attacker\'s side, by its own', A_drops),
        ('net length lost a ram after 5 rounds: attacker\'s side, target\'s side; rate (rate after 15 rounds)', A_net),
        ('other heads within 5 tiles of the hit: attacker\'s side, target\'s side; attacker\'s side has more; target has none of its own', A_heads),
        ('another ram by the same side within 5 tiles and 3 rounds; an own 10+ within 5 tiles of the hit; share of the drops eaten by an own 10+ or queen', A_group),
        ('exchange, gross rate, net rate (rams a game): a 2 on a short head', xr(lambda h: short(h) and h['L0'] == 2)),
        ('a 3 on a short head', xr(lambda h: short(h) and h['L0'] == 3)),
        ('a 4 or longer on a short head', xr(lambda h: short(h) and h['L0'] >= 4)),
        ('any on another head of 5+', xr(lambda h: h['vk'] == 0 and h['Lv'] >= 5)),
        ('any on the side\'s longest of 8+', xr(lambda h: h['vk'] == 2)),
        ('any on the queen', xr(lambda h: h['vk'] == 1)),
    ]
    tA = table('each side\'s head-ons', COLS, rowsA)
    print(tA)
    print()
    print('FAR ' + ' | '.join(h + ' ' + A_far(k) for k, h in COLS))

    def kc(f):
        def g_(k):
            g = G[k]
            n = t = 0
            for (L, M, rc, tk, outn, bd, mk), v in g['ch'].items():
                if mk != 1 and f(L, M, rc, outn):
                    n += v[0]
                    t += v[1]
            return '%.1f, %s' % (n / g['games'], sh(t, n))
        return g_

    rowsC = [
        ('2 on 2, free step', kc(lambda L, M, rc, o: L == 2 and M == 2 and rc == 0)),
        ('2 on any, second step over a pearl, not outnumbered', kc(lambda L, M, rc, o: L == 2 and rc >= 1 and o == 0)),
        ('3 on 2, free or one paid step, not outnumbered', kc(lambda L, M, rc, o: L == 3 and M == 2 and rc <= 1 and o == 0)),
        ('3 on 3, one paid step, not outnumbered', kc(lambda L, M, rc, o: L == 3 and M == 3 and rc == 1 and o == 0)),
        ('3 on 4+, free or one paid step', kc(lambda L, M, rc, o: L == 3 and M >= 4 and rc <= 1)),
        ('4 on 2, any reach, not outnumbered', kc(lambda L, M, rc, o: L == 4 and M == 2 and o == 0)),
        ('4 on 3, any reach, not outnumbered', kc(lambda L, M, rc, o: L == 4 and M == 3 and o == 0)),
        ('2-4 on same to under twice, outnumbered', kc(lambda L, M, rc, o: L <= 4 and L <= M < 2 * L and o == 1)),
        ('2-4 on twice or more', kc(lambda L, M, rc, o: L <= 4 and M >= 2 * L)),
        ('all 2-4: free reach', kc(lambda L, M, rc, o: L <= 4 and rc == 0)),
        ('all 2-4: paid reach', kc(lambda L, M, rc, o: L <= 4 and rc >= 1)),
        ('5-7 on shorter', kc(lambda L, M, rc, o: 5 <= L <= 7 and M < L)),
        ('5-7 on same or longer', kc(lambda L, M, rc, o: 5 <= L <= 7 and M >= L)),
        ('8+ on any', kc(lambda L, M, rc, o: L >= 8)),
    ]
    tC = table('chances a game, share taken (non-queens)', COLS, rowsC)
    print(tC)
    print()

    def kd(c):
        def f(k):
            g = G[k]
            if not g['rowgames']:
                return '-'
            v = g['kc'].get(c, [0, 0])
            x = g['kv'].get(c, [0, 0, 0])
            gain = ', %+.2f' % ((x[2] - x[1]) / x[0]) if x[0] >= 8 else ', n/a'
            return '%.1f, %s%s' % (v[0] / g['rowgames'], sh(v[1], v[0]), gain)
        return f

    rowsD = [
        ('same or longer, not outnumbered, in own reach (our rule says yes)', kd('yes')),
        ('same to under twice, heads level in view (1 v 1, 2 v 2)', kd('m0')),
        ('same to under twice, outnumbered by one', kd('m1')),
        ('same to under twice, outnumbered by two or more', kd('m2')),
        ('a 3 on a 2, not outnumbered', kd('3on2')),
        ('a 4 on a 3, not outnumbered', kd('4on3')),
        ('a 4 on a 2, not outnumbered', kd('4on2')),
        ('shorter head, outnumbered or level', kd('short-outn')),
        ('same or longer, reachable only over a pearl', kd('pearl')),
        ('same or longer, fewer parts in view than own length, not outnumbered', kd('hid')),
    ]
    tD = table('chance turns a game, taken, gain a ram', ROWCOLS, rowsD)
    print(tD)
    print()

    def exc(sel):
        def f(k):
            v = [0] * 8
            for (bd, L, kd_), x in G[k]['ex'].items():
                if sel(L, kd_):
                    for z in range(8):
                        v[z] += x[z]
            return v
        return f

    def E_expo(sel):
        f = exc(sel)
        return lambda k: '%.2f / %.2f' % (100 * f(k)[2] / max(1, f(k)[0]), 100 * f(k)[1] / max(1, f(k)[0]))

    def E_safe(k):
        v = exc(lambda L, kd_: kd_ != 1 and L <= 4)(k)
        return '%s / %s' % (sh(v[4], v[2]), sh(v[3], v[1]))

    def E_haz(k):
        v = exc(lambda L, kd_: True)(k)
        return '%.2f / %.0f / %.0f' % (1000 * v[5] / max(1, v[0] - v[1] - v[2]), 1000 * v[6] / max(1, v[1]), 1000 * v[7] / max(1, v[2]))

    def trc(k, cls, rel, a0):
        c = Counter()
        for (c_, rl, s0, s1), n in G[k]['tr'].items():
            if c_ == cls and (rel is None or rl == rel) and s0 == a0:
                c[s1] += n
        return c

    def E_contact(k):
        g = G[k]
        if not g['trgames']:
            return '-'
        tot = sum(n for (c_, rl, s0, s1), n in g['tr'].items() if c_ == 0)
        near = sum(n for (c_, rl, s0, s1), n in g['tr'].items() if c_ == 0 and s0 <= 3)
        a = trc(k, 0, 2, 3)
        b = trc(k, 0, 2, 2)
        return '%.1f; %s; %s' % (100 * near / tot, sh(a[2], sum(a.values())), sh(b[3] + b[4] + b[5] + b[7], sum(b.values())))

    def E_adj(k):
        if not G[k]['trgames']:
            return '-'
        out = []
        for rel in (0, 1, 2):
            c = trc(k, 0, rel, 1)
            out.append(sh(c[8], sum(c.values())))
        c2 = trc(k, 0, 0, 2)
        return ' / '.join(out) + '; ' + sh(c2[8], sum(c2.values()))

    def E_long(k):
        g = G[k]
        v = [0] * 8
        b = [0] * 8
        al = [0] * 8
        for (bd, cls, d0b, n5, btw), x in g['lr'].items():
            if cls in (2, 3) and d0b in (1, 2):
                for z in range(8):
                    v[z] += x[z]
                    if btw:
                        b[z] += x[z]
                    if n5 == 0:
                        al[z] += x[z]
        tot = v[0] + v[5]
        return '%.1f; %s; %.0f; %s; %s' % (tot / g['games'], sh(v[3], v[0]), 1000 * v[6] / max(1, tot), sh(b[0] + b[5], tot), sh(al[0] + al[5], tot))

    def E_long0(k):
        g = G[k]
        v = [0] * 8
        for (bd, cls, d0b, n5, btw), x in g['lr'].items():
            if cls in (2, 3) and d0b == 0:
                for z in range(8):
                    v[z] += x[z]
        tot = v[0] + v[5]
        return '%.1f; %.2f; %s' % (tot / g['games'], 1000 * v[6] / max(1, tot), sh(v[4], v[0]))

    rowsE = [
        ('turn ends inside an enemy head\'s free reach / paid reach, percent: dragons of 2-4; 5-7; 8+; queen',
         lambda k: '; '.join(E_expo(f_)(k) for f_ in (lambda L, kd_: kd_ != 1 and L <= 4, lambda L, kd_: kd_ != 1 and 5 <= L <= 7,
                                                     lambda L, kd_: kd_ != 1 and L >= 8, lambda L, kd_: kd_ == 1))),
        ('of those turn ends of 2-4, a single step to a tile outside every reach existed: free / paid', E_safe),
        ('rammed before the next own turn per 1,000 turn ends: outside reach / in paid / in free', E_haz),
        ('2-4: percent of turns starting with an enemy head within 3 tiles; 3 tiles from a longer head, share stepping to 2; 2 tiles from one, share stepping away', E_contact),
        ('2-4 beside a head, share dead that turn (the ram): head shorter / same / longer; two tiles from a shorter head', E_adj),
        ('8+ with a head of 5 or less within 3 tiles: turns a game; share moving away; rammed before next turn per 1,000; a team mate between; no team mate within 5', E_long),
        ('8+ with no such head within 6 tiles: turns a game; rammed per 1,000; share of turns of 2+ steps', E_long0),
    ]
    tE = table('where dragons end their turns', COLS, rowsE)
    print(tE)
    print()
    print('FACTS')
    for k, hname in COLS:
        g = G[k]
        hs = g['hos']
        print(k, 'games', g['games'], 'rowgames', g['rowgames'], 'rams', len(hs), 'per1000 all %.2f' % (1000 * len(hs) / max(1, sum(g['turns'].values()))),
              'mover died share', sh(sum(1 for h in hs if h['dm'] > 0), len(hs)))
        for c in ('yes', 'm0', '3on2', '4on3', 'pearl', 'hid'):
            v = g['kc'].get(c, [0, 0])
            x = g['kv'].get(c, [0, 0, 0])
            e = g['ev'].get(c, [0, 0, 0])
            print('     ', c, 'turns', v[0], 'taken', v[1], 'rams', x[0], 'mover net %.2f victim net %.2f' % (x[1] / max(1, x[0]), x[2] / max(1, x[0])),
                  '| refused', e[0], 'in games', len(g['evg'].get(c, ())), 'then rammed in 5 rounds', e[1], 'by that head', e[2])
            if k in ('OQ:us', 'OT:us'):
                lst = g['evx'].get(c, [])
                for t in lst[::max(1, len(lst) // 5)][:5]:
                    print('            game %d %s %dx%d r%d ours %d at (%d,%d) their %d at (%d,%d) %d steps, heads in view %d v %d, rammed by it r%d' % t)

    total = sum(len(G[k]['hos']) for k in G)
    died = sum(1 for k in G for h in G[k]['hos'] if h['dm'] > 0)
    bey = sum(1 for k in G for h in G[k]['hos'] if h['k'] > h['free'] + h['L0'] - 2)
    beyp = sum(1 for k in G for h in G[k]['hos'] if h['k'] > h['free'] + h['L0'] - 2 and h['ate'] >= h['k'] - h['free'] - h['L0'] + 2)
    print('TWOS that walked 2+ steps', sum(1 for k in G for h in G[k]['hos'] if h['L0'] == 2 and h['k'] >= 2), 'of them ate a pearl', sum(1 for k in G for h in G[k]['hos'] if h['L0'] == 2 and h['k'] >= 2 and h['ate'] >= 1))
    print('ALL head-ons', total, 'attacker died', died, 'beyond own reach', bey, 'with enough pearls eaten', beyp, 'games', sum(G[k]['games'] for k in G) // 2)
    if len(sys.argv) > 1 and sys.argv[1] == 'write':
        text = Path(W + 'tf_prose.txt').read_text()
        for tag, tab in (('@@A@@', tA), ('@@C@@', tC), ('@@D@@', tD), ('@@E@@', tE)):
            parts = text.split(tag)
            assert len(parts) == 2, tag
            text = tab.join(parts)
        text = (chr(96) * 3).join(text.split('@@F@@'))
        Path(REPORT).write_text(text)
        print('written', len(text.splitlines()), 'lines')


main()
