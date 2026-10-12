"""Scratch (diag-topfight): tables from tf_scan-*.jsonl. Usage: python3 tf_agg.py <section|all> <file> [file...]
Groups: T3:<team> fresh top games, T1:<team> older top games, OQ/OB/OM:us ours (B7Q, B7, main), *:opp the other side."""
import sys, json
from collections import defaultdict, Counter
from pathlib import Path

NAMES = {454: 'aAah', 157: 'larp', 306: 'Cutlery', 70: 'chad gdp', 91: 'SSS', 264: 'forgot', 842: 'horse', 1119: 'ours'}
STUDY = {'T3': {454, 157, 306, 70}, 'T1': {306, 91, 264, 842, 454}}
LCS = ['2', '3', '4', '5-7', '8-14', '15+']


def lc(L):
    return 0 if L <= 2 else 1 if L == 3 else 2 if L == 4 else 3 if L <= 7 else 4 if L <= 14 else 5


PAIR = [False]
BIG = [0]


def grp(rec, s):
    base = grp0(rec, s)
    if BIG[0] == 1 and rec['cells'] <= 1200:
        return 'skip'
    if BIG[0] == 2 and rec['cells'] > 1200:
        return 'skip'
    if PAIR[0]:
        other = rec['b'] if s == 0 else rec['a']
        on = rec['bn'] if s == 0 else rec['an']
        return base + '>' + str(NAMES.get(other, (on or str(other)).encode('ascii', 'ignore').decode()[:10]))
    return base


def grp0(rec, s):
    team = rec['a'] if s == 0 else rec['b']
    lab = rec['label']
    if lab in STUDY:
        return '%s:%s' % (lab, NAMES.get(team, team)) if team in STUDY[lab] else lab + ':opp'
    return lab + (':us' if team == 1119 else ':' + str(NAMES.get(team, 'opp')) if lab == 'OT' else ':opp')


def load(files):
    recs, seen = [], set()
    for f in files:
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
            recs.append(r)
    return recs


def sh(a, b):
    return '%.2f' % (a / b) if b else '-'


