# Scratch (diag-topopen): the report tables as markdown, written to to_tables.md (sections split by lines "@@ name").
# Usage: python3 to_tab.py
import sys, json
from collections import defaultdict, Counter
from pathlib import Path
from statistics import mean, median

D = '개인 프로젝트'
WORK = '~/01. Project/' + D + '/unsw-swarm/data/analysis/ladder/dossier/work/'
W = Path('data/analysis/ladder/dossier/work')
ROUNDS = (10, 20, 30, 40, 60, 80, 100, 150, 200, 300)
NAMES = {454: 'aAah', 157: 'larp', 306: 'Cutlery', 70: 'chad', 91: 'SSS', 264: 'ftm', 842: 'horse', 1119: 'ours'}
GROUPS = ['aAah today', 'larp today', 'Cutlery today', 'chad today', 'aAah old', 'Cutlery old', 'SSS old', 'ftm old', 'horse old',
          'ours B7Q', 'ours main', 'ours B7', 'ours vs top', 'larp vs us', 'Cutlery vs us', 'aAah vs us', 'top vs us', 'ours ladder', 'our opp today']
TOPS = ['aAah today', 'larp today', 'Cutlery today', 'chad today', 'Cutlery old', 'SSS old', 'ftm old', 'horse old']
SIZES = (('S', '700 cells or fewer'), ('M', '701-1200 cells'), ('L', 'above 1200 cells'))
OUT = []


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
            if 'error' in g or g['game'] in seen or g['map'].startswith('Autarky') or g['map'].startswith('Prisoners'):
                continue
            seen.add(g['game'])
            src = g['src'][:2]
            for s in 'ut':
                d = g['sides'][s]
                team = d['team']
                if src == 'T3':
                    lab = (NAMES[team] + ' today') if team in NAMES and team != 1119 else 'T3 opp'
                elif src == 'T1':
                    lab = (NAMES[team] + ' old') if team in NAMES and team != 1119 else 'T1 opp'
                elif src in ('OQ', 'OM', 'OB'):
                    lab = dict(OQ='ours B7Q', OM='ours main', OB='ours B7')[src] if s == 'u' else 'our opp today'
                elif src == 'OT':
                    lab = 'ours vs top' if s == 'u' else (NAMES.get(team, 'top') + ' vs us')
                else:
                    lab = 'ours ladder' if s == 'u' else 'ladder opp'
                out.append(dict(lab=lab, g=g, d=d, o=g['sides']['t' if s == 'u' else 'u'], size=size(g['cells']),
                                lay='%s %dx%d k%d' % (g['map'].split(' #')[0], g['w'], g['h'], g['walls'])))
    return out


def at(r, name, rd):
    v = r['d']['series'][name]
    return v[rd] if len(v) > rd else None


def col(rs, name, rd):
    v = [at(r, name, rd) for r in rs]
    v = [x for x in v if x is not None]
    return (mean(v), len(v)) if v else (None, 0)


def f0(x):
    return '-' if x is None else '%.0f' % x


def f1(x):
    return '-' if x is None else '%.1f' % x


def emit(s):
    OUT.append(s)


def curves(rows):
    for sz, nm in SIZES:
        emit('@@ curve ' + sz)
        emit('| %s: side (games; still running at r100, r300) | %s |' % (nm, ' | '.join('r%d' % r for r in ROUNDS)))
        emit('|---|' + '---|' * len(ROUNDS))
        for l in GROUPS:
            rs = [r for r in rows if r['lab'] == l and r['size'] == sz]
            if len(rs) < 2:
                continue
            cells = []
            for rd in ROUNDS:
                a = col(rs, 'alive', rd)[0]
                if a is None:
                    cells.append('-')
                    continue
                cells.append('%s / %s / %s; %s / %s / %s' % (f1(a), f0(col(rs, 'total', rd)[0]), f1(col(rs, 'longest', rd)[0]),
                                                           f0(col(rs, 'eaten', rd)[0]), f0(col(rs, 'splits', rd)[0]), f0(col(rs, 'deaths', rd)[0])))
            emit('| %s (%d; %d, %d) | %s |' % (l, len(rs), col(rs, 'alive', 100)[1], col(rs, 'alive', 300)[1], ' | '.join(cells)))


def causes(rows):
    emit('@@ causes')
    emit('| Deaths so far by cause, r60 and r300: boxed in or own error / rammed by an enemy head / ramming as the mover / enemy body / mate head | S r60 | S r300 | M r60 | M r300 | L r60 | L r300 |')
    emit('|---|---|---|---|---|---|---|')
    for l in GROUPS:
        cells = []
        ok = False
        for sz, nm in SIZES:
            rs = [r for r in rows if r['lab'] == l and r['size'] == sz]
            for rd in (60, 300):
                v = [r['d']['samp'][str(rd)]['dc'] for r in rs if str(rd) in r['d']['samp']]
                if len(v) < 2:
                    cells.append('-')
                    continue
                ok = True
                tot = Counter()
                for c in v:
                    tot.update(c)
                n = len(v)
                box = sum(tot[k] for k in ('wall', 'own', 'matebody', 'noact', 'nosplit', 'nopay', 'body?'))
                cells.append('%s / %s / %s / %s / %s' % (f1(box / n), f1(tot['hit-by-enemy'] / n), f1(tot['headon-enemy'] / n), f1(tot['enemybody'] / n),
                                                    f1((tot['headon-mate'] + tot['hit-by-mate']) / n)))
        if ok:
            emit('| %s | %s |' % (l, ' | '.join(cells)))


