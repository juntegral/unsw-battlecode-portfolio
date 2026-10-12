# Scratch (diag-topopen): layout-matched tables from to_scan-*.jsonl.
# Usage: python3 to_agg2.py lay <size> | match | open
import sys, json
from collections import defaultdict, Counter
from pathlib import Path
from statistics import mean, median

W = Path('data/analysis/ladder/dossier/work')
ROUNDS = (10, 20, 30, 40, 60, 80, 100, 150, 200, 300)
NAMES = {454: 'aAah', 157: 'larp', 306: 'Cutlery', 70: 'chad', 91: 'SSS', 264: 'ftm', 842: 'horse', 1119: 'ours'}


def size(c):
    return 'S' if c <= 700 else 'M' if c <= 1200 else 'L'


def rows_all():
    out, seen = [], set()
    for f in sorted(W.glob('to_scan-*.jsonl')):
        if 'test' in f.name:
            continue
        for line in f.read_text().splitlines():
            if not line.strip():
                continue
            g = json.loads(line)
            if 'error' in g or g['game'] in seen:
                continue
            seen.add(g['game'])
            src = g['src'][:2]
            for s in 'ut':
                d = g['sides'][s]
                team = d['team']
                if src == 'T3':
                    lab = (NAMES[team] + ' today') if team in NAMES and team != 1119 else 'T3 opp'
                elif src == 'T1':
                    lab = (NAMES[team] + ' old') if s == 'u' and team in NAMES else 'T1 opp'
                elif src in ('OQ', 'OM', 'OB'):
                    lab = dict(OQ='ours B7Q', OM='ours main', OB='ours B7')[src] if s == 'u' else 'our opp today'
                elif src == 'OT':
                    lab = 'ours vs top' if s == 'u' else (NAMES.get(team, 'top') + ' vs us')
                else:
                    lab = 'ours ladder' if s == 'u' else 'ladder opp'
                out.append(dict(lab=lab, g=g, d=d, size=size(g['cells']),
                                lay='%s %dx%d k%d' % (g['map'].split(' #')[0], g['w'], g['h'], g['walls'])))
    return out


def at(r, name, rd):
    v = r['d']['series'][name]
    return v[rd] if len(v) > rd else None


def col(rs, name, rd):
    v = [at(r, name, rd) for r in rs]
    v = [x for x in v if x is not None]
    return (mean(v), len(v)) if v else (None, 0)


def fm(x, nd=1):
    return '-' if x is None else ('%.' + str(nd) + 'f') % x


def pc(a, b):
    return '-' if not b else '%.0f' % (100.0 * a / b)


def metrics(rs):
    n = len(rs)
    st = [d for r in rs for d in r['d']['dragons'] if d[0] == 0]
    ch = [d for r in rs for d in r['d']['dragons'] if 1 <= d[0] <= 40]
    pr = [r for r in rs if r['g']['pairs'] > 0]
    sp0 = sum(1 for r in rs if r['d']['splits'] and r['d']['splits'][0][0] == 0)
    seen30 = [100.0 * r['d']['samp']['30']['seen'] / r['g']['cells'] for r in rs if '30' in r['d']['samp']]
    seen60 = [100.0 * r['d']['samp']['60']['seen'] / r['g']['cells'] for r in rs if '60' in r['d']['samp']]
    nn20 = [r['d']['samp']['20']['nn'] for r in rs if '20' in r['d']['samp'] and r['d']['samp']['20']['nn'] >= 0]
    nat60 = [(at(r, 'nat', 60), r['d']['samp']['60']['born']) for r in rs if '60' in r['d']['samp'] and at(r, 'nat', 60) is not None]
    nat100 = [(at(r, 'nat', 100), r['d']['samp']['100']['born']) for r in rs if '100' in r['d']['samp'] and at(r, 'nat', 100) is not None]
    return dict(n=n, cfg=Counter(str(r['d']['cfg']) for r in rs).most_common(1)[0][0],
                a20=col(rs, 'alive', 20)[0], a40=col(rs, 'alive', 40)[0], a60=col(rs, 'alive', 60)[0], a100=col(rs, 'alive', 100)[0],
                t20=col(rs, 'total', 20)[0], t40=col(rs, 'total', 40)[0], t60=col(rs, 'total', 60)[0], t100=col(rs, 'total', 100)[0],
                e20=col(rs, 'eaten', 20)[0], e40=col(rs, 'eaten', 40)[0], e60=col(rs, 'eaten', 60)[0], e100=col(rs, 'eaten', 100)[0],
                d60=col(rs, 'deaths', 60)[0],
                stfed20=pc(sum(1 for d in st if d[2] is not None and d[2] <= 20), len(st)),
                chfed10=pc(sum(1 for d in ch if d[2] is not None and d[2] - d[0] <= 10), len(ch)),
                chdead10=pc(sum(1 for d in ch if d[3] is not None and d[3] - d[0] <= 10), len(ch)),
                sp0=pc(sp0, n), port20=pc(sum(1 for r in pr if r['d']['pfirst'] is not None and r['d']['pfirst'] <= 20), len(pr)),
                seen30=mean(seen30) if seen30 else None, seen60=mean(seen60) if seen60 else None, nn20=mean(nn20) if nn20 else None,
                nat60=pc(sum(a for a, c in nat60), sum(c for a, c in nat60)), nat100=pc(sum(a for a, c in nat100), sum(c for a, c in nat100)),
                won=pc(sum(1 for r in rs if r['d']['won']), n))