def main():
    sec = sys.argv[1]
    while ':' in sec:
        flag, sec = sec.split(':', 1)
        if flag == 'p':
            PAIR[0] = True
        elif flag == 'big':
            BIG[0] = 1
        elif flag == 'small':
            BIG[0] = 2
    recs = load(sys.argv[2:])
    G = defaultdict(lambda: dict(games=0, wins=0, big=0, turns=Counter(), tl=Counter(), hos=[], ch=defaultdict(lambda: [0, 0]),
                                 ex=defaultdict(lambda: [0] * 8), lr=defaultdict(lambda: [0] * 8), qa=defaultdict(lambda: [0] * 3),
                                 la=defaultdict(lambda: [0] * 3), sp=Counter(), dth=defaultdict(lambda: [0, 0]),
                                 mix=defaultdict(lambda: [0] * 6), mixn=Counter(), ser=defaultdict(list), hov=[], tr=Counter(), ends=[]))
    for r in recs:
        gs = [grp(r, 0), grp(r, 1)]
        for s in (0, 1):
            g = G[gs[s]]
            g['games'] += 1
            f = r['final']
            me, ot = f[4 * s:4 * s + 4], f[4 * (1 - s):4 * (1 - s) + 4]
            rule = 'wipe' if (me[0] == 0 or ot[0] == 0) else 'queen' if me[3] != ot[3] else 'longest' if me[1] != ot[1] else 'total'
            g['ends'].append((r['last_round'], rule, r.get('winner') == 'ab'[s], me, ot, r['cells']))
            g['big'] += r['cells'] > 1200
            g['wins'] += r.get('winner') == 'ab'[s]
            for rnd, m in r['mix'].items():
                for z in range(6):
                    g['mix'][rnd][z] += m[s][z]
                g['mixn'][rnd] += 1
            for rnd, v in r['series'].items():
                g['ser'][rnd].append(v[4 * s:4 * s + 4])
            g['ser']['end'].append(r['final'][4 * s:4 * s + 4])
        for s, bd, L, kd, n in r['turns']:
            G[gs[s]]['turns'][bd] += n
            G[gs[s]]['tl'][(lc(L), kd)] += n
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
        for nm in ('qa', 'la'):
            for row in r[nm]:
                v = G[gs[row[0]]][nm][tuple(row[1:3])]
                for z in range(3):
                    v[z] += row[3 + z]
        for row in r['sp']:
            G[gs[row[0]]]['sp'][tuple(row[1:5])] += row[5]
        for row in r.get('tr', []):
            G[gs[row[0]]]['tr'][tuple(row[1:5])] += row[5]
        for row in r['dth']:
            v = G[gs[row[0]]]['dth'][tuple(row[1:3])]
            v[0] += row[3]
            v[1] += row[4]
        for h in r['hos']:
            if h['cross']:
                h['game'] = r['game']
                h['cells'] = r['cells']
                G[gs[h['ms']]]['hos'].append(h)
                G[gs[1 - h['ms']]]['hov'].append(h)
    G.pop('skip', None)
    order = sorted(G, key=lambda k: (k.split(':')[0], k))
    if sec in ('all', 'rate'):
        print('== RATE: games, won, above 1200 cells; rams started a game; per 1000 own dragon turns r0-100, r101-300, r301-500, all; rams suffered a game')
        for k in order:
            g = G[k]
            n = Counter(band_(h['r']) for h in g['hos'])
            t = g['turns']
            tot = sum(t.values())
            print('%-14s %4d %4d %4d | %6.1f | %5.2f %5.2f %5.2f %5.2f | %6.1f' % (
                k, g['games'], g['wins'], g['big'], len(g['hos']) / g['games'],
                1000 * n[0] / max(1, t[0]), 1000 * n[1] / max(1, t[1]), 1000 * n[2] / max(1, t[2]), 1000 * len(g['hos']) / max(1, tot),
                len(g['hov']) / g['games']))
    if sec in ('all', 'ram'):
        print('== RAM PROFILE (cross-team head-ons this side started)')
        for k in order:
            g = G[k]
            H = g['hos']
            n = len(H)
            if not n:
                continue
            ml = Counter(min(lc(h['L0']), 3) for h in H)
            vl = Counter(lc(h['Lv']) for h in H)
            vk = Counter('queen' if h['vk'] == 1 else 'top' if h['vk'] == 2 else 'short' if h['Lv'] <= 4 else 'mid' for h in H)
            rel = Counter(0 if h['Lv'] < h['L0'] else 1 if h['Lv'] == h['L0'] else 2 if h['Lv'] < 2 * h['L0'] else 3 for h in H)
            stp = Counter(min(h['k'], 4) for h in H)
            paid = [max(0, h['L0'] + h['ate'] - h['Ld']) for h in H]
            print(k, 'n', n)
            print('  mover L 2/3/4/5+: %s | victim L %s' % (' '.join(sh(ml[z], n) for z in range(4)), ' '.join(sh(vl[z], n) for z in range(6))))
            print('  victim kind queen/top8+/short/mid: %s | shorter/same/longer/twice: %s' % (
                ' '.join(sh(vk[z], n) for z in ('queen', 'top', 'short', 'mid')), ' '.join(sh(rel[z], n) for z in range(4))))
            print('  steps 1/2/3/4+: %s | paid share %s, mean paid %.2f, ate on way %s | mover died too %s' % (
                ' '.join(sh(stp[z], n) for z in (1, 2, 3, 4)), sh(sum(1 for x in paid if x > 0), n), sum(paid) / n,
                sh(sum(1 for h in H if h['ate'] > 0), n), sh(sum(1 for h in H if h['dm'] > 0), n)))
            print('  length lost a ram: mover side %.2f (drops %.2f: own side ate %.2f, enemy %.2f) | victim side %.2f (drops %.2f: victim side ate %.2f, mover side %.2f)' % (
                sum(h['L0'] for h in H) / n, sum(h['dm'] for h in H) / n, sum(h['mm'] for h in H) / n, sum(h['mv'] for h in H) / n,
                sum(h['Lv'] for h in H) / n, sum(h['dv'] for h in H) / n, sum(h['vv'] for h in H) / n, sum(h['vm'] for h in H) / n))
            netm = sum(h['L0'] - h['mm'] - h['vm'] for h in H) / n
            netv = sum(h['Lv'] - h['vv'] - h['mv'] for h in H) / n
            netm15 = sum(h['L0'] - h['mm15'] - h['vm15'] for h in H) / n
            netv15 = sum(h['Lv'] - h['vv15'] - h['mv15'] for h in H) / n
            print('  net after 5 rounds: mover side -%.2f, victim side -%.2f, rate %.2f | after 15: -%.2f, -%.2f, rate %.2f' % (
                netm, netv, netm / netv if netv else 0, netm15, netv15, netm15 / netv15 if netv15 else 0))
            print('  heads within 5 of the hit: mover side %.2f, victim side %.2f | mover side more/equal/fewer %s %s %s | victim alone %s | not outnumbered in view %s' % (
                sum(h['m5'] for h in H) / n, sum(h['v5'] for h in H) / n, sh(sum(1 for h in H if h['m5'] > h['v5']), n),
                sh(sum(1 for h in H if h['m5'] == h['v5']), n), sh(sum(1 for h in H if h['m5'] < h['v5']), n),
                sh(sum(1 for h in H if h['v5'] == 0), n), sh(sum(1 for h in H if h['ov'] >= 0 and h['ov'] + 1 > h['ev']), sum(1 for h in H if h['ov'] >= 0))))
            print('  victim ended its last turn in free reach %s, paid reach %s, outside %s, no turn yet %s | of those in reach, had a safe step %s' % (
                sh(sum(1 for h in H if h['vs'] == 2), n), sh(sum(1 for h in H if h['vs'] == 1), n), sh(sum(1 for h in H if h['vs'] == 0), n),
                sh(sum(1 for h in H if h['vs'] < 0), n), sh(sum(1 for h in H if h['vs'] > 0 and h['vsafe']), sum(1 for h in H if h['vs'] > 0))))
    if sec in ('all', 'xr'):
        print('== EXCHANGE by mover length x victim kind: n a game; gross mover L / victim L = rate; net after 5 rounds mover / victim = rate')
        for k in order:
            g = G[k]
            H = g['hos']
            if not H:
                continue
            print(k)
            cells = defaultdict(list)
            for h in H:
                a = min(lc(h['L0']), 3)
                t = 'queen' if h['vk'] == 1 else 'top8+' if h['vk'] == 2 else 'short' if h['Lv'] <= 4 else 'mid5+'
                cells[(a, t)].append(h)
                cells[(9, t)].append(h)
                cells[(a, 'all')].append(h)
            for a in (0, 1, 2, 3, 9):
                out = []
                for t in ('queen', 'top8+', 'mid5+', 'short', 'all'):
                    hs = cells.get((a, t), [])
                    if not hs:
                        out.append('%s: -' % t)
                        continue
                    m = sum(h['L0'] for h in hs)
                    v = sum(h['Lv'] for h in hs)
                    nm = sum(h['L0'] - h['mm'] - h['vm'] for h in hs)
                    nv = sum(h['Lv'] - h['vv'] - h['mv'] for h in hs)
                    out.append('%s: %.2f/g %.1f/%.1f=%.2f net %.1f/%.1f=%.2f' % (t, len(hs) / g['games'], m / len(hs), v / len(hs), m / v,
                                                                                nm / len(hs), nv / len(hs), nm / nv if nv else 0))
                print('  mover %s | %s' % ('all' if a == 9 else ['2', '3', '4', '5+'][a], ' | '.join(out)))
    if sec in ('all', 'ch'):
        print('== CHANCES (non-queen movers): per mover length x target length, free reach n/game taken; paid reach n/game taken')
        for k in order:
            g = G[k]
            if not g['ch']:
                continue
            print(k)
            F = defaultdict(lambda: [0, 0])
            P = defaultdict(lambda: [0, 0])
            for (L, M, rc, tk, outn, bd, mk), v in g['ch'].items():
                if mk == 1:
                    continue
                d = F if rc == 0 else P
                d[(lc(L), lc(M))][0] += v[0]
                d[(lc(L), lc(M))][1] += v[1]
            print('  target:      ' + ''.join('%-26s' % x for x in LCS))
            for a in range(6):
                print('  mover %-5s ' % LCS[a] + ''.join('%5.2f %s ; %5.2f %s   ' % (F[(a, m)][0] / g['games'], sh(F[(a, m)][1], F[(a, m)][0]),
                                                                              P[(a, m)][0] / g['games'], sh(P[(a, m)][1], P[(a, m)][0])) for m in range(6)))
    if sec in ('all', 'ch2'):
        print('== CHANCES by relation, movers 2-4 non-queen: [free not-outnumbered | free outnumbered | paid not-out | paid out] n/game taken; and by target kind')
        for k in order:
            g = G[k]
            if not g['ch']:
                continue
            R = defaultdict(lambda: [0, 0])
            K = defaultdict(lambda: [0, 0])
            B = defaultdict(lambda: [0, 0])
            for (L, M, rc, tk, outn, bd, mk), v in g['ch'].items():
                if mk == 1:
                    continue
                if L <= 4:
                    rel = 0 if M < L else 1 if M < 2 * L else 2
                    x = R[(rel, min(rc, 1), outn)]
                    x[0] += v[0]
                    x[1] += v[1]
                    x = B[(rel, bd)]
                    x[0] += v[0]
                    x[1] += v[1]
                x = K[(0 if L <= 4 else 1 if L <= 7 else 2, tk, min(rc, 1))]
                x[0] += v[0]
                x[1] += v[1]
            print(k)
            for rel, nm in ((0, 'shorter'), (1, 'same to under twice'), (2, 'twice or more')):
                print('  %-20s ' % nm + ' | '.join('%5.2f %s' % (R[(rel, rc, o)][0] / g['games'], sh(R[(rel, rc, o)][1], R[(rel, rc, o)][0]))
                                                for rc in (0, 1) for o in (0, 1)) + '   by band r0-100/101-300/301+: ' +
                      ' '.join(sh(B[(rel, b)][1], B[(rel, b)][0]) for b in (0, 1, 2)))
            for ml, nm in ((0, 'mover 2-4'), (1, 'mover 5-7'), (2, 'mover 8+')):
                print('  %-10s ' % nm + ' | '.join('%s free %5.2f %s paid %5.2f %s' % (tn, K[(ml, tk, 0)][0] / g['games'], sh(K[(ml, tk, 0)][1], K[(ml, tk, 0)][0]),
                                                                                    K[(ml, tk, 1)][0] / g['games'], sh(K[(ml, tk, 1)][1], K[(ml, tk, 1)][0]))
                                                 for tk, tn in ((1, 'queen'), (2, 'top8+'), (0, 'other'))))
    if sec in ('all', 'ex'):
        print('== EXPOSURE at the end of own turn: per class turn-ends/game; share in free reach, paid reach; of those, share with a safe single step; rammed before next turn per 1000 turn-ends: outside / paid / free')
        for k in order:
            g = G[k]
            if not g['ex']:
                continue
            print(k)
            C = defaultdict(lambda: [0] * 8)
            for (bd, L, kd), v in g['ex'].items():
                keys = ['queen' if kd == 1 else LCS[lc(L)], 'all']
                if kd == 2:
                    keys.append('top8+')
                if kd != 1 and L <= 4:
                    keys.append('2-4')
                if kd != 1 and L >= 8:
                    keys.append('8+')
                for c in keys:
                    for z in range(8):
                        C[c][z] += v[z]
            for c in LCS + ['2-4', '8+', 'top8+', 'queen', 'all']:
                v = C[c]
                if not v[0]:
                    continue
                out0 = v[0] - v[1] - v[2]
                print('  %-6s %8.1f | free %.4f paid %.4f | safe step: free %s paid %s | rammed/1000: %.2f / %.2f / %.2f' % (
                    c, v[0] / g['games'], v[2] / v[0], v[1] / v[0], sh(v[4], v[2]), sh(v[3], v[1]),
                    1000 * v[5] / max(1, out0), 1000 * v[6] / max(1, v[1]), 1000 * v[7] / max(1, v[2])))
    if sec in ('all', 'lr'):
        print('== LONG DRAGON / QUEEN at turn start, nearest enemy head of 5 or less within 6 tiles: turns/game; closer/same/away; 2+ steps; died in its turn /1000; rammed before next turn /1000; a team mate between')
        CL = ['queen 2-4', 'queen 5+', 'long 8-14', 'long 15+']
        DB = ['none in 6', '1-2 tiles', '3 tiles', '4-6 tiles']
        for k in order:
            g = G[k]
            if not g['lr']:
                continue
            print(k)
            C = defaultdict(lambda: [0] * 8)
            S = defaultdict(lambda: [0] * 8)
            for (bd, cls, d0b, n5, btw), v in g['lr'].items():
                for z in range(8):
                    C[(cls, d0b)][z] += v[z]
                    S[(cls, d0b, btw, n5)][z] += v[z]
            for cls in range(4):
                for d0b in range(4):
                    v = C[(cls, d0b)]
                    tot = v[0] + v[5]
                    if not tot:
                        continue
                    b1 = [0] * 8
                    for n5 in range(3):
                        for z in range(8):
                            b1[z] += S[(cls, d0b, 1, n5)][z]
                    alone = S[(cls, d0b, 0, 0)]
                    comp = [S[(cls, d0b, 0, 1)][z] + S[(cls, d0b, 0, 2)][z] + b1[z] for z in range(8)]
                    print('  %-10s %-10s %7.1f | %s %s %s | sprint %s | died %.1f | rammed %.2f | between %s (rammed with %.2f) | alone in 5: %s of turns, rammed %.2f; with company %.2f' % (
                        CL[cls], DB[d0b], tot / g['games'], sh(v[1], v[0]), sh(v[2], v[0]), sh(v[3], v[0]), sh(v[4], v[0]),
                        1000 * v[5] / tot, 1000 * v[6] / tot, sh(b1[0] + b1[5], tot), 1000 * b1[6] / max(1, b1[0] + b1[5]),
                        sh(alone[0] + alone[5], tot), 1000 * alone[6] / max(1, alone[0] + alone[5]), 1000 * comp[6] / max(1, comp[0] + comp[5])))
    if sec in ('all', 'tr'):
        print('== NEAREST ENEMY HEAD before and after own turn (tiles; path within 8 steps). Per class: share of turns by gap at start 1/2/3/4/5-6/none; then for start gap g: ends at 1 / 2 / 3 / 4+ / died')
        CN = ['2-4', '5-7', '8+', 'queen']
        RN = ['shorter', 'same', 'longer']
        for k in order:
            g = G[k]
            if not g['tr']:
                continue
            print(k)
            for cls in range(4):
                tot = sum(n for (c, rl, a0, a1), n in g['tr'].items() if c == cls)
                if not tot:
                    continue
                st = Counter()
                for (c, rl, a0, a1), n in g['tr'].items():
                    if c == cls:
                        st[a0] += n
                print('  %-6s %8.1f turns/g | start gap 1/2/3/4/5-6/none: %s' % (CN[cls], tot / g['games'], ' '.join('%.4f' % (st[z] / tot) for z in (1, 2, 3, 4, 5, 7))))
                for rl in range(3):
                    out = []
                    for a0 in (1, 2, 3, 4):
                        c = Counter()
                        for (c_, rl_, a0_, a1), n in g['tr'].items():
                            if c_ == cls and rl_ == rl and a0_ == a0:
                                c[a1 if a1 <= 3 else 9 if a1 == 8 else 4] += n
                        t = sum(c.values())
                        out.append('g%d n %.1f/g: %s' % (a0, t / g['games'], ' '.join(sh(c[z], t) for z in (1, 2, 3, 4, 9))))
                    print('      nearest %-8s %s' % (RN[rl], ' | '.join(out)))
    if sec in ('all', 'key'):
        print('== KEY CELLS (non-queen movers; n a game, taken). own reach = free steps + length - 2; "pearl" = beyond it')
        cells_ = [
            ('2>2 free', lambda L, M, rc, o: L == 2 and M == 2 and rc == 0),
            ('2>3+ free', lambda L, M, rc, o: L == 2 and M >= 3 and rc == 0),
            ('2>any pearl, not outn', lambda L, M, rc, o: L == 2 and rc >= 1 and o == 0),
            ('2>any pearl, outn', lambda L, M, rc, o: L == 2 and rc >= 1 and o == 1),
            ('3>2 free/1 paid, not outn', lambda L, M, rc, o: L == 3 and M == 2 and rc <= 1 and o == 0),
            ('3>2 free/1 paid, outn', lambda L, M, rc, o: L == 3 and M == 2 and rc <= 1 and o == 1),
            ('3>3 free', lambda L, M, rc, o: L == 3 and M == 3 and rc == 0),
            ('3>3 1 paid, not outn', lambda L, M, rc, o: L == 3 and M == 3 and rc == 1 and o == 0),
            ('3>3 1 paid, outn', lambda L, M, rc, o: L == 3 and M == 3 and rc == 1 and o == 1),
            ('3>4+ free/1 paid', lambda L, M, rc, o: L == 3 and M >= 4 and rc <= 1),
            ('4>2 any, not outn', lambda L, M, rc, o: L == 4 and M == 2 and o == 0),
            ('4>3 any, not outn', lambda L, M, rc, o: L == 4 and M == 3 and o == 0),
            ('4>4+ any', lambda L, M, rc, o: L == 4 and M >= 4),
            ('2-4 > same..<2x, not outn', lambda L, M, rc, o: L <= 4 and L <= M < 2 * L and o == 0),
            ('2-4 > same..<2x, outn', lambda L, M, rc, o: L <= 4 and L <= M < 2 * L and o == 1),
            ('2-4 > shorter, not outn', lambda L, M, rc, o: L <= 4 and M < L and o == 0),
            ('2-4 > shorter, outn', lambda L, M, rc, o: L <= 4 and M < L and o == 1),
            ('2-4 > twice+', lambda L, M, rc, o: L <= 4 and M >= 2 * L),
            ('5-7 > shorter', lambda L, M, rc, o: 5 <= L <= 7 and M < L),
            ('5-7 > same or longer', lambda L, M, rc, o: 5 <= L <= 7 and M >= L),
            ('8+ > any', lambda L, M, rc, o: L >= 8),
        ]
        for nm, f in cells_:
            out = []
            for k in order:
                g = G[k]
                n = t = 0
                for (L, M, rc, tk, outn, bd, mk), v in g['ch'].items():
                    if mk != 1 and f(L, M, rc, outn):
                        n += v[0]
                        t += v[1]
                out.append('%s %.1f %s' % (k.split(':')[0][:2] + ':' + k.split(':')[1][:7], n / g['games'], sh(t, n)))
            print('  %-28s ' % nm + ' | '.join(out))
    if sec in ('all', 'ends'):
        print('== HOW GAMES END: games; ended before r200 / r200-399 / r400-499 / r500; decided by wipe-out, queen, longest, total as won-lost; median final own count/longest/total/queen vs other side')
        for k in order:
            g = G[k]
            E = g['ends']
            n = len(E)
            lr_ = Counter(0 if e[0] < 200 else 1 if e[0] < 400 else 2 if e[0] < 500 else 3 for e in E)
            rl = Counter((e[1], e[2]) for e in E)
            med = lambda z, w: sorted(e[w][z] for e in E)[n // 2]
            print('  %-22s %3d | %d %d %d %d | %s | %s vs %s' % (k, n, lr_[0], lr_[1], lr_[2], lr_[3],
                  ' '.join('%s %d-%d' % (x, rl[(x, True)], rl[(x, False)]) for x in ('wipe', 'queen', 'longest', 'total')),
                  '/'.join(str(med(z, 3)) for z in range(4)), '/'.join(str(med(z, 4)) for z in range(4))))
    if sec in ('all', 'qa'):
        print('== APPROACH by dragons of 2-4 (non-queen): share of turns that end closer / further, by gap at turn start 0-3, 4-6, 7-12, 13-20, 21+; to the enemy queen, then to the enemy longest of 10+')
        for k in order:
            g = G[k]
            for nm in ('qa', 'la'):
                C = defaultdict(lambda: [0] * 3)
                for (bd, gb), v in g[nm].items():
                    for z in range(3):
                        C[gb][z] += v[z]
                print('  %-14s %s ' % (k, nm) + ' | '.join('%7.0f/g %s %s' % (C[gb][0] / g['games'], sh(C[gb][1], C[gb][0]), sh(C[gb][2], C[gb][0])) for gb in range(5)))
    if sec in ('all', 'far'):
        print('== HOW FAR THE RAMMER CAME: gap between rammer (or its parent) and victim 10 and 20 rounds before; share 10+ tiles away at -10; at -20; median; for queen victims, top8+ victims, others')
        for k in order:
            g = G[k]
            out = []
            for nm, f in (('queen', lambda h: h['vk'] == 1), ('top8+', lambda h: h['vk'] == 2), ('other', lambda h: h['vk'] == 0)):
                hs = [h for h in g['hos'] if f(h) and h['g10'] >= 0]
                hs2 = [h for h in g['hos'] if f(h) and h['g20'] >= 0]
                if not hs:
                    out.append('%s: -' % nm)
                    continue
                a = sorted(h['g10'] for h in hs)
                b = sorted(h['g20'] for h in hs2) or [0]
                out.append('%s n %d: -10r %s (med %d) -20r %s (med %d)' % (nm, len(hs), sh(sum(1 for x in a if x >= 10), len(a)), a[len(a) // 2],
                                                                        sh(sum(1 for x in b if x >= 10), len(b)), b[len(b) // 2]))
            print('  %-14s ' % k + ' | '.join(out))
    if sec in ('all', 'feed'):
        print('== FEED: of pearls dropped by both bodies, share eaten within 5 rounds by mover-side queen, by a mover-side 10+, by other mover-side, by victim side; rams with a mover-side 10+ within 5 tiles; victim-side 10+ within 5 tiles; groups: another ram by the same side within 5 tiles and 3 rounds')
        for k in order:
            g = G[k]
            H = g['hos']
            if not H:
                continue
            drops = sum(h['dm'] + h['dv'] for h in H)
            fq = sum(h['fq'] for h in H)
            fb = sum(h['fb'] for h in H)
            ms = sum(h['mm'] + h['vm'] for h in H)
            vs = sum(h['mv'] + h['vv'] for h in H)
            bygame = defaultdict(list)
            for h in H:
                bygame[h['game']].append(h)
            pair = 0
            for hs in bygame.values():
                for i, h in enumerate(hs):
                    for h2 in hs:
                        if h2 is not h and abs(h2['r'] - h['r']) <= 3 and abs(h2['x'] - h['x']) + abs(h2['y'] - h['y']) <= 5:
                            pair += 1
                            break
            print('  %-14s queen %s | 10+ %s | other own %s | victim side %s | nobody %s || own 10+ within 5: %s | victim-side 10+ within 5: %s | grouped %s' % (
                k, sh(fq, drops), sh(fb, drops), sh(ms - fq - fb, drops), sh(vs, drops), sh(drops - ms - vs, drops),
                sh(sum(1 for h in H if h['ml'] <= 5), len(H)), sh(sum(1 for h in H if h['vl'] <= 5), len(H)), sh(pair, len(H))))
    if sec in ('all', 'mix'):
        print('== LENGTH MIX: dragons a game of 2 / 3 / 4 / 5-7 / 8-14 / 15+ at r100, r200, r300, r400; medians count, longest, total, queen at r200, r300, end')
        for k in order:
            g = G[k]
            out = []
            for rnd in ('100', '200', '300', '400'):
                n = g['mixn'][rnd]
                if n:
                    out.append('r%s[%d]: ' % (rnd, n) + ' '.join('%.1f' % (x / n) for x in g['mix'][rnd]))
            med = []
            for rnd in ('200', '300', 'end'):
                vs = g['ser'][rnd]
                if vs:
                    med.append('%s: ' % rnd + '/'.join(str(sorted(v[z] for v in vs)[len(vs) // 2]) for z in range(4)))
            print('  %-14s ' % k + ' | '.join(out) + ' || ' + ' | '.join(med))
    if sec in ('all', 'sp'):
        print('== SPLITS a game by length before -> length kept (non-queen), top patterns; r0-100 / r101-300 / r301+')
        for k in order:
            g = G[k]
            for bd in (0, 1, 2):
                c = Counter()
                for (b, before, keep, isq), n in g['sp'].items():
                    if b == bd and not isq:
                        c[(before, keep)] += n
                tot = sum(c.values())
                print('  %-14s band %d: %6.1f/g  ' % (k, bd, tot / g['games']) + ' '.join('%d>%d+%d %.2f' % (b_, kp, b_ - kp, n / tot) for (b_, kp), n in c.most_common(8)))
    if sec in ('all', 'dth'):
        print('== DEATHS a game (count, length): wall, own body, other body, rammed (victim), ramming (mover), same-team head-on, other (no action etc.)')
        for k in order:
            g = G[k]
            c = defaultdict(lambda: [0, 0])
            for (bd, code), v in g['dth'].items():
                nm = {0: 'wall', 1: 'own', 2: 'body', 6: 'rammed', 5: 'ramming', 15: 'same', 16: 'same', 4: 'other'}.get(code, 'other')
                c[nm][0] += v[0]
                c[nm][1] += v[1]
            print('  %-14s ' % k + ' | '.join('%s %.1f, %.0f' % (nm, c[nm][0] / g['games'], c[nm][1] / g['games'])
                                              for nm in ('wall', 'own', 'body', 'rammed', 'ramming', 'same', 'other')))


def band_(r):
    return 0 if r <= 100 else 1 if r <= 300 else 2


main()
