"""Scratch (diag-toprams): tables from tr_scan-*.jsonl. Usage: python3 tr_agg.py <tags,comma> <section> [rmax]
Columns: for each opponent team, 'us' = our dragons are the subject (victims in t1/t2), 'them' = theirs are."""
import sys, json
from collections import Counter, defaultdict
from pathlib import Path

W = 'data/analysis/ladder/dossier/work/'
NAMES = {157: 'larp', 306: 'Cutlery', 454: 'aAah', 70: 'chad', 1119: 'ours'}
ME = 1119
tags = sys.argv[1].split(',')
sec = sys.argv[2]
RM = int(sys.argv[3]) if len(sys.argv) > 3 else 150
games = []
for tag in tags:
    f = Path(W + 'tr_scan-' + tag + '.jsonl')
    for line in f.read_text().splitlines():
        if line.strip():
            games.append(json.loads(line))
COLS = []
for opp in (157, 306, 454, 0):
    for who in ('us', 'them'):
        COLS.append((opp, who))


def cols_of(gm, s):
    os_ = 0 if gm['a'] == ME else 1
    opp = gm['b'] if os_ == 0 else gm['a']
    who = 'us' if s == os_ else 'them'
    return [(opp, who), (0, who)]


def head(c):
    return ('ours v ' + NAMES.get(c[0], 'all')) if c[1] == 'us' else (NAMES.get(c[0], 'all') + ' v ours')


def show(title, table, order=None, fmt='%s'):
    print('##', title)
    keys = order or sorted({k for c in COLS for k in table[c]}, key=str)
    print('| row | ' + ' | '.join(head(c) for c in COLS) + ' |')
    for k in keys:
        print('| ' + str(k) + ' | ' + ' | '.join(fmt % (table[c].get(k, 0),) for c in COLS) + ' |')


def share(cnt, keys):
    tot = sum(cnt.values())
    return ' / '.join('%.2f' % (cnt.get(k, 0) / tot if tot else 0) for k in keys) + ' (n=%d)' % tot


def doing(row):
    if row is None:
        return 'no turn yet (split child)'
    if row.get('lite'):
        return 'no head within 5 at its turn start'
    if row.get('sp'):
        return 'splitting'
    if row.get('ate', 0) > 0:
        return 'eating'
    ch = chosen(row)
    if ch is None:
        return 'no step'
    if row['pv'] > 0 and ch[2] >= 0 and (row['dp'] < 0 or ch[2] < row['dp']):
        return 'walking to a pearl'
    if row['pv'] > 0:
        return 'pearl in view, not nearer'
    return 'no pearl in view'


def chosen(row):
    f = row.get('first', -1)
    for o in row.get('opt', ()):
        if o[0] == f:
            return o
    return None


def opt_cls(row, o, only=None, small=True):
    """Highest class of option o over the near heads (heads of 2 to 4 when small; one head id when only is given)."""
    best = 0
    for e, c in zip(row['near'], o[3]):
        if only is not None and e[0] != only:
            continue
        if small and e[1] > 4:
            continue
        if c > best:
            best = c
    return best


G = Counter()
T = defaultdict(Counter)
for gm in games:
    os_ = 0 if gm['a'] == ME else 1
    for s in (0, 1):
        for c in cols_of(gm, s):
            G[c] += 1
            for (ts, bd, lb, q, n) in gm['turns']:
                if ts == s:
                    T[c][bd] += n
                    if lb <= 4:
                        T[c]['s%d' % bd] += n
                        if not q:
                            T[c]['n%d' % bd] += n
            for r_ in ('50', '100', '150'):
                mk = gm['marks'].get(r_)
                if mk:
                    T[c]['alive' + r_] += mk[s][0]
                    T[c]['len' + r_] += mk[s][1]
                    T[c]['g' + r_] += 1