def lay(rows, sz, labs):
    by = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r['size'] == sz or sz == 'all':
            by[r['lay']][r['lab']].append(r)
    for k in sorted(by):
        print('==', k, 'cells', by[k][next(iter(by[k]))][0]['g']['cells'], 'portal pairs', by[k][next(iter(by[k]))][0]['g']['pairs'])
        print('   %-14s %3s %-18s | alive 20/40/60/100 | total 20/40/60/100 | eaten 20/40/60/100 | d60 | stfed20 chfed10 chdead10 sp0 port20 | seen30/60 nn20 | nat60 nat100 | won' % ('group', 'n', 'start'))
        for l in labs:
            rs = by[k].get(l)
            if not rs:
                continue
            m = metrics(rs)
            print('   %-14s %3d %-18s | %s %s %s %s | %s %s %s %s | %s %s %s %s | %s | %s %s %s %s %s | %s %s %s | %s %s | %s' % (
                l, m['n'], m['cfg'][:18], fm(m['a20']), fm(m['a40']), fm(m['a60']), fm(m['a100']), fm(m['t20']), fm(m['t40']), fm(m['t60']), fm(m['t100']),
                fm(m['e20']), fm(m['e40']), fm(m['e60']), fm(m['e100']), fm(m['d60']), m['stfed20'], m['chfed10'], m['chdead10'], m['sp0'], m['port20'],
                fm(m['seen30'], 0), fm(m['seen60'], 0), fm(m['nn20']), m['nat60'], m['nat100'], m['won']))


def matched(rows, a, b, sz, names=('alive', 'total', 'longest', 'eaten', 'splits', 'deaths')):
    A = defaultdict(list)
    B = defaultdict(list)
    for r in rows:
        if sz != 'all' and r['size'] != sz:
            continue
        if r['lab'] in a:
            A[r['lay']].append(r)
        if r['lab'] in b:
            B[r['lay']].append(r)
    common = sorted(k for k in A if k in B)
    na = sum(len(A[k]) for k in common)
    nb = sum(len(B[k]) for k in common)
    res = {}
    for name in names:
        line = []
        first = None
        streak = 0
        for rd in range(1, 301):
            xs, ys = [], []
            for k in common:
                ma, n1 = col(A[k], name, rd)
                mb, n2 = col(B[k], name, rd)
                if ma is not None and mb is not None:
                    xs.append(ma)
                    ys.append(mb)
            if len(xs) < max(2, len(common) // 2):
                streak = 0
                continue
            x, y = mean(xs), mean(ys)
            if y > 0 and x / y >= 1.5:
                streak += 1
                if streak >= 5 and first is None:
                    first = rd - 4
            else:
                streak = 0
            if rd in ROUNDS:
                line.append((rd, x, y, len(xs)))
        res[name] = (line, first)
    return common, na, nb, res


def match(rows, tops, ours):
    for sz in ('S', 'M', 'L'):
        for o in ours:
            for t in tops:
                common, na, nb, res = matched(rows, t if isinstance(t, tuple) else (t,), o if isinstance(o, tuple) else (o,), sz)
                if len(common) < 2 or na < 4:
                    continue
                print('== size %s: %s (%d games) against %s (%d games) on %d shared layouts' % (sz, t, na, o, nb, len(common)))
                for name, (line, first) in res.items():
                    print('   %-8s first 1.5x at r%s | %s' % (name, first, '  '.join('r%d %s/%s=%.2f' % (rd, fm(x), fm(y), x / y if y else 0) for rd, x, y, n in line)))


def main():
    mode = sys.argv[1]
    rows = rows_all()
    today = ('ours B7Q', 'ours main', 'ours B7')
    if mode == 'lay':
        for r in rows:
            if r['lab'] in today:
                r['lab'] = 'ours today'
        labs = sys.argv[3:] or ['aAah today', 'larp today', 'Cutlery today', 'chad today', 'Cutlery old', 'SSS old', 'ftm old', 'horse old', 'aAah old', 'ours today', 'ours vs top', 'ours ladder', 'our opp today']
        lay(rows, sys.argv[2], labs)
    elif mode == 'match':
        tops = ['aAah today', 'larp today', 'Cutlery today', 'chad today', ('aAah today', 'larp today', 'Cutlery today', 'chad today'), 'Cutlery old', 'SSS old', 'ftm old', 'horse old']
        match(rows, tops, [today, 'ours B7Q', 'ours ladder'])


main()
