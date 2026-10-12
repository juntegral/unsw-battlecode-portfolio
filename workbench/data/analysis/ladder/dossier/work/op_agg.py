# Scratch (diag-opening): tables from op_scan-*.jsonl. Each value is formed per game, averaged inside a layout and
# then over layouts with equal weight (layouts that have the value for both bots). "R higher" counts layouts.
# Usage: python3 data/analysis/ladder/dossier/work/op_agg.py [layout-detail metric names ...]
import sys, json
sys.dont_write_bytecode = True
from collections import defaultdict
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
W = 'data/analysis/ladder/dossier/work/'
FILES = ['op_scan-O0.jsonl', 'op_scan-O1.jsonl', 'op_scan-O2.jsonl', 'op_scan-O3.jsonl',
         'op_scan-R0.jsonl', 'op_scan-R1.jsonl', 'op_scan-R2.jsonl', 'op_scan-R3.jsonl']


def load():
    games = []
    for f in FILES:
        with open(W + f) as fh:
            for line in fh:
                if line.strip():
                    games.append(json.loads(line))
    return games


def ser(sd, name, r, neg=False):
    v = sd['series'][name]
    if len(v) <= r:
        return None
    x = v[r]
    if x < 0 and not neg:
        return None
    return x


def tsum(sd, idx, win=None, lb=None, ctx=None, q=None):
    tot = 0
    for key, v in sd['turns'].items():
        a, b, c, d = key.split('|')
        if win is not None and int(a) not in win:
            continue
        if lb is not None and b not in lb:
            continue
        if ctx is not None and c not in ctx:
            continue
        if q is not None and int(d) != q:
            continue
        tot += v[idx]
    return tot


def ratio(n, d, scale=1.0):
    return scale * n / d if d else None


def qclass(sd, r):
    al, qd, fr = ser(sd, 'alive', r), ser(sd, 'qd', r, True), ser(sd, 'front', r, True)
    if al is None:
        return None
    if qd is None or qd < 0:
        return 'dead'
    if al <= 1:
        return 'alone'
    if qd <= 3:
        return 'stays'
    if qd >= fr:
        return 'leads'
    return 'follows'