if sec == 't0':
    print('games', len(games), {head(c): G[c] for c in COLS})
    tab = defaultdict(dict)
    R = defaultdict(Counter)
    for gm in games:
        for ram in gm['rams']:
            if not ram['cross']:
                continue
            vs = 1 - ram['ms']
            bd = 0 if ram['r'] <= 100 else 1 if ram['r'] <= 150 else 2
            for c in cols_of(gm, vs):
                R[c][bd] += 1
                if ram['Lv'] <= 4:
                    R[c]['s%d' % bd] += 1
    for c in COLS:
        t = tab[c]
        t['games'] = G[c]
        t['rammed /1k own turns r0-100'] = '%.2f' % (1000 * R[c][0] / max(1, T[c][0]))
        t['rammed /1k own turns r101-150'] = '%.2f' % (1000 * R[c][1] / max(1, T[c][1]))
        t['short rammed /1k short turns r0-100'] = '%.2f' % (1000 * R[c]['s0'] / max(1, T[c]['s0']))
        t['short rammed /1k short turns r101-150'] = '%.2f' % (1000 * R[c]['s1'] / max(1, T[c]['s1']))
        t['rammed a game r0-100; r101-150'] = '%.1f; %.1f' % (R[c][0] / G[c], R[c][1] / G[c])
        t['short rammed a game r0-100; r101-150'] = '%.1f; %.1f' % (R[c]['s0'] / G[c], R[c]['s1'] / G[c])
        t['dragons at r50; r100; r150'] = '%.1f; %.1f; %.1f' % tuple(T[c]['alive' + r_] / max(1, T[c]['g' + r_]) for r_ in ('50', '100', '150'))
        t['share of turns by 2-4 r0-100'] = '%.2f' % (T[c]['s0'] / max(1, T[c][0]))
    show('t0 rates', tab, ['games', 'rammed /1k own turns r0-100', 'rammed /1k own turns r101-150', 'short rammed /1k short turns r0-100',
                           'short rammed /1k short turns r101-150', 'rammed a game r0-100; r101-150', 'short rammed a game r0-100; r101-150',
                           'dragons at r50; r100; r150', 'share of turns by 2-4 r0-100'])

