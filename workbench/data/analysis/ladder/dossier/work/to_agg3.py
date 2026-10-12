# Scratch (diag-topopen): turn contexts, sprint detail and deaths by cause from to_scan-*.jsonl.
# Usage: python3 to_agg3.py ctx <size|all> | paid <size|all> | dc <size|all>
import sys, json
from collections import defaultdict, Counter
from pathlib import Path
from statistics import mean, median

W = Path('data/analysis/ladder/dossier/work')
NAMES = {454: 'aAah', 157: 'larp', 306: 'Cutlery', 70: 'chad', 91: 'SSS', 264: 'ftm', 842: 'horse', 1119: 'ours'}
LABS = ['aAah today', 'larp today', 'Cutlery today', 'chad today', 'Cutlery old', 'SSS old', 'ftm old', 'horse old', 'aAah old',
        'ours today', 'ours B7Q', 'ours vs top', 'ours ladder', 'our opp today', 'T3 opp', 'larp vs us', 'Cutlery vs us', 'aAah vs us', 'top vs us']


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
                labs = []
                if src == 'T3':
                    labs.append((NAMES[team] + ' today') if team in NAMES and team != 1119 else 'T3 opp')
                elif src == 'T1':
                    labs.append((NAMES[team] + ' old') if s == 'u' and team in NAMES else 'T1 opp')
                elif src in ('OQ', 'OM', 'OB'):
                    if s == 'u':
                        labs.append('ours today')
                        if src == 'OQ':
                            labs.append('ours B7Q')
                    else:
                        labs.append('our opp today')
                elif src == 'OT':
                    labs.append('ours vs top' if s == 'u' else (NAMES.get(team, 'top') + ' vs us'))
                else:
                    labs.append('ours ladder' if s == 'u' else 'ladder opp')
                for lab in labs:
                    out.append(dict(lab=lab, g=g, d=d, size=size(g['cells'])))
    return out


def pct(a, b, nd=1):
    return '-' if not b else ('%.' + str(nd) + 'f') % (100.0 * a / b)


def tsum(rs, pred):
    tot = [0] * 13
    for r in rs:
        for k, v in r['d']['turns'].items():
            w, lb, ctx, q = k.split('|')
            if pred(int(w), lb, ctx, int(q)):
                for i in range(13):
                    tot[i] += v[i]
    return tot


def ctx(rows, sz):
    print('== turn contexts r0-60, dragons of length 4 or less, size', sz)
    print('   %-14s %4s | share of turns P1 P2 P3 E N | P1: split%% move-no-eat%% eaten per 100 | by window P1 eaten/100 (r0-10, 11-20, 21-40, 41-60) | N share by window' % ('group', 'n'))
    for l in LABS:
        rs = [r for r in rows if r['lab'] == l and (sz == 'all' or r['size'] == sz)]
        if len(rs) < 3:
            continue
        short = ('2', '3', '4')
        tot = tsum(rs, lambda w, lb, c, q: w <= 3 and lb in short)[0]
        sh = []
        for c0 in ('P1', 'P2', 'P3', 'E', 'N'):
            sh.append(pct(tsum(rs, lambda w, lb, c, q: w <= 3 and lb in short and c == c0)[0], tot))
        p1 = tsum(rs, lambda w, lb, c, q: w <= 3 and lb in short and c == 'P1')
        noeat = p1[2] - min(p1[9], p1[2])
        win = []
        nwin = []
        for w0 in range(4):
            a = tsum(rs, lambda w, lb, c, q: w == w0 and lb in short and c == 'P1')
            win.append(pct(a[9], a[0], 0))
            b = tsum(rs, lambda w, lb, c, q: w == w0 and lb in short and c == 'N')
            t = tsum(rs, lambda w, lb, c, q: w == w0 and lb in short)
            nwin.append(pct(b[0], t[0], 0))
        print('   %-14s %4d | %s | %s %s %s | %s | %s' % (l, len(rs), ' '.join(sh), pct(p1[1], p1[0]), pct(noeat, p1[0]), pct(p1[9], p1[0]), ' '.join(win), ' '.join(nwin)))
        for lb0, nm in ((('2',), 'len2'), (('3',), 'len3'), (('4',), 'len4')):
            a = tsum(rs, lambda w, lb, c, q: w <= 3 and lb in lb0 and c == 'P1')
            t = tsum(rs, lambda w, lb, c, q: w <= 3 and lb in lb0)
            print('        %s: turns %d (%.0f a game), P1 turns %s%%, of them split %s%%, eaten per 100 %s' % (nm, t[0], t[0] / len(rs), pct(a[0], t[0]), pct(a[1], a[0]), pct(a[9], a[0])))


def paid(rows, sz):
    print('== paid sprints r0-60 by dragons of length 4 or less, size', sz)
    for l in LABS:
        rs = [r for r in rows if r['lab'] == l and (sz == 'all' or r['size'] == sz)]
        if len(rs) < 3:
            continue
        n = len(rs)
        pd = [p for r in rs for p in r['d']['paid'] if p[0] <= 60 and p[1] <= 4]
        kinds = Counter()
        for p in pd:
            rnd, L, steps, free, ate, c, dead, q, ateat = p
            if dead:
                k = 'died'
            elif ate and ateat <= free:
                k = 'ate on the free step, then paid on'
            elif ate:
                k = 'paid to reach the pearl'
            elif c[0] == 'E' or c.endswith('e'):
                k = 'no pearl, enemy in view'
            else:
                k = 'no pearl, no enemy'
            kinds[k] += 1
        print('   %-14s n=%3d paid turns a game %.2f | %s' % (l, n, len(pd) / n, '; '.join('%s %.2f' % (k, v / n) for k, v in kinds.most_common())))


def dc(rows, sz):
    print('== deaths r0-60 a game by cause, size', sz)
    for l in LABS:
        rs = [r for r in rows if r['lab'] == l and (sz == 'all' or r['size'] == sz)]
        if len(rs) < 3:
            continue
        n = len(rs)
        dl = [d for r in rs for d in r['d']['deaths'] if d[0] <= 60]
        boxed = sum(1 for d in dl if d[2] in ('wall', 'own', 'matebody', 'noact', 'nosplit', 'nopay', 'body?', 'enemybody'))
        fight = sum(1 for d in dl if d[2].startswith('headon') or d[2].startswith('hit'))
        young = sum(1 for d in dl if d[0] - d[3] <= 10 and d[3] > 0)
        print('   %-14s n=%3d deaths %.1f | not in a fight (wall, own, body, no action) %.1f | head-on as mover %.1f, as victim %.1f | within 10 rounds of birth %.1f | per 100 dragons born+started: %s' % (
            l, n, len(dl) / n, boxed / n, sum(1 for d in dl if d[2].startswith('headon')) / n, sum(1 for d in dl if d[2].startswith('hit')) / n, young / n,
            pct(len(dl), sum(1 for r in rs for d in r['d']['dragons'] if d[0] <= 60))))


def main():
    rows = rows_all()
    mode = sys.argv[1]
    for sz in sys.argv[2:] or ['all']:
        if mode == 'ctx':
            ctx(rows, sz)
        elif mode == 'paid':
            paid(rows, sz)
        elif mode == 'dc':
            dc(rows, sz)


main()