def first15(rows, tops, ours, sz, name, matched):
    A = defaultdict(list)
    B = defaultdict(list)
    for r in rows:
        if r['size'] != sz:
            continue
        k = r['lay'] if matched else 'all'
        if r['lab'] in tops:
            A[k].append(r)
        if r['lab'] in ours:
            B[k].append(r)
    common = [k for k in A if k in B]
    if not common:
        return None, 0, {}
    first, streak, ratios = None, 0, {}
    for rd in range(1, 301):
        xs, ys = [], []
        for k in common:
            ma, n1 = col(A[k], name, rd)
            mb, n2 = col(B[k], name, rd)
            if ma is not None and mb is not None and (matched or (n1 >= 2 and n2 >= 2)):
                xs.append(ma)
                ys.append(mb)
        if len(xs) < max(1, (len(common) + 1) // 2):
            streak = 0
            continue
        x, y = mean(xs), mean(ys)
        q = x / y if y else 0
        if rd in (20, 40, 60, 100, 200, 300):
            ratios[rd] = q
        if q >= 1.5:
            streak += 1
            if streak >= 5 and first is None:
                first = rd - 4
        else:
            streak = 0
    return first, len(common), ratios


def x15(rows):
    emit('@@ x15')
    emit('| First round with 1.5 times ours for 5 rounds running: dragons alive, total length (ratio at r40, r100, r300) | S vs B7Q | S vs all three builds, same layouts | M vs B7Q | M vs all three, same layouts | L vs B7Q | L vs all three, same layouts |')
    emit('|---|---|---|---|---|---|---|')
    today = ('ours B7Q', 'ours main', 'ours B7')
    for l in TOPS:
        cells = []
        ok = False
        for sz, nm in SIZES:
            n = len([r for r in rows if r['lab'] == l and r['size'] == sz])
            for ours, matched in ((('ours B7Q',), False), (today, True)):
                if n < 2:
                    cells.append('-')
                    continue
                ok = True
                part = []
                for name in ('alive', 'total'):
                    first, nl, ratios = first15(rows, (l,), ours, sz, name, matched)
                    part.append('%s (%s)' % ('r%d' % first if first is not None else 'never', ', '.join('%.2f' % ratios[k] for k in (40, 100, 300) if k in ratios)))
                cells.append('; '.join(part) + (' [%d layouts]' % nl if matched else ''))
        if ok:
            emit('| %s | %s |' % (l, ' | '.join(cells)))


def h2h(rows):
    emit('@@ h2h')
    emit('| Our live build against them, same games: first round they hold 1.5 times ours for 5 rounds running (their mean / our mean at r20, r40, r60, r100, r150, r300) | S alive | S total length | M alive | M total length | L alive | L total length |')
    emit('|---|---|---|---|---|---|---|')
    for l in ('larp vs us', 'Cutlery vs us', 'aAah vs us', 'top vs us'):
        cells = []
        ok = False
        for sz, nm in SIZES:
            rs = [r for r in rows if r['lab'] == l and r['size'] == sz]
            for name in ('alive', 'total'):
                if len(rs) < 2:
                    cells.append('-')
                    continue
                ok = True
                first, streak, pts = None, 0, []
                for rd in range(1, 301):
                    a = [r['d']['series'][name][rd] for r in rs if len(r['d']['series'][name]) > rd]
                    b = [r['o']['series'][name][rd] for r in rs if len(r['o']['series'][name]) > rd]
                    if len(a) < 2:
                        streak = 0
                        continue
                    x, y = mean(a), mean(b)
                    if y > 0 and x / y >= 1.5:
                        streak += 1
                        if streak >= 5 and first is None:
                            first = rd - 4
                    else:
                        streak = 0
                    if rd in (20, 40, 60, 100, 150, 300):
                        pts.append('%s/%s' % (f1(x) if name == 'alive' else f0(x), f1(y) if name == 'alive' else f0(y)))
                cells.append('%s (%s) n=%d' % ('r%d' % first if first is not None else 'never', ', '.join(pts), len(rs)))
        if ok:
            emit('| %s | %s |' % (l, ' | '.join(cells)))


def main():
    rows = rows_all()
    curves(rows)
    causes(rows)
    x15(rows)
    h2h(rows)
    Path(WORK + 'to_tables.md').write_text('\n'.join(OUT) + '\n')
    print('\n'.join(OUT))


main()