if sec in ('t1', 't2'):
    C = defaultdict(lambda: defaultdict(Counter))
    SUM = defaultdict(Counter)
    ex = []
    for gm in games:
        rowof = {}
        for row in gm['rows']:
            if 'hit' in row:
                rowof[row['hit']] = row
        for ri, ram in enumerate(gm['rams']):
            if not ram['cross'] or ram['r'] > RM or ram['Lv'] > 4:
                continue
            vs = 1 - ram['ms']
            row = rowof.get(ri)
            for c in cols_of(gm, vs):
                K = C[c]
                S_ = SUM[c]
                S_['n'] += 1
                K['victim queen']['q' if ram['vq'] else 'not'] += 1
                if ram['vq']:
                    continue
                S_['nq'] += 1
                K['round']['0-50' if ram['r'] <= 50 else '51-100' if ram['r'] <= 100 else '101-150'] += 1
                K['attacker L']['%d' % min(ram['L0'], 5)] += 1
                K['victim L']['%d' % ram['Lv']] += 1
                K['pair']['%dv%d' % (min(ram['L0'], 5), ram['Lv'])] += 1
                K['attacker vs victim']['longer' if ram['L0'] > ram['Lv'] else 'same' if ram['L0'] == ram['Lv'] else 'shorter'] += 1
                K['steps']['%d' % min(ram['k'], 3)] += 1
                paid = max(0, ram['k'] - ram['free'])
                K['paid steps']['%d' % min(paid, 2)] += 1
                K['pearl on the way']['yes' if ram['ate'] else 'no'] += 1
                K['a 3 from two tiles']['yes' if ram['L0'] == 3 and ram['k'] == 2 else 'no'] += 1
                K['beyond plain reach']['yes' if ram['k'] > ram['free'] + ram['L0'] - 2 else 'no'] += 1
                K['where (victim side)'][('own', 'middle', 'theirs', 'n/a')[ram['zv']]] += 1
                K['doing'][doing(row)] += 1
                K['attacker queen']['q' if ram['mq'] else 'not'] += 1
                K['rammer start in view after its move']['yes' if ram['inv'] else 'no'] += 1
                S_['m5'] += ram['m5']
                S_['v5'] += ram['v5']
                K['heads within 5']['attacker more' if ram['m5'] > ram['v5'] else 'level' if ram['m5'] == ram['v5'] else 'victim more'] += 1
                K['victim alone within 5']['yes' if ram['v5'] == 0 else 'no'] += 1
                S_['lost_m'] += ram['L0']
                S_['lost_v'] += ram['Lv']
                S_['got_m'] += ram['mm'] + ram['vm']
                S_['got_v'] += ram['mv'] + ram['vv']
                S_['dm'] += ram['dm']
                S_['dv'] += ram['dv']
                if row is None or row.get('lite'):
                    K['t2 kind']['no row'] += 1
                    continue
                S_['rows'] += 1
                ne = None
                for e in row['near']:
                    if e[0] == ram['mid']:
                        ne = e
                en = None
                for e in row.get('end', ()):
                    if e[0] == ram['mid']:
                        en = e
                c0 = ne[6] if ne else 0
                c1 = en[3] if en else 0
                K['rammer in view at last turn start']['yes' if ne and ne[4] else 'no'] += 1
                K['rammer parts in view'][str(ne[5]) if ne else '0'] += 1
                K['trader (now rule) at last turn']['yes' if row['tn'] else 'no'] += 1
                K['trader (short-by-1) at last turn']['yes' if row['tw'] else 'no'] += 1
                K['outnumbered or level in view']['yes' if row['nA'] + 1 - row['nE'] < 1 else 'no'] += 1
                kind = 'stayed in reach' if c0 else 'walked into reach' if c1 else 'outside at its turn end'
                K['t2 kind'][kind] += 1
                K['t2 class at start'][str(c0)] += 1
                K['t2 class at end'][str(c1)] += 1
                K['could ram first: engine']['yes' if ne and ne[8] else 'no'] += 1
                K['could ram first: now rule']['yes' if ne and ne[14] else 'no'] += 1
                K['could ram first: switches']['yes' if ne and ne[15] else 'no'] += 1
                ch = chosen(row)
                opts = row['opt']
                mid = ram['mid']
                safe_r2 = [o for o in opts if opt_cls(row, o, only=mid, small=False) < 3]
                safe_r1 = [o for o in opts if opt_cls(row, o, only=mid, small=False) < 4]
                safe_r0 = [o for o in opts if opt_cls(row, o, only=mid, small=False) == 0]
                safe_a2 = [o for o in opts if opt_cls(row, o) < 3]
                safe_a0 = [o for o in opts if opt_cls(row, o) == 0]
                K['t2 step open outside rammer free+1 paid']['yes' if safe_r2 else 'no'] += 1
                K['t2 step open outside rammer free reach']['yes' if safe_r1 else 'no'] += 1
                K['t2 step open outside rammer every reach']['yes' if safe_r0 else 'no'] += 1
                K['t2 step open outside free+1 paid of every 2-4 head']['yes' if safe_a2 else 'no'] += 1
                K['t2 step open outside every reach of every 2-4 head']['yes' if safe_a0 else 'no'] += 1
                K['t2 kind x safe(all heads, free+1)'][kind + ' / ' + ('safe' if safe_a2 else 'none')] += 1
                if ch is None:
                    K['t2 chosen']['no step (split, stay)'] += 1
                else:
                    cc = opt_cls(row, ch, only=mid, small=False)
                    K['t2 chosen class at decision'][str(cc)] += 1
                    if safe_a2 and opt_cls(row, ch) >= 3:
                        if ch[1]:
                            K['t2 cost of the safe step']['a pearl not eaten' if not any(o[1] for o in safe_a2) else 'another pearl'] += 1
                        else:
                            best = min((o[2] if o[2] >= 0 else 9) for o in safe_a2)
                            cur = ch[2] if ch[2] >= 0 else 9
                            dlt = best - cur
                            K['t2 cost of the safe step']['pearl %s' % ('no farther' if dlt <= 0 else '1 farther' if dlt == 1 else '2+ farther')] += 1
                    elif opt_cls(row, ch) >= 3:
                        K['t2 cost of the safe step']['no safe step'] += 1
                    else:
                        K['t2 cost of the safe step']['chosen was outside at decision'] += 1
                if len(ex) < 400 and vs == (0 if gm['a'] == ME else 1):
                    ex.append((gm['game'], ram['r'], ram['L0'], ram['Lv'], ram['k'], ram['ate'], (ram['sx'], ram['sy']), (ram['x'], ram['y']),
                               (row['x'], row['y']), row['r'], kind, doing(row), row['tn'], row['nA'], row['nE'], bool(safe_a2), NAMES.get(gm['b'] if gm['a'] == ME else gm['a'])))
    print('rmax', RM)
    for c in COLS:
        S_ = SUM[c]
        n = max(1, S_['nq'])
        print(head(c), 'rams on 2-4:', S_['n'], 'non-queen', S_['nq'], 'a game %.1f' % (S_['nq'] / max(1, G[c])), 'with row', S_['rows'],
              '| heads within 5: attacker side %.2f victim side %.2f' % (S_['m5'] / n, S_['v5'] / n),
              '| lost: attacker %.2f victim %.2f | regained in 5 rounds: attacker side %.2f victim side %.2f | net attacker %.2f victim %.2f' % (
                  S_['lost_m'] / n, S_['lost_v'] / n, S_['got_m'] / n, S_['got_v'] / n, (S_['lost_m'] - S_['got_m']) / n, (S_['lost_v'] - S_['got_v']) / n))
    names = sorted({k for c in COLS for k in C[c]})
    for nm in names:
        if (sec == 't1') == nm.startswith('t2') or (sec == 't1' and nm.startswith('could')):
            continue
        keys = sorted({k for c in COLS for k in C[c][nm]})
        print('##', nm, keys)
        for c in COLS:
            print('   %-18s %s' % (head(c), share(C[c][nm], keys)))
    if sec == 't2' and len(sys.argv) > 4:
        for e in ex:
            print(e)
