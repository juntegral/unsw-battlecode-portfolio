# Scratch (diag-topopen): the mechanics table (rounds 0-60) as markdown -> to_mech.md. Cells are S / M / L size classes.
# Layouts our sets do not have (Autarky, Prisoners Dilemma) are left out so every column plays the same 15 layouts.
import sys, json
from collections import defaultdict, Counter
from pathlib import Path
from statistics import mean, median

D = '개인 프로젝트'
WORK = '~/01. Project/' + D + '/unsw-swarm/data/analysis/ladder/dossier/work/'
W = Path('data/analysis/ladder/dossier/work')
NAMES = {454: 'aAah', 157: 'larp', 306: 'Cutlery', 70: 'chad gdp'}
COLS = ['aAah', 'larp', 'chad gdp', 'Cutlery', 'ours live (B7Q), ladder', 'ours live against larp and Cutlery', 'larp and Cutlery in those games', 'ours B7', 'ours main']
SKIP = ('Autarky', 'Prisoners')


def size(c):
    return 'S' if c <= 700 else 'M' if c <= 1200 else 'L'


def label(src, s, team):
    if src == 'T3':
        return NAMES.get(team)
    if src in ('OQ', 'OB', 'OM'):
        return {'OQ': 'ours live (B7Q), ladder', 'OB': 'ours B7', 'OM': 'ours main'}[src] if s == 'u' else None
    if src == 'OT':
        return 'ours live against larp and Cutlery' if s == 'u' else 'larp and Cutlery in those games'
    return None


def load(prefix):
    out, seen = defaultdict(list), set()
    for f in sorted(W.glob(prefix + '-*.jsonl')):
        if 'test' in f.name:
            continue
        for line in f.read_text().splitlines():
            if not line.strip():
                continue
            g = json.loads(line)
            if 'error' in g or g['game'] in seen or any(g['map'].startswith(m) for m in SKIP):
                continue
            seen.add(g['game'])
            for s in 'ut':
                lab = label(g['src'][:2], s, g['sides'][s]['team'])
                if lab:
                    out[lab, size(g['cells'])].append((g, g['sides'][s], s))
    return out


def pc(a, b, nd=0):
    return '-' if not b else ('%.' + str(nd) + 'f') % (100.0 * a / b)


def f1(x):
    return '-' if x is None else '%.1f' % x


def tsum(rs, pred):
    tot = [0] * 13
    for g, d, s in rs:
        for k, v in d['turns'].items():
            w, lb, ctx, q = k.split('|')
            if pred(int(w), lb, ctx, int(q)):
                for i in range(13):
                    tot[i] += v[i]
    return tot