def metrics():
    m = {}
    for r in (10, 20, 30, 40, 60):
        m['alive%d' % r] = lambda g, sd, r=r: ser(sd, 'alive', r)
        m['total%d' % r] = lambda g, sd, r=r: ser(sd, 'total', r)
        m['eaten%d' % r] = lambda g, sd, r=r: ser(sd, 'eaten', r)
        m['seen%d %%' % r] = lambda g, sd, r=r: ratio(ser(sd, 'seen', r) or 0, g['cells'], 100) if ser(sd, 'seen', r) is not None else None
        m['front%d' % r] = lambda g, sd, r=r: ser(sd, 'front', r)
        m['meand%d' % r] = lambda g, sd, r=r: ser(sd, 'meand', r) / 10 if ser(sd, 'meand', r) is not None else None
        m['adv%d' % r] = lambda g, sd, r=r: g['sep'] - ser(sd, 'toward', r) if ser(sd, 'toward', r) is not None and g['sep'] < 9999 else None
        m['spread%d' % r] = lambda g, sd, r=r: ser(sd, 'spread', r) / 10 if ser(sd, 'spread', r) is not None else None
        m['centre%d' % r] = lambda g, sd, r=r: ser(sd, 'cd', r) / 10 if ser(sd, 'cd', r) is not None else None
        m['qd%d' % r] = lambda g, sd, r=r: ser(sd, 'qd', r)
        m['ql%d' % r] = lambda g, sd, r=r: ser(sd, 'ql', r)
        m['qalive%d %%' % r] = lambda g, sd, r=r: (100.0 if ser(sd, 'ql', r, True) > 0 else 0.0) if ser(sd, 'ql', r, True) is not None else None
        for c in ('stays', 'leads', 'follows', 'alone', 'dead'):
            m['q %s r%d %%' % (c, r)] = lambda g, sd, r=r, c=c: (100.0 if qclass(sd, r) == c else 0.0) if qclass(sd, r) is not None else None
        m['nsplit%d' % r] = lambda g, sd, r=r: sum(1 for s in sd['splits'] if s[0] <= r) if g['last_round'] >= r else None
    m['eaten100'] = lambda g, sd: sd['at100']['eaten'] if sd['at100'] else None
    m['total100'] = lambda g, sd: sd['at100']['total'] if sd['at100'] else None
    m['alive100'] = lambda g, sd: sd['at100']['alive'] if sd['at100'] else None
    m['split1 round'] = lambda g, sd: sd['splits'][0][0] if sd['splits'] else None
    m['split1 len'] = lambda g, sd: sd['splits'][0][1] if sd['splits'] else None
    m['split1 held'] = lambda g, sd: sd['splits'][0][6] if sd['splits'] and sd['splits'][0][6] >= 0 else None
    m['no split by 60 %'] = lambda g, sd: (0.0 if sd['splits'] else 100.0) if g['last_round'] >= 60 else None
    m['split held mean'] = lambda g, sd: ratio(sum(s[6] for s in sd['splits'] if s[6] >= 0), sum(1 for s in sd['splits'] if s[6] >= 0))
    m['split at len4 %'] = lambda g, sd: ratio(sum(1 for s in sd['splits'] if s[1] == 4), len(sd['splits']), 100)
    m['split child2 %'] = lambda g, sd: ratio(sum(1 for s in sd['splits'] if s[2] == 2), len(sd['splits']), 100)
    m['split by queen %'] = lambda g, sd: ratio(sum(1 for s in sd['splits'] if s[3] == 1), len(sd['splits']), 100)
    m['split pearl in view %'] = lambda g, sd: ratio(sum(1 for s in sd['splits'] if s[4] == 'P'), len(sd['splits']), 100)
    m['L4+ turns that split %'] = lambda g, sd: ratio(tsum(sd, 1, lb=('4', '5', '9')), tsum(sd, 0, lb=('4', '5', '9')), 100)
    m['L4 turns that split %'] = lambda g, sd: ratio(tsum(sd, 1, lb=('4',)), tsum(sd, 0, lb=('4',)), 100)
    m['L4+ turn share %'] = lambda g, sd: ratio(tsum(sd, 0, lb=('4', '5', '9')), tsum(sd, 0), 100)
    m['L3 turn share %'] = lambda g, sd: ratio(tsum(sd, 0, lb=('3',)), tsum(sd, 0), 100)
    m['L2 turn share %'] = lambda g, sd: ratio(tsum(sd, 0, lb=('2',)), tsum(sd, 0), 100)
    m['first pearl seen'] = lambda g, sd: sd['see1']
    m['first pearl eaten'] = lambda g, sd: min([d[2] for d in sd['dragons'] if d[2] is not None], default=None)
    m['starters fed by 10 %'] = lambda g, sd: ratio(sum(1 for d in sd['dragons'] if d[0] == 0 and len(d) and d[2] is not None and d[2] <= 10 and (d[3] is None or True)), sum(1 for d in sd['dragons'] if d[0] == 0), 100) if g['last_round'] >= 10 else None
    m['starters fed by 20 %'] = lambda g, sd: ratio(sum(1 for d in sd['dragons'] if d[0] == 0 and d[2] is not None and d[2] <= 20), sum(1 for d in sd['dragons'] if d[0] == 0), 100) if g['last_round'] >= 20 else None
    m['contact round'] = lambda g, sd: sd['contact']
    m['contact by 10 %'] = lambda g, sd: (100.0 if sd['contact'] is not None and sd['contact'] <= 10 else 0.0) if g['last_round'] >= 10 else None
    m['contact by 20 %'] = lambda g, sd: (100.0 if sd['contact'] is not None and sd['contact'] <= 20 else 0.0) if g['last_round'] >= 20 else None
    m['contact by 40 %'] = lambda g, sd: (100.0 if sd['contact'] is not None and sd['contact'] <= 40 else 0.0) if g['last_round'] >= 40 else None
    m['steps per move turn'] = lambda g, sd: ratio(tsum(sd, 2), tsum(sd, 0) - tsum(sd, 1))
    m['turns with 2+ steps /100'] = lambda g, sd: ratio(tsum(sd, 3), tsum(sd, 0), 100)
    m['paid steps /100 turns'] = lambda g, sd: ratio(tsum(sd, 4), tsum(sd, 0), 100)
    m['paid turns /100 turns'] = lambda g, sd: ratio(tsum(sd, 5), tsum(sd, 0), 100)
    m['paid steps a game'] = lambda g, sd: float(tsum(sd, 4)) if g['last_round'] >= 60 else None
    m['paid steps a game r0-20'] = lambda g, sd: float(tsum(sd, 4, win=(0, 1))) if g['last_round'] >= 60 else None
    m['free extra used %'] = lambda g, sd: ratio(tsum(sd, 6), tsum(sd, 7), 100)
    m['free extra on offer /100 turns'] = lambda g, sd: ratio(tsum(sd, 7), tsum(sd, 0), 100)
    for c, nm in (('P', 'pearl in view'), ('E', 'enemy only'), ('N', 'nothing in view')):
        m['turn share: %s %%' % nm] = lambda g, sd, c=c: ratio(tsum(sd, 0, ctx=(c,)), tsum(sd, 0), 100)
        m['paid /100 turns: %s' % nm] = lambda g, sd, c=c: ratio(tsum(sd, 4, ctx=(c,)), tsum(sd, 0, ctx=(c,)), 100)
        m['2+ steps /100 turns: %s' % nm] = lambda g, sd, c=c: ratio(tsum(sd, 3, ctx=(c,)), tsum(sd, 0, ctx=(c,)), 100)
        m['free extra used %%: %s' % nm] = lambda g, sd, c=c: ratio(tsum(sd, 6, ctx=(c,)), tsum(sd, 7, ctx=(c,)), 100)
    for wn, wl in ((0, 'r0-10'), (1, 'r11-20'), (2, 'r21-40'), (3, 'r41-60')):
        m['paid /100 turns %s' % wl] = lambda g, sd, wn=wn: ratio(tsum(sd, 4, win=(wn,)), tsum(sd, 0, win=(wn,)), 100)
        m['nothing-in-view share %s %%' % wl] = lambda g, sd, wn=wn: ratio(tsum(sd, 0, win=(wn,), ctx=('N',)), tsum(sd, 0, win=(wn,)), 100)
    m['paid /100 L3 turns'] = lambda g, sd: ratio(tsum(sd, 4, lb=('3',)), tsum(sd, 0, lb=('3',)), 100)
    m['paid /100 L4 turns'] = lambda g, sd: ratio(tsum(sd, 4, lb=('4',)), tsum(sd, 0, lb=('4',)), 100)
    m['paid /100 L5+ turns'] = lambda g, sd: ratio(tsum(sd, 4, lb=('5', '9')), tsum(sd, 0, lb=('5', '9')), 100)
    m['queen: split share of her turns %'] = lambda g, sd: ratio(tsum(sd, 1, q=1), tsum(sd, 0, q=1), 100)
    m['queen: paid /100 turns'] = lambda g, sd: ratio(tsum(sd, 4, q=1), tsum(sd, 0, q=1), 100)
    m['queen pearls r0-60'] = lambda g, sd: float(sum(d[6] for d in sd['dragons'] if d[5] == 1)) if g['last_round'] >= 60 else None
    m['queen splits r0-60'] = lambda g, sd: float(sum(d[7] for d in sd['dragons'] if d[5] == 1)) if g['last_round'] >= 60 else None
    m['deaths r0-60'] = lambda g, sd: float(sum(sd['deaths'].values())) if g['last_round'] >= 60 else None
    for c in ('wall', 'own', 'body', 'headon', 'hit', 'nosplit', 'nopay', 'noact'):
        m['deaths r0-60: %s' % c] = lambda g, sd, c=c: float(sd['deaths'].get(c, 0)) if g['last_round'] >= 60 else None
    m['kids born r0-40 fed within 10 %'] = lambda g, sd: ratio(sum(1 for d in sd['dragons'] if 0 < d[0] <= 40 and d[2] is not None and d[2] - d[0] <= 10), sum(1 for d in sd['dragons'] if 0 < d[0] <= 40), 100)
    m['kids born r0-40 dead within 10 %'] = lambda g, sd: ratio(sum(1 for d in sd['dragons'] if 0 < d[0] <= 40 and d[3] is not None and d[3] - d[0] <= 10), sum(1 for d in sd['dragons'] if 0 < d[0] <= 40), 100)
    return m