def main():
    A = load('to_scan')
    B = load('to_scan2')
    C = load('to_scan3')
    rows = []

    def add(name, fn, src=A):
        cells = []
        for c in COLS:
            parts = []
            for sz in 'SML':
                rs = src.get((c, sz), [])
                parts.append(fn(rs) if len(rs) >= 2 else '-')
            cells.append(' / '.join(parts))
        rows.append('| %s | %s |' % (name, ' | '.join(cells)))

    add('Games (S / M / L)', lambda rs: str(len(rs)))

    def splitlen(rs):
        sp = [x for g, d, s in rs for x in d['splits'] if x[0] <= 60]
        return '%s, %s, %s' % (pc(sum(1 for x in sp if x[1] == 4), len(sp)), '%.2f' % mean(x[2] for x in sp) if sp else '-', pc(sum(1 for x in sp if x[2] >= 4), len(sp)))
    add('Splits r0-60: parent 4 long %, mean child length, children of 4+ %', splitlen)

    def r0(rs):
        w = [(g, d) for g, d, s in rs if any(x >= 4 for x in d['cfg'])]
        return '%s (%d)' % (pc(sum(1 for g, d in w if any(x[0] == 0 for x in d['splits'])), len(w)), len(w))
    add('Games with a starter of 4+: a split in round 0 % (games)', r0)

    def queen(rs):
        t = tsum(rs, lambda w, lb, ctx, q: w <= 2 and q == 1 and lb in ('4', '5', '9'))
        ql = [d['series']['ql'][20] for g, d, s in rs if len(d['series']['ql']) > 20]
        return '%.1f, %s, %s' % (t[0] / len(rs), pc(t[1], t[0]), f1(mean(ql)) if ql else '-')
    add('Queen r0-40: her turns at length 4+ a game, split on %, her length at r20', queen)

    def others(rs):
        t = tsum(rs, lambda w, lb, ctx, q: w <= 3 and q == 0 and lb == '4')
        return '%.0f, %s' % (t[0] / len(rs), pc(t[1], t[0]))
    add('Other dragons r0-60: turns at length 4 a game, split on %', others)

    def kids(rs):
        ch = [x for g, d, s in rs for x in d['dragons'] if 1 <= x[0] <= 40]
        if not ch:
            return '-'
        waits = sorted((x[2] - x[0]) if x[2] is not None else 999 for x in ch)
        return '%s, %s, %s' % (pc(sum(1 for x in ch if x[2] is not None and x[2] - x[0] <= 10), len(ch)), waits[len(waits) // 2] if waits[len(waits) // 2] < 999 else 'none',
                               pc(sum(1 for x in ch if x[3] is not None and x[3] - x[0] <= 10), len(ch)))
    add('Dragons born r1-40: first pearl within 10 rounds %, median rounds to it, dead within 10 rounds %', kids)

    def walk(rs):
        ch = [x for g, d, s in rs for x in d['dragons'] if 1 <= x[0] <= 40]
        d5 = [x[9] for x in ch if x[9] is not None and x[9] < 9999]
        d10 = [x[10] for x in ch if x[10] is not None and x[10] < 9999]
        pd = [x[11] for x in ch if x[11] is not None and x[11] < 9999]
        return '%s, %s, %s' % (f1(mean(d5)) if d5 else '-', f1(mean(d10)) if d10 else '-', f1(mean(pd)) if pd else '-')
    add('The child: path steps from its birth tile after 5 and 10 rounds, from the parent head after 5', walk)

    def nn(rs):
        out = []
        for rd in ('20', '40', '60'):
            v = [d['samp'][rd]['nn'] for g, d, s in rs if rd in d['samp'] and d['samp'][rd]['nn'] >= 0]
            out.append(f1(mean(v)) if v else '-')
        return ', '.join(out)
    add('Mean distance to the nearest team mate head (wrapped tiles) r20, r40, r60', nn)

    def seen(rs):
        out = []
        for rd in ('30', '60'):
            v = [100.0 * d['samp'][rd]['seen'] / g['cells'] for g, d, s in rs if rd in d['samp']]
            out.append('%.0f' % mean(v) if v else '-')
        return ', '.join(out)
    add('Layout seen by r30, r60 %', seen)

    def portal(rs):
        pr = [(g, d) for g, d, s in rs if g['pairs'] > 0]
        if len(pr) < 2:
            return '-'
        st = [d['samp']['40']['pstep'] for g, d in pr if '40' in d['samp']]
        return '%s, %s, %s' % (pc(sum(1 for g, d in pr if d['pfirst'] is not None and d['pfirst'] <= 10), len(pr)),
                               pc(sum(1 for g, d in pr if d['pfirst'] is not None and d['pfirst'] <= 20), len(pr)), f1(mean(st)) if st else '-')
    add('Layouts with portals: a portal step by r10, by r20 % of games; portal steps by r40', portal)

    def gate(rs):
        pr = [(g, d) for g, d, s in rs if g['pairs'] > 0]
        if len(pr) < 2:
            return '-'
        t = [0, 0]
        for g, d in pr:
            v = d['gate'].get('0|s', [0, 0])
            t[0] += v[0]
            t[1] += v[1]
        return '%.1f, %s' % (t[0] / len(pr), pc(t[1], t[0]))
    add('Short dragons r0-20 beside a portal mouth, no pearl beside them: turns a game, step through %', gate, B)

    def far(rs):
        pr = [(g, d) for g, d, s in rs if g['pairs'] > 0]
        if len(pr) < 2:
            return '-'
        t = Counter()
        for g, d in pr:
            for k, v in d['tally'].items():
                w, band = k.split('|')
                if int(w) <= 1:
                    t[band] += v[0]
                    t[band + 'n'] += v[1]
        n = len(pr)
        return '%.1f:%s, %.1f:%s, %.1f' % (t['m1'] / n, pc(t['m1n'], t['m1']), (t['m2'] + t['m3']) / n, pc(t['m2n'] + t['m3n'], t['m2'] + t['m3']), t['u1'] / n)
    add('Blind turns r0-40 with a seen, unexplored portal mouth 1-6 steps off: a game:ends nearer %; 7-26 steps off; with one within 12 steps not yet seen', far, C)

    def paid(rs):
        pd = [p for g, d, s in rs for p in d['paid'] if p[0] <= 60 and p[1] <= 4]
        n = len(rs)
        a = sum(1 for p in pd if not p[6] and p[4] >= 2)
        b = sum(1 for p in pd if not p[6] and p[4] == 1 and p[8] <= p[3])
        c = sum(1 for p in pd if not p[6] and p[4] >= 1 and p[8] > p[3])
        dd = sum(1 for p in pd if p[6])
        return '%.1f: %.1f, %.1f, %.1f, %.1f' % (len(pd) / n, a / n, b / n, c / n, dd / n)
    add('Paid sprints r0-60 by dragons of 4 or less, a game: of them two pearls in one turn, one pearl on the free step then a paid step, paid to reach the pearl, died on it', paid)

    def free(rs):
        t = tsum(rs, lambda w, lb, ctx, q: w <= 3 and lb == '5')
        p2 = tsum(rs, lambda w, lb, ctx, q: w <= 3 and lb == '5' and ctx == 'P2')
        return '%.0f, %s, %s' % (t[2] / len(rs), pc(t[7], t[8]), pc(p2[9], p2[0]))
    add('Dragons 5-8 long r0-60: move turns a game, free second step used %, pearl two steps off eaten that turn %', free)

    def p1(rs):
        t = [p for g, d, s in rs for p in d['p1'] if p[0] <= 60 and not p[3]]
        e = sum(1 for p in t if p[4] == 'E')
        m = sum(1 for p in t if p[4] == 'M')
        return '%.0f, %s' % (len(t) / len(rs), pc(m, e + m))
    add('Turns that start with a pearl beside the head (length 4 or less, r0-60): a game, moved elsewhere %', p1, B)

    def births(rs):
        tot = near = c47 = e47 = 0
        for g, d, s in rs:
            for b in g['births']:
                if b[0] > 60:
                    continue
                dist = b[1] if s == 'u' else b[2]
                tot += 1
                near += dist <= 3
                if 4 <= dist <= 7:
                    c47 += 1
                    e47 += b[3] == s and b[4] - b[0] <= 10
        return '%s, %s' % (pc(near, tot), pc(e47, c47))
    add('Natural pearls born r1-60: a head of the side within 3 path steps %; born 4-7 steps off and eaten by it within 10 rounds %', births, B)

    def nat(rs):
        out = []
        for rd in (60, 100):
            v = [(d['series']['nat'][rd], d['samp'][str(rd)]['born']) for g, d, s in rs if str(rd) in d['samp'] and len(d['series']['nat']) > rd]
            out.append(pc(sum(a for a, c in v), sum(c for a, c in v)))
        return ', '.join(out)
    add('Natural pearls born that the side has eaten by r60, by r100 %', nat)

    def deaths(rs):
        dl = [x for g, d, s in rs for x in d['dead'] if x[0] <= 60]
        n = len(rs)
        return '%.1f: %.1f, %.1f, %.1f' % (len(dl) / n, sum(1 for x in dl if x[3] == 0) / n, sum(1 for x in dl if x[2] == 'headon') / n, sum(1 for x in dl if x[3] < 0) / n)
    add('Dragons lost r0-60 a game: with no free tile beside the head, ramming an enemy or mate head, rammed', deaths, B)

    def kidroom(rs):
        ks = [k for g, d, s in rs for k in d['kids'] if 1 <= k[0] <= 60]
        small = [k for k in ks if k[2] < 8]
        return '%.1f, %s' % (len(small) / len(rs), pc(sum(1 for k in small if k[6] is not None and k[6] - k[0] <= 10), len(small)))
    add('Children r1-60 born into under 8 free tiles: a game, dead within 10 rounds %', kidroom, B)

    head = '| Rounds 0-60 unless said; each cell is 700 cells or fewer / 701-1200 / above 1200 | ' + ' | '.join(COLS) + ' |'
    text = '\n'.join([head, '|---|' + '---|' * len(COLS)] + rows) + '\n'
    Path(WORK + 'to_mech.md').write_text(text)
    print(text)


main()