def table(games, mets, detail):
    acc = defaultdict(lambda: defaultdict(list))
    for g in games:
        for s, tag in (('u', g['who']), ('t', g['who'] + 'o')):
            sd = g['sides'][s]
            for name, fn in mets.items():
                v = fn(g, sd)
                if v is not None:
                    acc[name][(tag, g['layout'])].append(v)
    lines = []
    layouts = sorted({g['layout'] for g in games})
    lines.append('%-40s %9s %9s %9s %9s  %s' % ('metric', 'O', 'R', 'Oopp', 'Ropp', 'R higher / lower / layouts'))
    for name in mets:
        a = acc[name]
        both = [l for l in layouts if a.get(('O', l)) and a.get(('R', l))]
        if not both:
            continue
        mean = lambda tag: sum(sum(a[(tag, l)]) / len(a[(tag, l)]) for l in both if a.get((tag, l))) / max(1, sum(1 for l in both if a.get((tag, l))))
        hi = sum(1 for l in both if sum(a[('R', l)]) / len(a[('R', l)]) > sum(a[('O', l)]) / len(a[('O', l)]) + 1e-9)
        lo = sum(1 for l in both if sum(a[('R', l)]) / len(a[('R', l)]) < sum(a[('O', l)]) / len(a[('O', l)]) - 1e-9)
        lines.append('%-40s %9.2f %9.2f %9.2f %9.2f  %d / %d / %d' % (name, mean('O'), mean('R'), mean('Oo'), mean('Ro'), hi, lo, len(both)))
        if name in detail:
            for l in layouts:
                row = []
                for tag in ('O', 'R', 'Oo', 'Ro'):
                    v = a.get((tag, l))
                    row.append('%9.2f' % (sum(v) / len(v)) if v else '%9s' % '-')
                lines.append('    %-36s %s  n %d / %d' % (l[:36], ' '.join(row), len(a.get(('O', l), ())), len(a.get(('R', l), ()))))
    return lines


def main():
    games = load()
    detail = set(sys.argv[1:])
    lines = ['games O %d R %d' % (sum(1 for g in games if g['who'] == 'O'), sum(1 for g in games if g['who'] == 'R'))]
    lay = {}
    for g in games:
        lay.setdefault(g['layout'], set()).add((g['cells'], g['w'], g['h'], g['sep'], tuple(g['sides']['u']['cfg']), tuple(g['sides']['t']['cfg'])))
    for l in sorted(lay):
        lines.append('LAYOUT %-24s %s' % (l, sorted(lay[l])))
    lines += table(games, metrics(), detail)
    body = '\n'.join(lines) + '\n'
    Path(OUT + 'op_agg.txt').write_text(body)
    print(body)


main()
